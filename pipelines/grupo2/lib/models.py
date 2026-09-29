"""Modelos, tuning e walk-forward da Base 2."""

from __future__ import annotations

import json
import time
import warnings
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

from pipelines.grupo2 import config

warnings.filterwarnings("ignore")


@dataclass
class ForecastResult:
    model_name: str
    params: dict[str, Any]
    predictions: pd.DataFrame
    mae: float
    runtime_sec: float
    ljung_box_pvalue: float
    feature_importance: pd.DataFrame | None = None


def _origins(test_index: np.ndarray, refit_every: int) -> list[int]:
    """Índices locais no teste onde o modelo é reajustado."""
    return list(range(0, len(test_index), refit_every))


def tune_random_forest(train: pd.DataFrame) -> dict:
    """Grid search com split interno 80/20 do bloco de treino."""
    cut = int(len(train) * 0.8)
    tr, va = train.iloc[:cut], train.iloc[cut:]
    X_tr, y_tr = tr[config.FEATURE_COLS], tr[config.TARGET]
    X_va, y_va = va[config.FEATURE_COLS], va[config.TARGET]

    best_mae, best_params = np.inf, None
    keys = list(config.RF_PARAM_GRID)
    for values in product(*[config.RF_PARAM_GRID[k] for k in keys]):
        params = dict(zip(keys, values))
        model = RandomForestRegressor(
            random_state=config.RANDOM_STATE,
            n_jobs=-1,
            **params,
        )
        model.fit(X_tr, y_tr)
        pred = model.predict(X_va)
        mae = mean_absolute_error(y_va, pred)
        if mae < best_mae:
            best_mae, best_params = mae, params
    assert best_params is not None
    best_params["validation_mae"] = float(best_mae)
    return best_params


def tune_pls(train: pd.DataFrame) -> dict:
    cut = int(len(train) * 0.8)
    tr, va = train.iloc[:cut], train.iloc[cut:]
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(tr[config.FEATURE_COLS])
    X_va = scaler.transform(va[config.FEATURE_COLS])
    y_tr, y_va = tr[config.TARGET].values, va[config.TARGET].values

    best_mae, best_n = np.inf, 2
    max_n = min(max(config.PLS_COMPONENTS_GRID), X_tr.shape[1])
    for n in range(2, max_n + 1):
        model = PLSRegression(n_components=n, scale=False)
        model.fit(X_tr, y_tr)
        pred = model.predict(X_va).ravel()
        mae = mean_absolute_error(y_va, pred)
        if mae < best_mae:
            best_mae, best_n = mae, n
    return {"n_components": best_n, "scale": True, "validation_mae": float(best_mae)}


def tune_holt_winters(train: pd.DataFrame) -> dict:
    y = train[config.TARGET].astype(float)
    # usa final do treino para acelerar
    y_fit = y.iloc[-config.HW_MAX_TRAIN :] if len(y) > config.HW_MAX_TRAIN else y
    cut = int(len(y_fit) * 0.85)
    y_tr, y_va = y_fit.iloc[:cut], y_fit.iloc[cut:]
    best_mae, best = np.inf, None
    for trend, seasonal, damped in product(
        config.HW_TREND_GRID, config.HW_SEASONAL_GRID, config.HW_DAMPED_GRID
    ):
        if trend is None and damped:
            continue
        try:
            model = ExponentialSmoothing(
                y_tr,
                trend=trend,
                seasonal=seasonal,
                seasonal_periods=config.SEASONAL_PERIOD,
                damped_trend=damped,
                initialization_method="estimated",
            ).fit(optimized=True)
            pred = model.forecast(len(y_va))
            mae = mean_absolute_error(y_va, pred)
            if mae < best_mae:
                best_mae = mae
                best = {
                    "trend": trend,
                    "seasonal": seasonal,
                    "damped_trend": damped,
                    "seasonal_periods": config.SEASONAL_PERIOD,
                    "validation_mae": float(mae),
                }
        except Exception:
            continue
    if best is None:
        best = {
            "trend": "add",
            "seasonal": "add",
            "damped_trend": False,
            "seasonal_periods": config.SEASONAL_PERIOD,
            "validation_mae": None,
        }
    return best


def tune_sarimax(train: pd.DataFrame) -> dict:
    y = train[config.TARGET].astype(float)
    exog = train[config.SARIMAX_EXOG].astype(float)
    y_fit = y.iloc[-config.SARIMAX_MAX_TRAIN :]
    ex_fit = exog.iloc[-config.SARIMAX_MAX_TRAIN :]
    cut = int(len(y_fit) * 0.85)
    y_tr, y_va = y_fit.iloc[:cut], y_fit.iloc[cut:]
    ex_tr, ex_va = ex_fit.iloc[:cut], ex_fit.iloc[cut:]

    best_aic, best = np.inf, None
    for order, seasonal_order in config.SARIMAX_ORDER_GRID:
        try:
            fit = SARIMAX(
                y_tr,
                exog=ex_tr,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False, maxiter=50)
            if fit.aic < best_aic:
                best_aic = fit.aic
                # avalia MAE no holdout interno
                pred = fit.forecast(steps=len(y_va), exog=ex_va)
                mae = mean_absolute_error(y_va, pred)
                best = {
                    "order": order,
                    "seasonal_order": seasonal_order,
                    "aic": float(fit.aic),
                    "bic": float(fit.bic),
                    "validation_mae": float(mae),
                }
        except Exception:
            continue
    if best is None:
        best = {
            "order": (1, 0, 1),
            "seasonal_order": (0, 1, 1, config.SEASONAL_PERIOD),
            "aic": None,
            "bic": None,
            "validation_mae": None,
        }
    return best


def walkforward_ml(
    df: pd.DataFrame,
    train_end: int,
    model_name: str,
    params: dict,
) -> ForecastResult:
    t0 = time.time()
    test = df.iloc[train_end:].reset_index(drop=True)
    preds = []
    importances = []

    model = None
    scaler = None
    last_fit_pos = -10**9

    for i in range(len(test)):
        abs_pos = train_end + i
        if model is None or (i - last_fit_pos) >= config.REFIT_EVERY:
            hist = df.iloc[:abs_pos]
            if config.ML_MAX_TRAIN is not None and len(hist) > config.ML_MAX_TRAIN:
                hist = hist.iloc[-config.ML_MAX_TRAIN :]
            X = hist[config.FEATURE_COLS]
            y = hist[config.TARGET]
            if model_name == "Random_Forest":
                fit_params = {k: v for k, v in params.items() if k != "validation_mae"}
                model = RandomForestRegressor(
                    random_state=config.RANDOM_STATE, n_jobs=-1, **fit_params
                )
                model.fit(X, y)
                importances.append(pd.Series(model.feature_importances_, index=config.FEATURE_COLS))
            else:
                scaler = StandardScaler()
                Xs = scaler.fit_transform(X)
                model = PLSRegression(n_components=params["n_components"], scale=False)
                model.fit(Xs, y)
                coef = np.abs(model.coef_.ravel())
                importances.append(pd.Series(coef, index=config.FEATURE_COLS))
            last_fit_pos = i

        row = test.iloc[[i]][config.FEATURE_COLS]
        if model_name == "Random_Forest":
            yhat = float(model.predict(row)[0])
        else:
            yhat = float(model.predict(scaler.transform(row)).ravel()[0])
        preds.append(
            {
                "date_time": test.iloc[i][config.DATETIME_COL],
                "y_true": float(test.iloc[i][config.TARGET]),
                "y_pred": yhat,
            }
        )

    pred_df = pd.DataFrame(preds)
    resid = pred_df["y_true"] - pred_df["y_pred"]
    lb = acorr_ljungbox(resid, lags=[24], return_df=True)
    fi = None
    if importances:
        fi = pd.concat(importances, axis=1).mean(axis=1).sort_values(ascending=False)
        fi = fi.rename("importance").reset_index().rename(columns={"index": "feature"})

    return ForecastResult(
        model_name=model_name,
        params=params,
        predictions=pred_df,
        mae=float(mean_absolute_error(pred_df["y_true"], pred_df["y_pred"])),
        runtime_sec=time.time() - t0,
        ljung_box_pvalue=float(lb["lb_pvalue"].iloc[0]),
        feature_importance=fi,
    )


def walkforward_holt_winters(df: pd.DataFrame, train_end: int, params: dict) -> ForecastResult:
    t0 = time.time()
    y = df[config.TARGET].astype(float).values
    dates = df[config.DATETIME_COL].values
    preds = []
    remaining = 0
    batch = np.array([])
    batch_offset = 0

    for i in range(train_end, len(df)):
        if remaining <= 0:
            hist = y[:i]
            if len(hist) > config.HW_MAX_TRAIN:
                hist = hist[-config.HW_MAX_TRAIN :]
            fitted = ExponentialSmoothing(
                hist,
                trend=params["trend"],
                seasonal=params["seasonal"],
                seasonal_periods=params["seasonal_periods"],
                damped_trend=params["damped_trend"],
                initialization_method="estimated",
            ).fit(optimized=True)
            steps = min(config.REFIT_EVERY, len(df) - i)
            batch = np.asarray(fitted.forecast(steps), dtype=float)
            remaining = steps
            batch_offset = 0
        yhat = float(batch[batch_offset])
        batch_offset += 1
        remaining -= 1
        preds.append(
            {
                "date_time": dates[i],
                "y_true": float(y[i]),
                "y_pred": yhat,
            }
        )

    pred_df = pd.DataFrame(preds)
    resid = pred_df["y_true"] - pred_df["y_pred"]
    lb = acorr_ljungbox(resid, lags=[24], return_df=True)
    return ForecastResult(
        model_name="Holt_Winters",
        params=params,
        predictions=pred_df,
        mae=float(mean_absolute_error(pred_df["y_true"], pred_df["y_pred"])),
        runtime_sec=time.time() - t0,
        ljung_box_pvalue=float(lb["lb_pvalue"].iloc[0]),
    )


def walkforward_sarimax(df: pd.DataFrame, train_end: int, params: dict) -> ForecastResult:
    t0 = time.time()
    y = df[config.TARGET].astype(float)
    exog = df[config.SARIMAX_EXOG].astype(float)
    preds = []
    model = None
    remaining = 0
    batch = None
    batch_offset = 0

    order = tuple(params["order"])
    seasonal_order = tuple(params["seasonal_order"])

    for i in range(train_end, len(df)):
        if model is None or remaining <= 0:
            y_hist = y.iloc[:i]
            ex_hist = exog.iloc[:i]
            if len(y_hist) > config.SARIMAX_MAX_TRAIN:
                y_hist = y_hist.iloc[-config.SARIMAX_MAX_TRAIN :]
                ex_hist = ex_hist.iloc[-config.SARIMAX_MAX_TRAIN :]
            model = SARIMAX(
                y_hist,
                exog=ex_hist,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False, maxiter=50)
            steps = min(config.REFIT_EVERY, len(df) - i)
            ex_future = exog.iloc[i : i + steps]
            batch = np.asarray(model.forecast(steps=steps, exog=ex_future), dtype=float)
            remaining = steps
            batch_offset = 0

        yhat = float(batch[batch_offset])
        batch_offset += 1
        remaining -= 1
        preds.append(
            {
                "date_time": df.iloc[i][config.DATETIME_COL],
                "y_true": float(y.iloc[i]),
                "y_pred": yhat,
            }
        )

    pred_df = pd.DataFrame(preds)
    resid = pred_df["y_true"] - pred_df["y_pred"]
    lb = acorr_ljungbox(resid, lags=[24], return_df=True)
    return ForecastResult(
        model_name="SARIMAX",
        params=params,
        predictions=pred_df,
        mae=float(mean_absolute_error(pred_df["y_true"], pred_df["y_pred"])),
        runtime_sec=time.time() - t0,
        ljung_box_pvalue=float(lb["lb_pvalue"].iloc[0]),
    )


def permutation_importance_pls(train: pd.DataFrame, params: dict, n_repeats: int = 3) -> pd.DataFrame:
    cut = int(len(train) * 0.8)
    tr, va = train.iloc[:cut], train.iloc[cut:]
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(tr[config.FEATURE_COLS])
    X_va = scaler.transform(va[config.FEATURE_COLS])
    y_tr = tr[config.TARGET].values
    y_va = va[config.TARGET].values
    model = PLSRegression(n_components=params["n_components"], scale=False).fit(X_tr, y_tr)
    baseline = mean_absolute_error(y_va, model.predict(X_va).ravel())

    rng = np.random.default_rng(config.RANDOM_STATE)
    rows = []
    for j, feat in enumerate(config.FEATURE_COLS):
        scores = []
        for _ in range(n_repeats):
            Xp = X_va.copy()
            rng.shuffle(Xp[:, j])
            scores.append(mean_absolute_error(y_va, model.predict(Xp).ravel()) - baseline)
        rows.append({"feature": feat, "importance": float(np.mean(scores))})
    return pd.DataFrame(rows).sort_values("importance", ascending=False)


def save_result(result: ForecastResult, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    result.predictions.to_csv(out_dir / f"predictions_{result.model_name}.csv", index=False)
    meta = {
        "model": result.model_name,
        "params": result.params,
        "mae": result.mae,
        "runtime_sec": result.runtime_sec,
        "ljung_box_pvalue_lag24": result.ljung_box_pvalue,
    }
    (out_dir / f"metrics_{result.model_name}.json").write_text(
        json.dumps(meta, indent=2, default=str), encoding="utf-8"
    )
    if result.feature_importance is not None:
        result.feature_importance.to_csv(
            out_dir / f"feature_importance_{result.model_name}.csv", index=False
        )
