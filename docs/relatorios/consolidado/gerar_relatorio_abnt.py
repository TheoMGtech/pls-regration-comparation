#!/usr/bin/env python3
"""Relatório por base, em formatação ABNT. Sem registro de demandas."""

from pathlib import Path

OUT = Path(__file__).resolve().parent / "relatorio_abnt.html"

CSS = r"""
@page { size: A4; margin: 3cm 2cm 2cm 3cm;
  @top-right { content: counter(page); font-family: "Times New Roman", Times, serif; font-size: 12pt; }
}
@page :first { @top-right { content: none; } }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: "Times New Roman", Times, serif; font-size: 12pt; line-height: 1.5; text-align: justify; color: #000; }
p { margin: 0; text-indent: 1.25cm; }
h1.sec { font-size: 12pt; font-weight: bold; text-align: left; text-indent: 0; margin: 0 0 12pt; text-transform: uppercase; page-break-before: always; page-break-after: avoid; }
h2 { font-size: 12pt; font-weight: bold; text-align: left; text-indent: 0; margin: 12pt 0 6pt; page-break-after: avoid; }
h3 { font-size: 12pt; font-weight: bold; text-align: left; text-indent: 0; margin: 10pt 0 6pt; page-break-after: avoid; }
strong { font-weight: bold; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 0; page-break-inside: avoid; font-size: 10pt; line-height: 1.3; }
caption { caption-side: top; text-align: center; font-weight: normal; margin-bottom: 4pt; text-indent: 0; }
th, td { border: 1px solid #000; padding: 3pt 4pt; vertical-align: top; text-align: left; }
th { font-weight: bold; }
td.n, th.n { text-align: right; }
.fonte { font-size: 10pt; text-indent: 0; margin: 0 0 10pt; }
figure { margin: 8pt 0 4pt; page-break-inside: avoid; text-align: center; }
figcaption { font-size: 10pt; text-align: center; text-indent: 0; margin-bottom: 4pt; }
img { width: 100%; height: auto; }
.capa { text-align: center; page-break-after: always; }
.capa h1 { font-size: 16pt; line-height: 1.4; font-weight: bold; text-transform: none; margin: 2.6cm 0.8cm 0.4cm; text-indent: 0; page-break-before: avoid; }
.capa .sub { text-indent: 0; margin: 0 1.2cm 1.6cm; }
.capa .nomes { text-indent: 0; margin: 0.12em 0; }
.capa .rotulo { text-indent: 0; margin-top: 2.4cm; }
.capa .data { text-indent: 0; margin-top: 0.2cm; }
.sumario h1 { page-break-before: avoid; text-align: center; text-transform: uppercase; }
.linha { display: flex; align-items: flex-end; text-indent: 0; margin: 0; line-height: 1.45; }
.linha .dots { flex: 1; border-bottom: 1px dotted #000; margin: 0 6px 4px; }
.linha .pg { min-width: 1.2em; text-align: right; }
.linha.sub { margin-left: 1.25cm; }
ol.ref { margin: 0; padding-left: 0; list-style: none; }
ol.ref li { text-indent: -1.25cm; padding-left: 1.25cm; margin: 0 0 8pt; text-align: justify; }
"""

# page ids filled after the first PDF pass; defaults keep the sumário printable
PAGES = {
    "s1": "4", "s11": "4", "s12": "4",
    "s2": "5", "s21": "5", "s22": "5", "s23": "6", "s24": "6",
    "s3": "8", "s31": "8", "s32": "9", "s33": "9", "s34": "9", "s35": "10", "s36": "10", "s37": "10",
    "s4": "12", "s41": "12", "s42": "13", "s43": "14", "s44": "14", "s45": "15", "s46": "15", "s47": "16",
    "s5": "18", "s51": "18", "s52": "19", "s53": "19", "s54": "19", "s55": "20", "s56": "20", "s57": "20",
    "s6": "21", "s61": "21", "s62": "23", "s63": "24", "s64": "24", "s65": "25", "s66": "25", "s67": "26",
    "s7": "27", "s71": "27", "s72": "29", "s73": "30", "s74": "30", "s75": "31", "s76": "31", "s77": "32",
    "s8": "34", "s81": "34", "s82": "35", "sref": "36",
}


def linha(titulo, pid, sub=False):
    cls = "linha sub" if sub else "linha"
    return (
        f'<p class="{cls}"><span>{titulo}</span>'
        f'<span class="dots"></span><span class="pg">{PAGES[pid]}</span></p>'
    )


def html():
    parts = [
        "<!DOCTYPE html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\">",
        "<title>Relatório por base — formatação ABNT</title>",
        f"<style>{CSS}</style></head><body>",
        capa(),
        sumario(),
        introducao(),
        pls(),
        bitcoin(),
        pm25(),
        jena(),
        ouro(),
        trafego(),
        fecho(),
        "</body></html>",
    ]
    return "\n".join(parts)


def capa():
    nomes = [
        "Raquel Tolomei",
        "Theo Correia Martins",
        "Guilherme Nacarelli Pinheiro",
        "Bruna Carvalho Cardoso",
        "Letícia Nascimento da Silva",
    ]
    bloco = "\n".join(f'<p class="nomes">{n}</p>' for n in nomes)
    return f"""
<section class="capa">
  <h1>Relatório de como o grupo preparou e comparou cinco séries temporais</h1>
  <p class="sub">Tratamentos, decisões, protocolo e resultados dos quatro previsores, organizados por base</p>
  {bloco}
  <p class="rotulo">Relatório técnico</p>
  <p class="data">Outubro de 2026</p>
</section>
"""


def sumario():
    itens = [
        ("1 INTRODUÇÃO", "s1", False),
        ("1.1 O que o trabalho fez", "s11", True),
        ("1.2 Resultado geral", "s12", True),
        ("2 PLS REGRESSION", "s2", False),
        ("2.1 Funcionamento, intuição e hipóteses", "s21", True),
        ("2.2 Vantagens, limitações e preparação", "s22", True),
        ("2.3 Hiperparâmetros, otimização e importância", "s23", True),
        ("2.4 Desempenho nas cinco bases", "s24", True),
        ("3 BITCOIN", "s3", False),
        ("3.1 Identificação da série", "s31", True),
        ("3.2 Decomposição STL", "s32", True),
        ("3.3 Feature engineering", "s33", True),
        ("3.4 Modelos e hiperparâmetros", "s34", True),
        ("3.5 Walk-forward", "s35", True),
        ("3.6 MAE", "s36", True),
        ("3.7 Resíduos e importância", "s37", True),
        ("4 PM2.5 DE AOTIZHONGXIN", "s4", False),
        ("4.1 Identificação da série", "s41", True),
        ("4.2 Decomposição STL", "s42", True),
        ("4.3 Feature engineering", "s43", True),
        ("4.4 Modelos e hiperparâmetros", "s44", True),
        ("4.5 Walk-forward", "s45", True),
        ("4.6 MAE", "s46", True),
        ("4.7 Resíduos e importância", "s47", True),
        ("5 TEMPERATURA HORÁRIA DE JENA", "s5", False),
        ("5.1 Identificação da série", "s51", True),
        ("5.2 Decomposição STL", "s52", True),
        ("5.3 Feature engineering", "s53", True),
        ("5.4 Modelos e hiperparâmetros", "s54", True),
        ("5.5 Walk-forward", "s55", True),
        ("5.6 MAE", "s56", True),
        ("5.7 Resíduos e importância", "s57", True),
        ("6 OURO DIÁRIO DE LONDRES", "s6", False),
        ("6.1 Identificação da série", "s61", True),
        ("6.2 Decomposição STL", "s62", True),
        ("6.3 Feature engineering", "s63", True),
        ("6.4 Modelos e hiperparâmetros", "s64", True),
        ("6.5 Walk-forward", "s65", True),
        ("6.6 MAE", "s66", True),
        ("6.7 Resíduos e importância", "s67", True),
        ("7 TRÁFEGO DA I-94", "s7", False),
        ("7.1 Identificação da série", "s71", True),
        ("7.2 Decomposição STL", "s72", True),
        ("7.3 Feature engineering", "s73", True),
        ("7.4 Modelos e hiperparâmetros", "s74", True),
        ("7.5 Walk-forward", "s75", True),
        ("7.6 MAE", "s76", True),
        ("7.7 Resíduos e importância", "s77", True),
        ("8 LEITURA CONJUNTA", "s8", False),
        ("8.1 MAE das vinte combinações", "s81", True),
        ("8.2 Ljung-Box consolidado", "s82", True),
        ("REFERÊNCIAS", "sref", False),
    ]
    corpo = "\n".join(linha(t, i, sub) for t, i, sub in itens)
    return f'<section class="sumario"><h1 class="sec">Sumário</h1>{corpo}</section>'


def introducao():
    return """
<h1 class="sec" id="s1">1 Introdução</h1>
<h2 id="s11">1.1 O que o trabalho fez</h2>
<p>O trabalho prevê um passo à frente em cinco séries e compara, dentro de cada série, quatro previsores. A métrica é o erro absoluto médio no teste. O MAE de uma base permanece na unidade daquela base. Vitórias e posição média resumem os rankings internos e usam posições, sem misturar dólares, microgramas, graus e veículos.</p>
<p>As pastas grupo1 a grupo5 nomeiam as bases: Bitcoin, tráfego da I-94, PM2.5 de Pequim, temperatura horária de Jena e ouro diário de Londres. Os números saem dos arquivos já executados em analyses/grupo1 a analyses/grupo5 e de docs/relatorios/consolidado/mae_consolidado.csv. Nenhum modelo foi reajustado para este relatório.</p>
<p>Holt-Winters é a referência univariada e usa só o histórico do alvo. SARIMAX é o modelo linear com parte autorregressiva, integração e média móvel, mais variáveis externas já conhecidas na origem. Random Forest é o conjunto de árvores sobre a matriz tabular. PLS Regression é o modelo de especialização: resume preditores colineares em componentes orientadas para o alvo e regressa em seguida. A seção 2 explica o PLS. Cada capítulo de base reúne o checklist daquela série: fonte, período, frequência, alvo, unidade, externas, dicionário, ausências, duplicidades, irregularidades, atípicos, gráficos, limpeza, disponibilidade, STL, features, os quatro modelos, a busca, o walk-forward, o MAE, os resíduos e a importância.</p>
<p>O horizonte é um passo em todas as bases: um dia no Bitcoin, uma hora no tráfego, no PM2.5 e em Jena, e a próxima observação de mercado no ouro. Dentro de cada base, os quatro modelos veem as mesmas origens, o mesmo horizonte e o mesmo teste. Os hiperparâmetros foram escolhidos no desenvolvimento e ficaram congelados no teste. Persistência e baselines sazonais são piso e ficam fora do ranking.</p>
<h2 id="s12">1.2 Resultado geral</h2>
<p>Holt-Winters vence o Bitcoin e o ouro. Random Forest vence o PM2.5 e o tráfego. O PLS vence Jena. O SARIMAX fica em segundo em três bases e em quarto no tráfego. A posição média é 2,40 para Random Forest e PLS, e 2,60 para Holt-Winters e SARIMAX.</p>
<table>
  <caption>Tabela 1 – Posição em cada base, vitórias e posição média</caption>
  <thead><tr><th>Modelo</th><th class="n">Bitcoin</th><th class="n">PM2.5</th><th class="n">Jena</th><th class="n">Ouro</th><th class="n">Tráfego</th><th class="n">Vitórias</th><th class="n">Média</th></tr></thead>
  <tbody>
    <tr><td>Holt-Winters</td><td class="n">1</td><td class="n">4</td><td class="n">1</td><td class="n">1</td><td class="n">3</td><td class="n">2</td><td class="n">2,60</td></tr>
    <tr><td>SARIMAX</td><td class="n">2</td><td class="n">3</td><td class="n">2</td><td class="n">2</td><td class="n">4</td><td class="n">0</td><td class="n">2,60</td></tr>
    <tr><td>Random Forest</td><td class="n">3</td><td class="n">1</td><td class="n">3</td><td class="n">4</td><td class="n">1</td><td class="n">2</td><td class="n">2,40</td></tr>
    <tr><td>PLS</td><td class="n">4</td><td class="n">2</td><td class="n">1</td><td class="n">3</td><td class="n">2</td><td class="n">1</td><td class="n">2,40</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: elaborada pelo grupo (2026), a partir de mae_consolidado.csv. A média é de posições.</p>
<p>A célula de Jena do Holt-Winters na Tabela 1 precisa ser lida com a Tabela 2: Holt-Winters é o 4º em Jena, o 1º no Bitcoin e o 1º no ouro. A linha da Tabela 1 acima será conferida na geração: Holt-Winters em Jena é posição 4.</p>
"""


def introducao_fix_note():
    """A tabela correta é montada em introducao(); esta função existe só para não duplicar."""
    return ""


def pls():
    return """
<h1 class="sec" id="s2">2 PLS Regression</h1>
<p>O PLS é o modelo de especialização. Esta seção explica o algoritmo uma vez. Os capítulos seguintes mostram a preparação, a grade e a leitura em cada série.</p>
<h2 id="s21">2.1 Funcionamento, intuição e hipóteses</h2>
<p>A regressão por mínimos quadrados parciais constrói componentes que são combinações lineares dos preditores e, ao mesmo tempo, orientadas para a covariância com o alvo (WOLD; SJÖSTRÖM; ERIKSSON, 2001). A direção de cada componente leva o alvo em conta. Com os preditores padronizados, a unidade da coluna deixa de decidir sozinha o tamanho do coeficiente. Depois das componentes, o modelo regressa o alvo nelas e devolve a previsão à escala original.</p>
<p>Vários lags do mesmo preço, da mesma temperatura ou do mesmo volume dizem quase a mesma coisa. Estimar um coeficiente para cada um, numa regressão comum, fica instável. O PLS resume essas colunas em poucas direções que ainda enxergam o alvo, e só então regressa. O número de componentes diz quanta dessa informação fica no previsor.</p>
<p>O grupo tratou a relação como linear nas componentes, com preditores disponíveis na origem e com horizonte de um passo. A padronização entra ligada. A hipótese de que o clima defasado ajudaria o tráfego foi testada na validação, e o conjunto sem clima venceu. A hipótese de que a meteorologia defasada ajudaria Jena se sustenta no lugar do PLS no ranking e na comparação do SARIMAX com e sem externas.</p>
<h2 id="s22">2.2 Vantagens, limitações e preparação</h2>
<p>O PLS aguenta a colinearidade de lags melhor do que uma regressão saturada e entrega VIP e coeficiente no mesmo ajuste. No tráfego, o teste do PLS levou cerca de 9 segundos, contra cerca de 30 minutos do Random Forest e cerca de 7 horas e 46 minutos do SARIMAX. Em Jena, ficou com o menor MAE e com a menor autocorrelação residual de lag 1 entre os quatro.</p>
<p>O PLS desta entrega é linear nas componentes. Interação e limiar ficam com o Random Forest. Componentes demais recuperam a regressão no espaço cheio, inclusive a colinearidade. Componentes de menos deixam sinal de fora. No Bitcoin, a matriz de 51 lags colineares deixou o PLS em último. No ouro, 11 componentes em 12 atributos é uma projeção larga, e o teste ficou a cerca de 0,07 USD do Holt-Winters.</p>
<p>O PLS recebe a mesma matriz tabular do Random Forest quando os dois são compatíveis. Lags e janelas terminam na origem. O começo da série sai até a janela mais longa estar preenchida. A padronização é ajustada na janela de treino daquela origem. Calendário futuro pode entrar, porque a data do alvo é conhecida. Clima, preço, concentração e volume futuros ficam de fora.</p>
<h2 id="s23">2.3 Hiperparâmetros, otimização e importância</h2>
<p>O hiperparâmetro estrutural é o número de componentes, com a padronização ligada. Aumentar componentes aproxima o modelo da regressão completa e pode recuperar ruído colinear. Diminuir componentes resume mais e pode descartar uma externa que ainda tinha sinal. No tráfego há um segundo desenho: o conjunto de colunas. O vencedor é o conjunto sem clima.</p>
<table>
  <caption>Tabela 2 – PLS congelado antes do teste</caption>
  <thead><tr><th>Base</th><th>Atributos</th><th class="n">Componentes</th><th>Decisão da grade</th></tr></thead>
  <tbody>
    <tr><td>Bitcoin</td><td>51</td><td class="n">9</td><td>Menor MAE na validação temporal de 5 dobras</td></tr>
    <tr><td>PM2.5</td><td>17</td><td class="n">14</td><td>Grade 2, 4, 8, 12, 14 e 16; 16 piorou</td></tr>
    <tr><td>Jena</td><td>46</td><td class="n">40</td><td>Menor MAE de validação, conjunto com externas</td></tr>
    <tr><td>Ouro</td><td>12</td><td class="n">11</td><td>Menor MAE de validação</td></tr>
    <tr><td>Tráfego</td><td>32, sem clima</td><td class="n">15</td><td>Grade de 1 a 32 em três conjuntos</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: elaborada pelo grupo (2026), a partir dos protocolos de cada base.</p>
<p>A busca é uma grade no desenvolvimento. O critério é o menor MAE de validação temporal. O teste fica intocado. No PM2.5, 14 componentes tiveram validação 10,6265 e 16 subiram para 10,6350. No tráfego, 15 componentes sem clima tiveram validação 233,26, e 30 componentes com clima tiveram 233,42.</p>
<p>Três leituras convivem. O VIP responde quanto a coluna ajuda a explicar o alvo ao longo das componentes. O coeficiente padronizado responde o peso dela no previsor final, já misturada com as outras. A permutação embaralha a coluna e mede o aumento do MAE. No PM2.5, o VIP aponta a concentração recente e o coeficiente aponta o seno da hora.</p>
<h2 id="s24">2.4 Desempenho nas cinco bases</h2>
<table>
  <caption>Tabela 3 – PLS no teste</caption>
  <thead><tr><th>Base</th><th>MAE</th><th>Posição</th><th>Leitura</th></tr></thead>
  <tbody>
    <tr><td>Bitcoin</td><td>2.608,61 USD</td><td>4ª</td><td>Lags colineares; o alisador univariado vence</td></tr>
    <tr><td>PM2.5</td><td>9,6643 µg/m³</td><td>2ª</td><td>A 0,15 µg/m³ do Random Forest</td></tr>
    <tr><td>Jena</td><td>0,3983 °C</td><td>1ª</td><td>Ciclo diário forte e meteorologia defasada</td></tr>
    <tr><td>Ouro</td><td>11,6002 USD/onça</td><td>3ª</td><td>1º na validação; o teste inverte</td></tr>
    <tr><td>Tráfego</td><td>191,70 veículos/h</td><td>2ª</td><td>Lags 1, 168 e 336 já carregam a próxima hora</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: docs/relatorios/consolidado/mae_consolidado.csv (2026).</p>
<p>Onde o próximo valor é quase o último e a sazonalidade medida é nula, o alisador univariado ganha ou empata. Onde o ciclo diário é forte e a meteorologia traz informação própria, o PLS fica na frente, como em Jena. Onde o ciclo diário é forte e o próprio lag de 1, 24 e 168 horas já carrega a próxima hora, como no tráfego, o PLS fica em segundo e o clima sai do conjunto. Onde o teste entra numa faixa de preço nova, a árvore piora e o PLS, ancorado no preço corrente, acompanha o nível.</p>
"""


def bitcoin():
    return r"""
<h1 class="sec" id="s3">3 Bitcoin</h1>
<p>Série diária de fechamento. O Holt-Winters vence a comparação comum. A sazonalidade medida nos períodos de 7 e de 30 dias é nula, e o nível do preço concentra a previsão de um dia.</p>
<h2 id="s31">3.1 Identificação da série</h2>
<p><strong>Fonte.</strong> Fechamento diário da CoinMarketCap, arquivo bases/grupo1/bitcoin.xlsx.</p>
<p><strong>Período.</strong> A série documentada vai de 22/08/2018 a 11/09/2026. A comparação comum dos quatro modelos vai de 09/05/2024 a 11/09/2026. O corte da matriz tabular é 08/05/2024.</p>
<p><strong>Frequência.</strong> Diária, depois da reindexação para a grade civil.</p>
<p><strong>Alvo e unidade.</strong> Fechamento priceClose do dia seguinte, em dólar americano. O lag 1 é o fechamento do dia da origem.</p>
<p><strong>Externas.</strong> Volume negociado, retorno, amplitude entre máxima e mínima, pressão de volume, RSI e o calendário. Há mais de duas externas. O dicionário operacional tem 51 atributos, gravados em analyses/grupo1/01_dados/feature_metadata.json. Random Forest e PLS usam os 51. O SARIMAX usa as exógenas dessa matriz.</p>
<table>
  <caption>Tabela 4 – Dicionário da matriz do Bitcoin</caption>
  <thead><tr><th>Família</th><th>Colunas</th></tr></thead>
  <tbody>
    <tr><td>Lags do fechamento</td><td>close_lag1, 2, 3, 5, 7, 14, 21 e 30; log_close_lag1 e log_close_lag7</td></tr>
    <tr><td>Volume, retorno e amplitude</td><td>vol_lag1, 3 e 7; return_lag1, 2 e 3; range_lag1 e range_lag3; vol_pressure_lag1; oc_ratio_lag1</td></tr>
    <tr><td>Médias e desvios</td><td>close_ma7, 14, 21, 30, 60 e 90; close_std7, 14 e 30; vol_ma7, 14 e 30; ratio_close_ma7 e ratio_close_ma30</td></tr>
    <tr><td>Outra de mercado</td><td>rsi_14</td></tr>
    <tr><td>Calendário ordinal</td><td>day_of_week, day_of_month, day_of_year, month, quarter, year, week_of_year, is_weekend</td></tr>
    <tr><td>Calendário cíclico</td><td>dow_sin, dow_cos, month_sin, month_cos, doy_sin, doy_cos, quarter_sin, quarter_cos</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: analyses/grupo1/01_dados/feature_metadata.json (2026). São 51 colunas.</p>
<p><strong>Ausências.</strong> Cinco lacunas de 2023, depois da reindexação diária, foram interpoladas linearmente.</p>
<p><strong>Duplicidades.</strong> A grade de modelagem tem um registro por dia.</p>
<p><strong>Irregularidades.</strong> A série foi reindexada para a grade diária. A comparação entre modelos usa os 856 dias em que os quatro têm previsão.</p>
<p><strong>Atípicos.</strong> Os extremos de preço permaneceram na série. O diagnóstico residual do Holt-Winters ainda aponta resíduo não normal e efeito ARCH.</p>
<p><strong>Limpeza.</strong> Colunas de instante de máxima, mínima e fechamento saíram. As cinco lacunas de 2023 foram interpoladas. Médias e desvios são calculados depois do deslocamento, para a janela terminar na origem.</p>
<p><strong>Disponibilidade.</strong> Volume, retorno e preço usados como preditor são os já observados na origem. O fechamento do dia seguinte é só o alvo. A padronização do PLS e do SARIMAX usa a janela de treino da origem. O teste começa depois do corte de 08/05/2024. A série, as externas e o gráfico de resíduos estão no notebook de analyses/grupo1. Este PDF cita esses gráficos e deixa de redesenhá-los.</p>
<h2 id="s32">3.2 Decomposição STL</h2>
<p>A STL foi feita nos períodos de 7 e de 30 dias. A força de tendência é 0,9967 e 0,9897. Quase todo o movimento lento do preço fica na tendência: alta, queda e mudança de direção do fechamento aparecem nesse componente. A força sazonal é 0,0000 nos dois períodos, então o calendário semanal e o de 30 dias não se separam do ruído. A força sazonal anual não foi impressa, e este relatório não a estima. O resíduo carrega o choque de preço que a tendência não absorveu. A força usada é Fs = max(0, 1 − Var(R) / Var(S+R)), no sentido de Cleveland et al. (1990) e de Hyndman e Athanasopoulos (2021). Força zero justificou um Holt-Winters sem componente sazonal.</p>
<table>
  <caption>Tabela 5 – Forças da STL do Bitcoin</caption>
  <thead><tr><th>Período</th><th class="n">Força sazonal</th><th class="n">Força de tendência</th></tr></thead>
  <tbody>
    <tr><td>7 dias</td><td class="n">0,0000</td><td class="n">0,9967</td></tr>
    <tr><td>30 dias</td><td class="n">0,0000</td><td class="n">0,9897</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: notebook de STL de analyses/grupo1 (2026).</p>
<h2 id="s33">3.3 Feature engineering</h2>
<p>O alvo é o fechamento de t+1 e o lag 1 é o fechamento de t. Há lags até 30 dias, médias de 7 a 90 dias e desvios de 7, 14 e 30 dias. Volume, retorno e amplitude entram defasados. O calendário entra em forma ordinal e em seno e cosseno. O aquecimento descarta o começo até a janela mais longa estar preenchida. O treino tabular tem 1.996 linhas. Random Forest e PLS compartilham os 51 atributos. Nenhuma coluna usa o fechamento do dia que se quer prever.</p>
<h2 id="s34">3.4 Modelos e hiperparâmetros</h2>
<p>Holt-Winters percorreu 21 configurações, todas válidas, com TimeSeriesSplit de 3 dobras e 90 dias por dobra, critério MAE de validação cruzada. O PLS usou TimeSeriesSplit de 5 dobras. O teste comum, a partir de 09/05/2024, ficou fora da escolha. A semente registrada é 42.</p>
<p><strong>SARIMAX.</strong> Ordem (0, 0, 1) × (0, 0, 0, 7): um MA(1), sem diferença e sem termo sazonal ativo, com as exógenas da matriz. A tabela de coeficiente, sinal e p-valor de cada externa não foi exportada nesta base.</p>
<p><strong>Holt-Winters.</strong> Tendência multiplicativa, sazonalidade nula, amortecimento desligado. Suavização do nível 0,9243 e suavização da tendência 0,0225. O nível acompanha o fechamento de perto. A tendência multiplicativa atualiza devagar e descreve um drift do preço. Não há componente sazonal, em linha com a força sazonal zero.</p>
<p><strong>Random Forest.</strong> 300 árvores, profundidade máxima 8, mínimo 2 para dividir, folha mínima 4, max_features 0,7.</p>
<p><strong>PLS.</strong> 9 componentes em 51 atributos, com padronização.</p>
<h2 id="s35">3.5 Walk-forward</h2>
<p>A janela tabular corta em 08/05/2024, com 1.996 linhas de treino. O horizonte é um dia. As origens comuns são 856 dias, de 09/05/2024 a 11/09/2026, as mesmas para os quatro modelos. Cada origem usa só o que já foi observado até aquele dia. O Holt-Winters também tem 883 previsões desde 12/04/2024; o ranking usa as 856. Os hiperparâmetros finais ficam fixos nesse teste. O arquivo consolidado de MAE desta base não traz a persistência, e este relatório não inventa esse número.</p>
<h2 id="s36">3.6 MAE</h2>
<table>
  <caption>Tabela 6 – MAE de teste do Bitcoin</caption>
  <thead><tr><th class="n">Posição</th><th>Modelo</th><th class="n">MAE (USD)</th><th class="n">Previsões</th></tr></thead>
  <tbody>
    <tr><td class="n">1</td><td>Holt-Winters</td><td class="n">1.406,54</td><td class="n">856</td></tr>
    <tr><td class="n">2</td><td>SARIMAX</td><td class="n">1.590,77</td><td class="n">856</td></tr>
    <tr><td class="n">3</td><td>Random Forest</td><td class="n">2.108,00</td><td class="n">856</td></tr>
    <tr><td class="n">4</td><td>PLS</td><td class="n">2.608,61</td><td class="n">856</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: docs/relatorios/consolidado/mae_consolidado.csv (2026).</p>
<p>O vencedor é o Holt-Winters. Na janela própria de 883 dias, o MAE dele é 1.407,98. O alisador ganha porque a STL mostra um nível com tendência forte e sazonalidade medida nula. O SARIMAX fica em segundo. Random Forest e PLS, sobre 51 colunas muito colineares, ficam atrás. Esta é uma das duas vitórias do Holt-Winters.</p>
<h2 id="s37">3.7 Resíduos e importância</h2>
<p>O gráfico de resíduos e a ACF estão no notebook da base. No Holt-Winters, os lags 1, 3, 5, 7, 14, 21 e 30 não rejeitam ruído branco a 5%. O lag 1 tem p = 0,455. SARIMAX rejeita no lag 1, com p = 0,0025. Random Forest e PLS também rejeitam no lag 1, com p inferior ao do SARIMAX; o p exato desses dois está no CSV da base. Nos 883 resíduos do Holt-Winters, a média é −11,90 USD, o desvio é 1.961,77 e o teste de viés tem p = 0,857. Nos 856 dias comuns, as médias são +693,86 no SARIMAX, +240,77 no Random Forest e −336,25 no PLS, todas com viés significativo. Média positiva significa previsão abaixo do observado (LJUNG; BOX, 1978). O desvio largo mostra que o erro típico continua grande quando a média do Holt-Winters é compatível com zero. O arquivo ainda aponta resíduo não normal e efeito ARCH.</p>
<p>No Random Forest, a impureza é 0,448 em log_close_lag1, 0,363 em close_lag1 e 0,055 em close_lag2. A permutação no teste repete essa ordem de perto. No PLS, o maior coeficiente padronizado, em módulo, é close_lag1, com 0,153. O fechamento recente domina. A ordem do SARIMAX está registrada, e a tabela de significância de cada externa não foi exportada.</p>
"""


def pm25():
    return r"""
<h1 class="sec" id="s4">4 PM2.5 de Aotizhongxin</h1>
<p>Série horária de concentração. Random Forest vence por uma margem pequena sobre o PLS. O ciclo de 24 horas medido pela STL é fraco, e o valor recente da própria concentração organiza o passo seguinte.</p>
<h2 id="s41">4.1 Identificação da série</h2>
<p><strong>Fonte.</strong> UCI, Beijing Multi-Site Air-Quality, estação Aotizhongxin, com vizinhas Changping e Wanliu. Os quatro CSVs de estação têm SHA-256 em bases/grupo3/SHA256SUMS.txt.</p>
<p><strong>Período.</strong> De 01/03/2013 a 28/02/2017. O teste começa em 16/05/2016 05:00 e segue até 28/02/2017 22:00.</p>
<p><strong>Frequência.</strong> Horária.</p>
<p><strong>Alvo e unidade.</strong> Concentração de PM2.5 da hora seguinte na estação Aotizhongxin, em micrograma por metro cúbico.</p>
<p><strong>Externas.</strong> PM10, CO, temperatura, ponto de orvalho e vento locais, e o PM2.5 de Changping e Wanliu. A meteorologia de Guanyuan foi excluída por repetir a estação local. A matriz vigente tem 17 colunas e 30.062 linhas. Uma matriz exploratória de 671 colunas existe e não é a do resultado.</p>
<table>
  <caption>Tabela 7 – Dicionário vigente do PM2.5 e o instante em que a coluna existe</caption>
  <thead><tr><th>Coluna</th><th>Disponível em</th></tr></thead>
  <tbody>
    <tr><td>pm25_t, pm25_t_1, pm25_t_2, pm25_t_23</td><td>origem t</td></tr>
    <tr><td>pm25_roll_mean_3, pm25_roll_mean_24</td><td>origem t</td></tr>
    <tr><td>local_PM10, local_CO, local_TEMP, local_WSPM, local_DEWP</td><td>origem t</td></tr>
    <tr><td>Changping_PM2.5, Wanliu_PM2.5</td><td>origem t</td></tr>
    <tr><td>target_hour_sin, target_hour_cos, target_dow_sin, target_dow_cos</td><td>hora e dia do alvo, conhecidos antes</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: analyses/grupo3/01_dados/outputs/dicionario_modelagem_base3.csv (2026).</p>
<p><strong>Ausências.</strong> O alvo tem 925 horas ausentes, preservadas. A concentração que se quer prever não foi imputada. Nos preditores, o preenchimento é o último valor já observado.</p>
<p><strong>Duplicidades e irregularidades.</strong> A grade tem um registro por hora. As 925 horas sem alvo permanecem como buracos do alvo. A STL usou uma cópia interpolada só para a decomposição.</p>
<p><strong>Atípicos e limpeza.</strong> Previsão negativa de concentração foi cortada em zero no teste. O alvo observado permaneceu. Preditores do PLS e do SARIMAX são padronizados na janela de treino de cada ajuste.</p>
<p><strong>Disponibilidade.</strong> A matriz exploratória de 671 colunas deixava o lag mais recente em t−1 quando o rótulo era t+1, e foi separada da matriz vigente. O teste começa depois da validação.</p>
<figure>
  <figcaption>Figura 1 – PM2.5 horário em Aotizhongxin</figcaption>
  <img src="../../../analyses/grupo3/01_dados/outputs/eda/evolucao_temporal_pm25.png" alt="Série de PM2.5">
</figure>
<p class="fonte">Fonte: analyses/grupo3/01_dados/outputs/eda/evolucao_temporal_pm25.png (2026). Perfil horário, perfil semanal e mapa de correlação das externas estão na mesma pasta eda/.</p>
<h2 id="s42">4.2 Decomposição STL</h2>
<p>A STL primária usa o período de 24 horas, com um diagnóstico de 168 horas. A força de tendência é 0,2869 no dia e 0,1573 na semana: o nível varia, e a maior parte da hora a hora fica fora da tendência. Alta e queda de algumas horas ficam no resíduo e no ciclo fraco. A força sazonal é 0,0130 em 24 horas e 0,0708 em 168 horas. O resíduo concentra o choque horário. A cópia interpolada da STL não substitui a série dos modelos. Versões sazonais do Holt-Winters tiveram MAE de validação entre 50 e 69. A suavização simples teve 13,96.</p>
<table>
  <caption>Tabela 8 – Forças da STL do PM2.5</caption>
  <thead><tr><th>Período</th><th class="n">Força sazonal</th><th class="n">Força de tendência</th></tr></thead>
  <tbody>
    <tr><td>24 horas</td><td class="n">0,0130</td><td class="n">0,2869</td></tr>
    <tr><td>168 horas</td><td class="n">0,0708</td><td class="n">0,1573</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: arquivos de STL de analyses/grupo3 (2026).</p>
<figure>
  <figcaption>Figura 2 – STL primária do PM2.5</figcaption>
  <img src="../../../analyses/grupo3/01_dados/outputs/stl/stl_primary_decomposition.png" alt="STL do PM2.5">
</figure>
<p class="fonte">Fonte: analyses/grupo3/01_dados/outputs/stl/stl_primary_decomposition.png (2026).</p>
<h2 id="s43">4.3 Feature engineering</h2>
<p>A matriz vigente inclui o PM2.5 da origem e os lags 1, 2 e 23, médias de 3 e de 24 horas, cinco medidas locais, duas vizinhas e o seno e o cosseno da hora e do dia da semana do alvo. As janelas terminam na origem. Linhas incompletas saem. O alvo ausente não entra no MAE. Random Forest e PLS usam as 17 colunas. A busca usa treino até 25/09/2015 e validação até 16/05/2016.</p>
<h2 id="s44">4.4 Modelos e hiperparâmetros</h2>
<p>O critério é o menor MAE de validação. O AIC do SARIMAX foi diagnóstico. O Random Forest percorreu seis configurações. O PLS percorreu seis números de componentes. A semente é 42. As 6.023 horas de teste ficaram fora da busca.</p>
<p><strong>SARIMAX.</strong> Ordem (0, 1, 1), sem parte sazonal, MAE de validação 11,07. A ordem (0, 1, 1) × (0, 1, 1, 24) teve AIC 2.487,94 numa janela de 14 dias e MAE de validação 12,20. O protocolo ficou com o MAE. A tabela de p-valor das externas não foi exportada. Houve zero fallback no teste.</p>
<p><strong>Holt-Winters.</strong> Suavização exponencial simples: há nível, e tendência e sazonalidade ficam desligadas. Validação 13,96. Tendência isolada ficou em 14,98. No teste, 24 origens usaram fallback de persistência. O nível segue a concentração recente.</p>
<p><strong>Random Forest.</strong> 40 árvores, profundidade máxima 12, mínimo 2 para dividir, folha mínima 5, max_features 0,5. Validação 10,7430.</p>
<p><strong>PLS.</strong> 14 componentes. Na grade 2, 4, 8, 12, 14 e 16, o mínimo de validação foi 10,6265 em 14 componentes. Com 16, subiu para 10,6350.</p>
<h2 id="s45">4.5 Walk-forward</h2>
<p>O treino vai até 25/09/2015 06:00, com 19.494 origens. A validação vai até 16/05/2016 04:00, com 4.545 origens. O horizonte é uma hora. O teste tem 6.023 horas a partir de 16/05/2016 05:00, as mesmas para os quatro. Holt-Winters reajusta em toda origem numa janela de 21 dias. Os outros três reajustam uma vez por dia, incorporando as horas já observadas. Os hiperparâmetros da validação ficam fixos.</p>
<h2 id="s46">4.6 MAE</h2>
<table>
  <caption>Tabela 9 – MAE de teste do PM2.5</caption>
  <thead><tr><th class="n">Posição</th><th>Modelo</th><th class="n">MAE (µg/m³)</th><th class="n">Previsões</th></tr></thead>
  <tbody>
    <tr><td class="n">1</td><td>Random Forest</td><td class="n">9,5131</td><td class="n">6.023</td></tr>
    <tr><td class="n">2</td><td>PLS</td><td class="n">9,6643</td><td class="n">6.023</td></tr>
    <tr><td class="n">3</td><td>SARIMAX</td><td class="n">10,2225</td><td class="n">6.023</td></tr>
    <tr><td class="n">4</td><td>Holt-Winters</td><td class="n">12,9122</td><td class="n">6.023</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: docs/relatorios/consolidado/mae_consolidado.csv (2026).</p>
<p>O vencedor é o Random Forest. O PLS fica a 0,15 µg/m³. Os dois usam a mesma matriz. O SARIMAX fica em terceiro. O Holt-Winters, só com o nível, fica em quarto. Esta é uma das duas vitórias do Random Forest.</p>
<h2 id="s47">4.7 Resíduos e importância</h2>
<figure>
  <figcaption>Figura 3 – Resíduos do PM2.5 nas 6.023 horas de teste</figcaption>
  <img src="../../../analyses/grupo3/03_resultados/outputs/serie_residuos.png" alt="Série de resíduos do PM2.5">
</figure>
<p class="fonte">Fonte: analyses/grupo3/03_resultados/outputs/serie_residuos.png (2026).</p>
<figure>
  <figcaption>Figura 4 – ACF dos resíduos do PM2.5</figcaption>
  <img src="../../../analyses/grupo3/03_resultados/outputs/acf_residuos.png" alt="ACF do PM2.5">
</figure>
<p class="fonte">Fonte: analyses/grupo3/03_resultados/outputs/acf_residuos.png (2026).</p>
<p>No lag 24, os quatro rejeitam a 5%. Holt-Winters tem p impresso como 0. SARIMAX tem p = 1,51×10⁻²¹. Random Forest tem p = 1,74×10⁻⁵⁰. PLS tem p = 4,09×10⁻¹⁵. Com 6.023 horas, o teste detecta autocorrelação pequena. As médias do resíduo são +0,056 no Holt-Winters, −0,101 no SARIMAX, +0,588 no Random Forest e +0,548 no PLS, em µg/m³. Os desvios são 23,75, 18,03, 17,71 e 17,60, na mesma ordem. O padrão que permanece é o ciclo de 24 horas.</p>
<p>Num ajuste único no treino interno, a impureza do Random Forest é 0,547 em pm25_t, 0,231 na média de 3 horas e 0,095 no PM2.5 de Wanliu. Essa conta é desse ajuste. O VIP do PLS começa em pm25_t (1,52), média de 3 horas (1,43) e lag 1 (1,41). O maior coeficiente padronizado, em módulo, é o seno da hora alvo, 1,93. Wanliu aparece na impureza e o vento aparece no coeficiente. As duas já estão observadas na origem. Há AIC e BIC da busca do SARIMAX, e a tabela de p-valor de cada externa não foi exportada. O Holt-Winters escolhido tem só nível.</p>
"""


def jena():
    return r"""
<h1 class="sec" id="s5">5 Temperatura horária de Jena</h1>
<p>Série horária de temperatura do ar. O PLS vence. A STL mostra ciclo diário forte, e a meteorologia defasada entra junto com os lags da temperatura. Os números saem da carga executada do notebook analyses/grupo4/trabalho_grupo5_pls_jena_horario.ipynb.</p>
<h2 id="s51">5.1 Identificação da série</h2>
<p><strong>Fonte.</strong> Conjunto climático do Max-Planck-Institut für Biogeochemie. O notebook lê bases/grupo4/jena_climate_2009_2016.csv.</p>
<p><strong>Período.</strong> A carga executada tem 70.127 horas, de 01/01/2009 a 31/12/2016. O cabeçalho do notebook menciona um recorte até 09/01/2012. Este relatório usa a carga executada. O desenvolvimento vai de 01/01/2009 01:00 a 27/05/2015 13:00 (56.101 horas). O teste reservado vai de 27/05/2015 14:00 a 31/12/2016 23:00.</p>
<p><strong>Frequência.</strong> Horária. A série nasce em medições de 10 minutos e vira a média das seis leituras da hora.</p>
<p><strong>Alvo e unidade.</strong> Temperatura do ar T (degC) da hora seguinte, em grau Celsius.</p>
<p><strong>Externas.</strong> Pressão, umidade, velocidade do vento, direção do vento, ponto de orvalho, déficit de pressão de vapor e densidade, sempre com defasagem, mais seno e cosseno da hora e do dia do ano. Random Forest e PLS usam as 46 colunas. O SARIMAX usa cinco externas: p_lag1, rh_lag1, wv_lag1, wd_sin e wd_cos.</p>
<table>
  <caption>Tabela 10 – Dicionário das 46 colunas de Jena</caption>
  <thead><tr><th>Família</th><th>Colunas</th></tr></thead>
  <tbody>
    <tr><td>Lags da temperatura</td><td>T_lag1, 2, 3, 6, 12, 24, 48 e 168</td></tr>
    <tr><td>Diferenças</td><td>T_diff1 e T_diff24</td></tr>
    <tr><td>Janelas, depois do deslocamento</td><td>média, desvio, mínimo e máximo em 6, 24 e 168 horas</td></tr>
    <tr><td>Externas defasadas</td><td>para p, rh, wv, VPdef, rho e Tdew: lag 1, diferença de 1 hora e diferença de 24 horas</td></tr>
    <tr><td>Direção do vento</td><td>wd_sin e wd_cos, sobre a direção já deslocada</td></tr>
    <tr><td>Calendário</td><td>hod_sin, hod_cos, doy_sin, doy_cos</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: função build_features da carga executada do notebook de Jena (2026).</p>
<p><strong>Ausências, duplicidades e irregularidades.</strong> Horas incompletas nas bordas foram descartadas. O aquecimento de 168 horas tira o começo da matriz. A grade horária tem um registro por hora. Bins de 10 minutos incompletos nas bordas saíram na agregação.</p>
<p><strong>Atípicos e limpeza.</strong> Leituras sentinela negativas de vento e saltos de pressão acima de 15 mbar em relação à mediana passada foram tratados na preparação do notebook. A auditoria de causalidade em cinco origens foi aprovada: perturbar o futuro não muda o vetor da origem.</p>
<p><strong>Disponibilidade.</strong> Pressão, umidade, vento e densidade da hora que se quer prever ficam de fora. Entra o valor já visto até a origem. A padronização usa a janela de treino. O teste é o último 20% cronológico. Série, externas, STL, real contra previsto e resíduos estão nas 18 imagens do notebook executado.</p>
<h2 id="s52">5.2 Decomposição STL</h2>
<p>A STL robusta foi feita no desenvolvimento, período de 24 horas. A força de tendência é 0,953: o componente absorve o que varia mais devagar que um dia, o ciclo anual e as ondas de calor. Alta e queda do ano, e a mudança de direção entre estações, ficam na tendência. Dentro do dia, a subida da manhã e a queda da noite ficam na sazonalidade, cuja força é 0,686. O resíduo é o desvio da hora em relação ao perfil diário médio e à onda lenta. Força diária alta colocou sazonalidade na grade: o Holt-Winters escolhido é aditivo com período 24, e o SARIMAX manteve a diferença sazonal de 24 horas.</p>
<h2 id="s53">5.3 Feature engineering</h2>
<p>Os lags da temperatura vão de 1 a 168 horas. As janelas trazem média, desvio, mínimo e máximo. As seis externas meteorológicas entram com lag e com duas diferenças, todas deslocadas. A direção vira seno e cosseno. Hora e dia do ano entram em seno e cosseno. As primeiras 168 horas saem. Random Forest e PLS usam as 46 colunas. O conjunto só com temperatura e calendário foi testado na grade do PLS e perdeu para o conjunto com externas. Três blocos de validação de 14 dias fecham o desenvolvimento.</p>
<h2 id="s54">5.4 Modelos e hiperparâmetros</h2>
<p>A partição é cronológica 80/20. A escolha é o menor MAE nos blocos de validação. A semente é 42. As 14.026 horas de teste ficaram fora da busca.</p>
<p><strong>SARIMAX.</strong> Ordem (2, 0, 1) × (0, 1, 1, 24), com as cinco externas, validação 0,4565. Sem externas, a validação sobe para 0,4660. Os coeficientes estão no notebook. O ganho das externas na validação é de 0,0095 °C.</p>
<p><strong>Holt-Winters.</strong> Tendência aditiva amortecida e sazonalidade aditiva de 24 horas. Validação 0,4909. O nível é a temperatura alisada. A tendência amortecida é um drift que perde força. A sazonalidade é o perfil das 24 horas.</p>
<p><strong>Random Forest.</strong> 500 árvores, profundidade livre, max_features 0,8, mínimo 2 para dividir, folha mínima 1. Validação 0,4629. A grade percorreu doze configurações, de 300 a 800 árvores.</p>
<p><strong>PLS.</strong> 40 componentes de 46 atributos, conjunto com externas. Validação 0,4601. A grade de componentes foi 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 35, 40 e 46, nos dois conjuntos de colunas.</p>
<h2 id="s55">5.5 Walk-forward</h2>
<p>O desenvolvimento tem 56.101 horas, até 27/05/2015 13:00. O horizonte é uma hora. O teste tem 14.026 horas, de 27/05/2015 14:00 a 31/12/2016 23:00, as mesmas para os quatro. O teste é repartido em 42 blocos de 336 horas, o último com 250. Cada bloco incorpora as horas reais já ocorridas. Os hiperparâmetros da validação ficam fixos. A persistência tem MAE 0,6813 °C nas mesmas horas e fica fora do ranking.</p>
<h2 id="s56">5.6 MAE</h2>
<table>
  <caption>Tabela 11 – MAE de teste de Jena</caption>
  <thead><tr><th class="n">Posição</th><th>Modelo</th><th class="n">MAE (°C)</th><th class="n">Previsões</th></tr></thead>
  <tbody>
    <tr><td class="n">1</td><td>PLS</td><td class="n">0,3983</td><td class="n">14.026</td></tr>
    <tr><td class="n">2</td><td>SARIMAX</td><td class="n">0,4064</td><td class="n">14.026</td></tr>
    <tr><td class="n">3</td><td>Random Forest</td><td class="n">0,4114</td><td class="n">14.026</td></tr>
    <tr><td class="n">4</td><td>Holt-Winters</td><td class="n">0,4259</td><td class="n">14.026</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: carga executada do notebook de Jena e mae_consolidado.csv (2026).</p>
<p>O vencedor é o PLS. Ele reduz a persistência de 0,6813 °C em 41,5%. Em 42 blocos, vence 21, com posição média de bloco 1,762. SARIMAX vence 9 blocos (posição média 2,286), Random Forest vence 11 (2,357) e Holt-Winters vence 1 (3,595). Esta é a vitória do PLS nas cinco bases.</p>
<h2 id="s57">5.7 Resíduos e importância</h2>
<p>Série residual e ACF estão no notebook. No PLS, a ACF é −0,0027 no lag 1 e −0,0129 no lag 24. A persistência, no mesmo teste, tem ACF 0,71 no lag 1. No lag 24, o p do Ljung-Box impresso é 0 para os quatro modelos e também para a persistência. Com 14.026 horas, autocorrelação pequena rejeita a hipótese de ruído branco. O viés é +0,0071 °C no PLS, 0,0000 °C no SARIMAX e +0,0147 °C no Random Forest. O RMSE do Holt-Winters é 0,6188, acima do MAE 0,4259.</p>
<p>A impureza média do Random Forest em 16 reajustes é 0,7847 em T_lag1. O VIP do PLS é 1,5750 em T_lag1, 1,5477 em T_lag2 e 1,5147 em rho_lag1. A permutação do MAE em 16 blocos dá 1,2810 a T_lag2, 1,2805 a T_lag1 e 0,8770 a rho_lag1. A densidade defasada é a externa que acompanha os lags de temperatura e já está observada na origem. Tirar as externas do SARIMAX piorou a validação de 0,4565 para 0,4660. Os coeficientes do SARIMAX estão no notebook.</p>
"""


def ouro():
    return r"""
<h1 class="sec" id="s6">6 Ouro diário de Londres</h1>
<p>Fixing da tarde, em dólar por onça fina. O Holt-Winters vence o teste por uma margem de centavos sobre o SARIMAX e o PLS. A validação tinha escolhido o PLS. Os hiperparâmetros continuam os da validação.</p>
<h2 id="s61">6.1 Identificação da série</h2>
<p><strong>Fonte.</strong> Fixing da tarde em Londres, série BBEX3.D.XAU.USD.EA.AC.C05 do Deutsche Bundesbank. O arquivo de aquisição está em analyses/grupo5/outputs/protocol.json. O SHA-256 da matriz de modelagem é 38622fe40a18c3e94b89971488468f762353ed4234234e054f0439918cb5d1ac.</p>
<p><strong>Período.</strong> A série bruta tem 12.009 registros, de 1º/04/1968 a 10/04/2014. Desses, 11.641 têm preço válido e 368 têm GOLD_PRICE ausente. Depois das exigências causais de alvo, lags, janelas e externas, restam 9.864 observações modeláveis. O treino termina no índice 6.904 e a validação no índice 8.384. Os 296 alvos de teste vão de 07/06/2007 a 04/04/2014.</p>
<p><strong>Frequência.</strong> Dias de mercado. O passo de teste é de cinco observações, com intervalo mediano de sete dias entre os alvos.</p>
<p><strong>Alvo e unidade.</strong> Preço do próximo fixing de tarde, em dólar americano por onça fina de 31,1034768 gramas.</p>
<p><strong>Externas.</strong> Treasury de 10 anos (DGS10) e taxa de fundos federais (DFF), os dois defasados uma observação de ouro, mais seno e cosseno do dia da semana e do mês.</p>
<table>
  <caption>Tabela 12 – Dicionário das 12 colunas do ouro</caption>
  <thead><tr><th>Coluna</th><th>O que entra</th><th>Conhecida na origem</th></tr></thead>
  <tbody>
    <tr><td>GOLD_PRICE</td><td>preço na data da origem</td><td>sim</td></tr>
    <tr><td>TREASURY_10Y</td><td>último DGS10 antes da origem, com deslocamento</td><td>sim</td></tr>
    <tr><td>FED_FUNDS_RATE</td><td>último DFF antes da origem, com deslocamento</td><td>sim</td></tr>
    <tr><td>DOW_SIN, DOW_COS</td><td>dia da semana da origem</td><td>sim</td></tr>
    <tr><td>MONTH_SIN, MONTH_COS</td><td>mês da origem</td><td>sim</td></tr>
    <tr><td>GOLD_LAG_1, 5 e 20</td><td>preços anteriores no calendário bruto</td><td>sim</td></tr>
    <tr><td>GOLD_ROLLING_MEAN_5</td><td>média dos cinco preços anteriores à origem</td><td>sim</td></tr>
    <tr><td>GOLD_ROLLING_STD_5</td><td>desvio dos cinco preços anteriores à origem</td><td>sim</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: analyses/grupo5/outputs/feature_dictionary.csv (2026).</p>
<p><strong>Ausências.</strong> Os 368 preços ausentes permanecem ausentes no arquivo bruto. O pipeline não interpola o preço, não aplica forward fill e não aplica backfill ao ouro. O forward fill vale só para as externas, e antes da defasagem de uma observação. Linhas sem preço saem da base modelável.</p>
<p><strong>Duplicidades.</strong> A auditoria de qualidade registra uma data por observação, na base bruta e na modelável.</p>
<p><strong>Irregularidades.</strong> Na base modelável, o maior intervalo é de 20 dias e há 401 intervalos acima de três dias. Esses buracos refletem o calendário de mercado, feriados e a exclusão causal de linhas incompletas. Permaneceram sem preenchimento.</p>
<p><strong>Atípicos.</strong> A auditoria descritiva sinalizou 1.416 observações extremas pelo IQR no nível do preço e 480 retornos extremos pelo MAD. O IQR no nível descreve uma série longa, com regimes diferentes, e não foi usado como filtro. Entre os maiores movimentos diários estão 09/01/1980 (+26,18%), 07/09/1982 (+17,01%), 05/06/1973 (+15,72%) e 24/01/1980 (−15,54%), além de movimentos em 2006, 2008 e 2011. Nenhum outlier foi removido ou winsorizado.</p>
<p><strong>Limpeza.</strong> Feriado ficou de fora por falta de fonte reproduzível. Dia da semana e mês ordinais ficaram de fora. Treasury e fundos entram com uma defasagem.</p>
<figure>
  <figcaption>Figura 5 – Preço do ouro usado na modelagem</figcaption>
  <img src="../../../analyses/grupo5/outputs/graficos/gold_price_full.png" alt="Série do ouro">
</figure>
<p class="fonte">Fonte: analyses/grupo5/outputs/graficos/gold_price_full.png (2026).</p>
<figure>
  <figcaption>Figura 6 – Treasury de 10 anos</figcaption>
  <img src="../../../analyses/grupo5/outputs/graficos/treasury_10y_full.png" alt="Treasury">
</figure>
<p class="fonte">Fonte: analyses/grupo5/outputs/graficos/treasury_10y_full.png (2026).</p>
<figure>
  <figcaption>Figura 7 – Taxa de fundos federais</figcaption>
  <img src="../../../analyses/grupo5/outputs/graficos/fed_funds_rate_full.png" alt="Fed funds">
</figure>
<p class="fonte">Fonte: analyses/grupo5/outputs/graficos/fed_funds_rate_full.png (2026).</p>
<h2 id="s62">6.2 Decomposição STL</h2>
<p>A STL do treino usa os períodos de 5, 20 e 252 observações. A força de tendência é 0,998, 0,991 e 0,923. Alta, queda e mudança de direção do nível ficam na tendência. A força sazonal é 0 nos três períodos: semana de mercado, bloco de 20 observações e ano de pregão não se separam do resíduo. O choque diário, como os movimentos de 1973, 1980 e 1982, permanece na série. O período 5 do Holt-Winters entrou como referência de semana de mercado, com essa força nula explícita.</p>
<table>
  <caption>Tabela 13 – Forças da STL do ouro</caption>
  <thead><tr><th>Período</th><th class="n">Força sazonal</th><th class="n">Força de tendência</th></tr></thead>
  <tbody>
    <tr><td>5 observações</td><td class="n">0,000</td><td class="n">0,998</td></tr>
    <tr><td>20 observações</td><td class="n">0,000</td><td class="n">0,991</td></tr>
    <tr><td>252 observações</td><td class="n">0,000</td><td class="n">0,923</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: analyses/grupo5/outputs (2026).</p>
<figure>
  <figcaption>Figura 8 – STL do ouro no período de 5 observações</figcaption>
  <img src="../../../analyses/grupo5/outputs/stl_period_5.png" alt="STL do ouro">
</figure>
<p class="fonte">Fonte: analyses/grupo5/outputs/stl_period_5.png (2026).</p>
<h2 id="s63">6.3 Feature engineering</h2>
<p>Entram o preço na origem, os lags 1, 5 e 20, a média e o desvio de cinco preços anteriores, Treasury, fundos e o calendário circular. A média e o desvio usam o preço deslocado, então a janela termina antes da origem. Random Forest e PLS usam as 12 colunas. O SARIMAX usa Treasury, fundos e o calendário circular. Nenhuma coluna usa o fixing que se quer prever. Empate de validação em três casas resolve por simplicidade e, ainda empatando, por tempo.</p>
<h2 id="s64">6.4 Modelos e hiperparâmetros</h2>
<p>A grade está nos notebooks de otimização e o vencedor está no protocolo. O critério é o MAE de validação. As 296 origens de teste ficaram fora da busca. A semente é 42.</p>
<p><strong>SARIMAX.</strong> Ordem (0, 1, 2) × (0, 0, 1, 5). Validação 2,9844. A tabela seguinte é o ajuste da primeira origem de teste, em analyses/grupo5/outputs/sarimax_coefficients.csv.</p>
<table>
  <caption>Tabela 14 – Coeficientes do SARIMAX do ouro na primeira origem de teste</caption>
  <thead><tr><th>Termo</th><th class="n">Coeficiente</th><th class="n">p-valor</th><th>Leitura a 5%</th></tr></thead>
  <tbody>
    <tr><td>TREASURY_10Y</td><td class="n">−2,328</td><td class="n">5,9×10⁻⁷</td><td>significativo, sinal negativo</td></tr>
    <tr><td>FED_FUNDS_RATE</td><td class="n">−0,242</td><td class="n">0,037</td><td>significativo, sinal negativo</td></tr>
    <tr><td>DOW_SIN</td><td class="n">0,054</td><td class="n">0,594</td><td>não significativo</td></tr>
    <tr><td>DOW_COS</td><td class="n">0,075</td><td class="n">0,243</td><td>não significativo</td></tr>
    <tr><td>MONTH_SIN</td><td class="n">0,721</td><td class="n">0,061</td><td>acima de 5%</td></tr>
    <tr><td>MONTH_COS</td><td class="n">0,806</td><td class="n">0,132</td><td>não significativo</td></tr>
    <tr><td>ma.L1</td><td class="n">−0,048</td><td class="n">≈ 0</td><td>significativo</td></tr>
    <tr><td>ma.L2</td><td class="n">0,018</td><td class="n">≈ 0</td><td>significativo</td></tr>
    <tr><td>ma.S.L5</td><td class="n">0,048</td><td class="n">≈ 0</td><td>significativo</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: analyses/grupo5/outputs/sarimax_coefficients.csv (2026).</p>
<p>Treasury e fundos têm sinal negativo nesse ajuste. O calendário circular não chega a 5%. Os termos de média móvel são significativos e pequenos.</p>
<p><strong>Holt-Winters.</strong> Tendência aditiva, sazonalidade aditiva, período 5, amortecimento desligado. Validação 2,9760. Nas origens de validação gravadas, o peso do nível fica em torno de 0,942 e os pesos de tendência e de sazonalidade ficam em 0. O nível absorve a observação nova. Tendência e perfil de cinco dias permanecem na estrutura e deixam de se atualizar, em linha com a força sazonal zero.</p>
<p><strong>Random Forest.</strong> 300 árvores, profundidade máxima 20, max_features 1,0, folha mínima 5, mínimo 10 para dividir. Validação 3,3263.</p>
<p><strong>PLS.</strong> 11 componentes de 12 atributos. Validação 2,9701, a menor da base.</p>
<h2 id="s65">6.5 Walk-forward</h2>
<p>O treino termina no índice 6.904 e a validação no índice 8.384, em 9.864 linhas modeláveis. O horizonte é a próxima observação de mercado. Há 296 origens, a cada cinco observações, as mesmas para os quatro, com alvos de 07/06/2007 a 04/04/2014. Cada origem incorpora os fixings já realizados. Os hiperparâmetros permanecem os da validação. A persistência tem MAE 11,6377 USD por onça nas mesmas 296 origens e fica fora do ranking.</p>
<h2 id="s66">6.6 MAE</h2>
<table>
  <caption>Tabela 15 – MAE de teste do ouro</caption>
  <thead><tr><th class="n">Posição</th><th>Modelo</th><th class="n">MAE (USD/onça)</th><th class="n">Previsões</th></tr></thead>
  <tbody>
    <tr><td class="n">1</td><td>Holt-Winters</td><td class="n">11,5331</td><td class="n">296</td></tr>
    <tr><td class="n">2</td><td>SARIMAX</td><td class="n">11,5988</td><td class="n">296</td></tr>
    <tr><td class="n">3</td><td>PLS</td><td class="n">11,6002</td><td class="n">296</td></tr>
    <tr><td class="n">4</td><td>Random Forest</td><td class="n">14,2826</td><td class="n">296</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: analyses/grupo5/outputs/gold_model_comparison_summary.csv (2026).</p>
<p>Na validação, a ordem era PLS 2,9701, Holt-Winters 2,9760, SARIMAX 2,9844 e Random Forest 3,3263. A inversão do teste foi mantida como resultado. Holt-Winters, SARIMAX e PLS ficam a menos de 0,11 USD da persistência. O Random Forest fica 2,64 USD acima dela: a árvore extrapola mal um preço que o treino mal viu. Esta é a segunda vitória do Holt-Winters.</p>
<figure>
  <figcaption>Figura 9 – Ouro no teste: realizado e Holt-Winters</figcaption>
  <img src="../../../analyses/grupo5/outputs/graficos/test_real_vs_pred_holt_winters.png" alt="Real contra previsto, ouro">
</figure>
<p class="fonte">Fonte: analyses/grupo5/outputs/graficos/test_real_vs_pred_holt_winters.png (2026).</p>
<h2 id="s67">6.7 Resíduos e importância</h2>
<p>Série residual e ACF estão em analyses/grupo5/outputs. Nos lags 1 a 20, o menor p é 0,102 no Holt-Winters e 0,106 no PLS: esses dois não rejeitam a 5%. O SARIMAX tem menor p 0,040 e rejeita em 1 lag. O Random Forest tem menor p 0,015 e rejeita em 3 lags. As médias do resíduo são +0,113, +0,234, +0,362 e +3,162 USD para Holt-Winters, PLS, SARIMAX e Random Forest. O desvio fica perto de 15,8 USD nos três primeiros e sobe para 20,6 no Random Forest. O erro absoluto máximo chega a 117 USD.</p>
<p>A impureza do Random Forest é 0,901 no preço da origem, e 0,093 em GOLD_LAG_1. O VIP do PLS é 1,50 no preço corrente. A permutação no teste aumenta o MAE em 348 USD, em média, quando esse preço é embaralhado. Treasury e fundos ficam no fim da permutação, com efeito médio perto de zero, embora o coeficiente do SARIMAX na primeira origem seja significativo. Para um passo, o preço corrente já carrega quase tudo.</p>
"""


def trafego():
    return r"""
<h1 class="sec" id="s7">7 Tráfego da I-94</h1>
<p>Volume horário na I-94 oeste, entre Minneapolis e Saint Paul. O Random Forest vence. O PLS fica em segundo, no conjunto sem clima. A STL mostra um dia muito marcado e um nível estável. O material está em analyses/grupo2.</p>
<h2 id="s71">7.1 Identificação da série</h2>
<p><strong>Fonte.</strong> UCI Machine Learning Repository, Metro Interstate Traffic Volume, com dados do Minnesota Department of Transportation e do Weather Underground. Arquivo bases/grupo2/Metro_Interstate_Traffic_Volume.csv.</p>
<p><strong>Período.</strong> O bruto vai de 02/10/2012 09:00 a 30/09/2018 23:00. O segmento modelado, depois da lacuna longa, vai de 11/06/2015 20:00 a 30/09/2018 23:00. Os alvos de teste vão de 04/02/2018 08:00 a 30/09/2018 16:00.</p>
<p><strong>Frequência.</strong> Horária no segmento modelado. Dentro dele, 2.295 horas foram imputadas de forma causal.</p>
<p><strong>Alvo e unidade.</strong> traffic_volume da hora seguinte, em veículos por hora. O MAE usa só a hora originalmente observada, marcada por target_observed.</p>
<p><strong>Externas.</strong> Feriado, fim de semana e clima defasado: temperatura em kelvin, chuva em milímetro, neve em milímetro e nuvens em porcentagem. O PLS vencedor descartou o clima na validação. O SARIMAX ficou com temperatura, chuva e nuvens, sem a neve. As duas descrições textuais do tempo ficam fora do modelo.</p>
<p>O bruto tem nove colunas: data, volume, feriado, temperatura, chuva, neve, nuvens e duas descrições. O dicionário de modelagem tem 36 atributos. O conjunto do PLS vencedor tem 32, sem temp_lag_1, rain_lag_1, snow_lag_1 e clouds_lag_1.</p>
<table>
  <caption>Tabela 16 – Dicionário das 36 colunas do tráfego</caption>
  <thead><tr><th>Família</th><th>Colunas</th></tr></thead>
  <tbody>
    <tr><td>Calendário cíclico</td><td>hour_sin, hour_cos, dow_sin, dow_cos, month_sin, month_cos</td></tr>
    <tr><td>Indicadores</td><td>is_weekend, is_holiday</td></tr>
    <tr><td>Lags do volume</td><td>1, 2, 3, 6, 12, 23, 24, 25, 48, 72, 167, 168, 169 e 336 horas</td></tr>
    <tr><td>Janelas</td><td>média e desvio de 6, 24 e 168 horas</td></tr>
    <tr><td>Clima defasado</td><td>temp_lag_1, rain_lag_1, snow_lag_1, clouds_lag_1</td></tr>
    <tr><td>Marca de observação real</td><td>observed_lag_1, 24, 168 e 336</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: analyses/grupo2/config.py (2026).</p>
<p>As nove exógenas do SARIMAX são hour_sin, hour_cos, dow_sin, dow_cos, is_holiday, is_weekend, temp_lag_1, rain_lag_1 e clouds_lag_1.</p>
<p><strong>Ausências.</strong> A coluna de feriado vem vazia na maior parte das horas: a hora não é feriado. Dentro do segmento, 2.295 horas de volume foram imputadas e saem do MAE.</p>
<p><strong>Duplicidades.</strong> 48.204 linhas brutas correspondem a 40.575 timestamps únicos: 7.629 horas repetidas, em geral por mais de uma descrição de clima no mesmo instante. A decisão foi uma linha por hora.</p>
<p><strong>Irregularidades.</strong> A maior lacuna tem 7.387 horas, cerca de dez meses. Ela ficou sem interpolação. O segmento modelado começa depois dela e tem 28.972 horas na grade.</p>
<p><strong>Atípicos.</strong> O maior erro compartilhado é 04/07/2018 05:00, feriado, com volume real 698 e previsões tabulares acima de 2.300. A leitura foi de calendário raro. A observação permaneceu.</p>
<p><strong>Limpeza.</strong> Deduplicação da hora. Imputação interna com lag 168, depois lag 24, depois o último valor já visto. O feriado, informado só à meia-noite, foi estendido ao dia inteiro. O clima que entra no modelo está defasado uma hora. A semente é 67. Temperatura, chuva, neve e nuvens de t+1 estão proibidas. Previsão meteorológica oficial não estava no arquivo.</p>
<figure>
  <figcaption>Figura 10 – Volume horário modelado na I-94</figcaption>
  <img src="../../../analyses/grupo2/outputs/figures/01_serie_alvo.png" alt="Série do tráfego">
</figure>
<p class="fonte">Fonte: analyses/grupo2/outputs/figures/01_serie_alvo.png (2026).</p>
<figure>
  <figcaption>Figura 11 – Clima defasado acompanhando o tráfego</figcaption>
  <img src="../../../analyses/grupo2/outputs/figures/02_externas.png" alt="Externas do tráfego">
</figure>
<p class="fonte">Fonte: analyses/grupo2/outputs/figures/02_externas.png (2026).</p>
<h2 id="s72">7.2 Decomposição STL</h2>
<p>A STL do desenvolvimento usa a amostra de 04/02/2017 08:00 a 04/02/2018 07:00, período de 24 horas. A média da tendência passa de cerca de 3.462,95 veículos por hora no início para 3.450,83 no fim. O nível é estável. A força de tendência não foi impressa como número. A diferença de cerca de 12 veículos por hora entre as pontas descreve estabilidade. A subida e a queda de cada dia ficam na sazonalidade, cuja força é 0,8061. O resíduo concentra incidente, clima extremo e feriado. A força diária alta confirma o calendário circular e a diferença sazonal de 24 horas no SARIMAX. O Holt-Winters escolhido mede a semana, período 168, sem tendência.</p>
<figure>
  <figcaption>Figura 12 – STL do tráfego, período de 24 horas</figcaption>
  <img src="../../../analyses/grupo2/outputs/figures/04_stl.png" alt="STL do tráfego">
</figure>
<p class="fonte">Fonte: analyses/grupo2/outputs/figures/04_stl.png (2026).</p>
<h2 id="s73">7.3 Feature engineering</h2>
<p>Os lags do volume vão de 1 a 336 horas, com a vizinhança 23, 25, 167 e 169. Médias e desvios cobrem 6, 24 e 168 horas, depois do deslocamento. Hora, dia da semana e mês entram em seno e cosseno, com fim de semana e feriado do dia inteiro. Indicadores marcam se o lag era observação real. Depois de 336 horas de aquecimento restam 28.636 linhas. Random Forest parte das 36 colunas. O PLS partiu do mesmo dicionário e a validação escolheu as 32 sem clima. A partição 80/20 é cronológica.</p>
<h2 id="s74">7.4 Modelos e hiperparâmetros</h2>
<p>Holt-Winters tem 18 candidatos, o PLS tem 93, o Random Forest tem 12 e o SARIMAX tem cinco estruturas que sobreviveram à triagem de BIC. O BIC só reduziu a grade do SARIMAX. A escolha final é o MAE de validação. Dentro dos 80% iniciais, o treino vai até o índice 20.044 e a validação até 22.908. As 521 origens de teste ficaram fora da busca.</p>
<p><strong>SARIMAX.</strong> Ordem (2, 0, 1) × (0, 1, 1, 24), janela de 1.440 horas, exógenas padronizadas dentro de cada janela. Validação 292,478. Convergência no teste 0,8349. A tabela de p-valor das nove exógenas não foi exportada.</p>
<p><strong>Holt-Winters.</strong> Sazonalidade aditiva, período 168, tendência nula, amortecimento desligado, janela máxima de 1.440 horas. Validação 349,463. Há nível e perfil semanal. Se o ajuste não converge ou a previsão sai do intervalo causal aceito, a origem usa o volume de 168 horas antes. Isso ocorreu em 167 das 521 origens de teste.</p>
<p><strong>Random Forest.</strong> 900 árvores, profundidade livre, max_features igual à raiz quadrada, folha mínima 1, mínimo 2 para dividir. Validação 197,321.</p>
<p><strong>PLS.</strong> Grade de 1 a 32 componentes nos conjuntos completo, sem clima e compacto. Venceu o conjunto sem clima, com 15 componentes, validação 233,263. O conjunto com clima ficou em 233,42 com 30 componentes.</p>
<h2 id="s75">7.5 Walk-forward</h2>
<p>Há 258 origens de validação e 521 de teste, de 11 em 11 horas. O passo 11 é coprimo de 24 e visita todas as horas do dia. A primeira origem de teste é 04/02/2018 07:00 e a última é 30/09/2018 15:00. O horizonte é uma hora. O MAE conta só o alvo originalmente observado. Os hiperparâmetros da validação ficam fixos. Validação e teste concordam no Random Forest. Fora do ranking, o sazonal de 168 horas tem MAE 283,31, o sazonal de 24 horas tem 554,75 e a persistência de 1 hora tem 595,39.</p>
<h2 id="s76">7.6 MAE</h2>
<table>
  <caption>Tabela 17 – MAE de teste do tráfego</caption>
  <thead><tr><th class="n">Posição</th><th>Modelo</th><th class="n">MAE</th><th>Intervalo de 95%</th><th class="n">n</th></tr></thead>
  <tbody>
    <tr><td class="n">1</td><td>Random Forest</td><td class="n">157,76</td><td>139,6 a 176,8</td><td class="n">521</td></tr>
    <tr><td class="n">2</td><td>PLS</td><td class="n">191,70</td><td>173,2 a 213,4</td><td class="n">521</td></tr>
    <tr><td class="n">3</td><td>Holt-Winters</td><td class="n">209,83</td><td>180,5 a 243,6</td><td class="n">521</td></tr>
    <tr><td class="n">4</td><td>SARIMAX</td><td class="n">263,68</td><td>—</td><td class="n">521</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: analyses/grupo2/outputs/results/mae_consolidado.csv e mae_uncertainty.csv (2026).</p>
<p>O Random Forest reduz o piso de 168 horas em 44,3%. O PLS reduz esse piso em 32,3%. O Holt-Winters fica em terceiro, com o fallback semanal em cerca de um terço das origens. O SARIMAX fica em quarto, com convergência de 83,5% no teste. Esta é a segunda vitória do Random Forest.</p>
<figure>
  <figcaption>Figura 13 – Tráfego no teste: realizado e Random Forest</figcaption>
  <img src="../../../analyses/grupo2/outputs/figures/previsao_Random_Forest.png" alt="Previsão do tráfego">
</figure>
<p class="fonte">Fonte: analyses/grupo2/outputs/figures/previsao_Random_Forest.png (2026). Os quatro pares estão em previsao_*.png.</p>
<h2 id="s77">7.7 Resíduos e importância</h2>
<p>O Ljung-Box interpretativo usa 168 previsões horárias consecutivas. As 521 origens do MAE são a sequência de 11 em 11 horas. Nessa sequência horária, o Random Forest tem ACF 0,505 no lag 1, p do lag 1 praticamente 0 e p do lag 24 igual a 1,45×10⁻¹¹. O PLS tem ACF −0,008, p do lag 1 igual a 0,916 e p do lag 24 igual a 0,061. O Holt-Winters tem ACF 0,768 e p praticamente 0. O SARIMAX tem ACF 0,048, p do lag 1 igual a 0,528 e p do lag 24 igual a 0,026. O PLS é o único dos quatro que não rejeita o lag 24 a 5% nessa sequência.</p>
<p>Nas 521 origens, observado menos previsto: Random Forest +13,81, PLS +2,41, Holt-Winters −4,26 e SARIMAX −11,80 veículos por hora. Na amostra de 168 horas, os vieses são +42,52, −23,98, −44,24 e +50,80, na mesma ordem. O PLS é o mais centrado nas 521 origens. O Random Forest erra menos em módulo e deixa um termo autorregressivo no erro. O feriado de 04/07/2018 permanece como o maior erro compartilhado. O tempo de teste foi de cerca de 1.804 segundos no Random Forest, 8,9 no PLS, 25,4 no Holt-Winters e 27.940 no SARIMAX.</p>
<figure>
  <figcaption>Figura 14 – Resíduos do Random Forest no tráfego</figcaption>
  <img src="../../../analyses/grupo2/outputs/figures/residuos_Random_Forest.png" alt="Resíduos do tráfego">
</figure>
<p class="fonte">Fonte: analyses/grupo2/outputs/figures/residuos_Random_Forest.png (2026).</p>
<p>A impureza do Random Forest é 0,1568 em y_lag_1, 0,1553 em y_lag_168 e 0,1521 em y_lag_336. Clima e feriado ficam abaixo de 0,002. A permutação do PLS na validação aumenta o MAE, em média, em 1.425,60 veículos por hora em y_lag_1, 565,47 em y_lag_169, 461,67 em y_lag_168, 339,33 em y_lag_336 e 262,96 em y_lag_24. O VIP passa de 1,7 em y_lag_336 e y_lag_168. O coeficiente padronizado de is_holiday é −58,040, com VIP 0,357 e permutação cerca de 7. O clima não sobreviveu à validação do PLS. A tabela de p-valor das exógenas do SARIMAX não foi exportada.</p>
"""


def fecho():
    return r"""
<h1 class="sec" id="s8">8 Leitura conjunta</h1>
<h2 id="s81">8.1 MAE das vinte combinações</h2>
<p>A Tabela 18 reúne as vinte combinações. A posição é interna à base. A média de MAE entre bases não entra neste relatório.</p>
<table>
  <caption>Tabela 18 – MAE de teste das vinte combinações</caption>
  <thead><tr><th>Base</th><th>Modelo</th><th class="n">MAE</th><th class="n">n</th><th class="n">Posição</th></tr></thead>
  <tbody>
    <tr><td>Bitcoin (USD)</td><td>Holt-Winters</td><td class="n">1.406,54</td><td class="n">856</td><td class="n">1</td></tr>
    <tr><td>Bitcoin (USD)</td><td>SARIMAX</td><td class="n">1.590,77</td><td class="n">856</td><td class="n">2</td></tr>
    <tr><td>Bitcoin (USD)</td><td>Random Forest</td><td class="n">2.108,00</td><td class="n">856</td><td class="n">3</td></tr>
    <tr><td>Bitcoin (USD)</td><td>PLS</td><td class="n">2.608,61</td><td class="n">856</td><td class="n">4</td></tr>
    <tr><td>PM2.5 (µg/m³)</td><td>Random Forest</td><td class="n">9,5131</td><td class="n">6.023</td><td class="n">1</td></tr>
    <tr><td>PM2.5 (µg/m³)</td><td>PLS</td><td class="n">9,6643</td><td class="n">6.023</td><td class="n">2</td></tr>
    <tr><td>PM2.5 (µg/m³)</td><td>SARIMAX</td><td class="n">10,2225</td><td class="n">6.023</td><td class="n">3</td></tr>
    <tr><td>PM2.5 (µg/m³)</td><td>Holt-Winters</td><td class="n">12,9122</td><td class="n">6.023</td><td class="n">4</td></tr>
    <tr><td>Jena (°C)</td><td>PLS</td><td class="n">0,3983</td><td class="n">14.026</td><td class="n">1</td></tr>
    <tr><td>Jena (°C)</td><td>SARIMAX</td><td class="n">0,4064</td><td class="n">14.026</td><td class="n">2</td></tr>
    <tr><td>Jena (°C)</td><td>Random Forest</td><td class="n">0,4114</td><td class="n">14.026</td><td class="n">3</td></tr>
    <tr><td>Jena (°C)</td><td>Holt-Winters</td><td class="n">0,4259</td><td class="n">14.026</td><td class="n">4</td></tr>
    <tr><td>Ouro (USD/onça)</td><td>Holt-Winters</td><td class="n">11,5331</td><td class="n">296</td><td class="n">1</td></tr>
    <tr><td>Ouro (USD/onça)</td><td>SARIMAX</td><td class="n">11,5988</td><td class="n">296</td><td class="n">2</td></tr>
    <tr><td>Ouro (USD/onça)</td><td>PLS</td><td class="n">11,6002</td><td class="n">296</td><td class="n">3</td></tr>
    <tr><td>Ouro (USD/onça)</td><td>Random Forest</td><td class="n">14,2826</td><td class="n">296</td><td class="n">4</td></tr>
    <tr><td>Tráfego (veíc./h)</td><td>Random Forest</td><td class="n">157,76</td><td class="n">521</td><td class="n">1</td></tr>
    <tr><td>Tráfego (veíc./h)</td><td>PLS</td><td class="n">191,70</td><td class="n">521</td><td class="n">2</td></tr>
    <tr><td>Tráfego (veíc./h)</td><td>Holt-Winters</td><td class="n">209,83</td><td class="n">521</td><td class="n">3</td></tr>
    <tr><td>Tráfego (veíc./h)</td><td>SARIMAX</td><td class="n">263,68</td><td class="n">521</td><td class="n">4</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: docs/relatorios/consolidado/mae_consolidado.csv (2026).</p>
<p>Holt-Winters é o melhor previsor de um passo nas duas séries de nível com sazonalidade medida nula. Random Forest é o melhor no PM2.5 e no tráfego. O PLS é o melhor em Jena e o segundo no PM2.5 e no tráfego. O SARIMAX fica em segundo nas séries de preço e de temperatura e em quarto no tráfego.</p>
<p>As decisões de limpeza que mais mudaram o desenho foram manter a lacuna de dez meses do tráfego sem interpolação, preservar as 925 horas sem alvo no PM2.5, agregar Jena para a hora, manter extremo e lacuna de calendário no ouro, e comparar o Bitcoin só nos 856 dias comuns. No PM2.5, o MAE de validação prevaleceu sobre o AIC. No ouro, o hiperparâmetro continua o da validação, e o ranking publicado é o do teste.</p>
<h2 id="s82">8.2 Ljung-Box consolidado</h2>
<p>O resíduo é observado menos previsto. O lag da tabela é o que cada base usou para o ciclo principal. No tráfego, o p-valor é o da sequência de 168 horas consecutivas.</p>
<table>
  <caption>Tabela 19 – Ljung-Box dos vinte resultados</caption>
  <thead><tr><th>Base</th><th>Modelo</th><th>Lag</th><th class="n">p-valor</th><th>Leitura a 5%</th></tr></thead>
  <tbody>
    <tr><td>Bitcoin</td><td>Holt-Winters</td><td>1 (e 3, 5, 7, 14, 21, 30)</td><td class="n">0,455</td><td>não rejeita</td></tr>
    <tr><td>Bitcoin</td><td>SARIMAX</td><td>1</td><td class="n">0,0025</td><td>rejeita</td></tr>
    <tr><td>Bitcoin</td><td>Random Forest</td><td>1</td><td class="n">menor que 0,0025</td><td>rejeita</td></tr>
    <tr><td>Bitcoin</td><td>PLS</td><td>1</td><td class="n">menor que 0,0025</td><td>rejeita</td></tr>
    <tr><td>PM2.5</td><td>Holt-Winters</td><td>24</td><td class="n">0</td><td>rejeita</td></tr>
    <tr><td>PM2.5</td><td>SARIMAX</td><td>24</td><td class="n">1,5×10⁻²¹</td><td>rejeita</td></tr>
    <tr><td>PM2.5</td><td>Random Forest</td><td>24</td><td class="n">1,7×10⁻⁵⁰</td><td>rejeita</td></tr>
    <tr><td>PM2.5</td><td>PLS</td><td>24</td><td class="n">4,1×10⁻¹⁵</td><td>rejeita</td></tr>
    <tr><td>Jena</td><td>Os quatro</td><td>24</td><td class="n">0 impresso</td><td>rejeita</td></tr>
    <tr><td>Ouro</td><td>Holt-Winters</td><td>menor p, lags 1–20</td><td class="n">0,102</td><td>não rejeita</td></tr>
    <tr><td>Ouro</td><td>PLS</td><td>menor p, lags 1–20</td><td class="n">0,106</td><td>não rejeita</td></tr>
    <tr><td>Ouro</td><td>SARIMAX</td><td>menor p, lags 1–20</td><td class="n">0,040</td><td>rejeita 1 lag</td></tr>
    <tr><td>Ouro</td><td>Random Forest</td><td>menor p, lags 1–20</td><td class="n">0,015</td><td>rejeita 3 lags</td></tr>
    <tr><td>Tráfego</td><td>Random Forest</td><td>24, em 168 h</td><td class="n">1,5×10⁻¹¹</td><td>rejeita</td></tr>
    <tr><td>Tráfego</td><td>PLS</td><td>24, em 168 h</td><td class="n">0,061</td><td>não rejeita o lag 24</td></tr>
    <tr><td>Tráfego</td><td>Holt-Winters</td><td>24, em 168 h</td><td class="n">≈ 0</td><td>rejeita</td></tr>
    <tr><td>Tráfego</td><td>SARIMAX</td><td>24, em 168 h</td><td class="n">0,026</td><td>rejeita o lag 24</td></tr>
  </tbody>
</table>
<p class="fonte">Fonte: elaborada pelo grupo (2026), a partir dos CSV de diagnóstico. O p exato do lag 1 de Random Forest e PLS no Bitcoin está no CSV da base e é inferior ao do SARIMAX.</p>
<p>Três itens permanecem como lacuna de arquivo: a tabela de p-valor das exógenas do SARIMAX no Bitcoin, no PM2.5 e no tráfego; a força sazonal anual do Bitcoin; e a força de tendência do tráfego como número. Os gráficos de Bitcoin e de Jena estão nos notebooks executados.</p>
<h1 class="sec" id="sref">Referências</h1>
<ol class="ref">
  <li>BOX, G. E. P.; JENKINS, G. M.; REINSEL, G. C.; LJUNG, G. M. <strong>Time series analysis</strong>: forecasting and control. Hoboken: Wiley, 2015.</li>
  <li>BREIMAN, L. Random forests. <strong>Machine Learning</strong>, v. 45, n. 1, p. 5-32, 2001.</li>
  <li>CLEVELAND, R. B.; CLEVELAND, W. S.; MCRAE, J. E.; TERPENNING, I. STL: a seasonal-trend decomposition procedure based on loess. <strong>Journal of Official Statistics</strong>, v. 6, n. 1, p. 3-73, 1990.</li>
  <li>COINMARKETCAP. Série diária BTC/USD. Arquivo bases/grupo1/bitcoin.xlsx.</li>
  <li>DEUTSCHE BUNDESBANK. Série BBEX3.D.XAU.USD.EA.AC.C05. Arquivo indicado em analyses/grupo5/outputs/protocol.json.</li>
  <li>HYNDMAN, R. J.; ATHANASOPOULOS, G. <strong>Forecasting</strong>: principles and practice. 3. ed. Melbourne: OTexts, 2021.</li>
  <li>LJUNG, G. M.; BOX, G. E. P. On a measure of lack of fit in time series models. <strong>Biometrika</strong>, v. 65, n. 2, p. 297-303, 1978.</li>
  <li>MAX-PLANCK-INSTITUT FÜR BIOGEOCHEMIE. Jena climate dataset. Agregado de 10 minutos para hora no notebook do grupo.</li>
  <li>UCI MACHINE LEARNING REPOSITORY. Beijing multi-site air-quality data. Estação Aotizhongxin.</li>
  <li>UCI MACHINE LEARNING REPOSITORY. Metro interstate traffic volume. Minnesota Department of Transportation; Weather Underground.</li>
  <li>WOLD, S.; SJÖSTRÖM, M.; ERIKSSON, L. PLS-regression: a basic tool of chemometrics. <strong>Chemometrics and Intelligent Laboratory Systems</strong>, v. 58, n. 2, p. 109-130, 2001.</li>
</ol>
"""


def main():
    # Corrige a célula errada de Jena na Tabela 1 antes de gravar.
    text = html()
    errado = (
        "<tr><td>Holt-Winters</td><td class=\"n\">1</td><td class=\"n\">4</td>"
        "<td class=\"n\">1</td><td class=\"n\">1</td><td class=\"n\">3</td>"
    )
    certo = (
        "<tr><td>Holt-Winters</td><td class=\"n\">1</td><td class=\"n\">4</td>"
        "<td class=\"n\">4</td><td class=\"n\">1</td><td class=\"n\">3</td>"
    )
    if errado not in text:
        raise SystemExit("linha da Tabela 1 não encontrada")
    text = text.replace(errado, certo, 1)
    nota = (
        "<p>A célula de Jena do Holt-Winters na Tabela 1 precisa ser lida com a Tabela 2: "
        "Holt-Winters é o 4º em Jena, o 1º no Bitcoin e o 1º no ouro. "
        "A linha da Tabela 1 acima será conferida na geração: Holt-Winters em Jena é posição 4.</p>"
    )
    text = text.replace(nota, "")
    OUT.write_text(text, encoding="utf-8")
    print(OUT, "chars", len(text))


if __name__ == "__main__":
    main()
