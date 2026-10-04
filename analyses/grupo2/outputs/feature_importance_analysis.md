# Análise de importância das features — Base 2

## PLS Regression

As três leituras são coeficientes padronizados, VIP Scores e permutation importance, calculadas nas origens de **validação**.

Pela permutation, a ordem principal foi:

1. `y_lag_1`;
2. `y_lag_169`;
3. `y_lag_168`;
4. `y_lag_336`;
5. `y_lag_24`.

Essas variáveis dominam porque o problema prevê o volume da próxima hora e a série tem persistência forte mais ciclos diário e semanal. O VIP de `y_lag_336` e `y_lag_168` ficou acima de 1,7.

`is_holiday` tem coeficiente padronizado negativo (−58) e permutation pequena (≈7 de MAE). O sinal é o esperado (menos tráfego em feriado), mas a contribuição marginal é baixa frente aos lags. O conjunto vencedor **não inclui clima**: `temp_lag_1` e chuva não sobreviveram à validação.

Permutation negativa em algumas colunas de calendário/flags indica redundância, não efeito causal negativo.

## Random Forest

A importância nativa concentra-se em `y_lag_1` (0,157), `y_lag_168` (0,155) e `y_lag_336` (0,152). Em seguida vêm `y_lag_167`, `y_lag_169`, `hour_cos` e `y_lag_24`. Clima e feriado ficam abaixo de 0,002.

RF e PLS concordam no essencial: o volume recente e o mesmo horário da semana passada. Discordam no clima porque o PLS já o removeu no conjunto vencedor, e o RF o mantém com peso quase nulo.

Nenhuma medida implica causalidade. Números: `feature_importance_PLS_Regression.csv` e `feature_importance_Random_Forest.csv`.
