"""Executa o protocolo final da Base 3 e grava previsões, AIC/BIC, VIP e resíduos.

Uso, na raiz do projeto:

    python analyses/grupo3/02_modelos/run_protocolo_final.py
"""
from __future__ import annotations

import json
import time

import protocolo_final as protocolo


def main() -> None:
    root = protocolo.repository_root()
    started = time.perf_counter()
    frame, pm, exog = protocolo.load_frame(root)
    print(frame["split"].value_counts().to_string(), flush=True)
    protocolo.write_protocol(root, frame)

    print("\nAIC/BIC do SARIMAX no fim do treino", flush=True)
    information = protocolo.sarimax_information_criteria(pm, exog)
    aic_path = root / "analyses" / "grupo3" / "02_modelos" / "SARIMAX" / "results"
    aic_path.mkdir(parents=True, exist_ok=True)
    information.to_csv(aic_path / "aic_bic.csv", index=False)

    holt = protocolo.run_holt_winters(frame, pm)
    sarimax = protocolo.run_sarimax(frame, pm, exog)
    forest = protocolo.run_random_forest(frame)
    pls = protocolo.run_pls(frame)
    results = protocolo.align_predictions([holt, sarimax, forest, pls])

    train_rows = int((frame["split"] == "train_interno").sum())
    test_rows = int(len(results[0]["test_predictions"]))
    for result in results:
        protocolo.save_result(root, result, train_rows, test_rows)
        print(
            f"{result['model']}: MAE={result['test_predictions']['absolute_error'].mean():.4f} "
            f"n={len(result['test_predictions'])} tempo={result['seconds'] / 60:.1f} min",
            flush=True,
        )

    n_components = int(pls["config"]["n_components"])
    vip_path = root / "analyses" / "grupo3" / "03_resultados" / "outputs"
    vip_path.mkdir(parents=True, exist_ok=True)
    protocolo.vip_table(frame, n_components).to_csv(vip_path / "pls_vip.csv", index=False)
    protocolo.coefficient_table(frame, n_components).to_csv(vip_path / "pls_feature_importance.csv", index=False)

    protocolo.residual_diagnostics(root, results)
    protocolo.write_comparison(root, results)
    summary = {
        "runtime_minutes": round((time.perf_counter() - started) / 60, 2),
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
