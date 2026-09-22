# Documentação da base - Grupo 5 (ouro)

Este documento cobre apenas a documentação inicial exigida no item 5.1 da atividade. Não registra decisões de limpeza, tratamento de valores atípicos, regularização temporal, seleção de features, escolha de modelo ou hiperparâmetros, pois essas etapas ainda não foram definidas pelo grupo.

## Base e variável-alvo

| Item | Registro atual |
| --- | --- |
| Arquivo bruto | `bases/grupo5-tratamento/gold_daily_prices.csv` |
| Fonte | Série fornecida ao Grupo 5. O arquivo recebido não identifica a fonte primária; ela deve ser confirmada antes da entrega final. |
| Descrição | Série histórica de preços do ouro, com uma observação por dia útil. |
| Período bruto | 1968-04-01 a 2014-04-10 (12.009 registros). |
| Frequência observada | Diária em dias úteis: há registros de segunda a sexta-feira. Não houve regularização de calendário nesta etapa. |
| Variável-alvo | `VALUE` no arquivo bruto; renomeada para `GOLD_PRICE` na base modelada. |
| Unidade da variável-alvo | Não informada no arquivo fornecido. Não deve ser assumida como moeda, onça ou outra unidade sem confirmação da fonte primária. |
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

## Escopo ainda pendente

Ainda serão documentados, na etapa apropriada: decisões de limpeza dos 368 valores ausentes do preço, investigação de valores atípicos e irregularidades, STL, features temporais, definição final das externas por modelo, horizonte, walk-forward e otimização.
