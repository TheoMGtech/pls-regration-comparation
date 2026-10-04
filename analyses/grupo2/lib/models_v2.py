"""Protocolo experimental reforçado da Base 2.

Diferenças centrais em relação à primeira versão:
- previsão estritamente uma hora à frente;
- um novo ajuste em cada origem selecionada;
- mesmas origens para os quatro modelos;
- tuning walk-forward apenas dentro dos 80% de desenvolvimento;
- teste final de 20% intocado até o congelamento dos parâmetros;
- avaliação somente sobre alvos realmente observados.
"""

from __future__ import annotations

import json
import hashlib
import platform
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import sklearn
import statsmodels
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

import config

@dataclass
class ForecastResult:
    model_name: str
    params: dict[str, Any]
    predictions: pd.DataFrame
    mae: float
    runtime_sec: float
    ljung_box_pvalue: float
    feature_importance: pd.DataFrame | None = None


def make_origins(
    df: pd.DataFrame,
    start: int,
    end: int,
    step: int,
) -> list[int]:
    """Origens sistemáticas comuns, avaliadas somente quando y é observado."""
    ids = [
        i
        for i in range(start, end, step)
        if i > 0 and int(df.iloc[i]["target_observed"]) == 1
    ]
    if not ids:
        raise ValueError("Nenhuma origem observada foi selecionada.")
    return ids


def protocol_summary(df: pd.DataFrame) -> dict[str, Any]:
    train_end, validation_end = _boundaries(df)
    validation_origins = make_origins(
        df, train_end, validation_end, config.VALIDATION_ORIGIN_STEP
    )
    test_origins = make_origins(
        df, validation_end, len(df), config.TEST_ORIGIN_STEP
    )
    return {
        "protocol_version": 3,
        "random_state": config.RANDOM_STATE,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "statsmodels": statsmodels.__version__,
        },
        "granularity": "1 hora",
        "horizon_hours": config.HORIZON,
        "external_split": "80% desenvolvimento / 20% teste",
        "development_split": "70% treino interno / 10% validação",
        "train_end_index": train_end,
        "validation_end_index": validation_end,
        "n_rows": len(df),
        "validation_origin_step_hours": config.VALIDATION_ORIGIN_STEP,
        "test_origin_step_hours": config.TEST_ORIGIN_STEP,
        "n_validation_origins": len(validation_origins),
        "n_test_origins": len(test_origins),
        "residual_diagnostic_hours": 168,
        "validation_origins": validation_origins,
        "test_origins": test_origins,
        "window_policy": {
            "Random_Forest": config.ML_MAX_TRAIN,
            "PLS_Regression": config.ML_MAX_TRAIN,
            "Holt_Winters_candidates": sorted(
                {candidate["max_train_rows"] for candidate in config.HW_CANDIDATES}
            ),
            "SARIMAX": config.SARIMAX_MAX_TRAIN,
        },
        "pls_feature_sets": config.PLS_FEATURE_SETS,
        "refit_policy": "reajuste em toda origem; previsão exclusiva de 1 hora",
        "evaluation_policy": "MAE somente em traffic_volume originalmente observado",
        "selection_metric": "menor MAE walk-forward na validação",
        "numerical_safeguard": (
            "Holt-Winters não convergido ou fora do intervalo causal plausível "
            "usa sazonal 168h"
        ),
        "checkpoint_policy": (
            "assinatura de protocolo impede reaproveitar tuning incompatível"
        ),
    }


def _boundaries(df: pd.DataFrame) -> tuple[int, int]:
    validation_end = int(len(df) * config.TRAIN_RATIO)
    train_end = int(validation_end * config.INNER_TRAIN_RATIO)
    return train_end, validation_end


def _window(df: pd.DataFrame, end: int, max_rows: int) -> pd.DataFrame:
    start = max(0, end - max_rows)
    return df.iloc[start:end]


def _clean_params(params: dict[str, Any]) -> dict[str, Any]:
    ignored = {
        "validation_mae",
        "mean_seconds_per_origin",
        "elapsed_seconds",
        "aic",
        "bic",
        "status",
        "protocol_signature",
        "feature_set",
    }
    return {k: v for k, v in params.items() if k not in ignored}


def _predict_ml(
    df: pd.DataFrame,
    origin: int,
    model_name: str,
    params: dict[str, Any],
) -> tuple[float, Any, StandardScaler | None]:
    hist = _window(df, origin, config.ML_MAX_TRAIN)
    # Alvos imputados ajudam os modelos temporais, mas não entram no treino ML.
    hist = hist.loc[hist["target_observed"] == 1]
    feature_set = str(params.get("feature_set", "full"))
    feature_columns = (
        config.PLS_FEATURE_SETS[feature_set]
        if model_name == "PLS_Regression"
        else config.FEATURE_COLS
    )
    X_train = hist[feature_columns]
    y_train = hist[config.TARGET]
    X_origin = df.iloc[[origin]][feature_columns]
    fit_params = _clean_params(params)

    if model_name == "Random_Forest":
        estimator = RandomForestRegressor(
            random_state=config.RANDOM_STATE,
            n_jobs=-1,
            **fit_params,
        ).fit(X_train, y_train)
        return float(estimator.predict(X_origin)[0]), estimator, None

    scaler = StandardScaler().fit(X_train)
    estimator = PLSRegression(
        n_components=int(fit_params["n_components"]),
        scale=False,
    ).fit(scaler.transform(X_train), y_train)
    prediction = float(estimator.predict(scaler.transform(X_origin)).ravel()[0])
    return prediction, estimator, scaler


def _predict_holt_winters(
    df: pd.DataFrame,
    origin: int,
    params: dict[str, Any],
) -> tuple[float, Any, None]:
    fit_params = _clean_params(params)
    max_train_rows = int(
        fit_params.pop("max_train_rows", config.HW_MAX_TRAIN)
    )
    hist = _window(df, origin, max_train_rows)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        fitted = ExponentialSmoothing(
            hist[config.TARGET].astype(float),
            trend=fit_params["trend"],
            seasonal=fit_params["seasonal"],
            seasonal_periods=int(fit_params["seasonal_periods"]),
            damped_trend=bool(fit_params["damped_trend"]),
            initialization_method="estimated",
        ).fit(optimized=True)
    fitted._forecast_converged = not any(
        issubclass(item.category, ConvergenceWarning) for item in caught
    )
    prediction = float(np.asarray(fitted.forecast(1))[0])

    # Alguns ajustes convergem numericamente, mas extrapolam para valores
    # fisicamente absurdos. O limite usa somente o histórico disponível na
    # origem; a alternativa sazonal de 168h também já é conhecida.
    historical_max = float(hist[config.TARGET].max())
    fallback_used = bool(
        not fitted._forecast_converged
        or not np.isfinite(prediction)
        or prediction < 0
        or prediction > historical_max * 1.5
    )
    if fallback_used:
        prediction = float(df.iloc[origin]["y_lag_168"])
    fitted._forecast_fallback_used = fallback_used
    return prediction, fitted, None


def _predict_sarimax(
    df: pd.DataFrame,
    origin: int,
    params: dict[str, Any],
) -> tuple[float, Any, None]:
    hist = _window(df, origin, config.SARIMAX_MAX_TRAIN)
    future = df.iloc[[origin]]
    fit_params = _clean_params(params)
    exog_scaler = StandardScaler().fit(
        hist[config.SARIMAX_EXOG].astype(float)
    )
    exog_train = exog_scaler.transform(
        hist[config.SARIMAX_EXOG].astype(float)
    )
    exog_future = exog_scaler.transform(
        future[config.SARIMAX_EXOG].astype(float)
    )
    fitted = SARIMAX(
        hist[config.TARGET].astype(float),
        exog=exog_train,
        order=tuple(fit_params["order"]),
        seasonal_order=tuple(fit_params["seasonal_order"]),
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False, maxiter=100)
    prediction = fitted.get_forecast(
        steps=1,
        exog=exog_future,
    ).predicted_mean
    return float(np.asarray(prediction)[0]), fitted, None


def _predict_one(
    df: pd.DataFrame,
    origin: int,
    model_name: str,
    params: dict[str, Any],
) -> tuple[float, Any, StandardScaler | None]:
    if model_name in {"Random_Forest", "PLS_Regression"}:
        return _predict_ml(df, origin, model_name, params)
    if model_name == "Holt_Winters":
        return _predict_holt_winters(df, origin, params)
    if model_name == "SARIMAX":
        return _predict_sarimax(df, origin, params)
    raise ValueError(f"Modelo desconhecido: {model_name}")


def evaluate(
    df: pd.DataFrame,
    origins: list[int],
    model_name: str,
    params: dict[str, Any],
    progress_every: int = 10,
) -> ForecastResult:
    """Walk-forward real: refit e previsão de um passo em cada origem."""
    started = time.perf_counter()
    records: list[dict[str, Any]] = []
    importance_rows: list[pd.Series] = []

    for number, origin in enumerate(origins, start=1):
        origin_started = time.perf_counter()
        prediction, fitted, _ = _predict_one(df, origin, model_name, params)
        elapsed = time.perf_counter() - origin_started
        actual = float(df.iloc[origin][config.TARGET])
        previous_date = pd.Timestamp(df.iloc[origin - 1][config.DATETIME_COL])
        target_date = pd.Timestamp(df.iloc[origin][config.DATETIME_COL])
        records.append(
            {
                "origin_index": origin,
                "forecast_origin": previous_date,
                "target_date": target_date,
                "horizon_hours": 1,
                "y_true": actual,
                "y_pred": prediction,
                "residual": actual - prediction,
                "elapsed_seconds": elapsed,
                "target_observed": True,
                "fallback_used": bool(
                    getattr(fitted, "_forecast_fallback_used", False)
                ),
                "converged": bool(
                    getattr(
                        fitted,
                        "_forecast_converged",
                        getattr(fitted, "mle_retvals", {}).get(
                            "converged", True
                        ),
                    )
                ),
            }
        )
        if model_name == "Random_Forest":
            importance_rows.append(
                pd.Series(fitted.feature_importances_, index=config.FEATURE_COLS)
            )
        if number % progress_every == 0 or number == len(origins):
            running_mae = float(
                np.mean([abs(r["residual"]) for r in records])
            )
            print(
                f"{model_name}: {number}/{len(origins)} origens | "
                f"MAE parcial={running_mae:.3f}"
            )

    predictions = pd.DataFrame(records)
    residuals = predictions["residual"]
    if len(residuals) >= 5:
        lag = max(1, min(24, len(residuals) // 4))
        lb = acorr_ljungbox(residuals, lags=[lag], return_df=True)
        ljung_box_pvalue = float(lb["lb_pvalue"].iloc[0])
    else:
        # Smoke tests e execuções interrompidas podem ter poucas origens.
        ljung_box_pvalue = float("nan")
    feature_importance = None
    if importance_rows:
        feature_importance = (
            pd.concat(importance_rows, axis=1)
            .mean(axis=1)
            .sort_values(ascending=False)
            .rename("importance")
            .reset_index()
            .rename(columns={"index": "feature"})
        )
    return ForecastResult(
        model_name=model_name,
        params=params,
        predictions=predictions,
        mae=float(mean_absolute_error(predictions["y_true"], predictions["y_pred"])),
        runtime_sec=time.perf_counter() - started,
        ljung_box_pvalue=ljung_box_pvalue,
        feature_importance=feature_importance,
    )


def baseline_predictions(df: pd.DataFrame, origins: list[int]) -> pd.DataFrame:
    rows = []
    for origin in origins:
        actual = float(df.iloc[origin][config.TARGET])
        for baseline, column in (
            ("Persistencia_1h", "y_lag_1"),
            ("Sazonal_24h", "y_lag_24"),
            ("Sazonal_168h", "y_lag_168"),
        ):
            prediction = float(df.iloc[origin][column])
            rows.append(
                {
                    "baseline": baseline,
                    "origin_index": origin,
                    "target_date": df.iloc[origin][config.DATETIME_COL],
                    "y_true": actual,
                    "y_pred": prediction,
                    "absolute_error": abs(actual - prediction),
                }
            )
    return pd.DataFrame(rows)


def _rank_candidates(
    rows: list[dict[str, Any]],
    tie_columns: list[str],
) -> pd.DataFrame:
    ranking = pd.DataFrame(rows)
    ranking["mae_3"] = ranking["validation_mae"].round(3)
    return ranking.sort_values(
        ["mae_3", *tie_columns, "mean_seconds_per_origin"],
        na_position="last",
    ).reset_index(drop=True)


def _checkpoint_signature(
    df: pd.DataFrame,
    origins: list[int],
    model_name: str,
    candidates: list[dict[str, Any]],
) -> str:
    """Identifica o protocolo para não reutilizar checkpoints incompatíveis."""
    payload = {
        "checkpoint_version": 4,
        "model": model_name,
        "n_rows": len(df),
        "first_timestamp": str(df.iloc[0][config.DATETIME_COL]),
        "last_timestamp": str(df.iloc[-1][config.DATETIME_COL]),
        "origins": [int(value) for value in origins],
        "features": config.FEATURE_COLS,
        "pls_feature_sets": config.PLS_FEATURE_SETS,
        "sarimax_exog": config.SARIMAX_EXOG,
        "windows": {
            "ml": config.ML_MAX_TRAIN,
            "hw": config.HW_MAX_TRAIN,
            "sarimax": config.SARIMAX_MAX_TRAIN,
        },
        "sarimax_maxiter": 100,
        "sarimax_exog_scaling": "standardized_within_each_training_window",
        "holt_winters_guard": (
            "fallback_168h_on_nonconvergence_nonfinite_negative_or_1.5x_history"
        ),
        "candidates": candidates,
    }
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def _evaluate_candidates(
    df: pd.DataFrame,
    origins: list[int],
    model_name: str,
    candidates: list[dict[str, Any]],
    ranking_path: Path | None = None,
    tie_key: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], pd.DataFrame]:
    signature = _checkpoint_signature(df, origins, model_name, candidates)
    rows: list[dict[str, Any]] = []
    if ranking_path and ranking_path.exists():
        existing = pd.read_csv(ranking_path)
        if "protocol_signature" in existing.columns:
            existing = existing.loc[
                existing["protocol_signature"].astype(str) == signature
            ]
            rows = existing.to_dict("records")
    completed = {str(row["parameters"]) for row in rows}

    for index, params in enumerate(candidates, start=1):
        key = json.dumps(params, sort_keys=True)
        if key in completed:
            continue
        print(f"\n{model_name} candidato {index}/{len(candidates)}: {params}")
        try:
            result = evaluate(df, origins, model_name, params, progress_every=20)
            row = {
                "model": model_name,
                "parameters": key,
                "validation_mae": result.mae,
                "mean_seconds_per_origin": (
                    result.runtime_sec / len(result.predictions)
                ),
                "elapsed_seconds": result.runtime_sec,
                "convergence_rate": float(
                    result.predictions["converged"].mean()
                ),
                "status": "ok",
                "protocol_signature": signature,
            }
            if tie_key:
                row.update(tie_key(params))
        except Exception as exc:
            row = {
                "model": model_name,
                "parameters": key,
                "validation_mae": np.nan,
                "mean_seconds_per_origin": np.nan,
                "elapsed_seconds": np.nan,
                "convergence_rate": np.nan,
                "status": f"failed: {type(exc).__name__}: {exc}",
                "protocol_signature": signature,
            }
            if tie_key:
                row.update(tie_key(params))
        rows.append(row)
        if ranking_path:
            ranking_path.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(rows).to_csv(ranking_path, index=False)

    tie_columns = list(tie_key(candidates[0]).keys()) if tie_key else []
    ranking = _rank_candidates(rows, tie_columns)
    valid = ranking.loc[ranking["status"] == "ok"]
    if model_name in {"SARIMAX", "Holt_Winters"}:
        converged = valid.loc[valid["convergence_rate"] >= 0.95]
        if not converged.empty:
            valid = converged
    if valid.empty:
        raise RuntimeError(f"Nenhum candidato {model_name} concluiu.")
    winner = json.loads(valid.iloc[0]["parameters"])
    if ranking_path:
        ranking.to_csv(ranking_path, index=False)
    return winner, ranking


def tune_random_forest(
    df: pd.DataFrame,
    ranking_path: Path | None = None,
) -> tuple[dict[str, Any], pd.DataFrame]:
    train_end, validation_end = _boundaries(df)
    origins = make_origins(
        df, train_end, validation_end, config.VALIDATION_ORIGIN_STEP
    )
    return _evaluate_candidates(
        df,
        origins,
        "Random_Forest",
        config.RF_CANDIDATES,
        ranking_path,
        tie_key=lambda p: {
            "depth_complexity": np.inf if p["max_depth"] is None else p["max_depth"],
            "tree_complexity": p["n_estimators"],
        },
    )


def tune_pls(
    df: pd.DataFrame,
    ranking_path: Path | None = None,
) -> tuple[dict[str, Any], pd.DataFrame]:
    train_end, validation_end = _boundaries(df)
    origins = make_origins(
        df, train_end, validation_end, config.VALIDATION_ORIGIN_STEP
    )
    candidates = [
        {"feature_set": feature_set, "n_components": n}
        for feature_set, columns in config.PLS_FEATURE_SETS.items()
        for n in config.PLS_COMPONENTS_GRID
        if n <= len(columns)
    ]
    return _evaluate_candidates(
        df,
        origins,
        "PLS_Regression",
        candidates,
        ranking_path,
        tie_key=lambda p: {
            "feature_complexity": len(
                config.PLS_FEATURE_SETS[p["feature_set"]]
            ),
            "component_complexity": p["n_components"],
        },
    )


def tune_holt_winters(
    df: pd.DataFrame,
    ranking_path: Path | None = None,
) -> tuple[dict[str, Any], pd.DataFrame]:
    train_end, validation_end = _boundaries(df)
    origins = make_origins(
        df, train_end, validation_end, config.VALIDATION_ORIGIN_STEP
    )
    return _evaluate_candidates(
        df,
        origins,
        "Holt_Winters",
        config.HW_CANDIDATES,
        ranking_path,
        tie_key=lambda p: {
            "component_complexity": (
                int(p["trend"] is not None)
                + int(p["seasonal"] is not None)
                + int(p["damped_trend"])
            ),
            "period_complexity": p["seasonal_periods"],
            "window_complexity": p["max_train_rows"],
        },
    )


def _screen_sarimax(df: pd.DataFrame, path: Path | None) -> pd.DataFrame:
    train_end, _ = _boundaries(df)
    hist = _window(df, train_end, config.SARIMAX_MAX_TRAIN)
    exog_scaler = StandardScaler().fit(
        hist[config.SARIMAX_EXOG].astype(float)
    )
    exog_train = exog_scaler.transform(
        hist[config.SARIMAX_EXOG].astype(float)
    )
    specs = [
        {"order": order, "seasonal_order": seasonal}
        for order in config.SARIMAX_REGULAR_ORDERS
        for seasonal in config.SARIMAX_SEASONAL_ORDERS
    ]
    signature = _checkpoint_signature(
        df, [train_end], "SARIMAX_BIC", specs
    )
    rows: list[dict[str, Any]] = []
    if path and path.exists():
        existing = pd.read_csv(path)
        if "protocol_signature" in existing.columns:
            existing = existing.loc[
                existing["protocol_signature"].astype(str) == signature
            ]
            rows = existing.to_dict("records")
    completed = {str(row["parameters"]) for row in rows}
    for number, params in enumerate(specs, start=1):
        key = json.dumps(params, sort_keys=True)
        if key in completed:
            continue
        print(f"SARIMAX BIC {number}/{len(specs)}: {params}")
        try:
            fitted = SARIMAX(
                hist[config.TARGET].astype(float),
                exog=exog_train,
                order=tuple(params["order"]),
                seasonal_order=tuple(params["seasonal_order"]),
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False, maxiter=100)
            row = {
                "parameters": key,
                "aic": float(fitted.aic),
                "bic": float(fitted.bic),
                "converged": bool(fitted.mle_retvals.get("converged", True)),
                "status": "ok",
                "protocol_signature": signature,
            }
        except Exception as exc:
            row = {
                "parameters": key,
                "aic": np.nan,
                "bic": np.nan,
                "converged": False,
                "status": f"failed: {type(exc).__name__}: {exc}",
                "protocol_signature": signature,
            }
        rows.append(row)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(rows).to_csv(path, index=False)
    screening = pd.DataFrame(rows).sort_values(["bic", "aic"], na_position="last")
    if path:
        screening.to_csv(path, index=False)
    return screening


def tune_sarimax(
    df: pd.DataFrame,
    screening_path: Path | None = None,
    ranking_path: Path | None = None,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    screening = _screen_sarimax(df, screening_path)
    candidates = [
        json.loads(value)
        for value in screening.loc[
            (screening["status"] == "ok")
            & screening["converged"].astype(str).str.lower().eq("true"),
            "parameters",
        ]
        .head(config.SARIMAX_SCREEN_TOP_N)
        .tolist()
    ]
    if not candidates:
        raise RuntimeError("Nenhuma estrutura SARIMAX convergiu na triagem BIC.")
    train_end, validation_end = _boundaries(df)
    origins = make_origins(
        df, train_end, validation_end, config.SARIMAX_VALIDATION_ORIGIN_STEP
    )
    winner, ranking = _evaluate_candidates(
        df,
        origins,
        "SARIMAX",
        candidates,
        ranking_path,
        tie_key=lambda p: {
            "order_complexity": sum(p["order"]) + sum(p["seasonal_order"][:3]),
            "max_order": max([*p["order"], *p["seasonal_order"][:3]]),
        },
    )
    return winner, ranking, screening


def final_origins(df: pd.DataFrame) -> list[int]:
    _, validation_end = _boundaries(df)
    return make_origins(
        df, validation_end, len(df), config.TEST_ORIGIN_STEP
    )


def validation_origins(df: pd.DataFrame) -> list[int]:
    train_end, validation_end = _boundaries(df)
    return make_origins(
        df, train_end, validation_end, config.VALIDATION_ORIGIN_STEP
    )


def residual_diagnostic_origins(
    df: pd.DataFrame,
    length: int = 168,
) -> list[int]:
    """Seleciona uma faixa horária consecutiva observada dentro do teste."""
    _, test_start = _boundaries(df)
    run: list[int] = []
    for origin in range(test_start, len(df)):
        if int(df.iloc[origin]["target_observed"]) == 1:
            run.append(origin)
            if len(run) == length:
                return run
        else:
            run = []
    raise ValueError(
        f"Teste não contém {length} alvos observados consecutivos."
    )


def pls_importance(
    df: pd.DataFrame,
    params: dict[str, Any],
    origins: list[int],
) -> pd.DataFrame:
    """Coeficiente, VIP e permutação em ajuste pós-seleção auditável."""
    development_end = origins[0]
    development = _window(df, development_end, config.ML_MAX_TRAIN)
    development = development.loc[development["target_observed"] == 1]
    sample = df.iloc[origins]
    feature_set = str(params.get("feature_set", "full"))
    feature_columns = config.PLS_FEATURE_SETS[feature_set]
    scaler = StandardScaler().fit(development[feature_columns])
    X_train = scaler.transform(development[feature_columns])
    X_test = scaler.transform(sample[feature_columns])
    estimator = PLSRegression(
        n_components=int(params["n_components"]), scale=False
    ).fit(X_train, development[config.TARGET])
    coefficient = estimator.coef_.ravel()
    weights = estimator.x_weights_
    weights = weights / np.sqrt((weights**2).sum(axis=0, keepdims=True))
    explained = (
        np.diag(estimator.x_scores_.T @ estimator.x_scores_)
        * estimator.y_loadings_.ravel() ** 2
    )
    vip = np.sqrt(
        len(feature_columns) * ((weights**2) @ explained) / explained.sum()
    )
    permutation = permutation_importance(
        estimator,
        X_test,
        sample[config.TARGET],
        n_repeats=10,
        random_state=config.RANDOM_STATE,
        n_jobs=-1,
        scoring="neg_mean_absolute_error",
    )
    return pd.DataFrame(
        {
            "feature": feature_columns,
            "absolute_standardized_coefficient": np.abs(coefficient),
            "standardized_coefficient": coefficient,
            "vip_score": vip,
            "permutation_mean": permutation.importances_mean,
            "permutation_std": permutation.importances_std,
        }
    ).sort_values("permutation_mean", ascending=False)


def save_result(result: ForecastResult, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    result.predictions.to_csv(
        out_dir / f"predictions_{result.model_name}.csv", index=False
    )
    y_true = result.predictions["y_true"].astype(float)
    y_pred = result.predictions["y_pred"].astype(float)
    residuals = y_true - y_pred
    absolute_errors = residuals.abs()
    available_lags = [
        lag for lag in (1, 6, 12, 24) if lag < len(residuals)
    ]
    ljung_box = (
        acorr_ljungbox(residuals, lags=available_lags, return_df=True)
        if available_lags
        else pd.DataFrame(columns=["lb_stat", "lb_pvalue"])
    )
    meta = {
        "model": result.model_name,
        "params": result.params,
        "n_forecasts": len(result.predictions),
        "mae": result.mae,
        "rmse": float(np.sqrt(np.mean(residuals**2))),
        "median_absolute_error": float(absolute_errors.median()),
        "wape_percent": float(
            100 * absolute_errors.sum() / y_true.abs().sum()
        ),
        "bias": float(residuals.mean()),
        "r2": float(r2_score(y_true, y_pred)),
        "residual_acf_lag1": float(residuals.autocorr(lag=1)),
        "runtime_sec": result.runtime_sec,
        "mean_seconds_per_origin": result.runtime_sec / len(result.predictions),
        "ljung_box_pvalue_lag24": result.ljung_box_pvalue,
        "ljung_box_pvalue_sampled_sequence_lag24": result.ljung_box_pvalue,
        "ljung_box_pvalues": {
            str(lag): float(ljung_box.loc[lag, "lb_pvalue"])
            for lag in available_lags
        },
        "fallback_count": int(
            result.predictions.get(
                "fallback_used",
                pd.Series(False, index=result.predictions.index),
            ).sum()
        ),
        "convergence_rate": float(
            result.predictions.get(
                "converged",
                pd.Series(True, index=result.predictions.index),
            ).mean()
        ),
        "walk_forward": "refit em cada origem; horizonte 1h",
    }
    (out_dir / f"metrics_{result.model_name}.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    if result.feature_importance is not None:
        result.feature_importance.to_csv(
            out_dir / f"feature_importance_{result.model_name}.csv",
            index=False,
        )
