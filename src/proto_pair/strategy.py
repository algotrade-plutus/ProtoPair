"""The pure pair signal both arms replay. No plutus import, no I/O.

Signal (spec 2026-09-15-protopair-design.md §3c): the rolling z-score of the
basis ``VN30F1M_close - VN30_close`` over ``lookback`` sessions.

* ``z >= +z_in`` (future rich vs the basket): the **executable** side --
  long the basket, short the future (state ``RICH``).
* ``z <= -z_in`` (future cheap): the **mirror** side -- short the basket, long
  the future (state ``CHEAP``). It does not exist in Vietnam (no operational
  stock short sale). The signal still emits it: the naive arm trades it, the
  faithful arm attempts it and is refused. That divergence is a Tier-1 count.
* Exit ``RICH`` when ``z <= z_out``, ``CHEAP`` when ``z >= -z_out``, and both
  on a roll boundary (the last session of the front-month dated contract,
  §3e). No entry is taken on a roll-boundary session.

The roll is data-driven off the ``VN30F1M -> dated contract`` map
(``quote.futurecontractcode``); the basket off the VN30 review snapshots
(``quote.vn30``, equal lots, §3a); the hedge is a static notional ratio
``hedge_beta`` snapped to whole contracts (§3b).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from math import sqrt
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

__all__ = ['State', 'Decision', 'PairSignal', 'PairPlan', 'plans_from', 'rolling_z', 'front_month',
           'is_roll_boundary', 'constituents_on', 'hedge_contracts',
           'decide_all']


class State(str, Enum):
    FLAT = 'FLAT'
    RICH = 'RICH'     # long basket / short future: executable
    CHEAP = 'CHEAP'   # short basket / long future: mirror, not executable in VN


@dataclass(frozen=True)
class Decision:
    day: date
    basis: float
    z: Optional[float]
    before: State
    after: State
    reason: str

    @property
    def changed(self) -> bool:
        return self.before is not self.after


def rolling_z(history: Sequence[float], lookback: int) -> Optional[float]:
    """z of the last value against the trailing ``lookback`` values
    (population std). ``None`` while warming up or when the window is flat."""
    if len(history) < lookback:
        return None
    w = list(history)[-lookback:]
    m = sum(w) / lookback
    sd = sqrt(sum((x - m) ** 2 for x in w) / lookback)
    if sd == 0:
        return None
    return (w[-1] - m) / sd


class PairSignal:
    def __init__(self, lookback: int = 60, z_in: float = 1.5,
                 z_out: float = 0.5) -> None:
        self.lookback, self.z_in, self.z_out = lookback, float(z_in), float(z_out)
        self.history: List[float] = []
        self.state = State.FLAT

    def update(self, day: date, future_close: float, index_close: float,
               roll_boundary: bool = False) -> Decision:
        b = float(future_close) - float(index_close)
        self.history.append(b)
        z = rolling_z(self.history, self.lookback)
        before = self.state
        reason = 'hold'
        if before is State.RICH:
            if roll_boundary:
                self.state, reason = State.FLAT, 'roll boundary'
            elif z is not None and z <= self.z_out:
                self.state, reason = State.FLAT, 'basis reverted'
        elif before is State.CHEAP:
            if roll_boundary:
                self.state, reason = State.FLAT, 'roll boundary'
            elif z is not None and z >= -self.z_out:
                self.state, reason = State.FLAT, 'basis reverted'
        elif z is None:
            reason = 'warming up'
        elif roll_boundary:
            reason = 'no entry on a roll boundary'
        elif z >= self.z_in:
            self.state, reason = State.RICH, 'future rich: long basket / short future'
        elif z <= -self.z_in:
            self.state, reason = State.CHEAP, 'future cheap: mirror side'
        return Decision(day, b, z, before, self.state, reason)


# -- the roll (strategy-side glue; plutus has none) --------------------------

def front_month(roll_map: Mapping[date, str], day: date) -> str:
    return roll_map[day]


def is_roll_boundary(roll_map: Mapping[date, str], day: date) -> bool:
    """True iff ``day`` is the last session of its front-month contract (the
    next mapped session carries a different dated contract)."""
    days = sorted(roll_map)
    i = days.index(day)
    return i + 1 < len(days) and roll_map[days[i + 1]] != roll_map[day]


# -- the basket ----------------------------------------------------------------

def constituents_on(snapshots: Mapping[date, Tuple[str, ...]], day: date) -> Tuple[str, ...]:
    """The VN30 membership in force on ``day``: the latest review at or before it."""
    chosen = [d for d in sorted(snapshots) if d <= day]
    if not chosen:
        raise ValueError(f'no VN30 review snapshot in force on {day}')
    return tuple(sorted(snapshots[chosen[-1]]))


# -- the hedge -----------------------------------------------------------------

def hedge_contracts(basket_notional: float, future_price: float,
                    multiplier: float, beta: float = 1.0) -> int:
    """Whole contracts whose notional best matches ``beta x basket_notional``
    (at least one: a pair needs both legs)."""
    return max(1, int(round(beta * basket_notional / (future_price * multiplier))))


def decide_all(days: Sequence[date], future_close: Mapping[date, float],
               index_close: Mapping[date, float], roll_map: Mapping[date, str],
               lookback: int, z_in: float, z_out: float) -> List[Decision]:
    """Run the signal over ``days`` (warm-up included) and return every decision."""
    sig = PairSignal(lookback, z_in, z_out)
    return [sig.update(d, future_close[d], index_close[d], is_roll_boundary(roll_map, d))
            for d in days]


# -- order intents: what both arms are asked to do ---------------------------

@dataclass(frozen=True)
class PairPlan:
    """One pair position the signal asks for. ``exit_day`` is when the signal
    wants it closed (``None``: still open at the window's end)."""
    side: State                     # RICH (executable) or CHEAP (mirror)
    entry_day: date
    exit_day: Optional[date]
    contract: str
    contracts: int
    shares: Tuple[Tuple[str, int], ...]   # (name, shares) -- equal lots

    @property
    def executable(self) -> bool:
        return self.side is State.RICH


def plans_from(decisions: Sequence[Decision], window: Tuple[date, date],
               roll_map: Mapping[date, str],
               snapshots: Mapping[date, Tuple[str, ...]],
               equity_close: Mapping[Tuple[str, date], float],
               future_close: Mapping[date, float], *, lots_per_name: int,
               board_lot: int, price_scale: float, multiplier: float,
               beta: float) -> List[PairPlan]:
    """Turn the decision stream into sized pair plans inside ``window``.

    A position open on the window's first session is not inherited (both arms
    start flat): entries are only taken from in-window decisions.
    """
    start, end = window
    plans: List[PairPlan] = []
    open_: Optional[dict] = None
    for d in decisions:
        if not (start <= d.day <= end):
            continue
        if open_ is not None and d.after is not open_['side']:
            plans.append(PairPlan(exit_day=d.day, **open_))
            open_ = None
        if open_ is None and d.changed and d.after is not State.FLAT:
            names = [n for n in constituents_on(snapshots, d.day)
                     if (n, d.day) in equity_close]
            qty = lots_per_name * board_lot
            notional = sum(equity_close[(n, d.day)] * qty * price_scale for n in names)
            open_ = dict(side=d.after, entry_day=d.day,
                         contract=front_month(roll_map, d.day),
                         contracts=hedge_contracts(notional, future_close[d.day],
                                                   multiplier, beta),
                         shares=tuple((n, qty) for n in names))
    if open_ is not None:
        plans.append(PairPlan(exit_day=None, **open_))
    return plans
