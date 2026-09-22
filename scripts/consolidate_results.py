"""Consolidate completed area outputs without re-running individual analyses."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pls_regration.config import load_dataset_contracts
from pls_regration.results import validate_result_directory


def consolidate(root: Path = ROOT) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for contract in load_dataset_contracts(root / "config/datasets.json"):
        output = root / "analyses" / contract.owner_area / "outputs"
        validate_result_directory(output, contract.identifier)
        frames.append(pd.read_csv(output / "metrics.csv"))
    metrics = pd.concat(frames, ignore_index=True)
    metrics["rank"] = metrics.groupby("dataset_id")["mae"].rank(method="min", ascending=True).astype(int)
    summary = metrics.groupby("model", as_index=False).agg(wins=("rank", lambda ranks: int((ranks == 1).sum())), mean_rank=("rank", "mean"))
    summary.to_csv(root / "reports" / "output" / "model_summary.csv", index=False)
    metrics.to_csv(root / "reports" / "output" / "consolidated_mae.csv", index=False)
    return summary


if __name__ == "__main__":
    output = ROOT / "reports" / "output"
    output.mkdir(parents=True, exist_ok=True)
    print(consolidate().to_string(index=False))
