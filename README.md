# Comparação de Séries Temporais - Grupo 5

Fundação reproduzível para a comparação de SARIMAX, Holt-Winters, Random Forest e PLS Regression em cinco bases temporais com variáveis externas.

## Estado atual

Esta fundação organiza cinco pipelines independentes para SARIMAX, Holt-Winters, Random Forest e PLS Regression. As bases congeladas vivem em `bases/grupo1` a `bases/grupo5`; cada área em `analyses/grupoN/` adapta seu preparo sem alterar as demais. Nenhum resultado analítico é entregue nesta fase. O enunciado de referência está em `n2_series_temporais.pdf`.

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

- `bases/`: cinco bases congeladas e verificadas por checksum.
- `analyses/`: cinco áreas independentes, cada uma com pipeline, notebook e outputs locais.
- `config/`: contratos de datasets e disponibilidade temporal.
- `src/`: código reutilizável para contratos, proteção temporal e resultados.
- `tests/`: testes dos contratos e das proteções contra vazamento.
- `docs/`: requisitos, ADRs, specs e documentação da entrega.
- `reports/`: template e instruções do relatório HTML/PDF consolidado.

Valide uma área com `python analyses/grupoN/pipeline.py`; valide a integração com `python scripts/validate_project.py` e `python -m pytest`. Antes de mudar comportamento ou protocolo, atualize a spec ativa.
