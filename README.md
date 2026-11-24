# ProtoPair

An equal-lot VN30 proxy basket (long, HSX) against the front-month `VN30F1M` future (short, HNXDS), traded on the
daily basis `F - S`. It is the fourth point of the Plutus execution-fidelity spectrum (SB, Grid, MM, **Pair**) and the
only strategy that trades **two venues and two segregated pools at once**. ProtoPair is a demonstrator, not an alpha
strategy: the result is the gap between a naive single-ledger backtest and the same signals executed through the
faithful Plutus market. Rebuilt from scratch for the RIVF'26 camera-ready (handoff task T7) from
`plutus-simulator/docs/superpowers/specs/2026-09-15-protopair-design.md`. No earlier Pair code was used.

## Hypothesis

See `docs/hypothesis.md`. In short: the basis mean-reverts (checked by `pp-credibility`). A real Vietnamese
account can hold only the future-rich side, and can only close it once the shares bought to open have settled
T+2. A naive single ledger sees neither constraint.

## Layout

| Path | What |
|---|---|
| `src/proto_pair/strategy.py` | **Pure signal** (no plutus import): basis z-score, RICH/CHEAP/FLAT states, roll boundary, VN30 membership, hedge snap, sized `PairPlan` intents |
| `src/proto_pair/backtest.py` | **Naive arm** (`pp-backtest`): one ledger, shorting allowed, fills at close, no admission, static assumed cost |
| `src/proto_pair/faithful.py` | **Faithful arm**: the same plans through `plutus.execution.PlutusBackend` over a two-venue `ExchangeSession`, plus the caller-side pair coordinator |
| `src/proto_pair/experiments/pair_anchor.py` | Runner (`pp-anchor`) → `result/pair_anchor/<window>.json` with `naive`, `faithful`, `tier1`, `variants` blocks |
| `src/proto_pair/experiments/credibility_check.py` | `pp-credibility` → `result/credibility/<window>.json` (ADF + OU half-life) |
| `src/proto_pair/experiments/extract.py` | `pp-extract`: VN30 membership + roll map from the DB, and the exact request for the shared extraction tool |
| `data/market/<window>/` | The frozen daily slice per window, with `DATA-MANIFEST.md` and `request.json` |
| `tests/` | signal unit tests, request test, naive regression baseline, faithful smoke test |

## Modelling choices

**Both arms** replay one decision stream (`strategy.decide_all`, then `plans_from`):
- The basis is the dated front-month close minus the `VN30` index close. The z-score uses a 60-session lookback.
- Enter RICH (long basket, short future) at z ≥ 1.5 and exit at z ≤ 0.5. CHEAP is the mirror: enter at z ≤ −1.5,
  exit at z ≥ −0.5.
- Both states exit on the last session of the front-month contract (the roll, read from
  `quote.futurecontractcode` VN30F1M → dated code). No entry is taken on that session. The next front month is
  entered only on a fresh signal.
- The basket is 100 shares of each name in the VN30 review in force on the entry day. The hedge is
  `round(basket notional / (F × 100,000đ))` contracts, at least one. That is one contract throughout both windows.
- Orders are priced at the session's close in both arms. The faithful arm submits them at 09:30 and they fill at
  14:45. Deciding on the day's close and trading at that close is a same-day look-ahead, disclosed and identical in
  both arms.

**Naive arm**: one ledger with no segregation, T+2 or margin. Shorting is allowed, so it trades the CHEAP plans.
Fills are frictionless at the close. Costs are 0.15% a side plus 0.1% sell tax on equity, and 10,000đ per contract a
side on futures.

**Faithful arm** (`soft` fills, deposit target 80,000,000đ, T+2 on, sale advance off):
- **Venues and pools.** `venues=['HSX','HNXDS']`. There are two segregated pools with no auto-transfer. Capital is
  600,000,000đ in securities, and the derivatives deposit opens at **0đ**.
- **Admission and rules.** Each leg is admitted by its own venue's dated rules. The engine's dated VSD initial
  margin is used: the measured IM rate on every opened leg is 0.13 before 2022-12-15 and 0.17 after (recorded per
  entry in `tier1.dated_im_at_entry`). The broker ladder is 0.80/0.90/1.00, variation margin settles daily, and real
  dated charges apply per venue.
- **Settlement calendar.** It is derived from the slice: weekdays with no HOSE session are closures. It is not a
  VSDC notice, and `provenance` in the result says so. It replaces the session default
  `weekday-only-UNSOURCED`, which ignores every holiday.
- **Caller-side glue** (`FaithfulArm`). Equity legs are submitted first. The futures leg is refused
  `INSUFFICIENT_DEPOSIT`; the arm reads `funded_in_aggregate`, transfers securities→derivatives up to the deposit
  target, and resubmits. If the leg still cannot be placed, the arm cancels that session's equity orders and abandons
  the pair. Once the futures book is flat, the free deposit is swept back. Each session every name is traded toward
  its target holding. Excess shares that are not yet sellable stay held, and each such session is one **name-day
  held open**.
- **Mirror side.** CHEAP plans are submitted as the signal asks (short-basket sells). Any refused equity leg
  cancels the rest, and the long future is never placed.
- **Margin calls** are not answered: a call the mark does not cure runs to the broker's forced close.
- **Hedge retry.** If a hedge leg is accepted but does not fill, the arm re-places it (funded) on the next session.
- **Variants:** `thin` (deposit target 62,000,000đ), `hard` (fill policy), and `sale_advance` (advance on, 0.03%/day).

**Units.** The slice stores prices in **thousands of đồng** (DB unit). All cash, P&L and costs are real đồng:
equity value = price × 1,000 × shares; futures = points × 100,000đ × contracts.

## Windows, and why they are minimal

| Window | Span | Sessions | Why |
|---|---|---:|---|
| `w1` (headline) | 2022-08-01 → 2023-08-04 | 254 | Contains the 2022-12-15 IM step (entries on both sides of it), 12 front-month rolls, one VN30 re-constitution (2023-02-06), and 20 signalled positions. Starts on the 2022-08-01 review because the DB has no 2022-02 snapshot, and ends before the 2023-08-07 review. |
| `w2` (robustness) | 2023-08-07 → 2024-02-02 | 127 | One whole review period (2023-08-07; the DB has no 2024-02/2024-08 snapshot, so it cannot run longer on correct membership). Post-step IM 0.17 throughout, 6 rolls, 13 positions. Does not overlap `w1` or reach the 2025-05-05 KRX cutover. |

Each slice also carries the close-only signal warm-up (59 sessions of `VN30` and front-month closes before the
window). The old window was 2022-01-01 → 2023-12-31. These two windows together are shorter, and each stands
alone. Per-file detail is in `data/market/<window>/DATA-MANIFEST.md`.

## Results (plutus-simulator `b62e163`, as recorded in `result/pair_anchor/<window>.json`)

| Window | fills n → f (f/n) | HPR n → f | exits blocked by T+2 | name-days held open | opposite-side trades forgone |
|---|---|---|---|---|---|
| w1 | 1,209 → 651 (0.538) | +1.03% → −2.15% | 8 of 10 | 420 | 9 of 9 |
| w2 | 775 → 403 (0.520) | +0.28% → −0.31% | 4 of 6 | 180 | 6 of 6 |

Every cross-pool funding need was `funded_in_aggregate` and funded on demand: w1 had 11 transfers (880,000,000đ in)
and 10 sweeps back. No pair was abandoned. There were 0 margin calls and 0 forced liquidations at both deposit
targets, because a one-contract hedge never stresses the ladder. No leg was carried to expiry, so `CLOSE_PROXY`
was not exercised. The sale advance does not change a single blocked exit: the stall is on unsettled *purchases*.
`hard` still fills daily LIMIT orders here (w1: 583 fills, 71 fill-time INDETERMINATE). The full blocks are in
`result/pair_anchor/<window>.json`.

## Regenerate

```bash
python3.15 -m venv .venv && .venv/bin/pip install -e <plutus-simulator> -e . pytest
.venv/bin/pp-credibility        # result/credibility/w1.json, w2.json
.venv/bin/pp-anchor             # result/pair_anchor/w1.json, w2.json (about 35 s)
.venv/bin/python -m pytest -q
```

To re-extract the slice from the DB (needs read access; credentials are read by the shared tool at runtime):

```bash
export RIVF26_EXTRACT=<plutus-simulator>/scripts/rivf26_extract.py
.venv/bin/pp-extract meta --window w1           # quote_vn30, quote_futurecontractcode, request.json
<plutus-simulator>/.venv/bin/python "$RIVF26_EXTRACT" declared --source db \
    --experiment pair-daily-w1 --request data/market/w1/request.json
cp <rivf26-data>/pair-daily-w1/quote_*.parquet data/market/w1/
```

## Data manifest

`data/market/w1/DATA-MANIFEST.md` and `data/market/w2/DATA-MANIFEST.md`. They give the source tables, the query
shape, tickers × ranges per file, rows, bytes and sha256, and why each window is minimal. The data is
confidential Algotrade data, committed only to reproduce this result. Do not push it without the owner's sign-off.
