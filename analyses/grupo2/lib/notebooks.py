"""Gera os notebooks da pasta analyses/grupo2 a partir dos resultados."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import nbformat as nbf
import pandas as pd

import config


def _nb(*cells: dict) -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb["cells"] = list(cells)
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }
    return nb


def _md(text: str):
    return nbf.v4.new_markdown_cell(text)


def _code(text: str):
    return nbf.v4.new_code_cell(text)


def _write(path: Path, notebook) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        nbf.write(notebook, f)


def write_all_notebooks(
    clean_report: dict,
    split_info: dict,
    stl_info: dict,
    params: dict,
    mae_df: pd.DataFrame,
    results: dict[str, Any],
) -> None:
    base = config.NOTEBOOKS_DIR
    out_rel = config.NOTEBOOK_OUTPUTS_REL
    out_models = config.NOTEBOOK_OUTPUTS_REL_MODELS

    # ---- 01 dados ----
    _write(
        base / "01_dados/01_documentacao_bases.ipynb",
        _nb(
            _md(
                "# Documentação — Base 2 (Metro Interstate Traffic Volume)\n\n"
                f"**Responsável:** {config.OWNER}\n\n"
                "## Fonte e descrição\n"
                "- Dataset público UCI / Kaggle: volume horário de tráfego em uma via interestadual "
                "da região metropolitana de Minneapolis-St. Paul (MN, EUA), com sensores e meteorologia.\n"
                f"- Arquivo congelado: `bases/grupo2/Metro_Interstate_Traffic_Volume.csv`\n"
                f"- Período bruto: {clean_report['start']} → {clean_report['end']}\n"
                "- Frequência: **horária (1h)**\n"
                "- Variável-alvo: `traffic_volume` (veículos/hora)\n\n"
                "## Variáveis externas e disponibilidade\n"
                "| Variável | Uso | Disponibilidade |\n|---|---|---|\n"
                "| `holiday` → `is_holiday` | Calendário | Conhecido antecipadamente |\n"
                "| hora / dia / mês (cíclico) | Calendário | Conhecido antecipadamente |\n"
                "| `temp`, `rain_1h`, `snow_1h`, `clouds_all` | Clima | Observação realizada → **lag 1h** |\n"
                "| `weather_main` | Categórica | Não usada no modelo final (redundante com clima numérico) |\n"
            ),
            _code(
                "import json\n"
                f"print(json.dumps({json.dumps(clean_report, default=str)}, indent=2, ensure_ascii=False))"
            ),
        ),
    )

    _write(
        base / "01_dados/02_limpeza_preparacao.ipynb",
        _nb(
            _md(
                "# Limpeza e preparação — Base 2\n\n"
                "Decisões:\n"
                "1. Agregar timestamps duplicados (média numérica; feriado = max; weather = moda).\n"
                "2. Reindexar grade horária completa.\n"
                "3. Interpolar gaps curtos (≤6h) no alvo e no clima; ffill/bfill residual.\n"
            ),
            _code(
                "import pandas as pd\n"
                f"df = pd.read_csv('{out_rel}/data/clean_hourly.csv', parse_dates=['date_time'])\n"
                "display(df.head())\n"
                "print(df.shape)\n"
                "print(df.isna().sum())"
            ),
        ),
    )

    _write(
        base / "01_dados/03_feature_engineering.ipynb",
        _nb(
            _md(
                "# Feature Engineering — Base 2\n\n"
                "Features compartilhadas entre Random Forest e PLS:\n\n"
                + ", ".join(f"`{c}`" for c in config.FEATURE_COLS)
                + "\n\n"
                f"Split cronológico **{int(config.TRAIN_RATIO*100)}/{int((1-config.TRAIN_RATIO)*100)}**, "
                f"`random_state={config.RANDOM_STATE}`, horizonte={config.HORIZON}h."
            ),
            _code(
                "import json, pandas as pd\n"
                f"info = json.load(open('{out_rel}/data/split_info.json'))\n"
                f"df = pd.read_csv('{out_rel}/data/modeling_frame.csv', parse_dates=['date_time'])\n"
                "print(info)\n"
                "display(df.head())"
            ),
        ),
    )

    _write(
        base / "01_dados/04_analise_exploratoria.ipynb",
        _nb(
            _md("# Análise exploratória — Base 2\n\nFiguras em `outputs/figures/`."),
            _code(
                "from IPython.display import Image, display\n"
                f"for name in ['01_serie_alvo.png','02_externas.png','03_perfil_horario.png']:\n"
                f"    display(Image(filename=f'{out_rel}/figures/' + name))"
            ),
        ),
    )

    _write(
        base / "01_dados/05_STL_decomposicao.ipynb",
        _nb(
            _md(
                "# Decomposição STL — Base 2\n\n"
                f"Período sazonal m={config.SEASONAL_PERIOD}. "
                f"Força da sazonalidade = **{stl_info['seasonal_strength']:.3f}** "
                f"(amostra {stl_info['stl_sample_start']} → {stl_info['stl_sample_end']}).\n\n"
                "Interpretação: força próxima de 1 indica sazonalidade diária dominante "
                "(picos de pico/vale do tráfego urbano)."
            ),
            _code(
                "from IPython.display import Image, display\n"
                f"display(Image(filename='{out_rel}/figures/04_stl.png'))"
            ),
        ),
    )

    # ---- modelos ----
    for model in ["Holt_Winters", "PLS_Regression", "Random_Forest", "SARIMAX"]:
        p = params[model]
        res = results[model]
        folder = base / "02_modelos" / model
        _write(
            folder / "01_otimizacao_hiperparametros.ipynb",
            _nb(
                _md(f"# Otimização — {model}\n\nBusca apenas no bloco de treino (sem teste final)."),
                _code(f"import json\nprint(json.dumps({json.dumps(p, default=str)}, indent=2))"),
            ),
        )
        _write(
            folder / "02_walkforward_validacao.ipynb",
            _nb(
                _md(
                    f"# Walk-forward — {model}\n\n"
                    f"MAE fora da amostra = **{res.mae:.3f}** | "
                    f"runtime = {res.runtime_sec:.1f}s | "
                    f"refit a cada {config.REFIT_EVERY}h."
                ),
                _code(
                    "import pandas as pd\n"
                    f"pred = pd.read_csv('{out_models}/results/predictions_{model}.csv', parse_dates=['date_time'])\n"
                    "display(pred.head())\n"
                    "print('MAE', (pred.y_true-pred.y_pred).abs().mean())"
                ),
            ),
        )
        _write(
            folder / "03_previsoes_residuos.ipynb",
            _nb(
                _md(
                    f"# Previsões e resíduos — {model}\n\n"
                    f"Ljung-Box (lag 24) p-valor = **{res.ljung_box_pvalue:.4g}**"
                ),
                _code(
                    "from IPython.display import Image, display\n"
                    f"display(Image(filename='{out_models}/figures/previsao_{model}.png'))\n"
                    f"display(Image(filename='{out_models}/figures/residuos_{model}.png'))"
                ),
            ),
        )

    # ---- resultados ----
    _write(
        base / "03_resultados/01_MAE_consolidado.ipynb",
        _nb(
            _md("# MAE consolidado — Base 2"),
            _code(
                "import pandas as pd\n"
                f"df = pd.read_csv('{out_rel}/results/mae_consolidado.csv')\n"
                "display(df)"
            ),
        ),
    )
    _write(
        base / "03_resultados/02_analise_residuos_Ljung_Box.ipynb",
        _nb(
            _md("# Ljung-Box — Base 2"),
            _code(
                "import pandas as pd\n"
                f"df = pd.read_csv('{out_rel}/results/mae_consolidado.csv')\n"
                "display(df[['model','ljung_box_pvalue_lag24','mae']])"
            ),
        ),
    )
    _write(
        base / "03_resultados/03_importancia_features.ipynb",
        _nb(
            _md("# Importância das features — RF e PLS"),
            _code(
                "import pandas as pd\n"
                f"rf = pd.read_csv('{out_rel}/results/feature_importance_Random_Forest.csv')\n"
                f"pls = pd.read_csv('{out_rel}/results/feature_importance_PLS_Regression.csv')\n"
                "print('Random Forest'); display(rf.head(10))\n"
                "print('PLS (permutation / coef)'); display(pls.head(10))"
            ),
        ),
    )
    ranking = mae_df.to_string(index=False)
    _write(
        base / "03_resultados/04_comparacao_modelos.ipynb",
        _nb(
            _md(
                "# Comparação dos modelos — Base 2\n\n"
                f"```\n{ranking}\n```\n\n"
                f"Melhor modelo nesta base: **{mae_df.iloc[0]['model']}** "
                f"(MAE={mae_df.iloc[0]['mae']:.3f})."
            ),
            _code(
                "import pandas as pd\n"
                f"display(pd.read_csv('{out_rel}/results/mae_consolidado.csv'))"
            ),
        ),
    )

    # ---- especialista PLS ----
    _write(
        base / "04_especialista_PLS/01_estudo_conceitual_PLS.ipynb",
        _nb(
            _md(
                "# PLS Regression — estudo conceitual\n\n"
                "Partial Least Squares encontra componentes latentes que maximizam a "
                "covariância entre X e y. É útil com multicolinearidade (lags + calendário + clima).\n\n"
                "**Hipóteses/vantagens:** reduz dimensionalidade supervisionada; estável com "
                "features correlacionadas.\n\n"
                "**Limitações:** relação essencialmente linear nos componentes; exige padronização; "
                "número de componentes é hiperparâmetro crítico.\n\n"
                f"Configuração escolhida na Base 2: `{params['PLS_Regression']}`."
            )
        ),
    )
    _write(
        base / "04_especialista_PLS/02_implementacao_PLS.ipynb",
        _nb(
            _md("# Implementação PLS — Base 2"),
            _code(
                "import json, pandas as pd\n"
                f"print(json.load(open('{out_rel}/results/best_params.json'))['PLS_Regression'])\n"
                f"pred = pd.read_csv('{out_rel}/results/predictions_PLS_Regression.csv')\n"
                "print('MAE', (pred.y_true-pred.y_pred).abs().mean())"
            ),
        ),
    )
    _write(
        base / "04_especialista_PLS/03_interpretacao_resultados.ipynb",
        _nb(
            _md(
                "# Interpretação PLS — Base 2\n\n"
                "Importância via permutação (aumento de MAE ao embaralhar a feature) "
                "e magnitudes de coeficientes nos componentes."
            ),
            _code(
                "import pandas as pd\n"
                f"display(pd.read_csv('{out_rel}/results/feature_importance_PLS_Regression.csv'))"
            ),
        ),
    )

    # ---- relatório ----
    _write(
        base / "05_relatorio/relatorio.ipynb",
        _nb(
            _md(
                f"# Relatório Base 2 — {config.OWNER}\n\n"
                "## Resumo\n"
                f"- Série horária regularizada ({clean_report['n_regular_hours']} horas).\n"
                f"- Força sazonal STL ≈ {stl_info['seasonal_strength']:.3f}.\n"
                f"- Melhor modelo: **{mae_df.iloc[0]['model']}** (MAE={mae_df.iloc[0]['mae']:.3f}).\n"
                f"- Protocolo: split {int(config.TRAIN_RATIO*100)}/{int((1-config.TRAIN_RATIO)*100)}, "
                f"random_state={config.RANDOM_STATE}, horizonte 1h, walk-forward com refit "
                f"a cada {config.REFIT_EVERY}h.\n\n"
                "Abra também `outputs/relatorio_base2.html`."
            ),
            _code(
                "import pandas as pd\n"
                f"display(pd.read_csv('{out_rel}/results/mae_consolidado.csv'))"
            ),
        ),
    )
