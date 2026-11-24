"""``pp-anchor``: naive vs faithful on one frozen window -> ``result/pair_anchor/<window>.json``.

Both arms replay the identical pair plans (``strategy.plans_from`` over
``strategy.decide_all``) on the identical slice ``data/market/<window>/``;
only execution differs.

Faithful variants (all on the same plans):

* ``headline``     -- ``soft`` fills, deposit target 80,000,000đ, T+2 on, sale advance off
* ``thin``         -- as headline, deposit target 62,000,000đ
* ``hard``         -- as headline, ``hard`` fill policy
* ``sale_advance`` -- as headline, sale advance on (0.03%/day)

The ``faithful`` and ``tier1`` blocks are the headline variant's.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import plutus

from proto_pair.backtest import run_naive, signal_plans
from proto_pair.data import REPO, load_market, load_params
from proto_pair.faithful import run_faithful

VARIANTS = {
    'headline': dict(deposit='comfortable', fill_policy='soft', sale_advance=False),
    'thin': dict(deposit='thin', fill_policy='soft', sale_advance=False),
    'hard': dict(deposit='comfortable', fill_policy='hard', sale_advance=False),
    'sale_advance': dict(deposit='comfortable', fill_policy='soft', sale_advance=True),
}


def _git(path: Path, *args: str) -> str:
    try:
        return subprocess.run(['git', '-C', str(path), *args], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return 'unknown'


def _slice_manifest(root: Path) -> dict:
    return {f.name: {'bytes': f.stat().st_size,
                     'sha256': hashlib.sha256(f.read_bytes()).hexdigest()}
            for f in sorted(root.glob('*.parquet'))}


def _summary(f: dict) -> dict:
    t = f['tier1']
    return {'fills': f['fills'], 'hpr_pct': f['hpr_pct'], 'sharpe': f['sharpe'],
            'mdd_pct': f['mdd_pct'],
            'exits_blocked_by_t2': t['settlement_asymmetry']['exits_blocked_by_t2'],
            'exits_wanted': t['settlement_asymmetry']['exits_wanted'],
            'name_days_held_open': t['settlement_asymmetry']['name_days_held_open'],
            'opposite_side_forgone': t['opposite_side']['forgone'],
            'opposite_side_signalled': t['opposite_side']['mirror_trades_signalled'],
            'margin': t['margin'], 'funding': t['funding'],
            'fill_time_indeterminate_events': t['fill_time_indeterminate_events'],
            'submit_indeterminate': t['submit_indeterminate'],
            'refusals_by_cause': t['refusals_by_cause']}


def run_window(name: str) -> dict:
    m, p = load_market(name), load_params()
    plans = signal_plans(m, p)
    naive = run_naive(m, p, plans)
    variants = {}
    for vname, v in VARIANTS.items():
        variants[vname] = run_faithful(m, p, plans,
                                       deposit_target=p['deposit_target'][v['deposit']],
                                       fill_policy=v['fill_policy'],
                                       sale_advance=v['sale_advance'])
    head = variants['headline']
    sim = Path(plutus.__file__).resolve().parents[2]
    return {
        'window': name, 'start': m.window[0].isoformat(), 'end': m.window[1].isoformat(),
        'sessions': len(m.window_days),
        'plutus_simulator_commit': _git(sim, 'rev-parse', 'HEAD'),
        'plutus_simulator_dirty': bool(_git(sim, 'status', '--porcelain', '--untracked-files=no')),
        'proto_pair_commit': _git(REPO, 'rev-parse', 'HEAD'),
        'parameters': {k: p[k] for k in ('capital', 'deposit_target', 'lookback', 'z_in',
                                         'z_out', 'lots_per_name', 'hedge_beta',
                                         'naive_cost')},
        'plans': [{'side': pl.side.value, 'entry': pl.entry_day.isoformat(),
                   'exit': pl.exit_day.isoformat() if pl.exit_day else None,
                   'contract': pl.contract, 'contracts': pl.contracts,
                   'names': len(pl.shares)} for pl in plans],
        'naive': naive,
        'faithful': {k: v for k, v in head.items() if k != 'tier1'},
        'tier1': head['tier1'],
        'gap': {'fills_f_over_n': round(head['fills'] / naive['fills'], 4) if naive['fills'] else None,
                'hpr_naive_pct': naive['hpr_pct'], 'hpr_faithful_pct': head['hpr_pct']},
        'variants': {k: _summary(v) for k, v in variants.items()},
        'slice': _slice_manifest(m.root),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='pp-anchor')
    ap.add_argument('--window', action='append', default=None)
    a = ap.parse_args(argv)
    out_dir = REPO / 'result' / 'pair_anchor'
    out_dir.mkdir(parents=True, exist_ok=True)
    for w in a.window or ['w1', 'w2']:
        res = run_window(w)
        (out_dir / f'{w}.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
        g, v = res['gap'], res['variants']
        print(f"{w}: fills n={res['naive']['fills']} f={res['faithful']['fills']} "
              f"(f/n {g['fills_f_over_n']}), HPR {g['hpr_naive_pct']}% -> {g['hpr_faithful_pct']}%")
        for k, s in v.items():
            print(f"  {k:12s} fills={s['fills']:5d} hpr={s['hpr_pct']:8.4f}% "
                  f"exits blocked {s['exits_blocked_by_t2']}/{s['exits_wanted']} "
                  f"name-days {s['name_days_held_open']} opp forgone "
                  f"{s['opposite_side_forgone']}/{s['opposite_side_signalled']} "
                  f"margin {s['margin']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
