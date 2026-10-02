# V2 Stage B findings

## Scope and audit

Objective: test, without post-test tuning, whether alternative targets and causally available feature blocks improve next-observation gold forecasts beyond the frozen V1/persistence context. This document consolidates already completed Stage B outputs. No model, tuning, walk-forward, or ablation was rerun. V1 checksums remain byte-identical. All 99 canonical experiments have 296 frozen origins, finite forecasts, unique origins, reproduced MAE values, and correct price reconstruction for DELTA and LOG_RETURN.

The raw prediction files use `target_date` for the forecast-origin date rather than the following target date. This is a metadata-alignment defect, not a changed forecast value: the comparison tables reconcile dates through frozen `origin_manifest.csv` and retain raw files unchanged. Direct V1 claims are restricted to forecast-series reproductions.

## Main result

The lowest V2 result whose forecast series directly reproduces V1 is **11.6002 USD/oz** (PLS), versus **11.6002 USD/oz** in V1. It is a reproduction, not an improvement. V1 Holt-Winters remains the lowest frozen V1 reference at 11.5331 USD/oz.

## Targets and models

The best completed SARIMAX target is DELTA (11.5824 USD/oz); Holt-Winters is also closest to persistence in DELTA (11.6352). PLS A2/DELTA reaches 11.5856. RF's lowest experimental MAE is LOG_RETURN/A3 at 11.2986, but it is not a direct V1 replacement. In particular, A8 falls from 39.5007 in LEVEL to 12.1579 (DELTA) and 11.7850 (LOG_RETURN), showing that transformed targets reduce the observed RF level extrapolation problem; neither A8 transformed-target result beats persistence.

Residual means are small relative to their residual standard deviations for the best DELTA configurations (reported in `model_summary.csv`), so this aggregate check does not show a large average directional bias. Stage B does not contain a new Ljung-Box/ACF residual output; therefore it does not claim a new residual-autocorrelation conclusion beyond the frozen V1 diagnostics.

## RF A8 diagnosis

For RF LEVEL, A2/V1 features MAE is 14.2826, while A8 core is 39.5007. The A8 diagnostic training target range ends at 725.75; 281 of 296 test targets exceed that value. This makes the observed weakness consistent with a tree-model extrapolation limit, compounded by distribution shift and redundant technical blocks—not a basis for post-test optimization. Block permutation and drift are diagnostic-only; they do not authorize feature changes.

## Ablation and stability

For RF LEVEL, removing `GOLD_PRICE` from FULL costs 2.0914 USD/oz (14.0%). Removing all gold lags changes MAE by -0.2929 USD/oz (a small apparent improvement, still worse than persistence), so this result is not evidence to remove lags. Exogenous-only MAE is 38.1406; it does not work as a standalone predictor. In the technical path, USD produces the largest observed external reduction, taking A3 from 657.89 to 171.24; rates reduce it further to 39.93; risk worsens it to 41.60, while the remaining A8 additions partly recover to 39.50. Thus USD is the largest observed external helper in this path, rates are a further stabilizer, and risk is the clearest observed detractor. The available importance/drift output covers one test period only, so cross-regime feature stability is **not assessable**. It shows drift and redundancy candidates, not stable causal importance.

## PLS and recommendation

PLS uses 11 components for the 12-feature A2/V1 configuration (11/12 = 91.7%). Thus, this configuration does not provide meaningful dimensionality reduction. V2 should remain a complementary diagnostic study: it clarifies target transformations, feature dependence, and RF extrapolation, but does not displace the frozen V1 as the principal result.

## Remaining limitations

The raw date-label defect must remain visible in any reuse of the prediction files. Stability has only a single-period diagnostic, external availability is governed by conservative documented lags rather than intraday vintage timestamps, and no post-test optimization was performed or is justified by these results.
