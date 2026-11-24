"""``pp-credibility``: does the basis mean-revert? (the credibility half of the
pre-registered proceed gate, spec §2). Not a P&L test.

For each window, on the daily basis ``VN30F1M_close - VN30_close`` over the
window's sessions (the continuous front month, so the series carries the roll
jumps the signal itself sees):

* the augmented Dickey-Fuller test (``statsmodels.adfuller``, constant, lag
  order by AIC): p < 0.10 rejects a unit root;
* the Ornstein-Uhlenbeck half-life from the AR(1) fit
  ``delta_b_t = a + phi * b_{t-1} + e``: ``-ln 2 / ln(1 + phi)`` sessions,
  finite iff ``phi < 0``.

Pass = ADF p < 0.10 **or** a finite half-life shorter than the window. The
thresholds are the spec's, fixed before any run.

Writes ``result/credibility/<window>.json``.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, Optional, Sequence

import numpy as np
from statsmodels.tsa.stattools import adfuller

from proto_pair.data import REPO, load_market

ADF_MAX_P = 0.10


def half_life(series: Sequence[float]) -> Optional[float]:
    x = np.asarray(series, dtype=float)
    lag, dx = x[:-1], np.diff(x)
    a = np.column_stack([np.ones_like(lag), lag])
    _, phi = np.linalg.lstsq(a, dx, rcond=None)[0]
    if phi >= 0 or phi <= -1:
        return None if phi >= 0 else 0.0
    return float(-math.log(2) / math.log(1 + phi))


def credibility(series: Sequence[float]) -> Dict:
    stat, p, lags, nobs, crit, _ = adfuller(np.asarray(series, dtype=float),
                                            regression='c', autolag='AIC',
                                            result_object=False)
    hl = half_life(series)
    return {'n_sessions': len(series),
            'adf_stat': round(float(stat), 4), 'adf_pvalue': float(f'{p:.4e}'),
            'adf_lags': int(lags), 'adf_crit': {k: round(float(v), 4) for k, v in crit.items()},
            'ou_half_life_sessions': None if hl is None else round(hl, 4),
            'pass_adf': bool(p < ADF_MAX_P),
            'pass_half_life': hl is not None and hl < len(series),
            'credible': bool(p < ADF_MAX_P) or (hl is not None and hl < len(series))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='pp-credibility')
    ap.add_argument('--window', action='append', default=None)
    a = ap.parse_args(argv)
    out_dir = REPO / 'result' / 'credibility'
    out_dir.mkdir(parents=True, exist_ok=True)
    for w in a.window or ['w1', 'w2']:
        m = load_market(w)
        basis = [m.future_close[d] - m.index_close[d] for d in m.window_days]
        res = {'window': w, 'start': m.window[0].isoformat(), 'end': m.window[1].isoformat(),
               'series': 'VN30F1M (dated front month) close - VN30 index close, daily',
               **credibility(basis)}
        (out_dir / f'{w}.json').write_text(json.dumps(res, indent=1) + '\n')
        print(json.dumps(res))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
