# Roteiro da apresentação - PLS do Grupo 5 e estudo de caso Ouro

Material visual principal: `relatorio_ouro.html`.

## BLOCO A - Aula geral de PLS (5 a 8 minutos)

Este bloco é independente da Base Ouro. Abra diretamente as páginas 1 a 9 do módulo didático.

| Tempo | Seção/página a abrir | O que falar | Mensagem principal |
|---:|---|---|---|
| 0:00-0:40 | Aula PLS - página 1 | Motivar o método para predictors correlacionados e resposta contínua. | PLS une redução supervisionada e regressão. |
| 0:40-1:20 | Página 2 | Explicar multicolinearidade com lags e médias móveis. | Correlação entre features dificulta coeficientes, não torna previsão impossível. |
| 1:20-2:00 | Página 3 | Mostrar o fluxo `X -> pesos -> componentes -> y` e a fórmula `t_k = Xw_k`. | Componentes são combinações construídas, não causas. |
| 2:00-2:40 | Página 4 | Comparar PLS e PCA pela tabela. | PCA resume `X`; PLS procura estrutura útil para prever `y`. |
| 2:40-3:30 | Página 5 | Explicar scaling e escolha temporal de `n_components`. | Scaling é ajustado no treino; 11/12 não é variância explicada. |
| 3:30-4:15 | Página 6 | Situar PLS como regressão tabular em séries temporais. | Causalidade vem das features e do protocolo, não do nome do modelo. |
| 4:15-5:10 | Página 7 | Percorrer treino, validação walk-forward, congelamento e teste. | Teste final não escolhe componentes nem features. |
| 5:10-6:00 | Página 8 | Diferenciar coeficientes, VIP e permutation importance. | Interpretações são complementares e não causais. |
| 6:00-7:00 | Página 9 | Comparar PLS, SARIMAX, Holt-Winters e RF. | Não existe vencedor universal; contexto e protocolo decidem. |

Se o tempo total estiver apertado, una as páginas 2-3 e 6-7; preserve obrigatoriamente páginas 4, 5, 8 e 9.

## BLOCO B - Estudo de caso Ouro (5 a 7 minutos)

| Tempo | Seção/página a abrir | O que falar | Mensagem principal |
|---:|---|---|---|
| 0:00-1:10 | Aula PLS - página 10 | Apresentar 9.864 observações, 12 features, horizonte 1, 296 origens em validação e teste, busca 1-12 e escolha 11. | Ouro é o primeiro estudo de caso completo. |
| 1:10-2:00 | Página 10 + gráfico de componentes | Distinguir MAE validação 2,9701 de teste 11,6002 e explicar períodos diferentes. | A diferença não é mudança de unidade. |
| 2:00-2:50 | Ranking MAE e persistência | Mostrar PLS em 3º, Holt-Winters 11,5331 e persistência 11,6377 fora do ranking. | Os três primeiros ficaram muito próximos. |
| 2:50-3:40 | Importância das features | Destacar preço atual, lag 1, média móvel e lags 5/20. | A memória recente domina neste horizonte; importância não é causalidade. |
| 3:40-4:30 | Resíduos e Ljung-Box | Destacar 0 rejeições para PLS e sua dispersão residual. | Diagnóstico residual complementa o MAE. |
| 4:30-5:20 | V2 - targets, ablation e extrapolação | Mostrar LEVEL/DELTA/LOG_RETURN, ablation e 94,9% acima do máximo de treino. | V2 explica limitações, mas não substitui a V1. |
| 5:20-6:00 | Conclusão local - Ouro | Reforçar limitações e ranking oficial. | O caso Ouro não autoriza conclusão geral sobre PLS. |

## BLOCO C - Comparação futura das cinco bases (1 a 2 minutos)

| Tempo | Seção/página a abrir | O que falar | Mensagem principal |
|---:|---|---|---|
| 0:00-0:50 | Aula PLS - página 11 | Mostrar o template e a tabela; Ouro é a única linha preenchida. | As Bases 1-4 continuam explicitamente pendentes. |
| 0:50-1:30 | Página 12 | Ler as perguntas orientadoras, sem respondê-las. | Vitórias, posição média e conclusão global só existirão após consolidação. |

## Perguntas prováveis

- **11 de 12 componentes significa 91,7% da variância?** Não. É apenas a proporção de dimensões retidas; a PLS não admite essa leitura por divisão simples.
- **Por que o MAE de validação foi 2,9701 e o de teste 11,6002?** São janelas temporais distintas, na mesma unidade, com escala e volatilidade diferentes.
- **Por que Holt-Winters venceu se a sazonalidade foi fraca?** A configuração congelada teve o menor MAE nas origens finais; isso não transforma a STL em evidência de sazonalidade forte.
- **A V2 encontrou modelo melhor?** Encontrou RF/LOG_RETURN/A3 com MAE 11,2986, mas como resultado exploratório `INFORMATIVE`; não substitui a V1.
- **Qual é a conclusão global do PLS?** Ainda não existe: quatro bases permanecem sem resultados consolidados.
