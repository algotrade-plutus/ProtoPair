"""Load one window's frozen daily slice (``data/market/<window>/``).

Prices in the slice are in **thousands of đồng** (the DB's unit); cash and
P&L everywhere else in ProtoPair are in real đồng (``price_scale = 1000``;
futures multiplier 100,000đ per index point).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple

import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[2]
MARKET = REPO / 'data' / 'market'
PARAMS = REPO / 'parameter' / 'pair.json'
INDEX = 'VN30'


def load_params() -> dict:
    return json.loads(PARAMS.read_text())


@dataclass
class Market:
    name: str
    root: Path
    window: Tuple[date, date]
    days: List[date]                      # warm-up + window sessions (signal days)
    window_days: List[date]               # sessions inside the window
    index_close: Dict[date, float]
    roll_map: Dict[date, str]             # session -> front-month dated contract
    future_close: Dict[date, float]       # session -> front-month close
    contract_close: Dict[Tuple[str, date], float]
    equity_close: Dict[Tuple[str, date], float]
    snapshots: Dict[date, Tuple[str, ...]]


def _rows(path: Path):
    return pq.read_table(path).to_pylist()


def load_market(name: str, root: Path = None) -> Market:
    root = Path(root or MARKET / name)
    w = load_params()['windows'][name]
    window = (date.fromisoformat(w['start']), date.fromisoformat(w['end']))
    roll_map = {r['datetime']: r['tickersymbol']
                for r in _rows(root / 'quote_futurecontractcode.parquet')}
    snaps: Dict[date, set] = {}
    for r in _rows(root / 'quote_vn30.parquet'):
        snaps.setdefault(r['datetime'], set()).add(r['tickersymbol'])
    index_close, contract_close, equity_close = {}, {}, {}
    for r in _rows(root / 'quote_close.parquet'):
        t, d, p = r['tickersymbol'], r['datetime'], float(r['price'])
        if t == INDEX:
            index_close[d] = p
        elif t.startswith('VN30F'):
            contract_close[(t, d)] = p
        else:
            equity_close[(t, d)] = p
    future_close = {d: contract_close[(c, d)] for d, c in roll_map.items()
                    if (c, d) in contract_close}
    days = sorted(set(index_close) & set(future_close))
    window_days = [d for d in days if window[0] <= d <= window[1]]
    return Market(name, root, window, days, window_days, index_close, roll_map,
                  future_close, contract_close, equity_close,
                  {d: tuple(sorted(s)) for d, s in snaps.items()})


def settlement_calendar(m: Market) -> dict:
    """A settlement calendar for the session, *derived* from the slice: every
    weekday in the window with no HOSE ``VN30`` session is a closure. Coverage
    runs four calendar days past the window so the last sessions' T+2 resolves
    (no closure falls in those days for either window: 2023-08-05..08 and
    2024-02-03..06; Tet 2024 starts 2024-02-08). Not a VSDC notice, and the
    id and source say so. Replaces the session default, which is weekday-only
    and ignores every holiday (``weekday-only-UNSOURCED``)."""
    from datetime import timedelta
    start, end = m.window
    sessions = set(m.window_days)
    holidays, d = [], start
    while d <= end:
        if d.weekday() < 5 and d not in sessions:
            holidays.append(d.isoformat())
        d += timedelta(days=1)
    return {'calendar_id': f'derived-hose-sessions-{m.name}',
            'coverage': [start.isoformat(), (end + timedelta(days=4)).isoformat()],
            'holidays': holidays,
            'source': 'derived: weekdays with no HOSE VN30 session in the frozen '
                      'slice (exchange closures), not a VSDC notice'}
