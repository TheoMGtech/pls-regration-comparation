# Auditoria técnica dos resultados — Grupo 5: Ouro

Data da auditoria: 27/09/2026.

## Conclusão executiva

Os resultados de validação e teste podem permanecer congelados. Não foi identificado erro de alinhamento temporal, deslocamento de uma observação, divergência de `Y_TRUE`, leakage ou falha no walk-forward. Não é necessário repetir tuning nem previsões.

O `TARGET` não representa necessariamente o preço da próxima linha da base modelável. Ele foi construído antes da filtragem e representa o preço da próxima linha cronológica do arquivo bruto de ouro. Essa relação foi reconstruída e validada nas 9.864 linhas modeláveis.

## 1. Construção do TARGET

A ordem confirmada em `prepare_gold_dataset.py` é:

1. leitura da série bruta de ouro e das duas séries externas;
2. `left merge` das externas no calendário bruto do ouro;
3. `forward fill` somente das externas;
4. defasagem de uma linha bruta das externas;
5. criação de calendário, lags e janelas móveis;
6. criação de `TARGET = GOLD_PRICE.shift(-1)`;
7. remoção das linhas com `NaN` nas colunas modeláveis.

Portanto, `TARGET` é criado depois do merge e das features, mas antes do `dropna` e da formação da base modelável final.

Resultados da reconstrução:

| Verificação | Resultado |
|---|---:|
| Linhas no arquivo bruto | 12.009 |
| Linhas brutas com preço | 11.641 |
| Linhas brutas sem preço | 368 |
| Linhas modeláveis | 9.864 |
| TARGET igual ao próximo valor bruto | 9.864 |
| TARGET diferente do próximo valor bruto | 0 |
| Linhas comparáveis com uma próxima linha modelável | 9.863 |
| TARGET igual ao preço da próxima linha modelável | 9.435 |
| TARGET diferente do preço da próxima linha modelável | 428 |
| Linha final sem próxima linha modelável | 1 |

As 428 diferenças são estruturais. Linhas intermediárias do calendário bruto deixam de ser modeláveis quando algum lag, janela, externa ou TARGET fica ausente. Isso não muda o TARGET da origem anterior, que continua apontando para a próxima linha cronológica válida do arquivo bruto.

Exemplo: em 09/05/1968, o preço na origem é 39,70 e o TARGET é 39,80 em 10/05/1968. A próxima linha modelável é apenas 14/05/1968, com preço 39,60. O TARGET continua correto porque foi definido no calendário bruto antes da filtragem.

O artefato `target_alignment_audit.csv` contém, para cada linha, `DATE_ORIGIN`, preço na origem, `TARGET_DATE`, TARGET, próxima linha modelável e indicadores de correspondência.

## 2. Origens e splits

O protocolo foi reproduzido diretamente do código:

| Split | Origens | Primeira origem | Última origem | Primeira TARGET_DATE | Última TARGET_DATE | Passo |
|---|---:|---|---|---|---|---:|
| Validação | 296 | 27/06/2000, índice 6.904 | 21/05/2007, índice 8.379 | 28/06/2000 | 22/05/2007 | 5 |
| Teste | 296 | 06/06/2007, índice 8.384 | 03/04/2014, índice 9.859 | 07/06/2007 | 04/04/2014 | 5 |

- Treino inicial: índices 0 a 6.903, total de 6.904 linhas.
- Validação: faixa 6.904 a 8.383.
- Teste: faixa 8.384 a 9.863.
- As origens vêm exatamente de `range(início, fim, 5)`; 296 não resulta de corte acidental.
- Validação e teste não se sobrepõem.
- Horizonte: uma próxima linha real do calendário bruto do ouro, identificada por `TARGET_DATE`.

## 3. Baseline de persistência

O baseline foi reconstruído sem usar `metrics.csv`:

`Y_PRED = GOLD_PRICE_ORIGIN`

`Y_TRUE = TARGET` da mesma origem

Nas mesmas 296 origens do teste:

- número de previsões: 296;
- MAE: **11,6376689189**.

Nas 1.480 linhas consecutivas da faixa modelável de teste:

- MAE: **11,4379391892**.

Os valores diferem porque as 296 origens são uma amostra sistemática a cada cinco linhas modeláveis. O baseline consecutivo avalia todas as linhas do período e não é diretamente comparável ao protocolo oficial dos quatro modelos.

O baseline permanece uma referência diagnóstica e não entra no ranking oficial.

## 4. Alinhamento das previsões

Para cada um dos quatro modelos foram confirmados:

- 296 previsões;
- zero duplicidades em `DATE_ORIGIN + TARGET_DATE`;
- zero datas ausentes;
- origens e datas-alvo idênticas ao manifesto de teste;
- horizonte igual a 1;
- valores finitos;
- resíduos iguais a `Y_TRUE - Y_PRED`;
- `Y_TRUE` idêntico entre todos os modelos;
- `Y_TRUE` idêntico ao TARGET da base congelada.

Uma reprodução independente das previsões em três origens — início, meio e fim — apresentou diferença absoluta máxima de `2,27e-13`, apenas precisão numérica.

## 5. Recálculo dos MAEs

| Modelo | MAE armazenado | MAE recalculado | Diferença absoluta |
|---|---:|---:|---:|
| Holt-Winters | 11,5330902396 | 11,5330902396 | 1,78e-15 |
| SARIMAX | 11,5988410717 | 11,5988410717 | 3,55e-15 |
| PLS Regression | 11,6002116901 | 11,6002116901 | 1,78e-15 |
| Random Forest | 14,2826175651 | 14,2826175651 | 1,78e-15 |

As diferenças são exclusivamente de representação em ponto flutuante.

## 6. Leakage e walk-forward

Foram confirmados por inspeção do código e reconstrução numérica:

- `TARGET` e `TARGET_UP` não pertencem à matriz de features;
- `TARGET_UP` não existe na base modelada;
- `GOLD_LAG_1`, `GOLD_LAG_5` e `GOLD_LAG_20` coincidem com as defasagens causais no calendário bruto;
- médias e desvios móveis usam `GOLD_PRICE.shift(1)` antes da janela e não incluem o preço da origem;
- não existe `backfill`;
- as externas recebem `forward fill` e depois `shift(1)`;
- `TREASURY_10Y` e `FED_FUNDS_RATE` usados na origem correspondem à última informação conservadoramente disponível;
- PLS ajusta um novo `StandardScaler` dentro de cada janela de treino;
- Random Forest usa `random_state=42`;
- SARIMAX mantém as externas econômicas conhecidas na origem e altera somente o calendário conhecido da data-alvo;
- ML treina em `df.iloc[:origin]`, cujo último TARGET termina na própria data da origem;
- SARIMAX e Holt-Winters usam o histórico de preços até e incluindo a origem;
- a observação-alvo da origem nunca entra no treino;
- a janela expande a cada origem.

As janelas auditadas nos índices 8.384, 9.124 e 9.859 confirmaram essa regra.

## 7. Random Forest

O desempenho inferior não é causado por desalinhamento.

- RF e PLS usam as mesmas 12 features.
- As origens e `Y_TRUE` são idênticos.
- Os parâmetros congelados foram usados: 300 árvores, profundidade 20, `min_samples_leaf=5`, `min_samples_split=10` e `max_features=1.0`.
- Em scikit-learn, `max_features=1.0` significa 100% das features disponíveis em cada divisão, não apenas uma feature.
- Todas as 296 previsões do RF permaneceram dentro da faixa histórica dos TARGETs de treino.
- Em 18 origens, o valor real ficou acima do maior TARGET disponível no treino.

Esse comportamento é compatível com a limitação de árvores para extrapolar novos níveis. O RF não deve ser alterado apenas por ter perdido.

## 8. Veredito

- TARGET está correto: **sim**.
- TARGET_DATE foi validado: **sim, nas 9.864 linhas**.
- As 296 origens de validação e teste estão corretas: **sim**.
- Baseline 11,6377 foi reproduzido: **sim**.
- Os quatro modelos usam os mesmos `Y_TRUE`: **sim**.
- Os MAEs foram reproduzidos: **sim**.
- Existe leakage: **não foi encontrada evidência**.
- O walk-forward está correto: **sim**.
- Existe deslocamento temporal: **não**.
- RF está implementado incorretamente: **não**.
- Algum resultado precisa ser invalidado: **não**.
- É necessário repetir tuning: **não**.
- É necessário repetir previsões: **não**.
- Os resultados podem permanecer congelados: **sim**.

## Artefatos da auditoria

- `audit_summary.json`
- `target_alignment_audit.csv`
- `target_alignment_summary.csv`
- `target_mismatch_examples.csv`
- `origin_audit.csv`
- `baseline_persistencia.csv`
- `baseline_persistencia_todas_observacoes_teste.csv`
- `prediction_alignment_audit.csv`
- `prediction_file_checks.csv`
- `manual_alignment_sample.csv`
- `mae_recalculation_audit.csv`
- `leakage_feature_checks.csv`
- `leakage_feature_sample.csv`
- `walkforward_window_audit.csv`
- `walkforward_reproduction_sample.csv`
- `rf_extrapolation_audit.csv`

## Validação final do pacote

- 24 notebooks fora de `05_relatorio` analisados e compilados sem erro de sintaxe;
- nenhum notebook contém output de exceção armazenado;
- todos usam o kernel `pls-regration-py314`;
- nenhum notebook depende de caminho absoluto do computador;
- 81 CSVs de saída foram lidos com sucesso;
- 1.184 previsões finais: 296 por modelo;
- 80 resultados de Ljung-Box: 20 por modelo;
- 24 registros de importância: 12 para RF e 12 para PLS;
- 33 imagens verificadas como arquivos válidos e não vazios;
- hash da base coincide com o protocolo;
- seed permanece 42;
- protocolo permanece em `final_results_frozen`;
- `scripts/validate_project.py` não existe neste repositório;
- `pytest` foi executado, mas o repositório não contém testes coletáveis;
- a validação estrutural foi coberta pelas asserções dos notebooks e pelos artefatos desta auditoria.
