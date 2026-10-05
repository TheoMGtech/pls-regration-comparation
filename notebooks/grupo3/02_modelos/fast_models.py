"""Implementação anterior do Random Forest e do SARIMAX.

O protocolo vigente está em `protocolo_final.py`. Este módulo não é mais o
atalho de execução. O protocolo original reajustava o modelo em cada hora,
com 671 preditores no Random Forest e com sazonalidade 24 no SARIMAX. Nesta cópia:

- os dois modelos preveem PM2.5 da hora seguinte;
- os parâmetros são reestimados uma vez por dia e permanecem fixos nas horas
  daquele dia, já com o valor observado de cada hora anterior;
- o Random Forest usa um conjunto curto de preditores conhecidos na origem;
- o SARIMAX é não sazonal, numa janela recente, com poucas exógenas.
"""
from __future__ import annotations

import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")

TRAIN_END = pd.Timestamp("2015-09-25 06:00:00")
VAL_END = pd.Timestamp("2016-05-16 04:00:00")
TEST_START = pd.Timestamp("2016-05-16 05:00:00")
RANDOM_STATE = 42
REFIT = "uma vez por dia; parâmetros fixos dentro do dia"
WINDOW_HOURS = 24 * 14
SARIMAX_MAXITER = 20

RF_FEATURES = [
    "pm25_t",
    "pm25_t_1",
    "pm25_t_2",
    "pm25_t_23",
    "pm25_roll_mean_3",
    "pm25_roll_mean_24",
    "local_PM10",
    "local_CO",
    "local_TEMP",
    "local_WSPM",
    "local_DEWP",
    "Changping_PM2.5",
    "Wanliu_PM2.5",
    "target_hour_sin",
    "target_hour_cos",
    "target_dow_sin",
    "target_dow_cos",
]

RF_GRID = [
    {"n_estimators": 40, "max_depth": 12, "min_samples_leaf": 5, "max_features": "sqrt"},
    {"n_estimators": 40, "max_depth": 16, "min_samples_leaf": 2, "max_features": "sqrt"},
]

SARIMAX_EXOG = ["hour_sin", "hour_cos", "dow_sin", "dow_cos", "pm10_lag1", "temp_lag1", "wspm_lag1", "changping_pm25_lag1"]
SARIMAX_GRID = [
    {"order": (1, 0, 1), "seasonal_order": (0, 0, 0, 0), "trend": "n"},
    {"order": (1, 1, 1), "seasonal_order": (0, 0, 0, 0), "trend": "n"},
    {"order": (0, 1, 1), "seasonal_order": (0, 0, 0, 0), "trend": "n"},
]


def repository_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / "bases" / "grupo3").exists():
            return candidate
    raise FileNotFoundError("Raiz da cópia não encontrada.")


def _calendar(index: pd.DatetimeIndex, prefix: str) -> pd.DataFrame:
    hour = index.hour.to_numpy()
    dow = index.dayofweek.to_numpy()
    return pd.DataFrame(
        {
            f"{prefix}hour_sin": np.sin(2 * np.pi * hour / 24),
            f"{prefix}hour_cos": np.cos(2 * np.pi * hour / 24),
            f"{prefix}dow_sin": np.sin(2 * np.pi * dow / 7),
            f"{prefix}dow_cos": np.cos(2 * np.pi * dow / 7),
        },
        index=index,
    )


def load_modeling_frame(root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Monta a matriz curta do Random Forest e a série horária do SARIMAX."""
    columns = [
        "timestamp",
        "target_pm25",
        "local_PM10",
        "local_CO",
        "local_TEMP",
        "local_WSPM",
        "local_DEWP",
        "Changping_PM2.5",
        "Wanliu_PM2.5",
    ]
    prepared = pd.read_csv(
        root / "analyses" / "grupo3" / "01_dados" / "outputs" / "prepared_base3.csv",
        usecols=columns,
        parse_dates=["timestamp"],
    ).sort_values("timestamp")
    prepared = prepared.set_index("timestamp")
    if not prepared.index.is_monotonic_increasing or prepared.index.has_duplicates:
        raise ValueError("A base preparada precisa estar ordenada e sem timestamps duplicados.")

    pm = prepared["target_pm25"].astype(float)
    target_time = pm.index + pd.Timedelta(hours=1)
    calendar = _calendar(pd.DatetimeIndex(target_time), "target_")
    frame = pd.DataFrame(
        {
            "pm25_t": pm,
            "pm25_t_1": pm.shift(1),
            "pm25_t_2": pm.shift(2),
            "pm25_t_23": pm.shift(23),
            "pm25_roll_mean_3": pm.rolling(3, min_periods=3).mean(),
            "pm25_roll_mean_24": pm.rolling(24, min_periods=24).mean(),
            "local_PM10": prepared["local_PM10"],
            "local_CO": prepared["local_CO"],
            "local_TEMP": prepared["local_TEMP"],
            "local_WSPM": prepared["local_WSPM"],
            "local_DEWP": prepared["local_DEWP"],
            "Changping_PM2.5": prepared["Changping_PM2.5"],
            "Wanliu_PM2.5": prepared["Wanliu_PM2.5"],
            "y": pm.shift(-1),
        },
        index=pm.index,
    )
    frame = frame.join(calendar.set_index(pm.index))
    frame = frame.dropna(subset=RF_FEATURES + ["y"]).reset_index(names="timestamp")
    frame["target_timestamp"] = frame["timestamp"] + pd.Timedelta(hours=1)
    frame["split"] = np.where(
        frame["timestamp"] <= TRAIN_END,
        "train_interno",
        np.where(frame["timestamp"] <= VAL_END, "validacao_interna", "test_final"),
    )
    if not (frame["target_timestamp"] - frame["timestamp"]).eq(pd.Timedelta(hours=1)).all():
        raise ValueError("O horizonte deixou de ser de uma hora.")

    measurement_calendar = _calendar(pd.DatetimeIndex(pm.index), "")
    exog = measurement_calendar.copy()
    exog["pm10_lag1"] = prepared["local_PM10"].shift(1)
    exog["temp_lag1"] = prepared["local_TEMP"].shift(1)
    exog["wspm_lag1"] = prepared["local_WSPM"].shift(1)
    exog["changping_pm25_lag1"] = prepared["Changping_PM2.5"].shift(1)
    exog = exog[SARIMAX_EXOG].ffill().fillna(0.0)
    return frame, exog, pm


def _blocks(origins: pd.Series, limit: int | None) -> list[pd.Timestamp]:
    blocks = list(pd.Series(origins).dt.floor("D").drop_duplicates().sort_values())
    if limit is not None:
        return blocks[:limit]
    return blocks


def _prediction_row(model: str, split: str, origin: pd.Timestamp, y_true: float, y_pred: float) -> dict:
    y_pred = float(max(y_pred, 0.0))
    residual = float(y_true) - y_pred
    return {
        "model": model,
        "split": split,
        "forecast_origin": origin,
        "target_date": origin + pd.Timedelta(hours=1),
        "horizon": 1,
        "y_true": float(y_true),
        "y_pred": y_pred,
        "residual": residual,
        "absolute_error": abs(residual),
    }


def run_random_forest(frame: pd.DataFrame, *, max_blocks: int | None = None) -> dict:
    started = time.perf_counter()
    origins = frame["timestamp"].to_numpy(dtype="datetime64[ns]")
    origin_ns = frame["timestamp"].astype("int64").to_numpy()
    features = frame[RF_FEATURES].to_numpy(dtype=float)
    target = frame["y"].to_numpy(dtype=float)
    splits = frame["split"].to_numpy()

    def evaluate(config: dict, split_name: str) -> pd.DataFrame:
        rows: list[dict] = []
        eval_origins = frame.loc[frame["split"] == split_name, "timestamp"]
        for block_start in _blocks(eval_origins, max_blocks):
            block_ns = np.int64(pd.Timestamp(block_start).value)
            next_ns = np.int64((pd.Timestamp(block_start) + pd.Timedelta(days=1)).value)
            train_end = int(np.searchsorted(origin_ns, block_ns, side="left"))
            block_end = int(np.searchsorted(origin_ns, next_ns, side="left"))
            if train_end < 50 or block_end <= train_end:
                continue
            model = RandomForestRegressor(
                random_state=RANDOM_STATE,
                n_jobs=-1,
                bootstrap=True,
                **config,
            )
            model.fit(features[:train_end], target[:train_end])
            predicted = model.predict(features[train_end:block_end])
            for offset, y_pred in enumerate(predicted):
                position = train_end + offset
                if splits[position] != split_name:
                    continue
                rows.append(
                    _prediction_row(
                        "Random_Forest",
                        split_name,
                        pd.Timestamp(origins[position]),
                        float(target[position]),
                        float(y_pred),
                    )
                )
        if not rows:
            raise RuntimeError(f"Random Forest não gerou previsões em {split_name}.")
        return pd.DataFrame(rows)

    tuning_rows = []
    validation_by_config: list[pd.DataFrame] = []
    for config_id, config in enumerate(RF_GRID):
        config_started = time.perf_counter()
        predictions = evaluate(config, "validacao_interna")
        tuning_rows.append(
            {
                "config_id": config_id,
                "parameters": json.dumps(config, sort_keys=True),
                "MAE_validation": float(predictions["absolute_error"].mean()),
                "n_predictions": int(len(predictions)),
                "seconds": round(time.perf_counter() - config_started, 1),
            }
        )
        validation_by_config.append(predictions)
        print(
            f"  RF config {config_id}: MAE={tuning_rows[-1]['MAE_validation']:.4f} "
            f"({tuning_rows[-1]['n_predictions']} previsões, {tuning_rows[-1]['seconds']}s)",
            flush=True,
        )

    best_id = int(min(range(len(tuning_rows)), key=lambda i: tuning_rows[i]["MAE_validation"]))
    test_predictions = evaluate(RF_GRID[best_id], "test_final")
    elapsed = time.perf_counter() - started
    return {
        "model": "Random_Forest",
        "config": RF_GRID[best_id],
        "features": RF_FEATURES,
        "tuning": pd.DataFrame(tuning_rows).sort_values("MAE_validation"),
        "validation_predictions": validation_by_config[best_id],
        "test_predictions": test_predictions,
        "seconds": elapsed,
    }


def _fit_sarimax(y: np.ndarray, exog: np.ndarray, config: dict):
    model = SARIMAX(
        y,
        exog=exog,
        order=tuple(config["order"]),
        seasonal_order=tuple(config["seasonal_order"]),
        trend=config["trend"],
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    return model.fit(disp=False, maxiter=SARIMAX_MAXITER, method="lbfgs")


def run_sarimax(
    scored_origins: pd.DataFrame,
    exog: pd.DataFrame,
    pm: pd.Series,
    *,
    max_blocks: int | None = None,
) -> dict:
    started = time.perf_counter()
    observed = pm.notna()
    filled = pm.ffill(limit=24)
    origin_set = {
        split: set(pd.DatetimeIndex(scored_origins.loc[scored_origins["split"] == split, "timestamp"]))
        for split in ("validacao_interna", "test_final")
    }

    def evaluate(config: dict, split_name: str) -> pd.DataFrame:
        rows: list[dict] = []
        failures = 0
        origins = scored_origins.loc[scored_origins["split"] == split_name, "timestamp"]
        allowed = origin_set[split_name]
        for block_start in _blocks(origins, max_blocks):
            day_origins = origins[(origins >= block_start) & (origins < block_start + pd.Timedelta(days=1))]
            if day_origins.empty:
                continue
            first_origin = pd.Timestamp(day_origins.iloc[0])
            history = filled.loc[:first_origin]
            if history.isna().any():
                last_missing = history[history.isna()].index.max()
                history = history.loc[history.index > last_missing]
            history = history.iloc[-WINDOW_HOURS:]
            if len(history) < 24 * 7:
                failures += 1
                continue
            hist_exog = exog.loc[history.index].to_numpy(dtype=float)
            center = hist_exog.mean(axis=0)
            scale = hist_exog.std(axis=0)
            scale[scale == 0] = 1.0
            hist_exog = (hist_exog - center) / scale
            try:
                state = _fit_sarimax(history.to_numpy(dtype=float), hist_exog, config)
            except Exception:
                failures += 1
                continue
            known_through = history.index[-1]
            last_value = float(history.iloc[-1])
            for origin in day_origins:
                origin = pd.Timestamp(origin)
                while known_through < origin:
                    known_through = known_through + pd.Timedelta(hours=1)
                    if known_through not in filled.index:
                        break
                    value = filled.at[known_through]
                    if pd.isna(value):
                        value = last_value
                    row = ((exog.loc[known_through].to_numpy(dtype=float) - center) / scale).reshape(1, -1)
                    state = state.append(np.asarray([float(value)]), exog=row, refit=False)
                    last_value = float(value)
                target_time = origin + pd.Timedelta(hours=1)
                if target_time not in exog.index:
                    continue
                future = ((exog.loc[target_time].to_numpy(dtype=float) - center) / scale).reshape(1, -1)
                try:
                    forecast = float(np.asarray(state.forecast(steps=1, exog=future), dtype=float).reshape(-1)[0])
                except Exception:
                    failures += 1
                    forecast = last_value
                if origin in allowed and bool(observed.get(target_time, False)):
                    rows.append(
                        _prediction_row(
                            "SARIMAX",
                            split_name,
                            origin,
                            float(pm.at[target_time]),
                            forecast,
                        )
                    )
        if not rows:
            raise RuntimeError(f"SARIMAX não gerou previsões em {split_name} ({failures} blocos falharam).")
        predictions = pd.DataFrame(rows)
        predictions.attrs["failures"] = failures
        return predictions

    tuning_rows = []
    validation_by_config: list[pd.DataFrame] = []
    for config_id, config in enumerate(SARIMAX_GRID):
        config_started = time.perf_counter()
        predictions = evaluate(config, "validacao_interna")
        tuning_rows.append(
            {
                "config_id": config_id,
                "parameters": json.dumps(config),
                "MAE_validation": float(predictions["absolute_error"].mean()),
                "n_predictions": int(len(predictions)),
                "block_failures": int(predictions.attrs.get("failures", 0)),
                "seconds": round(time.perf_counter() - config_started, 1),
            }
        )
        validation_by_config.append(predictions)
        print(
            f"  SARIMAX config {config_id}: MAE={tuning_rows[-1]['MAE_validation']:.4f} "
            f"({tuning_rows[-1]['n_predictions']} previsões, {tuning_rows[-1]['seconds']}s)",
            flush=True,
        )

    best_id = int(min(range(len(tuning_rows)), key=lambda i: tuning_rows[i]["MAE_validation"]))
    test_predictions = evaluate(SARIMAX_GRID[best_id], "test_final")
    return {
        "model": "SARIMAX",
        "config": SARIMAX_GRID[best_id],
        "exog": SARIMAX_EXOG,
        "tuning": pd.DataFrame(tuning_rows).sort_values("MAE_validation"),
        "validation_predictions": validation_by_config[best_id],
        "test_predictions": test_predictions,
        "seconds": time.perf_counter() - started,
    }


def save_model_result(root: Path, result: dict, train_rows: int, test_rows_available: int) -> None:
    model_dir = root / "analyses" / "grupo3" / "02_modelos" / result["model"] / "results"
    model_dir.mkdir(parents=True, exist_ok=True)
    test_predictions = result["test_predictions"]
    test_predictions.to_csv(model_dir / "walkforward_predictions.csv", index=False)
    result["tuning"].to_csv(model_dir / "tuning_results.csv", index=False)
    selected = {
        "model": result["model"],
        "selection_split": "validacao_interna",
        "metric": "MAE",
        "protocol": REFIT,
        "config": result["config"],
        "features": result.get("features", result.get("exog")),
    }
    (model_dir / "selected_config.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    metadata = {
        "model": result["model"],
        "config": result["config"],
        "features": result.get("features", result.get("exog")),
        "train_rows_initial": train_rows,
        "test_rows": test_rows_available,
        "stride": 1,
        "refit_every": "calendar_day",
        "horizon": 1,
        "window": "expanding_daily_refit" if result["model"] == "Random_Forest" else f"rolling_{WINDOW_HOURS}h_daily_refit",
        "refit": REFIT,
        "runtime_seconds": round(result["seconds"], 1),
        "mae_test": float(test_predictions["absolute_error"].mean()),
        "n_predictions": int(len(test_predictions)),
    }
    (model_dir / "walkforward_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    residual = {
        "model": result["model"],
        "n_predictions": int(len(test_predictions)),
        "MAE": float(test_predictions["absolute_error"].mean()),
        "mean_error": float(test_predictions["residual"].mean()),
        "residual_std": float(test_predictions["residual"].std()),
        "residual_min": float(test_predictions["residual"].min()),
        "residual_max": float(test_predictions["residual"].max()),
    }
    pd.DataFrame([residual]).to_csv(model_dir / "residual_summary.csv", index=False)
    checkpoint = model_dir / "tuning_checkpoint.csv"
    if checkpoint.exists():
        checkpoint.unlink()


def write_comparison(root: Path) -> None:
    models_dir = root / "analyses" / "grupo3" / "02_modelos"
    results_dir = root / "analyses" / "grupo3" / "03_resultados" / "outputs"
    results_dir.mkdir(parents=True, exist_ok=True)
    model_names = ["Holt_Winters", "PLS_Regression", "Random_Forest", "SARIMAX"]
    frames = []
    mae_rows = []
    accuracy_rows = []
    ljung_rows = []
    for model_name in model_names:
        path = models_dir / model_name / "results" / "walkforward_predictions.csv"
        if not path.exists():
            continue
        predictions = pd.read_csv(path, parse_dates=["forecast_origin", "target_date"])
        predictions["model"] = model_name
        frames.append(predictions)
        metadata_path = models_dir / model_name / "results" / "walkforward_metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
        mae_rows.append(
            {
                "model": model_name,
                "MAE_test": round(float(predictions["absolute_error"].mean()), 4),
                "n_predictions": int(len(predictions)),
                "stride": metadata.get("stride", 1),
                "config": json.dumps(metadata.get("config", {}), sort_keys=True),
            }
        )
        y_true = predictions["y_true"].to_numpy(dtype=float)
        y_pred = predictions["y_pred"].to_numpy(dtype=float)
        residual = y_true - y_pred
        denominator = np.where(y_true == 0, 1e-10, y_true)
        accuracy_rows.append(
            {
                "model": model_name,
                "MAE": round(float(np.mean(np.abs(residual))), 4),
                "RMSE": round(float(np.sqrt(np.mean(residual**2))), 4),
                "MAPE_pct": round(float(np.mean(np.abs(residual / denominator)) * 100), 2),
                "R2": round(float(r2_score(y_true, y_pred)), 4),
                "bias": round(float(np.mean(residual)), 4),
                "n_predictions": int(len(predictions)),
            }
        )
        ljung = acorr_ljungbox(predictions["residual"].dropna(), lags=[10, 24, 48], return_df=True)
        for lag, row in ljung.iterrows():
            ljung_rows.append(
                {
                    "model": model_name,
                    "lag": int(lag),
                    "lb_stat": float(row["lb_stat"]),
                    "lb_pvalue": float(row["lb_pvalue"]),
                    "n_residuals": int(predictions["residual"].notna().sum()),
                }
            )

    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(results_dir / "combined_predictions.csv", index=False)
    mae_table = pd.DataFrame(mae_rows).sort_values("MAE_test")
    mae_table.to_csv(results_dir / "mae_consolidado.csv", index=False)
    summary = (
        combined.groupby("model")["absolute_error"]
        .agg(["mean", "std", "median", "min", "max", "count"])
        .reset_index()
    )
    summary.columns = ["model", "MAE_mean", "MAE_std", "MAE_median", "MAE_min", "MAE_max", "n_predictions"]
    summary = summary.sort_values("MAE_mean")
    summary.to_csv(results_dir / "comparison_summary.csv", index=False)
    pd.DataFrame(accuracy_rows).sort_values("MAE").to_csv(results_dir / "accuracy_metrics.csv", index=False)
    pd.DataFrame(ljung_rows).to_csv(results_dir / "ljung_box_results.csv", index=False)

    shared = None
    for model_name, predictions in zip(
        [item["model"] for item in mae_rows],
        frames,
        strict=True,
    ):
        origins = set(pd.to_datetime(predictions["forecast_origin"]))
        shared = origins if shared is None else shared & origins
    if shared:
        fair_rows = []
        for model_name, predictions in zip([item["model"] for item in mae_rows], frames, strict=True):
            subset = predictions[pd.to_datetime(predictions["forecast_origin"]).isin(shared)]
            fair_rows.append(
                {
                    "model": model_name,
                    "MAE_same_origins": float(subset["absolute_error"].mean()) if len(subset) else None,
                    "n_shared_origins": int(len(subset)),
                }
            )
        pd.DataFrame(fair_rows).sort_values("MAE_same_origins").to_csv(
            results_dir / "mae_mesmas_origens.csv",
            index=False,
        )
