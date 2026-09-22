# ADR 001 Stack de análise reproduzível

## Status

Aceito para a fundação.

## Contexto

O Grupo 5 precisa comparar modelos temporais com variáveis externas de forma reproduzível, auditável e compatível com CI. A modelagem não deve depender de notebooks ou ambientes pessoais não documentados.

## Decisão

Usar Python 3.11 com ambiente virtual local e versões fixadas em `requirements.txt`. O código reutilizável ficará em `src/pls_regration`; cada integrante trabalhará isoladamente em `analyses/grupoN/`, e notebooks delegarão regras reutilizáveis para `src/`. Pandas/Numpy tratarão dados, statsmodels suportará STL, SARIMAX e Holt-Winters, scikit-learn suportará Random Forest, PLS Regression, pré-processamento e métricas, e pytest executará a validação automatizada.

O CI usará Python 3.11 e instalará exatamente as dependências fixadas. Dados gerados, ambientes, segredos e contexto local de IA não serão versionados. Bases congeladas, documentação, contratos e testes serão versionados.

## Consequências

A reprodução começa com ambiente limpo e `pip install -r requirements.txt`. As versões deverão ser atualizadas deliberadamente em PR própria. Não serão adicionados modelos, tuning ou notebooks de resultado antes da aprovação da spec do protocolo experimental.
