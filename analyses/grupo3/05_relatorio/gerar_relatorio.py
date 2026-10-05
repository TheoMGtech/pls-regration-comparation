"""Monta o relatório HTML da Base 3 a partir dos arquivos do protocolo final.

Uso, na raiz do projeto:

    python analyses/grupo3/05_relatorio/gerar_relatorio.py
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def repository_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / "bases" / "grupo3").exists():
            return candidate
    raise FileNotFoundError("Raiz do repositório não encontrada.")


def br(value: float, digits: int = 2) -> str:
    text = f"{value:,.{digits}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def table(frame: pd.DataFrame) -> str:
    header = "".join(f"<th>{column}</th>" for column in frame.columns)
    body = []
    for _, row in frame.iterrows():
        cells = "".join(f"<td>{row[column]}</td>" for column in frame.columns)
        body.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def image_tag(path: Path, alt: str) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img alt="{alt}" src="data:image/png;base64,{encoded}"/>'


def residual_series(combined: pd.DataFrame, path: Path) -> None:
    figure, axes = plt.subplots(4, 1, figsize=(11, 9), sharex=True, constrained_layout=True)
    for axis, (model, group) in zip(axes, combined.groupby("model", sort=False)):
        group = group.sort_values("forecast_origin")
        axis.plot(pd.to_datetime(group["forecast_origin"]), group["residual"], color="#1f4e79", linewidth=0.4)
        axis.axhline(0, color="#888888", linewidth=0.6)
        axis.set_ylabel("µg/m³")
        axis.set_title(model.replace("_", " "))
    axes[-1].set_xlabel("Origem da previsão")
    figure.savefig(path, dpi=130)
    plt.close(figure)


def random_forest_importance(root: Path, selected: dict) -> pd.DataFrame:
    frame = pd.read_csv(
        root / "analyses" / "grupo3" / "01_dados" / "outputs" / "features_modelagem_base3.csv",
        parse_dates=["timestamp"],
    )
    train = frame[frame["split"] == "train_interno"]
    features = selected["features"]
    model = RandomForestRegressor(random_state=42, n_jobs=-1, bootstrap=True, **selected["config"])
    model.fit(train[features].to_numpy(dtype=float), train["y"].to_numpy(dtype=float))
    table_out = pd.DataFrame({"feature": features, "importance": model.feature_importances_})
    table_out = table_out.sort_values("importance", ascending=False).reset_index(drop=True)
    output = root / "analyses" / "grupo3" / "03_resultados" / "outputs" / "rf_feature_importance.csv"
    table_out.to_csv(output, index=False)
    return table_out


def config_label(raw: str) -> str:
    payload = json.loads(raw)
    return ", ".join(f"{key}={value}" for key, value in payload.items())


def build() -> Path:
    root = repository_root()
    base = root / "analyses" / "grupo3"
    out = base / "03_resultados" / "outputs"
    models = base / "02_modelos"
    summary = json.loads((models / "results" / "protocolo_final.json").read_text(encoding="utf-8"))
    protocol = json.loads((models / "results" / "validation_protocol.json").read_text(encoding="utf-8"))
    mae = pd.read_csv(out / "mae_consolidado.csv")
    accuracy = pd.read_csv(out / "accuracy_metrics.csv")
    ljung = pd.read_csv(out / "ljung_box_results.csv")
    notes = pd.read_csv(out / "residuos_interpretacao.csv")
    vip = pd.read_csv(out / "pls_vip.csv")
    aic = pd.read_csv(models / "SARIMAX" / "results" / "aic_bic.csv")
    combined = pd.read_csv(out / "combined_predictions.csv", parse_dates=["forecast_origin"])
    series_path = out / "serie_residuos.png"
    residual_series(combined, series_path)

    selected_rf = json.loads((models / "Random_Forest" / "results" / "selected_config.json").read_text(encoding="utf-8"))
    importance = random_forest_importance(root, selected_rf)
    tuning_blocks = []
    metadata_rows = []
    for name in ("Holt_Winters", "SARIMAX", "Random_Forest", "PLS_Regression"):
        tuning = pd.read_csv(models / name / "results" / "tuning_results.csv")
        tuning.insert(0, "modelo", name.replace("_", " "))
        tuning["parameters"] = tuning["parameters"].map(config_label)
        keep = [column for column in ("modelo", "parameters", "MAE_validation", "n_predictions", "seconds", "fallbacks") if column in tuning.columns]
        tuning_blocks.append(tuning[keep])
        meta = json.loads((models / name / "results" / "walkforward_metadata.json").read_text(encoding="utf-8"))
        metadata_rows.append(meta)

    tuning_all = pd.concat(tuning_blocks, ignore_index=True)
    for column in ("MAE_validation",):
        tuning_all[column] = tuning_all[column].map(lambda value: br(float(value), 4))
    mae_view = mae.copy()
    mae_view["MAE_test"] = mae_view["MAE_test"].map(lambda value: br(float(value), 4))
    mae_view["config"] = mae_view["config"].map(config_label)
    accuracy_view = accuracy.copy()
    for column in ("MAE", "RMSE", "MAPE_pct", "R2", "bias"):
        digits = 4 if column != "MAPE_pct" else 2
        accuracy_view[column] = accuracy_view[column].map(lambda value, digits=digits: br(float(value), digits))
    ljung_view = ljung.copy()
    ljung_view["lb_stat"] = ljung_view["lb_stat"].map(lambda value: br(float(value), 1))
    ljung_view["lb_pvalue"] = ljung_view["lb_pvalue"].map(lambda value: f"{float(value):.3g}")
    aic_view = aic.copy()
    for column in ("aic", "bic"):
        aic_view[column] = aic_view[column].map(lambda value: br(float(value), 1))
    vip_view = vip.copy()
    vip_view["vip"] = vip_view["vip"].map(lambda value: br(float(value), 3))
    coefficients = pd.read_csv(out / "pls_feature_importance.csv")
    coefficient_view = coefficients.copy()
    for column in ("standardized_coefficient", "abs_coefficient"):
        coefficient_view[column] = coefficient_view[column].map(lambda value: br(float(value), 3))
    importance_view = importance.copy()
    importance_view["importance"] = importance_view["importance"].map(lambda value: br(float(value), 3))
    notes_view = notes[["model", "bias", "residual_std", "interpretacao"]].copy()
    notes_view["bias"] = notes_view["bias"].map(lambda value: br(float(value), 3))
    notes_view["residual_std"] = notes_view["residual_std"].map(lambda value: br(float(value), 3))

    labels = {
        "Holt_Winters": "Holt-Winters",
        "Random_Forest": "Random Forest",
        "PLS_Regression": "PLS",
        "SARIMAX": "SARIMAX",
    }
    winner = mae.sort_values("MAE_test").iloc[0]
    winner_name = labels.get(str(winner["model"]), str(winner["model"]))
    n_origins = int(summary["n_test_origins"])
    runtime = br(float(summary["runtime_minutes"]), 2)
    pls_tuning = pd.read_csv(models / "PLS_Regression" / "results" / "tuning_results.csv")
    pls_components = [json.loads(raw)["n_components"] for raw in pls_tuning["parameters"]]
    best_components = int(json.loads(pls_tuning.sort_values("MAE_validation").iloc[0]["parameters"])["n_components"])
    if best_components == max(pls_components):
        ordered = pls_tuning.copy()
        ordered["n_components"] = pls_components
        earlier = ordered.loc[ordered["n_components"] < best_components, "MAE_validation"].min()
        best_validation = float(ordered.loc[ordered["n_components"] == best_components, "MAE_validation"].iloc[0])
        movement = "ainda melhorava" if best_validation < earlier else "não melhorou"
        pls_note = (
            f"O menor MAE da validação ficou em {best_components} componentes, "
            f"o maior número da grade. Nesse último degrau a validação {movement} "
            "em relação aos números menores, então este é o melhor ponto entre os que foram testados."
        )
    else:
        pls_note = f"A validação escolheu {best_components} componentes, no interior da grade."
    fallback_bits = [
        f"{labels.get(item['model'], item['model'])} recorreu à persistência em {int(item.get('test_fallbacks', 0))} horas"
        for item in metadata_rows
        if int(item.get("test_fallbacks", 0))
    ]
    fallback_note = (
        ". ".join(fallback_bits) + "."
        if fallback_bits
        else "Nenhum modelo precisou da persistência de reserva no teste."
    )
    sarimax_order = tuple(summary["models"]["SARIMAX"]["config"]["order"])
    sarimax_seasonal = tuple(summary["models"]["SARIMAX"]["config"]["seasonal_order"])
    component_list = ", ".join(str(value) for value in sorted(pls_components))
    rf_config = summary["models"]["Random_Forest"]["config"]
    rf_sentence = (
        f"A floresta escolhida tem {rf_config['n_estimators']} árvores, profundidade {rf_config['max_depth']}, "
        f"folha mínima {rf_config['min_samples_leaf']}, divisão mínima {rf_config.get('min_samples_split', 2)} "
        f"e max_features {rf_config['max_features']}, com random_state 42."
    )
    runtime_note = summary.get("runtime_note", "")
    checksum_path = root / "bases" / "grupo3" / "SHA256SUMS.txt"
    checksum_rows = []
    if checksum_path.exists():
        for line in checksum_path.read_text(encoding="utf-8").splitlines():
            digest, filename = line.split(maxsplit=1)
            checksum_rows.append({"arquivo": filename, "sha256": digest})
    checksum_table = table(pd.DataFrame(checksum_rows)) if checksum_rows else "<p>Checksum ainda não registrado.</p>"
    hw_meta = next(item for item in metadata_rows if item["model"] == "Holt_Winters")
    hw_config = hw_meta["config"]
    seasonal_hw = hw_config.get("seasonal")
    if seasonal_hw:
        hw_sentence = (
            f"A validação escolheu Holt-Winters com tendência {hw_config.get('trend')} "
            f"e sazonalidade {seasonal_hw}."
        )
    else:
        hw_sentence = (
            "A validação escolheu suavização exponencial simples, sem tendência e sem sazonalidade. "
            "As versões com sazonalidade de 24 horas tiveram erro bem maior na validação, "
            "no mesmo sentido da força sazonal baixa medida no STL."
        )

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<title>Base 3 — PM2.5 em Aotizhongxin</title>
<style>
  @page {{ size: A4; margin: 16mm 14mm 16mm 14mm; }}
  body {{ font-family: "Iowan Old Style", Palatino, Georgia, serif; color: #1c1c1c; line-height: 1.45; margin: 0; }}
  main {{ max-width: 920px; margin: 0 auto; padding: 24px 18px 48px; }}
  h1 {{ font-size: 28px; line-height: 1.15; margin-bottom: 0.2em; }}
  h2 {{ font-size: 20px; margin-top: 0; break-after: avoid; }}
  h3 {{ font-size: 16px; break-after: avoid; }}
  section {{ break-after: page; }}
  section:last-child {{ break-after: auto; }}
  p, li {{ font-size: 14px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0 18px; font-size: 12px; font-family: "Source Sans 3", "Segoe UI", sans-serif; }}
  th, td {{ border-bottom: 1px solid #d5d5d5; text-align: left; padding: 5px 6px; vertical-align: top; }}
  th {{ background: #f3f6f8; }}
  img {{ width: 100%; height: auto; }}
  .lead {{ font-size: 16px; }}
  .meta {{ color: #444; font-size: 13px; }}
</style>
</head>
<body>
<main>
<section>
<h1>Base 3 — PM2.5 horário em Aotizhongxin</h1>
<p class="meta">Grupo 5 · horizonte de 1 hora · protocolo único para SARIMAX, Holt-Winters, Random Forest e PLS</p>
<h2>Resumo</h2>
<p class="lead">Os quatro modelos previram o PM2.5 da hora seguinte nas mesmas {n_origins} origens do teste, de 16 de maio de 2016 a 28 de fevereiro de 2017. O menor MAE foi {br(float(winner['MAE_test']), 4)} µg/m³, do {winner_name}. A soma dos tempos dos quatro modelos é {runtime} minutos.</p>
<p>{runtime_note}</p>
<p>{hw_sentence} O SARIMAX comparou ordens sazonais e não sazonais por AIC e BIC no fim do treino e, para a previsão, ficou com a ordem de menor MAE na validação. Random Forest e PLS usaram a mesma matriz de 17 preditores, sem a meteorologia de Guanyuan.</p>
</section>

<section>
<h2>Participantes e escopo</h2>
<p>Este relatório cobre somente a Base 3. O repositório não registra os nomes dos integrantes. As outras quatro bases ficam fora desta entrega.</p>
<p>A fonte é o conjunto Beijing Multi-Site Air-Quality Data, estação Aotizhongxin, de 1º de março de 2013 a 28 de fevereiro de 2017, em frequência horária. O alvo é o PM2.5 em µg/m³. As estações externas usadas na previsão são Changping e Wanliu.</p>
</section>

<section>
<h2>Base e preparo</h2>
<p>A série preparada tem 35.064 horas. Havia 925 valores ausentes de PM2.5; eles foram preservados no alvo. Os preditores receberam preenchimento para a frente, só com o passado. Não houve preenchimento para trás nem interpolação na base de modelagem. A interpolação usada no STL ficou restrita à cópia da decomposição.</p>
<p>A matriz exploratória de 671 colunas permanece em <code>features_base3.csv</code>. A modelagem de Random Forest e PLS usa <code>features_modelagem_base3.csv</code>, com {protocol['rows_by_split']['train_interno']} horas de treino, {protocol['rows_by_split']['validacao_interna']} de validação e {protocol['rows_by_split']['test_final']} de teste antes do alinhamento final das origens. Na previsão de PM2.5(t+1), as medições entram com o valor conhecido em t. O calendário é o da hora prevista, porque a hora e o dia da semana já são conhecidos na origem.</p>
<p>DEWP, PRES, RAIN e WSPM de Guanyuan repetem a estação local nos arquivos congelados. Essa meteorologia foi excluída. O PM2.5 de Guanyuan é distinto, mas não entrou na matriz reduzida.</p>
<h3>Preditores compartilhados</h3>
{table(pd.DataFrame({"preditor": protocol["shared_features"], "disponível em": ["t+1, já conhecido" if name.startswith("target_") else "origem t" for name in protocol["shared_features"]]}))}
</section>

<section>
<h2>Decomposição STL</h2>
<p>O STL principal usa período de 24 horas. A força sazonal foi 0,013 e a força de tendência foi 0,287. A sazonalidade diária explica pouco da variância do PM2.5 nesta estação. Por isso a busca sazonal do SARIMAX e a grade do Holt-Winters foram mantidas, mas a escolha final obedece ao MAE da validação, não à presença do termo sazonal.</p>
</section>

<section>
<h2>Protocolo walk-forward</h2>
<p>O horizonte é de 1 hora. O treino interno vai até 2015-09-25 06:00. A validação interna vai até 2016-05-16 04:00. O teste começa em 2016-05-16 05:00. Nenhum hiperparâmetro foi escolhido no teste.</p>
<p>Holt-Winters é reestimado em toda origem, numa janela de 21 dias do PM2.5. Se a janela ainda tem buraco depois do preenchimento causal de até 24 horas, o ajuste usa só o trecho contínuo após o último buraco. Random Forest, PLS e SARIMAX reestimam os parâmetros uma vez por dia. Dentro do dia, cada hora usa a informação já observada até aquela origem, com os parâmetros do dia congelados. No SARIMAX isso é um <code>append</code> sem novo ajuste. No Random Forest e no PLS, os preditores da hora entram na previsão, mas o ajuste não vê as horas daquele dia.</p>
<p>Previsões negativas são truncadas em zero. Se um ajuste falha, a hora recebe a persistência do último PM2.5 observado e a falha é contada. {fallback_note} Depois da geração, as quatro séries ficam restritas à interseção das origens. Nesta execução, essa interseção tem {n_origins} horas.</p>
</section>

<section>
<h2>Modelos e ajuste</h2>
<h3>Holt-Winters</h3>
<p>{hw_sentence} A referência é univariada: não usa estação externa nem calendário como regressor.</p>
<h3>SARIMAX</h3>
<p>AIC e BIC foram calculados uma vez, nos últimos 14 dias de treino até 2015-09-25 06:00. As ordens sazonais tiveram AIC menor. A escolha da previsão, porém, é o MAE da validação, na mesma grade. As exógenas são o calendário da hora e a defasagem de 1 hora de PM10, temperatura, velocidade do vento e PM2.5 de Changping. Cada ajuste diário usa os últimos 14 dias.</p>
{table(aic_view)}
<h3>Random Forest e PLS</h3>
<p>Os dois modelos compartilham os 17 preditores. O PLS padroniza os preditores em cada ajuste (<code>scale=True</code>). {rf_sentence} A grade abaixo é a validação interna. {pls_note}</p>
{table(tuning_all)}
</section>

<section>
<h2>MAE no teste</h2>
<p>O MAE abaixo usa somente previsões fora da amostra, nas mesmas origens. Ele não deve ser somado ao MAE de outra base: a escala do PM2.5 não é a escala das demais séries do grupo.</p>
{table(mae_view.drop(columns=["stride"]))}
<h3>Outras métricas</h3>
{table(accuracy_view)}
<p>O erro médio (viés) é observado menos previsão. Valor positivo indica previsão abaixo do PM2.5 realizado.</p>
</section>

<section>
<h2>Resíduos</h2>
<p>Cada painel é a série do resíduo no teste. Em seguida está a autocorrelação até o lag 48 e o teste de Ljung-Box nos lags 10, 24 e 48.</p>
{image_tag(series_path, "Série dos resíduos no teste")}
{image_tag(out / "acf_residuos.png", "Autocorrelação dos resíduos")}
{table(ljung_view)}
{table(notes_view)}
</section>

<section>
<h2>Importância das variáveis</h2>
<p>A importância do Random Forest é a redução média de impureza de uma floresta ajustada só no treino interno, com a configuração escolhida na validação. Não é a média das florestas diárias do walk-forward. Preditores de PM2.5 muito correlacionados dividem crédito entre si.</p>
{table(importance_view)}
<p>O VIP do PLS também vem de um único ajuste no treino interno, com o número de componentes escolhido na validação e com padronização. VIP acima de 1 indica preditor mais útil que a média para explicar o PM2.5 da hora seguinte nesse ajuste. A limitação é a mesma: o número não descreve cada janela diária, e lags colineares repartem a importância.</p>
{table(vip_view)}
<p>Os coeficientes abaixo são do mesmo ajuste, já na escala padronizada. O arquivo <code>pls_feature_importance.csv</code> guarda esses coeficientes. VIP e coeficiente podem ordenar as colunas de formas diferentes: o VIP mede a contribuição para os componentes e o coeficiente é o peso depois dessa projeção. Lags colineares repartem os dois números.</p>
{table(coefficient_view)}
<p>As variáveis externas com VIP ou importância altos são medições da origem t: PM2.5 de Wanliu e de Changping, além de PM10, CO, temperatura, vento e ponto de orvalho locais. Nenhuma delas usa valor de t+1.</p>
</section>

<section>
<h2>PLS em linguagem direta</h2>
<p>Com muitos preditores parecidos, uma regressão comum fica instável: o coeficiente de um lag compete com o do lag vizinho e os dois podem sair grandes e com sinais opostos. O PLS evita esse passo. Ele constrói poucas combinações dos preditores, chamadas componentes, escolhidas para acompanhar o PM2.5 da hora seguinte, e só então faz a regressão nessas combinações.</p>
<p>A diferença para o componente principal comum é o critério. O componente principal resume a variação dos preditores sem olhar o alvo. O componente do PLS olha os dois lados: ele privilegia a direção de X que anda junto com y. Por isso um preditor pode variar muito e mesmo assim receber pouco peso, se essa variação não ajudar a prever o PM2.5.</p>
<p>Nesta base a grade pediu {component_list} componentes. Dezesseis é o maior número usado: com 17 preditores, o passo seguinte já ocupa todas as colunas. O número vencedor está na tabela de ajuste e fica fixo no teste. Cada dia reestima os componentes com o passado disponível até a véspera, sempre com os preditores padronizados. O VIP e os coeficientes padronizados vêm de um único ajuste no treino interno. Eles ajudam a leitura e não substituem o MAE do teste.</p>
</section>

<section>
<h2>Conclusões</h2>
<p>Nas {n_origins} horas comuns, {winner_name} teve o menor MAE, {br(float(winner['MAE_test']), 4)} µg/m³. A comparação é direta porque a origem, o horizonte e o período de teste são os mesmos.</p>
<p>A sazonalidade de 24 horas aparece no calendário, mas a força sazonal do STL é 0,013. Na validação, Holt-Winters com período 24 perde para a suavização sem sazonalidade. O SARIMAX escolhido foi a ordem {sarimax_order} com sazonalidade {sarimax_seasonal}. As ordens sazonais tiveram AIC menor na janela final do treino e MAE maior na validação, então não foram para o teste.</p>
<p>A matriz de 17 colunas deixa Random Forest e PLS no mesmo conjunto de informação, com disponibilidade explícita na origem. A meteorologia duplicada de Guanyuan ficou de fora. Os resíduos ainda mostram estrutura, então o erro de uma hora continua informando o erro das horas vizinhas; o MAE resume o tamanho do erro, não a ausência de dependência.</p>
</section>

<section>
<h2>Referências</h2>
<ul>
<li>Breiman, L. Random Forests. Machine Learning, 2001.</li>
<li>Chong, I.-G.; Jun, C.-H. Performance of some variable selection methods when multicollinearity is present. Chemometrics and Intelligent Laboratory Systems, 2005.</li>
<li>Hyndman, R. J.; Athanasopoulos, G. Forecasting: Principles and Practice. OTexts.</li>
<li>Ljung, G. M.; Box, G. E. P. On a measure of lack of fit in time series models. Biometrika, 1978.</li>
<li>Wold, S.; Sjöström, M.; Eriksson, L. PLS-regression: a basic tool of chemometrics. Chemometrics and Intelligent Laboratory Systems, 2001.</li>
<li>Zhang, S. et al. Beijing Multi-Site Air-Quality Data. UCI Machine Learning Repository, 2017. https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data</li>
</ul>
<h2>Apêndice — arquivos</h2>
<ul>
<li><code>analyses/grupo3/02_modelos/protocolo_final.py</code> — protocolo executado.</li>
<li><code>analyses/grupo3/02_modelos/results/protocolo_final.json</code> — tempo e MAE.</li>
<li><code>analyses/grupo3/02_modelos/results/validation_protocol.json</code> — cortes e preditores.</li>
<li><code>analyses/grupo3/01_dados/outputs/features_modelagem_base3.csv</code> — matriz usada por Random Forest e PLS.</li>
<li><code>analyses/grupo3/03_resultados/outputs/</code> — MAE, resíduos, ACF, VIP e importância.</li>
<li>Cada modelo guarda previsões, grade e configuração em <code>02_modelos/&lt;modelo&gt;/results/</code>.</li>
</ul>
<h2>Checksum das bases congeladas</h2>
<p>SHA-256 dos arquivos em <code>bases/grupo3</code>, gravado em <code>bases/grupo3/SHA256SUMS.txt</code>.</p>
{checksum_table}
</section>
</main>
</body>
</html>
"""
    report_dir = base / "05_relatorio"
    report_dir.mkdir(parents=True, exist_ok=True)
    html_path = report_dir / "relatorio_base3.html"
    html_path.write_text(html, encoding="utf-8")
    docs = root / "docs" / "relatorios" / "grupo3"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "relatorio_base3.html").write_text(html, encoding="utf-8")
    (docs / "README.md").write_text(
        "# Relatório da Base 3\n\n"
        "O HTML e o PDF estão em `analyses/grupo3/05_relatorio/` "
        "(`relatorio_base3.html` e `relatorio_base3.pdf`). "
        "Os dois têm o mesmo conteúdo.\n",
        encoding="utf-8",
    )
    return html_path


if __name__ == "__main__":
    print(build())
