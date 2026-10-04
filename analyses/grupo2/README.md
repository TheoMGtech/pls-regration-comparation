# Base 2 — Metro Interstate Traffic Volume

**Responsável:** Bruna Carvalho Cardoso

Implementação dos modelos Random Forest, PLS Regression, Holt-Winters e
SARIMAX para previsão horária de volume de tráfego.

## Protocolo

- granularidade: 1 hora;
- horizonte: próxima hora;
- divisão externa cronológica: 80% desenvolvimento / 20% teste;
- `random_state=67`;
- mesmas origens finais para os quatro modelos;
- reajuste do modelo em toda origem e previsão de somente um passo;
- MAE calculado apenas onde o alvo original foi observado;
- tuning walk-forward em aproximadamente 260 origens dentro dos primeiros
  80%, sem usar o teste final;
- PLS escolhe conjuntamente conjunto de variáveis e 1–32 componentes;
- Random Forest compara 12 configurações e Holt-Winters compara três janelas;
- SARIMAX faz 72 triagens BIC e valida as cinco melhores estruturas;
- flags indicam quando lags do alvo vieram de observação real ou imputação;
- janelas móveis documentadas para viabilizar o custo da série horária.

A maior lacuna da base tem 7.387 horas. Para não criar quase dez meses de
tráfego sintético, a análise utiliza o segmento posterior a essa lacuna. As
horas ausentes restantes são preenchidas somente com informação do passado.

## Como executar

Abra `00_ORDEM_DE_EXECUCAO.ipynb` e rode os notebooks na ordem indicada. Cada
notebook mostra seus resultados e grava em `outputs/` os artefatos necessários
para a próxima etapa.

O tuning e o teste final podem levar aproximadamente 40–50 horas, dependendo
do computador. Os rankings de tuning são gravados
incrementalmente; se a execução for interrompida, rode novamente o notebook
para continuar sem repetir candidatos concluídos.

Atalho opcional para executar tudo:

```bash
source .venv/bin/activate
python analyses/grupo2/run_pipeline_v2.py
```

Resultados principais:

- `DOCUMENTACAO_BASE2.md` — contrato da base (estilo ouro/Jena);
- `CHECKLIST_BASE2.md` — checklist técnico;
- `outputs/PLS_technical_summary.md` — PLS conceitual + interpretação;
- `outputs/relatorio_base2.html` — relatório paginado (abrir no navegador → PDF);
- `outputs/results/mae_consolidado.csv`;
- `outputs/results/predictions_<MODELO>.csv`;
- `outputs/figures/`.

Leia também `DIAGNOSTICO_RESULTADOS_ANTIGOS.md` para entender por que a versão
anterior era muito mais rápida e por que seus números não devem ser usados como
resultado final.
