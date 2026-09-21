import json
import pytest
from pls_regration.config import load_dataset_contracts

def test_five_frozen_contracts_are_loadable() -> None:
    contracts = load_dataset_contracts("config/datasets.json")
    assert len(contracts) == 5
    assert {contract.owner_area for contract in contracts} == {f"grupo{number}" for number in range(1, 6)}
    assert all(len(contract.external_variables) >= 2 for contract in contracts)

def test_dataset_requires_exactly_five_contracts(tmp_path) -> None:
    path = tmp_path / "datasets.json"
    path.write_text(json.dumps({"datasets": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="exactly five"):
        load_dataset_contracts(path)
