# Comparação de Séries Temporais - Grupo 5

Fundação reproduzível para a comparação de SARIMAX, Holt-Winters, Random Forest e PLS Regression em cinco bases temporais com variáveis externas.

## Estado atual

Esta entrega estabelece documentação, contratos, testes, CI e gestão de demandas. Nenhum modelo foi treinado nesta fase. As bases agora reunidas em `bases/` devem ser documentadas e congeladas pelo grupo antes da modelagem; a série inicialmente associada ao Grupo 5 está em `bases/grupo5/gold_daily_prices_targets.csv`. O enunciado de referência está em `n2_series_temporais.pdf`.

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
