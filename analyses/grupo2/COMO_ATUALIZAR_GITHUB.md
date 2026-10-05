# Como atualizar o que já subiu no GitHub

Você já tem a branch `feat/grupo2-base2-bruna`. Agora a estrutura mudou:
- **saiu** `pipelines/grupo2/`
- **entrou** tudo em `analyses/grupo2/` (código + `outputs/`)

## No PC que consegue dar push

```bash
cd pls-regration-comparation
git checkout feat/grupo2-base2-bruna
git pull origin feat/grupo2-base2-bruna

# copie/substitua a pasta analyses/grupo2 pela versão nova deste PC
# (ou copie o zip atualizado)

# remove a pasta antiga se ainda existir
git rm -r pipelines 2>/dev/null || rm -rf pipelines

git add analyses/grupo2 .gitignore
git status
git commit -m "refactor(grupo2): motor e outputs dentro de analyses/grupo2"
git push origin feat/grupo2-base2-bruna
```

Depois abra/atualize o PR:  
https://github.com/TheoMGtech/pls-regration-comparation/compare/main...feat/grupo2-base2-bruna?expand=1
