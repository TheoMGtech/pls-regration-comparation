# Comparação técnica final — Base 2 (tráfego)

| Modelo | MAE teste | IC 95% | vs. sazonal 168h | Rank |
|---|---:|---|---:|---:|
| Random Forest | 157,76 | 139,6 – 176,8 | +44,3% | 1 |
| PLS Regression | 191,70 | 173,2 – 213,4 | +32,3% | 2 |
| Holt-Winters | 209,83 | 180,5 – 243,6 | +25,9% | 3 |
| SARIMAX | 263,68 | 242,7 – 286,7 | +6,9% | 4 |
| Sazonal 168h (baseline) | 283,31 | — | 0% | fora do ranking |
| Sazonal 24h | 554,75 | — | — | fora |
| Persistência 1h | 595,39 | — | — | fora |

Random Forest é o melhor modelo oficial desta base. PLS é o segundo e o especialista: mais rápido (~9 s no teste contra ~30 min do RF e ~7h46 do SARIMAX) e com resíduos horários mais limpos.

Holt-Winters supera o SARIMAX no MAE, mas 32% das previsões foram fallback semanal; a comparação com o PLS deve olhar também a mediana (HW 115 vs PLS 135). SARIMAX usa exógenas e ordem `(2,0,1)(0,1,1,24)`, convergência 83% no teste. Ele vence os baselines ingênuos e perde para os modelos tabulares porque, em horizonte de 1 h, os lags já carregam quase tudo.

O baseline permanece fora do ranking oficial. Não some este MAE ao da base de ouro.
