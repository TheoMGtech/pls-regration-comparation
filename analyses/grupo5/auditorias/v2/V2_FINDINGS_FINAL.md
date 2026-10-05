# Achados V2 usados na entrega Ouro

Fonte: commit `d6f67bd789ce780af2e5472f6b1fc47015e89f27` da branch `feature/gold-v2-deep-analysis`.

## Estado

A Stage B foi concluída. Foram auditados 99 experimentos canônicos, todos com 296 origens congeladas, previsões finitas, origens únicas, MAE reproduzido e reconstrução correta de preço para DELTA e LOG_RETURN. Nenhum modelo foi reexecutado durante a integração documental.

## Resultado de validação

`PASS_WITH_METADATA_RECONCILIATION_REQUIRED`.

Nos arquivos brutos, a coluna `target_date` rotula a data da origem. As tabelas consolidadas usam a data-alvo do manifesto V1 congelado. Essa reconciliação altera somente o rótulo de metadado; não altera previsões, `Y_TRUE`, as 296 origens ou os MAEs.

## Uso permitido na entrega

- Explicar a dificuldade de prever o nível crescente do ouro com árvores.
- Comparar LEVEL, DELTA e LOG_RETURN como diagnóstico complementar.
- Mostrar ablation, drift e redundância de forma descritiva.
- Registrar RF/LOG_RETURN/A3 como resultado `INFORMATIVE`, não como substituto do ranking V1.

A V1 permanece a modelagem oficial.
