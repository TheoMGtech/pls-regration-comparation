#!/usr/bin/env python3
"""Pipeline completa da Base 2 — Bruna Cardoso.

Roda na raiz do repositório:

    .venv/bin/python analyses/grupo2/run_pipeline.py

Ou de dentro da pasta:

    cd analyses/grupo2 && ../../.venv/bin/python run_pipeline.py

Gera tudo em analyses/grupo2/outputs/ (data, figures, results, HTML).
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf

GROUP_DIR = Path(__file__).resolve().parent
ROOT = GROUP_DIR.parents[1]
if str(GROUP_DIR) not in sys.path:
    sys.path.insert(0, str(GROUP_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
from lib import data as data_lib
from lib import eda_stl
from lib import features
from lib import models
from lib.notebooks import write_all_notebooks
from lib.report import write_report


def _plot_residuals(pred_df: pd.DataFrame, model_name: str) -> None:
    resid = pred_df["y_true"] - pred_df["y_pred"]
    fig, axes = plt.subplots(2, 1, figsize=(11, 6))
    axes[0].plot(pd.to_datetime(pred_df["date_time"]), resid, lw=0.5, color="#334155")
    axes[0].axhline(0, color="red", lw=0.8)
    axes[0].set_title(f"Resíduos — {model_name}")
    plot_acf(resid, lags=48, ax=axes[1])
    axes[1].set_title("ACF dos resíduos")
    fig.tight_layout()
    fig.savefig(config.FIG_DIR / f"residuos_{model_name}.png", dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 4))
    sample = pred_df.iloc[: 24 * 14]
    ax.plot(pd.to_datetime(sample["date_time"]), sample["y_true"], label="Real", lw=1)
    ax.plot(pd.to_datetime(sample["date_time"]), sample["y_pred"], label="Previsto", lw=1)
    ax.set_title(f"Previsão vs real (14 dias) — {model_name}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(config.FIG_DIR / f"previsao_{model_name}.png", dpi=120)
    plt.close(fig)


def main() -> int:
    print("=== Base 2 | Metro Interstate Traffic Volume | Bruna Cardoso ===")
    print("Saídas →", config.OUTPUT_DIR)
    data_lib.ensure_output_dirs()

    print("\n[1/8] Limpeza e regularização horária...")
    raw = data_lib.load_raw()
    clean, clean_report = data_lib.clean_and_regularize(raw)
    data_lib.save_frame(clean, config.DATA_DIR / "clean_hourly.csv")
    data_lib.save_json(clean_report, config.DATA_DIR / "cleaning_report.json")
    print(f"  raw={clean_report['n_raw']} -> regular={clean_report['n_regular_hours']}")

    print("\n[2/8] Feature engineering...")
    feat = features.add_calendar_and_lags(clean)
    model_df = features.modeling_matrix(feat)
    data_lib.save_frame(model_df, config.DATA_DIR / "modeling_frame.csv")
    train, test, cut = data_lib.chronological_split(model_df)
    data_lib.save_json(
        {
            "n_modeling": len(model_df),
            "train_size": len(train),
            "test_size": len(test),
            "train_ratio": config.TRAIN_RATIO,
            "train_start": str(train[config.DATETIME_COL].iloc[0]),
            "train_end": str(train[config.DATETIME_COL].iloc[-1]),
            "test_start": str(test[config.DATETIME_COL].iloc[0]),
            "test_end": str(test[config.DATETIME_COL].iloc[-1]),
            "random_state": config.RANDOM_STATE,
            "horizon": config.HORIZON,
            "features": config.FEATURE_COLS,
        },
        config.DATA_DIR / "split_info.json",
    )
    print(f"  modeling={len(model_df)} train={len(train)} test={len(test)}")

    print("\n[3/8] EDA e STL...")
    stl_info = eda_stl.run_eda_and_stl(clean)
    data_lib.save_json(stl_info, config.RESULT_DIR / "stl_summary.json")
    print(f"  força sazonal={stl_info['seasonal_strength']:.3f}")
    print("  figuras em", config.FIG_DIR)

    print("\n[4/8] Otimização de hiperparâmetros (somente treino)...")
    params = {
        "Random_Forest": models.tune_random_forest(train),
        "PLS_Regression": models.tune_pls(train),
        "Holt_Winters": models.tune_holt_winters(train),
        "SARIMAX": models.tune_sarimax(train),
    }
    data_lib.save_json(params, config.RESULT_DIR / "best_params.json")
    for name, p in params.items():
        print(f"  {name}: {p}")

    print("\n[5/8] Walk-forward nos 4 modelos (pode demorar alguns minutos)...")
    results = {}
    train_end = cut

    print("  -> Random Forest...")
    results["Random_Forest"] = models.walkforward_ml(
        model_df, train_end, "Random_Forest", params["Random_Forest"]
    )
    print(f"     MAE={results['Random_Forest'].mae:.3f}")

    print("  -> PLS Regression...")
    results["PLS_Regression"] = models.walkforward_ml(
        model_df, train_end, "PLS_Regression", params["PLS_Regression"]
    )
    results["PLS_Regression"].feature_importance = models.permutation_importance_pls(
        train, params["PLS_Regression"]
    )
    print(f"     MAE={results['PLS_Regression'].mae:.3f}")

    print("  -> Holt-Winters...")
    results["Holt_Winters"] = models.walkforward_holt_winters(
        model_df, train_end, params["Holt_Winters"]
    )
    print(f"     MAE={results['Holt_Winters'].mae:.3f}")

    print("  -> SARIMAX...")
    results["SARIMAX"] = models.walkforward_sarimax(model_df, train_end, params["SARIMAX"])
    print(f"     MAE={results['SARIMAX'].mae:.3f}")

    print("\n[6/8] Salvando métricas, previsões e gráficos...")
    rows = []
    for name, res in results.items():
        models.save_result(res, config.RESULT_DIR)
        _plot_residuals(res.predictions, name)
        rows.append(
            {
                "model": name,
                "mae": res.mae,
                "runtime_sec": res.runtime_sec,
                "ljung_box_pvalue_lag24": res.ljung_box_pvalue,
            }
        )
    mae_df = pd.DataFrame(rows).sort_values("mae")
    mae_df["rank"] = range(1, len(mae_df) + 1)
    mae_df.to_csv(config.RESULT_DIR / "mae_consolidado.csv", index=False)
    print(mae_df.to_string(index=False))

    print("\n[7/8] Atualizando notebooks...")
    write_all_notebooks(
        clean_report=clean_report,
        split_info=json.loads((config.DATA_DIR / "split_info.json").read_text()),
        stl_info=stl_info,
        params=params,
        mae_df=mae_df,
        results=results,
    )

    print("\n[8/8] Relatório HTML...")
    path = write_report(clean_report, stl_info, params, mae_df, results)
    print("OK")
    print("  HTML:", path)
    print("  MAE: ", config.RESULT_DIR / "mae_consolidado.csv")
    print("  Figs:", config.FIG_DIR)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
