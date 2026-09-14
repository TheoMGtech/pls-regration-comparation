import json

import pytest

from pls_regration.config import load_dataset_contracts


def test_empty_foundation_contract_is_loadable() -> None:
    contracts = load_dataset_contracts("config/datasets.json")
    assert contracts == ()


def test_dataset_requires_two_external_variables(tmp_path) -> None:
    path = tmp_path / "datasets.json"
    path.write_text(
        json.dumps(
            {
                "datasets": [
                    {
                        "id": "sample",
                        "source": "source",
                        "target": {"column": "target", "unit": "unit"},
                        "frequency": "D",
                        "forecast_horizon": 1,
                        "external_variables": [
                            {"name": "calendar", "availability": "known_in_advance", "evidence": "calendar"}
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="at least two"):
        load_dataset_contracts(path)

