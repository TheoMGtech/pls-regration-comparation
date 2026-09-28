# Spec 004 - Modelagem da base de ouro em notebooks

## Objetivo

Executar, exclusivamente nos notebooks já existentes em `analyses/grupo5/`, a análise causal e a comparação de SARIMAX, Holt-Winters, Random Forest e PLS Regression na base congelada de ouro. Relatórios HTML/PDF e o notebook `05_relatorio/` não pertencem a esta spec.

## Contrato experimental

- A base oficial é `bases/grupo5/gold_daily_modeling.csv`; ela não pode ser editada manualmente.
- Uma linha na origem `t` prevê `TARGET`, o preço da próxima observação de mercado. O horizonte é uma observação.
- O protocolo usa split cronológico 70/15/15 e origens expansivas a cada cinco observações. Todos os modelos usam as mesmas origens.
- Tuning usa apenas treino e validação. Após os quatro vencedores serem congelados e receberem aprovação humana explícita, `02_walkforward_validacao.ipynb` executa exclusivamente o teste final, sem reabrir decisões de tuning, features ou sazonalidade.
- Random Forest e PLS usam a mesma matriz causal aprovada; PLS ajusta o escalonador em cada janela de treino. Holt-Winters é univariado. SARIMAX usa somente externas e calendário disponíveis na origem.
- Fonte/unidade, limpeza/outliers, features, período sazonal, grades e aceite de candidatos são decisões humanas registradas em `outputs/`.
- A validação e o teste têm 296 origens distintas cada. As datas de origem, datas-alvo e horizonte ficam congelados em `origin_manifest.csv`.
- SARIMAX faz 72 ajustes de triagem no treino: 18 ordens `(p,d,q)` e as estruturas `(0,0,0,5)`, `(1,0,0,5)`, `(0,0,1,5)` e `(0,1,0,5)`. Os cinco menores BIC seguem para MAE walk-forward; BIC não escolhe o vencedor.
- Holt-Winters compara 15 estruturas válidas, incluindo ausência de sazonalidade. Quando sazonal, usa `seasonal_periods=5`; os parâmetros de suavização são estimados internamente em cada janela.
- Random Forest usa 12 combinações dirigidas e predefinidas, com `random_state=42`. PLS testa de 1 a 12 componentes, limitado automaticamente por features e observações.
- O ranking usa: MAE de validação walk-forward; empate no MAE arredondado a três casas resolvido pela menor complexidade; persistindo, menor tempo médio por origem. Esse critério é congelado antes da execução.

## Critérios de aceitação

1. Os 24 notebooks fora de `05_relatorio/` têm conteúdo executável e produzem a evidência definida em `docs/requisitos.md`.
2. `outputs/protocol.json` registra hash da base, seed, versões, horizonte, splits, origens, features, grades, critério de seleção e decisões; notebooks posteriores exigem a versão 2.
3. O projeto persiste previsões, MAE, hiperparâmetros, importância e Ljung-Box em esquemas comuns, sem inventar resultados antes das decisões humanas.
4. Gates impedem tuning sem decisões de dados e mantêm o teste final indisponível até o congelamento dos quatro vencedores e uma nova aprovação explícita.
5. As validações demonstram ausência de dados futuros, sobreposição temporal e previsões não finitas.
