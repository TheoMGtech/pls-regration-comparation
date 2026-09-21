# Spec 003 - Pipelines colaborativas independentes

## Objetivo

Preparar cinco áreas independentes, uma por base congelada, para executar SARIMAX, Holt-Winters, Random Forest e PLS Regression com proteção compartilhada contra vazamento e regressões de integração.

## Critérios de aceitação

1. Há exatamente cinco contratos, arquivos congelados e áreas `analyses/grupo1` a `analyses/grupo5`.
2. Todo arquivo congelado coincide com seu checksum e possui eixo temporal parseável; CSVs usam checksum com finais de linha normalizados para LF, e XLSX usa bytes brutos. Duplicidades brutas conhecidas são contadas no contrato e devem ser tratadas pela pipeline responsável antes da modelagem.
3. Cada área contém README, pipeline smoke, notebook e diretório de outputs com contrato comum.
4. Cada pipeline pode validar sua base sem executar ou alterar a análise de outro integrante.
5. O consolidado aceitará somente CSVs de previsões, métricas, parâmetros, importância e Ljung-Box no esquema definido pelo núcleo.
6. Não há registro diário de demandas neste repositório; o desvio do enunciado permanece documentado.
