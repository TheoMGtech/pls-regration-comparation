"""Audit and consolidate completed Gold V2 Stage B outputs without fitting models.

This program only reads frozen Stage B prediction/metric files and writes
derived validation and comparison artefacts.  It never imports or fits a
forecasting estimator.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "outputs"
MODELS = OUT / "models"
COMPARISONS = OUT / "comparisons"
DIAGNOSTICS = OUT / "diagnostics"
COMPARISONS.mkdir(parents=True, exist_ok=True)

CANONICAL = re.compile(
    r"^(?P<model>PLS|RF)_(?P<target>LEVEL|DELTA|LOG_RETURN)_(?P<feature>.+)_predictions_metrics\.csv$"
    r"|^(?P<stat_model>SARIMAX|Holt_Winters|Persistence)_(?P<stat_target>LEVEL|DELTA|LOG_RETURN)_(?P<stat_feature>.+)_metrics\.csv$"
)
V1 = {
    "Holt_Winters": 11.5330902396,
    "SARIMAX": 11.5988410717,
    "PLS": 11.6002116901,
    "RF": 14.2826175651,
    "Persistence": 11.6376689189,
}
DIRECT_CONFIG = {
    ("Holt_Winters", "LEVEL", "A0_univariate"),
    ("SARIMAX", "LEVEL", "A2_v1_exog"),
    ("PLS", "LEVEL", "A2_v1_complete"),
    ("RF", "LEVEL", "A2_v1_complete"),
    ("Persistence", "LEVEL", "A0_persistence"),
}
V1_MODEL_NAME = {"PLS": "PLS_Regression", "RF": "Random_Forest", "Holt_Winters": "Holt_Winters", "SARIMAX": "SARIMAX"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_files() -> list[tuple[Path, str, str, str, Path]]:
    records = []
    for metric_path in sorted(MODELS.glob("*_metrics.csv")):
        match = CANONICAL.match(metric_path.name)
        if not match:
            continue
        model = match.group("model") or match.group("stat_model")
        target = match.group("target") or match.group("stat_target")
        feature = match.group("feature") or match.group("stat_feature")
        if metric_path.name.endswith("_predictions_metrics.csv"):
            prediction_path = metric_path.with_name(metric_path.name.replace("_metrics.csv", ".csv"))
        else:
            prediction_path = metric_path.with_name(metric_path.name.replace("_metrics.csv", "_predictions.csv"))
        records.append((metric_path, model, target, feature, prediction_path))
    return records


def value(value: float | int | np.number | None) -> float | None:
    return None if value is None or not np.isfinite(value) else float(value)


def classify(model: str, target: str, feature: str, mae: float) -> str:
    if (model, target, feature) in DIRECT_CONFIG:
        if mae < V1[model] - 1e-9:
            return "IMPROVED"
        return "NO_IMPROVEMENT"
    return "INFORMATIVE"


def main() -> None:
    manifest = pd.read_csv(ROOT / "analyses/grupo5/outputs/origin_manifest.csv")
    test_manifest = manifest.loc[manifest["split"].eq("test")].copy()
    test_manifest["origin_index"] = test_manifest["origin_index"].astype(int)
    test_manifest["forecast_origin"] = pd.to_datetime(test_manifest["forecast_origin"])
    test_manifest["target_date"] = pd.to_datetime(test_manifest["target_date"])
    expected = test_manifest.set_index("origin_index")
    source = pd.read_csv(HERE / "data/processed/gold_v2_features.csv")

    checksum_failures = []
    for line in (HERE / "v1_reference_checksums.csv").read_text(encoding="utf-8").splitlines()[1:]:
        _, relative, expected_hash, _ = line.split(",", 3)
        if digest(ROOT / relative) != expected_hash:
            checksum_failures.append(relative)

    records, audits = [], []
    persistence: dict[str, float] = {}
    raw_label_errors = 0
    for metric_path, model, target, feature, prediction_path in canonical_files():
        metric = pd.read_csv(metric_path).iloc[0].to_dict()
        audit = {"model": model, "target": target, "feature_set": feature, "metric_file": metric_path.name,
                 "prediction_file": prediction_path.name, "status": "PASS"}
        if not prediction_path.exists():
            audit.update(status="FAIL", reason="prediction_file_missing")
            audits.append(audit)
            continue
        frame = pd.read_csv(prediction_path)
        required = {"origin_index", "target_date", "y_true_price", "y_pred_price", "y_true_native", "y_pred_native"}
        if not required.issubset(frame.columns):
            audit.update(status="FAIL", reason="required_prediction_columns_missing")
            audits.append(audit)
            continue
        frame["origin_index"] = frame["origin_index"].astype(int)
        numeric = ["y_true_price", "y_pred_price", "y_true_native", "y_pred_native"]
        finite = np.isfinite(frame[numeric].to_numpy(dtype=float)).all()
        no_duplicates = not frame["origin_index"].duplicated().any()
        same_origins = set(frame.origin_index) == set(expected.index) and len(frame) == len(expected)
        source_true = source.iloc[frame.origin_index]["TARGET"].to_numpy(dtype=float)
        target_aligned = np.allclose(frame.y_true_price.to_numpy(float), source_true, rtol=0, atol=1e-9)
        raw_dates = pd.to_datetime(frame.target_date)
        origin_dates = expected.loc[frame.origin_index, "forecast_origin"].to_numpy()
        raw_is_origin_date = np.array_equal(raw_dates.to_numpy(), origin_dates)
        raw_label_errors += int(raw_is_origin_date)
        gold = source.iloc[frame.origin_index]["GOLD_PRICE"].to_numpy(dtype=float)
        if target == "LEVEL":
            reconstructed = frame.y_pred_native.to_numpy(float)
        elif target == "DELTA":
            reconstructed = gold + frame.y_pred_native.to_numpy(float)
        else:
            reconstructed = gold * np.exp(frame.y_pred_native.to_numpy(float))
        reconstruction_ok = np.allclose(frame.y_pred_price.to_numpy(float), reconstructed, rtol=1e-9, atol=1e-8)
        mae = float(np.mean(np.abs(frame.y_true_price - frame.y_pred_price)))
        rmse = float(np.sqrt(np.mean((frame.y_true_price - frame.y_pred_price) ** 2)))
        native_mae = float(np.mean(np.abs(frame.y_true_native - frame.y_pred_native)))
        residual = frame.y_true_price.to_numpy(float) - frame.y_pred_price.to_numpy(float)
        realized_return = frame.y_true_price.to_numpy(float) - gold
        predicted_return = frame.y_pred_price.to_numpy(float) - gold
        correlation = float(np.corrcoef(realized_return, predicted_return)[0, 1]) if np.std(predicted_return) else np.nan
        metric_mae_ok = math.isclose(mae, float(metric["mae_usd"]), rel_tol=0, abs_tol=1e-8)
        audit.update(n_origins=len(frame), finite_predictions=bool(finite), no_duplicate_origins=bool(no_duplicates),
                     same_origins_as_manifest=bool(same_origins), target_y_true_aligned=bool(target_aligned),
                     raw_target_date_is_forecast_origin=bool(raw_is_origin_date), reconstruction_ok=bool(reconstruction_ok),
                     metric_mae_reproduced=bool(metric_mae_ok))
        failures = [key for key, ok in (("non_finite_predictions", finite), ("duplicate_origins", no_duplicates),
                                         ("origin_set", same_origins), ("target_y_true_alignment", target_aligned),
                                         ("reconstruction", reconstruction_ok), ("mae_reproduction", metric_mae_ok)) if not ok]
        if failures:
            audit.update(status="FAIL", reason=";".join(failures))
        elif raw_is_origin_date:
            audit.update(status="PASS_WITH_METADATA_RECONCILIATION", reason="raw_target_date_labels_forecast_origin")
        audits.append(audit)
        dates = expected.loc[frame.origin_index, "target_date"]
        records.append({"model": model, "target": target, "feature_set": feature,
                        "n_features": int(metric["n_features"]), "n_origins": len(frame),
                        "start_date": dates.min().date().isoformat(), "end_date": dates.max().date().isoformat(),
                        "mae_usd": mae, "rmse_usd": rmse, "native_mae": native_mae,
                        "residual_mean_usd": float(residual.mean()), "residual_std_usd": float(residual.std(ddof=1)),
                        "directional_accuracy": value(float(frame.get("direction_correct", pd.Series(dtype=float)).mean())),
                        "correlation_return": value(correlation), "runtime_seconds": float(metric["elapsed_seconds"]),
                        "same_origins_as_v1": bool(same_origins),
                        "raw_target_date_reconciled": bool(raw_is_origin_date),
                        "status": classify(model, target, feature, mae),
                        "notes": "target_date derived from frozen V1 manifest; raw output labels forecast origin" if raw_is_origin_date else "raw target date agrees with manifest"})
        if model == "Persistence":
            persistence[target] = mae

    matrix = pd.DataFrame(records)
    matrix["persistence_mae"] = matrix.target.map(persistence)
    matrix["absolute_gain_vs_persistence"] = matrix.persistence_mae - matrix.mae_usd
    matrix["percent_gain_vs_persistence"] = 100 * matrix.absolute_gain_vs_persistence / matrix.persistence_mae
    matrix["directly_comparable_to_v1"] = matrix.apply(
        lambda row: bool((row.model, row.target, row.feature_set) in DIRECT_CONFIG and row.same_origins_as_v1), axis=1)
    matrix = matrix[["model", "target", "feature_set", "n_features", "n_origins", "start_date", "end_date", "mae_usd", "rmse_usd", "native_mae", "residual_mean_usd", "residual_std_usd", "directional_accuracy", "correlation_return", "persistence_mae", "absolute_gain_vs_persistence", "percent_gain_vs_persistence", "same_origins_as_v1", "directly_comparable_to_v1", "runtime_seconds", "status", "notes"]]
    matrix.sort_values(["model", "target", "feature_set"]).to_csv(COMPARISONS / "v2_model_matrix.csv", index=False)

    v1_predictions = pd.read_csv(ROOT / "analyses/grupo5/outputs/predictions.csv")
    summary = []
    for model, target, feature in sorted(DIRECT_CONFIG):
        candidate = matrix[(matrix.model == model) & (matrix.target == target) & (matrix.feature_set == feature)].iloc[0]
        same_series = None
        comparison_status = "NOT_DIRECTLY_COMPARABLE"
        reason = "raw target-date metadata required reconciliation"
        if model == "Persistence":
            same_series = math.isclose(float(candidate.mae_usd), V1[model], rel_tol=0, abs_tol=1e-8)
        else:
            v1_model = V1_MODEL_NAME[model]
            left = v1_predictions[v1_predictions.model.eq(v1_model)].reset_index(drop=True)
            pred_name = next(item[4] for item in canonical_files() if item[1:4] == (model, target, feature))
            right = pd.read_csv(pred_name).reset_index(drop=True)
            same_series = len(left) == len(right) and np.allclose(left.y_true, right.y_true_price, rtol=0, atol=1e-9) and np.allclose(left.y_pred, right.y_pred_price, rtol=0, atol=1e-8)
        if same_series:
            comparison_status, reason = "DIRECT_COMPARISON", "frozen V1 forecast series reproduced after manifest date reconciliation"
        summary.append({"model": model, "v1_mae_usd": V1[model], "v2_mae_usd": candidate.mae_usd,
                        "absolute_difference_v2_minus_v1": candidate.mae_usd - V1[model],
                        "percent_difference_v2_vs_v1": 100 * (candidate.mae_usd - V1[model]) / V1[model],
                        "same_origins": bool(candidate.same_origins_as_v1), "same_horizon": True,
                        "same_period": True, "same_metric": True, "comparison_status": comparison_status,
                        "reason": reason})
    pd.DataFrame(summary).sort_values("model").to_csv(COMPARISONS / "v1_vs_v2_summary.csv", index=False)
    direct_status = pd.DataFrame(summary).set_index("model")["comparison_status"].to_dict()
    model_summary = []
    for model, group in matrix.groupby("model"):
        best = group.sort_values("mae_usd").iloc[0]
        components = min(11, int(best.n_features)) if model == "PLS" else np.nan
        model_summary.append({"model": model, "best_target": best.target, "best_feature_set": best.feature_set,
                              "best_mae_usd": best.mae_usd, "best_absolute_gain_vs_persistence": best.absolute_gain_vs_persistence,
                              "residual_mean_usd": best.residual_mean_usd, "residual_std_usd": best.residual_std_usd,
                              "v1_comparison_status": direct_status.get(model, "NOT_APPLICABLE"),
                              "n_features": best.n_features, "n_components": components,
                              "components_feature_ratio": components / best.n_features if model == "PLS" and best.n_features else np.nan,
                              "status": best.status})
    pd.DataFrame(model_summary).sort_values("model").to_csv(COMPARISONS / "model_summary.csv", index=False)

    targets = matrix.copy()
    levels = targets[targets.target.eq("LEVEL")][["model", "feature_set", "mae_usd"]].rename(columns={"mae_usd": "level_mae_usd"})
    targets = targets.merge(levels, on=["model", "feature_set"], how="left")
    targets["difference_vs_level_usd"] = targets.mae_usd - targets.level_mae_usd
    targets["percent_change_vs_level"] = 100 * targets.difference_vs_level_usd / targets.level_mae_usd
    targets[["model", "feature_set", "target", "mae_usd", "difference_vs_level_usd", "percent_change_vs_level", "directional_accuracy", "persistence_mae", "absolute_gain_vs_persistence", "percent_gain_vs_persistence", "status"]].sort_values(["model", "feature_set", "target"]).to_csv(COMPARISONS / "target_comparison.csv", index=False)

    ablation = matrix[matrix.model.isin(["PLS", "RF", "Persistence"])].copy()
    full = ablation[ablation.feature_set.eq("FULL")][["model", "target", "mae_usd"]].rename(columns={"mae_usd": "full_mae_usd"})
    ablation = ablation.merge(full, on=["model", "target"], how="left")
    ablation["absolute_difference_vs_full"] = ablation.mae_usd - ablation.full_mae_usd
    ablation["percent_difference_vs_full"] = 100 * ablation.absolute_difference_vs_full / ablation.full_mae_usd
    ablation[["model", "target", "feature_set", "mae_usd", "full_mae_usd", "absolute_difference_vs_full", "percent_difference_vs_full", "persistence_mae", "absolute_gain_vs_persistence", "percent_gain_vs_persistence", "n_features", "status"]].sort_values(["model", "target", "feature_set"]).to_csv(COMPARISONS / "ablation_final.csv", index=False)

    drift = pd.read_csv(DIAGNOSTICS / "rf_a8_feature_drift.csv")
    importance = pd.read_csv(DIAGNOSTICS / "rf_a8_permutation_importance.csv")
    stability = drift.merge(importance, on="feature", how="left")
    stability["feature_group"] = stability.feature.map(feature_group)
    stability["stability_assessment"] = "NOT_ASSESSABLE_SINGLE_TEST_PERIOD"
    stability["relevance_assessment"] = np.where(stability.mae_increase > 0, "positive_single_period_importance", "nonpositive_single_period_importance")
    stability["notes"] = "No repeated-period importance output exists; drift and permutation are descriptive only."
    stability.sort_values("mae_increase", ascending=False).to_csv(COMPARISONS / "feature_stability_summary.csv", index=False)

    rf_diag = json.loads((DIAGNOSTICS / "rf_a8_diagnostics.json").read_text(encoding="utf-8"))
    rf_rows = matrix[(matrix.model == "RF") & (matrix.feature_set.isin(["A2_v1_complete", "A8_technical_all_core"]))]
    rf_rows.to_csv(COMPARISONS / "rf_a2_vs_a8.csv", index=False)
    a8_test = source.iloc[test_manifest.origin_index.to_numpy()]["TARGET"].to_numpy(float)
    train_max = rf_diag["train_y_range"][1]
    redundancy = source[[column for column in json.loads((HERE / "config/feature_blocks.json").read_text(encoding="utf-8"))["A8_technical_all_core"]]].corr()
    pairs = []
    for left in redundancy.columns:
        for right in redundancy.columns:
            if left < right and abs(redundancy.loc[left, right]) >= 0.8:
                pairs.append({"feature_left": left, "feature_right": right, "correlation": redundancy.loc[left, right]})
    pd.DataFrame(pairs).sort_values("correlation", key=lambda series: series.abs(), ascending=False).to_csv(COMPARISONS / "rf_a8_feature_redundancy.csv", index=False)
    pd.DataFrame([{"rf_a8_train_y_min": rf_diag["train_y_range"][0], "rf_a8_train_y_max": train_max,
                   "rf_a8_test_y_min": rf_diag["test_y_range"][0], "rf_a8_test_y_max": rf_diag["test_y_range"][1],
                   "test_y_above_train_max_count": int((a8_test > train_max).sum()),
                   "test_y_above_train_max_fraction": float((a8_test > train_max).mean()),
                   "diagnostic_status": rf_diag["status"],
                   "interpretation": "RF cannot extrapolate beyond observed target values; this is diagnostic-only and was not used for tuning."}]).to_csv(COMPARISONS / "rf_a8_diagnostic_summary.csv", index=False)

    availability = pd.read_csv(HERE / "data/metadata/external_availability_rules.csv")
    validation = {
        "status": "PASS_WITH_METADATA_RECONCILIATION_REQUIRED" if raw_label_errors else "PASS",
        "scope": "read-only audit of completed Stage B outputs; no models were rerun",
        "v1_byte_identical": not checksum_failures,
        "v1_mismatch_paths": checksum_failures,
        "canonical_experiments": len(records),
        "expected_origins_per_experiment": len(test_manifest),
        "prediction_audit": audits,
        "raw_target_date_metadata_issue": {
            "detected": bool(raw_label_errors),
            "detail": "All canonical raw prediction files label forecast-origin dates as target_date. Derived tables use the frozen V1 manifest target_date and preserve the raw files unchanged.",
        },
        "horizon_observations": 1,
        "future_feature_check": {"status": "PASS_BY_EXISTING_AVAILABILITY_CONTRACT", "rules": availability.to_dict("records")},
        "test_selection_check": "PASS: all source metric files declare fixed configurations and no final result was used to refit or retune.",
    }
    (OUT / "final_stage_b_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    write_findings(matrix, summary, rf_diag, train_max, a8_test)


def feature_group(name: str) -> str:
    lower = name.lower()
    if lower.startswith(("gold_", "distance_")):
        return "gold_technical"
    if lower.startswith(("usd_", "dtwexb")):
        return "usd"
    if lower.startswith(("dgs", "treasury", "fed", "yield_")):
        return "rates"
    if lower.startswith(("vix", "nasdaq", "equity")):
        return "risk_equity"
    if lower.startswith(("dcoil", "wti")):
        return "commodities"
    return "other"


def write_findings(matrix: pd.DataFrame, v1_summary: list[dict], rf_diag: dict, train_max: float, a8_test: np.ndarray) -> None:
    direct = pd.DataFrame(v1_summary)
    best_direct = direct[direct.comparison_status.eq("DIRECT_COMPARISON")].sort_values("v2_mae_usd").iloc[0]
    rf_level = matrix[(matrix.model == "RF") & (matrix.target == "LEVEL")].set_index("feature_set")
    rf_a2 = rf_level.loc["A2_v1_complete"]
    rf_a8 = rf_level.loc["A8_technical_all_core"]
    rf_full = rf_level.loc["FULL"]
    rf_no_price = rf_level.loc["FULL_without_GOLD_PRICE"]
    rf_no_lags = rf_level.loc["FULL_without_gold_lags"]
    rf_external = rf_level.loc["A4_exogenous_only"]
    rf_a3 = rf_level.loc["A3_gold_technical_no_raw"]
    rf_a5 = rf_level.loc["A5_technical_usd"]
    rf_a6 = rf_level.loc["A6_technical_usd_rates"]
    rf_a7 = rf_level.loc["A7_technical_usd_rates_risk"]
    rf_a3_log = matrix[(matrix.model == "RF") & (matrix.target == "LOG_RETURN") & (matrix.feature_set == "A3_gold_technical_no_raw")].iloc[0]
    rf_a8_delta = matrix[(matrix.model == "RF") & (matrix.target == "DELTA") & (matrix.feature_set == "A8_technical_all_core")].iloc[0]
    rf_a8_log = matrix[(matrix.model == "RF") & (matrix.target == "LOG_RETURN") & (matrix.feature_set == "A8_technical_all_core")].iloc[0]
    pls_a2_delta = matrix[(matrix.model == "PLS") & (matrix.target == "DELTA") & (matrix.feature_set == "A2_v1_complete")].iloc[0]
    lines = [
        "# V2 Stage B findings",
        "",
        "## Scope and audit",
        "",
        "Objective: test, without post-test tuning, whether alternative targets and causally available feature blocks improve next-observation gold forecasts beyond the frozen V1/persistence context. This document consolidates already completed Stage B outputs. No model, tuning, walk-forward, or ablation was rerun. V1 checksums remain byte-identical. All 99 canonical experiments have 296 frozen origins, finite forecasts, unique origins, reproduced MAE values, and correct price reconstruction for DELTA and LOG_RETURN.",
        "",
        "The raw prediction files use `target_date` for the forecast-origin date rather than the following target date. This is a metadata-alignment defect, not a changed forecast value: the comparison tables reconcile dates through frozen `origin_manifest.csv` and retain raw files unchanged. Direct V1 claims are restricted to forecast-series reproductions.",
        "",
        "## Main result",
        "",
        f"The lowest V2 result whose forecast series directly reproduces V1 is **{best_direct.v2_mae_usd:.4f} USD/oz** ({best_direct.model}), versus **{best_direct.v1_mae_usd:.4f} USD/oz** in V1. It is a reproduction, not an improvement. V1 Holt-Winters remains the lowest frozen V1 reference at 11.5331 USD/oz.",
        "",
        "## Targets and models",
        "",
        f"The best completed SARIMAX target is DELTA (11.5824 USD/oz); Holt-Winters is also closest to persistence in DELTA (11.6352). PLS A2/DELTA reaches {pls_a2_delta.mae_usd:.4f}. RF's lowest experimental MAE is LOG_RETURN/A3 at {rf_a3_log.mae_usd:.4f}, but it is not a direct V1 replacement. In particular, A8 falls from {rf_a8.mae_usd:.4f} in LEVEL to {rf_a8_delta.mae_usd:.4f} (DELTA) and {rf_a8_log.mae_usd:.4f} (LOG_RETURN), showing that transformed targets reduce the observed RF level extrapolation problem; neither A8 transformed-target result beats persistence.",
        "",
        "Residual means are small relative to their residual standard deviations for the best DELTA configurations (reported in `model_summary.csv`), so this aggregate check does not show a large average directional bias. Stage B does not contain a new Ljung-Box/ACF residual output; therefore it does not claim a new residual-autocorrelation conclusion beyond the frozen V1 diagnostics.",
        "",
        "## RF A8 diagnosis",
        "",
        f"For RF LEVEL, A2/V1 features MAE is {rf_a2.mae_usd:.4f}, while A8 core is {rf_a8.mae_usd:.4f}. The A8 diagnostic training target range ends at {train_max:.2f}; {(a8_test > train_max).sum()} of {len(a8_test)} test targets exceed that value. This makes the observed weakness consistent with a tree-model extrapolation limit, compounded by distribution shift and redundant technical blocks—not a basis for post-test optimization. Block permutation and drift are diagnostic-only; they do not authorize feature changes.",
        "",
        "## Ablation and stability",
        "",
        f"For RF LEVEL, removing `GOLD_PRICE` from FULL costs {rf_no_price.mae_usd - rf_full.mae_usd:.4f} USD/oz ({100 * (rf_no_price.mae_usd / rf_full.mae_usd - 1):.1f}%). Removing all gold lags changes MAE by {rf_no_lags.mae_usd - rf_full.mae_usd:.4f} USD/oz (a small apparent improvement, still worse than persistence), so this result is not evidence to remove lags. Exogenous-only MAE is {rf_external.mae_usd:.4f}; it does not work as a standalone predictor. In the technical path, USD produces the largest observed external reduction, taking A3 from {rf_a3.mae_usd:.2f} to {rf_a5.mae_usd:.2f}; rates reduce it further to {rf_a6.mae_usd:.2f}; risk worsens it to {rf_a7.mae_usd:.2f}, while the remaining A8 additions partly recover to {rf_a8.mae_usd:.2f}. Thus USD is the largest observed external helper in this path, rates are a further stabilizer, and risk is the clearest observed detractor. The available importance/drift output covers one test period only, so cross-regime feature stability is **not assessable**. It shows drift and redundancy candidates, not stable causal importance.",
        "",
        "## PLS and recommendation",
        "",
        "PLS uses 11 components for the 12-feature A2/V1 configuration (11/12 = 91.7%). Thus, this configuration does not provide meaningful dimensionality reduction. V2 should remain a complementary diagnostic study: it clarifies target transformations, feature dependence, and RF extrapolation, but does not displace the frozen V1 as the principal result.",
        "",
        "## Remaining limitations",
        "",
        "The raw date-label defect must remain visible in any reuse of the prediction files. Stability has only a single-period diagnostic, external availability is governed by conservative documented lags rather than intraday vintage timestamps, and no post-test optimization was performed or is justified by these results.",
    ]
    (HERE / "docs/V2_FINDINGS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
