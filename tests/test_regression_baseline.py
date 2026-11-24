"""Pin the naive arm on the shipped slices (the behaviour-preserving anchor).

The values are what `pp-backtest --window w1|w2` printed when the anchor was
recorded; a change here means the naive arm (or its data) changed.
"""
import pytest

from proto_pair.backtest import run_naive
from proto_pair.data import load_market, load_params

BASELINE = {
    'w1': {'fills': 1209, 'executable_rich': 11, 'mirror_cheap': 9, 'round_trips': 19,
           'hpr_pct': 1.0278, 'final_equity': 606166888.0},
    'w2': {'fills': 775, 'executable_rich': 7, 'mirror_cheap': 6, 'round_trips': 12,
           'hpr_pct': 0.2766, 'final_equity': 601659790.0},
}


@pytest.mark.parametrize('window', sorted(BASELINE))
def test_naive_reproduces_its_baseline(window):
    r = run_naive(load_market(window), load_params())
    b = BASELINE[window]
    assert r['fills'] == b['fills']
    assert r['positions']['executable_rich'] == b['executable_rich']
    assert r['positions']['mirror_cheap'] == b['mirror_cheap']
    assert r['positions']['round_trips'] == b['round_trips']
    assert r['hpr_pct'] == pytest.approx(b['hpr_pct'], abs=1e-4)
    assert r['final_equity'] == pytest.approx(b['final_equity'], abs=1.0)
