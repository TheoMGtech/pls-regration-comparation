from pathlib import Path
import subprocess
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TREATMENT_DIR = ROOT / "bases" / "grupo5-tratamento"


def test_gold_treatment_documentation_is_canonical_and_answers_column_questions() -> None:
    canonical = TREATMENT_DIR / "DATASET_CONFIG.md"
    content = canonical.read_text(encoding="utf-8")
    for term in ("DATE", "VALUE", "IS_HOLIDAY", "TARGET_UP", "TARGET", "GOLD_LAG_1"):
        assert term in content
    pointer = (ROOT / "docs" / "DATASET_CONFIG.md").read_text(encoding="utf-8")
    assert "bases/grupo5-tratamento/DATASET_CONFIG.md" in pointer
    for filename in ("gold_daily_prices.csv", "dgs10.csv", "dff.csv", "prepare_gold_dataset.py"):
        assert (TREATMENT_DIR / filename).is_file()


def test_gold_script_reproduces_the_versioned_final_csv(tmp_path: Path) -> None:
    output = tmp_path / "gold_daily_modeling.csv"
    subprocess.run(
        [sys.executable, str(TREATMENT_DIR / "prepare_gold_dataset.py"), "--output", str(output)],
        check=True,
        capture_output=True,
        text=True,
    )
    expected = pd.read_csv(ROOT / "bases" / "grupo5" / "gold_daily_modeling.csv")
    generated = pd.read_csv(output)
    pd.testing.assert_frame_equal(generated, expected)
