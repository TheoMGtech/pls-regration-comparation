"""Reestima Random Forest e PLS com a grade ampliada.

Holt-Winters e SARIMAX permanecem nas previsões já gravadas. Em seguida
o script realinha as quatro séries, regrava VIP, coeficientes e resíduos.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import protocolo_final as protocolo


def load_saved(root: Path, model_name: str) -> dict:
    model_dir = root / "analyses" / "grupo3" / "02_modelos" / model_name / "results"
    selected = json.loads((model_dir / "selected_config.json").read_text(encoding="utf-8"))
    metadata = json.loads((model_dir / "walkforward_metadata.json").read_text(encoding="utf-8"))
    predictions = pd.read_csv(model_dir / "walkforward_predictions.csv", parse_dates=["forecast_origin"])
    return {
        "model": model_name,
        "config": selected["config"],
        "features": selected.get("features", []),
        "tuning": pd.read_csv(model_dir / "tuning_results.csv"),
        "test_predictions": predictions,
        "seconds": float(metadata["runtime_seconds"]),
        "test_fallbacks": int(metadata.get("test_fallbacks", 0)),
    }


def main() -> None:
    root = protocolo.repository_root()
    frame, _, _ = protocolo.load_frame(root)
    holt = load_saved(root, "Holt_Winters")
    sarimax = load_saved(root, "SARIMAX")
    forest = protocolo.run_random_forest(frame)
    pls = protocolo.run_pls(frame)
    results = protocolo.align_predictions([holt, sarimax, forest, pls])

    train_rows = int((frame["split"] == "train_interno").sum())
    test_rows = int(len(results[0]["test_predictions"]))
    for result in results:
        protocolo.save_result(root, result, train_rows, test_rows)
        print(
            f"{result['model']}: MAE={result['test_predictions']['absolute_error'].mean():.4f} "
            f"n={len(result['test_predictions'])}",
            flush=True,
        )

    n_components = int(pls["config"]["n_components"])
    output_dir = root / "analyses" / "grupo3" / "03_resultados" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    protocolo.vip_table(frame, n_components).to_csv(output_dir / "pls_vip.csv", index=False)
    protocolo.coefficient_table(frame, n_components).to_csv(output_dir / "pls_feature_importance.csv", index=False)
    protocolo.residual_diagnostics(root, results)
    protocolo.write_comparison(root, results)
    summary = {
        "runtime_minutes": round(sum(result["seconds"] for result in results) / 60, 2),
        "runtime_note": (
            "Soma dos tempos de cada modelo. Holt-Winters e SARIMAX permanecem da execução anterior; "
            "Random Forest e PLS foram reestimados com a grade ampliada."
        ),
        "n_test_origins": test_rows,
        "models": {
            result["model"]: {
                "mae": float(result["test_predictions"]["absolute_error"].mean()),
                "config": result["config"],
                "minutes": round(result["seconds"] / 60, 2),
            }
            for result in results
        },
    }
    (root / "analyses" / "grupo3" / "02_modelos" / "results" / "protocolo_final.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
