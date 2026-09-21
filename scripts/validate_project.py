"""Run every repository-level validation before integration."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pls_regration.cli import validate_area
from pls_regration.config import load_dataset_contracts

def main() -> None:
    for contract in load_dataset_contracts(ROOT / "config/datasets.json"):
        validate_area(contract.owner_area, ROOT)
    print("all five dataset contracts and frozen sources validated")

if __name__ == "__main__":
    main()
