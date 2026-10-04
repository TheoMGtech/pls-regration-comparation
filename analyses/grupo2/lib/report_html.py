"""Gera o HTML paginado da Base 2 a partir dos artefatos já congelados."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pandas as pd

import config


def _img(name: str) -> str:
    path = config.FIG_DIR / name
    if not path.exists():
        return f"<p class='note'>Figura ausente: {name}</p>"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return (
        f'<img src="data:image/png;base64,{b64}" alt="{name}" />'
    )


def _md_block(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    parts = []
    for line in text.splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            parts.append(f"<h3>{line[3:]}</h3>")
        elif line.startswith("|") and "---" not in line:
            parts.append(line)
        else:
            parts.append(line)
    # Keep as pre-wrapped paragraphs: convert blank lines
    html = []
    buf = []
    table = []

    def flush_buf():
        if buf:
            html.append("<p>" + " ".join(buf) + "</p>")
            buf.clear()

    def flush_table():
        if not table:
            return
        rows = [r.strip().strip("|") for r in table if r.strip()]
        table.clear()
        if len(rows) < 2:
            return
        html.append("<table>")
        for i, row in enumerate(rows):
            cells = [c.strip() for c in row.split("|")]
            tag = "th" if i == 0 else "td"
            html.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
        html.append("</table>")

    for line in parts:
        if line.startswith("|"):
            flush_buf()
            table.append(line)
            continue
        flush_table()
        if line.startswith("<h3>"):
            flush_buf()
            html.append(line)
        elif line.startswith("- "):
            flush_buf()
            html.append(f"<li>{line[2:]}</li>")
        elif not line.strip():
            flush_buf()
        else:
            buf.append(line.replace("**", ""))
    flush_buf()
    flush_table()
    # wrap consecutive li
    out = []
    in_ul = False
    for item in html:
        if item.startswith("<li>"):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(item)
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(item)
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)


def write_paginated_report() -> Path:
    mae = pd.read_csv(config.RESULT_DIR / "mae_consolidado.csv")
    ci = pd.read_csv(config.RESULT_DIR / "mae_uncertainty.csv")
    lb = pd.read_csv(config.RESULT_DIR / "residual_diagnostics.csv")
    cleaning = json.loads((config.DATA_DIR / "cleaning_report.json").read_text())
    protocol = json.loads((config.RESULT_DIR / "protocol.json").read_text())
    stl = json.loads((config.RESULT_DIR / "stl_summary.json").read_text())
    params = json.loads((config.RESULT_DIR / "best_params.json").read_text())
    baseline = pd.read_csv(config.RESULT_DIR / "baseline_predictions.csv")
    baseline_mae = baseline.groupby("baseline")["absolute_error"].mean().sort_values()

    rf_imp = pd.read_csv(config.RESULT_DIR / "feature_importance_Random_Forest.csv").head(8)
    pls_imp = pd.read_csv(config.RESULT_DIR / "feature_importance_PLS_Regression.csv").head(8)

    def tbl(df: pd.DataFrame, cols=None, fmt=3) -> str:
        view = df if cols is None else df[cols]
        return view.to_html(index=False, float_format=lambda x: f"{x:.{fmt}f}")

    mae_view = mae.merge(ci[["model", "mae_ci95_low", "mae_ci95_high"]], on="model", how="left")
    pages = []

    pages.append(f"""
<section class="page">
<h1>Base 2 — Metro Interstate Traffic Volume</h1>
<p class="kicker">Grupos 5 · PLS Regression · Relatório técnico da base · Bruna Carvalho Cardoso</p>
<h2>1. Resumo executivo</h2>
<p>Esta base prevê o volume horário de veículos na I-94 (Minneapolis–Saint Paul)
uma hora à frente. Os quatro modelos usaram as mesmas 521 origens de teste,
hiperparâmetros congelados na validação e MAE apenas em horas originalmente
observadas.</p>
<p><b>Melhor modelo:</b> Random Forest (MAE 157,8; WAPE 4,7%).
<b>Especialista PLS:</b> segundo lugar (MAE 191,7; WAPE 5,7%), +32% frente
à sazonal semanal. Holt-Winters 209,8. SARIMAX 263,7 — o pior dos quatro,
ainda assim melhor que o baseline semanal (283,3).</p>
<p>A sazonalidade diária é forte (STL 0,81). Clima observado no futuro foi
proibido; o PLS vencedor sequer usou clima defasado. Não compare estes MAEs
com ouro ou Jena.</p>
</section>
""")

    pages.append("""
<section class="page">
<h2>2. Integrantes e responsabilidades</h2>
<p>Grupo 5 da disciplina, especialização PLS. Cada integrante responde por
uma das cinco bases. Esta pasta cobre somente a Base 2.</p>
<table>
<tr><th>Integrante</th><th>Base</th><th>Papel nesta entrega</th></tr>
<tr><td>Bruna Carvalho Cardoso</td><td>2 — tráfego I-94</td><td>Documentação, limpeza, FE, STL, quatro modelos, resíduos, PLS, relatório desta base</td></tr>
<tr><td>Demais integrantes do Grupo 5</td><td>1, 3, 4 e 5</td><td>Pipelines das outras bases e relatório consolidado (vitórias / posição média)</td></tr>
</table>
<p>A apresentação oral navega este HTML. Não há slides separados.</p>
</section>
""")

    pages.append(f"""
<section class="page">
<h2>3. Documentação da base e variáveis externas</h2>
<p><b>Fonte:</b> UCI Metro Interstate Traffic Volume (Minnesota DoT + Weather Underground).
<b>Arquivo congelado:</b> <code>bases/grupo2/Metro_Interstate_Traffic_Volume.csv</code>.</p>
<p>Período bruto {cleaning.get('start', '2012-10-02')} a 2018-09-30 no segmento
analisado ({cleaning['start']} → {cleaning['end']}). Alvo: <code>traffic_volume</code>
em veículos/hora. Frequência: 1 hora. Horizonte: 1 hora. Origem: último instante conhecido.</p>
<table>
<tr><th>Variável</th><th>Disponível para prever t+1?</th><th>Uso</th></tr>
<tr><td>Calendário / feriado</td><td>Sim</td><td>seno/cosseno, is_weekend, is_holiday no dia inteiro</td></tr>
<tr><td>Temperatura/chuva/neve/nuvens em t+1</td><td>Não — vazamento</td><td>proibido</td></tr>
<tr><td>Clima já observado em t</td><td>Sim</td><td>lags de 1 hora</td></tr>
<tr><td>Volume futuro</td><td>Não</td><td>nunca é feature</td></tr>
</table>
<p>Duplicatas de timestamp: {cleaning['n_duplicate_timestamps']}.
Lacuna máxima: {cleaning['largest_gap_hours']:.0f} h (segmento posterior mantido).
Alvos observados no segmento: {cleaning['n_observed_in_selected_segment']}.</p>
{_img("01_serie_alvo.png")}
</section>
""")

    pages.append(f"""
<section class="page">
<h2>4. Limpeza, preparação e feature engineering</h2>
<p>Imputação causal do alvo nas {cleaning['n_imputed_targets']} horas faltantes
do segmento: lag 168 → lag 24 → forward-fill. O MAE ignora essas horas.
Feriado do CSV (só 00:00) foi expandido ao dia inteiro.</p>
<p>Features tabulares compartilhadas por RF e PLS: lags 1–336 h, janelas 6/24/168,
ciclo de hora/semana/mês, clima lag 1, flags de observação. Warmup de 336 h
removido. Frame final: {protocol['n_rows']} linhas.</p>
{_img("02_externas.png")}
{_img("03_perfil_horario.png")}
</section>
""")

    pages.append(f"""
<section class="page">
<h2>5. STL, tendência e força da sazonalidade</h2>
<p>STL apenas no desenvolvimento. Período 24. Força sazonal =
<b>{stl['seasonal_strength']:.3f}</b> (sazonalidade diária nítida).
Tendência estável (média inicial {stl['trend_start_mean']:.0f} vs final
{stl['trend_end_mean']:.0f}). O Holt-Winters, na validação, preferiu
sazonalidade semanal 168 sem tendência — o dia e a semana coexistam.</p>
{_img("04_stl.png")}
</section>
""")

    pages.append(f"""
<section class="page">
<h2>6. Protocolo walk-forward</h2>
<p>{protocol['external_split']}. {protocol['development_split']}.
{protocol['refit_policy']}. Passo das origens: {protocol['test_origin_step_hours']} h
(coprimo de 24). Validação: {protocol['n_validation_origins']} origens.
Teste: {protocol['n_test_origins']} origens, idênticas nos quatro modelos.
{protocol['evaluation_policy']}. random_state={protocol['random_state']}.</p>
<p>Hiperparâmetros fixos no teste. Salvaguarda Holt-Winters: {protocol['numerical_safeguard']}.</p>
</section>
""")

    pages.append(f"""
<section class="page">
<h2>7. Modelos, hiperparâmetros e otimização</h2>
<p>Busca só na validação. Espaços: RF 12 candidatos; PLS 1–32 componentes × 3
conjuntos de features; Holt-Winters tendência/sazonal/amortecimento/janela;
SARIMAX 72 BIC + 5 walk-forward.</p>
<pre>{json.dumps(params, indent=2, ensure_ascii=False)}</pre>
<p>RF: 900 árvores, max_features=sqrt. PLS: no_weather, 15 componentes.
HW: sazonal aditiva 168, sem tendência, janela 1440. SARIMAX: (2,0,1)×(0,1,1,24)
com exógenas de calendário e clima lag 1, reescaladas por janela.</p>
</section>
""")

    base_rows = "".join(
        f"<tr><td>{k}</td><td>{v:.2f}</td></tr>" for k, v in baseline_mae.items()
    )
    pages.append(f"""
<section class="page">
<h2>8. Resultados comparativos por MAE</h2>
<p>Ranking oficial desta base. Baselines fora do ranking. Não somar com outras bases.</p>
{tbl(mae_view, ["model", "n_forecasts", "mae", "mae_ci95_low", "mae_ci95_high", "wape_percent", "rank", "improvement_vs_best_baseline_percent", "runtime_sec"], 3)}
<table><tr><th>Baseline</th><th>MAE</th></tr>{base_rows}</table>
<p>Vitórias e posição média nas cinco bases ficam para o relatório consolidado
do Grupo 5. Nesta base: RF 1º, PLS 2º, HW 3º, SARIMAX 4º.</p>
</section>
""")

    pages.append(f"""
<section class="page">
<h2>9. Resíduos e Ljung-Box</h2>
<p>Tabela principal: 168 horas consecutivas (espaçamento 1 h). Série amostrada
de 11 h não interpreta lag 24 horário.</p>
{tbl(lb, None, 4)}
<p>PLS deixou o resíduo mais próximo de ruído (ACF1 ≈ 0; p lag 24 = 0,061).
RF ganha no MAE e retém ACF1 = 0,50. HW sofre com 167 fallbacks. SARIMAX
limpa lag 1 e ainda rejeita lag 24 em 5%.</p>
{_img("residuos_Random_Forest.png")}
</section>
""")

    pages.append(f"""
<section class="page">
<h2>9b. Gráficos de resíduo (apêndice visual imediato)</h2>
{_img("residuos_PLS_Regression.png")}
{_img("residuos_Holt_Winters.png")}
{_img("residuos_SARIMAX.png")}
</section>
""")

    pages.append(f"""
<section class="page">
<h2>10. Importância das features</h2>
<p>RF: importância nativa. PLS: coeficiente padronizado, VIP e permutation
na validação. Externas meteorológicas: disponíveis só defasadas; o PLS
vencedor as excluiu.</p>
<h3>Random Forest (topo)</h3>
{tbl(rf_imp, None, 4)}
<h3>PLS (topo)</h3>
{tbl(pls_imp, None, 3)}
<p>Concordância: lags 1 h, 24 h, 168 h e 336 h. Feriado tem sinal negativo
no PLS e peso pequeno. Sem inferência causal.</p>
</section>
""")

    pages.append(f"""
<section class="page">
<h2>11. Modelo de especialização — PLS Regression</h2>
{_md_block(config.OUTPUT_DIR / "PLS_technical_summary.md")}
</section>
""")

    pages.append(f"""
<section class="page">
<h2>11b. Previsões do PLS e do melhor modelo</h2>
{_img("previsao_PLS_Regression.png")}
{_img("previsao_Random_Forest.png")}
</section>
""")

    pages.append("""
<section class="page">
<h2>12. Conclusões, limitações e recomendações</h2>
<ul>
<li>Em horizonte de 1 hora nesta via, persistência e sazonalidade semanal
dominam; modelos tabulares vencem SARIMAX.</li>
<li>PLS cumpre o papel de especialista: segundo MAE, resíduos mais limpos,
runtime de segundos, compressão real (15 de 32 features).</li>
<li>Holt-Winters não deve ser lido como vitória plena: 32% de fallback 168h.</li>
<li>SARIMAX não “falhou”; é o pior dos quatro e o mais caro (~7h46 no teste).</li>
<li>Limitação: coeficientes/p-valores das exógenas do SARIMAX não foram
exportados; feriados raros (4 de julho) seguem difíceis para todos.</li>
<li>Recomendação operacional: RF para acurácia; PLS para diagnóstico e custo.</li>
<li>O grupo ainda precisa consolidar vitórias nas outras quatro bases.</li>
</ul>
</section>
""")

    pages.append("""
<section class="page">
<h2>13. Referências</h2>
<ul>
<li>UCI Machine Learning Repository. Metro Interstate Traffic Volume Data Set.</li>
<li>Hyndman, R. J.; Athanasopoulos, G. Forecasting: Principles and Practice.</li>
<li>Wold, H. Partial Least Squares. Enciclopédias de estatística.</li>
<li>Box, G.; Jenkins, G.; Reinsel, G. Time Series Analysis.</li>
<li>Cleveland et al. STL: A Seasonal-Trend Decomposition Procedure Based on Loess.</li>
<li>Ljung, G.; Box, G. On a measure of lack of fit in time series models.</li>
<li>scikit-learn PLSRegression; statsmodels SARIMAX / ExponentialSmoothing.</li>
<li>Enunciado da disciplina: Modelagem Comparativa de Séries Temporais com Variáveis Externas.</li>
</ul>
<h2>14. Apêndices</h2>
<p>Sínteses em <code>outputs/*.md</code>, candidatos de tuning em CSV,
<code>protocol.json</code>, <code>CHECKLIST_BASE2.md</code> e
<code>DOCUMENTACAO_BASE2.md</code>. Registro diário de demandas: planilha
do grupo (não versionada neste repositório por decisão anterior; o enunciado
ainda a exige na entrega Odete).</p>
</section>
""")

    css = """
@page { size: A4; margin: 16mm; }
html, body { font-family: "Helvetica Neue", Arial, sans-serif; color: #111;
  line-height: 1.45; background: #f4f4f5; }
.page { background: #fff; max-width: 820px; margin: 24px auto; padding: 28px 36px;
  page-break-after: always; box-shadow: 0 1px 8px rgba(0,0,0,.08); }
h1 { font-size: 1.7rem; margin: 0 0 .4rem; }
h2 { font-size: 1.2rem; border-bottom: 2px solid #c45c26; padding-bottom: .25rem; }
h3 { font-size: 1.02rem; }
.kicker { color: #555; margin-top: 0; }
table { border-collapse: collapse; width: 100%; font-size: .82rem; margin: 12px 0; }
th, td { border: 1px solid #d4d4d8; padding: 5px 7px; text-align: left; }
th { background: #fafafa; }
img { max-width: 100%; height: auto; margin: 8px 0 14px; border: 1px solid #e4e4e7; }
pre { background: #fafafa; padding: 10px; overflow: auto; font-size: .75rem; }
.note { background: #fff7ed; padding: .6rem .8rem; border-left: 4px solid #c45c26; }
@media print { body { background: #fff; } .page { box-shadow: none; margin: 0; } }
"""
    html = (
        "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'/>"
        "<title>Relatório Base 2 — Tráfego interestadual</title>"
        f"<style>{css}</style></head><body>"
        + "".join(pages)
        + "</body></html>"
    )
    out = config.OUTPUT_DIR / "relatorio_base2.html"
    out.write_text(html, encoding="utf-8")
    return out


if __name__ == "__main__":
    path = write_paginated_report()
    print(path)
