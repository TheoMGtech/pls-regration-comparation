"""Shared result-file contracts used by all five independent pipelines."""
from __future__ import annotations
from pathlib import Path
import pandas as pd

REQUIRED_RESULT_FILES = {
    "predictions.csv": {"dataset_id", "model", "forecast_origin", "actual", "prediction", "residual"},
    "metrics.csv": {"dataset_id", "model", "mae", "rank", "execution_seconds"},
    "hyperparameters.csv": {"dataset_id", "model", "parameter", "value"},
    "feature_importance.csv": {"dataset_id", "model", "feature", "method", "importance"},
    "ljung_box.csv": {"dataset_id", "model", "lag", "p_value"},
}

def validate_result_directory(path: str | Path, dataset_id: str) -> None:
    directory = Path(path)
    for filename, required_columns in REQUIRED_RESULT_FILES.items():
        output = directory / filename
        if not output.is_file():
            raise ValueError(f"{dataset_id}: missing result file {filename}")
        frame = pd.read_csv(output)
        missing = required_columns.difference(frame.columns)
        if missing:
            raise ValueError(f"{dataset_id}: {filename} is missing {sorted(missing)}")
        if not frame.empty and set(frame["dataset_id"].dropna()) != {dataset_id}:
            raise ValueError(f"{dataset_id}: {filename} contains another dataset")
