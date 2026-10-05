# Exploração final da Base 2 — tráfego

## Cobertura e significado

O CSV bruto tem 48.204 linhas entre 2 de outubro de 2012 e 30 de setembro de 2018. Há 40.575 horários únicos e 7.629 duplicatas de timestamp (várias descrições meteorológicas na mesma hora). Depois de cortar a lacuna de 7.387 horas e regularizar a grade, o segmento modelado vai de 11 de junho de 2015 20:00 a 30 de setembro de 2018 23:00 (28.972 horas), com 26.677 alvos originalmente observados.

O alvo `traffic_volume` é a contagem horária de veículos na I-94 oeste. Média no segmento ≈ 3.300; máximo 7.280.

## Frequência e qualidade temporal

A frequência desejada é horária. O arquivo bruto **não** é uma grade perfeita: duplicatas, buracos curtos e uma interrupção de cerca de 10 meses. A duplicata foi reduzida a uma linha por hora. A interrupção longa **não** foi interpolada. Buracos curtos no segmento posterior receberam imputação causal do alvo, marcada por `target_observed=0`.

## Valores ausentes

Não há nulos numéricos de temperatura/chuva no bruto. `holiday` vazio significa “não é feriado”. As 2.295 horas imputadas no segmento entram no treino como contexto, mas **saem do MAE**.

## Valores atípicos

Volumes próximos de zero de madrugada e picos de fim de tarde são o regime normal da via, não erro. O 4 de julho de 2018 (678 veículos às 05h frente a ~2.500 previstos) é feriado, não outlier a remover. Nenhum ponto foi winsorizado.

Gráficos: `01_serie_alvo.png`, `02_externas.png`, `03_perfil_horario.png`.
