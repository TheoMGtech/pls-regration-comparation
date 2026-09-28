# Checklist técnico final — Grupo 5: Ouro

## Documentação

- [x] **Concluído** — fonte e código da série documentados.
- [x] **Concluído** — período bruto de 1968-04-01 a 2014-04-10 documentado.
- [x] **Concluído** — frequência de dias de mercado e irregularidades documentadas.
- [x] **Concluído** — unidade em USD por onça fina documentada.
- [x] **Concluído** — significado como fixing da tarde em Londres documentado.
- [x] **Concluído** — Treasury de 10 anos e Fed Funds documentados.
- [x] **Concluído** — 368 preços ausentes auditados sem imputação do ouro.
- [x] **Concluído** — ausência de duplicidades validada.
- [x] **Concluído** — outliers descritos e preservados por falta de evidência de erro.
- [x] **Concluído** — lacunas e calendário irregular documentados.

## STL

- [x] **Concluído** — componente de tendência analisado.
- [x] **Concluído** — componente sazonal analisado nos períodos 5, 20 e 252.
- [x] **Concluído** — componente residual analisado.
- [x] **Concluído** — força sazonal 0,0 validada nos três períodos.

## Feature engineering

- [x] **Concluído** — lags 1, 5 e 20 validados contra a base bruta.
- [x] **Concluído** — média e desvio padrão móveis calculados após `shift(1)`.
- [x] **Concluído** — calendário cíclico por seno e cosseno documentado.
- [x] **Concluído** — externas com forward fill e defasagem causal validadas.
- [x] **Concluído** — ausência de leakage validada.
- [x] **Concluído** — base modelável sem NaNs validada.
- [x] **Concluído** — dicionário das 12 features gerado sem `TARGET` ou `TARGET_UP`.

## Modelos

- [x] **Concluído** — SARIMAX implementado e congelado.
- [x] **Concluído** — Holt-Winters implementado e congelado.
- [x] **Concluído** — Random Forest implementado e congelado com `random_state=42`.
- [x] **Concluído** — PLS Regression implementado e congelado com scaler por janela.

## Tuning

- [x] **Concluído** — grades e candidatos registrados.
- [x] **Concluído** — vencedores selecionados somente pela validação walk-forward.
- [x] **Concluído** — MAEs de validação registrados.
- [x] **Concluído** — hiperparâmetros congelados antes do teste.

## Teste final

- [x] **Concluído** — 296 origens comuns validadas.
- [x] **Concluído** — MAEs recalculados a partir das previsões.
- [x] **Concluído** — previsões, datas-alvo e resíduos alinhados.
- [x] **Concluído** — baseline comparável nas mesmas 296 origens.
- [x] **Concluído** — baseline mantido fora do ranking oficial.

## Resíduos

- [x] **Concluído** — gráficos real versus previsto, série residual e distribuição.
- [x] **Concluído** — ACF dos resíduos.
- [x] **Concluído** — Ljung-Box nos lags 1 a 20.
- [x] **Concluído** — interpretação de viés, dispersão e autocorrelação.

## Importância

- [x] **Concluído** — importância nativa e permutation importance do RF.
- [x] **Concluído** — coeficientes, VIP e permutation importance do PLS.
- [x] **Concluído** — contribuição das variáveis externas interpretada sem inferência causal.

## Especialização PLS

- [x] **Concluído** — teoria e componentes latentes.
- [x] **Concluído** — tuning de 1 a 12 componentes e seleção de 11.
- [x] **Concluído** — coeficientes padronizados.
- [x] **Concluído** — VIP Scores.
- [x] **Concluído** — permutation importance.
- [x] **Concluído** — vantagens, limitações e mudança de regime.

## Auditoria e reprodutibilidade

- [x] **Concluído** — construção de `TARGET` auditada.
- [x] **Concluído** — `TARGET_DATE` reconstruído e validado.
- [x] **Concluído** — ausência de leakage validada por código.
- [x] **Concluído** — walk-forward expansivo reproduzido em amostra.
- [x] **Concluído** — MAEs armazenados e recalculados conferem.
- [x] **Concluído** — seed, versões, parâmetros, tempos, origens e features registrados.
- [x] **Concluído** — checksums dos artefatos congelados registrados.

## Situação final

Não há pendência técnica da base de ouro. A redação de `05_relatorio` está fora deste escopo e não foi alterada.
