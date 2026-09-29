"""Create small, didactic V2 notebooks without copying V1 notebooks."""
from pathlib import Path
import nbformat as nbf

HERE = Path(__file__).resolve().parent
NB = HERE / "notebooks"

NOTEBOOKS = [
    ("01_target_diagnostics.ipynb", "Target diagnostics", "Read the target difficulty and V1 MAE context generated in Stage A.", "outputs/diagnostics/target_difficulty_summary.csv"),
    ("02_external_data_audit.ipynb", "External-data audit", "Inspect official-source provenance and conservative availability rules.", "config/sources.json"),
    ("03_feature_engineering_v2.ipynb", "Causal feature engineering", "Inspect the V2 processed features; every external value is backward-as-of its conservative availability date.", "data/processed/gold_v2_features.csv"),
    ("04_ablation_study.ipynb", "Ablation feasibility screen", "Read the small validation-only Stage A screen. It is not a V2 ranking and must not be used as a final comparison.", "outputs/ablation/ablation_results.csv"),
    ("05_target_variants.ipynb", "Level, delta, and log-return targets", "The three targets are materialized in the processed dataset. Full target-model evaluation requires Stage B approval.", "data/processed/gold_v2_features.csv"),
    ("06_feature_stability.ipynb", "Feature stability", "Reserved for post-model rolling coefficients, VIP and block permutation. No tuning or stability conclusion is produced in Stage A.", "docs/V2_STATUS.md"),
    ("07_models_v2.ipynb", "V2 models", "SARIMAX, Random Forest, PLS and Holt-Winters remain gated. Stage A has no candidate selection.", "config/protocol_v2.json"),
    ("08_v1_vs_v2.ipynb", "V1 vs V2 comparison", "Only scale context is available now; comparable test results require Stage B and identical-origin eligibility checks.", "outputs/diagnostics/mae_context.csv"),
]

for filename, title, purpose, rel in NOTEBOOKS:
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        nbf.v4.new_markdown_cell(f"# {title}\n\n## Objective\n\n{purpose}\n\n## Stage\n\nStage A — lightweight and reproducible. No frozen V1 artifact is changed."),
        nbf.v4.new_markdown_cell("## Configuration\n\nThe notebook uses paths relative to the repository root and does not trigger heavy processing."),
        nbf.v4.new_code_cell("from pathlib import Path\nimport pandas as pd\nROOT = Path.cwd()\nif not (ROOT / 'experiments' / 'gold_v2').exists():\n    ROOT = next(p for p in Path.cwd().parents if (p / 'experiments' / 'gold_v2').exists())\nV2 = ROOT / 'experiments' / 'gold_v2'\nprint(V2)"),
        nbf.v4.new_markdown_cell("## Result\n\nRead the generated artifact below. Interpret it only within its stated Stage A scope."),
        nbf.v4.new_code_cell(f"artifact = V2 / '{rel}'\nprint(artifact)\nif artifact.suffix == '.csv':\n    display(pd.read_csv(artifact).head())\nelse:\n    print(artifact.read_text(encoding='utf-8')[:4000])"),
        nbf.v4.new_markdown_cell("## Interpretation\n\nRecord observations and limitations here after review. Do not turn preliminary evidence into a final model claim."),
    ]
    nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}
    nbf.write(nb, NB / filename)
