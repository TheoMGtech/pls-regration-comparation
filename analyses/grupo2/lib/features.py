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
    out["y_lag_1"] = y.shift(1)
    out["y_lag_24"] = y.shift(24)
    out["y_lag_168"] = y.shift(168)

    # Rolling sempre sobre valores já observados (shift 1 antes da janela)
    prior = y.shift(1)
    out["y_roll_mean_24"] = prior.rolling(24, min_periods=12).mean()
    out["y_roll_std_24"] = prior.rolling(24, min_periods=12).std()
    out["y_roll_mean_168"] = prior.rolling(168, min_periods=24).mean()

    # Exógenas climáticas: observação realizada → usa defasagem de 1h
    out["temp_lag_1"] = out["temp"].shift(1)
    out["rain_lag_1"] = out["rain_1h"].shift(1)
    out["snow_lag_1"] = out["snow_1h"].shift(1)
    out["clouds_lag_1"] = out["clouds_all"].shift(1)

    # Alvo de previsão 1 passo à frente (para clareza; modelos usam y em t+h)
    out["target_h1"] = y.shift(-config.HORIZON)

    return out


def modeling_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Remove linhas com NaN gerados por lags/janelas no início da série."""
    cols = [config.DATETIME_COL, config.TARGET, *config.FEATURE_COLS]
    return df[cols].dropna().reset_index(drop=True)
