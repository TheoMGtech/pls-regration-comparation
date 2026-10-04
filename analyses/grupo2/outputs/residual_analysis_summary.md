# Análise final dos resíduos — Base 2

Resíduo = real − previsto. O MAE oficial usa 521 origens espaçadas de 11 h, somente com alvo observado. O Ljung-Box **interpretativo** usa 168 previsões consecutivas de 1 h (`residual_diagnostics.csv`), para o lag 24 ter sentido horário.

## Viés e variabilidade (teste oficial)

| Modelo | Viés | MAE | Mediana AE | ACF(1) na sequência amostrada |
|---|---:|---:|---:|---:|
| Random Forest | +13,8 | 157,8 | 101,3 | 0,12 |
| PLS | +2,4 | 191,7 | 135,1 | 0,00 |
| Holt-Winters | −4,3 | 209,8 | 115,0 | 0,09 |
| SARIMAX | −11,8 | 263,7 | 179,4 | 0,00 |

O PLS é o mais centrado. O RF subestima um pouco em média, mas erra menos em módulo. O Holt-Winters teve **167** fallbacks para o lag 168h (32% das origens); o MAE dele mistura modelo e baseline semanal.

O maior erro compartilhado é 2018-07-04 05:00 (feriado): real 698, RF ~2.545, PLS ~2.390. Isso é padrão de calendário raro, não falha de implementação.

## Autocorrelação e Ljung-Box (168 h consecutivas)

| Modelo | ACF(1) | p LB lag 1 | p LB lag 24 |
|---|---:|---:|---:|
| Random Forest | 0,50 | ≈ 0 | ≈ 0 |
| PLS | −0,01 | 0,92 | 0,061 |
| Holt-Winters | 0,77 | ≈ 0 | ≈ 0 |
| SARIMAX | 0,05 | 0,53 | 0,026 |

O PLS deixou o resíduo horário mais próximo de ruído entre os quatro. O RF ganha no MAE e ainda deixa autocorrelação: árvores capturam nível e sazonalidade, mas não um AR residual. Holt-Winters falha no diagnóstico porque muitas previsões são o próprio lag semanal. SARIMAX limpa o lag 1, mas o lag 24 ainda rejeita em 5%.

A tabela consolidada no relatório principal deve usar estes p-valores horários, não o Ljung-Box da sequência amostrada de 11 h (essa coluna existe em `mae_consolidado.csv` só como rastreio).
