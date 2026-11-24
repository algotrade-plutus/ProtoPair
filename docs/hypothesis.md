# ProtoPair: hypothesis and pre-registration (9-step, step 1)

Written 2026-11-24. The parameters below are the spec/plan defaults and were not changed after any run. The
activity bar was written **after** the first naive run, with its counts in view, so it is not a genuine
pre-registration; it is stated so a reader can check it, not to claim it was fixed blind.

## Thesis

`VN30F1M` and the VN30 basket are cointegrated, so the basis `F - S` mean-reverts. A desk trades it on the
only side a Vietnamese account can hold: long the basket, short the future when the future is rich. Two
things a naive single-ledger backtest cannot see then decide what a real account can hold:

1. **settlement asymmetry.** The equity leg settles T+2 in the securities pool and the futures leg settles daily
   variation margin in the derivatives pool. The two pools are segregated with no auto-transfer. Shares bought
   to open cannot be sold to close until they settle, so the pair cannot be closed when the signal says.
2. **no short sale.** The mirror trade (short basket, long future) does not exist in Vietnam. The naive arm
   trades it; the faithful arm is refused.

ProtoPair is an **execution-fidelity demonstrator, not an alpha strategy**. The headline is the naive vs faithful
gap. P&L is Tier-2 and never a gate.

## Proceed gate: activity plus credibility, not P&L

- **Credibility** (`pp-credibility`): on each window's daily basis, ADF p < 0.10 **or** a finite OU half-life
  shorter than the window.
- **Activity**: the naive arm signals at least 5 executable and 5 mirror pair positions per window, and several
  of them exit inside the window. A daily pair is chunky, so this is a lower bar than the spec's 20 round trips
  over two years. The windows are a year and a half-year, not the spec's two-year in-sample window.
- No Sharpe or HPR stop-gate is used.

## Fixed parameters (`parameter/pair.json`)

| Parameter | Value | Why |
|---|---|---|
| lookback L | 60 sessions | spec §3c default |
| z_in / z_out | 1.5 / 0.5 | spec plan default, not swept (no optimisation step was run) |
| basket | 1 board lot (100 sh) of each VN30 name, membership from the review in force | spec §3a; the smallest lot-matchable basket |
| hedge | static notional ratio beta = 1.0, snapped to whole contracts at entry | spec §3b (notional match; no OLS fit, no rolling beta) |
| capital | 600,000,000đ; derivatives deposit opens at 0 | handoff T7 |
| deposit target | 80,000,000đ (headline), 62,000,000đ (thin) | handoff T7 |
| naive assumed cost | equity 0.15%/side + 0.1% sell tax; futures 10,000đ/contract/side | spec §3c |
| faithful charges | broker 0.15% HSX trade value, 5,000đ/contract HNXDS, plus Plutus's dated statutory and exchange charges | template `BROKER_PROFILE` |
| margin ladder | warning 0.80 / call 0.90 / forced 1.00; VSD IM from the rulebook (0.13, then 0.17 from 2022-12-15) | spec §3f |
