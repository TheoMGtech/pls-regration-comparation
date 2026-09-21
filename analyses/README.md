# Áreas independentes de análise

Cada `grupoN` é dono de uma única base congelada e executa os quatro modelos exigidos: SARIMAX, Holt-Winters, Random Forest e PLS Regression. Não altere contratos ou código de outro grupo para adaptar sua base.

1. Complete o dicionário de dados e a referência da fonte no contrato central.
2. Desenvolva limpeza e features no pipeline da sua área, preservando causalidade temporal.
3. Use o notebook como narrativa exploratória; regras reutilizáveis devem ficar em código testável.
4. Grave os cinco CSVs definidos em `src/pls_regration/results.py` em `outputs/` ao concluir a análise.

Valide apenas sua área com `python analyses/grupoN/pipeline.py --smoke`. Valide a integração inteira com `python scripts/validate_project.py` e `python -m pytest`.
