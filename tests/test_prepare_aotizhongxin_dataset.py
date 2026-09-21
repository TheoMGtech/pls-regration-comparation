from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from prepare_aotizhongxin_dataset import build_dataset


def test_aotizhongxin_target_and_calendar():
    raw = pd.read_csv(ROOT / "bases/grupo3/PRSA_Data_Aotizhongxin_20130301-20170228.csv")
    out = build_dataset(raw)
    assert out["DATETIME"].is_monotonic_increasing
    assert not out["DATETIME"].duplicated().any()
    assert out["TARGET"].notna().all()
    # For the first retained row, target is exactly the next source PM2.5 observation.
    assert out.loc[0, "TARGET"] == raw.loc[1, "PM2.5"]


def test_aotizhongxin_lag_is_past_only():
    raw = pd.read_csv(ROOT / "bases/grupo3/PRSA_Data_Aotizhongxin_20130301-20170228.csv")
    out = build_dataset(raw)
    # At each row, PM25_LAG_1 is the previous source observation, not current/future.
    assert out.loc[1, "PM25_LAG_1"] == out.loc[0, "PM2.5"]


def test_aotizhongxin_external_variables_are_lagged():
    raw = pd.read_csv(ROOT / "bases/grupo3/PRSA_Data_Aotizhongxin_20130301-20170228.csv")
    out = build_dataset(raw)
    assert out.loc[1, "TEMP_LAG_1"] == raw.loc[0, "TEMP"]
    assert out.loc[1, "PM10_LAG_1"] == raw.loc[0, "PM10"]
