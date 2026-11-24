"""The faithful arm: the same pair plans through ``PlutusBackend`` over one
two-venue (``['HSX', 'HNXDS']``) ``ExchangeSession`` (spec §4b).

What Plutus models here, by configuration only: two segregated pools with no
auto-transfer (securities cash / derivatives deposit), each leg admitted by its
own venue's dated rules (lot, tick, band), fills under the chosen
``FillPolicy``, T+2 equity settlement (sale advance off unless the variant
turns it on), the dated VSD initial margin (0.13 -> 0.17 on 2022-12-15) with
the broker ladder (warning 0.80 / call 0.90 / forced 1.00), daily variation
settlement, real dated charges per venue, and expiry cash settlement.

What is caller-side glue, because Plutus has no notion of a pair:

* **the pair coordinator** (:class:`PairCoordinator`): equity legs first; the
  futures leg into an empty deposit is refused, the coordinator reads
  ``funded_in_aggregate`` off the refusal, transfers securities -> derivatives
  to the deposit *target* (not the printed shortfall: the template's finding 3)
  and resubmits; if it still cannot place the futures leg, it cancels the
  equity orders it placed that session (no naked basket) and abandons the pair.
  Once the futures book is flat, the free deposit is swept back.
* **the mirror side**: the coordinator submits the short-basket legs exactly as
  the signal asks; they are refused (no short sale). A mirror pair whose equity
  leg is not fully accepted is abandoned before its futures leg -- a naked
  long future is a different trade -- and counted as an opposite-side trade
  forgone.
* **working the exit**: each session the arm trades every name toward its
  target holding. A name whose excess shares are not yet sellable (bought too
  recently to have settled) cannot be sold; it is retried every session and
  each such session is one *name-day held open* by the settlement asymmetry.
* **margin calls are not answered** (the template's choice): a call that is not
  cured by the mark runs to the broker's forced close, and is counted.

Limit orders are priced at the session's close (the same price the naive arm
fills at) and submitted at 09:30 -- a disclosed same-day look-ahead of a
daily-resolution demonstrator, identical in both arms.
"""
from __future__ import annotations

import json
import os
import tempfile
from collections import Counter, defaultdict
from datetime import date, datetime, time
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from plutus.core.order import OrderType, Side
from plutus.execution import PlutusBackend
from plutus.market.adapters.datahub import DataHubSource
from plutus.market.protocol import Order
from plutus.market.session.types import Pool

from proto_pair.data import Market, settlement_calendar
from proto_pair.metrics import summarize
from proto_pair.strategy import PairPlan, State

OPEN, CLOSE = time(9, 30), time(14, 45)
_ZERO = Decimal('0')


def _rule(outcome) -> str:
    r = getattr(outcome, 'rule', None)
    return str(getattr(r, 'value', r))


def _accepted(outcome) -> bool:
    return hasattr(outcome, 'venue') and not hasattr(outcome, 'rule')


def session_config(m: Market, p: dict, *, fill_policy: str = 'soft',
                   sale_advance: bool = False, calendar_path: str = '') -> dict:
    profile = dict(p['broker_profile'])
    profile['advance_sale_proceeds'] = {'enabled': bool(sale_advance),
                                        'daily_rate': p['sale_advance_daily_rate']}
    return {
        'period': {'start': m.window[0].isoformat(), 'end': m.window[1].isoformat()},
        'resolution': '1d',
        'exchange_rules': {'venues': ['HSX', 'HNXDS'], 'rulebook': 'vn-2020-2026',
                           'pins': []},
        'accounts': {'securities': {'initial_cash': str(p['capital'])},
                     'derivatives': {'initial_deposit': '0'}},
        'fill_policy': {'kind': fill_policy},
        'broker_profile': profile,
        'data': {'settlement_calendar': calendar_path} if calendar_path else {},
    }


class FaithfulArm:
    def __init__(self, m: Market, p: dict, *, deposit_target: int,
                 fill_policy: str = 'soft', sale_advance: bool = False) -> None:
        self.m, self.p = m, p
        self.deposit_target = Decimal(deposit_target)
        self.source = DataHubSource.for_root(str(m.root))
        self.calendar = settlement_calendar(m)
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fh:
            json.dump(self.calendar, fh)
        self.backend = PlutusBackend.from_config(
            session_config(m, p, fill_policy=fill_policy, sale_advance=sale_advance,
                           calendar_path=fh.name),
            source=self.source)
        os.unlink(fh.name)
        self.now: Optional[datetime] = None
        # -- holdings targets (what the arm is trying to hold) --
        self.target_eq: Dict[str, int] = {}
        self.target_fut: Dict[str, int] = {}
        self.names_seen: set = set()
        self.contracts_seen: set = set()
        self.held_plan: Optional[PairPlan] = None
        # -- Tier-1 tallies --
        self.refusals: Dict[str, Counter] = defaultdict(Counter)
        self.submit_indeterminate: Counter = Counter()
        self.events: Counter = Counter()
        self.fills = Counter()
        self.transfers_in: List[Decimal] = []
        self.sweeps: List[Decimal] = []
        self.funding = Counter()
        self.exit_records: List[dict] = []
        self.blocked_name_days = 0
        self.unfilled_exit_name_days = 0
        self.mirror = Counter()
        self.entries = Counter()
        self.expiry: List[dict] = []
        self.equity_curve: List[float] = []
        self.im_at_entry: List[dict] = []
        self.hedge_retries = 0          # sessions the basket sat without its hedge

    # -- session plumbing ---------------------------------------------------
    def _price(self, ticker: str) -> Optional[Decimal]:
        st = self.source.state_at(ticker, self.now)
        return None if st is None else st.last

    def _submit(self, ticker: str, side: Side, qty: int):
        price = self._price(ticker)
        if price is None or qty <= 0:
            return None
        out = self.backend.submit(Order(ticker=ticker, side=side, quantity=int(qty),
                                        order_type=OrderType.LIMIT, limit_price=price))
        if not _accepted(out):
            venue = 'HNXDS' if ticker.startswith('VN30F') else 'HSX'
            verdict = str(getattr(getattr(out, 'verdict', None), 'value', ''))
            if verdict == 'indeterminate':
                self.submit_indeterminate[f'{venue}:{_rule(out)}'] += 1
            else:
                self.refusals[venue][_rule(out)] += 1
        return out

    def _tally(self, events) -> None:
        for e in events:
            kind = str(getattr(e.kind, 'value', e.kind))
            self.events[kind] += 1
            if kind in ('filled', 'partially_filled'):
                venue = str(getattr(e.venue, 'value', e.venue))
                self.fills[venue] += 1
            if kind == 'expiry_settled':
                self.expiry.append({k: str(v) for k, v in
                                    {'ticker': e.ticker, 'ts': e.ts, **e.detail}.items()})

    # -- the coordinator ------------------------------------------------------
    def _fund_and_place_future(self, contract: str, side: Side, qty: int) -> bool:
        out = self._submit(contract, side, qty)
        if out is None:
            return False
        if _accepted(out):
            self.funding['placed_without_transfer'] += 1
            return True
        detail = getattr(out, 'detail', {}) or {}
        if _rule(out) != 'insufficient_deposit':
            return False
        if not detail.get('funded_in_aggregate'):
            self.funding['funded_in_aggregate_false'] += 1
            return False
        self.funding['funded_in_aggregate_true'] += 1
        need = self.deposit_target - self.backend.margin().deposit_balance
        if need <= _ZERO:
            need = Decimal(detail.get('shortfall', 0))
        moved = self.backend.transfer(Pool.SECURITIES, Pool.DERIVATIVES, need)
        if not hasattr(moved, 'amount') or hasattr(moved, 'rule'):
            self.funding['transfer_refused'] += 1
            return False
        self.transfers_in.append(Decimal(moved.amount))
        again = self._submit(contract, side, qty)
        return again is not None and _accepted(again)

    def _cancel(self, order_ids: List[str]) -> None:
        for oid in order_ids:
            self.backend.cancel(oid)

    def _enter(self, pl: PairPlan) -> None:
        self.entries[pl.side.value] += 1
        eq_side = Side.BUY if pl.side is State.RICH else Side.SELL
        placed, refused = [], 0
        for name, q in pl.shares:
            self.names_seen.add(name)
            if pl.side is State.RICH:
                held = self.backend.holdings(name).total
                qty = max(0, q - held)        # leftovers of a blocked exit count
                if qty == 0:
                    continue
            else:
                qty = q
            out = self._submit(name, eq_side, qty)
            if out is not None and _accepted(out):
                placed.append(out.order_id)
            else:
                refused += 1
        if pl.side is State.CHEAP:
            self.mirror['attempted'] += 1
            self.mirror['equity_legs_refused'] += refused
            if refused:
                self._cancel(placed)
                self.mirror['forgone'] += 1
                return
            # the whole short basket was accepted (only possible on settled
            # leftovers); place the long future without funding glue
            ok = self._fund_and_place_future(pl.contract, Side.BUY, pl.contracts)
            if not ok:
                self._cancel(placed)
                self.mirror['forgone'] += 1
                return
            self.mirror['opened'] += 1
            return
        fut_side = Side.SELL
        self.contracts_seen.add(pl.contract)
        if not self._fund_and_place_future(pl.contract, fut_side, pl.contracts):
            self._cancel(placed)
            self.funding['abandoned'] += 1
            return
        self.held_plan = pl
        for name, q in pl.shares:
            self.target_eq[name] = q
        self.target_fut = {pl.contract: -pl.contracts}

    def _flatten_targets(self) -> None:
        self.target_eq = {}
        self.target_fut = {}
        self.held_plan = None

    def _work(self, exit_today: Optional[PairPlan]) -> None:
        """Trade every name and contract toward its target; record what the
        settlement asymmetry blocks."""
        blocked_names = []
        for name in sorted(self.names_seen):
            h = self.backend.holdings(name)
            excess = h.total - self.target_eq.get(name, 0)
            if excess <= 0:
                continue
            sellable = min(h.sellable, excess)
            if sellable > 0:
                self._submit(name, Side.SELL, sellable)
            if excess > h.sellable:
                self.blocked_name_days += 1
                blocked_names.append(name)
        for contract in sorted(self.contracts_seen):
            pos = self.backend.positions().get(contract)
            net = pos.net_quantity if pos is not None else 0
            target = self.target_fut.get(contract, 0)
            diff = target - net
            if not diff:
                continue
            side = Side.BUY if diff > 0 else Side.SELL
            if abs(target) > abs(net):
                # the hedge leg is short of target (its order did not fill):
                # the basket has been naked since; place it again, funded
                self.hedge_retries += 1
                self._fund_and_place_future(contract, side, abs(diff))
            else:
                self._submit(contract, side, abs(diff))
        if exit_today is not None:
            self.exit_records.append({'plan_entry': exit_today.entry_day.isoformat(),
                                      'exit_wanted': exit_today.exit_day.isoformat(),
                                      'names_blocked_on_exit_day': len(blocked_names)})

    def _sweep(self) -> None:
        if any(p.net_quantity for p in self.backend.positions().values()):
            return
        free = self.backend.margin().free_deposit
        if free > _ZERO and self.held_plan is None:
            out = self.backend.transfer(Pool.DERIVATIVES, Pool.SECURITIES, free)
            if hasattr(out, 'amount') and not hasattr(out, 'rule'):
                self.sweeps.append(Decimal(out.amount))

    def _record_im(self, d: date, entered: List[PairPlan]) -> None:
        """The dated VSD initial-margin rate the session charged on each
        opened futures leg: IM / (|net| x close x multiplier)."""
        for pl in entered:
            pos = self.backend.positions().get(pl.contract)
            if pl.side is not State.RICH or pos is None or not pos.net_quantity:
                continue
            mv = self.backend.margin()
            notional = Decimal(abs(pos.net_quantity)) * Decimal(str(
                self.m.contract_close[(pl.contract, d)])) * pos.multiplier
            self.im_at_entry.append({'day': d.isoformat(), 'contract': pl.contract,
                                     'contracts': abs(pos.net_quantity),
                                     'initial_margin_dong': str(mv.initial_margin),
                                     'im_rate': str(round(mv.initial_margin / notional, 4))})

    def _mark(self, d: date) -> float:
        cash = self.backend.cash()
        value = float(cash.settled_balance + cash.pending_total - cash.interest_accrued)
        scale = self.p['price_scale']
        for name in self.names_seen:
            h = self.backend.holdings(name)
            if h.total:
                px = self.m.equity_close.get((name, d))
                if px is None:
                    px = max((v for (n, dd), v in self.m.equity_close.items()
                              if n == name and dd <= d), default=0.0)
                value += h.total * px * scale
        value += float(self.backend.margin().deposit_balance)
        return value

    # -- the run -----------------------------------------------------------------
    def run(self, plans: List[PairPlan]) -> dict:
        entries = defaultdict(list)
        exits = defaultdict(list)
        for pl in plans:
            entries[pl.entry_day].append(pl)
            if pl.exit_day is not None:
                exits[pl.exit_day].append(pl)
        for d in self.m.window_days:
            self.now = datetime.combine(d, OPEN)
            self._tally(self.backend.advance_to(self.now))
            self._sweep()
            exit_today = None
            for pl in exits.get(d, []):
                if pl.side is State.RICH:
                    exit_today = pl
                    if self.held_plan is pl:
                        self._flatten_targets()
            self._work(exit_today if exit_today is not None else None)
            for pl in entries.get(d, []):
                self._enter(pl)
            self.now = datetime.combine(d, CLOSE)
            self._tally(self.backend.advance_to(self.now))
            self._record_im(d, entries.get(d, []))
            self.equity_curve.append(self._mark(d))
        return self.result(plans)

    def result(self, plans: List[PairPlan]) -> dict:
        rich_exits = [pl for pl in plans if pl.side is State.RICH and pl.exit_day is not None]
        blocked = [r for r in self.exit_records if r['names_blocked_on_exit_day']]
        charges = defaultdict(Decimal)
        for ch in self.backend.charges():
            charges[str(getattr(ch.venue, 'value', ch.venue))] += ch.amount
        rep = self.backend.indeterminate_report()
        fills = sum(self.fills.values())
        return {
            'fills': fills,
            'fills_by_venue': dict(self.fills),
            'tier1': {
                'settlement_asymmetry': {
                    'executable_entries_signalled': sum(pl.side is State.RICH for pl in plans),
                    'executable_entries_opened': self.entries['RICH'] - self.funding['abandoned'],
                    'exits_wanted': len(rich_exits),
                    'exits_blocked_by_t2': len(blocked),
                    'name_days_held_open': self.blocked_name_days,
                    'hedge_leg_unfilled_session_retries': self.hedge_retries,
                    'exit_records': self.exit_records,
                },
                'opposite_side': {
                    'mirror_trades_signalled': sum(pl.side is State.CHEAP for pl in plans),
                    'attempted': self.mirror['attempted'],
                    'forgone': self.mirror['forgone'],
                    'opened': self.mirror['opened'],
                    'equity_legs_refused': self.mirror['equity_legs_refused'],
                },
                'funding': {
                    'transfers_in': len(self.transfers_in),
                    'transferred_in_dong': str(sum(self.transfers_in, _ZERO)),
                    'sweeps_back': len(self.sweeps),
                    'swept_back_dong': str(sum(self.sweeps, _ZERO)),
                    **dict(self.funding),
                },
                'margin': {k: self.events.get(k, 0) for k in
                           ('margin_warning', 'margin_call', 'margin_call_cleared',
                            'forced_liquidation')},
                'expiry_settlements': self.expiry,
                'dated_im_at_entry': self.im_at_entry,
                'refusals_by_cause': {v: dict(c) for v, c in self.refusals.items()},
                'submit_indeterminate': dict(self.submit_indeterminate),
                'fill_time_indeterminate_events': self.events.get('indeterminate', 0),
                'charges_by_venue_dong': {k: str(v) for k, v in charges.items()},
                'indeterminate_report': str(rep)[:2000],
            },
            'provenance': {
                'settlement_calendar_id': str(self.backend.session.provenance()
                                              .settlement_calendar_id),
                'settlement_calendar_source': self.calendar['source'],
            },
            **summarize(self.equity_curve, float(self.p['capital'])),
        }


def run_faithful(m: Market, p: dict, plans: List[PairPlan], **kw) -> dict:
    return FaithfulArm(m, p, **kw).run(plans)
