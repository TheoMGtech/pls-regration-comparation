"""Limpeza e regularização horária da Base 2."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from pipelines.grupo2 import config


def ensure_output_dirs() -> None:
    for path in (
        config.OUTPUT_DIR,
        config.DATA_DIR,
        config.FIG_DIR,
        config.MODEL_DIR,
        config.RESULT_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def load_raw(path: Path | None = None) -> pd.DataFrame:
    path = path or config.RAW_PATH
    df = pd.read_csv(path)
    df[config.DATETIME_COL] = pd.to_datetime(df[config.DATETIME_COL])
    return df


def clean_and_regularize(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Deduplica horários, agrega clima/tráfego e reindexa em grade horária completa."""
    df = raw.copy()
    report: dict = {
        "n_raw": int(len(df)),
        "n_unique_timestamps": int(df[config.DATETIME_COL].nunique()),
        "n_duplicate_timestamps": int(df[config.DATETIME_COL].duplicated().sum()),
        "nulls_raw": {c: int(df[c].isna().sum()) for c in df.columns},
    }

    # holiday: string "None" -> 0; feriados nomeados -> 1
    holiday_raw = df["holiday"].astype(str)
    df["is_holiday_row"] = (~holiday_raw.str.strip().isin(["None", "nan", ""])).astype(int)

    agg = (
        df.groupby(config.DATETIME_COL, as_index=False)
        .agg(
            traffic_volume=("traffic_volume", "mean"),
            temp=("temp", "mean"),
            rain_1h=("rain_1h", "mean"),
            snow_1h=("snow_1h", "mean"),
            clouds_all=("clouds_all", "mean"),
            is_holiday=("is_holiday_row", "max"),
            weather_main=("weather_main", lambda s: s.mode().iloc[0] if len(s.mode()) else s.iloc[0]),
        )
        .sort_values(config.DATETIME_COL)
        .reset_index(drop=True)
    )

    full_idx = pd.date_range(
        agg[config.DATETIME_COL].min(),
        agg[config.DATETIME_COL].max(),
        freq=config.FREQ,
    )
    series = agg.set_index(config.DATETIME_COL).reindex(full_idx)
    series.index.name = config.DATETIME_COL

    missing_hours = int(series[config.TARGET].isna().sum())
    # Preenchimento conservador: interpolação linear do alvo em gaps curtos; ffill/bfill residual
    series[config.TARGET] = series[config.TARGET].interpolate(method="time", limit=6)
    series[config.TARGET] = series[config.TARGET].ffill().bfill()

    for col in ["temp", "rain_1h", "snow_1h", "clouds_all"]:
        series[col] = series[col].interpolate(method="time", limit=6).ffill().bfill()

    series["is_holiday"] = series["is_holiday"].fillna(0).astype(int)
    series["weather_main"] = series["weather_main"].ffill().bfill()

    report.update(
        {
            "n_after_dedup": int(len(agg)),
            "n_regular_hours": int(len(series)),
            "missing_hours_before_fill": missing_hours,
            "start": str(series.index.min()),
            "end": str(series.index.max()),
            "target_min": float(series[config.TARGET].min()),
            "target_max": float(series[config.TARGET].max()),
            "target_mean": float(series[config.TARGET].mean()),
        }
    )

    out = series.reset_index()
    return out, report


def chronological_split(df: pd.DataFrame, train_ratio: float = config.TRAIN_RATIO):
    n = len(df)
    cut = int(n * train_ratio)
    train = df.iloc[:cut].copy()
    test = df.iloc[cut:].copy()
    return train, test, cut


def save_frame(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_json(obj: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
