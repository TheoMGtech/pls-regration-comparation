# Análise final dos resíduos

Os resíduos foram definidos como `real - previsto` e calculados a partir das previsões congeladas do teste final. Cada modelo possui 296 resíduos nas mesmas datas-alvo.

## Viés e variabilidade

- **Holt-Winters:** média 0,1131, mediana 0,9062 e desvio padrão 15,7363. A média está próxima de zero e não indica viés médio relevante.
- **SARIMAX:** média 0,3621, mediana 1,3112 e desvio padrão 15,7470. A dispersão é próxima à do Holt-Winters e o viés médio é pequeno.
- **PLS:** média 0,2337, mediana 1,0881 e desvio padrão 15,8807. O comportamento é semelhante ao dos dois modelos estatísticos.
- **Random Forest:** média 3,1615, mediana 2,6788 e desvio padrão 20,5757. O sinal positivo indica subestimação média, e a dispersão é maior que nos demais modelos.

As assimetrias foram -0,0940 para Holt-Winters, -0,0617 para SARIMAX, -0,0757 para PLS e 0,6226 para Random Forest. Assim, os três primeiros ficaram próximos de uma distribuição residual simétrica, enquanto o RF mostrou cauda positiva mais pronunciada.

## Autocorrelação e Ljung-Box

Holt-Winters e PLS não rejeitaram a hipótese de ausência de autocorrelação em nenhum dos lags 1 a 20. SARIMAX apresentou uma rejeição isolada, no lag 1; isso é evidência pontual e não sustenta uma conclusão ampla de dependência residual. Random Forest apresentou rejeição em 3 de 20 lags, indicando alguma estrutura remanescente, embora a maior parte dos lags não tenha rejeitado.

Considerando centralização, dispersão e Ljung-Box, Holt-Winters apresentou o conjunto de resíduos mais próximo de ruído entre os quatro, com PLS muito próximo. Essa interpretação não substitui o MAE e não transforma diferenças pequenas em superioridade ampla.

Os valores completos estão em `residual_diagnostics_summary.csv` e `ljung_box.csv`; as séries, distribuições e ACFs estão nos gráficos `residual_*`.
