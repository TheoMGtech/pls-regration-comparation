"""Protocolo final da Base 3.

Os quatro modelos preveem o PM2.5 da hora seguinte nas mesmas origens.
A matriz tabular é única para Random Forest e PLS: medições conhecidas na
origem t, calendário de t+1, sem a meteorologia duplicada de Guanyuan.
Holt-Winters é reestimado em cada origem. Os outros três reestimam os
parâmetros uma vez por dia e, dentro do dia, usam só o que já foi observado.
"""
from __future__ import annotations

import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import r2_score
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")

TRAIN_END = pd.Timestamp("2015-09-25 06:00:00")
VAL_END = pd.Timestamp("2016-05-16 04:00:00")
TEST_START = pd.Timestamp("2016-05-16 05:00:00")
RANDOM_STATE = 42
HW_WINDOW = 24 * 21
SARIMAX_WINDOW = 24 * 14
SARIMAX_MAXITER = 20

FEATURES = [
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
    {"n_estimators": 40, "max_depth": 12, "min_samples_leaf": 5, "min_samples_split": 2, "max_features": "sqrt"},
    {"n_estimators": 80, "max_depth": 12, "min_samples_leaf": 5, "min_samples_split": 2, "max_features": "sqrt"},
    {"n_estimators": 40, "max_depth": 8, "min_samples_leaf": 5, "min_samples_split": 2, "max_features": "sqrt"},
    {"n_estimators": 40, "max_depth": 16, "min_samples_leaf": 2, "min_samples_split": 2, "max_features": "sqrt"},
    {"n_estimators": 40, "max_depth": 12, "min_samples_leaf": 5, "min_samples_split": 10, "max_features": "sqrt"},
    {"n_estimators": 40, "max_depth": 12, "min_samples_leaf": 5, "min_samples_split": 2, "max_features": 0.5},
]
PLS_GRID = [{"n_components": n} for n in (2, 4, 8, 12, 14, 16)]
HW_GRID = [
    {"trend": "add", "seasonal": "add", "damped_trend": False},
    {"trend": "add", "seasonal": "add", "damped_trend": True},
    {"trend": "add", "seasonal": None, "damped_trend": False},
    {"trend": None, "seasonal": "add", "damped_trend": False},
    {"trend": None, "seasonal": None, "damped_trend": False},
]
SARIMAX_CANDIDATES = [
    {"order": (1, 0, 1), "seasonal_order": (0, 0, 0, 0), "trend": "n"},
    {"order": (0, 1, 1), "seasonal_order": (0, 0, 0, 0), "trend": "n"},
    {"order": (1, 1, 1), "seasonal_order": (0, 0, 0, 0), "trend": "n"},
    {"order": (1, 0, 1), "seasonal_order": (1, 0, 0, 24), "trend": "n"},
    {"order": (0, 1, 1), "seasonal_order": (0, 1, 1, 24), "trend": "n"},
]


def repository_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / "bases" / "grupo3").exists():
            return candidate
    raise FileNotFoundError("Raiz do repositório não encontrada.")


def _calendar(index: pd.DatetimeIndex) -> pd.DataFrame:
    hour = index.hour.to_numpy()
    dow = index.dayofweek.to_numpy()
    return pd.DataFrame(
        {
            "target_hour_sin": np.sin(2 * np.pi * hour / 24),
            "target_hour_cos": np.cos(2 * np.pi * hour / 24),
            "target_dow_sin": np.sin(2 * np.pi * dow / 7),
            "target_dow_cos": np.cos(2 * np.pi * dow / 7),
        },
        index=index,
    )


def load_frame(root: Path) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Matriz compartilhada. Medições de t entram na previsão de t+1."""
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
    pm = prepared["target_pm25"].astype(float)
    target_time = pd.DatetimeIndex(pm.index + pd.Timedelta(hours=1))
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
    frame = frame.join(_calendar(target_time).set_index(pm.index))
    frame = frame.dropna(subset=FEATURES + ["y"]).reset_index(names="timestamp")
    frame["target_timestamp"] = frame["timestamp"] + pd.Timedelta(hours=1)
    frame["split"] = np.where(
        frame["timestamp"] <= TRAIN_END,
        "train_interno",
        np.where(frame["timestamp"] <= VAL_END, "validacao_interna", "test_final"),
    )
    exog = _calendar(pd.DatetimeIndex(pm.index)).rename(
        columns={
            "target_hour_sin": "hour_sin",
            "target_hour_cos": "hour_cos",
            "target_dow_sin": "dow_sin",
            "target_dow_cos": "dow_cos",
        }
    )
    exog["pm10_lag1"] = prepared["local_PM10"].shift(1)
    exog["temp_lag1"] = prepared["local_TEMP"].shift(1)
    exog["wspm_lag1"] = prepared["local_WSPM"].shift(1)
    exog["changping_pm25_lag1"] = prepared["Changping_PM2.5"].shift(1)
    exog = exog.ffill().fillna(0.0)
    return frame, pm, exog


def _prediction(model: str, split: str, origin: pd.Timestamp, y_true: float, y_pred: float) -> dict:
    y_pred = float(max(0.0, y_pred))
    if not np.isfinite(y_pred):
        y_pred = float("nan")
    residual = float(y_true) - y_pred
    return {
        "model": model,
        "split": split,
        "forecast_origin": pd.Timestamp(origin),
        "target_date": pd.Timestamp(origin) + pd.Timedelta(hours=1),
        "horizon": 1,
        "y_true": float(y_true),
        "y_pred": y_pred,
        "residual": residual,
        "absolute_error": abs(residual),
    }


def _blocks(origins: pd.Series) -> list[pd.Timestamp]:
    return list(pd.Series(origins).dt.floor("D").drop_duplicates().sort_values())


def run_tabular(frame: pd.DataFrame, model_name: str, grid: list[dict], fit_predict_block) -> dict:
    started = time.perf_counter()
    origin_ns = frame["timestamp"].astype("int64").to_numpy()
    origins = frame["timestamp"].to_numpy(dtype="datetime64[ns]")
    features = frame[FEATURES].to_numpy(dtype=float)
    target = frame["y"].to_numpy(dtype=float)
    splits = frame["split"].to_numpy()

    def evaluate(config: dict, split_name: str) -> pd.DataFrame:
        rows: list[dict] = []
        eval_origins = frame.loc[frame["split"] == split_name, "timestamp"]
        for block_start in _blocks(eval_origins):
            block_ns = np.int64(pd.Timestamp(block_start).value)
            next_ns = np.int64((pd.Timestamp(block_start) + pd.Timedelta(days=1)).value)
            train_end = int(np.searchsorted(origin_ns, block_ns, side="left"))
            block_end = int(np.searchsorted(origin_ns, next_ns, side="left"))
            positions = [i for i in range(train_end, block_end) if splits[i] == split_name]
            if train_end < 50 or not positions:
                continue
            predicted = fit_predict_block(config, features[:train_end], target[:train_end], features[positions])
            for position, y_pred in zip(positions, predicted):
                rows.append(
                    _prediction(
                        model_name,
                        split_name,
                        pd.Timestamp(origins[position]),
                        float(target[position]),
                        float(y_pred),
                    )
                )
        if not rows:
            raise RuntimeError(f"{model_name} não gerou previsões em {split_name}.")
        return pd.DataFrame(rows)

    tuning_rows = []
    validations = []
    for config_id, config in enumerate(grid):
        tick = time.perf_counter()
        predictions = evaluate(config, "validacao_interna")
        tuning_rows.append(
            {
                "config_id": config_id,
                "parameters": json.dumps(config, sort_keys=True),
                "MAE_validation": float(predictions["absolute_error"].mean()),
                "n_predictions": int(len(predictions)),
                "seconds": round(time.perf_counter() - tick, 1),
            }
        )
        validations.append(predictions)
        print(
            f"  {model_name} config {config_id}: MAE={tuning_rows[-1]['MAE_validation']:.4f} "
            f"({tuning_rows[-1]['n_predictions']} previsões, {tuning_rows[-1]['seconds']}s)",
            flush=True,
        )
    best_id = int(min(range(len(tuning_rows)), key=lambda i: tuning_rows[i]["MAE_validation"]))
    test_predictions = evaluate(grid[best_id], "test_final")
    return {
        "model": model_name,
        "config": grid[best_id],
        "features": FEATURES,
        "tuning": pd.DataFrame(tuning_rows).sort_values("MAE_validation"),
        "test_predictions": test_predictions,
        "seconds": time.perf_counter() - started,
    }


def _rf_block(config, x_train, y_train, x_future):
    model = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, bootstrap=True, **config)
    model.fit(x_train, y_train)
    return model.predict(x_future)


def _pls_block(config, x_train, y_train, x_future):
    model = PLSRegression(scale=True, max_iter=500, **config)
    model.fit(x_train, y_train)
    return np.asarray(model.predict(x_future)).reshape(-1)


def run_random_forest(frame: pd.DataFrame) -> dict:
    print("Random Forest", flush=True)
    return run_tabular(frame, "Random_Forest", RF_GRID, _rf_block)


def run_pls(frame: pd.DataFrame) -> dict:
    print("PLS Regression", flush=True)
    return run_tabular(frame, "PLS_Regression", PLS_GRID, _pls_block)


def _hw_one(window: np.ndarray, config: dict) -> float:
    kwargs = {
        "trend": config["trend"],
        "seasonal": config["seasonal"],
        "initialization_method": "estimated",
    }
    if config["seasonal"] is not None:
        kwargs["seasonal_periods"] = 24
    if config["trend"] is not None:
        kwargs["damped_trend"] = config["damped_trend"]
    fitted = ExponentialSmoothing(window, **kwargs).fit(optimized=True, use_brute=False)
    return float(np.asarray(fitted.forecast(1)).reshape(-1)[0])


def run_holt_winters(frame: pd.DataFrame, pm: pd.Series) -> dict:
    print("Holt-Winters", flush=True)
    started = time.perf_counter()
    filled = pm.ffill(limit=24)
    lookup = frame.set_index("timestamp")["y"]

    def evaluate(config: dict, split_name: str) -> tuple[pd.DataFrame, int]:
        rows = []
        failures = 0
        origins = frame.loc[frame["split"] == split_name, "timestamp"]
        for done, origin in enumerate(origins, start=1):
            origin = pd.Timestamp(origin)
            window = filled.loc[origin - pd.Timedelta(hours=HW_WINDOW) : origin]
            if window.isna().any():
                last_missing = window[window.isna()].index.max()
                window = window.loc[window.index > last_missing]
            y_true = float(lookup.loc[origin])
            fallback = float(filled.loc[origin])
            if len(window) < 48 or window.index[-1] != origin:
                failures += 1
                forecast = fallback
            else:
                try:
                    forecast = _hw_one(window.to_numpy(dtype=float), config)
                    if not np.isfinite(forecast):
                        raise ValueError("previsão não finita")
                except Exception:
                    failures += 1
                    forecast = fallback
            rows.append(_prediction("Holt_Winters", split_name, origin, y_true, forecast))
            if done % 1000 == 0:
                print(f"    Holt-Winters {split_name}: {done}/{len(origins)}", flush=True)
        return pd.DataFrame(rows), failures

    tuning_rows = []
    for config_id, config in enumerate(HW_GRID):
        tick = time.perf_counter()
        predictions, failures = evaluate(config, "validacao_interna")
        tuning_rows.append(
            {
                "config_id": config_id,
                "parameters": json.dumps(config, sort_keys=True),
                "MAE_validation": float(predictions["absolute_error"].mean()),
                "n_predictions": int(len(predictions)),
                "fallbacks": int(failures),
                "seconds": round(time.perf_counter() - tick, 1),
            }
        )
        print(
            f"  Holt_Winters config {config_id}: MAE={tuning_rows[-1]['MAE_validation']:.4f} "
            f"({tuning_rows[-1]['seconds']}s, fallbacks={failures})",
            flush=True,
        )
    best_id = int(min(range(len(tuning_rows)), key=lambda i: tuning_rows[i]["MAE_validation"]))
    test_predictions, test_failures = evaluate(HW_GRID[best_id], "test_final")
    return {
        "model": "Holt_Winters",
        "config": HW_GRID[best_id],
        "features": [],
        "tuning": pd.DataFrame(tuning_rows).sort_values("MAE_validation"),
        "test_predictions": test_predictions,
        "seconds": time.perf_counter() - started,
        "test_fallbacks": test_failures,
    }


def _fit_sarimax(y, exog, config: dict):
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


def sarimax_information_criteria(pm: pd.Series, exog: pd.DataFrame) -> pd.DataFrame:
    """AIC e BIC numa janela do treino, inclusive ordens sazonais."""
    end = TRAIN_END
    history = pm.ffill(limit=24).loc[:end].dropna()
    history = history.iloc[-SARIMAX_WINDOW:]
    raw = exog.loc[history.index].to_numpy(dtype=float)
    center = raw.mean(axis=0)
    scale = raw.std(axis=0)
    scale[scale == 0] = 1.0
    raw = (raw - center) / scale
    rows = []
    for config in SARIMAX_CANDIDATES:
        tick = time.perf_counter()
        try:
            fitted = _fit_sarimax(history.to_numpy(dtype=float), raw, config)
            rows.append(
                {
                    "order": str(config["order"]),
                    "seasonal_order": str(config["seasonal_order"]),
                    "aic": float(fitted.aic),
                    "bic": float(fitted.bic),
                    "converged": True,
                    "seconds": round(time.perf_counter() - tick, 2),
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "order": str(config["order"]),
                    "seasonal_order": str(config["seasonal_order"]),
                    "aic": np.nan,
                    "bic": np.nan,
                    "converged": False,
                    "seconds": round(time.perf_counter() - tick, 2),
                    "error": str(exc)[:180],
                }
            )
        print(f"  AIC {config['order']} x {config['seasonal_order']}: {rows[-1].get('aic')}", flush=True)
    return pd.DataFrame(rows).sort_values("aic", na_position="last")


def run_sarimax(frame: pd.DataFrame, pm: pd.Series, exog: pd.DataFrame) -> dict:
    print("SARIMAX", flush=True)
    started = time.perf_counter()
    filled = pm.ffill(limit=24)
    observed = pm.notna()
    lookup = frame.set_index("timestamp")["y"]
    allowed = {
        split: set(pd.DatetimeIndex(frame.loc[frame["split"] == split, "timestamp"]))
        for split in ("validacao_interna", "test_final")
    }

    def evaluate(config: dict, split_name: str) -> tuple[pd.DataFrame, int]:
        rows = []
        failures = 0
        origins = frame.loc[frame["split"] == split_name, "timestamp"]
        for block_start in _blocks(origins):
            day = origins[(origins >= block_start) & (origins < block_start + pd.Timedelta(days=1))]
            if day.empty:
                continue
            first_origin = pd.Timestamp(day.iloc[0])
            history = filled.loc[:first_origin]
            if history.isna().any():
                last_missing = history[history.isna()].index.max()
                history = history.loc[history.index > last_missing]
            history = history.iloc[-SARIMAX_WINDOW:]
            use_model = len(history) >= 24 * 7
            state = None
            center = scale = None
            if use_model:
                hist_exog = exog.loc[history.index].to_numpy(dtype=float)
                center = hist_exog.mean(axis=0)
                scale = hist_exog.std(axis=0)
                scale[scale == 0] = 1.0
                try:
                    state = _fit_sarimax(history.to_numpy(dtype=float), (hist_exog - center) / scale, config)
                except Exception:
                    use_model = False
                    failures += 1
            known_through = history.index[-1] if len(history) else first_origin
            last_value = float(filled.loc[first_origin])
            for origin in day:
                origin = pd.Timestamp(origin)
                while use_model and known_through < origin:
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
                forecast = float(filled.loc[origin])
                if use_model and target_time in exog.index:
                    future = ((exog.loc[target_time].to_numpy(dtype=float) - center) / scale).reshape(1, -1)
                    try:
                        forecast = float(np.asarray(state.forecast(steps=1, exog=future)).reshape(-1)[0])
                    except Exception:
                        failures += 1
                if origin in allowed[split_name] and bool(observed.get(target_time, False)):
                    rows.append(_prediction("SARIMAX", split_name, origin, float(lookup.loc[origin]), forecast))
        return pd.DataFrame(rows), failures

    tuning_rows = []
    for config_id, config in enumerate(SARIMAX_CANDIDATES):
        tick = time.perf_counter()
        predictions, failures = evaluate(config, "validacao_interna")
        tuning_rows.append(
            {
                "config_id": config_id,
                "parameters": json.dumps(config),
                "MAE_validation": float(predictions["absolute_error"].mean()) if len(predictions) else np.inf,
                "n_predictions": int(len(predictions)),
                "fallbacks": int(failures),
                "seconds": round(time.perf_counter() - tick, 1),
            }
        )
        print(
            f"  SARIMAX config {config_id}: MAE={tuning_rows[-1]['MAE_validation']:.4f} "
            f"({tuning_rows[-1]['seconds']}s)",
            flush=True,
        )
    best_id = int(min(range(len(tuning_rows)), key=lambda i: tuning_rows[i]["MAE_validation"]))
    test_predictions, test_failures = evaluate(SARIMAX_CANDIDATES[best_id], "test_final")
    return {
        "model": "SARIMAX",
        "config": SARIMAX_CANDIDATES[best_id],
        "features": ["hour_sin", "hour_cos", "dow_sin", "dow_cos", "pm10_lag1", "temp_lag1", "wspm_lag1", "changping_pm25_lag1"],
        "tuning": pd.DataFrame(tuning_rows).sort_values("MAE_validation"),
        "test_predictions": test_predictions,
        "seconds": time.perf_counter() - started,
        "test_fallbacks": test_failures,
    }


def align_predictions(results: list[dict]) -> list[dict]:
    sets = [set(pd.to_datetime(item["test_predictions"]["forecast_origin"])) for item in results]
    common = set.intersection(*sets)
    if not common:
        raise RuntimeError("Não há origem comum entre os quatro modelos.")
    for item in results:
        predictions = item["test_predictions"]
        predictions = predictions[pd.to_datetime(predictions["forecast_origin"]).isin(common)].sort_values("forecast_origin")
        item["test_predictions"] = predictions.reset_index(drop=True)
    lengths = {item["model"]: len(item["test_predictions"]) for item in results}
    if len(set(lengths.values())) != 1:
        raise RuntimeError(f"Origens divergentes depois do alinhamento: {lengths}")
    return results


def _fit_pls_train(frame: pd.DataFrame, n_components: int) -> PLSRegression:
    train = frame[frame["split"] == "train_interno"]
    model = PLSRegression(n_components=n_components, scale=True, max_iter=500)
    model.fit(train[FEATURES].to_numpy(dtype=float), train["y"].to_numpy(dtype=float))
    return model


def vip_table(frame: pd.DataFrame, n_components: int) -> pd.DataFrame:
    model = _fit_pls_train(frame, n_components)
    weights = np.asarray(model.x_weights_, dtype=float)
    weights = weights / np.linalg.norm(weights, axis=0)
    scores = np.asarray(model.x_scores_, dtype=float)
    loadings = np.asarray(model.y_loadings_, dtype=float).reshape(-1)
    explained = np.sum(scores**2, axis=0) * (loadings**2)
    total = float(np.sum(explained))
    if total <= 0:
        raise RuntimeError("VIP indefinido.")
    vip = np.sqrt(len(FEATURES) * (weights**2 @ explained) / total)
    table = pd.DataFrame({"feature": FEATURES, "vip": vip})
    return table.sort_values("vip", ascending=False).reset_index(drop=True)


def coefficient_table(frame: pd.DataFrame, n_components: int) -> pd.DataFrame:
    """Coeficientes do PLS com preditores padronizados, num único ajuste do treino interno."""
    model = _fit_pls_train(frame, n_components)
    coefficient = np.asarray(model.coef_, dtype=float).reshape(-1)
    table = pd.DataFrame(
        {
            "feature": FEATURES,
            "standardized_coefficient": coefficient,
            "abs_coefficient": np.abs(coefficient),
        }
    )
    return table.sort_values("abs_coefficient", ascending=False).reset_index(drop=True)


def save_result(root: Path, result: dict, train_rows: int, test_rows: int) -> None:
    model_dir = root / "analyses" / "grupo3" / "02_modelos" / result["model"] / "results"
    model_dir.mkdir(parents=True, exist_ok=True)
    predictions = result["test_predictions"]
    predictions.to_csv(model_dir / "walkforward_predictions.csv", index=False)
    result["tuning"].to_csv(model_dir / "tuning_results.csv", index=False)
    selected = {
        "model": result["model"],
        "selection_split": "validacao_interna",
        "metric": "MAE",
        "protocol": "mesmas origens; reajuste diário exceto Holt-Winters, reestimado a cada origem",
        "config": result["config"],
        "features": result.get("features", FEATURES),
    }
    (model_dir / "selected_config.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    metadata = {
        "model": result["model"],
        "config": result["config"],
        "features": result.get("features", []),
        "train_rows_initial": train_rows,
        "test_rows": test_rows,
        "stride": 1,
        "refit_every": "forecast_origin" if result["model"] == "Holt_Winters" else "calendar_day",
        "horizon": 1,
        "window": f"rolling_{HW_WINDOW}h" if result["model"] == "Holt_Winters" else "expanding_daily_refit",
        "runtime_seconds": round(result["seconds"], 1),
        "mae_test": float(predictions["absolute_error"].mean()),
        "n_predictions": int(len(predictions)),
        "test_fallbacks": int(result.get("test_fallbacks", 0)),
    }
    (model_dir / "walkforward_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(
        [
            {
                "model": result["model"],
                "n_predictions": int(len(predictions)),
                "MAE": float(predictions["absolute_error"].mean()),
                "mean_error": float(predictions["residual"].mean()),
                "residual_std": float(predictions["residual"].std()),
                "residual_min": float(predictions["residual"].min()),
                "residual_max": float(predictions["residual"].max()),
            }
        ]
    ).to_csv(model_dir / "residual_summary.csv", index=False)


def residual_diagnostics(root: Path, results: list[dict]) -> pd.DataFrame:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir = root / "analyses" / "grupo3" / "03_resultados" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    ljung_rows = []
    notes = []
    figure, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for axis, result in zip(axes.ravel(), results):
        residual = result["test_predictions"]["residual"].to_numpy(dtype=float)
        plot_acf(residual, lags=48, ax=axis, zero=False)
        axis.set_title(result["model"])
        ljung = acorr_ljungbox(residual, lags=[10, 24, 48], return_df=True)
        for lag, row in ljung.iterrows():
            ljung_rows.append(
                {
                    "model": result["model"],
                    "lag": int(lag),
                    "lb_stat": float(row["lb_stat"]),
                    "lb_pvalue": float(row["lb_pvalue"]),
                    "n_residuals": int(len(residual)),
                }
            )
        bias = float(np.mean(residual))
        direction = "abaixo do observado" if bias > 0 else "acima do observado"
        lag24 = float(ljung.loc[24, "lb_pvalue"])
        dependence = "ainda há autocorrelação nos resíduos" if lag24 < 0.05 else "não há autocorrelação relevante no lag 24"
        notes.append(
            {
                "model": result["model"],
                "bias": round(bias, 3),
                "residual_std": round(float(np.std(residual)), 3),
                "ljung_box_p_lag24": lag24,
                "interpretacao": (
                    f"O erro médio é {bias:.2f} µg/m³, então a previsão fica {direction}. "
                    f"O desvio-padrão do resíduo é {float(np.std(residual)):.2f} µg/m³. "
                    f"No lag 24, {dependence} (p={lag24:.3g})."
                ),
            }
        )
    figure.savefig(output_dir / "acf_residuos.png", dpi=140)
    plt.close(figure)
    ljung_table = pd.DataFrame(ljung_rows)
    ljung_table.to_csv(output_dir / "ljung_box_results.csv", index=False)
    pd.DataFrame(notes).to_csv(output_dir / "residuos_interpretacao.csv", index=False)
    return ljung_table


def write_comparison(root: Path, results: list[dict]) -> None:
    output_dir = root / "analyses" / "grupo3" / "03_resultados" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    mae_rows = []
    accuracy_rows = []
    for result in results:
        predictions = result["test_predictions"].copy()
        predictions["model"] = result["model"]
        frames.append(predictions)
        mae_rows.append(
            {
                "model": result["model"],
                "MAE_test": round(float(predictions["absolute_error"].mean()), 4),
                "n_predictions": int(len(predictions)),
                "stride": 1,
                "config": json.dumps(result["config"], sort_keys=True),
            }
        )
        y_true = predictions["y_true"].to_numpy(dtype=float)
        y_pred = predictions["y_pred"].to_numpy(dtype=float)
        residual = y_true - y_pred
        denominator = np.where(y_true == 0, 1e-10, y_true)
        accuracy_rows.append(
            {
                "model": result["model"],
                "MAE": round(float(np.mean(np.abs(residual))), 4),
                "RMSE": round(float(np.sqrt(np.mean(residual**2))), 4),
                "MAPE_pct": round(float(np.mean(np.abs(residual / denominator)) * 100), 2),
                "R2": round(float(r2_score(y_true, y_pred)), 4),
                "bias": round(float(np.mean(residual)), 4),
                "n_predictions": int(len(predictions)),
            }
        )
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(output_dir / "combined_predictions.csv", index=False)
    pd.DataFrame(mae_rows).sort_values("MAE_test").to_csv(output_dir / "mae_consolidado.csv", index=False)
    summary = (
        combined.groupby("model")["absolute_error"]
        .agg(["mean", "std", "median", "min", "max", "count"])
        .reset_index()
    )
    summary.columns = ["model", "MAE_mean", "MAE_std", "MAE_median", "MAE_min", "MAE_max", "n_predictions"]
    summary.sort_values("MAE_mean").to_csv(output_dir / "comparison_summary.csv", index=False)
    pd.DataFrame(accuracy_rows).sort_values("MAE").to_csv(output_dir / "accuracy_metrics.csv", index=False)
    origins = set(pd.to_datetime(frames[0]["forecast_origin"]))
    fair = pd.DataFrame(
        [
            {
                "model": item["model"],
                "MAE_same_origins": float(item["test_predictions"]["absolute_error"].mean()),
                "n_shared_origins": int(len(item["test_predictions"])),
            }
            for item in results
        ]
    ).sort_values("MAE_same_origins")
    fair.to_csv(output_dir / "mae_mesmas_origens.csv", index=False)
    if len(origins) != int(fair["n_shared_origins"].iloc[0]):
        raise RuntimeError("A tabela de origens comuns não bate com as previsões.")


def write_protocol(root: Path, frame: pd.DataFrame) -> None:
    output_dir = root / "analyses" / "grupo3" / "02_modelos" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    counts = frame["split"].value_counts().to_dict()
    protocol = {
        "dataset": "Base 3 — PRSA Aotizhongxin",
        "features_file": "analyses/grupo3/01_dados/outputs/features_modelagem_base3.csv",
        "target": "y = PM2.5(t+1)",
        "availability": "medições de t inclusive; calendário de t+1; meteorologia de Guanyuan excluída por duplicar a estação local",
        "shared_features": FEATURES,
        "same_test_origins": True,
        "horizon_hours": 1,
        "train_end": str(TRAIN_END),
        "validation_end": str(VAL_END),
        "test_start": str(TEST_START),
        "rows_by_split": {key: int(value) for key, value in counts.items()},
        "holt_winters_refit": "cada origem, janela de 21 dias",
        "other_models_refit": "uma vez por dia; previsão de cada hora usa dados observados até a origem",
        "random_state": RANDOM_STATE,
    }
    (output_dir / "validation_protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
    feature_dir = root / "analyses" / "grupo3" / "01_dados" / "outputs"
    frame.to_csv(feature_dir / "features_modelagem_base3.csv", index=False)
    dictionary = pd.DataFrame(
        [
            {"feature": name, "disponivel_em": "t+1, conhecido antes" if name.startswith("target_") else "origem t"}
            for name in FEATURES
        ]
    )
    dictionary.to_csv(feature_dir / "dicionario_modelagem_base3.csv", index=False)
    manifest = {
        "output_file": "analyses/grupo3/01_dados/outputs/features_modelagem_base3.csv",
        "replaced_for_modeling": "features_base3.csv permanece como matriz exploratória de 671 colunas",
        "why_not_671": "Random Forest e PLS compartilham estas 17 colunas, todas disponíveis na origem",
        "guanyuan_meteo": "excluída porque DEWP, PRES, RAIN e WSPM repetem Aotizhongxin",
        "rows": int(len(frame)),
        "predictor_columns": FEATURES,
    }
    (feature_dir / "manifest_modelagem_base3.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
