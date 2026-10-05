# Checklist interno de integração das bases

Este documento é controle interno de QA. Ele não integra diretamente o pacote
entregue ao professor.

## Regras de entrada

- [ ] Identificar branch, commit e responsável pela base.
- [ ] Usar somente resultados já concluídos e versionados.
- [ ] Não reexecutar tuning, treino, walk-forward ou teste final durante a integração.
- [ ] Não reconstruir métricas a partir de valores arredondados quando existir o
      artefato original.
- [ ] Confirmar que todos os modelos usam o mesmo horizonte e as mesmas origens
      finais dentro da base.
- [ ] Separar validação/tuning de teste final.
- [ ] Preservar baseline fora do ranking dos quatro modelos.
- [ ] Registrar unidade do alvo e proibir média direta de MAE entre bases com
      escalas diferentes.

## Checklist padronizado por base

### Identificação e documentação

- [ ] Nome da base e variável-alvo.
- [ ] Fonte institucional e URL de aquisição separadas.
- [ ] Período, frequência, unidade e horizonte.
- [ ] Qualidade dos dados, ausências, duplicidades e tratamento aplicado.
- [ ] Referência exata ao notebook ou relatório-fonte.

### Exploração temporal

- [ ] STL documentada.
- [ ] Período sazonal justificado.
- [ ] Força sazonal registrada.
- [ ] Força de tendência registrada, quando calculada.
- [ ] ACF/PACF ou diagnóstico temporal equivalente.

### Features e causalidade

- [ ] Dicionário de features.
- [ ] Disponibilidade de cada feature na origem.
- [ ] Lags e janelas móveis explicitamente deslocados.
- [ ] Tratamento de variáveis externas documentado.
- [ ] Evidência de ausência de leakage.

### Protocolo experimental

- [ ] Split temporal.
- [ ] Protocolo walk-forward.
- [ ] Número de origens de validação.
- [ ] Número de origens de teste.
- [ ] Frequência de refit.
- [ ] Hiperparâmetros finais dos quatro modelos.
- [ ] Evidência de que hiperparâmetros foram escolhidos antes do teste.

### Resultados obrigatórios

- [ ] MAE final de SARIMAX.
- [ ] MAE final de Holt-Winters.
- [ ] MAE final de Random Forest.
- [ ] MAE final de PLS Regression.
- [ ] Ranking local dos quatro modelos.
- [ ] Baseline diagnóstico identificado separadamente.
- [ ] Tabela de previsões/alvos do teste preservada.
- [ ] Resíduos dos quatro modelos preservados.
- [ ] Série/gráfico de resíduos.
- [ ] ACF residual.
- [ ] Ljung-Box com lags, estatística e p-valor.
- [ ] Feature importance do Random Forest.
- [ ] Interpretação do PLS: coeficientes, VIP e/ou permutation importance.
- [ ] Resultado e posição local do PLS.
- [ ] Limitações específicas da base.

### Integração editorial

- [ ] Criar ou atualizar docs/relatorios/grupoN/.
- [ ] Produzir uma página visual de estudo de caso para o consolidado.
- [ ] Resumir dados, protocolo, ranking, resíduos e interpretabilidade.
- [ ] Evitar tabelas brutas extensas no corpo principal.
- [ ] Atualizar docs/relatorios/consolidado/resultados_mae.csv.
- [ ] Preencher somente a linha da base validada.
- [ ] Atualizar ranking global apenas quando as cinco bases estiverem completas.
- [ ] Validar HTML, PDF, links e ausência de caminhos absolutos.

## Contrato mínimo recomendado de artefatos

Cada base deve fornecer, ou mapear inequivocamente, estes conteúdos:

| Conteúdo | Artefato recomendado |
|---|---|
| protocolo | protocol.json ou seção equivalente |
| MAEs e ranking | model_comparison_mae.csv |
| hiperparâmetros | selected_hyperparameters.csv |
| previsões | test_predictions.csv |
| resíduos | test_residuals.csv |
| Ljung-Box/ACF | ljung_box_comparison.csv |
| importance | feature_importance.csv |
| interpretação PLS | pls_coefficients_vip.csv |
| limitações | relatório local ou Markdown factual |

Nomes diferentes são aceitos, mas o mapeamento deve constar no manifesto da base.

## Diagnóstico de ingestão — Base 4 / Jena Climate

Referência auditada: origin/main em
8d77abfaf2fb8bc6cda10558ecb9fd16092f5c5f.

### Fontes versionadas com conteúdo

- bases/grupo4/doc_base4.md: documentação da base e decisões de tratamento.
- notebooks/grupo4/analise_notebook_jena_grupo5.md: síntese metodológica.
- notebooks/grupo4/trabalho_grupo5_pls_jena_horario.ipynb: notebook executado
  com resultados, tabelas e gráficos.
- bases/grupo4/jena_climate_2009_2016.csv: base original.

Os 25 notebooks em analyses/grupo4/ existem, mas estão vazios. A pasta de
resultados citada pelo notebook principal não está versionada em main.

### Resultados presentes nos outputs do notebook

| Posição | Modelo | MAE de teste |
|---:|---|---:|
| 1 | PLS | 0,3983 °C |
| 2 | SARIMAX | 0,4064 °C |
| 3 | Random Forest | 0,4114 °C |
| 4 | Holt-Winters | 0,4259 °C |

Baselines fora do ranking: persistência 0,6813 °C; sazonal ingênuo de 24 h
2,5642 °C.

Hiperparâmetros observados:

- PLS: n_components=40, conjunto T+exog, 46 features,
  StandardScaler;
- SARIMAX: order=(2,0,1), seasonal_order=(0,1,1,24), com exógenas;
- Random Forest: n_estimators=500, max_depth=None,
  max_features=0.8, min_samples_split=2, min_samples_leaf=1;
- Holt-Winters: tendência aditiva amortecida, sazonalidade aditiva,
  período 24.

STL no desenvolvimento: força sazonal Fs=0,686 e força de tendência
Ft=0,953.

Ljung-Box em lags 24 e 48 rejeita ausência de autocorrelação para os quatro
modelos (p exibido como 0,0). O PLS apresenta as menores estatísticas entre
eles e ACF residual pequena (lag 1=-0,0027; lag 24=-0,0129), sem eliminar a
rejeição formal.

Importância e interpretação disponíveis:

- Random Forest: importância por impureza e permutation importance;
- PLS: coeficientes padronizados, VIP e permutation importance;
- principais sinais PLS nos outputs: T_lag1, T_lag2, rho_lag1,
  T_lag3, T_rmax6, T_rmean6 e T_rmin6.

### Pontos de QA antes da publicação

- a execução informa 42 blocos de refit, mas alguns títulos e nomes de colunas
  ainda mencionam 16 refits/blocos;
- a tabela arredonda p-valores do Ljung-Box para 0,0, enquanto a síntese do PLS
  mostra 4,716e-16 no lag 24;
- os resultados estão embutidos no notebook, mas não estão separados em
  artefatos versionados para ingestão automática;
- essas inconsistências devem ser reconciliadas editorialmente, sem recalcular
  resultados ou alterar previsões.

### Bloqueio para ingestão definitiva

O notebook afirma gerar model_comparison_mae.csv,
selected_hyperparameters.csv, test_predictions.csv, test_residuals.csv,
ljung_box_comparison.csv, feature_importance.csv e
pls_coefficients_vip.csv, mas esses arquivos não estão em origin/main.

Antes de preencher o consolidado, recuperar esses artefatos exatos da execução
original ou exportá-los dos outputs armazenados no notebook, com revisão do
responsável pela Base 4. Não reexecutar modelos e não usar valores arredondados
do HTML como fonte quando houver artefato original disponível.
