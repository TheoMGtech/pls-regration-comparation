"""Limpeza e regularização horária da Base 2."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import config


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
    # "None" em holiday é uma categoria real, não valor ausente.
    df = pd.read_csv(path, keep_default_na=False)
    df[config.DATETIME_COL] = pd.to_datetime(df[config.DATETIME_COL])
    return df


def clean_and_regularize(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Deduplica e cria grade horária sem usar observações futuras.

    O arquivo tem uma lacuna estrutural de mais de dez meses. O segmento
    anterior à maior lacuna é removido em vez de inventar milhares de alvos.
    Dentro do segmento final, faltas são preenchidas causalmente: mesmo horário
    da semana anterior, mesmo horário do dia anterior e, por fim, último valor.
    Uma flag preserva quais alvos foram realmente observados para que validação
    e teste nunca sejam calculados sobre alvos imputados.
    """
    df = raw.copy()
    report: dict = {
        "n_raw": int(len(df)),
        "n_unique_timestamps": int(df[config.DATETIME_COL].nunique()),
        "n_duplicate_timestamps": int(df[config.DATETIME_COL].duplicated().sum()),
        "nulls_raw": {c: int(df[c].isna().sum()) for c in df.columns},
    }

    # holiday: string "None" -> 0; feriados nomeados -> 1.
    holiday_raw = df["holiday"].astype(str)
    df["is_holiday_row"] = (~holiday_raw.str.strip().isin(["None", "nan", ""])).astype(int)
    holiday_dates = set(
        df.loc[df["is_holiday_row"] == 1, config.DATETIME_COL].dt.normalize()
    )

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
    n_after_dedup = int(len(agg))

    # A maior lacuna (7.387 h na versão congelada) separa dois regimes de
    # cobertura. Manter só o segmento posterior evita uma longa faixa sintética.
    gaps = agg[config.DATETIME_COL].diff().dt.total_seconds().div(3600)
    largest_gap_hours = float(gaps.max())
    segment_start = agg.loc[gaps.idxmax(), config.DATETIME_COL]
    agg = agg.loc[agg[config.DATETIME_COL] >= segment_start].copy()

    full_idx = pd.date_range(
        agg[config.DATETIME_COL].min(),
        agg[config.DATETIME_COL].max(),
        freq=config.FREQ,
    )
    series = agg.set_index(config.DATETIME_COL).reindex(full_idx)
    series.index.name = config.DATETIME_COL

    series["target_observed"] = series[config.TARGET].notna().astype(int)
    missing_hours = int((series["target_observed"] == 0).sum())

    # Somente passado: t-168, t-24 e último valor conhecido.
    for lag in (config.WEEKLY_PERIOD, config.SEASONAL_PERIOD):
        series[config.TARGET] = series[config.TARGET].fillna(
            series[config.TARGET].shift(lag)
        )
    series[config.TARGET] = series[config.TARGET].ffill()

    for col in ["temp", "rain_1h", "snow_1h", "clouds_all"]:
        series[col] = series[col].ffill()

    # Na fonte o nome do feriado aparece apenas à meia-noite. A informação de
    # calendário vale para todas as 24 horas daquele dia e é conhecida antes
    # da previsão.
    series["is_holiday"] = (
        pd.Series(series.index.normalize(), index=series.index)
        .isin(holiday_dates)
        .astype(int)
    )
    series["weather_main"] = series["weather_main"].ffill().fillna("Unknown")

    report.update(
        {
            "n_after_dedup": n_after_dedup,
            "n_observed_in_selected_segment": int(len(agg)),
            "n_regular_hours": int(len(series)),
            "missing_hours_before_fill": missing_hours,
            "largest_gap_hours": largest_gap_hours,
            "segment_policy": "segmento posterior à maior lacuna",
            "target_fill_policy": "lag 168h, lag 24h, forward-fill; somente passado",
            "holiday_policy": "feriado nomeado expandido para todas as horas do dia",
            "n_holiday_dates": int(len(holiday_dates)),
            "n_observed_targets": int(series["target_observed"].sum()),
            "n_imputed_targets": int((series["target_observed"] == 0).sum()),
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


def temporal_boundaries(df: pd.DataFrame) -> tuple[int, int]:
    """Retorna limites treino interno/validação e teste final.

    Total: 70% treino interno, 10% validação, 20% teste final. O contrato
    externo solicitado permanece 80/20.
    """
    validation_end = int(len(df) * config.TRAIN_RATIO)
    train_end = int(validation_end * config.INNER_TRAIN_RATIO)
    return train_end, validation_end


def save_frame(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_json(obj: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
