"""Relatório HTML da Base 2."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import config


def write_report(clean_report: dict, stl_info: dict, params: dict, mae_df: pd.DataFrame, results: dict) -> Path:
    best = mae_df.iloc[0]
    rows = "".join(
        f"<tr><td>{r.model}</td><td>{r.mae:.3f}</td><td>{r.ljung_box_pvalue_lag24:.4g}</td>"
        f"<td>{r.runtime_sec:.1f}s</td><td>{int(r.rank)}</td></tr>"
        for r in mae_df.itertuples()
    )
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<title>Base 2 — Tráfego Interestadual | {config.OWNER}</title>
<style>
body {{ font-family: Georgia, serif; margin: 2rem auto; max-width: 920px; line-height: 1.5; color: #1a1a1a; }}
h1,h2 {{ font-family: "Helvetica Neue", Arial, sans-serif; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
th, td {{ border: 1px solid #ccc; padding: .45rem .6rem; text-align: left; }}
th {{ background: #f3f4f6; }}
img {{ max-width: 100%; height: auto; margin: .5rem 0 1.2rem; border: 1px solid #e5e7eb; }}
code {{ background: #f3f4f6; padding: .1rem .3rem; }}
.note {{ background: #fff7ed; border-left: 4px solid #c45c26; padding: .8rem 1rem; }}
</style>
</head>
<body>
<h1>Base 2 — Metro Interstate Traffic Volume</h1>
<p><strong>Responsável:</strong> {config.OWNER} · Grupo 5 (PLS Regression)</p>

<div class="note">
Parâmetros fixos: granularidade horária · random_state={config.RANDOM_STATE} ·
treino/teste {int(config.TRAIN_RATIO*100)}/{int((1-config.TRAIN_RATIO)*100)} ·
horizonte {config.HORIZON}h · walk-forward com refit a cada {config.REFIT_EVERY}h.
</div>

<h2>1. Base e preparação</h2>
<ul>
<li>Registros brutos: {clean_report['n_raw']} ({clean_report['n_duplicate_timestamps']} duplicatas de timestamp)</li>
<li>Série regular: {clean_report['n_regular_hours']} horas ({clean_report['start']} → {clean_report['end']})</li>
<li>Alvo: <code>traffic_volume</code> (média {clean_report['target_mean']:.1f}, máx {clean_report['target_max']:.0f})</li>
<li>Clima usado com <strong>lag 1h</strong> para evitar vazamento; feriados/calendário conhecidos antecipadamente.</li>
</ul>

<h2>2. STL</h2>
<p>Força da sazonalidade (m={config.SEASONAL_PERIOD}): <strong>{stl_info['seasonal_strength']:.3f}</strong>.</p>
<img src="figures/04_stl.png" alt="STL"/>

<h2>3. Modelos e hiperparâmetros</h2>
<pre>{params}</pre>

<h2>4. MAE walk-forward</h2>
<table>
<thead><tr><th>Modelo</th><th>MAE</th><th>Ljung-Box p (lag 24)</th><th>Tempo</th><th>Rank</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<p>Melhor modelo nesta base: <strong>{best.model}</strong> (MAE={best.mae:.3f}).</p>

<h2>5. Previsões (amostra 14 dias)</h2>
"""
    for model in mae_df["model"]:
        html += f'<h3>{model}</h3><img src="figures/previsao_{model}.png" alt="{model}"/>'
        html += f'<img src="figures/residuos_{model}.png" alt="resíduos {model}"/>'

    html += """
<h2>6. Observações</h2>
<ul>
<li>Holt-Winters é univariado (referência).</li>
<li>SARIMAX, RF e PLS usam externas temporalmente válidas.</li>
<li>RF/PLS compartilham o mesmo conjunto de features.</li>
</ul>
</body></html>
"""
    path = config.OUTPUT_DIR / "relatorio_base2.html"
    path.write_text(html, encoding="utf-8")
    return path
