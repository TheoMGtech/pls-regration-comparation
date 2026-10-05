"""Regrava os notebooks de leitura da Base 3 com o protocolo final e executa as células."""
from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


def repository_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / "bases" / "grupo3").exists():
            return candidate
    raise FileNotFoundError("Raiz do repositório não encontrada.")


def notebook(cells: list) -> nbformat.NotebookNode:
    book = new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
    )
    return book


def execute(path: Path, book: nbformat.NotebookNode, root: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(nbformat.writes(book), encoding="utf-8")
    client = NotebookClient(
        book,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(root)}},
    )
    client.execute()
    path.write_text(nbformat.writes(book), encoding="utf-8")
    print(path.relative_to(root), flush=True)


ROOT_CELL = '''from pathlib import Path
import json
import numpy as np
import pandas as pd

current = Path.cwd()
while current != current.parent and not (current / "bases" / "grupo3").exists():
    current = current.parent
ROOT = current
BASE = ROOT / "analyses" / "grupo3"
OUT = BASE / "03_resultados" / "outputs"
print(ROOT)
'''


def build() -> None:
    root = repository_root()
    base = root / "analyses" / "grupo3"
    jobs = []

    jobs.append((
        base / "04_especialista_PLS" / "01_estudo_conceitual_PLS.ipynb",
        notebook([
            new_markdown_cell(
                """# PLS — estudo conceitual

Random Forest e PLS desta base usam os mesmos 17 preditores. Vários deles são defasagens e médias do próprio PM2.5, então andam juntos. Uma regressão comum reparte mal esse crédito: coeficientes vizinhos ficam instáveis e podem sair com sinais opostos.

O PLS monta poucos componentes. Cada componente é uma combinação dos preditores escolhida para acompanhar o PM2.5 da hora seguinte. A regressão é feita nesses componentes, não nas 17 colunas cruas.

| | OLS | componente principal | PLS |
|---|---|---|---|
| Colinearidade | coeficientes instáveis | reduz a dimensão de X | reduz a dimensão de X |
| Olha o alvo ao construir o eixo? | — | não | sim |
| O que a grade escolhe | — | variância de X | covariância entre X e y |

A matriz exploratória de 671 colunas continua em `01_dados`. Ela não é a matriz deste ajuste."""
            ),
            new_code_cell(
                ROOT_CELL
                + '''
frame = pd.read_csv(BASE / "01_dados" / "outputs" / "features_modelagem_base3.csv", parse_dates=["timestamp"])
features = [
    "pm25_t", "pm25_t_1", "pm25_t_2", "pm25_t_23", "pm25_roll_mean_3", "pm25_roll_mean_24",
    "local_PM10", "local_CO", "local_TEMP", "local_WSPM", "local_DEWP",
    "Changping_PM2.5", "Wanliu_PM2.5",
    "target_hour_sin", "target_hour_cos", "target_dow_sin", "target_dow_cos",
]
print(frame["split"].value_counts().to_string())
print("preditores", len(features), "linhas", len(frame))
'''
            ),
            new_markdown_cell(
                """## Colinearidade do histórico de PM2.5

As seis colunas abaixo são funções do mesmo PM2.5. A correlação alta é esperada e é o motivo de não ler um coeficiente isolado como efeito separado."""
            ),
            new_code_cell(
                '''history = ["pm25_t", "pm25_t_1", "pm25_t_2", "pm25_t_23", "pm25_roll_mean_3", "pm25_roll_mean_24"]
corr = frame.loc[frame["split"] == "train_interno", history].corr().round(3)
print(corr.to_string())
'''
            ),
            new_markdown_cell(
                """## Componentes principais e número de componentes do PLS

O componente principal resume X sem olhar y. O laço abaixo ajusta o PLS no treino interno e mede o R² na validação, com preditores padronizados. Esse R² é um retrato de um único ajuste. A escolha usada no teste é o MAE do walk-forward diário, gravado no notebook de implementação."""
            ),
            new_code_cell(
                '''from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler

train = frame[frame["split"] == "train_interno"]
valid = frame[frame["split"] == "validacao_interna"]
scaler = StandardScaler().fit(train[features])
x_train = scaler.transform(train[features])
x_valid = scaler.transform(valid[features])
y_train = train["y"].to_numpy(float)
y_valid = valid["y"].to_numpy(float)

pca = PCA().fit(x_train)
print("variância acumulada dos componentes principais")
print(np.cumsum(pca.explained_variance_ratio_).round(3))

rows = []
for n_components in (1, 2, 4, 8, 12, 14, 16):
    model = PLSRegression(n_components=n_components, scale=True, max_iter=500)
    model.fit(x_train, y_train)
    rows.append({
        "n_components": n_components,
        "R2_treino": r2_score(y_train, model.predict(x_train)),
        "R2_validacao": r2_score(y_valid, model.predict(x_valid)),
    })
comparison = pd.DataFrame(rows)
comparison.to_csv(BASE / "04_especialista_PLS" / "outputs" / "r2_um_ajuste.csv", index=False)
print(comparison.round(4).to_string(index=False))
'''
            ),
        ]),
    ))

    jobs.append((
        base / "04_especialista_PLS" / "02_implementacao_PLS.ipynb",
        notebook([
            new_markdown_cell(
                """# PLS — implementação na Base 3

O código do walk-forward está em `02_modelos/protocolo_final.py`. Este notebook lê a grade que já foi executada e mostra as decisões que ficaram fixas no teste.

- Alvo: PM2.5 da hora seguinte.
- Preditores: os mesmos 17 do Random Forest, conhecidos na origem.
- Padronização: `scale=True` dentro de cada ajuste.
- Grade: 2, 4, 8, 12, 14 e 16 componentes, escolhida pelo MAE da validação interna. Dezesseis é o maior número testado, porque há 17 preditores.
- Reajuste: uma vez por dia. As horas do dia entram na previsão, mas não no ajuste daquele dia.
- Previsão negativa: truncada em zero.
- O teste não entra na escolha do número de componentes."""
            ),
            new_code_cell(
                ROOT_CELL
                + '''
tuning = pd.read_csv(BASE / "02_modelos" / "PLS_Regression" / "results" / "tuning_results.csv")
selected = json.loads((BASE / "02_modelos" / "PLS_Regression" / "results" / "selected_config.json").read_text())
meta = json.loads((BASE / "02_modelos" / "PLS_Regression" / "results" / "walkforward_metadata.json").read_text())
print(tuning.to_string(index=False))
print("configuração escolhida", selected["config"])
print("MAE no teste", round(meta["mae_test"], 4), "horas", meta["n_predictions"], "reajuste", meta["refit_every"])
'''
            ),
            new_markdown_cell(
                """## Um ajuste, para ver o objeto

O bloco abaixo repete um ajuste só no treino interno, com o número de componentes vencedor. Serve para inspecionar pesos e cargas. As previsões do teste continuam sendo as do walk-forward diário, já gravadas em `walkforward_predictions.csv`."""
            ),
            new_code_cell(
                '''from sklearn.cross_decomposition import PLSRegression

frame = pd.read_csv(BASE / "01_dados" / "outputs" / "features_modelagem_base3.csv")
features = selected["features"]
train = frame[frame["split"] == "train_interno"]
model = PLSRegression(n_components=int(selected["config"]["n_components"]), scale=True, max_iter=500)
model.fit(train[features], train["y"])
print("x_weights_", model.x_weights_.shape)
print("y_loadings_", np.asarray(model.y_loadings_).ravel().round(4))
predictions = pd.read_csv(BASE / "02_modelos" / "PLS_Regression" / "results" / "walkforward_predictions.csv", parse_dates=["forecast_origin"])
print(predictions[["forecast_origin", "y_true", "y_pred", "residual"]].head(3).to_string(index=False))
print("primeira origem", predictions["forecast_origin"].iloc[0], "última", predictions["forecast_origin"].iloc[-1])
'''
            ),
        ]),
    ))

    jobs.append((
        base / "04_especialista_PLS" / "03_interpretacao_resultados.ipynb",
        notebook([
            new_markdown_cell(
                """# PLS — interpretação

O VIP vem de um único `PLSRegression(scale=True)` no treino interno, com o número de componentes escolhido na validação. Ele não é a média dos ajustes diários. Preditores de PM2.5 muito correlacionados dividem o crédito: um VIP menor não significa que a coluna seja inútil sozinha.

VIP acima de 1 indica preditor mais útil que a média, nesse ajuste, para acompanhar o PM2.5 da hora seguinte. As estações externas entram com a medição da origem, nunca com o valor da hora prevista."""
            ),
            new_code_cell(
                ROOT_CELL
                + '''
vip = pd.read_csv(OUT / "pls_vip.csv")
notes = pd.read_csv(OUT / "residuos_interpretacao.csv")
ljung = pd.read_csv(OUT / "ljung_box_results.csv")
print(vip.to_string(index=False))
print()
print(notes.loc[notes["model"] == "PLS_Regression", "interpretacao"].iloc[0])
print(ljung.loc[ljung["model"] == "PLS_Regression"].to_string(index=False))
'''
            ),
            new_markdown_cell(
                """## Como ler o erro

O resíduo é observado menos previsão. Média positiva significa que o modelo ficou abaixo do PM2.5 realizado. O desvio-padrão do resíduo mede a dispersão. O Ljung-Box no lag 24 pergunta se, um dia depois, o erro ainda carrega o erro anterior. Rejeitar a hipótese nula não muda o MAE; mostra que o erro ainda tem memória."""
            ),
        ]),
    ))

    resultados = [
        (
            "01_MAE_consolidado.ipynb",
            "# MAE no teste\n\nAs quatro linhas usam as mesmas origens, o mesmo horizonte e o mesmo período. O MAE não deve ser somado ao de outra base.",
            '''mae = pd.read_csv(OUT / "mae_consolidado.csv")
fair = pd.read_csv(OUT / "mae_mesmas_origens.csv")
print(mae.to_string(index=False))
print(fair.to_string(index=False))
''',
        ),
        (
            "05_acuracia_modelos.ipynb",
            "# Outras métricas no mesmo teste\n\nO viés é a média de observado menos previsão.",
            '''accuracy = pd.read_csv(OUT / "accuracy_metrics.csv")
print(accuracy.to_string(index=False))
''',
        ),
        (
            "04_comparacao_modelos.ipynb",
            "# Comparação\n\nA ordem segue o MAE. A configuração é a que venceu a validação interna e ficou fixa no teste.",
            '''summary = json.loads((BASE / "02_modelos" / "results" / "protocolo_final.json").read_text())
print("minutos", summary["runtime_minutes"], "origens", summary["n_test_origins"])
for name, item in summary["models"].items():
    print(name, round(item["mae"], 4), item["config"], "min", item["minutes"])
''',
        ),
        (
            "02_analise_residuos_Ljung_Box.ipynb",
            "# Resíduos\n\nA série, a autocorrelação e o Ljung-Box estão nos arquivos abaixo. A última coluna é a leitura de viés, dispersão e autocorrelação no lag 24.",
            '''notes = pd.read_csv(OUT / "residuos_interpretacao.csv")
ljung = pd.read_csv(OUT / "ljung_box_results.csv")
print(notes.to_string(index=False))
print(ljung.to_string(index=False))
print("figura", OUT / "acf_residuos.png")
print("série", OUT / "serie_residuos.png")
''',
        ),
        (
            "03_importancia_features.ipynb",
            "# Importância\n\nRandom Forest: redução média de impureza de uma floresta ajustada no treino interno. PLS: VIP do mesmo corte, com padronização. Os dois retratos são de um ajuste só, não a média do walk-forward diário. Lags de PM2.5 dividem crédito entre si.",
            '''rf = pd.read_csv(OUT / "rf_feature_importance.csv")
vip = pd.read_csv(OUT / "pls_vip.csv")
coef = pd.read_csv(OUT / "pls_feature_importance.csv")
print(rf.to_string(index=False))
print(vip.to_string(index=False))
print(coef.to_string(index=False))
''',
        ),
    ]
    for filename, title, code in resultados:
        jobs.append((
            base / "03_resultados" / filename,
            notebook([
                new_markdown_cell(title),
                new_code_cell(ROOT_CELL + "\n" + code),
            ]),
        ))

    jobs.append((
        base / "05_relatorio" / "relatorio.ipynb",
        notebook([
            new_markdown_cell(
                """# Relatório da Base 3

O relatório paginado está em `relatorio_base3.html` e `relatorio_base3.pdf`, nesta pasta. Os dois arquivos têm o mesmo conteúdo: resumo, base, STL, walk-forward, ajuste, MAE, resíduos, importância, leitura do PLS, conclusões e referências.

O repositório não registra os nomes dos integrantes. Este notebook só reapresenta as tabelas que sustentam o relatório."""
            ),
            new_code_cell(
                ROOT_CELL
                + '''
print(pd.read_csv(OUT / "mae_consolidado.csv").to_string(index=False))
print(pd.read_csv(OUT / "residuos_interpretacao.csv")[["model", "interpretacao"]].to_string(index=False))
print("HTML", BASE / "05_relatorio" / "relatorio_base3.html")
print("PDF", BASE / "05_relatorio" / "relatorio_base3.pdf")
'''
            ),
        ]),
    ))

    chapters = {
        "Holt_Winters": "Holt-Winters é a referência univariada, reestimada em cada origem numa janela de 21 dias. A grade inclui sazonalidade de 24 horas. A validação escolhe a configuração e o teste usa só essa.",
        "SARIMAX": "O SARIMAX reestima os parâmetros uma vez por dia, com exógenas conhecidas na origem. A escolha da previsão é o MAE da validação. AIC e BIC estão em `results/aic_bic.csv` e não decidem a ordem.",
        "Random_Forest": "A floresta usa os 17 preditores de `features_modelagem_base3.csv`. A grade varia número de árvores, profundidade, divisão mínima, folha mínima e amostragem de colunas. O teste usa a configuração de menor MAE na validação.",
        "PLS_Regression": "O PLS usa os mesmos 17 preditores, com padronização em cada ajuste. A grade vai de 2 a 16 componentes. Dezesseis é o maior número testado, porque há 17 preditores.",
    }
    for folder, intro in chapters.items():
        model_dir = base / "02_modelos" / folder
        jobs.append((
            model_dir / "01_otimizacao_hiperparametros.ipynb",
            notebook([
                new_markdown_cell(f"# {folder.replace('_', ' ')}\n\n{intro}"),
                new_code_cell(
                    ROOT_CELL
                    + f'''
tuning = pd.read_csv(BASE / "02_modelos" / "{folder}" / "results" / "tuning_results.csv")
selected = json.loads((BASE / "02_modelos" / "{folder}" / "results" / "selected_config.json").read_text())
print(tuning.to_string(index=False))
print("escolhida", selected["config"])
'''
                ),
            ]),
        ))
        jobs.append((
            model_dir / "02_walkforward_validacao.ipynb",
            notebook([
                new_markdown_cell(
                    f"# Previsões de teste — {folder.replace('_', ' ')}\n\nAs horas são as mesmas dos outros três modelos. O arquivo completo está em `results/walkforward_predictions.csv`."
                ),
                new_code_cell(
                    ROOT_CELL
                    + f'''
meta = json.loads((BASE / "02_modelos" / "{folder}" / "results" / "walkforward_metadata.json").read_text())
predictions = pd.read_csv(BASE / "02_modelos" / "{folder}" / "results" / "walkforward_predictions.csv", parse_dates=["forecast_origin"])
print("MAE", round(meta["mae_test"], 4), "horas", meta["n_predictions"], "reajuste", meta["refit_every"])
print(predictions[["forecast_origin", "y_true", "y_pred", "residual"]].head(3).to_string(index=False))
print("primeira", predictions["forecast_origin"].iloc[0], "última", predictions["forecast_origin"].iloc[-1])
'''
                ),
            ]),
        ))
        jobs.append((
            model_dir / "03_previsoes_residuos.ipynb",
            notebook([
                new_markdown_cell(
                    f"# Resíduos — {folder.replace('_', ' ')}\n\nO resíduo é observado menos previsão. A leitura conjunta dos quatro modelos está em `03_resultados`."
                ),
                new_code_cell(
                    ROOT_CELL
                    + f'''
summary = pd.read_csv(BASE / "02_modelos" / "{folder}" / "results" / "residual_summary.csv")
note = pd.read_csv(OUT / "residuos_interpretacao.csv")
print(summary.to_string(index=False))
print(note.loc[note["model"] == "{folder}", "interpretacao"].iloc[0])
'''
                ),
            ]),
        ))

    jobs.append((
        base / "02_modelos" / "RAPIDO_rf_sarimax.ipynb",
        notebook([
            new_markdown_cell(
                """# Protocolo final

Este arquivo substitui o atalho da execução anterior. Os quatro modelos estão em `protocolo_final.py` e o relatório está em `05_relatorio/relatorio_base3.html`."""
            ),
            new_code_cell(
                ROOT_CELL
                + '''
summary = json.loads((BASE / "02_modelos" / "results" / "protocolo_final.json").read_text())
print("origens", summary["n_test_origins"])
for name, item in summary["models"].items():
    print(name, round(item["mae"], 4), item["config"])
'''
            ),
        ]),
    ))
    for folder in ("Random_Forest", "SARIMAX"):
        jobs.append((
            base / "02_modelos" / folder / "fast_pipeline.ipynb",
            notebook([
                new_markdown_cell(
                    f"# {folder.replace('_', ' ')}\n\nA execução vigente é `run_protocolo_final.py`. Os notebooks `01`, `02` e `03` desta pasta leem esse resultado."
                ),
                new_code_cell(
                    ROOT_CELL
                    + f'''
meta = json.loads((BASE / "02_modelos" / "{folder}" / "results" / "walkforward_metadata.json").read_text())
print(meta["model"], round(meta["mae_test"], 4), meta["n_predictions"], meta["config"])
'''
                ),
            ]),
        ))

    outputs = base / "04_especialista_PLS" / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    for path, book in jobs:
        execute(path, book, root)


if __name__ == "__main__":
    build()
