# Base 3 — Aotizhongxin Air Quality

## Identificação

- Arquivo original: `bases/grupo3/PRSA_Data_Aotizhongxin_20130301-20170228.csv`
- Estação: Aotizhongxin
- Cobertura do arquivo: 2013-03-01 00:00 a 2017-02-28 23:00
- Frequência: horária
- Observações: 35.064
- Calendário: completo, sem timestamps ausentes ou duplicados
- Alvo: `PM2.5`
- Horizonte: 1 hora à frente
- Unidade do alvo: µg/m³

## Limpeza

- `DATETIME` foi construído a partir de `year`, `month`, `day` e `hour`.
- A série foi ordenada cronologicamente.
- Não foram criados timestamps sintéticos porque o calendário original já é regular.
- Não foram removidas linhas por outliers nesta etapa; valores extremos devem ser investigados e documentados na EDA antes de qualquer decisão de tratamento.
- `PM2.5` não é imputado, pois é a variável-alvo.
- Variáveis externas observadas com lacunas recebem apenas preenchimento para frente (`ffill`), nunca preenchimento para trás. Assim, uma observação futura não é usada para preencher o passado.

## Disponibilidade temporal

As variáveis externas são utilizadas somente com defasagens de 1 e 24 horas. Portanto, na origem `t`, cada valor externo utilizado foi observado antes da origem. As variáveis externas são:

- PM10
- SO2
- NO2
- CO
- O3
- TEMP
- PRES
- DEWP
- RAIN
- WSPM

`wd` é convertido em seno/cosseno de direção do vento e também usado com defasagem de uma hora.

## Feature Engineering

### Calendário

- `HOUR_SIN`, `HOUR_COS`
- `DOW_SIN`, `DOW_COS`
- `MONTH_SIN`, `MONTH_COS`

### Histórico do alvo

- lags: 1, 3, 6, 24 e 168 horas
- médias móveis: 3, 6, 24 e 168 horas
- desvios-padrão móveis: 3, 6, 24 e 168 horas

Todas as janelas móveis terminam em `t-1`.

### Externas

Cada variável externa numérica possui `LAG_1` e `LAG_24`.

## Valores ausentes

As lacunas produzidas por lags e janelas são preservadas no dataset preparado. Elas não devem ser preenchidas com informação futura. O tratamento final para treinamento deve ser feito dentro do pipeline de cada modelo, ajustado somente com a janela de treinamento de cada origem walk-forward.
