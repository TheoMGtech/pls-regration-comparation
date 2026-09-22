from pathlib import Path
import pytest
from pls_regration.config import load_dataset_contracts
from pls_regration.integrity import assert_frozen_source_integrity

def test_every_frozen_dataset_has_a_valid_time_axis_and_checksum() -> None:
    root = Path.cwd()
    for contract in load_dataset_contracts(root / "config/datasets.json"):
        assert_frozen_source_integrity(contract, root)

def test_checksum_mismatch_is_rejected(tmp_path) -> None:
    source = tmp_path / "tiny.csv"
    source.write_text("date,value\n2020-01-01,1\n", encoding="utf-8")
    contract = next(contract for contract in load_dataset_contracts("config/datasets.json") if contract.owner_area == "grupo2")
    modified = contract.__class__(**{**contract.__dict__, "source": "tiny.csv", "checksum_sha256": "0" * 64, "time_column": "date"})
    with pytest.raises(ValueError, match="checksum"):
        assert_frozen_source_integrity(modified, tmp_path)
