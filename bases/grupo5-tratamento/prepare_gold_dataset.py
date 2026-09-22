"""Build the leakage-safe Gold modelling dataset from versioned raw CSV files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

INVALID_VALUES = [".", "", " ", "NA", "N/A", "null", "None"]
EXTERNAL_COLUMNS = ["TREASURY_10Y", "FED_FUNDS_RATE"]
TREATMENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TREATMENT_DIR.parents[1]
FEATURE_COLUMNS = [
    "DATE", "GOLD_PRICE", "TREASURY_10Y", "FED_FUNDS_RATE", "DAY_OF_WEEK", "MONTH",
    "DOW_SIN", "DOW_COS", "MONTH_SIN", "MONTH_COS", "GOLD_LAG_1", "GOLD_LAG_5",
    "GOLD_LAG_20", "GOLD_ROLLING_MEAN_5", "GOLD_ROLLING_STD_5", "TARGET",
]


def read_series(path: Path, value_column: str, output_column: str) -> pd.DataFrame:
    """Read a raw series, normalising FRED's date header without altering the raw file."""
    frame = pd.read_csv(path, sep=None, engine="python", na_values=INVALID_VALUES)
    frame = frame.rename(columns={"observation_date": "DATE", value_column: output_column})
    required = {"DATE", output_column}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {sorted(missing)}")
    frame = frame[["DATE", output_column]].copy()
    frame["DATE"] = pd.to_datetime(frame["DATE"], errors="coerce")
    frame[output_column] = pd.to_numeric(frame[output_column], errors="coerce")
    if frame["DATE"].isna().any():
        raise ValueError(f"{path} contains an invalid DATE")
    if frame["DATE"].duplicated().any():
        raise ValueError(f"{path} contains duplicate DATE values")
    return frame.sort_values("DATE").reset_index(drop=True)


def summary(frame: pd.DataFrame) -> dict[str, object]:
    return {
        "records": len(frame),
        "start": frame["DATE"].min().date().isoformat(),
        "end": frame["DATE"].max().date().isoformat(),
        "duplicates": int(frame["DATE"].duplicated().sum()),
        "missing": {column: int(count) for column, count in frame.isna().sum().items()},
    }


def build_dataset(raw_dir: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    gold = read_series(raw_dir / "gold_daily_prices.csv", "VALUE", "GOLD_PRICE")
    dgs10 = read_series(raw_dir / "dgs10.csv", "DGS10", "TREASURY_10Y")
    dff = read_series(raw_dir / "dff.csv", "DFF", "FED_FUNDS_RATE")
    raw_summary = {"gold": summary(gold), "dgs10": summary(dgs10), "dff": summary(dff)}

    merged = gold.merge(dgs10, on="DATE", how="left", validate="one_to_one")
    merged = merged.merge(dff, on="DATE", how="left", validate="one_to_one")
    assert len(merged) == len(gold), "left merge must preserve the gold calendar"
    assert merged["DATE"].equals(gold["DATE"]), "left merge changed the gold calendar"
    missing_after_merge = {column: int(merged[column].isna().sum()) for column in EXTERNAL_COLUMNS}

    # `ffill` covers market-calendar gaps only.  The subsequent one-observation lag is
    # conservative: the raw FRED observations do not carry an intraday availability time.
    merged[EXTERNAL_COLUMNS] = merged[EXTERNAL_COLUMNS].ffill()
    missing_after_ffill = {column: int(merged[column].isna().sum()) for column in EXTERNAL_COLUMNS}
    merged[EXTERNAL_COLUMNS] = merged[EXTERNAL_COLUMNS].shift(1)

    merged["DAY_OF_WEEK"] = merged["DATE"].dt.dayofweek
    merged["MONTH"] = merged["DATE"].dt.month
    merged["DOW_SIN"] = np.sin(2 * np.pi * merged["DAY_OF_WEEK"] / 7)
    merged["DOW_COS"] = np.cos(2 * np.pi * merged["DAY_OF_WEEK"] / 7)
    merged["MONTH_SIN"] = np.sin(2 * np.pi * merged["MONTH"] / 12)
    merged["MONTH_COS"] = np.cos(2 * np.pi * merged["MONTH"] / 12)
    merged["GOLD_LAG_1"] = merged["GOLD_PRICE"].shift(1)
    merged["GOLD_LAG_5"] = merged["GOLD_PRICE"].shift(5)
    merged["GOLD_LAG_20"] = merged["GOLD_PRICE"].shift(20)
    prior_gold = merged["GOLD_PRICE"].shift(1)
    merged["GOLD_ROLLING_MEAN_5"] = prior_gold.rolling(5).mean()
    merged["GOLD_ROLLING_STD_5"] = prior_gold.rolling(5).std()
    merged["TARGET"] = merged["GOLD_PRICE"].shift(-1)

    nan_by_column = {column: int(merged[column].isna().sum()) for column in FEATURE_COLUMNS}
    usable = merged.dropna(subset=FEATURE_COLUMNS).copy()
    assert usable["DATE"].is_monotonic_increasing
    assert not usable["DATE"].duplicated().any()
    assert not usable.isna().any().any(), "final dataset has unexpected NaN values"
    assert usable["DATE"].isin(gold["DATE"]).all()
    assert "TARGET_UP" not in usable.columns and "IS_HOLIDAY" not in usable.columns

    # Validate temporal construction before rows with natural edge NaNs are removed.
    pd.testing.assert_series_equal(merged["GOLD_LAG_1"], merged["GOLD_PRICE"].shift(1), check_names=False)
    pd.testing.assert_series_equal(merged["TARGET"], merged["GOLD_PRICE"].shift(-1), check_names=False)
    pd.testing.assert_series_equal(merged["GOLD_ROLLING_MEAN_5"], prior_gold.rolling(5).mean(), check_names=False)

    report = {
        "raw": raw_summary,
        "records_before": len(merged),
        "missing_after_merge": missing_after_merge,
        "missing_after_ffill": missing_after_ffill,
        "nan_by_column_before_cleaning": nan_by_column,
        "rows_removed": len(merged) - len(usable),
        "records_after": len(usable),
        "period_used": {"start": usable["DATE"].min().date().isoformat(), "end": usable["DATE"].max().date().isoformat()},
        "columns": FEATURE_COLUMNS,
        "no_known_data_leakage": True,
    }
    return usable[FEATURE_COLUMNS], report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=TREATMENT_DIR)
    parser.add_argument(
        "--output", type=Path, default=PROJECT_ROOT / "bases/grupo5/gold_daily_modeling.csv"
    )
    args = parser.parse_args()
    dataset, report = build_dataset(args.raw_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(args.output, index=False, date_format="%Y-%m-%d")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nFirst 5 rows:\n", dataset.head().to_string(index=False))
    print("\nLast 5 rows:\n", dataset.tail().to_string(index=False))


if __name__ == "__main__":
    main()
