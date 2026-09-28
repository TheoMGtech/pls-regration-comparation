# Comparação técnica final — ouro

| Modelo | MAE de teste | Diferença para persistência | Melhora percentual vs. persistência | Diferença para o melhor |
|---|---:|---:|---:|---:|
| Holt-Winters | 11,5331 | -0,1046 | 0,8986% | 0,0000 |
| SARIMAX | 11,5988 | -0,0388 | 0,3336% | 0,0658 |
| PLS Regression | 11,6002 | -0,0375 | 0,3219% | 0,0671 |
| Random Forest | 14,2826 | +2,6449 | -22,7275% | 2,7495 |
| Persistência | 11,6377 | 0,0000 | 0,0000% | 0,1046 |

Holt-Winters obteve o menor MAE entre os quatro modelos. SARIMAX e PLS ficaram praticamente empatados: a diferença entre eles foi cerca de 0,0014 de MAE. Os três primeiros superaram a persistência, mas por margens pequenas; portanto, os resultados não sustentam uma declaração de superioridade ampla.

Random Forest ficou pior que a persistência, mas isso não indica erro de implementação. Ele usou as mesmas features e origens do PLS, com `random_state=42` e hiperparâmetros congelados. Árvores não extrapolam naturalmente além dos valores-alvo observados no treino. Em 18 origens, o valor real ultrapassou o maior `TARGET` disponível na janela de treino, situação que favorece subestimação pelo RF em um regime crescente.

O baseline permanece fora do ranking oficial. Os cálculos completos e não arredondados estão em `gold_model_comparison_summary.csv`.
