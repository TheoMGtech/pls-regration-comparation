from pathlib import Path
import json
import nbformat

def test_each_area_has_an_independent_pipeline_notebook_and_output_contract() -> None:
    root = Path.cwd()
    for number in range(1, 6):
        area = root / "analyses" / f"grupo{number}"
        assert (area / "README.md").is_file()
        assert (area / "config.json").is_file()
        assert (area / "data_dictionary.md").is_file()
        assert (area / "decisions.md").is_file()
        assert (area / "pipeline.py").is_file()
        assert (area / "tests" / "README.md").is_file()
        assert (area / "outputs" / ".gitignore").is_file()
        assert nbformat.read(area / "notebook.ipynb", as_version=4).nbformat == 4
        assert len(json.loads((area / "config.json").read_text(encoding="utf-8"))["models"]) == 4
