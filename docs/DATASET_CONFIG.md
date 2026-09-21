# Configuração da base de previsão do ouro

## Objetivo e granularidade

A base oficial é `bases/grupo5/gold_daily_modeling.csv`. Ela prevê o preço do ouro uma observação à frente: `TARGET = GOLD_PRICE.shift(-1)`. A granularidade é diária, respeitando exclusivamente as datas existentes na série original do ouro; finais de semana e datas inexistentes não são criados.

`GOLD_PRICE` é a variável observada no instante `t`; `TARGET` é somente a variável resposta em `t+1`. O horizonte oficial é uma observação à frente.

## Fontes brutas e rastreabilidade

Os arquivos em `bases/grupo5-tratamento/` são cópias versionadas e imutáveis para a execução desta etapa, juntamente com o script reprodutível:

| Arquivo | Conteúdo | Fonte e identificador |
| --- | --- | --- |
| `gold_daily_prices.csv` | série principal, com `VALUE` convertido para `GOLD_PRICE` apenas no processamento | série fornecida ao Grupo 5 |
| `dgs10.csv` | Treasury americano de 10 anos | FRED, série [DGS10](https://fred.stlouisfed.org/series/DGS10) |
| `dff.csv` | Federal Funds Effective Rate | FRED, série [DFF](https://fred.stlouisfed.org/series/DFF) |

Os arquivos FRED foram baixados pelo grupo em 2026-09-14 e então copiados sem transformação para `bases/grupo5-tratamento/`. O script não baixa, altera ou substitui arquivos brutos.

## Integração temporal e disponibilidade

O ouro é a referência temporal. O script faz `left` merge por `DATE`, portanto uma data exclusiva do FRED nunca cria uma linha na base final. Marcadores inválidos como `.`, strings vazias, `NA` e equivalentes são convertidos para `NaN` na memória.

Depois do merge, lacunas de calendário das externas recebem apenas `ffill()`. Não há `bfill`, interpolação ou uso de observação futura. Como os CSVs observados do FRED não trazem horário intradiário de publicação, `TREASURY_10Y` e `FED_FUNDS_RATE` recebem ainda uma defasagem de uma observação do ouro. Essa decisão conservadora garante que cada valor externo em `t` seja conhecido antes da origem de previsão em `t`; o contrato versionado em `config/datasets.json` classifica ambas como `lag_only`.

`TARGET_UP` não entra no processamento porque depende de `GOLD_PRICE` em `t+1`. `IS_HOLIDAY` também não entra na base oficial: a coluna recebida não possui regra de geração ou fonte reproduzível documentada.

## Features

O script cria `DAY_OF_WEEK`, `MONTH`, `DOW_SIN`, `DOW_COS`, `MONTH_SIN`, `MONTH_COS`, `GOLD_LAG_1`, `GOLD_LAG_5`, `GOLD_LAG_20`, `GOLD_ROLLING_MEAN_5`, `GOLD_ROLLING_STD_5` e `TARGET`.

As janelas móveis usam `GOLD_PRICE.shift(1).rolling(5)`: nunca incorporam o valor atual. As linhas descartadas são somente as que têm `NaN` causado por defasagem externa inicial, lags, janelas móveis ou o último `TARGET`; o relatório do script mostra a contagem por coluna antes da limpeza, o total removido e o total final.

## Protocolo de modelagem

- `random_state = 42` para algoritmos futuros que possuírem aleatoriedade.
- Divisão exclusivamente cronológica: primeiros 80% para treino, últimos 20% para teste final, sem `shuffle=True`.
- O teste final não será usado para selecionar hiperparâmetros; tuning ocorrerá somente no treino.
- A avaliação final será walk-forward. Todos os modelos usarão o mesmo teste, as mesmas origens, horizonte de uma observação e hiperparâmetros fixos durante o teste.
- A métrica oficial da comparação é MAE (Mean Absolute Error).

## Reprodução e verificações

Execute `python bases/grupo5-tratamento/prepare_gold_dataset.py`. O comando recria o CSV consolidado em `bases/grupo5/` e imprime períodos, registros, ausências antes e depois do tratamento, linhas removidas, colunas e as cinco primeiras e últimas linhas.

O pipeline falha se datas estiverem duplicadas, se o calendário do ouro não for preservado, se a saída tiver `NaN` inesperado ou se lags, janelas e target não respeitarem seus deslocamentos. Não há data leakage conhecido: toda feature autoregressiva usa `t` ou antes, as janelas acabam em `t-1` e as externas são observações defasadas.
