# Baseline de persistência

O baseline prevê o próximo preço usando o último `GOLD_PRICE` disponível na origem.

- Nas mesmas 296 origens espaçadas usadas pelos quatro modelos, o MAE foi **11,6376689189**.
- Nas 1.480 linhas consecutivas do período de teste, o MAE foi **11,4379391892**.

Os valores diferem porque as amostras de erros são diferentes. O protocolo oficial avalia uma origem a cada cinco observações; já o diagnóstico consecutivo usa todas as linhas modeláveis do período de teste. A média dos erros absolutos pode mudar quando se seleciona outro subconjunto de datas, mesmo com a mesma regra de persistência.

Somente o baseline das 296 origens é comparável aos modelos, pois compartilha datas de origem, datas-alvo, horizonte e observações reais. O baseline não é um quinto modelo oficial e não entra no ranking. Sua função é indicar quanto valor preditivo os modelos acrescentam sobre uma regra simples e forte para séries de preço persistentes.

Os erros por origem estão em `baseline_persistencia.csv`; o diagnóstico consecutivo está em `baseline_persistencia_todas_observacoes_teste.csv`.
