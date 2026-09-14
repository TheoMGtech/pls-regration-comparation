"""Small, model-agnostic safeguards for temporally valid feature frames."""

from __future__ import annotations

import pandas as pd


def assert_features_available_at_origin(
    frame: pd.DataFrame,
    origin_column: str = "forecast_origin",
    availability_column: str = "available_at",
) -> None:
    """Reject feature rows whose value became available after the forecast origin."""
    required = {origin_column, availability_column}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"missing temporal availability columns: {sorted(missing)}")
    origins = pd.to_datetime(frame[origin_column], utc=True)
    available_at = pd.to_datetime(frame[availability_column], utc=True)
    leaked_rows = frame.index[available_at > origins]
    if not leaked_rows.empty:
        raise ValueError(
            "future information detected in feature frame at rows: "
            + ", ".join(map(str, leaked_rows.tolist()))
        )
