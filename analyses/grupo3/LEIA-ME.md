# Base 3 — protocolo final

Os quatro modelos preveem o PM2.5 da hora seguinte nas mesmas origens. O relatório paginado está em `05_relatorio/relatorio_base3.html` e `05_relatorio/relatorio_base3.pdf`.

## Resultado no teste

6.023 horas, de 2016-05-16 05:00 a 2017-02-28 22:00.

| Modelo | MAE (µg/m³) | Configuração escolhida na validação |
|---|---:|---|
| Random Forest | 9,5131 | 40 árvores, profundidade 12, folha mínima 5, divisão mínima 2, max_features 0,5 |
| PLS | 9,6643 | 14 componentes, preditores padronizados |
| SARIMAX | 10,2225 | ordem (0, 1, 1), sem sazonalidade |
| Holt-Winters | 12,9122 | suavização exponencial simples |

A grade da floresta variou árvores, profundidade, divisão, folha e amostragem de colunas. A do PLS foi até 16 componentes; 14 ficou melhor que 16 na validação. Holt-Winters com período de 24 horas perdeu na validação. As ordens sazonais do SARIMAX tiveram AIC menor no fim do treino e MAE maior na validação.

## Ordem de leitura

1. `05_relatorio/relatorio_base3.html` — texto completo.
2. `01_dados/06_matriz_de_modelagem.ipynb` — os 17 preditores usados por Random Forest e PLS.
3. `01_dados/03_feature_engineering.ipynb` — matriz exploratória de 671 colunas. Não é a matriz dos modelos.
4. `02_modelos/results/validation_protocol.json` — cortes, horizonte e preditores.
5. `04_especialista_PLS/` — conceito, implementação e leitura do PLS.
6. `03_resultados/` — MAE, resíduos, importância e comparação.
7. `02_modelos/<modelo>/01_otimizacao_hiperparametros.ipynb` e os dois notebooks seguintes — grade e previsões do protocolo final.

O checksum das bases congeladas está em `bases/grupo3/SHA256SUMS.txt`.

## Como repetir

Na raiz do projeto:

```bash
.venv/bin/python analyses/grupo3/02_modelos/run_protocolo_final.py
.venv/bin/python analyses/grupo3/05_relatorio/gerar_relatorio.py
```

O código do protocolo está em `02_modelos/protocolo_final.py`.
