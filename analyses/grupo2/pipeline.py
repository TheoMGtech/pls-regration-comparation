import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from pls_regration.cli import validate_area

if __name__ == "__main__":
    argparse.ArgumentParser().parse_args()
    validate_area("grupo2", ROOT)
    print("grupo2: smoke validation passed")
