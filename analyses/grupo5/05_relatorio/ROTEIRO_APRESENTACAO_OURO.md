# Roteiro da apresentação - Base Ouro

Material visual principal: `relatorio_ouro.html`. Tempo local sugerido: 10 a 12 minutos, sem contar o bloco didático de PLS.

| Tempo | Seção/página a abrir | O que falar | Mensagem principal |
|---:|---|---|---|
| 0:00-0:40 | Capa e resumo executivo | Delimitar base Ouro, V1 oficial e V2 complementar. | A entrega preserva o experimento oficial e usa a V2 apenas para explicar limites. |
| 0:40-1:30 | Base, qualidade e causalidade | Fonte, unidade, 9.864 linhas, externas defasadas e ausência de leakage. | A comparação só é válida porque a informação respeita a origem. |
| 1:30-2:10 | STL e features | Mostrar tendência forte e força sazonal 0 nos períodos 5, 20 e 252. | Período 5 é referência operacional, não evidência de sazonalidade forte. |
| 2:10-3:00 | Protocolo walk-forward | Explicar 70/15/15, 296 origens, horizonte 1 e parâmetros congelados. | Os quatro modelos enfrentam exatamente as mesmas origens e alvos. |
| 3:00-4:10 | Ranking MAE e persistência | Apresentar o ranking e comparar o ganho inferior a 1% de Holt-Winters. | O vencedor formal existe, mas os três primeiros estão muito próximos. |
| 4:10-5:00 | Volatilidade e mudança de dificuldade | Contrastar validação PLS 2,9701 com teste 11,6002 sem chamar de mudança de unidade. | Períodos diferentes tiveram dificuldade e volatilidade diferentes. |
| 5:00-5:50 | Resíduos e Ljung-Box | Destacar 0 rejeições para Holt-Winters/PLS, 1 para SARIMAX e 3 para RF. | RF deixou maior dispersão, subestimação e alguma estrutura residual. |
| 5:50-6:40 | Importância das features | Mostrar dominação do preço recente e lags; evitar linguagem causal. | Horizonte curto é predominantemente autorregressivo nesta amostra. |
| 6:40-7:30 | V2 - LEVEL, DELTA e LOG_RETURN | Abrir `v2_targets.png`; mostrar como targets transformados reduzem a dificuldade do RF A8. | Transformar o alvo ajuda a diagnosticar extrapolação, mas não reabre o ranking. |
| 7:30-8:20 | V2 - ablation | Abrir `v2_ablation.png`; comparar FULL, sem preço, sem lags e somente exógenas. | Mais features não garantem melhora; o preço atual continua essencial. |
| 8:20-9:10 | V2 - drift e extrapolação | Abrir `v2_rf_drift_extrapolacao.png`; explicar 94,9% dos alvos acima do máximo de treino. | Árvores não extrapolam naturalmente novos níveis e o regime de teste mudou. |
| 9:10-10:00 | Limitações e conclusão | Reforçar série até 2014, horizonte 1, exógenas conservadoras e um único teste. | V1 continua oficial; V2 orienta pesquisa futura, não substitui o resultado. |

## Bloco reservado

### Explicação didática de PLS Regression

Conteúdo a incorporar posteriormente a partir do outro chat. Reservar aproximadamente 3 a 4 minutos e inserir entre “Importância das features” e “V2 - LEVEL, DELTA e LOG_RETURN”.

O bloco deverá explicar, de forma visual, componentes latentes, colinearidade, padronização e leitura do resultado com 11 componentes. Esta entrega não desenvolve a aula completa.

## Perguntas prováveis

- **Por que Holt-Winters venceu se a sazonalidade foi fraca?** A configuração selecionada teve o menor MAE nas origens finais; isso não transforma a STL em evidência de sazonalidade forte.
- **Por que persistência quase empatou?** Em horizonte de uma observação, o preço atual é um preditor muito forte; o ganho do vencedor foi 0,90%.
- **Por que RF perdeu?** Houve limitação de extrapolação no nível, drift e redundância, além de maior estrutura residual.
- **A V2 encontrou modelo melhor?** Encontrou RF/LOG_RETURN/A3 com MAE 11,2986, mas como resultado exploratório posterior, classificado `INFORMATIVE`; não substitui V1.
- **Houve leakage?** A auditoria não encontrou evidência; externas e janelas foram defasadas causalmente.
