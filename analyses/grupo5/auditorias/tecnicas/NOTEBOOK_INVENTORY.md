# Inventário dos notebooks técnicos — Grupo 5: Ouro

Este inventário cobre os 24 notebooks técnicos. `05_relatorio` não faz parte da refatoração.

## Documentação, preparação e análise da base

- `01_dados/01_documentacao_bases.ipynb` — Documentação da base de ouro
- `01_dados/02_limpeza_preparacao.ipynb` — Limpeza e preparação da base
- `01_dados/03_feature_engineering.ipynb` — Engenharia de features
- `01_dados/04_analise_exploratoria.ipynb` — Análise exploratória da série de ouro
- `01_dados/05_STL_decomposicao.ipynb` — Decomposição STL

## SARIMAX

- `02_modelos/SARIMAX/01_otimizacao_hiperparametros.ipynb` — SARIMAX — otimização de hiperparâmetros
- `02_modelos/SARIMAX/02_walkforward_validacao.ipynb` — SARIMAX — teste final walk-forward
- `02_modelos/SARIMAX/03_previsoes_residuos.ipynb` — SARIMAX — previsões e resíduos

## Holt-Winters

- `02_modelos/Holt_Winters/01_otimizacao_hiperparametros.ipynb` — Holt-Winters — otimização de hiperparâmetros
- `02_modelos/Holt_Winters/02_walkforward_validacao.ipynb` — Holt-Winters — teste final walk-forward
- `02_modelos/Holt_Winters/03_previsoes_residuos.ipynb` — Holt-Winters — previsões e resíduos

## Random Forest

- `02_modelos/Random_Forest/01_otimizacao_hiperparametros.ipynb` — Random Forest — otimização de hiperparâmetros
- `02_modelos/Random_Forest/02_walkforward_validacao.ipynb` — Random Forest — teste final walk-forward
- `02_modelos/Random_Forest/03_previsoes_residuos.ipynb` — Random Forest — previsões e resíduos

## PLS Regression

- `02_modelos/PLS_Regression/01_otimizacao_hiperparametros.ipynb` — PLS Regression — otimização de hiperparâmetros
- `02_modelos/PLS_Regression/02_walkforward_validacao.ipynb` — PLS Regression — teste final walk-forward
- `02_modelos/PLS_Regression/03_previsoes_residuos.ipynb` — PLS Regression — previsões e resíduos

## Consolidação dos resultados

- `03_resultados/01_MAE_consolidado.ipynb` — MAE consolidado da base de ouro
- `03_resultados/02_analise_residuos_Ljung_Box.ipynb` — Comparação dos resíduos e Ljung-Box
- `03_resultados/03_importancia_features.ipynb` — Importância das features
- `03_resultados/04_comparacao_modelos.ipynb` — Comparação técnica final dos modelos

## Especialização em PLS

- `04_especialista_PLS/01_estudo_conceitual_PLS.ipynb` — PLS Regression — estudo conceitual
- `04_especialista_PLS/02_implementacao_PLS.ipynb` — PLS Regression — implementação causal
- `04_especialista_PLS/03_interpretacao_resultados.ipynb` — PLS Regression — interpretação dos resultados

## Auditorias técnicas

As auditorias de target, origens, leakage, walk-forward, MAE e extrapolação estão consolidadas em `AUDITORIA_RESULTADOS.md` e nos CSVs de `outputs/`.

## Convenção de execução

Os notebooks de tuning e teste final preservam o código original, mas suas células pesadas estão marcadas como `execucao-pesada` e `nao-executar`. Células leves exibem os artefatos congelados sem refazer modelos.
