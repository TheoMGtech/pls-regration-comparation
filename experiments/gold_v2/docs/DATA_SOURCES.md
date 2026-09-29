# Data sources and availability

The gold target is the existing V1 frozen file, not a new download. Raw copies
and hashes for the external data are recorded in `config/sources.json`.

| Feature block | Series | Official source | Frequency | V2 coverage after conservative availability lag | Track | Availability / leakage control |
|---|---|---|---|---|---|---|
| Gold target | V1_GOLD_PRICE | frozen V1 dataset | market observation | 1968-04-29 to 2014-04-09 | A/B/C | referenced only; no replacement |
| USD | DTWEXB | Federal Reserve Board / FRED | daily | 1995-01-10 to 2014-04-09 | A | event date + one calendar day; backward as-of |
| Risk | VIXCLS | Cboe / FRED | daily close | 1990-01-09 to 2014-04-09 | A | one-day minimum lag; same-day close excluded |
| Equities proxy | NASDAQCOM | Nasdaq / FRED | daily | 1971-02-08 to 2014-04-09 | A | NASDAQ is used instead of SP500 for reproducible long coverage |
| Rates | DGS2 | U.S. Treasury / FRED | daily | 1976-06-08 to 2014-04-09 | A | event date + one calendar day |
| Commodities | DCOILWTICO | EIA / FRED | daily | 1986-01-09 to 2014-04-09 | A | event date + one calendar day |
| Real rates | DFII10 | U.S. Treasury / FRED | daily | 2003-01-09 to 2014-04-09 | B | separate shorter experiment; never a whole-V1 comparison |

EPU and GPR were deliberately deferred from Stage A: they are retrospective,
vintage-sensitive exploratory sources. Silver is **DEFERRED** pending a public,
official, licence-compatible daily source. Neither absence blocks Track A.
