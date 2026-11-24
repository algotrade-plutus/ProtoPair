"""Daily-equity metrics (Tier-2: reported, never gated)."""
from __future__ import annotations

from math import sqrt
from typing import Dict, Sequence


def summarize(equity: Sequence[float], capital: float) -> Dict[str, float]:
    if not equity:
        return {'hpr_pct': 0.0, 'sharpe': 0.0, 'mdd_pct': 0.0, 'final_equity': capital}
    curve = [capital] + list(equity)
    rets = [curve[i] / curve[i - 1] - 1 for i in range(1, len(curve))]
    mean = sum(rets) / len(rets)
    sd = sqrt(sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)) if len(rets) > 1 else 0.0
    peak, mdd = curve[0], 0.0
    for v in curve:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    return {'hpr_pct': round((curve[-1] / capital - 1) * 100, 4),
            'sharpe': round(mean / sd * sqrt(252), 4) if sd else 0.0,
            'mdd_pct': round(mdd * 100, 4),
            'final_equity': round(curve[-1], 0)}
