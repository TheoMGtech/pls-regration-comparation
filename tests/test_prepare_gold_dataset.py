from pathlib import Path
import sys

import pandas as pd

TREATMENT_DIR = Path(__file__).resolve().parents[1] / "bases" / "grupo5-tratamento"
sys.path.insert(0, str(TREATMENT_DIR))

from prepare_gold_dataset import FEATURE_COLUMNS, build_dataset


def test_build_dataset_uses_only_prior_gold_and_preserves_calendar(tmp_path: Path) -> None:
    dates = pd.date_range("2024-01-01", periods=30, freq="B")
    pd.DataFrame({"DATE": dates, "VALUE": range(100, 130), "TARGET_UP": 0}).to_csv(
        tmp_path / "gold_daily_prices.csv", index=False, sep=";"
    )
    pd.DataFrame({"observation_date": dates[::2], "DGS10": 4.0}).to_csv(tmp_path / "dgs10.csv", index=False)
    pd.DataFrame({"observation_date": dates, "DFF": 5.0}).to_csv(tmp_path / "dff.csv", index=False)

    dataset, report = build_dataset(tmp_path)

    assert list(dataset.columns) == FEATURE_COLUMNS
    assert len(dataset) == 9  # 20 lag rows and the final TARGET row are unusable.
    assert dataset["DATE"].is_monotonic_increasing
    assert dataset["DATE"].isin(dates).all()
    first = dataset.iloc[0]
    assert first["GOLD_LAG_1"] == 119
    assert first["GOLD_ROLLING_MEAN_5"] == sum(range(115, 120)) / 5
    assert first["TARGET"] == 121
    assert report["rows_removed"] == 21
    assert report["no_known_data_leakage"] is True
