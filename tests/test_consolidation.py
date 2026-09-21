from pathlib import Path

import pandas as pd

from scripts.consolidate_results import consolidate
from pls_regration.config import load_dataset_contracts
from pls_regration.results import REQUIRED_RESULT_FILES


def test_consolidation_uses_per_base_rank_without_averaging_mae(tmp_path) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "analyses").mkdir()
    (tmp_path / "reports" / "output").mkdir(parents=True)
    source = Path("config/datasets.json").read_text(encoding="utf-8")
    (tmp_path / "config" / "datasets.json").write_text(source, encoding="utf-8")
    for contract in load_dataset_contracts(tmp_path / "config/datasets.json"):
        output = tmp_path / "analyses" / contract.owner_area / "outputs"
        output.mkdir(parents=True)
        for filename, columns in REQUIRED_RESULT_FILES.items():
            rows = [{column: contract.identifier if column == "dataset_id" else 1 for column in columns}]
            if filename == "metrics.csv":
                rows = [
                    {"dataset_id": contract.identifier, "model": "SARIMAX", "mae": 10.0, "rank": 99, "execution_seconds": 1.0},
                    {"dataset_id": contract.identifier, "model": "PLS", "mae": 1.0, "rank": 99, "execution_seconds": 1.0},
                ]
            pd.DataFrame(rows).to_csv(output / filename, index=False)
    summary = consolidate(tmp_path)
    assert summary.loc[summary["model"] == "PLS", "wins"].item() == 5
    assert (tmp_path / "reports" / "output" / "consolidated_mae.csv").is_file()
