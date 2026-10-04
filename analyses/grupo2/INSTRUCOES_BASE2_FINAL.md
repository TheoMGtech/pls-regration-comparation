# Base 2 — instruções finais (substituir zip + GitHub + como rodar)

**Responsável:** Bruna Carvalho Cardoso  
**Zip:** `Documents/grupo2.zip`  
**Branch:** `feat/grupo2-base2-bruna`  
**Repo:** https://github.com/TheoMGtech/pls-regration-comparation

---

## 1. O que esse zip tem

- `grupo2/` — somente notebooks e código de análise; os `outputs/` serão gerados

A base não foi alterada e não está duplicada no ZIP. A pasta `grupo2/` deve
ficar dentro de `analyses/`, seguindo a organização do Theo.

---

## 2. No outro PC — apagar e substituir

Na **raiz** do repositório (onde estão `analyses/`, `bases/`, `README.md`):

### Apagar o que é antigo / errado

```bash
# pasta pipelines NÃO é padrão do grupo — remover se existir
rm -rf pipelines

# substitui a Base 2 inteira pelo zip novo
rm -rf analyses/grupo2
```

**Não apague** `analyses/grupo1`, `grupo3`, `grupo4`, `grupo5`.

### Extrair o zip

```bash
# ajuste o caminho se o zip estiver em Downloads
unzip -o ~/Documents/grupo2.zip -d analyses
```

### Conferir

Deve existir:

```
analyses/grupo2/00_ORDEM_DE_EXECUCAO.ipynb
analyses/grupo2/01_dados/
analyses/grupo2/02_modelos/
analyses/grupo2/03_resultados/
analyses/grupo2/04_especialista_PLS/
analyses/grupo2/05_relatorio/
analyses/grupo2/run_pipeline_v2.py
bases/grupo2/Metro_Interstate_Traffic_Volume.csv
```

**Não** deve existir: `pipelines/`

---

## 3. Subir de novo no GitHub (atualizar a branch)

```bash
cd pls-regration-comparation

git checkout feat/grupo2-base2-bruna
git pull origin feat/grupo2-base2-bruna

git add -A analyses/grupo2
git add -u pipelines          # registra remoção, se ainda estiver no git

git status
git commit -m "refactor(grupo2): notebooks em cadeia com outputs em analyses/grupo2"
git push origin feat/grupo2-base2-bruna
```

### Abrir / atualizar o Pull Request

Se ainda **não** tem PR:

https://github.com/TheoMGtech/pls-regration-comparation/compare/main...feat/grupo2-base2-bruna?expand=1

- base: `main` (ou `develop`, se o grupo combinar)
- compare: `feat/grupo2-base2-bruna`
- título: `feat(grupo2): Base 2 tráfego — Bruna Cardoso`

---

## 4. Como rodar (na mão — recomendado)

1. Crie/ative o ambiente (uma vez):

```bash
cd pls-regration-comparation
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. No Jupyter/VS Code/Cursor, abra:

`analyses/grupo2/00_ORDEM_DE_EXECUCAO.ipynb`

3. Rode nesta ordem:

| Ordem | Notebook | O que grava |
|------:|----------|-------------|
| 1 | `01_dados/01_documentacao_bases.ipynb` | (documenta / inspeciona) |
| 2 | `01_dados/02_limpeza_preparacao.ipynb` | `outputs/data/clean_hourly.csv` |
| 3 | `01_dados/03_feature_engineering.ipynb` | `outputs/data/modeling_frame.csv` |
| 4 | `01_dados/04_analise_exploratoria.ipynb` | figuras EDA |
| 5 | `01_dados/05_STL_decomposicao.ipynb` | STL + `stl_summary.json` |
| 6 | `02_modelos/<MODELO>/01_otimizacao_...` | `best_params_<MODELO>.json` |
| 7 | `02_modelos/<MODELO>/02_walkforward_...` | `predictions_*.csv`, `metrics_*.json` |
| 8 | `02_modelos/<MODELO>/03_previsoes_...` | figuras previsão/resíduos |
| 9 | `03_resultados/01_MAE_consolidado.ipynb` | `mae_consolidado.csv` |
| 10 | demais `03_resultados/` + PLS + relatório | HTML etc. |

`<MODELO>` = `Holt_Winters`, `SARIMAX`, `Random_Forest`, `PLS_Regression`  
(pode fazer um modelo completo de cada vez)

Se faltar arquivo de etapa anterior, o notebook **avisa** o que rodar antes.

O tuning e o teste final agora fazem walk-forward real: reajustam o modelo em
cada origem e preveem uma hora. Random Forest, Holt-Winters e principalmente
SARIMAX podem levar aproximadamente 40–50 horas no total. Isso é esperado.
Os CSVs de tuning funcionam como
checkpoint: se parar, rode o mesmo notebook novamente para continuar.

### Atalho (opcional) — tudo no terminal

```bash
source .venv/bin/activate
python analyses/grupo2/run_pipeline_v2.py
```

---

## 5. Onde ver os resultados

```
analyses/grupo2/outputs/
├── data/          # série limpa + matriz de modelagem
├── figures/       # gráficos
├── results/       # MAE, previsões, params, importância
└── relatorio_base2.html
```

---

## 6. Problemas comuns

| Situação | O que fazer |
|----------|-------------|
| Ainda existe `pipelines/` | `rm -rf pipelines` e `git add -u pipelines` |
| Notebook não acha `config.py` | rode a partir de `analyses/grupo2/...` / kernel no projeto certo |
| `Permission denied` no push | peça acesso ao Theo ou use rede sem Zscaler |
| Commit sem os `results/` | confira se `.gitignore` não ignora `analyses/*/outputs/` (na versão nova isso já foi ajustado no zip) |
| Quer atualizar pelo zip | apague `analyses/grupo2`, extraia `grupo2.zip` em `analyses/`, commit |

---

## 7. Checklist rápido

- [ ] Apaguei `pipelines/` e `analyses/grupo2` antigo  
- [ ] Extraí o zip dentro de `analyses/`  
- [ ] Commit + push na branch `feat/grupo2-base2-bruna`  
- [ ] PR aberto/atualizado  
- [ ] Consigo abrir `00_ORDEM_DE_EXECUCAO.ipynb` e rodar a limpeza  

Pronto.
