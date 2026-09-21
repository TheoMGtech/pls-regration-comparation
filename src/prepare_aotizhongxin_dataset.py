"""Prepare the Aotizhongxin hourly air-quality forecasting dataset.

Target: PM2.5 one hour ahead.
External variables are used with a one-hour lag (or longer), so every value
used at forecast origin t was observed no later than t-1.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "bases" / "grupo3" / "PRSA_Data_Aotizhongxin_20130301-20170228.csv"
OUT = ROOT / "bases" / "processed" / "aotizhongxin_hourly_modeling.csv"

EXTERNALS = ["PM10", "SO2", "NO2", "CO", "O3", "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
TARGET = "PM2.5"


def build_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Build the hourly timestamp and enforce the source calendar.
    df["DATETIME"] = pd.to_datetime(
        dict(year=df["year"], month=df["month"], day=df["day"], hour=df["hour"])
    )
    df = df.sort_values("DATETIME").reset_index(drop=True)

    # The source is already hourly and complete; assert this instead of silently repairing it.
    expected = pd.date_range(df["DATETIME"].min(), df["DATETIME"].max(), freq="h")
    if not df["DATETIME"].equals(expected.to_series().reset_index(drop=True)):
        raise ValueError("Aotizhongxin source is not a complete regular hourly calendar")
    if df["DATETIME"].duplicated().any():
        raise ValueError("Duplicate timestamps found in Aotizhongxin source")

    # Observed exogenous variables may have gaps. Forward fill only: no future value is used.
    # Leading missing values remain missing and are handled inside each model's training pipeline.
    for col in EXTERNALS:
        df[col] = df[col].ffill()

    # Wind direction is categorical. Convert it to a direction angle and then to cyclic features.
    wind_degrees = {
        "N": 0.0, "NNE": 22.5, "NE": 45.0, "ENE": 67.5,
        "E": 90.0, "ESE": 112.5, "SE": 135.0, "SSE": 157.5,
        "S": 180.0, "SSW": 202.5, "SW": 225.0, "WSW": 247.5,
        "W": 270.0, "WNW": 292.5, "NW": 315.0, "NNW": 337.5,
    }
    wind = df["wd"].map(wind_degrees).ffill()
    df["WIND_DIR_SIN_LAG1"] = np.sin(np.deg2rad(wind.shift(1)))
    df["WIND_DIR_COS_LAG1"] = np.cos(np.deg2rad(wind.shift(1)))

    # Calendar variables are known in advance and therefore do not leak future target values.
    df["HOUR_SIN"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["HOUR_COS"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["DOW_SIN"] = np.sin(2 * np.pi * df["DATETIME"].dt.dayofweek / 7)
    df["DOW_COS"] = np.cos(2 * np.pi * df["DATETIME"].dt.dayofweek / 7)
    df["MONTH_SIN"] = np.sin(2 * np.pi * (df["month"] - 1) / 12)
    df["MONTH_COS"] = np.cos(2 * np.pi * (df["month"] - 1) / 12)

    # Target is one hour ahead. Never impute PM2.5.
    df["TARGET"] = df[TARGET].shift(-1)

    # Target history. All lags are strictly in the past relative to the forecast origin.
    for lag in [1, 3, 6, 24, 168]:
        df[f"PM25_LAG_{lag}"] = df[TARGET].shift(lag)

    # Rolling statistics end at t-1, never at t or t+1.
    prior_target = df[TARGET].shift(1)
    for window in [3, 6, 24, 168]:
        df[f"PM25_ROLLING_MEAN_{window}"] = prior_target.rolling(window, min_periods=window).mean()
        df[f"PM25_ROLLING_STD_{window}"] = prior_target.rolling(window, min_periods=window).std()

    # External variables: lagged so their availability is unambiguous at origin t.
    for col in EXTERNALS:
        for lag in [1, 24]:
            df[f"{col}_LAG_{lag}"] = df[col].shift(lag)

    # Keep only the modeling contract. Raw identifiers are retained as audit metadata.
    feature_cols = [
        "PM25_LAG_1", "PM25_LAG_3", "PM25_LAG_6", "PM25_LAG_24", "PM25_LAG_168",
        "PM25_ROLLING_MEAN_3", "PM25_ROLLING_STD_3",
        "PM25_ROLLING_MEAN_6", "PM25_ROLLING_STD_6",
        "PM25_ROLLING_MEAN_24", "PM25_ROLLING_STD_24",
        "PM25_ROLLING_MEAN_168", "PM25_ROLLING_STD_168",
        "HOUR_SIN", "HOUR_COS", "DOW_SIN", "DOW_COS", "MONTH_SIN", "MONTH_COS",
        "WIND_DIR_SIN_LAG1", "WIND_DIR_COS_LAG1",
    ]
    for col in EXTERNALS:
        feature_cols.extend([f"{col}_LAG_1", f"{col}_LAG_24"])

    out = df[["DATETIME", TARGET, "TARGET", *feature_cols]].copy()
    out = out.dropna(subset=["TARGET"]).reset_index(drop=True)
    return out


def main() -> None:
    raw = pd.read_csv(RAW)
    out = build_dataset(raw)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"source_rows={len(raw)}")
    print(f"model_rows={len(out)}")
    print(f"date_start={out['DATETIME'].min()}")
    print(f"date_end={out['DATETIME'].max()}")
    print(f"target_missing={out['TARGET'].isna().sum()}")
    print(f"output={OUT}")


if __name__ == "__main__":
    main()
