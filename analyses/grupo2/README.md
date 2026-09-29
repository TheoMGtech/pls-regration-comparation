# Base 2 — Metro Interstate Traffic Volume

**Responsável:** Bruna Carvalho Cardoso

## Ideia

Você roda os notebooks **em ordem**. Cada um **grava** o que o próximo precisa em `outputs/`.

Abra primeiro: `00_ORDEM_DE_EXECUCAO.ipynb`.

## Fluxo

```
01_dados (limpeza → features → EDA → STL)
    ↓ outputs/data/*.csv
02_modelos/* (tuning → walk-forward → resíduos)   ← um modelo por vez
    ↓ outputs/results/predictions_*.csv, metrics_*.json
03_resultados (MAE, Ljung-Box, importância, comparação)
04_especialista_PLS + 05_relatorio
```

## Atalho no terminal (opcional)

```bash
# na raiz do repo
source .venv/bin/activate
python analyses/grupo2/run_pipeline.py
```

## Ver resultados

- `outputs/results/mae_consolidado.csv`
- `outputs/figures/`
- `outputs/relatorio_base2.html`
