# Síntese técnica do PLS Regression — Base 2 (tráfego)

## 1. Intuição

Partial Least Squares transforma as features originais em componentes latentes. Cada componente é uma combinação linear das variáveis, construída para explicar simultaneamente a estrutura de `X` e a covariância com o alvo `traffic_volume`. A regressão é então ajustada nesse espaço latente, não no espaço original colinear.

## 2. Componentes e covariância com o alvo

Diferentemente de PCA, o PLS usa o alvo ao definir as direções. Lags de 1h, 24h e 168h variam juntos e também predizem o volume da próxima hora; o PLS condensa essa redundância em poucos eixos supervisionados. Isso é o motivo de o método ser o especialista desta base: a matriz tabular tem muitos lags altamente correlacionados.

## 3. Diferença para regressão linear comum

A regressão linear estima um coeficiente por coluna e fica instável sob multicolinearidade. O PLS projeta primeiro e só depois regressa. O hiperparâmetro `n_components` controla quanta informação latente entra e funciona como regularização.

## 4. Preparação e padronização

Random Forest e PLS partem do mesmo dicionário causal (calendário, lags, janelas, flags de observação e, no conjunto `full`, clima com lag 1). Em **cada origem** walk-forward o `StandardScaler` é reajustado só na janela de treino e aplicado à linha da origem. Média e desvio do teste nunca entram no treino. O alvo futuro nunca é feature.

## 5. Seleção de 15 componentes no conjunto `no_weather`

Foram avaliados 1 a 32 componentes em três conjuntos (`full`, `no_weather`, `compact`) na validação walk-forward (258 origens). O menor MAE de validação foi **233,26**, com `feature_set=no_weather` e `n_components=15`. Os conjuntos `full` com 30–32 componentes ficaram a menos de 0,2 de MAE; a regra de desempate privilegiou o conjunto menor (sem clima).

Quinze componentes em 32 features de `no_weather` é compressão real, ao contrário do ouro (11 de 12). O teste final **não** reabriu essa escolha.

O fato de `no_weather` vencer significa que, **neste horizonte de 1 hora e com lags fortes do próprio tráfego**, temperatura/chuva/nuvens observadas em `t` adicionaram pouco poder preditivo marginal. Isso não afirma que o clima é irrelevante para o tráfego em geral.

## 6. Interpretação das features

Três leituras, todas na validação (não no teste):

- **coeficientes padronizados** — magnitude na escala transformada;
- **VIP** — contribuição da feature aos componentes que explicam o alvo (regra prática: VIP > 1);
- **permutation importance** — quanto o MAE sobe ao embaralhar a coluna, modelo fixo.

Pela permutation, a ordem principal foi `y_lag_1`, `y_lag_169`, `y_lag_168`, `y_lag_336`, `y_lag_24`. Ou seja: persistência imediata e o ciclo semanal/duas semanas. `is_holiday` tem coeficiente negativo (volume menor em feriado), mas VIP 0,36: o efeito existe e é interpretável, porém pequeno frente aos lags. Flags `observed_lag_*` e o calendário mensal ficaram no rodapé.

Features correlacionadas (168, 167, 169, 336) **dividem** importância. Nenhum ranking implica causalidade.

## 7. Vantagens e limitações

Vantagens: lidar com multicolinearidade dos lags, forma linear, padronização por janela, extrapolar melhor que uma floresta quando o volume sai da faixa vista no treino.

Limitações: relações sobretudo lineares; interpretação dos componentes menos direta que um coeficiente isolado; sensibilidade à escala (por isso o scaler); feriados e choques (4 de julho) continuam difíceis.

Nesta base o PLS **não** precisou do clima para vencer a validação. Se o horizonte fosse de várias horas, a conclusão poderia mudar.

## 8. Desempenho nesta base

No teste (521 origens, MAE só em alvos observados):

| Modelo | MAE | WAPE | vs. sazonal 168h (283,3) |
|---|---:|---:|---:|
| Random Forest | 157,8 | 4,7% | +44% |
| **PLS Regression** | **191,7** | **5,7%** | **+32%** |
| Holt-Winters | 209,8 | 6,2% | +26% |
| SARIMAX | 263,7 | 7,9% | +7% |

O PLS ficou em segundo, atrás do RF, e à frente da referência univariada. IC 95% do MAE: PLS 173–213; RF 140–177. A diferença para o RF é real, mas não gigantesca. Validação já apontava RF melhor (197 vs 233); o teste confirmou a ordem. O teste não foi usado para trocar os 15 componentes.

Comparar este MAE com o ouro ou com Jena é inválido: as escalas são outras.
