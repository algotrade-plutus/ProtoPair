# DATA-MANIFEST: pair-daily-w1

- **Reproduces:** ProtoPair (T7) naive vs faithful anchor, window w1: result/pair_anchor/w1*.json
- **Extraction mode:** `declared`
- **Command:** `rivf26_extract.py declared --source db --force --experiment pair-daily-w1 --reproduces ProtoPair (T7) naive vs faithful anchor, window w1: result/pair_anchor/w1*.json --request data/market/w1/request.json`
- **Source:** Algotrade PostgreSQL DB, schema `quote` (read-only transaction). File `<prefix>_<x>.<ext>` holds rows of DB table `quote.<x>`.
- **Extracted on:** 2026-11-24 with `scripts/rivf26_extract.py` (pyarrow 26.0.1; writer settings fixed in `WRITER`).
- **Total size:** 168,164 bytes (164.2 KiB) in 9 files.

## Why this window is minimal

**Window w1 = 2022-08-01 -> 2023-08-04 (254 sessions), the headline.** It is the shortest span that contains
everything the Pair row has to show at once: the dated VSD initial-margin step **0.13 -> 0.17 on 2022-12-15**
(entries on both sides of it: IM rate 0.13 through 2022-12-02, 0.17 from 2023-03-10), **12 front-month rolls**
(VN30F2208 ... VN30F2307 expire inside it), one **VN30 re-constitution** (review snapshots 2022-08-01 and
2023-02-06, both in `quote_vn30.parquet`), and enough signal activity to count exits: 20 signalled pair
positions (11 executable, 9 mirror), 19 round trips. It starts on the 2022-08-01 review because the DB has no
2022-02 review snapshot (an earlier start would run on a stale membership list) and ends the session before
the 2023-08-07 review (so no third membership list is needed).

**Tickers:** the 31 names in either review snapshot (equal-lot basket), the 13 dated VN30F1M contracts that
are front month inside the window, and the `VN30` index level. **Fields:** the 8 daily fields the session reads
(close, open, max, min, ceil, floor, reference, dailyvolume) for basket names over the window and for each
contract only over the sessions it is front month; `quote_close` alone for `VN30` and the front month over the
59 sessions before the window (signal warm-up: lookback 60), so `VN30F2205`..`VN30F2207` appear in close only.
`quote_ticker` master rows route each ticker to its venue. `quote_vn30.parquet` and
`quote_futurecontractcode.parquet` (VN30F1M rows only) were read by `pp-extract meta` (ProtoPair) because the
shared tool does not carry those tables. Total about 0.2 MB.

## Files

| File | Rows | Bytes | sha256 |
|---|---:|---:|---|
| `quote_ceil.parquet` | 8,127 | 17,405 | `453dc3ba5f56cee98d33b2265185b4a42275728b383ae5a85bed452b30b6f131` |
| `quote_close.parquet` | 8,500 | 21,135 | `9d1f11e832e2714b144701042dc4fff1445e33433ca673e9c0dccf089fa0da76` |
| `quote_dailyvolume.parquet` | 8,128 | 40,072 | `5e9804c37848cb99e9a1f608854b1dddc93997ce6742493eea7dc3b649c539d7` |
| `quote_floor.parquet` | 8,127 | 17,397 | `e3ac9e03a5704b1de9c36cbe0fde8e4dfcfc83a4dfcef595aa25e21515b4f4a0` |
| `quote_max.parquet` | 8,128 | 17,481 | `cfb0cc19cff8805a95c3c41b2f8450010ceeee5817e6074c451ce0799b0d4236` |
| `quote_min.parquet` | 8,128 | 17,530 | `52b36745d772a961625ecc79a7ccb4bedd43f7b726ed1e9b2ff8a1244cf6086f` |
| `quote_open.parquet` | 8,128 | 17,467 | `169e82af9b97898a2dae83353abdb1156a8b31d1bb5fc072c73200b335afafaa` |
| `quote_reference.parquet` | 8,130 | 17,464 | `2eabd11ffcca31b1fb6555fc1ea8a80fe7f256a842e5976f87fb9a3d078a4dd8` |
| `quote_ticker.parquet` | 48 | 2,213 | `dc15828c569e9a88da086b7c97e9aba48aafee0ed0c4f336c33ffefcfb50b4c1` |

## Files added by ProtoPair `pp-extract meta` (not the shared tool)

| File | Rows | Bytes | sha256 | Query |
|---|---:|---:|---|---|
| `quote_vn30.parquet` | 60 | 744 | `377cc47f637082c37db0e56bd114241d4fd140510dc6a5c91e28f86350c44428` | `quote.vn30` rows of the review snapshots in force over the window |
| `quote_futurecontractcode.parquet` | 324 | 1,625 | `2126958f5c51924ac9a8934a48a09024206d37da7acb69143decf48c9cc98ead` | `quote.futurecontractcode WHERE futurecode = 'VN30F1M'` over [warm-up start, window end] |

## Contents (tickers, ranges, fields, query)

### `quote_ceil.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.ceil WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2022-08-01, 2023-08-05)
- `BCM`: [2022-08-01, 2023-08-05)
- `BID`: [2022-08-01, 2023-08-05)
- `BVH`: [2022-08-01, 2023-08-05)
- `CTG`: [2022-08-01, 2023-08-05)
- `FPT`: [2022-08-01, 2023-08-05)
- `GAS`: [2022-08-01, 2023-08-05)
- `GVR`: [2022-08-01, 2023-08-05)
- `HDB`: [2022-08-01, 2023-08-05)
- `HPG`: [2022-08-01, 2023-08-05)
- `KDH`: [2022-08-01, 2023-08-05)
- `MBB`: [2022-08-01, 2023-08-05)
- `MSN`: [2022-08-01, 2023-08-05)
- `MWG`: [2022-08-01, 2023-08-05)
- `NVL`: [2022-08-01, 2023-08-05)
- `PDR`: [2022-08-01, 2023-08-05)
- `PLX`: [2022-08-01, 2023-08-05)
- `POW`: [2022-08-01, 2023-08-05)
- `SAB`: [2022-08-01, 2023-08-05)
- `SSI`: [2022-08-01, 2023-08-05)
- `STB`: [2022-08-01, 2023-08-05)
- `TCB`: [2022-08-01, 2023-08-05)
- `TPB`: [2022-08-01, 2023-08-05)
- `VCB`: [2022-08-01, 2023-08-05)
- `VHM`: [2022-08-01, 2023-08-05)
- `VIB`: [2022-08-01, 2023-08-05)
- `VIC`: [2022-08-01, 2023-08-05)
- `VJC`: [2022-08-01, 2023-08-05)
- `VN30F2208`: [2022-08-01, 2022-08-19)
- `VN30F2209`: [2022-08-19, 2022-09-16)
- `VN30F2210`: [2022-09-16, 2022-10-21)
- `VN30F2211`: [2022-10-21, 2022-11-18)
- `VN30F2212`: [2022-11-18, 2022-12-16)
- `VN30F2301`: [2022-12-16, 2023-01-20)
- `VN30F2302`: [2023-01-20, 2023-02-17)
- `VN30F2303`: [2023-02-17, 2023-03-17)
- `VN30F2304`: [2023-03-17, 2023-04-21)
- `VN30F2305`: [2023-04-21, 2023-05-19)
- `VN30F2306`: [2023-05-19, 2023-06-16)
- `VN30F2307`: [2023-06-16, 2023-07-21)
- `VN30F2308`: [2023-07-21, 2023-08-05)
- `VNM`: [2022-08-01, 2023-08-05)
- `VPB`: [2022-08-01, 2023-08-05)
- `VRE`: [2022-08-01, 2023-08-05)

### `quote_close.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.close WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2022-08-01, 2023-08-05)
- `BCM`: [2022-08-01, 2023-08-05)
- `BID`: [2022-08-01, 2023-08-05)
- `BVH`: [2022-08-01, 2023-08-05)
- `CTG`: [2022-08-01, 2023-08-05)
- `FPT`: [2022-08-01, 2023-08-05)
- `GAS`: [2022-08-01, 2023-08-05)
- `GVR`: [2022-08-01, 2023-08-05)
- `HDB`: [2022-08-01, 2023-08-05)
- `HPG`: [2022-08-01, 2023-08-05)
- `KDH`: [2022-08-01, 2023-08-05)
- `MBB`: [2022-08-01, 2023-08-05)
- `MSN`: [2022-08-01, 2023-08-05)
- `MWG`: [2022-08-01, 2023-08-05)
- `NVL`: [2022-08-01, 2023-08-05)
- `PDR`: [2022-08-01, 2023-08-05)
- `PLX`: [2022-08-01, 2023-08-05)
- `POW`: [2022-08-01, 2023-08-05)
- `SAB`: [2022-08-01, 2023-08-05)
- `SSI`: [2022-08-01, 2023-08-05)
- `STB`: [2022-08-01, 2023-08-05)
- `TCB`: [2022-08-01, 2023-08-05)
- `TPB`: [2022-08-01, 2023-08-05)
- `VCB`: [2022-08-01, 2023-08-05)
- `VHM`: [2022-08-01, 2023-08-05)
- `VIB`: [2022-08-01, 2023-08-05)
- `VIC`: [2022-08-01, 2023-08-05)
- `VJC`: [2022-08-01, 2023-08-05)
- `VN30`: [2022-05-10, 2023-08-05)
- `VN30F2205`: [2022-05-10, 2022-05-20)
- `VN30F2206`: [2022-05-20, 2022-06-17)
- `VN30F2207`: [2022-06-17, 2022-07-22)
- `VN30F2208`: [2022-07-22, 2022-08-19)
- `VN30F2209`: [2022-08-19, 2022-09-16)
- `VN30F2210`: [2022-09-16, 2022-10-21)
- `VN30F2211`: [2022-10-21, 2022-11-18)
- `VN30F2212`: [2022-11-18, 2022-12-16)
- `VN30F2301`: [2022-12-16, 2023-01-20)
- `VN30F2302`: [2023-01-20, 2023-02-17)
- `VN30F2303`: [2023-02-17, 2023-03-17)
- `VN30F2304`: [2023-03-17, 2023-04-21)
- `VN30F2305`: [2023-04-21, 2023-05-19)
- `VN30F2306`: [2023-05-19, 2023-06-16)
- `VN30F2307`: [2023-06-16, 2023-07-21)
- `VN30F2308`: [2023-07-21, 2023-08-05)
- `VNM`: [2022-08-01, 2023-08-05)
- `VPB`: [2022-08-01, 2023-08-05)
- `VRE`: [2022-08-01, 2023-08-05)

### `quote_dailyvolume.parquet`
- Fields: `datetime, tickersymbol, quantity`
- Query: `quote.dailyvolume WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2022-08-01, 2023-08-05)
- `BCM`: [2022-08-01, 2023-08-05)
- `BID`: [2022-08-01, 2023-08-05)
- `BVH`: [2022-08-01, 2023-08-05)
- `CTG`: [2022-08-01, 2023-08-05)
- `FPT`: [2022-08-01, 2023-08-05)
- `GAS`: [2022-08-01, 2023-08-05)
- `GVR`: [2022-08-01, 2023-08-05)
- `HDB`: [2022-08-01, 2023-08-05)
- `HPG`: [2022-08-01, 2023-08-05)
- `KDH`: [2022-08-01, 2023-08-05)
- `MBB`: [2022-08-01, 2023-08-05)
- `MSN`: [2022-08-01, 2023-08-05)
- `MWG`: [2022-08-01, 2023-08-05)
- `NVL`: [2022-08-01, 2023-08-05)
- `PDR`: [2022-08-01, 2023-08-05)
- `PLX`: [2022-08-01, 2023-08-05)
- `POW`: [2022-08-01, 2023-08-05)
- `SAB`: [2022-08-01, 2023-08-05)
- `SSI`: [2022-08-01, 2023-08-05)
- `STB`: [2022-08-01, 2023-08-05)
- `TCB`: [2022-08-01, 2023-08-05)
- `TPB`: [2022-08-01, 2023-08-05)
- `VCB`: [2022-08-01, 2023-08-05)
- `VHM`: [2022-08-01, 2023-08-05)
- `VIB`: [2022-08-01, 2023-08-05)
- `VIC`: [2022-08-01, 2023-08-05)
- `VJC`: [2022-08-01, 2023-08-05)
- `VN30F2208`: [2022-08-01, 2022-08-19)
- `VN30F2209`: [2022-08-19, 2022-09-16)
- `VN30F2210`: [2022-09-16, 2022-10-21)
- `VN30F2211`: [2022-10-21, 2022-11-18)
- `VN30F2212`: [2022-11-18, 2022-12-16)
- `VN30F2301`: [2022-12-16, 2023-01-20)
- `VN30F2302`: [2023-01-20, 2023-02-17)
- `VN30F2303`: [2023-02-17, 2023-03-17)
- `VN30F2304`: [2023-03-17, 2023-04-21)
- `VN30F2305`: [2023-04-21, 2023-05-19)
- `VN30F2306`: [2023-05-19, 2023-06-16)
- `VN30F2307`: [2023-06-16, 2023-07-21)
- `VN30F2308`: [2023-07-21, 2023-08-05)
- `VNM`: [2022-08-01, 2023-08-05)
- `VPB`: [2022-08-01, 2023-08-05)
- `VRE`: [2022-08-01, 2023-08-05)

### `quote_floor.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.floor WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2022-08-01, 2023-08-05)
- `BCM`: [2022-08-01, 2023-08-05)
- `BID`: [2022-08-01, 2023-08-05)
- `BVH`: [2022-08-01, 2023-08-05)
- `CTG`: [2022-08-01, 2023-08-05)
- `FPT`: [2022-08-01, 2023-08-05)
- `GAS`: [2022-08-01, 2023-08-05)
- `GVR`: [2022-08-01, 2023-08-05)
- `HDB`: [2022-08-01, 2023-08-05)
- `HPG`: [2022-08-01, 2023-08-05)
- `KDH`: [2022-08-01, 2023-08-05)
- `MBB`: [2022-08-01, 2023-08-05)
- `MSN`: [2022-08-01, 2023-08-05)
- `MWG`: [2022-08-01, 2023-08-05)
- `NVL`: [2022-08-01, 2023-08-05)
- `PDR`: [2022-08-01, 2023-08-05)
- `PLX`: [2022-08-01, 2023-08-05)
- `POW`: [2022-08-01, 2023-08-05)
- `SAB`: [2022-08-01, 2023-08-05)
- `SSI`: [2022-08-01, 2023-08-05)
- `STB`: [2022-08-01, 2023-08-05)
- `TCB`: [2022-08-01, 2023-08-05)
- `TPB`: [2022-08-01, 2023-08-05)
- `VCB`: [2022-08-01, 2023-08-05)
- `VHM`: [2022-08-01, 2023-08-05)
- `VIB`: [2022-08-01, 2023-08-05)
- `VIC`: [2022-08-01, 2023-08-05)
- `VJC`: [2022-08-01, 2023-08-05)
- `VN30F2208`: [2022-08-01, 2022-08-19)
- `VN30F2209`: [2022-08-19, 2022-09-16)
- `VN30F2210`: [2022-09-16, 2022-10-21)
- `VN30F2211`: [2022-10-21, 2022-11-18)
- `VN30F2212`: [2022-11-18, 2022-12-16)
- `VN30F2301`: [2022-12-16, 2023-01-20)
- `VN30F2302`: [2023-01-20, 2023-02-17)
- `VN30F2303`: [2023-02-17, 2023-03-17)
- `VN30F2304`: [2023-03-17, 2023-04-21)
- `VN30F2305`: [2023-04-21, 2023-05-19)
- `VN30F2306`: [2023-05-19, 2023-06-16)
- `VN30F2307`: [2023-06-16, 2023-07-21)
- `VN30F2308`: [2023-07-21, 2023-08-05)
- `VNM`: [2022-08-01, 2023-08-05)
- `VPB`: [2022-08-01, 2023-08-05)
- `VRE`: [2022-08-01, 2023-08-05)

### `quote_max.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.max WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2022-08-01, 2023-08-05)
- `BCM`: [2022-08-01, 2023-08-05)
- `BID`: [2022-08-01, 2023-08-05)
- `BVH`: [2022-08-01, 2023-08-05)
- `CTG`: [2022-08-01, 2023-08-05)
- `FPT`: [2022-08-01, 2023-08-05)
- `GAS`: [2022-08-01, 2023-08-05)
- `GVR`: [2022-08-01, 2023-08-05)
- `HDB`: [2022-08-01, 2023-08-05)
- `HPG`: [2022-08-01, 2023-08-05)
- `KDH`: [2022-08-01, 2023-08-05)
- `MBB`: [2022-08-01, 2023-08-05)
- `MSN`: [2022-08-01, 2023-08-05)
- `MWG`: [2022-08-01, 2023-08-05)
- `NVL`: [2022-08-01, 2023-08-05)
- `PDR`: [2022-08-01, 2023-08-05)
- `PLX`: [2022-08-01, 2023-08-05)
- `POW`: [2022-08-01, 2023-08-05)
- `SAB`: [2022-08-01, 2023-08-05)
- `SSI`: [2022-08-01, 2023-08-05)
- `STB`: [2022-08-01, 2023-08-05)
- `TCB`: [2022-08-01, 2023-08-05)
- `TPB`: [2022-08-01, 2023-08-05)
- `VCB`: [2022-08-01, 2023-08-05)
- `VHM`: [2022-08-01, 2023-08-05)
- `VIB`: [2022-08-01, 2023-08-05)
- `VIC`: [2022-08-01, 2023-08-05)
- `VJC`: [2022-08-01, 2023-08-05)
- `VN30F2208`: [2022-08-01, 2022-08-19)
- `VN30F2209`: [2022-08-19, 2022-09-16)
- `VN30F2210`: [2022-09-16, 2022-10-21)
- `VN30F2211`: [2022-10-21, 2022-11-18)
- `VN30F2212`: [2022-11-18, 2022-12-16)
- `VN30F2301`: [2022-12-16, 2023-01-20)
- `VN30F2302`: [2023-01-20, 2023-02-17)
- `VN30F2303`: [2023-02-17, 2023-03-17)
- `VN30F2304`: [2023-03-17, 2023-04-21)
- `VN30F2305`: [2023-04-21, 2023-05-19)
- `VN30F2306`: [2023-05-19, 2023-06-16)
- `VN30F2307`: [2023-06-16, 2023-07-21)
- `VN30F2308`: [2023-07-21, 2023-08-05)
- `VNM`: [2022-08-01, 2023-08-05)
- `VPB`: [2022-08-01, 2023-08-05)
- `VRE`: [2022-08-01, 2023-08-05)

### `quote_min.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.min WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2022-08-01, 2023-08-05)
- `BCM`: [2022-08-01, 2023-08-05)
- `BID`: [2022-08-01, 2023-08-05)
- `BVH`: [2022-08-01, 2023-08-05)
- `CTG`: [2022-08-01, 2023-08-05)
- `FPT`: [2022-08-01, 2023-08-05)
- `GAS`: [2022-08-01, 2023-08-05)
- `GVR`: [2022-08-01, 2023-08-05)
- `HDB`: [2022-08-01, 2023-08-05)
- `HPG`: [2022-08-01, 2023-08-05)
- `KDH`: [2022-08-01, 2023-08-05)
- `MBB`: [2022-08-01, 2023-08-05)
- `MSN`: [2022-08-01, 2023-08-05)
- `MWG`: [2022-08-01, 2023-08-05)
- `NVL`: [2022-08-01, 2023-08-05)
- `PDR`: [2022-08-01, 2023-08-05)
- `PLX`: [2022-08-01, 2023-08-05)
- `POW`: [2022-08-01, 2023-08-05)
- `SAB`: [2022-08-01, 2023-08-05)
- `SSI`: [2022-08-01, 2023-08-05)
- `STB`: [2022-08-01, 2023-08-05)
- `TCB`: [2022-08-01, 2023-08-05)
- `TPB`: [2022-08-01, 2023-08-05)
- `VCB`: [2022-08-01, 2023-08-05)
- `VHM`: [2022-08-01, 2023-08-05)
- `VIB`: [2022-08-01, 2023-08-05)
- `VIC`: [2022-08-01, 2023-08-05)
- `VJC`: [2022-08-01, 2023-08-05)
- `VN30F2208`: [2022-08-01, 2022-08-19)
- `VN30F2209`: [2022-08-19, 2022-09-16)
- `VN30F2210`: [2022-09-16, 2022-10-21)
- `VN30F2211`: [2022-10-21, 2022-11-18)
- `VN30F2212`: [2022-11-18, 2022-12-16)
- `VN30F2301`: [2022-12-16, 2023-01-20)
- `VN30F2302`: [2023-01-20, 2023-02-17)
- `VN30F2303`: [2023-02-17, 2023-03-17)
- `VN30F2304`: [2023-03-17, 2023-04-21)
- `VN30F2305`: [2023-04-21, 2023-05-19)
- `VN30F2306`: [2023-05-19, 2023-06-16)
- `VN30F2307`: [2023-06-16, 2023-07-21)
- `VN30F2308`: [2023-07-21, 2023-08-05)
- `VNM`: [2022-08-01, 2023-08-05)
- `VPB`: [2022-08-01, 2023-08-05)
- `VRE`: [2022-08-01, 2023-08-05)

### `quote_open.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.open WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2022-08-01, 2023-08-05)
- `BCM`: [2022-08-01, 2023-08-05)
- `BID`: [2022-08-01, 2023-08-05)
- `BVH`: [2022-08-01, 2023-08-05)
- `CTG`: [2022-08-01, 2023-08-05)
- `FPT`: [2022-08-01, 2023-08-05)
- `GAS`: [2022-08-01, 2023-08-05)
- `GVR`: [2022-08-01, 2023-08-05)
- `HDB`: [2022-08-01, 2023-08-05)
- `HPG`: [2022-08-01, 2023-08-05)
- `KDH`: [2022-08-01, 2023-08-05)
- `MBB`: [2022-08-01, 2023-08-05)
- `MSN`: [2022-08-01, 2023-08-05)
- `MWG`: [2022-08-01, 2023-08-05)
- `NVL`: [2022-08-01, 2023-08-05)
- `PDR`: [2022-08-01, 2023-08-05)
- `PLX`: [2022-08-01, 2023-08-05)
- `POW`: [2022-08-01, 2023-08-05)
- `SAB`: [2022-08-01, 2023-08-05)
- `SSI`: [2022-08-01, 2023-08-05)
- `STB`: [2022-08-01, 2023-08-05)
- `TCB`: [2022-08-01, 2023-08-05)
- `TPB`: [2022-08-01, 2023-08-05)
- `VCB`: [2022-08-01, 2023-08-05)
- `VHM`: [2022-08-01, 2023-08-05)
- `VIB`: [2022-08-01, 2023-08-05)
- `VIC`: [2022-08-01, 2023-08-05)
- `VJC`: [2022-08-01, 2023-08-05)
- `VN30F2208`: [2022-08-01, 2022-08-19)
- `VN30F2209`: [2022-08-19, 2022-09-16)
- `VN30F2210`: [2022-09-16, 2022-10-21)
- `VN30F2211`: [2022-10-21, 2022-11-18)
- `VN30F2212`: [2022-11-18, 2022-12-16)
- `VN30F2301`: [2022-12-16, 2023-01-20)
- `VN30F2302`: [2023-01-20, 2023-02-17)
- `VN30F2303`: [2023-02-17, 2023-03-17)
- `VN30F2304`: [2023-03-17, 2023-04-21)
- `VN30F2305`: [2023-04-21, 2023-05-19)
- `VN30F2306`: [2023-05-19, 2023-06-16)
- `VN30F2307`: [2023-06-16, 2023-07-21)
- `VN30F2308`: [2023-07-21, 2023-08-05)
- `VNM`: [2022-08-01, 2023-08-05)
- `VPB`: [2022-08-01, 2023-08-05)
- `VRE`: [2022-08-01, 2023-08-05)

### `quote_reference.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.reference WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2022-08-01, 2023-08-05)
- `BCM`: [2022-08-01, 2023-08-05)
- `BID`: [2022-08-01, 2023-08-05)
- `BVH`: [2022-08-01, 2023-08-05)
- `CTG`: [2022-08-01, 2023-08-05)
- `FPT`: [2022-08-01, 2023-08-05)
- `GAS`: [2022-08-01, 2023-08-05)
- `GVR`: [2022-08-01, 2023-08-05)
- `HDB`: [2022-08-01, 2023-08-05)
- `HPG`: [2022-08-01, 2023-08-05)
- `KDH`: [2022-08-01, 2023-08-05)
- `MBB`: [2022-08-01, 2023-08-05)
- `MSN`: [2022-08-01, 2023-08-05)
- `MWG`: [2022-08-01, 2023-08-05)
- `NVL`: [2022-08-01, 2023-08-05)
- `PDR`: [2022-08-01, 2023-08-05)
- `PLX`: [2022-08-01, 2023-08-05)
- `POW`: [2022-08-01, 2023-08-05)
- `SAB`: [2022-08-01, 2023-08-05)
- `SSI`: [2022-08-01, 2023-08-05)
- `STB`: [2022-08-01, 2023-08-05)
- `TCB`: [2022-08-01, 2023-08-05)
- `TPB`: [2022-08-01, 2023-08-05)
- `VCB`: [2022-08-01, 2023-08-05)
- `VHM`: [2022-08-01, 2023-08-05)
- `VIB`: [2022-08-01, 2023-08-05)
- `VIC`: [2022-08-01, 2023-08-05)
- `VJC`: [2022-08-01, 2023-08-05)
- `VN30F2208`: [2022-08-01, 2022-08-19)
- `VN30F2209`: [2022-08-19, 2022-09-16)
- `VN30F2210`: [2022-09-16, 2022-10-21)
- `VN30F2211`: [2022-10-21, 2022-11-18)
- `VN30F2212`: [2022-11-18, 2022-12-16)
- `VN30F2301`: [2022-12-16, 2023-01-20)
- `VN30F2302`: [2023-01-20, 2023-02-17)
- `VN30F2303`: [2023-02-17, 2023-03-17)
- `VN30F2304`: [2023-03-17, 2023-04-21)
- `VN30F2305`: [2023-04-21, 2023-05-19)
- `VN30F2306`: [2023-05-19, 2023-06-16)
- `VN30F2307`: [2023-06-16, 2023-07-21)
- `VN30F2308`: [2023-07-21, 2023-08-05)
- `VNM`: [2022-08-01, 2023-08-05)
- `VPB`: [2022-08-01, 2023-08-05)
- `VRE`: [2022-08-01, 2023-08-05)

### `quote_ticker.parquet`
- Fields: `tickersymbol, exchangeid, lastupdated, instrumenttype, startdate, expdate`
- Query: `quote.ticker WHERE tickersymbol = ANY(<tickers>)`
- `ACB`: ticker-master row
- `BCM`: ticker-master row
- `BID`: ticker-master row
- `BVH`: ticker-master row
- `CTG`: ticker-master row
- `FPT`: ticker-master row
- `GAS`: ticker-master row
- `GVR`: ticker-master row
- `HDB`: ticker-master row
- `HPG`: ticker-master row
- `KDH`: ticker-master row
- `MBB`: ticker-master row
- `MSN`: ticker-master row
- `MWG`: ticker-master row
- `NVL`: ticker-master row
- `PDR`: ticker-master row
- `PLX`: ticker-master row
- `POW`: ticker-master row
- `SAB`: ticker-master row
- `SSI`: ticker-master row
- `STB`: ticker-master row
- `TCB`: ticker-master row
- `TPB`: ticker-master row
- `VCB`: ticker-master row
- `VHM`: ticker-master row
- `VIB`: ticker-master row
- `VIC`: ticker-master row
- `VJC`: ticker-master row
- `VN30`: ticker-master row
- `VN30F2205`: ticker-master row
- `VN30F2206`: ticker-master row
- `VN30F2207`: ticker-master row
- `VN30F2208`: ticker-master row
- `VN30F2209`: ticker-master row
- `VN30F2210`: ticker-master row
- `VN30F2211`: ticker-master row
- `VN30F2212`: ticker-master row
- `VN30F2301`: ticker-master row
- `VN30F2302`: ticker-master row
- `VN30F2303`: ticker-master row
- `VN30F2304`: ticker-master row
- `VN30F2305`: ticker-master row
- `VN30F2306`: ticker-master row
- `VN30F2307`: ticker-master row
- `VN30F2308`: ticker-master row
- `VNM`: ticker-master row
- `VPB`: ticker-master row
- `VRE`: ticker-master row
