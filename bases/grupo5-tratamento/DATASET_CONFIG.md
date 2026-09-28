# Documentação da base - Grupo 5 (ouro)

Este documento cobre a origem da série, a disponibilidade temporal das variáveis e as decisões de preparação já aprovadas. A seleção de hiperparâmetros e o teste final continuam separados e ainda não foram executados.

## Base e variável-alvo

| Item | Registro atual |
| --- | --- |
| Arquivo bruto | `bases/grupo5-tratamento/gold_daily_prices.csv` |
| Fonte | CSV de referência `dengyishuo/quantitative-finance/gold.daily.prices.csv`, correspondente à série Deutsche Bundesbank `BBEX3.D.XAU.USD.EA.AC.C05`. O arquivo local coincide integralmente com as 12.009 datas e valores da referência. |
| Descrição | Preço do ouro no fixing da tarde em Londres. |
| Período bruto | 1968-04-01 a 2014-04-10 (12.009 registros). |
| Frequência observada | Diária em dias úteis: há registros de segunda a sexta-feira. Não houve regularização de calendário nesta etapa. |
| Variável-alvo | `VALUE` no arquivo bruto; renomeada para `GOLD_PRICE` na base modelada. |
| Unidade da variável-alvo | USD por onça fina de ouro (31,1034768 gramas). |
| Nulos observados no arquivo bruto | 368 em `VALUE`; este é um diagnóstico inicial, não uma decisão de tratamento. |
| Duplicidades temporais observadas | Nenhuma data duplicada. |

## Dicionário das variáveis externas candidatas

As variáveis abaixo foram incluídas na base modelada como candidatas exógenas. A seleção final de quais modelos as utilizarão ainda não foi feita.

| Coluna na base modelada | Coluna no arquivo bruto | Descrição | Fonte | Disponibilidade temporal e decisão de inclusão |
| --- | --- | --- | --- | --- |
| `TREASURY_10Y` | `DGS10` | Taxa de juros de vencimento constante do Treasury dos EUA em 10 anos. | FRED, série [DGS10](https://fred.stlouisfed.org/series/DGS10), arquivo `dgs10.csv`. | É uma observação realizada, sem horário intradiário de publicação no CSV. Para evitar usar uma informação ainda não publicada, a base modelada usa somente o valor da observação anterior do ouro; lacunas de calendário recebem apenas preenchimento para frente antes dessa defasagem. |
| `FED_FUNDS_RATE` | `DFF` | Federal Funds Effective Rate dos Estados Unidos. | FRED, série [DFF](https://fred.stlouisfed.org/series/DFF), arquivo `dff.csv`. | É uma observação realizada, sem horário intradiário de publicação no CSV. A mesma regra conservadora é aplicada: preenchimento apenas para frente nas lacunas de calendário e defasagem de uma observação do ouro. |

## Campos não tratados como variáveis exógenas

| Campo | Motivo |
| --- | --- |
| `IS_HOLIDAY` | O arquivo bruto não traz fonte nem regra reproduzível para esse indicador. Ele não é candidato exógeno até que essa documentação exista. |
| `TARGET_UP` | Depende do preço em uma observação futura. Não pode ser usado como variável exógena porque causaria vazamento temporal. |

## Decisões de preparação já aprovadas

- Os nulos e os valores extremos observados não são imputados, removidos ou winsorizados; a matriz modelada preserva somente observações com alvo causal válido.
- O horizonte é a próxima observação de mercado.
- `TREASURY_10Y` e `FED_FUNDS_RATE` recebem preenchimento somente para frente e depois uma defasagem de uma observação do ouro.
- RF e PLS usam a mesma matriz causal aprovada. `TARGET_UP`, `DAY_OF_WEEK` e `MONTH` não entram como features.
- A STL indicou sazonalidade fraca nos períodos 5, 20 e 252. O período 5 é apenas a referência diária/semanal para candidatos sazonais; modelos sem sazonalidade permanecem na comparação.
