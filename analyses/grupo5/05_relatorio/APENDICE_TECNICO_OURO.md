# Apêndice técnico - Base Ouro

## A. Escopo e fontes de verdade

- Resultado oficial: V1 incorporada em `main` e `develop` no commit `885edaa`.
- Capítulo documental de origem: `docs/grupo5-ouro-relatorio`, commit `72417a5`.
- Estudo complementar: V2, commit imutável de referência `d6f67bd`.
- A V2 não substitui ranking, hiperparâmetros, previsões ou conclusão oficial da V1.

## B. Protocolo V1

| Item | Valor |
|---|---|
| Base oficial | `bases/grupo5/gold_daily_modeling.csv` |
| Linhas modeláveis | 9.864 |
| Horizonte | 1 observação real futura |
| Split | 70% treino, 15% validação, 15% teste |
| Origens | 296 validação + 296 teste |
| Janela | Expansiva |
| Passo | 5 observações |
| Métrica oficial | MAE fora da amostra, USD/onça troy |
| Seed RF | 42 |
| Estado | `final_results_frozen` |

O manifesto de origens está em `outputs/origin_manifest.csv`. O contrato integral, incluindo versões, grades e decisões humanas, está em `outputs/protocol.json`.

## C. Hiperparâmetros congelados

| Modelo | Configuração final |
|---|---|
| SARIMAX | `(0,1,2) x (0,0,1,5)` |
| Holt-Winters | tendência aditiva, sazonalidade aditiva, período 5, sem damping |
| Random Forest | 300 árvores, profundidade 20, `min_samples_split=10`, `min_samples_leaf=5`, `max_features=1.0` |
| PLS Regression | 11 componentes, scaler reajustado em cada janela |

Os candidatos completos permanecem em `outputs/tuning_candidates_*.csv`. O teste final não retroagiu para alterar tuning ou features.

## D. Ranking e baseline

| Posição | Modelo | MAE de teste |
|---:|---|---:|
| 1 | Holt-Winters | 11,5331 |
| 2 | SARIMAX | 11,5988 |
| 3 | PLS Regression | 11,6002 |
| 4 | Random Forest | 14,2826 |

Persistência tem MAE 11,6377 nas mesmas 296 origens. É baseline diagnóstico e não integra o ranking oficial.

## E. Contexto temporal e volatilidade

- Movimento absoluto mediano no teste: 8,50 USD/onça.
- Movimento absoluto médio nas 296 origens: 11,6377 USD/onça.
- Movimento absoluto médio no histórico completo: aproximadamente 3,8893 USD/onça.
- O PLS teve MAE de validação 2,9701 e MAE de teste 11,6002. Ambos estão na mesma unidade, mas pertencem a períodos com escala e volatilidade diferentes.

Essa diferença é evidência de mudança da dificuldade temporal. Não prova, sozinha, uma causa econômica específica.

## F. Resíduos e Ljung-Box

| Modelo | Média residual | Desvio | Rejeições em 20 lags | p-valor lag 20 |
|---|---:|---:|---:|---:|
| Holt-Winters | 0,1131 | 15,7363 | 0 | 0,4041 |
| PLS Regression | 0,2337 | 15,8807 | 0 | 0,3550 |
| SARIMAX | 0,3621 | 15,7470 | 1 | 0,3162 |
| Random Forest | 3,1615 | 20,5757 | 3 | 0,4008 |

O arquivo `outputs/ljung_box.csv` preserva os 80 resultados, 20 por modelo. A tabela resumida evita despejar todos os lags no corpo principal.

## G. Importância e PLS

RF e PLS foram avaliados com permutation importance. RF também tem importância por redução de impureza; PLS tem coeficientes padronizados e VIP. No PLS, as cinco primeiras features por permutação são `GOLD_PRICE`, `GOLD_LAG_1`, `GOLD_ROLLING_MEAN_5`, `GOLD_LAG_5` e `GOLD_LAG_20`.

Os valores não estabelecem causalidade. Colinearidade pode repartir ou desestabilizar importâncias. O uso de 11 componentes para 12 features implica compressão dimensional pequena.

## H. Auditorias V1

Evidências principais em `analyses/grupo5/outputs/`:

- `audit_summary.json`: síntese da auditoria.
- `target_alignment_audit.csv`: construção e alinhamento de `TARGET`.
- `origin_audit.csv`: origens, datas e splits.
- `prediction_file_checks.csv`: cardinalidade, finitude e duplicidades.
- `prediction_alignment_audit.csv`: alinhamento entre modelos.
- `mae_recalculation_audit.csv`: MAE armazenado versus recalculado.
- `leakage_feature_checks.csv`: causalidade das features.
- `walkforward_window_audit.csv`: janelas expansivas.
- `rf_extrapolation_audit.csv`: limites do RF no nível.
- `frozen_artifacts_checksums.csv`: checksums registrados.

## I. V2 complementar - targets

| Configuração | Target | MAE reconstruído |
|---|---|---:|
| RF A8 | LEVEL | 39,5007 |
| RF A8 | DELTA | 12,1579 |
| RF A8 | LOG_RETURN | 11,7850 |
| RF A3 | LOG_RETURN | 11,2986 |

Transformar o alvo reduziu a dificuldade do RF A8 diante do nível crescente, mas DELTA e LOG_RETURN A8 ainda não superaram persistência. RF/LOG_RETURN/A3 superou persistência em 0,3390 USD/onça (2,91%), mas é classificado como `INFORMATIVE`: foi observado em especificação experimental posterior e não substitui o ranking V1.

## J. V2 complementar - ablation

| RF LEVEL | MAE | Diferença para FULL |
|---|---:|---:|
| FULL | 14,9906 | 0,0000 |
| sem `GOLD_PRICE` | 17,0820 | +2,0914 |
| sem lags do ouro | 14,6976 | -0,2929 |
| somente exógenas | 38,1406 | +23,1500 |

Remover `GOLD_PRICE` piorou o MAE em aproximadamente 14%. A pequena melhora sem todos os lags continuou inferior à persistência e não autoriza nova seleção. Exógenas isoladas não substituíram a dinâmica autorregressiva neste período e horizonte.

## K. V2 complementar - extrapolação, drift e redundância

- Faixa de `y_train` do diagnóstico RF A8: 252,90 a 725,75 USD/onça.
- Faixa de `y_test`: 647,75 a 1.877,75 USD/onça.
- 281 de 296 alvos de teste, ou 94,9%, superam o máximo observado no treino.
- Maiores deslocamentos padronizados selecionados: WTI, DGS2, `dgs2_lag1`, inclinação da curva, DTWEXB e volatilidades do ouro.
- Redundâncias observadas: DGS2 x `dgs2_lag1` (~0,9997), VIXCLS x `vix_lag1` (~0,9818) e `distance_ma20` x `gold_momentum_10` (~0,9289).

Drift e importância cobrem um único período de teste. A estabilidade entre regimes é `NOT_ASSESSABLE_SINGLE_TEST_PERIOD`.

## L. Ressalva de metadado V2

Estado final: `PASS_WITH_METADATA_RECONCILIATION_REQUIRED`.

Os arquivos brutos V2 registram a data da origem na coluna `target_date`. As tabelas consolidadas recuperam a data-alvo correta pelo manifesto V1 congelado. A correção é exclusivamente semântica e de metadado: não altera previsões, valores reais, origens ou MAEs.

## M. Hashes protegidos

| Artefato | SHA-256 |
|---|---|
| `gold_daily_modeling.csv` | `38622FE40A18C3E94B89971488468F762353ED4234234E054F0439918CB5D1AC` |
| `predictions.csv` | `83C52112B6DDE640F520F3F870D30F0927CB4A03103098B4C284B24662AC6EC0` |
| `metrics.csv` | `F9FE5418EB7F5F14357ADA49BA64B7264282A148B81D3B2F792AE673F708E92E` |
| `hyperparameters.csv` | `4CB56A13CB6CC3A31B8ACC60E2BB3DD3ECEAE1448EB698D39B1540BFC5203886` |
| `protocol.json` | `21F258988ABF0E585F426137F8FD16943997985C01F0AAFE204445F6481D74C5` |

Os 24 notebooks técnicos V1 também são protegidos por comparação de blobs Git com o commit de origem da branch.
