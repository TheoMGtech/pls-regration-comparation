"""Small entry point used by every area for independent smoke validation."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .config import load_dataset_contracts
from .integrity import assert_frozen_source_integrity

def validate_area(area: str, root: Path) -> None:
    matches = [contract for contract in load_dataset_contracts(root / "config/datasets.json") if contract.owner_area == area]
    if len(matches) != 1:
        raise ValueError(f"{area}: expected exactly one dataset contract")
    contract = matches[0]
    area_config = root / "analyses" / area / "config.json"
    if not area_config.is_file():
        raise ValueError(f"{area}: missing area configuration")
    config = json.loads(area_config.read_text(encoding="utf-8"))
    required_models = ["SARIMAX", "Holt-Winters", "Random Forest", "PLS Regression"]
    if config.get("dataset_id") != contract.identifier or config.get("models") != required_models:
        raise ValueError(f"{area}: configuration does not match the shared model contract")
    assert_frozen_source_integrity(contract, root)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--area", required=True, choices=[f"grupo{number}" for number in range(1, 6)])
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    validate_area(args.area, Path(args.root).resolve())
    print(f"{args.area}: frozen input and temporal axis validated")

if __name__ == "__main__":
    main()
