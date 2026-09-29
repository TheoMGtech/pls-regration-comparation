# V2 status

## Completed — Stage A

- [x] Isolated `feature/gold-v2-deep-analysis` branch from synced `develop`.
- [x] V1 reference checksums before/after: 144 tracked V1 files, identical.
- [x] Official FRED downloads for DTWEXB, VIXCLS, NASDAQCOM, DGS2, DCOILWTICO and DFII10, with hashes and metadata.
- [x] Conservative availability rules and causal feature table.
- [x] Level, delta and log-return targets; target-difficulty and V1-MAE context outputs.
- [x] Lightweight validation-only ablation feasibility screen.

## Deferred / not run

- [ ] Any heavy tuning, full walk-forward, or final V1-vs-V2 claim.
- [ ] SARIMAX, Random Forest, and PLS candidate selection for V2.
- [ ] Final ablation, block permutation, VIP and feature-stability windows.
- [ ] EPU, GPR and silver ingestion.

## Gate

Stage B is blocked until explicit human approval. `heavy_stage_authorized` is
`false` in `config/protocol_v2.json`.
