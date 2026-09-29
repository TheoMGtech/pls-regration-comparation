# Pipeline Base 2 — Metro Interstate Traffic Volume

**Responsável:** Bruna Carvalho Cardoso  
**Notebooks da entrega:** `analyses/grupo2/` (mesma estrutura dos outros grupos)  
**Código/resultados:** esta pasta (`pipelines/grupo2/`)

## Parâmetros

| Item | Valor |
|---|---|
| Granularidade | Horária (1h) |
| `random_state` | 67 |
| Treino / teste | 80% / 20% (cronológico) |
| Horizonte | 1 hora |
| Modelos | SARIMAX, Holt-Winters, Random Forest, PLS |

## Como rodar

Na raiz do repositório:

```bash
.venv/bin/python -m pipelines.grupo2.run_pipeline
```

Saídas em `pipelines/grupo2/outputs/`.
