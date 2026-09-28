# Síntese da decomposição STL

A STL foi estimada somente no trecho de treino. Foram comparados os períodos 5, 20 e 252, representando hipóteses de ciclo semanal de pregões, aproximadamente mensal e aproximadamente anual.

1. **Há tendência?** Sim. A força de tendência foi alta nos três ajustes: 0,9984 para período 5, 0,9907 para 20 e 0,9225 para 252.
2. **Como a tendência muda?** A série apresenta mudanças persistentes de nível e inclinação ao longo das décadas. O componente de tendência acompanha os regimes de valorização e correção, sem pressupor crescimento constante.
3. **Existe sazonalidade relevante?** Não foi identificada sazonalidade relevante. A força sazonal calculada foi 0,0 nos três períodos.
4. **O que mostram 5, 20 e 252?** Nenhum dos três horizontes produziu força sazonal mensurável. Ao aumentar o período, o desvio padrão do resíduo cresceu de 6,06 para 14,38 e 41,61, indicando que ciclos longos não forneceram uma decomposição sazonal mais convincente.
5. **Como se comporta o residual?** O resíduo concentra variações de curto prazo e choques que não são explicados pela tendência. Sua dispersão aumenta nos períodos sazonais maiores.
6. **Por que testar `m=5`?** Cinco pregões é uma hipótese econômica e operacional simples para um possível ciclo semanal de mercado. Mesmo com força sazonal fraca, ela permaneceu como hipótese previamente definida e testável nas grades de SARIMAX e Holt-Winters. Isso não equivale a afirmar que existe sazonalidade forte; apenas permite que a validação compare uma estrutura curta e parcimoniosa com alternativas sem sazonalidade.

Os valores numéricos estão em `stl_candidates.csv`; os componentes observado, tendência, sazonal e residual estão em `stl_period_5.png`, `stl_period_20.png` e `stl_period_252.png`.
