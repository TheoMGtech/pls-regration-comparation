# Roteiro local — estudo de caso da Base Ouro

Material visual: `relatorio_ouro.html`. Este roteiro cobre somente o estudo de
caso. A aula geral de PLS e a comparação das cinco bases pertencem a
`../consolidado/roteiro_apresentacao.md`.

| Tempo | Seção a abrir | O que falar | Mensagem principal |
|---:|---|---|---|
| 0:00–0:50 | Capa e resumo | Apresentar V1 oficial e V2 complementar. | V2 não substitui o ranking congelado. |
| 0:50–1:40 | Dados e protocolo | Explicar 9.864 observações modeláveis, 12 features, horizonte 1 e causalidade temporal. | Não houve uso de informação futura. |
| 1:40–2:30 | Ranking MAE | Mostrar Holt-Winters 11,5331; SARIMAX 11,5988; PLS 11,6002; RF 14,2826. | Os três primeiros ficaram próximos. |
| 2:30–3:10 | Persistência e contexto | Comparar com 11,6377 e distinguir validação 2,9701 de teste 11,6002. | Janelas diferentes tiveram escala e volatilidade diferentes. |
| 3:10–4:00 | Resíduos e Ljung-Box | Destacar o diagnóstico residual do PLS e as ressalvas. | Diagnóstico complementa o MAE. |
| 4:00–4:50 | Importância das features | Mostrar memória recente, redundância e interpretação não causal. | Importância não equivale a causa. |
| 4:50–5:50 | V2: targets, ablation e drift | Explicar LEVEL/DELTA/LOG_RETURN, ablation e extrapolação do RF. | A V2 explica limites sem alterar a V1. |
| 5:50–6:30 | Limitações e conclusão | Reforçar o caráter local do caso Ouro. | Não há conclusão global antes das outras bases. |

## Perguntas prováveis

- **Por que validação e teste têm MAEs diferentes?** São janelas temporais
  distintas, na mesma unidade, com regimes de escala e volatilidade diferentes.
- **A persistência participa do ranking?** Não. É baseline diagnóstico.
- **A V2 encontrou um MAE menor?** Sim, RF/LOG_RETURN/A3 teve 11,2986, mas é
  resultado exploratório `INFORMATIVE` e não substitui a V1.
- **O que significa `PASS_WITH_METADATA_RECONCILIATION_REQUIRED`?** O campo
  `target_date` exigiu reconciliação de rótulo/metadado; previsões e MAEs não
  foram alterados.
- **Qual é a conclusão global?** Ainda não existe; depende das Bases 1–4.
