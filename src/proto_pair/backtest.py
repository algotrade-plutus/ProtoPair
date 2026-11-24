"""The naive arm: ProtoPair's own single-ledger backtester (spec §4a).

The honest developer default, deliberately blind to every mechanism the
faithful arm models:

* **one ledger** -- both legs' cash netted the same day; no securities /
  derivatives segregation, no T+2, no daily variation-margin clock, no margin;
* **shorting allowed** -- it trades the mirror (``CHEAP``) side too;
* **frictionless fills** at the session close, unlimited size, no admission
  (no lot, tick or band check);
* a **static assumed cost** (``naive_cost`` in ``parameter/pair.json``):
  0.15% a side on the equity leg plus 0.1% sell tax, 10,000đ per contract a
  side on the futures leg.

Prices are read in thousands of đồng and converted (``price_scale``); every
amount here is real đồng.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from typing import Dict, List, Optional

from proto_pair.data import Market, load_market, load_params
from proto_pair.metrics import summarize
from proto_pair.strategy import PairPlan, State, decide_all, plans_from


def signal_plans(m: Market, p: dict) -> List[PairPlan]:
    decisions = decide_all(m.days, m.future_close, m.index_close, m.roll_map,
                           p['lookback'], p['z_in'], p['z_out'])
    return plans_from(decisions, m.window, m.roll_map, m.snapshots, m.equity_close,
                      m.future_close, lots_per_name=p['lots_per_name'],
                      board_lot=p['board_lot'], price_scale=p['price_scale'],
                      multiplier=p['futures_multiplier'], beta=p['hedge_beta'])


def run_naive(m: Market, p: dict, plans: Optional[List[PairPlan]] = None) -> dict:
    plans = signal_plans(m, p) if plans is None else plans
    scale, mult = p['price_scale'], p['futures_multiplier']
    c = p['naive_cost']
    cash = float(p['capital'])
    shares: Dict[str, int] = {}
    fut: Dict[str, List[float]] = {}           # contract -> [net, entry]
    last: Dict[str, float] = {}
    fills = {'equity': 0, 'futures': 0}
    costs = 0.0
    equity_curve: List[float] = []
    entries = {d: [] for d in m.window_days}
    exits = {d: [] for d in m.window_days}
    for pl in plans:
        entries[pl.entry_day].append(pl)
        if pl.exit_day is not None:
            exits[pl.exit_day].append(pl)

    def px(name: str, d: date) -> float:
        v = m.equity_close.get((name, d))
        if v is not None:
            last[name] = v
        return last[name]

    def trade_equity(name: str, qty: int, d: date):
        nonlocal cash, costs
        value = px(name, d) * scale * abs(qty)
        fee = value * c['equity_rate_per_side'] + (value * c['equity_sell_tax'] if qty < 0 else 0)
        cash += -value if qty > 0 else value
        cash -= fee
        costs += fee
        shares[name] = shares.get(name, 0) + qty
        fills['equity'] += 1

    def trade_future(contract: str, qty: int, d: date):
        nonlocal cash, costs
        price = m.contract_close[(contract, d)]
        net, entry = fut.get(contract, [0, 0.0])
        if net == 0:
            fut[contract] = [qty, price]
        else:                                   # closing (plans never scale in)
            cash += (price - entry) * mult * net
            fut[contract] = [net + qty, entry]
        fee = c['futures_per_contract_per_side'] * abs(qty)
        cash -= fee
        costs += fee
        fills['futures'] += 1

    for d in m.window_days:
        for pl in exits[d]:
            sign = 1 if pl.side is State.RICH else -1
            for name, q in pl.shares:
                trade_equity(name, -sign * q, d)
            trade_future(pl.contract, sign * pl.contracts, d)
        for pl in entries[d]:
            sign = 1 if pl.side is State.RICH else -1
            for name, q in pl.shares:
                trade_equity(name, sign * q, d)
            trade_future(pl.contract, -sign * pl.contracts, d)
        mtm = sum(px(n, d) * scale * q for n, q in shares.items() if q)
        for contract, (net, entry) in fut.items():
            if net:
                mtm += (m.contract_close[(contract, d)] - entry) * mult * net
        equity_curve.append(cash + mtm)

    rich = [pl for pl in plans if pl.side is State.RICH]
    cheap = [pl for pl in plans if pl.side is State.CHEAP]
    return {
        'fills': fills['equity'] + fills['futures'],
        'fills_by_leg': fills,
        'positions': {'executable_rich': len(rich), 'mirror_cheap': len(cheap),
                      'round_trips': sum(pl.exit_day is not None for pl in plans),
                      'open_at_end': sum(pl.exit_day is None for pl in plans)},
        'assumed_costs': round(costs, 0),
        **summarize(equity_curve, float(p['capital'])),
        'sessions': len(m.window_days),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='pp-backtest')
    ap.add_argument('--window', default='w1')
    a = ap.parse_args(argv)
    out = run_naive(load_market(a.window), load_params())
    print(json.dumps(out, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
