"""The faithful arm runs end to end through PlutusBackend on the shipped slice,
and the pair mechanics fire: funding on demand, T+2-blocked exit, refused
mirror side. A short sub-run (first RICH and first CHEAP plan of w1)."""
from proto_pair.backtest import signal_plans
from proto_pair.data import load_market, load_params
from proto_pair.faithful import run_faithful
from proto_pair.strategy import State


def test_faithful_arm_exercises_the_pair_axes():
    m, p = load_market('w1'), load_params()
    plans = signal_plans(m, p)
    rich = next(pl for pl in plans if pl.side is State.RICH)
    cheap = next(pl for pl in plans if pl.side is State.CHEAP)
    m.window_days = [d for d in m.window_days if d <= rich.exit_day + __import__(
        'datetime').timedelta(days=7)]
    r = run_faithful(m, p, [cheap, rich], deposit_target=p['deposit_target']['comfortable'])
    t = r['tier1']
    assert r['fills'] > 0
    assert t['funding']['transfers_in'] == 1 and t['funding']['funded_in_aggregate_true'] == 1
    assert t['opposite_side']['forgone'] == 1
    assert t['refusals_by_cause']['HSX']['unsettled_holding'] == len(cheap.shares)
    assert t['settlement_asymmetry']['exits_blocked_by_t2'] == 1
    assert t['settlement_asymmetry']['name_days_held_open'] > 0
    assert t['dated_im_at_entry'][0]['im_rate'] == '0.1300'
