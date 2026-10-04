# Status da entrega - Base Ouro (Grupo 5)

Data de fechamento: 04/10/2026.

## Pronto nesta branch

- Relatório interpretativo da base Ouro com V1 oficial e V2 complementar.
- Ranking V1 preservado e baseline de persistência mantido fora do ranking.
- Contextualização do MAE, volatilidade, resíduos, importância e limitações.
- Integração seletiva dos achados concluídos da V2 a partir de `d6f67bd`.
- Gráficos sintéticos de targets, ablation, drift e extrapolação.
- HTML autocontido e PDF paginado com a mesma narrativa.
- Apêndice técnico, checklist, referências, roteiro e manifesto.

## Estado correto da V2

A Stage B está concluída. O antigo texto de `V2_STATUS.md` que marcava atividades como `deferred/not run` ficou desatualizado em relação a `V2_FINDINGS.md` e aos resultados finais do commit `d6f67bd`. Para a entrega, prevalece a evidência final desse commit.

O resultado da validação permanece `PASS_WITH_METADATA_RECONCILIATION_REQUIRED`: nos arquivos brutos V2, `target_date` rotula a data da origem. As tabelas consolidadas usam o `target_date` do manifesto V1 congelado. A reconciliação corrige apenas o rótulo de metadado; previsões, `Y_TRUE`, origens e MAEs não foram alterados.

## Fora do escopo da base Ouro

- Consolidação das outras quatro bases.
- Ranking global, vitórias e posição média entre bases.
- Participantes e responsabilidades do grupo completo.
- Conclusão global da atividade.
- Conteúdo didático completo de PLS Regression, reservado para incorporação posterior.
