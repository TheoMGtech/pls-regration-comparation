import pandas as pd
import pytest
from pls_regration.results import REQUIRED_RESULT_FILES, validate_result_directory

def test_result_directory_requires_all_standard_outputs(tmp_path) -> None:
    with pytest.raises(ValueError, match="missing result file"):
        validate_result_directory(tmp_path, "gold_daily")

def test_result_directory_accepts_standard_schema(tmp_path) -> None:
    for filename, columns in REQUIRED_RESULT_FILES.items():
        row = {column: "gold_daily" if column == "dataset_id" else 1 for column in columns}
        pd.DataFrame([row]).to_csv(tmp_path / filename, index=False)
    validate_result_directory(tmp_path, "gold_daily")
