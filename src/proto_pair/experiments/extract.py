"""Freeze ProtoPair's minimal daily slice from the Algotrade DB.

Two steps, both read-only and scoped by ticker and date:

``pp-extract meta --tool <rivf26_extract.py> --window w1``
    Reads the two tables the shared extraction tool does not carry --
    ``quote.vn30`` (index membership review snapshots) and
    ``quote.futurecontractcode`` (``VN30F1M`` -> dated contract) -- plus the
    VN30 index's own session dates to place the signal warm-up. Writes
    ``quote_vn30.parquet`` and ``quote_futurecontractcode.parquet`` into
    ``data/market/<window>/`` and ``request.json`` beside them.

``pp-extract request --window w1``
    Rebuilds ``request.json`` from the two metadata files already in
    ``data/market/<window>/`` (no DB access). The request is then handed to the
    shared tool in ``declared --request`` mode, which writes the daily
    ``quote_*.parquet`` files and the ``DATA-MANIFEST.md``.

The request is the *exact* (file, ticker, day-range) set the two arms read:

* the 8 daily fields the session reads (close, open, max, min, ceil, floor,
  reference, dailyvolume) for every basket name over the window, and for each
  dated front-month contract over the sessions it is front month inside the
  window;
* ``quote_close`` only for the ``VN30`` index level and the front-month
  contracts over the ``lookback - 1`` sessions before the window (signal
  warm-up: the z-score needs ``lookback`` basis points on day one);
* ``quote_ticker`` master rows for every ticker above (venue routing).

Credentials are never read here directly: the DB client is the shared tool's
``PgClient`` (read-only transaction, statement timeout, scrubbed errors), loaded
from the path given by ``--tool`` or ``$RIVF26_EXTRACT``.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import pyarrow as pa
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[3]
PARAMS = REPO / 'parameter' / 'pair.json'
MARKET = REPO / 'data' / 'market'

EQUITY_FIELDS = ('close', 'open', 'max', 'min', 'ceil', 'floor', 'reference',
                 'dailyvolume')
FUTURE_FIELDS = EQUITY_FIELDS
INDEX = 'VN30'
F1M = 'VN30F1M'

_VN30_SCHEMA = pa.schema([('datetime', pa.date32()), ('tickersymbol', pa.string())])
_FCC_SCHEMA = pa.schema([('datetime', pa.date32()), ('tickersymbol', pa.string()),
                         ('futurecode', pa.string())])
_WRITER = dict(compression='zstd', use_dictionary=False, write_statistics=False,
               version='2.6')


def params() -> dict:
    return json.loads(PARAMS.read_text())


def window_bounds(name: str) -> Tuple[date, date]:
    w = params()['windows'][name]
    return date.fromisoformat(w['start']), date.fromisoformat(w['end'])


def _load_tool(path: str):
    spec = importlib.util.spec_from_file_location('rivf26_extract', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['rivf26_extract'] = mod
    spec.loader.exec_module(mod)
    return mod


def _write(path: Path, schema: pa.Schema, rows: List[tuple]) -> None:
    rows = sorted(set(rows), key=lambda r: (r[1], r[0]) + tuple(r[2:]))
    cols = list(zip(*rows)) if rows else [[] for _ in schema]
    table = pa.Table.from_arrays([pa.array(c, type=f.type) for c, f in zip(cols, schema)],
                                 schema=schema)
    pq.write_table(table, path, **_WRITER)


# --------------------------------------------------------------------------
# metadata (DB)
# --------------------------------------------------------------------------

def fetch_meta(db, start: date, end: date, lookback: int) -> Dict[str, list]:
    """Read the VN30 sessions for warm-up, the review snapshots in force, and
    the VN30F1M roll map over [warm-up start, end]."""
    prior = db.fetch(
        'SELECT datetime FROM quote.close WHERE tickersymbol = %s '
        'AND datetime < %s ORDER BY datetime DESC LIMIT %s',
        [INDEX, start, lookback - 1])
    warm = min(r[0] for r in prior) if prior else start
    snaps = db.fetch('SELECT DISTINCT datetime FROM quote.vn30 WHERE datetime <= %s '
                     'ORDER BY datetime', [end])
    in_force = [d for (d,) in snaps if d <= start][-1:] + [d for (d,) in snaps
                                                           if start < d <= end]
    vn30 = db.fetch('SELECT datetime, tickersymbol FROM quote.vn30 '
                    'WHERE datetime = ANY(%s)', [in_force])
    fcc = db.fetch('SELECT datetime, tickersymbol, futurecode FROM quote.futurecontractcode '
                   'WHERE futurecode = %s AND datetime >= %s AND datetime <= %s',
                   [F1M, warm, end])
    return {'vn30': [(d, str(t)) for d, t in vn30],
            'fcc': [(d, str(t), str(c)) for d, t, c in fcc]}


# --------------------------------------------------------------------------
# request (pure)
# --------------------------------------------------------------------------

def _runs(days: Sequence[date]) -> List[List[str]]:
    """Half-open [lo, hi) calendar intervals covering ``days`` (the tool's
    interval format); contiguous by calendar day, so weekends merge."""
    out: List[List[date]] = []
    for d in sorted(days):
        if out and (d - out[-1][1]).days <= 4:   # bridge weekends/short holidays
            out[-1][1] = d
        else:
            out.append([d, d])
    return [[lo.isoformat(), (hi + timedelta(days=1)).isoformat()] for lo, hi in out]


def build_request(vn30_rows, fcc_rows, start: date, end: date) -> dict:
    snaps: Dict[date, set] = {}
    for d, t in vn30_rows:
        snaps.setdefault(d, set()).add(t)
    names = sorted(set().union(*snaps.values()))
    span = [[start.isoformat(), (end + timedelta(days=1)).isoformat()]]
    by_contract_in: Dict[str, List[date]] = {}
    by_contract_all: Dict[str, List[date]] = {}
    for d, contract, _code in fcc_rows:
        by_contract_all.setdefault(contract, []).append(d)
        if start <= d <= end:
            by_contract_in.setdefault(contract, []).append(d)
    warm_start = min(d for d, _c, _f in fcc_rows)
    files = []
    for f in EQUITY_FIELDS:
        tickers = {n: span for n in names}
        for c, days in by_contract_in.items():
            tickers[c] = _runs(days)
        if f == 'close':
            for c, days in by_contract_all.items():
                tickers[c] = _runs(days)
            tickers[INDEX] = [[warm_start.isoformat(),
                               (end + timedelta(days=1)).isoformat()]]
        files.append({'file': f'quote_{f}.parquet',
                      'tickers': dict(sorted(tickers.items()))})
    master = sorted(names + list(by_contract_all) + [INDEX])
    files.append({'file': 'quote_ticker.parquet', 'tickers': {t: None for t in master}})
    return {'version': 1, 'files': sorted(files, key=lambda e: e['file'])}


def _read_meta(out: Path):
    vn30 = pq.read_table(out / 'quote_vn30.parquet').to_pylist()
    fcc = pq.read_table(out / 'quote_futurecontractcode.parquet').to_pylist()
    return ([(r['datetime'], r['tickersymbol']) for r in vn30],
            [(r['datetime'], r['tickersymbol'], r['futurecode']) for r in fcc])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='pp-extract')
    ap.add_argument('step', choices=('meta', 'request'))
    ap.add_argument('--window', required=True)
    ap.add_argument('--tool', default=os.environ.get('RIVF26_EXTRACT'),
                    help='path to the shared rivf26_extract.py (meta step only)')
    ap.add_argument('--out', type=Path, default=None)
    a = ap.parse_args(argv)
    start, end = window_bounds(a.window)
    out = a.out or (MARKET / a.window)
    out.mkdir(parents=True, exist_ok=True)
    if a.step == 'meta':
        if not a.tool:
            ap.error('--tool or $RIVF26_EXTRACT is required for the meta step')
        tool = _load_tool(a.tool)
        db = tool.PgClient()
        try:
            meta = fetch_meta(db, start, end, params()['lookback'])
        finally:
            db.close()
        _write(out / 'quote_vn30.parquet', _VN30_SCHEMA, meta['vn30'])
        _write(out / 'quote_futurecontractcode.parquet', _FCC_SCHEMA, meta['fcc'])
    vn30, fcc = _read_meta(out)
    req = build_request(vn30, fcc, start, end)
    (out / 'request.json').write_text(json.dumps(req, indent=1, sort_keys=True) + '\n')
    print(f'{a.window}: {len({d for d, _ in vn30})} review snapshot(s), '
          f'{len({c for _, c, _ in fcc})} front-month contracts, request -> {out / "request.json"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
