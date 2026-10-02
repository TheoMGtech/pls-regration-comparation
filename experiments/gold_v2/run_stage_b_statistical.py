"""Resumable fixed-configuration Stage B statistical models and RF diagnostics.

This runner applies the already frozen V1 SARIMAX/Holt-Winters structures to
the three predeclared V2 targets.  It never selects parameters from the test
window; RF diagnostics are labelled diagnostic-only and do not feed features
or hyperparameters back into any model.
"""
from __future__ import annotations

import json
import time
import traceback
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "outputs" / "models"
DIAG = HERE / "outputs" / "diagnostics"
OUT.mkdir(parents=True, exist_ok=True)
DIAG.mkdir(parents=True, exist_ok=True)
STATE = OUT / "stage_b_extended_state.json"
LOG = OUT / "stage_b_extended.log"


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str) -> None:
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(f"{stamp()} {message}\n")


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        # Stage B finishes before Phase C.  Its latest validated snapshot is a
        # safe recovery point if an interrupted write leaves the mutable state
        # file empty; completed metrics themselves remain immutable outputs.
        health = OUT / "stage_b_health.json"
        if health.exists():
            cached = json.loads(health.read_text(encoding="utf-8")).get("worker_state")
            if isinstance(cached, dict):
                return cached
        raise


def save_state(state: dict) -> None:
    temporary = STATE.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(STATE)


def native_name(target: str) -> str:
    return {"LEVEL": "TARGET", "DELTA": "target_delta", "LOG_RETURN": "target_log_return"}[target]


def decode(row: pd.Series, target: str, prediction: float) -> tuple[float, float, float, float]:
    if target == "LEVEL":
        return prediction, float(row.TARGET), prediction, float(row.TARGET)
    if target == "DELTA":
        return float(row.GOLD_PRICE + prediction), float(row.TARGET - row.GOLD_PRICE), prediction, float(row.TARGET)
    return float(row.GOLD_PRICE * np.exp(prediction)), float(np.log(row.TARGET / row.GOLD_PRICE)), prediction, float(row.TARGET)


def fit_predict(model: str, train: pd.DataFrame, row: pd.Series, target: str, exog: list[str]) -> float:
    y = train[native_name(target)].astype(float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if model == "SARIMAX":
            fitted = SARIMAX(
                y,
                exog=train[exog].astype(float),
                order=(0, 1, 2),
                seasonal_order=(0, 0, 1, 5),
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False, maxiter=100)
            return float(fitted.forecast(steps=1, exog=row[exog].astype(float).to_frame().T).iloc[0])
        fitted = ExponentialSmoothing(
            y,
            trend="add",
            damped_trend=False,
            seasonal="add",
            seasonal_periods=5,
            initialization_method="estimated",
        ).fit(optimized=True)
        return float(fitted.forecast(1).iloc[0])


def run_model(data: pd.DataFrame, origins: list[int], model: str, target: str, exog: list[str]) -> None:
    feature_set = "A2_v1_exog" if model == "SARIMAX" else "A0_univariate"
    stem = f"{model}_{target}_{feature_set}"
    prediction_path = OUT / f"{stem}_predictions.csv"
    metric_path = OUT / f"{stem}_metrics.csv"
    if prediction_path.exists() and metric_path.exists():
        return
    rows: list[dict] = []
    partial = OUT / f"{stem}_predictions_partial.csv"
    if partial.exists():
        try:
            rows = pd.read_csv(partial).to_dict("records")
        except pd.errors.EmptyDataError:
            # A process interruption can leave a zero-byte checkpoint.  It
            # contains no predictions, so discarding it resumes from origin 1.
            partial.unlink()
    completed = {int(item["origin_index"]) for item in rows}
    started = time.perf_counter()
    log(f"START {model} {target} {feature_set}")
    for position, origin in enumerate(origins, 1):
        if origin in completed:
            continue
        row = data.iloc[origin]
        columns = [native_name(target)] + (exog if model == "SARIMAX" else [])
        train = data.iloc[:origin].dropna(subset=columns)
        if model == "SARIMAX" and row[exog].isna().any():
            continue
        prediction = fit_predict(model, train, row, target, exog)
        price, true_native, pred_native, true_price = decode(row, target, prediction)
        rows.append({
            "origin_index": origin,
            "target_date": row.DATE,
            "y_true_price": true_price,
            "y_pred_price": price,
            "y_true_native": true_native,
            "y_pred_native": pred_native,
            "abs_error_usd": abs(true_price - price),
            "abs_error_native": abs(true_native - pred_native),
            "direction_correct": int(np.sign(price - row.GOLD_PRICE) == np.sign(true_price - row.GOLD_PRICE)),
        })
        if position % 25 == 0:
            pd.DataFrame(rows).to_csv(partial, index=False)
    frame = pd.DataFrame(rows)
    frame.to_csv(prediction_path, index=False)
    metrics = {
        "model": model,
        "target": target,
        "feature_set": feature_set,
        "mae_usd": float(frame.abs_error_usd.mean()),
        "mae_native": float(frame.abs_error_native.mean()),
        "directional_accuracy": float(frame.direction_correct.mean()),
        "n_features": len(exog) if model == "SARIMAX" else 0,
        "n_origins": len(frame),
        "elapsed_seconds": time.perf_counter() - started,
        "directly_comparable_v1": target == "LEVEL",
        "methodological_status": "fixed_v1_configuration_no_test_retuning",
    }
    pd.DataFrame([metrics]).to_csv(metric_path, index=False)
    log("DONE " + json.dumps(metrics))


def rf_diagnostics(data: pd.DataFrame, origins: list[int]) -> None:
    marker = DIAG / "rf_a8_diagnostics.json"
    if marker.exists():
        return
    blocks = json.loads((HERE / "config" / "feature_blocks.json").read_text(encoding="utf-8"))
    features = blocks["A8_technical_all_core"]
    split = origins[0]
    train = data.iloc[:split].dropna(subset=features + ["TARGET"])
    test = data.iloc[origins].dropna(subset=features + ["TARGET"])
    model = RandomForestRegressor(n_estimators=300, max_depth=20, min_samples_split=10, min_samples_leaf=5, max_features=1.0, random_state=42, n_jobs=-1)
    model.fit(train[features], train.TARGET)
    permutation = permutation_importance(model, test[features], test.TARGET, scoring="neg_mean_absolute_error", n_repeats=5, random_state=42, n_jobs=-1)
    importance = pd.DataFrame({"feature": features, "mae_increase": permutation.importances_mean, "mae_increase_std": permutation.importances_std})
    importance.to_csv(DIAG / "rf_a8_permutation_importance.csv", index=False)
    drift = pd.DataFrame({
        "feature": features,
        "train_mean": train[features].mean(),
        "test_mean": test[features].mean(),
        "train_std": train[features].std(),
        "test_std": test[features].std(),
    })
    drift["standardized_mean_shift"] = (drift.test_mean - drift.train_mean) / drift.train_std.replace(0, np.nan)
    drift.to_csv(DIAG / "rf_a8_feature_drift.csv", index=False)
    groups = {name: [feature for feature in values if feature in features] for name, values in blocks.items() if name in {"A3_gold_technical_no_raw", "A4_exogenous_only", "A5_technical_usd", "A6_technical_usd_rates", "A7_technical_usd_rates_risk", "A8_technical_all_core"}}
    baseline = float(np.mean(np.abs(test.TARGET - model.predict(test[features]))) )
    rng = np.random.default_rng(42)
    grouped = []
    for name, columns in groups.items():
        columns = sorted(set(columns))
        if not columns:
            continue
        scores = []
        for _ in range(5):
            shuffled = test[features].copy()
            shuffled.loc[:, columns] = shuffled.loc[:, columns].iloc[rng.permutation(len(shuffled))].to_numpy()
            scores.append(float(np.mean(np.abs(test.TARGET - model.predict(shuffled)))))
        grouped.append({"block": name, "n_features": len(columns), "baseline_mae": baseline, "permuted_mae": float(np.mean(scores)), "mae_increase": float(np.mean(scores) - baseline)})
    pd.DataFrame(grouped).to_csv(DIAG / "rf_a8_block_permutation.csv", index=False)
    payload = {
        "status": "diagnostic_only_not_used_for_selection",
        "train_y_range": [float(train.TARGET.min()), float(train.TARGET.max())],
        "test_y_range": [float(test.TARGET.min()), float(test.TARGET.max())],
        "n_train": len(train),
        "n_test": len(test),
        "fixed_rf_configuration": {"n_estimators": 300, "max_depth": 20, "min_samples_split": 10, "min_samples_leaf": 5, "max_features": 1.0, "random_state": 42},
    }
    marker.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    log("DONE RF_DIAGNOSTICS A8 diagnostic_only")


def consolidate() -> None:
    files = []
    for path in OUT.glob("*_metrics.csv"):
        try:
            files.append(pd.read_csv(path))
        except Exception:
            pass
    if files:
        pd.concat(files, ignore_index=True).drop_duplicates(["model", "target", "feature_set"], keep="last").to_csv(OUT / "consolidated_matrix.csv", index=False)


def main() -> None:
    data = pd.read_csv(HERE / "data" / "processed" / "gold_v2_features.csv")
    data["target_delta"] = data.TARGET - data.GOLD_PRICE
    data["target_log_return"] = np.log(data.TARGET / data.GOLD_PRICE)
    protocol = json.loads((ROOT / "analyses/grupo5/outputs/protocol.json").read_text(encoding="utf-8"))
    origins = protocol["origins"]["test"]
    exog = protocol["sarimax_exog"]
    state = load_state()
    state["phase_c_status"] = "running"
    state.pop("phase_c_traceback", None)
    state.pop("phase_c_failed_at_utc", None)
    save_state(state)
    for model in ("SARIMAX", "Holt_Winters"):
        for target in ("LEVEL", "DELTA", "LOG_RETURN"):
            state["phase_c_current"] = f"{model}_{target}"
            save_state(state)
            run_model(data, origins, model, target, exog)
    state["phase_c_current"] = "RF_DIAGNOSTICS"
    save_state(state)
    rf_diagnostics(data, origins)
    consolidate()
    state["phase_c_status"] = "completed"
    state["phase_c_completed_at_utc"] = stamp()
    state.pop("phase_c_current", None)
    save_state(state)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        state = load_state()
        state["phase_c_status"] = "failed"
        state["phase_c_traceback"] = traceback.format_exc()
        state["phase_c_failed_at_utc"] = stamp()
        save_state(state)
        raise
