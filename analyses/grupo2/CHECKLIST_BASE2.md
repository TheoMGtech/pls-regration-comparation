# Checklist técnico final — Base 2: tráfego interestadual

## Documentação

- [x] **Concluído** — fonte UCI / MNDoT + Weather Underground documentada.
- [x] **Concluído** — período bruto 2012-10-02 a 2018-09-30 documentado.
- [x] **Concluído** — frequência horária, duplicatas e lacunas documentadas.
- [x] **Concluído** — unidade em veículos por hora documentada.
- [x] **Concluído** — significado como volume na I-94 oeste documentado.
- [x] **Concluído** — temperatura, chuva, neve, nuvens e feriado documentados.
- [x] **Concluído** — 7.629 timestamps duplicados e 7.387 h de lacuna auditados.
- [x] **Concluído** — feriado expandido para o dia inteiro.
- [x] **Concluído** — disponibilidade temporal das externas declarada (clima só com lag 1).

## STL

- [x] **Concluído** — STL somente no desenvolvimento (80%).
- [x] **Concluído** — tendência, sazonal diário e residual interpretados.
- [x] **Concluído** — força sazonal 0,806 com período 24.

## Feature engineering

- [x] **Concluído** — lags 1 a 336 e vizinhança 23/25/167/169.
- [x] **Concluído** — média e desvio móveis após deslocamento causal.
- [x] **Concluído** — encoding cíclico de hora, dia e mês.
- [x] **Concluído** — clima defasado; sem temperatura futura.
- [x] **Concluído** — RF e PLS partem do mesmo dicionário tabular.
- [x] **Concluído** — NaNs de warmup de lags removidos.

## Modelos

- [x] **Concluído** — SARIMAX com exógenas causais.
- [x] **Concluído** — Holt-Winters univariado, com salvaguarda 168h.
- [x] **Concluído** — Random Forest com `random_state=67`.
- [x] **Concluído** — PLS com scaler por janela e três conjuntos de features.

## Tuning

- [x] **Concluído** — grades e candidatos em CSV.
- [x] **Concluído** — vencedores só pela validação walk-forward.
- [x] **Concluído** — hiperparâmetros congelados antes do teste.

## Teste final

- [x] **Concluído** — 521 origens comuns.
- [x] **Concluído** — MAE só em `target_observed`.
- [x] **Concluído** — previsões, resíduos e tempos gravados.
- [x] **Concluído** — baselines nas mesmas origens, fora do ranking oficial.

## Resíduos

- [x] **Concluído** — série residual, ACF e Ljung-Box.
- [x] **Concluído** — diagnóstico horário em 168 origens consecutivas.
- [x] **Concluído** — viés, dispersão e autocorrelação interpretados.

## Importância

- [x] **Concluído** — importância nativa do RF.
- [x] **Concluído** — coeficientes padronizados, VIP e permutation do PLS.
- [x] **Concluído** — externas meteorológicas interpretadas sem causalidade.
- [ ] **Parcial** — tabela de coeficientes/p-valores do SARIMAX não foi exportada na execução; a especificação com exógenas está registrada.

## Especialização PLS

- [x] **Concluído** — teoria e componentes latentes.
- [x] **Concluído** — busca 1–32 componentes × 3 conjuntos de features.
- [x] **Concluído** — 15 componentes no conjunto `no_weather`.
- [x] **Concluído** — VIP, coeficientes e permutation.
- [x] **Concluído** — vantagens, limitações e papel das lags.

## Situação

A modelagem da Base 2 está congelada. Vitórias/posição média nas cinco bases e o relatório consolidado do grupo dependem das outras bases. A tabela de coeficientes do SARIMAX é a única lacuna local e **não exige** reexecução do walk-forward.
