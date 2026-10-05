#!/usr/bin/env python3
"""Executa o protocolo reforçado completo da Base 2.

Esta rotina pode levar horas. Para acompanhar e revisar etapa a etapa, prefira
os notebooks indicados em 00_ORDEM_DE_EXECUCAO.ipynb.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

GROUP = Path(__file__).resolve().parent
ROOT = GROUP.parents[1]
for path in (GROUP, ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import config
from lib import data as data_lib
from lib import eda_stl, features
from lib import models_v2 as models


def main() -> int:
    data_lib.ensure_output_dirs()
    print("Base 2 — protocolo v3 reforçado (execução pesada)")

    print("\n[1/6] Limpeza causal")
    clean, cleaning_report = data_lib.clean_and_regularize(data_lib.load_raw())
    data_lib.save_frame(clean, config.DATA_DIR / "clean_hourly.csv")
    data_lib.save_json(cleaning_report, config.DATA_DIR / "cleaning_report.json")

    print("\n[2/6] Features e protocolo")
    frame = features.modeling_matrix(features.add_calendar_and_lags(clean))
    data_lib.save_frame(frame, config.DATA_DIR / "modeling_frame.csv")
    protocol = models.protocol_summary(frame)
    data_lib.save_json(protocol, config.RESULT_DIR / "protocol.json")
    data_lib.save_json(
        {
            "train_size_70pct": protocol["train_end_index"],
            "validation_end_80pct": protocol["validation_end_index"],
            "test_size_20pct": len(frame) - protocol["validation_end_index"],
            "features": config.FEATURE_COLS,
        },
        config.DATA_DIR / "split_info.json",
    )
    print(json.dumps(protocol, indent=2, ensure_ascii=False))

    print("\n[3/6] EDA e STL")
    stl = eda_stl.run_eda_and_stl(clean)
    data_lib.save_json(stl, config.RESULT_DIR / "stl_summary.json")

    print("\n[4/6] Tuning walk-forward")
    params: dict[str, dict] = {}
    params["Holt_Winters"], _ = models.tune_holt_winters(
        frame, config.RESULT_DIR / "tuning_candidates_Holt_Winters.csv"
    )
    params["PLS_Regression"], _ = models.tune_pls(
        frame, config.RESULT_DIR / "tuning_candidates_PLS_Regression.csv"
    )
    params["Random_Forest"], _ = models.tune_random_forest(
        frame, config.RESULT_DIR / "tuning_candidates_Random_Forest.csv"
    )
    params["SARIMAX"], _, _ = models.tune_sarimax(
        frame,
        config.RESULT_DIR / "sarimax_bic_screening.csv",
        config.RESULT_DIR / "tuning_candidates_SARIMAX.csv",
    )
    data_lib.save_json(params, config.RESULT_DIR / "best_params.json")
    for model, selected in params.items():
        data_lib.save_json(
            selected, config.RESULT_DIR / f"best_params_{model}.json"
        )

    print("\n[5/6] Teste final — mesmas origens, refit em cada origem")
    origins = models.final_origins(frame)
    baseline = models.baseline_predictions(frame, origins)
    baseline.to_csv(config.RESULT_DIR / "baseline_predictions.csv", index=False)
    results = {}
    for model in ("Holt_Winters", "PLS_Regression", "Random_Forest", "SARIMAX"):
        result = models.evaluate(frame, origins, model, params[model])
        if model == "PLS_Regression":
            result.feature_importance = models.pls_importance(
                frame, params[model], models.validation_origins(frame)
            )
        models.save_result(result, config.RESULT_DIR)
        diagnostic = models.evaluate(
            frame,
            models.residual_diagnostic_origins(frame),
            model,
            params[model],
            progress_every=24,
        )
        diagnostic.predictions.to_csv(
            config.RESULT_DIR / f"residual_diagnostic_{model}.csv",
            index=False,
        )
        results[model] = result

    print("\n[6/6] Consolidação")
    rows = [
        {
            "model": model,
            "n_forecasts": len(result.predictions),
            "mae": result.mae,
            "runtime_sec": result.runtime_sec,
            "mean_seconds_per_origin": (
                result.runtime_sec / len(result.predictions)
            ),
            "ljung_box_pvalue_lag24": result.ljung_box_pvalue,
        }
        for model, result in results.items()
    ]
    mae = pd.DataFrame(rows).sort_values("mae")
    mae["rank"] = range(1, len(mae) + 1)
    mae.to_csv(config.RESULT_DIR / "mae_consolidado.csv", index=False)
    print(mae.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
