#!/usr/bin/env python3
"""Gera notebooks executáveis em cadeia (cada um grava outputs/ para o próximo)."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

GROUP = Path(__file__).resolve().parent


def nb(*cells):
    node = nbf.v4.new_notebook()
    node["cells"] = list(cells)
    node["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }
    return node


def md(t):
    return nbf.v4.new_markdown_cell(t)


def code(t):
    return nbf.v4.new_code_cell(t)


BOOT = """from pathlib import Path
import sys
from IPython.display import display, Image, Markdown
import pandas as pd

# sobe até achar analyses/grupo2
here = Path.cwd().resolve()
group = None
for c in [here, *here.parents]:
    if (c / 'config.py').exists() and (c / 'lib').is_dir():
        group = c
        break
if group is None:
    raise RuntimeError('Abra/rode este notebook de dentro de analyses/grupo2/...')
if str(group) not in sys.path:
    sys.path.insert(0, str(group))

import config
from lib import data as data_lib
from lib import features, eda_stl, models
from lib.nb_boot import require_file, save_json, load_json
data_lib.ensure_output_dirs()
print('grupo2 →', group)
print('outputs →', config.OUTPUT_DIR)
"""


def write(rel: str, notebook) -> None:
    path = GROUP / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        nbf.write(notebook, f)
    print("wrote", path.relative_to(GROUP))


def main() -> None:
    # ---------- ORDEM ----------
    write(
        "00_ORDEM_DE_EXECUCAO.ipynb",
        nb(
            md(
                "# Ordem de execução — Base 2\n\n"
                "Rode **nesta ordem**. Cada notebook grava arquivos em `outputs/` "
                "que o próximo precisa.\n\n"
                "## 1. Dados\n"
                "1. `01_dados/01_documentacao_bases.ipynb`\n"
                "2. `01_dados/02_limpeza_preparacao.ipynb` → `outputs/data/clean_hourly.csv`\n"
                "3. `01_dados/03_feature_engineering.ipynb` → `outputs/data/modeling_frame.csv`\n"
                "4. `01_dados/04_analise_exploratoria.ipynb` → figuras\n"
                "5. `01_dados/05_STL_decomposicao.ipynb` → STL + força sazonal\n\n"
                "## 2. Modelos (para cada um: SARIMAX, Holt_Winters, Random_Forest, PLS_Regression)\n"
                "1. `02_modelos/<MODELO>/01_otimizacao_hiperparametros.ipynb` → params\n"
                "2. `02_modelos/<MODELO>/02_walkforward_validacao.ipynb` → predictions + metrics\n"
                "3. `02_modelos/<MODELO>/03_previsoes_residuos.ipynb` → figuras de resíduos\n\n"
                "## 3. Resultados\n"
                "1. `03_resultados/01_MAE_consolidado.ipynb`\n"
                "2. `03_resultados/02_analise_residuos_Ljung_Box.ipynb`\n"
                "3. `03_resultados/03_importancia_features.ipynb`\n"
                "4. `03_resultados/04_comparacao_modelos.ipynb`\n\n"
                "## 4. PLS + relatório\n"
                "- `04_especialista_PLS/...`\n"
                "- `05_relatorio/relatorio.ipynb`\n\n"
                "Atalho (opcional): `run_pipeline.py` roda tudo de uma vez no terminal."
            )
        ),
    )

    # ---------- 01 DADOS ----------
    write(
        "01_dados/01_documentacao_bases.ipynb",
        nb(
            md(
                f"# Documentação — Base 2\n\n**Responsável:** {__import__('config', fromlist=['OWNER']).OWNER if False else 'Bruna Carvalho Cardoso'}\n\n"
                "Base: Metro Interstate Traffic Volume (horária). "
                "Alvo: `traffic_volume`. Externas climáticas com **lag 1h**; feriado/calendário ok."
            ),
            code(BOOT),
            code(
                "raw = data_lib.load_raw()\n"
                "print('arquivo:', config.RAW_PATH)\n"
                "print('shape bruto:', raw.shape)\n"
                "print('colunas:', list(raw.columns))\n"
                "print('período:', raw[config.DATETIME_COL].min(), '→', raw[config.DATETIME_COL].max())\n"
                "display(raw.head())\n"
                "display(raw.isna().sum())"
            ),
            md(
                "## Dicionário rápido\n\n"
                "| Coluna | Papel | Disponibilidade |\n|---|---|---|\n"
                "| traffic_volume | alvo | — |\n"
                "| holiday → is_holiday | calendário | conhecido antes |\n"
                "| temp, rain_1h, snow_1h, clouds_all | clima | observação → usar lag 1h |\n"
            ),
        ),
    )

    write(
        "01_dados/02_limpeza_preparacao.ipynb",
        nb(
            md(
                "# Limpeza e preparação\n\n"
                "**Grava:** `outputs/data/clean_hourly.csv` e `cleaning_report.json`\n\n"
                "Próximo notebook: feature engineering."
            ),
            code(BOOT),
            code(
                "raw = data_lib.load_raw()\n"
                "clean, report = data_lib.clean_and_regularize(raw)\n"
                "out = config.DATA_DIR / 'clean_hourly.csv'\n"
                "data_lib.save_frame(clean, out)\n"
                "data_lib.save_json(report, config.DATA_DIR / 'cleaning_report.json')\n"
                "print('salvo:', out)\n"
                "display(report)\n"
                "display(clean.head())\n"
                "print('nulos restantes:', clean.isna().sum().sum())"
            ),
        ),
    )

    write(
        "01_dados/03_feature_engineering.ipynb",
        nb(
            md(
                "# Feature engineering\n\n"
                "**Lê:** `outputs/data/clean_hourly.csv`\n\n"
                "**Grava:** `outputs/data/modeling_frame.csv` + `split_info.json`\n\n"
                "Split cronológico 80/20, `random_state=67`, mesmas features RF+PLS."
            ),
            code(BOOT),
            code(
                "clean_path = require_file(config.DATA_DIR / 'clean_hourly.csv', '01_dados/02_limpeza_preparacao.ipynb')\n"
                "clean = pd.read_csv(clean_path, parse_dates=[config.DATETIME_COL])\n"
                "feat = features.add_calendar_and_lags(clean)\n"
                "model_df = features.modeling_matrix(feat)\n"
                "train, test, cut = data_lib.chronological_split(model_df)\n"
                "data_lib.save_frame(model_df, config.DATA_DIR / 'modeling_frame.csv')\n"
                "info = {\n"
                "    'n_modeling': len(model_df),\n"
                "    'train_size': len(train),\n"
                "    'test_size': len(test),\n"
                "    'train_ratio': config.TRAIN_RATIO,\n"
                "    'cut_index': cut,\n"
                "    'train_start': str(train[config.DATETIME_COL].iloc[0]),\n"
                "    'train_end': str(train[config.DATETIME_COL].iloc[-1]),\n"
                "    'test_start': str(test[config.DATETIME_COL].iloc[0]),\n"
                "    'test_end': str(test[config.DATETIME_COL].iloc[-1]),\n"
                "    'random_state': config.RANDOM_STATE,\n"
                "    'horizon': config.HORIZON,\n"
                "    'features': config.FEATURE_COLS,\n"
                "}\n"
                "data_lib.save_json(info, config.DATA_DIR / 'split_info.json')\n"
                "print('features:', config.FEATURE_COLS)\n"
                "display(info)\n"
                "display(model_df.head())"
            ),
        ),
    )

    write(
        "01_dados/04_analise_exploratoria.ipynb",
        nb(
            md("# Análise exploratória\n\n**Lê:** série limpa. **Grava:** figuras em `outputs/figures/`."),
            code(BOOT),
            code(
                "clean = pd.read_csv(require_file(config.DATA_DIR / 'clean_hourly.csv', '02_limpeza_preparacao.ipynb'),\n"
                "                   parse_dates=[config.DATETIME_COL])\n"
                "stl_info = eda_stl.run_eda_and_stl(clean)  # também gera STL; ok repetir depois\n"
                "print('figuras:', stl_info['figures'])\n"
                "for name in ['01_serie_alvo.png', '02_externas.png', '03_perfil_horario.png']:\n"
                "    display(Image(filename=str(config.FIG_DIR / name)))"
            ),
        ),
    )

    write(
        "01_dados/05_STL_decomposicao.ipynb",
        nb(
            md(
                "# STL\n\n**Lê:** `clean_hourly.csv`. **Grava:** `outputs/figures/04_stl.png` + `outputs/results/stl_summary.json`."
            ),
            code(BOOT),
            code(
                "clean = pd.read_csv(require_file(config.DATA_DIR / 'clean_hourly.csv', '02_limpeza_preparacao.ipynb'),\n"
                "                   parse_dates=[config.DATETIME_COL])\n"
                "stl_info = eda_stl.run_eda_and_stl(clean)\n"
                "data_lib.save_json(stl_info, config.RESULT_DIR / 'stl_summary.json')\n"
                "print('força sazonal =', round(stl_info['seasonal_strength'], 3))\n"
                "display(stl_info)\n"
                "display(Image(filename=str(config.FIG_DIR / '04_stl.png')))"
            ),
        ),
    )

    # ---------- MODELOS ----------
    model_specs = {
        "Holt_Winters": {
            "tune": "models.tune_holt_winters(train)",
            "wf": "models.walkforward_holt_winters(model_df, cut, params)",
            "importance": False,
        },
        "SARIMAX": {
            "tune": "models.tune_sarimax(train)",
            "wf": "models.walkforward_sarimax(model_df, cut, params)",
            "importance": False,
        },
        "Random_Forest": {
            "tune": "models.tune_random_forest(train)",
            "wf": "models.walkforward_ml(model_df, cut, 'Random_Forest', params)",
            "importance": True,
        },
        "PLS_Regression": {
            "tune": "models.tune_pls(train)",
            "wf": "models.walkforward_ml(model_df, cut, 'PLS_Regression', params)",
            "importance": True,
            "perm": True,
        },
    }

    load_modeling = (
        "model_df = pd.read_csv(require_file(config.DATA_DIR / 'modeling_frame.csv', '01_dados/03_feature_engineering.ipynb'),\n"
        "                       parse_dates=[config.DATETIME_COL])\n"
        "info = load_json(require_file(config.DATA_DIR / 'split_info.json', '01_dados/03_feature_engineering.ipynb'))\n"
        "cut = int(info['cut_index'])\n"
        "train = model_df.iloc[:cut].copy()\n"
        "test = model_df.iloc[cut:].copy()\n"
        "print('train', len(train), 'test', len(test))\n"
    )

    for model, spec in model_specs.items():
        write(
            f"02_modelos/{model}/01_otimizacao_hiperparametros.ipynb",
            nb(
                md(
                    f"# {model} — otimização de hiperparâmetros\n\n"
                    f"**Lê:** `modeling_frame.csv` (só treino).\n\n"
                    f"**Grava:** `outputs/results/best_params_{model}.json` "
                    f"(e atualiza chave em `best_params.json`).\n\n"
                    "Não usa o conjunto de teste."
                ),
                code(BOOT),
                code(load_modeling),
                code(
                    f"print('Otimizando {model}...')\n"
                    f"params = {spec['tune']}\n"
                    f"save_json(params, config.RESULT_DIR / 'best_params_{model}.json')\n"
                    "all_params = {}\n"
                    "bp = config.RESULT_DIR / 'best_params.json'\n"
                    "if bp.exists():\n"
                    "    all_params = load_json(bp)\n"
                    f"all_params['{model}'] = params\n"
                    "save_json(all_params, bp)\n"
                    "print('salvo')\n"
                    "display(params)"
                ),
            ),
        )

        perm_extra = ""
        if spec.get("perm"):
            perm_extra = (
                "\nres.feature_importance = models.permutation_importance_pls(train, params)\n"
            )

        write(
            f"02_modelos/{model}/02_walkforward_validacao.ipynb",
            nb(
                md(
                    f"# {model} — walk-forward\n\n"
                    f"**Lê:** `modeling_frame.csv` + `best_params_{model}.json`\n\n"
                    f"**Grava:** `predictions_{model}.csv`, `metrics_{model}.json`"
                    + (
                        f", `feature_importance_{model}.csv`"
                        if spec["importance"]
                        else ""
                    )
                ),
                code(BOOT),
                code(load_modeling),
                code(
                    f"params = load_json(require_file(config.RESULT_DIR / 'best_params_{model}.json',\n"
                    f"                               '02_modelos/{model}/01_otimizacao_hiperparametros.ipynb'))\n"
                    f"print('params:', params)\n"
                    f"print('Walk-forward {model} (pode demorar)...')\n"
                    f"res = {spec['wf']}\n"
                    f"{perm_extra}"
                    f"models.save_result(res, config.RESULT_DIR)\n"
                    f"print('MAE =', res.mae)\n"
                    f"print('Ljung-Box p =', res.ljung_box_pvalue)\n"
                    f"display(res.predictions.tail())\n"
                ),
            ),
        )

        write(
            f"02_modelos/{model}/03_previsoes_residuos.ipynb",
            nb(
                md(
                    f"# {model} — previsões e resíduos\n\n"
                    f"**Lê:** `predictions_{model}.csv`\n\n"
                    f"**Grava:** `outputs/figures/previsao_{model}.png` e `residuos_{model}.png`"
                ),
                code(BOOT),
                code(
                    "import matplotlib.pyplot as plt\n"
                    "from statsmodels.graphics.tsaplots import plot_acf\n"
                    f"pred = pd.read_csv(require_file(config.RESULT_DIR / 'predictions_{model}.csv',\n"
                    f"                               '02_modelos/{model}/02_walkforward_validacao.ipynb'),\n"
                    "                  parse_dates=['date_time'])\n"
                    "resid = pred['y_true'] - pred['y_pred']\n"
                    "print('MAE', resid.abs().mean())\n"
                    "\n"
                    "fig, ax = plt.subplots(figsize=(11, 4))\n"
                    "s = pred.iloc[:24*14]\n"
                    "ax.plot(s['date_time'], s['y_true'], label='Real')\n"
                    "ax.plot(s['date_time'], s['y_pred'], label='Previsto')\n"
                    f"ax.set_title('Previsão vs real (14 dias) — {model}')\n"
                    "ax.legend(); fig.tight_layout()\n"
                    f"fig.savefig(config.FIG_DIR / 'previsao_{model}.png', dpi=120); plt.show()\n"
                    "\n"
                    "fig, axes = plt.subplots(2, 1, figsize=(11, 6))\n"
                    "axes[0].plot(pred['date_time'], resid, lw=0.5)\n"
                    "axes[0].axhline(0, color='red', lw=0.8)\n"
                    f"axes[0].set_title('Resíduos — {model}')\n"
                    "plot_acf(resid, lags=48, ax=axes[1])\n"
                    "fig.tight_layout()\n"
                    f"fig.savefig(config.FIG_DIR / 'residuos_{model}.png', dpi=120); plt.show()\n"
                ),
            ),
        )

    # ---------- RESULTADOS ----------
    write(
        "03_resultados/01_MAE_consolidado.ipynb",
        nb(
            md(
                "# MAE consolidado\n\n"
                "**Lê:** `metrics_*.json` de cada modelo já rodado.\n\n"
                "**Grava:** `mae_consolidado.csv`"
            ),
            code(BOOT),
            code(
                "rows = []\n"
                "for model in ['Random_Forest', 'PLS_Regression', 'SARIMAX', 'Holt_Winters']:\n"
                "    path = config.RESULT_DIR / f'metrics_{model}.json'\n"
                "    if not path.exists():\n"
                "        print('ainda falta:', path.name, '→ rode o walk-forward desse modelo')\n"
                "        continue\n"
                "    m = load_json(path)\n"
                "    rows.append({'model': model, 'mae': m['mae'], 'runtime_sec': m['runtime_sec'],\n"
                "                 'ljung_box_pvalue_lag24': m['ljung_box_pvalue_lag24']})\n"
                "mae_df = pd.DataFrame(rows).sort_values('mae')\n"
                "mae_df['rank'] = range(1, len(mae_df) + 1)\n"
                "mae_df.to_csv(config.RESULT_DIR / 'mae_consolidado.csv', index=False)\n"
                "display(mae_df)\n"
                "if len(mae_df):\n"
                "    print('Melhor:', mae_df.iloc[0]['model'])\n"
            ),
        ),
    )

    write(
        "03_resultados/02_analise_residuos_Ljung_Box.ipynb",
        nb(
            md("# Ljung-Box consolidado\n\n**Lê:** `mae_consolidado.csv` (ou metrics)."),
            code(BOOT),
            code(
                "path = require_file(config.RESULT_DIR / 'mae_consolidado.csv', '03_resultados/01_MAE_consolidado.ipynb')\n"
                "df = pd.read_csv(path)\n"
                "display(df[['model', 'mae', 'ljung_box_pvalue_lag24']])\n"
                "print('p≈0 ⇒ ainda há autocorrelação nos resíduos (discutir no relatório).')"
            ),
        ),
    )

    write(
        "03_resultados/03_importancia_features.ipynb",
        nb(
            md(
                "# Importância das features\n\n"
                "**Lê:** CSVs de RF e PLS (gerados no walk-forward desses modelos)."
            ),
            code(BOOT),
            code(
                "for model in ['Random_Forest', 'PLS_Regression']:\n"
                "    path = config.RESULT_DIR / f'feature_importance_{model}.csv'\n"
                "    if not path.exists():\n"
                "        print('falta', path.name)\n"
                "        continue\n"
                "    print('===', model, '===')\n"
                "    display(pd.read_csv(path).head(12))"
            ),
        ),
    )

    write(
        "03_resultados/04_comparacao_modelos.ipynb",
        nb(
            md("# Comparação dos modelos\n\n**Lê:** MAE + figuras de previsão."),
            code(BOOT),
            code(
                "mae = pd.read_csv(require_file(config.RESULT_DIR / 'mae_consolidado.csv', '01_MAE_consolidado.ipynb'))\n"
                "display(mae)\n"
                "for model in mae['model']:\n"
                "    fig = config.FIG_DIR / f'previsao_{model}.png'\n"
                "    if fig.exists():\n"
                "        print(model)\n"
                "        display(Image(filename=str(fig)))\n"
            ),
        ),
    )

    write(
        "04_especialista_PLS/01_estudo_conceitual_PLS.ipynb",
        nb(
            md(
                "# PLS — estudo conceitual\n\n"
                "Partial Least Squares cria componentes que maximizam a covariância entre X e y. "
                "Bom com multicolinearidade (lags + calendário + clima).\n\n"
                "**Vantagens:** redução supervisionada, estável com correlação.\n\n"
                "**Limitações:** relação linear nos componentes; nº de componentes é crítico.\n\n"
                "Rode os notebooks de PLS em `02_modelos/PLS_Regression/` antes da interpretação."
            )
        ),
    )

    write(
        "04_especialista_PLS/02_implementacao_PLS.ipynb",
        nb(
            md("# PLS — implementação (aponta para artefatos já gerados)"),
            code(BOOT),
            code(
                "params = load_json(require_file(config.RESULT_DIR / 'best_params_PLS_Regression.json',\n"
                "                               '02_modelos/PLS_Regression/01_otimizacao...'))\n"
                "pred = pd.read_csv(require_file(config.RESULT_DIR / 'predictions_PLS_Regression.csv',\n"
                "                               '02_modelos/PLS_Regression/02_walkforward...'))\n"
                "display(params)\n"
                "print('MAE', (pred.y_true - pred.y_pred).abs().mean())\n"
                "display(pred.tail())"
            ),
        ),
    )

    write(
        "04_especialista_PLS/03_interpretacao_resultados.ipynb",
        nb(
            md("# PLS — interpretação"),
            code(BOOT),
            code(
                "fi = pd.read_csv(require_file(config.RESULT_DIR / 'feature_importance_PLS_Regression.csv',\n"
                "                             'walk-forward PLS'))\n"
                "display(fi)\n"
                "display(Image(filename=str(config.FIG_DIR / 'previsao_PLS_Regression.png')))\n"
                "display(Image(filename=str(config.FIG_DIR / 'residuos_PLS_Regression.png')))"
            ),
        ),
    )

    write(
        "05_relatorio/relatorio.ipynb",
        nb(
            md(
                "# Relatório Base 2\n\n"
                "Gera/atualiza `outputs/relatorio_base2.html` a partir dos artefatos já existentes."
            ),
            code(BOOT),
            code(
                "from lib.report import write_report\n"
                "from lib.models import ForecastResult\n"
                "\n"
                "clean_report = load_json(require_file(config.DATA_DIR / 'cleaning_report.json', '02_limpeza'))\n"
                "stl_info = load_json(require_file(config.RESULT_DIR / 'stl_summary.json', '05_STL'))\n"
                "params = load_json(require_file(config.RESULT_DIR / 'best_params.json', 'tuning dos modelos'))\n"
                "mae_df = pd.read_csv(require_file(config.RESULT_DIR / 'mae_consolidado.csv', '01_MAE'))\n"
                "results = {}\n"
                "for model in mae_df['model']:\n"
                "    pred = pd.read_csv(config.RESULT_DIR / f'predictions_{model}.csv')\n"
                "    meta = load_json(config.RESULT_DIR / f'metrics_{model}.json')\n"
                "    fi_path = config.RESULT_DIR / f'feature_importance_{model}.csv'\n"
                "    fi = pd.read_csv(fi_path) if fi_path.exists() else None\n"
                "    results[model] = ForecastResult(model, meta['params'], pred, meta['mae'],\n"
                "                                    meta['runtime_sec'], meta['ljung_box_pvalue_lag24'], fi)\n"
                "path = write_report(clean_report, stl_info, params, mae_df, results)\n"
                "print('HTML:', path)\n"
                "display(mae_df)\n"
            ),
        ),
    )

    # atualiza README
    (GROUP / "README.md").write_text(
        """# Base 2 — Metro Interstate Traffic Volume

**Responsável:** Bruna Carvalho Cardoso

## Ideia

Você roda os notebooks **em ordem**. Cada um **grava** o que o próximo precisa em `outputs/`.

Abra primeiro: `00_ORDEM_DE_EXECUCAO.ipynb`.

## Fluxo

```
01_dados (limpeza → features → EDA → STL)
    ↓ outputs/data/*.csv
02_modelos/* (tuning → walk-forward → resíduos)   ← um modelo por vez
    ↓ outputs/results/predictions_*.csv, metrics_*.json
03_resultados (MAE, Ljung-Box, importância, comparação)
04_especialista_PLS + 05_relatorio
```

## Atalho no terminal (opcional)

```bash
# na raiz do repo
source .venv/bin/activate
python analyses/grupo2/run_pipeline.py
```

## Ver resultados

- `outputs/results/mae_consolidado.csv`
- `outputs/figures/`
- `outputs/relatorio_base2.html`
""",
        encoding="utf-8",
    )
    print("README atualizado")


if __name__ == "__main__":
    main()
