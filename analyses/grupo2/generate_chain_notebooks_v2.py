#!/usr/bin/env python3
"""Gera a cadeia de notebooks do protocolo reforçado da Base 2."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

GROUP = Path(__file__).resolve().parent


def md(text: str):
    return nbf.v4.new_markdown_cell(text)


def code(text: str):
    return nbf.v4.new_code_cell(text)


def notebook(*cells):
    nb = nbf.v4.new_notebook()
    nb.cells = list(cells)
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python"},
    }
    return nb


def write(relative: str, nb) -> None:
    path = GROUP / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        nbf.write(nb, handle)
    print("wrote", relative)


BOOT = """from pathlib import Path
import sys, json
import numpy as np
import pandas as pd
from IPython.display import display, Image

here = Path.cwd().resolve()
group = next(
    (p for p in [here, *here.parents] if (p / "config.py").exists() and (p / "lib").is_dir()),
    None,
)
if group is None:
    raise RuntimeError("Não encontrei analyses/grupo2. Abra o notebook dentro do projeto.")
if str(group) not in sys.path:
    sys.path.insert(0, str(group))

import config
from lib import data as data_lib, features, eda_stl
from lib import models_v2 as models
from lib.nb_boot import require_file, save_json, load_json
data_lib.ensure_output_dirs()
print("outputs →", config.OUTPUT_DIR)
"""


LOAD_MODELING = """model_path = require_file(
    config.DATA_DIR / "modeling_frame.csv",
    "01_dados/03_feature_engineering.ipynb",
)
model_df = pd.read_csv(model_path, parse_dates=[config.DATETIME_COL])
protocol = models.protocol_summary(model_df)
print(
    f"linhas={len(model_df)} | validação={protocol['n_validation_origins']} origens "
    f"| teste={protocol['n_test_origins']} origens"
)
"""


def tuning_notebook(model: str, expression: str, extra: str = ""):
    return notebook(
        md(
            f"# {model} — otimização walk-forward\n\n"
            "A seleção usa apenas os 80% de desenvolvimento. Em cada origem de "
            "validação o modelo é reajustado e prevê somente a próxima hora.\n\n"
            "**Esta etapa é pesada e possui checkpoint em CSV.** Se interromper, "
            "rode novamente para continuar dos candidatos já concluídos."
        ),
        code(BOOT),
        code(LOAD_MODELING),
        code(
            f"""ranking_path = config.RESULT_DIR / "tuning_candidates_{model}.csv"
{extra}
winner, ranking{", screening" if model == "SARIMAX" else ""} = {expression}
save_json(winner, config.RESULT_DIR / "best_params_{model}.json")
all_params_path = config.RESULT_DIR / "best_params.json"
all_params = load_json(all_params_path) if all_params_path.exists() else {{}}
all_params["{model}"] = winner
save_json(all_params, all_params_path)
print("Vencedor:", winner)
display(ranking)
"""
        ),
        md(
            "O teste final não foi usado nesta escolha. Revise o ranking antes "
            "de executar o notebook de walk-forward final."
        ),
    )


def walkforward_notebook(model: str):
    importance = ""
    if model == "PLS_Regression":
        importance = """
res.feature_importance = models.pls_importance(
    model_df, params, models.validation_origins(model_df)
)
"""
    return notebook(
        md(
            f"# {model} — teste final walk-forward\n\n"
            "Parâmetros congelados, mesmas origens dos quatro modelos, horizonte "
            "de 1 hora e reajuste em **toda origem**. Esta é uma execução pesada."
        ),
        code(BOOT),
        code(LOAD_MODELING),
        code(
            f"""params = load_json(require_file(
    config.RESULT_DIR / "best_params_{model}.json",
    "01_otimizacao_hiperparametros.ipynb",
))
origins = models.final_origins(model_df)
print("Parâmetros:", params)
print("Origens finais:", len(origins))
res = models.evaluate(model_df, origins, "{model}", params)
{importance}
models.save_result(res, config.RESULT_DIR)

# Diagnóstico residual em 168 horas consecutivas. Essas previsões não alteram
# o MAE oficial nem a seleção; servem para ACF e Ljung-Box com espaçamento 1h.
diagnostic_origins = models.residual_diagnostic_origins(model_df)
diagnostic = models.evaluate(
    model_df, diagnostic_origins, "{model}", params, progress_every=24
)
diagnostic.predictions.to_csv(
    config.RESULT_DIR / "residual_diagnostic_{model}.csv", index=False
)

baseline_path = config.RESULT_DIR / "baseline_predictions.csv"
baseline = models.baseline_predictions(model_df, origins)
baseline.to_csv(baseline_path, index=False)

print(f"MAE final = {{res.mae:.3f}}")
print(f"Tempo = {{res.runtime_sec / 60:.1f}} min")
print(f"Diagnóstico residual consecutivo = {{diagnostic.runtime_sec / 60:.1f}} min")
display(res.predictions.head())
display(res.predictions.tail())
"""
        ),
        md(
            "O arquivo de métricas registra o número de previsões e o tempo médio "
            "por origem. Não compare o MAE bruto com bases de outra escala."
        ),
    )


def residual_notebook(model: str):
    return notebook(
        md(
            f"# {model} — previsões e resíduos\n\n"
            "Lê as previsões finais e salva os gráficos de diagnóstico."
        ),
        code(BOOT),
        code(
            f"""import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf

path = require_file(
    config.RESULT_DIR / "predictions_{model}.csv",
    "02_walkforward_validacao.ipynb",
)
pred = pd.read_csv(path, parse_dates=["forecast_origin", "target_date"])
diag_path = require_file(
    config.RESULT_DIR / "residual_diagnostic_{model}.csv",
    "02_walkforward_validacao.ipynb",
)
diag = pd.read_csv(diag_path, parse_dates=["forecast_origin", "target_date"])
residual = diag["residual"]
print("MAE oficial =", pred["residual"].abs().mean())
print("Diagnóstico horário: n =", len(diag), "| viés =", residual.mean())

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(pred["target_date"], pred["y_true"], label="Real", color="black")
ax.plot(pred["target_date"], pred["y_pred"], label="Previsto", alpha=.8)
ax.set_title("Real x previsto — {model}")
ax.legend(); fig.tight_layout()
fig.savefig(config.FIG_DIR / "previsao_{model}.png", dpi=140)
plt.show()

fig, axes = plt.subplots(2, 1, figsize=(12, 7))
axes[0].plot(diag["target_date"], residual, lw=.7)
axes[0].axhline(0, color="red", lw=.8)
axes[0].set_title("Resíduos — {model}")
plot_acf(residual, lags=min(72, len(residual)//4), ax=axes[1])
fig.tight_layout()
fig.savefig(config.FIG_DIR / "residuos_{model}.png", dpi=140)
plt.show()
"""
        ),
    )


def main() -> None:
    write(
        "00_ORDEM_DE_EXECUCAO.ipynb",
        notebook(
            md(
                "# Base 2 — ordem de execução (protocolo v3 reforçado)\n\n"
                "Cada notebook mostra resultados e grava o que a próxima etapa usa.\n\n"
                "## 1. Dados\n"
                "1. `01_dados/01_documentacao_bases.ipynb`\n"
                "2. `01_dados/02_limpeza_preparacao.ipynb`\n"
                "3. `01_dados/03_feature_engineering.ipynb`\n"
                "4. `01_dados/04_analise_exploratoria.ipynb`\n"
                "5. `01_dados/05_STL_decomposicao.ipynb`\n\n"
                "## 2. Modelos\n"
                "Para cada modelo: `01_otimizacao` → revise → `02_walkforward` → "
                "`03_previsoes_residuos`.\n\n"
                "A execução completa pode levar **40–50 horas**, pois o tuning "
                "usa 258 origens e o teste cerca de 520, com novo ajuste em cada origem.\n\n"
                "## 3. Consolidação\n"
                "Rode `03_resultados/01` até `04`, depois `04_especialista_PLS` "
                "e `05_relatorio`."
            )
        ),
    )

    write(
        "01_dados/01_documentacao_bases.ipynb",
        notebook(
            md(
                "# Documentação da base de tráfego\n\n"
                "**Etapa:** definição do contrato temporal  \n"
                "**Responsável:** Bruna Carvalho Cardoso · Grupo 5 (PLS) · Base 2\n\n"
                "Texto completo em `DOCUMENTACAO_BASE2.md`. Calendário e feriado "
                "são conhecidos antecipadamente; clima observado em t+1 é vazamento."
            ),
            code(BOOT),
            code(
                """raw = data_lib.load_raw()
print("shape:", raw.shape)
print("período:", raw.date_time.min(), "→", raw.date_time.max())
print("timestamps duplicados:", raw.date_time.duplicated().sum())
display(raw.head())
display(raw.describe(include="all").T)
"""
            ),
        ),
    )

    write(
        "01_dados/02_limpeza_preparacao.ipynb",
        notebook(
            md(
                "# Limpeza e regularização causal\n\n"
                "A versão antiga preenchia uma lacuna de 7.387 horas. Esta versão mantém "
                "o segmento posterior à maior lacuna e não usa valores futuros "
                "na imputação. Uma flag separa alvos reais de imputados."
            ),
            code(BOOT),
            code(
                """raw = data_lib.load_raw()
clean, report = data_lib.clean_and_regularize(raw)
data_lib.save_frame(clean, config.DATA_DIR / "clean_hourly.csv")
data_lib.save_json(report, config.DATA_DIR / "cleaning_report.json")
display(report)
display(clean.head())
print("nulos restantes:", int(clean.isna().sum().sum()))
"""
            ),
        ),
    )

    write(
        "01_dados/03_feature_engineering.ipynb",
        notebook(
            md(
                "# Feature engineering causal\n\n"
                "Inclui vizinhança horária, sazonalidades diária/semanal, janelas "
                "móveis deslocadas e clima defasado. RF e PLS usam as mesmas features."
            ),
            code(BOOT),
            code(
                """clean = pd.read_csv(
    require_file(config.DATA_DIR / "clean_hourly.csv", "02_limpeza_preparacao.ipynb"),
    parse_dates=[config.DATETIME_COL],
)
frame = features.modeling_matrix(features.add_calendar_and_lags(clean))
data_lib.save_frame(frame, config.DATA_DIR / "modeling_frame.csv")
protocol = models.protocol_summary(frame)
data_lib.save_json(protocol, config.RESULT_DIR / "protocol.json")
data_lib.save_json({
    "train_size_70pct": protocol["train_end_index"],
    "validation_end_80pct": protocol["validation_end_index"],
    "test_size_20pct": len(frame) - protocol["validation_end_index"],
    "features": config.FEATURE_COLS,
}, config.DATA_DIR / "split_info.json")
display(protocol)
display(frame.head())
print("features:", len(config.FEATURE_COLS))
"""
            ),
        ),
    )

    write(
        "01_dados/04_analise_exploratoria.ipynb",
        notebook(
            md("# Análise exploratória — somente desenvolvimento (80%)"),
            code(BOOT),
            code(
                """clean = pd.read_csv(
    require_file(config.DATA_DIR / "clean_hourly.csv", "02_limpeza_preparacao.ipynb"),
    parse_dates=[config.DATETIME_COL],
)
model_df = pd.read_csv(
    require_file(config.DATA_DIR / "modeling_frame.csv", "03_feature_engineering.ipynb"),
    parse_dates=[config.DATETIME_COL],
)
test_start = model_df.iloc[int(len(model_df) * config.TRAIN_RATIO)][config.DATETIME_COL]
development_clean = clean.loc[clean[config.DATETIME_COL] < test_start].copy()
summary = eda_stl.run_eda_and_stl(development_clean)
print("EDA limitada ao desenvolvimento; início do teste oculto:", test_start)
for name in ["01_serie_alvo.png", "02_externas.png", "03_perfil_horario.png"]:
    display(Image(filename=str(config.FIG_DIR / name)))
"""
            ),
        ),
    )

    write(
        "01_dados/05_STL_decomposicao.ipynb",
        notebook(
            md("# STL — somente desenvolvimento (80%)"),
            code(BOOT),
            code(
                """clean = pd.read_csv(
    require_file(config.DATA_DIR / "clean_hourly.csv", "02_limpeza_preparacao.ipynb"),
    parse_dates=[config.DATETIME_COL],
)
model_df = pd.read_csv(
    require_file(config.DATA_DIR / "modeling_frame.csv", "03_feature_engineering.ipynb"),
    parse_dates=[config.DATETIME_COL],
)
test_start = model_df.iloc[int(len(model_df) * config.TRAIN_RATIO)][config.DATETIME_COL]
development_clean = clean.loc[clean[config.DATETIME_COL] < test_start].copy()
summary = eda_stl.run_eda_and_stl(development_clean)
data_lib.save_json(summary, config.RESULT_DIR / "stl_summary.json")
display(summary)
display(Image(filename=str(config.FIG_DIR / "04_stl.png")))
"""
            ),
        ),
    )

    write(
        "02_modelos/Random_Forest/01_otimizacao_hiperparametros.ipynb",
        tuning_notebook(
            "Random_Forest",
            "models.tune_random_forest(model_df, ranking_path)",
        ),
    )
    write(
        "02_modelos/PLS_Regression/01_otimizacao_hiperparametros.ipynb",
        tuning_notebook(
            "PLS_Regression",
            "models.tune_pls(model_df, ranking_path)",
        ),
    )
    write(
        "02_modelos/Holt_Winters/01_otimizacao_hiperparametros.ipynb",
        tuning_notebook(
            "Holt_Winters",
            "models.tune_holt_winters(model_df, ranking_path)",
        ),
    )
    write(
        "02_modelos/SARIMAX/01_otimizacao_hiperparametros.ipynb",
        tuning_notebook(
            "SARIMAX",
            "models.tune_sarimax(model_df, screening_path, ranking_path)",
            extra='screening_path = config.RESULT_DIR / "sarimax_bic_screening.csv"',
        ),
    )

    for model in ("Holt_Winters", "PLS_Regression", "Random_Forest", "SARIMAX"):
        write(
            f"02_modelos/{model}/02_walkforward_validacao.ipynb",
            walkforward_notebook(model),
        )
        write(
            f"02_modelos/{model}/03_previsoes_residuos.ipynb",
            residual_notebook(model),
        )

    write(
        "03_resultados/01_MAE_consolidado.ipynb",
        notebook(
            md("# MAE consolidado e comparação com baselines"),
            code(BOOT),
            code(
                """rows = []
for model in ("Holt_Winters", "PLS_Regression", "Random_Forest", "SARIMAX"):
    path = config.RESULT_DIR / f"metrics_{model}.json"
    if not path.exists():
        print("Falta executar:", model)
        continue
    metric = load_json(path)
    rows.append({
        "model": model,
        "n_forecasts": metric["n_forecasts"],
        "mae": metric["mae"],
        "rmse": metric.get("rmse"),
        "median_absolute_error": metric.get("median_absolute_error"),
        "wape_percent": metric.get("wape_percent"),
        "bias": metric.get("bias"),
        "r2": metric.get("r2"),
        "residual_acf_lag1": metric.get("residual_acf_lag1"),
        "fallback_count": metric.get("fallback_count", 0),
        "convergence_rate": metric.get("convergence_rate", 1.0),
        "runtime_sec": metric["runtime_sec"],
        "mean_seconds_per_origin": metric["mean_seconds_per_origin"],
        "ljung_box_pvalue_sampled_sequence_lag24": metric.get(
            "ljung_box_pvalue_sampled_sequence_lag24"
        ),
    })
mae = pd.DataFrame(rows).sort_values("mae")
mae["rank"] = range(1, len(mae) + 1)
mae.to_csv(config.RESULT_DIR / "mae_consolidado.csv", index=False)

baseline = pd.read_csv(require_file(
    config.RESULT_DIR / "baseline_predictions.csv",
    "qualquer notebook 02_walkforward_validacao.ipynb",
))
baseline_mae = (
    baseline.assign(squared_error=lambda x: (x["y_true"] - x["y_pred"]) ** 2)
    .groupby("baseline", as_index=False)
    .agg(
        mae=("absolute_error", "mean"),
        rmse=("squared_error", lambda x: float(np.sqrt(x.mean()))),
        n_forecasts=("absolute_error", "size"),
    )
)
best_baseline = float(baseline_mae["mae"].min())
mae["improvement_vs_best_baseline_percent"] = (
    100 * (best_baseline - mae["mae"]) / best_baseline
)
mae.to_csv(config.RESULT_DIR / "mae_consolidado.csv", index=False)
display(mae)
display(baseline_mae)
"""
            ),
            md(
                "MAE só pode ser comparado dentro desta base. Para comparar bases "
                "de escalas diferentes, use ranking, WAPE ou melhoria contra baseline."
            ),
        ),
    )

    write(
        "03_resultados/02_analise_residuos_Ljung_Box.ipynb",
        notebook(
            md("# Resíduos e Ljung-Box consolidado"),
            code(BOOT),
            code(
                """from statsmodels.stats.diagnostic import acorr_ljungbox

mae = pd.read_csv(require_file(
    config.RESULT_DIR / "mae_consolidado.csv", "01_MAE_consolidado.ipynb"
))
rows = []
for model in mae["model"]:
    pred = pd.read_csv(require_file(
        config.RESULT_DIR / f"residual_diagnostic_{model}.csv",
        f"02_modelos/{model}/02_walkforward_validacao.ipynb",
    ))
    residual = pred["y_true"] - pred["y_pred"]
    lb = acorr_ljungbox(residual, lags=[1, 6, 12, 24], return_df=True)
    rows.append({
        "model": model,
        "bias": residual.mean(),
        "acf_lag1": residual.autocorr(1),
        **{
            f"p_ljung_box_{lag}": lb.loc[lag, "lb_pvalue"]
            for lag in (1, 6, 12, 24)
        },
    })
residual_summary = pd.DataFrame(rows)
residual_summary.to_csv(
    config.RESULT_DIR / "residual_diagnostics.csv", index=False
)
display(residual_summary)
print("p < 0,05 indica autocorrelação remanescente nos erros.")
print("Os lags acima são horários: o diagnóstico usa 168 origens consecutivas.")
"""
            ),
        ),
    )

    write(
        "03_resultados/03_importancia_features.ipynb",
        notebook(
            md("# Importância — Random Forest e PLS"),
            code(BOOT),
            code(
                """for model in ("Random_Forest", "PLS_Regression"):
    path = require_file(
        config.RESULT_DIR / f"feature_importance_{model}.csv",
        f"02_modelos/{model}/02_walkforward_validacao.ipynb",
    )
    print("\\n", model)
    display(pd.read_csv(path).head(15))
"""
            ),
        ),
    )

    write(
        "03_resultados/04_comparacao_modelos.ipynb",
        notebook(
            md("# Comparação final dos quatro modelos"),
            code(BOOT),
            code(
                """mae = pd.read_csv(require_file(
    config.RESULT_DIR / "mae_consolidado.csv", "01_MAE_consolidado.ipynb"
))
display(mae)
for model in mae["model"]:
    path = config.FIG_DIR / f"previsao_{model}.png"
    if path.exists():
        print(model)
        display(Image(filename=str(path)))
"""
            ),
            code(
                """# Incerteza do MAE: bootstrap em blocos de 7 origens.
rng = np.random.default_rng(config.RANDOM_STATE)
errors = {}
for model in mae["model"]:
    pred = pd.read_csv(
        config.RESULT_DIR / f"predictions_{model}.csv",
        parse_dates=["target_date"],
    )
    errors[model] = (pred["y_true"] - pred["y_pred"]).abs().to_numpy()

def block_sample(n, block=7):
    starts = rng.integers(0, n, size=int(np.ceil(n / block)))
    return np.concatenate([
        np.arange(start, start + block) % n for start in starts
    ])[:n]

ci_rows = []
for model, values in errors.items():
    samples = np.array([
        values[block_sample(len(values))].mean() for _ in range(5000)
    ])
    ci_rows.append({
        "model": model,
        "mae": values.mean(),
        "mae_ci95_low": np.quantile(samples, 0.025),
        "mae_ci95_high": np.quantile(samples, 0.975),
    })
ci = pd.DataFrame(ci_rows).sort_values("mae")
ci.to_csv(config.RESULT_DIR / "mae_uncertainty.csv", index=False)
display(ci)
"""
            ),
        ),
    )

    write(
        "04_especialista_PLS/01_estudo_conceitual_PLS.ipynb",
        notebook(
            md(
                "# PLS Regression — estudo conceitual\n\n"
                "**Etapa:** fundamentação do modelo especialista\n\n"
                "Síntese completa em `outputs/PLS_technical_summary.md`. "
                "Venceu `no_weather` com 15 componentes na validação; "
                "o teste não reabriu essa escolha."
            ),
            code(
                """from IPython.display import Markdown, display
text = (config.OUTPUT_DIR / "PLS_technical_summary.md").read_text(encoding="utf-8")
display(Markdown(text))
"""
            ),
        ),
    )
    write(
        "04_especialista_PLS/02_implementacao_PLS.ipynb",
        notebook(
            md("# PLS — implementação e parâmetros congelados"),
            code(BOOT),
            code(
                """params = load_json(require_file(
    config.RESULT_DIR / "best_params_PLS_Regression.json",
    "02_modelos/PLS_Regression/01_otimizacao_hiperparametros.ipynb",
))
metrics = load_json(require_file(
    config.RESULT_DIR / "metrics_PLS_Regression.json",
    "02_modelos/PLS_Regression/02_walkforward_validacao.ipynb",
))
display(params)
display(metrics)
"""
            ),
        ),
    )
    write(
        "04_especialista_PLS/03_interpretacao_resultados.ipynb",
        notebook(
            md(
                "# PLS — coeficientes, VIP e permutation importance\n\n"
                "Permutation na validação: y_lag_1, y_lag_169, y_lag_168, "
                "y_lag_336, y_lag_24. Sem causalidade. "
                "Ver `outputs/feature_importance_analysis.md`."
            ),
            code(BOOT),
            code(
                """importance = pd.read_csv(require_file(
    config.RESULT_DIR / "feature_importance_PLS_Regression.csv",
    "02_modelos/PLS_Regression/02_walkforward_validacao.ipynb",
))
display(importance)
for name in ("previsao_PLS_Regression.png", "residuos_PLS_Regression.png"):
    display(Image(filename=str(config.FIG_DIR / name)))
"""
            ),
        ),
    )

    write(
        "05_relatorio/relatorio.ipynb",
        notebook(
            md(
                "# Relatório técnico — Base 2\n\n"
                "Gera o HTML paginado a partir dos artefatos congelados. "
                "Não retreina modelos."
            ),
            code(BOOT),
            code(
                """from lib.report_html import write_paginated_report
mae = pd.read_csv(require_file(
    config.RESULT_DIR / "mae_consolidado.csv",
    "03_resultados/01_MAE_consolidado.ipynb",
))
display(mae.sort_values("mae"))
report_path = write_paginated_report()
print("Relatório gravado em:", report_path)
"""
            ),
        ),
    )


if __name__ == "__main__":
    main()
