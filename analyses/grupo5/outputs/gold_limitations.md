# Limitações da base e do experimento de ouro

- O período histórico termina em abril de 2014; os resultados não representam automaticamente regimes posteriores.
- Foram usadas somente duas variáveis externas: Treasury de 10 anos e Federal Funds Rate.
- A frequência é de dias de mercado e contém intervalos irregulares.
- A série bruta possui 368 preços ausentes. Eles não foram imputados e as linhas correspondentes não entram na base modelável.
- O horizonte é de apenas uma observação real de mercado; não há evidência sobre horizontes mais longos.
- As origens de validação e teste avançam em passos de cinco observações, e não cobrem cada linha consecutiva.
- Holt-Winters, SARIMAX e PLS apresentaram diferenças pequenas de MAE; a ordem observada pode ser sensível ao período avaliado.
- O baseline de persistência é muito competitivo, o que reduz o ganho incremental dos modelos mais complexos.
- A STL não encontrou sazonalidade forte nos períodos 5, 20 e 252.
- O PLS selecionou 11 dos 12 componentes possíveis, oferecendo pouca redução dimensional efetiva.
- Random Forest não extrapola naturalmente fora da faixa de alvos vista no treino; em 18 origens o valor real ficou acima do máximo de treino.
- Mudanças de regime podem alterar relações entre preço, lags e variáveis externas. Os resultados não devem ser generalizados automaticamente para outros períodos, ativos ou condições macroeconômicas.
