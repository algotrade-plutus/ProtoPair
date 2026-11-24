# DATA-MANIFEST: pair-daily-w2

- **Reproduces:** ProtoPair (T7) naive vs faithful anchor, window w2: result/pair_anchor/w2*.json
- **Extraction mode:** `declared`
- **Command:** `rivf26_extract.py declared --source db --force --experiment pair-daily-w2 --reproduces ProtoPair (T7) naive vs faithful anchor, window w2: result/pair_anchor/w2*.json --request data/market/w2/request.json`
- **Source:** Algotrade PostgreSQL DB, schema `quote` (read-only transaction). File `<prefix>_<x>.<ext>` holds rows of DB table `quote.<x>`.
- **Extracted on:** 2026-11-24 with `scripts/rivf26_extract.py` (pyarrow 26.0.1; writer settings fixed in `WRITER`).
- **Total size:** 98,887 bytes (96.6 KiB) in 9 files.

## Why this window is minimal

**Window w2 = 2023-08-07 -> 2024-02-02 (127 sessions), robustness.** One whole VN30 review period: the
2023-08-07 snapshot is the last the DB holds before 2025-02-03 (no 2024-02 or 2024-08 snapshot), so the window
stops on 2024-02-02, the last session before the real 2024-02 review would apply. It is post-step throughout
(IM 0.17) and contains 6 front-month rolls (VN30F2308 ... VN30F2401 expire inside it) and 13 signalled pair
positions (7 executable, 6 mirror). It does not overlap w1 and does not reach the 2025-05-05 KRX cutover.

**Tickers / fields:** as w1 (30 names of the 2023-08-07 snapshot, the dated front-month contracts, `VN30`;
8 daily fields in-window, close-only warm-up over the 59 sessions before 2023-08-07). Total about 0.1 MB.

## Files

| File | Rows | Bytes | sha256 |
|---|---:|---:|---|
| `quote_ceil.parquet` | 3,907 | 10,641 | `8c6873c1f5a649e62700c2239d0621bb35e76717095c46ff5798ce2db457b589` |
| `quote_close.parquet` | 4,182 | 11,330 | `203d71391af6d60fc38aecfc79cc465aa65c479bd3b7f4a9f56bc31f22f4bee2` |
| `quote_dailyvolume.parquet` | 3,937 | 21,025 | `40748aa05c4d76033efeecf9e5767ef0434cd807b732cf17171633466d7db1b7` |
| `quote_floor.parquet` | 3,907 | 10,584 | `dd72d5929b9a735f494afc10e8c2cac6106e4c9f8a4b2175ec3dd136e995548f` |
| `quote_max.parquet` | 3,937 | 10,797 | `ae6ae026cf40ad4f17c8e8bdd57ea3349bb72d9f9400c7f6709df14156dd4a07` |
| `quote_min.parquet` | 3,937 | 10,757 | `897dcbeb7e0d23292c45f2947cab122441a32e041f84b3f61541bfd6104a1150` |
| `quote_open.parquet` | 3,937 | 10,817 | `28d8208ed15d465042c4891849ed4bfd6ae2865ba880f1a978e7f0b4d327826c` |
| `quote_reference.parquet` | 3,937 | 10,752 | `916bcbba2561e52d836e799fdc127c7e54676ecd4e043cfe6bd32697209b2d2c` |
| `quote_ticker.parquet` | 41 | 2,184 | `227bce2b4227e56e659606c8fe232ec6f0e063541e843f2ca711b6d6aeef972e` |

## Files added by ProtoPair `pp-extract meta` (not the shared tool)

| File | Rows | Bytes | sha256 | Query |
|---|---:|---:|---|---|
| `quote_vn30.parquet` | 30 | 707 | `394849fa1f0a635fff98437d6b275bbc98213c71acc6eff946112ba28d50858a` | `quote.vn30` rows of the review snapshots in force over the window |
| `quote_futurecontractcode.parquet` | 189 | 1,257 | `b5905581331ffe84f6e6ae1f70bf7178d100ebff2c1d9c209fe810b8d8bb2796` | `quote.futurecontractcode WHERE futurecode = 'VN30F1M'` over [warm-up start, window end] |

## Contents (tickers, ranges, fields, query)

### `quote_ceil.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.ceil WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2023-08-07, 2024-02-03)
- `BCM`: [2023-08-07, 2024-02-03)
- `BID`: [2023-08-07, 2024-02-03)
- `BVH`: [2023-08-07, 2024-02-03)
- `CTG`: [2023-08-07, 2024-02-03)
- `FPT`: [2023-08-07, 2024-02-03)
- `GAS`: [2023-08-07, 2024-02-03)
- `GVR`: [2023-08-07, 2024-02-03)
- `HDB`: [2023-08-07, 2024-02-03)
- `HPG`: [2023-08-07, 2024-02-03)
- `MBB`: [2023-08-07, 2024-02-03)
- `MSN`: [2023-08-07, 2024-02-03)
- `MWG`: [2023-08-07, 2024-02-03)
- `PLX`: [2023-08-07, 2024-02-03)
- `POW`: [2023-08-07, 2024-02-03)
- `SAB`: [2023-08-07, 2024-02-03)
- `SHB`: [2023-08-07, 2024-02-03)
- `SSB`: [2023-08-07, 2024-02-03)
- `SSI`: [2023-08-07, 2024-02-03)
- `STB`: [2023-08-07, 2024-02-03)
- `TCB`: [2023-08-07, 2024-02-03)
- `TPB`: [2023-08-07, 2024-02-03)
- `VCB`: [2023-08-07, 2024-02-03)
- `VHM`: [2023-08-07, 2024-02-03)
- `VIB`: [2023-08-07, 2024-02-03)
- `VIC`: [2023-08-07, 2024-02-03)
- `VJC`: [2023-08-07, 2024-02-03)
- `VN30F2308`: [2023-08-07, 2023-08-18)
- `VN30F2309`: [2023-08-18, 2023-09-22)
- `VN30F2310`: [2023-09-22, 2023-10-20)
- `VN30F2311`: [2023-10-20, 2023-11-17)
- `VN30F2312`: [2023-11-17, 2023-12-22)
- `VN30F2401`: [2023-12-22, 2024-01-19)
- `VN30F2402`: [2024-01-19, 2024-02-03)
- `VNM`: [2023-08-07, 2024-02-03)
- `VPB`: [2023-08-07, 2024-02-03)
- `VRE`: [2023-08-07, 2024-02-03)

### `quote_close.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.close WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2023-08-07, 2024-02-03)
- `BCM`: [2023-08-07, 2024-02-03)
- `BID`: [2023-08-07, 2024-02-03)
- `BVH`: [2023-08-07, 2024-02-03)
- `CTG`: [2023-08-07, 2024-02-03)
- `FPT`: [2023-08-07, 2024-02-03)
- `GAS`: [2023-08-07, 2024-02-03)
- `GVR`: [2023-08-07, 2024-02-03)
- `HDB`: [2023-08-07, 2024-02-03)
- `HPG`: [2023-08-07, 2024-02-03)
- `MBB`: [2023-08-07, 2024-02-03)
- `MSN`: [2023-08-07, 2024-02-03)
- `MWG`: [2023-08-07, 2024-02-03)
- `PLX`: [2023-08-07, 2024-02-03)
- `POW`: [2023-08-07, 2024-02-03)
- `SAB`: [2023-08-07, 2024-02-03)
- `SHB`: [2023-08-07, 2024-02-03)
- `SSB`: [2023-08-07, 2024-02-03)
- `SSI`: [2023-08-07, 2024-02-03)
- `STB`: [2023-08-07, 2024-02-03)
- `TCB`: [2023-08-07, 2024-02-03)
- `TPB`: [2023-08-07, 2024-02-03)
- `VCB`: [2023-08-07, 2024-02-03)
- `VHM`: [2023-08-07, 2024-02-03)
- `VIB`: [2023-08-07, 2024-02-03)
- `VIC`: [2023-08-07, 2024-02-03)
- `VJC`: [2023-08-07, 2024-02-03)
- `VN30`: [2023-05-16, 2024-02-03)
- `VN30F2305`: [2023-05-16, 2023-05-19)
- `VN30F2306`: [2023-05-19, 2023-06-16)
- `VN30F2307`: [2023-06-16, 2023-07-21)
- `VN30F2308`: [2023-07-21, 2023-08-18)
- `VN30F2309`: [2023-08-18, 2023-09-22)
- `VN30F2310`: [2023-09-22, 2023-10-20)
- `VN30F2311`: [2023-10-20, 2023-11-17)
- `VN30F2312`: [2023-11-17, 2023-12-22)
- `VN30F2401`: [2023-12-22, 2024-01-19)
- `VN30F2402`: [2024-01-19, 2024-02-03)
- `VNM`: [2023-08-07, 2024-02-03)
- `VPB`: [2023-08-07, 2024-02-03)
- `VRE`: [2023-08-07, 2024-02-03)

### `quote_dailyvolume.parquet`
- Fields: `datetime, tickersymbol, quantity`
- Query: `quote.dailyvolume WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2023-08-07, 2024-02-03)
- `BCM`: [2023-08-07, 2024-02-03)
- `BID`: [2023-08-07, 2024-02-03)
- `BVH`: [2023-08-07, 2024-02-03)
- `CTG`: [2023-08-07, 2024-02-03)
- `FPT`: [2023-08-07, 2024-02-03)
- `GAS`: [2023-08-07, 2024-02-03)
- `GVR`: [2023-08-07, 2024-02-03)
- `HDB`: [2023-08-07, 2024-02-03)
- `HPG`: [2023-08-07, 2024-02-03)
- `MBB`: [2023-08-07, 2024-02-03)
- `MSN`: [2023-08-07, 2024-02-03)
- `MWG`: [2023-08-07, 2024-02-03)
- `PLX`: [2023-08-07, 2024-02-03)
- `POW`: [2023-08-07, 2024-02-03)
- `SAB`: [2023-08-07, 2024-02-03)
- `SHB`: [2023-08-07, 2024-02-03)
- `SSB`: [2023-08-07, 2024-02-03)
- `SSI`: [2023-08-07, 2024-02-03)
- `STB`: [2023-08-07, 2024-02-03)
- `TCB`: [2023-08-07, 2024-02-03)
- `TPB`: [2023-08-07, 2024-02-03)
- `VCB`: [2023-08-07, 2024-02-03)
- `VHM`: [2023-08-07, 2024-02-03)
- `VIB`: [2023-08-07, 2024-02-03)
- `VIC`: [2023-08-07, 2024-02-03)
- `VJC`: [2023-08-07, 2024-02-03)
- `VN30F2308`: [2023-08-07, 2023-08-18)
- `VN30F2309`: [2023-08-18, 2023-09-22)
- `VN30F2310`: [2023-09-22, 2023-10-20)
- `VN30F2311`: [2023-10-20, 2023-11-17)
- `VN30F2312`: [2023-11-17, 2023-12-22)
- `VN30F2401`: [2023-12-22, 2024-01-19)
- `VN30F2402`: [2024-01-19, 2024-02-03)
- `VNM`: [2023-08-07, 2024-02-03)
- `VPB`: [2023-08-07, 2024-02-03)
- `VRE`: [2023-08-07, 2024-02-03)

### `quote_floor.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.floor WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2023-08-07, 2024-02-03)
- `BCM`: [2023-08-07, 2024-02-03)
- `BID`: [2023-08-07, 2024-02-03)
- `BVH`: [2023-08-07, 2024-02-03)
- `CTG`: [2023-08-07, 2024-02-03)
- `FPT`: [2023-08-07, 2024-02-03)
- `GAS`: [2023-08-07, 2024-02-03)
- `GVR`: [2023-08-07, 2024-02-03)
- `HDB`: [2023-08-07, 2024-02-03)
- `HPG`: [2023-08-07, 2024-02-03)
- `MBB`: [2023-08-07, 2024-02-03)
- `MSN`: [2023-08-07, 2024-02-03)
- `MWG`: [2023-08-07, 2024-02-03)
- `PLX`: [2023-08-07, 2024-02-03)
- `POW`: [2023-08-07, 2024-02-03)
- `SAB`: [2023-08-07, 2024-02-03)
- `SHB`: [2023-08-07, 2024-02-03)
- `SSB`: [2023-08-07, 2024-02-03)
- `SSI`: [2023-08-07, 2024-02-03)
- `STB`: [2023-08-07, 2024-02-03)
- `TCB`: [2023-08-07, 2024-02-03)
- `TPB`: [2023-08-07, 2024-02-03)
- `VCB`: [2023-08-07, 2024-02-03)
- `VHM`: [2023-08-07, 2024-02-03)
- `VIB`: [2023-08-07, 2024-02-03)
- `VIC`: [2023-08-07, 2024-02-03)
- `VJC`: [2023-08-07, 2024-02-03)
- `VN30F2308`: [2023-08-07, 2023-08-18)
- `VN30F2309`: [2023-08-18, 2023-09-22)
- `VN30F2310`: [2023-09-22, 2023-10-20)
- `VN30F2311`: [2023-10-20, 2023-11-17)
- `VN30F2312`: [2023-11-17, 2023-12-22)
- `VN30F2401`: [2023-12-22, 2024-01-19)
- `VN30F2402`: [2024-01-19, 2024-02-03)
- `VNM`: [2023-08-07, 2024-02-03)
- `VPB`: [2023-08-07, 2024-02-03)
- `VRE`: [2023-08-07, 2024-02-03)

### `quote_max.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.max WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2023-08-07, 2024-02-03)
- `BCM`: [2023-08-07, 2024-02-03)
- `BID`: [2023-08-07, 2024-02-03)
- `BVH`: [2023-08-07, 2024-02-03)
- `CTG`: [2023-08-07, 2024-02-03)
- `FPT`: [2023-08-07, 2024-02-03)
- `GAS`: [2023-08-07, 2024-02-03)
- `GVR`: [2023-08-07, 2024-02-03)
- `HDB`: [2023-08-07, 2024-02-03)
- `HPG`: [2023-08-07, 2024-02-03)
- `MBB`: [2023-08-07, 2024-02-03)
- `MSN`: [2023-08-07, 2024-02-03)
- `MWG`: [2023-08-07, 2024-02-03)
- `PLX`: [2023-08-07, 2024-02-03)
- `POW`: [2023-08-07, 2024-02-03)
- `SAB`: [2023-08-07, 2024-02-03)
- `SHB`: [2023-08-07, 2024-02-03)
- `SSB`: [2023-08-07, 2024-02-03)
- `SSI`: [2023-08-07, 2024-02-03)
- `STB`: [2023-08-07, 2024-02-03)
- `TCB`: [2023-08-07, 2024-02-03)
- `TPB`: [2023-08-07, 2024-02-03)
- `VCB`: [2023-08-07, 2024-02-03)
- `VHM`: [2023-08-07, 2024-02-03)
- `VIB`: [2023-08-07, 2024-02-03)
- `VIC`: [2023-08-07, 2024-02-03)
- `VJC`: [2023-08-07, 2024-02-03)
- `VN30F2308`: [2023-08-07, 2023-08-18)
- `VN30F2309`: [2023-08-18, 2023-09-22)
- `VN30F2310`: [2023-09-22, 2023-10-20)
- `VN30F2311`: [2023-10-20, 2023-11-17)
- `VN30F2312`: [2023-11-17, 2023-12-22)
- `VN30F2401`: [2023-12-22, 2024-01-19)
- `VN30F2402`: [2024-01-19, 2024-02-03)
- `VNM`: [2023-08-07, 2024-02-03)
- `VPB`: [2023-08-07, 2024-02-03)
- `VRE`: [2023-08-07, 2024-02-03)

### `quote_min.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.min WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2023-08-07, 2024-02-03)
- `BCM`: [2023-08-07, 2024-02-03)
- `BID`: [2023-08-07, 2024-02-03)
- `BVH`: [2023-08-07, 2024-02-03)
- `CTG`: [2023-08-07, 2024-02-03)
- `FPT`: [2023-08-07, 2024-02-03)
- `GAS`: [2023-08-07, 2024-02-03)
- `GVR`: [2023-08-07, 2024-02-03)
- `HDB`: [2023-08-07, 2024-02-03)
- `HPG`: [2023-08-07, 2024-02-03)
- `MBB`: [2023-08-07, 2024-02-03)
- `MSN`: [2023-08-07, 2024-02-03)
- `MWG`: [2023-08-07, 2024-02-03)
- `PLX`: [2023-08-07, 2024-02-03)
- `POW`: [2023-08-07, 2024-02-03)
- `SAB`: [2023-08-07, 2024-02-03)
- `SHB`: [2023-08-07, 2024-02-03)
- `SSB`: [2023-08-07, 2024-02-03)
- `SSI`: [2023-08-07, 2024-02-03)
- `STB`: [2023-08-07, 2024-02-03)
- `TCB`: [2023-08-07, 2024-02-03)
- `TPB`: [2023-08-07, 2024-02-03)
- `VCB`: [2023-08-07, 2024-02-03)
- `VHM`: [2023-08-07, 2024-02-03)
- `VIB`: [2023-08-07, 2024-02-03)
- `VIC`: [2023-08-07, 2024-02-03)
- `VJC`: [2023-08-07, 2024-02-03)
- `VN30F2308`: [2023-08-07, 2023-08-18)
- `VN30F2309`: [2023-08-18, 2023-09-22)
- `VN30F2310`: [2023-09-22, 2023-10-20)
- `VN30F2311`: [2023-10-20, 2023-11-17)
- `VN30F2312`: [2023-11-17, 2023-12-22)
- `VN30F2401`: [2023-12-22, 2024-01-19)
- `VN30F2402`: [2024-01-19, 2024-02-03)
- `VNM`: [2023-08-07, 2024-02-03)
- `VPB`: [2023-08-07, 2024-02-03)
- `VRE`: [2023-08-07, 2024-02-03)

### `quote_open.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.open WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2023-08-07, 2024-02-03)
- `BCM`: [2023-08-07, 2024-02-03)
- `BID`: [2023-08-07, 2024-02-03)
- `BVH`: [2023-08-07, 2024-02-03)
- `CTG`: [2023-08-07, 2024-02-03)
- `FPT`: [2023-08-07, 2024-02-03)
- `GAS`: [2023-08-07, 2024-02-03)
- `GVR`: [2023-08-07, 2024-02-03)
- `HDB`: [2023-08-07, 2024-02-03)
- `HPG`: [2023-08-07, 2024-02-03)
- `MBB`: [2023-08-07, 2024-02-03)
- `MSN`: [2023-08-07, 2024-02-03)
- `MWG`: [2023-08-07, 2024-02-03)
- `PLX`: [2023-08-07, 2024-02-03)
- `POW`: [2023-08-07, 2024-02-03)
- `SAB`: [2023-08-07, 2024-02-03)
- `SHB`: [2023-08-07, 2024-02-03)
- `SSB`: [2023-08-07, 2024-02-03)
- `SSI`: [2023-08-07, 2024-02-03)
- `STB`: [2023-08-07, 2024-02-03)
- `TCB`: [2023-08-07, 2024-02-03)
- `TPB`: [2023-08-07, 2024-02-03)
- `VCB`: [2023-08-07, 2024-02-03)
- `VHM`: [2023-08-07, 2024-02-03)
- `VIB`: [2023-08-07, 2024-02-03)
- `VIC`: [2023-08-07, 2024-02-03)
- `VJC`: [2023-08-07, 2024-02-03)
- `VN30F2308`: [2023-08-07, 2023-08-18)
- `VN30F2309`: [2023-08-18, 2023-09-22)
- `VN30F2310`: [2023-09-22, 2023-10-20)
- `VN30F2311`: [2023-10-20, 2023-11-17)
- `VN30F2312`: [2023-11-17, 2023-12-22)
- `VN30F2401`: [2023-12-22, 2024-01-19)
- `VN30F2402`: [2024-01-19, 2024-02-03)
- `VNM`: [2023-08-07, 2024-02-03)
- `VPB`: [2023-08-07, 2024-02-03)
- `VRE`: [2023-08-07, 2024-02-03)

### `quote_reference.parquet`
- Fields: `datetime, tickersymbol, price`
- Query: `quote.reference WHERE tickersymbol = <t> AND datetime >= <lo> AND datetime < <hi>`, once per (ticker, interval) below
- `ACB`: [2023-08-07, 2024-02-03)
- `BCM`: [2023-08-07, 2024-02-03)
- `BID`: [2023-08-07, 2024-02-03)
- `BVH`: [2023-08-07, 2024-02-03)
- `CTG`: [2023-08-07, 2024-02-03)
- `FPT`: [2023-08-07, 2024-02-03)
- `GAS`: [2023-08-07, 2024-02-03)
- `GVR`: [2023-08-07, 2024-02-03)
- `HDB`: [2023-08-07, 2024-02-03)
- `HPG`: [2023-08-07, 2024-02-03)
- `MBB`: [2023-08-07, 2024-02-03)
- `MSN`: [2023-08-07, 2024-02-03)
- `MWG`: [2023-08-07, 2024-02-03)
- `PLX`: [2023-08-07, 2024-02-03)
- `POW`: [2023-08-07, 2024-02-03)
- `SAB`: [2023-08-07, 2024-02-03)
- `SHB`: [2023-08-07, 2024-02-03)
- `SSB`: [2023-08-07, 2024-02-03)
- `SSI`: [2023-08-07, 2024-02-03)
- `STB`: [2023-08-07, 2024-02-03)
- `TCB`: [2023-08-07, 2024-02-03)
- `TPB`: [2023-08-07, 2024-02-03)
- `VCB`: [2023-08-07, 2024-02-03)
- `VHM`: [2023-08-07, 2024-02-03)
- `VIB`: [2023-08-07, 2024-02-03)
- `VIC`: [2023-08-07, 2024-02-03)
- `VJC`: [2023-08-07, 2024-02-03)
- `VN30F2308`: [2023-08-07, 2023-08-18)
- `VN30F2309`: [2023-08-18, 2023-09-22)
- `VN30F2310`: [2023-09-22, 2023-10-20)
- `VN30F2311`: [2023-10-20, 2023-11-17)
- `VN30F2312`: [2023-11-17, 2023-12-22)
- `VN30F2401`: [2023-12-22, 2024-01-19)
- `VN30F2402`: [2024-01-19, 2024-02-03)
- `VNM`: [2023-08-07, 2024-02-03)
- `VPB`: [2023-08-07, 2024-02-03)
- `VRE`: [2023-08-07, 2024-02-03)

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
- `MBB`: ticker-master row
- `MSN`: ticker-master row
- `MWG`: ticker-master row
- `PLX`: ticker-master row
- `POW`: ticker-master row
- `SAB`: ticker-master row
- `SHB`: ticker-master row
- `SSB`: ticker-master row
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
- `VN30F2305`: ticker-master row
- `VN30F2306`: ticker-master row
- `VN30F2307`: ticker-master row
- `VN30F2308`: ticker-master row
- `VN30F2309`: ticker-master row
- `VN30F2310`: ticker-master row
- `VN30F2311`: ticker-master row
- `VN30F2312`: ticker-master row
- `VN30F2401`: ticker-master row
- `VN30F2402`: ticker-master row
- `VNM`: ticker-master row
- `VPB`: ticker-master row
- `VRE`: ticker-master row
