# Exploração final da base de ouro

## Cobertura e significado

A série bruta contém 12.009 registros entre 1º de abril de 1968 e 10 de abril de 2014. Desses, 11.641 possuem preço válido e 368 possuem `GOLD_PRICE` ausente. Depois das exigências causais de alvo, lags, janelas móveis e variáveis externas disponíveis, restam 9.864 observações modeláveis.

O preço é expresso em USD por onça fina de ouro e corresponde ao fixing da tarde em Londres, identificado pelo código `BBEX3.D.XAU.USD.EA.AC.C05`. O arquivo local coincide com as 12.009 datas e valores do CSV de referência.

## Frequência e qualidade temporal

A frequência observada é de dias de mercado, não uma grade diária civil perfeitamente regular. Não há datas duplicadas na base bruta nem na base modelável. Na base modelável, o maior intervalo entre observações é de 20 dias e existem 401 intervalos superiores a três dias. Esses intervalos refletem o calendário de mercado, feriados e a exclusão causal de linhas incompletas; não foram preenchidos artificialmente.

## Valores ausentes

Os 368 preços ausentes permanecem ausentes no arquivo bruto. O pipeline não interpola, não aplica forward fill e não aplica backfill ao preço do ouro. As linhas sem preço não entram na base modelável. O forward fill é aplicado somente às variáveis externas e antes da defasagem de uma observação.

## Valores atípicos

A auditoria descritiva sinalizou 1.416 observações extremas pelo IQR aplicado ao nível do preço e 480 retornos extremos pelo MAD. O número elevado de extremos no nível é coerente com uma série longa e não estacionária, com diferentes regimes de preço; por isso, o IQR no nível não deve ser tratado como detector automático de erro.

Entre os maiores movimentos diários observados estão 9 de janeiro de 1980 (+26,18%), 7 de setembro de 1982 (+17,01%), 5 de junho de 1973 (+15,72%) e 24 de janeiro de 1980 (-15,54%). Também aparecem movimentos expressivos em 2006, 2008 e 2011. Esses pontos são plausíveis como movimentos reais de mercado e não apresentam, isoladamente, evidência concreta de erro de digitação. Nenhum outlier foi removido ou winsorizado.

Os dados detalhados estão em `exploratory_summary.csv`, `missing_values_audit.csv`, `data_quality_audit.csv` e `outlier_candidates.csv`.
