# Manifesto de entrega - Base Ouro

## Identificação

- Branch de trabalho: `finalize/grupo5-ouro-entrega`.
- Base da branch: `docs/grupo5-ouro-relatorio` em `72417a55adae352d52926182c8bc63213adfb77c`.
- V1 oficial incorporada em `main`/`develop`: `885edaab761981eae97f5224dc1740d2310c0214`.
- Fonte seletiva V2: `d6f67bd789ce780af2e5472f6b1fc47015e89f27`.
- Data de fechamento: 04/10/2026.

O SHA do commit de fechamento é registrado no histórico Git e informado no ato da entrega; ele não pode ser autorreferenciado dentro do próprio commit.

## Arquivos principais

| Arquivo | Finalidade |
|---|---|
| `relatorio.ipynb` | Fonte executável leve e auditável do capítulo Ouro |
| `relatorio_ouro.html` | Relatório autocontido e material visual da apresentação |
| `relatorio_ouro.pdf` | Versão paginada para entrega e leitura |
| `build_report.py` | Composição reprodutível do HTML a partir do notebook; o PDF é impresso pelo Edge já instalado |
| `APENDICE_TECNICO_OURO.md` | Evidências detalhadas e rastreabilidade |
| `CHECKLIST_ATIVIDADE_OURO.md` | Atendimento literal dos requisitos locais/globais |
| `ROTEIRO_APRESENTACAO_OURO.md` | Sequência, tempo e mensagens para apresentação |
| `REFERENCIAS_OURO.md` | Fontes institucionais, aquisição, bibliotecas e artigos |
| `MANIFESTO_ENTREGA_OURO.md` | Inventário e governança desta entrega |
| `VALIDACAO_FINAL_OURO.json` | Hashes antes/depois e resultados de QA |

## Gráficos complementares

- `assets/v2_targets.png`: compara LEVEL, DELTA e LOG_RETURN no RF A8 e destaca RF/LOG_RETURN/A3.
- `assets/v2_ablation.png`: resume FULL, remoção do preço, remoção de lags e somente exógenas.
- `assets/v2_rf_drift_extrapolacao.png`: sintetiza faixas de treino/teste, 94,9% acima do máximo de treino e drift selecionado.

## Fonte dos resultados

- V1: somente `analyses/grupo5/outputs/` e a base congelada.
- V2: somente evidências consolidadas selecionadas do commit `d6f67bd`.
- Nenhum tuning, treinamento, walk-forward ou otimização foi executado nesta etapa.

## Artefatos oficiais protegidos

- `bases/grupo5/gold_daily_modeling.csv`.
- `analyses/grupo5/outputs/predictions.csv`.
- `analyses/grupo5/outputs/metrics.csv`.
- `analyses/grupo5/outputs/hyperparameters.csv`.
- `analyses/grupo5/outputs/protocol.json`.
- 24 notebooks técnicos em `01_dados/`, `02_modelos/`, `03_resultados/` e `04_especialista_PLS/`.

## Evidências V2 incorporadas

- `evidencias_v2/target_comparison_selected.csv`.
- `evidencias_v2/ablation_selected.csv`.
- `evidencias_v2/rf_a8_feature_drift_selected.csv`.
- `evidencias_v2/v2_validation_summary.json`.
- `evidencias_v2/V2_FINDINGS_FINAL.md`.

Nenhum arquivo bruto local de `experiments/` foi adicionado.

## Itens externos a esta entrega

- Outras quatro bases.
- Ranking global, vitórias e posição média.
- Participantes e responsabilidades globais.
- Conclusão consolidada das cinco bases.
- Resultados das Bases 1-4 necessários para preencher a comparação e a conclusão global do PLS.
- Decisão do grupo sobre o registro diário de demandas.
