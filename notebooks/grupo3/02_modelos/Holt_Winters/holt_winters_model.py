"""Implementação específica do Holt-Winters univariado."""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

DEFAULT_GRID = {
    "trend": ["add", None],
    "seasonal": ["add", None],
    "damped_trend": [False, True],
    "seasonal_periods": [24],
}


def valid_holt_winters_grid():
    """Return only semantically valid configurations for the search."""
    from itertools import product

    configurations = []
    for values in product(*DEFAULT_GRID.values()):
        config = dict(zip(DEFAULT_GRID, values))
        if config["damped_trend"] and config["trend"] is None:
            continue
        configurations.append(config)
    return configurations


def fit_holt_winters(y, *, trend="add", seasonal="add", damped_trend=False, seasonal_periods=24, use_brute=False):
    if seasonal is None and damped_trend and trend is None:
        raise ValueError("damped_trend exige uma tendência.")
    if seasonal is not None and seasonal_periods is None:
        raise ValueError("seasonal_periods é obrigatório com sazonalidade.")
    values = np.asarray(y, dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Holt-Winters não aceita NaN no alvo de treino.")
    model = ExponentialSmoothing(
        values,
        trend=trend,
        seasonal=seasonal,
        damped_trend=damped_trend if trend is not None else False,
        seasonal_periods=seasonal_periods if seasonal is not None else None,
        initialization_method="estimated",
    )
    return model.fit(optimized=True, use_brute=use_brute)


def build_continuous_series(features, value_col="target_pm25_observed"):
    """Reindexa para grade horária contínua e preenche lacunas com ffill limit=24."""
    ts = features.set_index("timestamp")[value_col].sort_index()
    full_range = pd.date_range(ts.index.min(), ts.index.max(), freq="h")
    ts = ts.reindex(full_range)
    ts.name = value_col
    ts = ts.ffill(limit=24)
    return ts


def forecast_holt_winters(y, horizon=1, **config):
    fitted = fit_holt_winters(y, **config)
    return np.asarray(fitted.forecast(horizon), dtype=float)
