# Apêndice técnico consolidado

## Índice de evidências por base

| Base | Relatório local | Protocolo/resultados | Estado |
|---|---|---|---|
| Base 1 | `../grupo1/` | PENDENTE | não consolidada |
| Base 2 | `../grupo2/` | PENDENTE | não consolidada |
| Base 3 | `../grupo3/` | PENDENTE | não consolidada |
| Base 4 | `../grupo4/` | PENDENTE | não consolidada |
| Base 5 — Ouro | `../grupo5/` | `../../../analyses/grupo5/outputs/` | V1 oficial concluída |

## Base Ouro

O apêndice completo está em `../grupo5/apendice_tecnico.md`. Ele cobre protocolo,
tuning, candidatos, resíduos, Ljung-Box, ablation, diagnósticos V2, hashes e
ressalvas metodológicas. A V2 é complementar e mantém o estado
`PASS_WITH_METADATA_RECONCILIATION_REQUIRED`: a reconciliação de `target_date`
corrige o rótulo/metadado sem alterar previsões ou MAEs.

## Critério para o ranking global

Somente serão calculados número de vitórias e posição média quando as cinco
bases tiverem quatro MAEs oficiais e comparáveis dentro de cada base. Não será
calculada média direta de MAEs entre séries com escalas ou unidades diferentes.
