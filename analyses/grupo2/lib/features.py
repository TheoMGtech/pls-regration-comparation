"""Feature engineering sem vazamento temporal."""

from __future__ import annotations

import numpy as np
import pandas as pd

import config


def add_calendar_and_lags(df: pd.DataFrame) -> pd.DataFrame:
    """Cria features de calendário, lags e janelas usando apenas passado."""
    out = df.copy()
    dt = pd.to_datetime(out[config.DATETIME_COL])
    out["hour"] = dt.dt.hour
    out["dayofweek"] = dt.dt.dayofweek
    out["month"] = dt.dt.month
    out["is_weekend"] = (out["dayofweek"] >= 5).astype(int)

    out["hour_sin"] = np.sin(2 * np.pi * out["hour"] / 24)
    out["hour_cos"] = np.cos(2 * np.pi * out["hour"] / 24)
    out["dow_sin"] = np.sin(2 * np.pi * out["dayofweek"] / 7)
    out["dow_cos"] = np.cos(2 * np.pi * out["dayofweek"] / 7)
    out["month_sin"] = np.sin(2 * np.pi * out["month"] / 12)
    out["month_cos"] = np.cos(2 * np.pi * out["month"] / 12)

    y = out[config.TARGET]
    for lag in (1, 2, 3, 6, 12, 23, 24, 25, 48, 72, 167, 168, 169, 336):
        out[f"y_lag_{lag}"] = y.shift(lag)

    # Rolling sempre sobre valores já observados (shift 1 antes da janela)
    prior = y.shift(1)
    for window in (6, 24, 168):
        out[f"y_roll_mean_{window}"] = prior.rolling(window).mean()
        out[f"y_roll_std_{window}"] = prior.rolling(window).std()

    # Exógenas climáticas: observação realizada → usa defasagem de 1h
    out["temp_lag_1"] = out["temp"].shift(1)
    out["rain_lag_1"] = out["rain_1h"].shift(1)
    out["snow_lag_1"] = out["snow_1h"].shift(1)
    out["clouds_lag_1"] = out["clouds_all"].shift(1)

    # Informa se os lags principais vieram de uma observação real ou do
    # preenchimento causal. A informação também é conhecida na origem.
    observed = out["target_observed"].astype(float)
    for lag in (1, 24, 168, 336):
        out[f"observed_lag_{lag}"] = observed.shift(lag)

    return out


def modeling_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Remove linhas com NaN gerados por lags/janelas no início da série."""
    cols = [
        config.DATETIME_COL,
        config.TARGET,
        "target_observed",
        *config.FEATURE_COLS,
    ]
    return df[cols].dropna().reset_index(drop=True)
