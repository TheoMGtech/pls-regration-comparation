# Análise de importância das features

## PLS Regression

As três leituras disponíveis são coeficientes padronizados, VIP Scores e permutation importance. Pela permutation importance, a ordem principal foi:

1. `GOLD_PRICE`;
2. `GOLD_LAG_1`;
3. `GOLD_ROLLING_MEAN_5`;
4. `GOLD_LAG_5`;
5. `GOLD_LAG_20`.

Essas variáveis dominam porque o problema prevê o preço da próxima observação e a série possui forte persistência temporal. O preço na origem, lags e médias móveis carregam diretamente o nível e a dinâmica recente do ouro.

Um VIP acima de 1 é uma regra prática para identificar variáveis com contribuição acima da média na construção dos componentes. `TREASURY_10Y` teve VIP 0,3435 e `FED_FUNDS_RATE` 0,2754; ambas ficaram abaixo de 1 e contribuíram pouco neste experimento. Treasury ficou acima de Fed Funds no VIP e na permutation importance do PLS.

Essa baixa contribuição não significa que juros não influenciem o ouro em geral. Significa apenas que, com estas definições temporais, duas séries externas, este período, este horizonte de uma observação e as demais features presentes, elas adicionaram pouco poder preditivo marginal.

## Random Forest

Na importância nativa, `GOLD_PRICE` concentrou 0,9013 e `GOLD_LAG_1` 0,0926. A permutation importance também colocou essas duas features no topo. `FED_FUNDS_RATE` apareceu em terceiro pela permutação, mas com magnitude muito menor.

Permutation importance negativa significa que permutar a variável não piorou o erro médio e chegou a melhorá-lo ligeiramente. Isso pode ocorrer por redundância entre features correlacionadas, ruído, instabilidade amostral ou uso substituível de variáveis pelo modelo. Não é evidência de efeito causal negativo.

Nenhuma dessas medidas implica causalidade. Elas descrevem como cada modelo utilizou as features sob o protocolo congelado. Os números completos estão em `feature_importance_summary.csv` e os gráficos em `feature_importance_pls_regression.png` e `feature_importance_random_forest.png`.
