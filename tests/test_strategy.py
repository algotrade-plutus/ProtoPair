"""Unit tests for the pure pair signal (no plutus, no data)."""
from datetime import date, timedelta

from proto_pair.strategy import (PairSignal, State, constituents_on, hedge_contracts,
                                 is_roll_boundary, plans_from, rolling_z)

D0 = date(2022, 1, 3)


def _feed(sig, pairs, roll=()):
    out = []
    for i, (f, ix) in enumerate(pairs):
        d = D0 + timedelta(days=i)
        out.append(sig.update(d, f, ix, roll_boundary=d in roll))
    return out


def test_rolling_z_warms_up_then_scores():
    assert rolling_z([1.0, 2.0], 3) is None
    assert rolling_z([1.0, 1.0, 1.0], 3) is None          # flat window
    assert rolling_z([0.0, 0.0, 3.0], 3) > 0


def test_rich_entry_and_reversion_exit():
    sig = PairSignal(lookback=5, z_in=1.0, z_out=0.3)
    ds = _feed(sig, [(100, 100), (101, 100), (99, 100), (100, 100), (130, 100), (100, 100)])
    assert ds[4].after is State.RICH and ds[4].changed
    assert ds[5].after is State.FLAT and ds[5].reason == 'basis reverted'


def test_mirror_side_is_emitted_not_dropped():
    sig = PairSignal(lookback=5, z_in=1.0, z_out=0.3)
    ds = _feed(sig, [(100, 100), (101, 100), (99, 100), (100, 100), (70, 100)])
    assert ds[-1].after is State.CHEAP


def test_roll_boundary_forces_exit_and_blocks_entry():
    sig = PairSignal(lookback=5, z_in=1.0, z_out=0.3)
    base = [(100, 100), (101, 100), (99, 100), (100, 100), (130, 100), (131, 100)]
    ds = _feed(sig, base, roll={D0 + timedelta(days=5)})
    assert ds[5].after is State.FLAT and ds[5].reason == 'roll boundary'
    sig2 = PairSignal(lookback=5, z_in=1.0, z_out=0.3)
    ds2 = _feed(sig2, base[:5], roll={D0 + timedelta(days=4)})
    assert ds2[4].after is State.FLAT


def test_roll_map_helpers():
    rmap = {date(2022, 1, 19): 'VN30F2201', date(2022, 1, 20): 'VN30F2202',
            date(2022, 1, 21): 'VN30F2202'}
    assert is_roll_boundary(rmap, date(2022, 1, 19))
    assert not is_roll_boundary(rmap, date(2022, 1, 20))
    assert not is_roll_boundary(rmap, date(2022, 1, 21))


def test_basket_and_hedge():
    snaps = {date(2022, 8, 1): ('B', 'A'), date(2023, 2, 6): ('A', 'C')}
    assert constituents_on(snaps, date(2022, 12, 1)) == ('A', 'B')
    assert constituents_on(snaps, date(2023, 2, 6)) == ('A', 'C')
    assert hedge_contracts(150e6, 1000.0, 100000) == 2
    assert hedge_contracts(40e6, 1000.0, 100000) == 1


def test_plans_carry_size_and_exit():
    sig = PairSignal(lookback=5, z_in=1.0, z_out=0.3)
    pairs = [(100, 100), (101, 100), (99, 100), (100, 100), (130, 100), (100, 100)]
    ds = _feed(sig, pairs)
    days = [d.day for d in ds]
    rmap = {d: 'VN30F2201' for d in days}
    eq = {(n, d): 20.0 for n in ('A', 'B') for d in days}
    plans = plans_from(ds, (days[0], days[-1]), rmap, {days[0]: ('A', 'B')}, eq,
                       {d: 1000.0 for d in days}, lots_per_name=1, board_lot=100,
                       price_scale=1000, multiplier=100000, beta=1.0)
    assert len(plans) == 1
    pl = plans[0]
    assert pl.side is State.RICH and pl.entry_day == days[4] and pl.exit_day == days[5]
    assert pl.shares == (('A', 100), ('B', 100)) and pl.contracts == 1
