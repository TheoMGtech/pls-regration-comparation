# Diagnóstico da execução anterior

## Resultados encontrados no zip executado

- Random Forest: MAE 198,80; 815,96 segundos.
- PLS Regression: MAE 349,59; 15,66 segundos.
- SARIMAX: MAE 577,88; 1.296,19 segundos.
- Holt-Winters: MAE 725,27; 0,87 segundo.
- 10.477 previsões por modelo.
- Ljung-Box com p-valor reportado como zero nos quatro modelos.

O Random Forest não estava “muito ruim”: seu MAE foi menor que os baselines de
lag 1 (589,97), lag 24 (563,63) e lag 168 (328,57). Ainda assim, o protocolo
anterior não permitia uma comparação final uniforme entre os quatro modelos.

## Por que executava mais rápido

Na versão anterior, `REFIT_EVERY=336`. Holt-Winters e SARIMAX eram ajustados
uma vez e produziam blocos de até 336 horas. Isso não é o mesmo protocolo do
Theo, que reajusta em cada origem e prevê somente o próximo instante. A versão
anterior também usava janelas menores e tuning por holdout simples.

No protocolo corrigido, cada candidato é avaliado em várias origens de
validação e cada modelo final é reajustado nas mesmas aproximadamente 520
origens de teste.
Portanto, principalmente Random Forest, Holt-Winters e SARIMAX podem levar
horas. Esse aumento de tempo é esperado.

## Problema na série

A base possui 40.575 timestamps únicos dentro de um intervalo de 52.551 horas,
com uma lacuna máxima de 7.387 horas. A limpeza anterior reindexava todo o
intervalo e interpolava/preenchia 11.976 alvos ausentes, inclusive essa lacuna
de quase dez meses.

A correção:

1. mantém o segmento posterior à maior lacuna;
2. reindexa esse segmento na frequência horária;
3. preenche faltas apenas com valores passados (lag 168, lag 24 e `ffill`);
4. marca `target_observed`;
5. avalia o MAE somente em alvos originalmente observados.

## Melhorias implementadas

- lags horários, diários e semanais, incluindo vizinhanças de 24 e 168 horas;
- médias e desvios móveis de 6, 24 e 168 horas;
- clima defasado em uma hora, evitando usar informação não disponível;
- feriados expandidos para todas as horas do dia (na fonte, o nome aparece
  apenas à meia-noite);
- tuning walk-forward;
- triagem de 72 estruturas SARIMAX por BIC e validação das melhores;
- mesmos timestamps, mesmo horizonte e mesmo alvo real nos quatro modelos;
- baselines e artefatos de auditoria;
- checkpoints de tuning para retomar uma execução interrompida.

Os MAEs do tráfego não devem ser comparados diretamente aos MAEs do ouro do
Grupo 5: as escalas, unidades e séries são diferentes. A comparação correta é
entre modelos e baselines dentro da mesma base.
