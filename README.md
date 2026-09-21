# Comparação de Séries Temporais - Grupo 5

Fundação reproduzível para a comparação de SARIMAX, Holt-Winters, Random Forest e PLS Regression em cinco bases temporais com variáveis externas.

## Estado atual

Esta entrega estabelece documentação, contratos, testes, CI e gestão de demandas. Nenhum modelo foi treinado nesta fase. A primeira base congelada é a previsão do ouro: o dataset modelável está em `bases/grupo5/gold_daily_modeling.csv`; as fontes e o tratamento reprodutível estão em `bases/grupo5-tratamento/`; e `python bases/grupo5-tratamento/prepare_gold_dataset.py` o recria. A documentação de dados está em `docs/DATASET_CONFIG.md`. O enunciado de referência está em `n2_series_temporais.pdf`.

## Ambiente local

Use Python 3.11 e crie um ambiente virtual fora do versionamento:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest
```

## Organização

- `bases/`: bases congeladas que podem ser versionadas quando seu tamanho permitir.
- `config/`: contratos de datasets e disponibilidade temporal.
- `src/`: código reutilizável, sem implementação de modelos nesta fundação.
- `tests/`: testes dos contratos e das proteções contra vazamento.
- `docs/`: requisitos, ADRs, specs SDD e gestão versionada do grupo.
- `notebooks/`: exploração local; checkpoints são ignorados.
- `data/` e `results/`: dados e artefatos gerados locais, ignorados por padrão.

Antes de mudar comportamento ou protocolo, atualize a spec correspondente; depois derive plano, tarefas, testes e código.
