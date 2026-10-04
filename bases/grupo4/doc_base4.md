# Documentação da base - Grupo 4 (Jena Climate)

Este documento registra a documentação inicial da base usada pelo grupo para a comparação de modelos temporais. O foco principal é descrever a estrutura da série, a variável-alvo, os campos meteorológicos disponíveis e as decisões de uso previstas antes da modelagem final.

## Base e variável-alvo

| Item | Registro atual |
| --- | --- |
| Arquivo bruto | `bases/grupo4/jena_climate_2009_2016.csv` |
| Fonte | Estação meteorológica de Jena, Alemanha, mantida pelo Max Planck Institute for Biogeochemistry. O nome do arquivo também aparece em materiais didáticos do TensorFlow para séries temporais. |
| Descrição | Série temporal de observações meteorológicas registradas em intervalos de 10 minutos em uma estação próxima a Jena. |
| Período bruto observado | 01/01/2009 00:10:00 até 01/01/2017 00:00:00 |
| Frequência observada | 10 minutos |
| Granularidade adotada para modelagem | Horária |
| Variável-alvo | `T (degC)` |
| Unidade da variável-alvo | Graus Celsius (°C) |
| Observações brutas | 159.023 linhas |
| Duplicidades temporais observadas | Sim; foram tratadas por média por instante |
| Dados ausentes no conjunto bruto | Não há datas inválidas; há ausência temporal pontual em séries agregadas e valores truncados em bins incompletos |

## Objetivo do uso

A base foi usada para construir uma série temporal horária de temperatura e comparar diferentes modelos de previsão, incluindo:

- SARIMAX com variáveis externas;
- Holt-Winters univariado;
- Random Forest Regressor;
- PLS Regression.

A variável alvo escolhida foi `T (degC)`, e o horizonte de previsão foi definido como 1 hora à frente. Em outras palavras, o problema é prever a temperatura no instante `t + 1 hora` usando informações disponíveis até `t`.

## Estrutura original do arquivo

O conjunto contém 15 colunas: uma temporal e 14 variáveis meteorológicas numéricas.

| Coluna | Descrição | Unidade | Papel principal |
| --- | --- | ---: | --- |
| `Date Time` | Data e hora da observação | data/hora | Índice temporal |
| `p (mbar)` | Pressão atmosférica | mbar | Variável externa |
| `T (degC)` | Temperatura do ar | °C | Variável-alvo |
| `Tpot (K)` | Temperatura potencial | K | Variável externa |
| `Tdew (degC)` | Temperatura do ponto de orvalho | °C | Variável externa |
| `rh (%)` | Umidade relativa | % | Variável externa |
| `VPmax (mbar)` | Pressão de vapor máxima possível | mbar | Variável externa |
| `VPact (mbar)` | Pressão de vapor atual | mbar | Variável externa |
| `VPdef (mbar)` | Déficit de pressão de vapor | mbar | Variável externa |
| `sh (g/kg)` | Umidade específica | g/kg | Variável externa |
| `H2OC (mmol/mol)` | Concentração de vapor de água | mmol/mol | Variável externa |
| `rho (g/m**3)` | Densidade do ar | g/m³ | Variável externa |
| `wv (m/s)` | Velocidade média do vento | m/s | Variável externa |
| `max. wv (m/s)` | Velocidade máxima do vento | m/s | Variável externa |
| `wd (deg)` | Direção do vento | graus | Variável externa |

## Descrição das variáveis

### `Date Time`

Identifica o instante de cada medição. Essa coluna deve ser convertida para datetime e utilizada como índice temporal. A ordenação correta é essencial para:

- agregação por hora;
- divisão treino/teste temporal;
- cálculo de defasagens e janelas móveis;
- aplicação de walk-forward;
- prevenção de vazamento temporal.

### `T (degC)`

Temperatura do ar em graus Celsius. Foi escolhida como variável-alvo porque apresenta comportamento temporal bem definido, com ciclos diários, tendência e variação sazonal.

### `p (mbar)`

Pressão atmosférica medida em milibares. Está diretamente relacionada às condições físicas do ar e pode influenciar a temperatura.

### `Tpot (K)`

Temperatura potencial ajustada para uma referência de pressão. É uma variável derivada com alto potencial de explicação atmosférica.

### `Tdew (degC)`

Temperatura de orvalho, ou seja, a temperatura na qual o ar ficaria saturado se resfriado. Está associada à umidade do ar.

### `rh (%)`

Umidade relativa do ar em percentual, comparando o vapor atual com o máximo possível nas condições observadas.

### `VPmax`, `VPact` e `VPdef`

- `VPmax (mbar)`: pressão máxima de vapor possível;
- `VPact (mbar)`: pressão de vapor atual;
- `VPdef (mbar)`: déficit de vapor.

Essas variáveis são fisicamente relacionadas e podem ter alta colinearidade, o que é relevante para modelos como PLS.

### `sh (g/kg)` e `H2OC (mmol/mol)`

Indicadores de quantidade de vapor de água no ar. Estão relacionados a umidade e temperatura e podem reforçar a previsão da temperatura.

### `rho (g/m**3)`

Densidade do ar. Pode variar em função de temperatura, pressão e composição atmosférica.

### `wv (m/s)` e `max. wv (m/s)`

Velocidade do vento média e máxima no intervalo de coleta. Pode impactar trocas térmicas e dissipação de calor.

### `wd (deg)`

Direção do vento em graus. Como é uma variável circular, o tratamento adequado exige representações cíclicas (seno/cosseno) em vez de média aritmética simples.

## Diagnóstico do arquivo recebido

Os valores abaixo refletem o diagnóstico realizado sobre o arquivo efetivamente recebido.

| Indicador | Resultado |
| --- | ---: |
| Linhas originais | 159.023 |
| Datas inválidas | 0 |
| Linhas após remoção de duplicidades | 158.879 |
| Timestamps duplicados envolvidos | 288 |
| Linhas duplicadas agregadas | 144 |
| Frequência original inferida | 10 minutos |
| Observações esperadas por hora | 6 |
| Bins horários incompletos descartados | 2 |
| Linhas horárias completas | 26.479 |
| Intervalos irregulares identificados | 1 |
| Timestamps horários ausentes inseridos | 1 |
| Início da série horária | 01/01/2009 01:00 |
| Final da série horária | 09/01/2012 08:00 |

## Tratamento dos dados

### Datas e ordenação

As datas foram convertidas para o tipo datetime e ordenadas cronologicamente. Não foram encontradas datas inválidas.

### Duplicidades

Foram encontrados timestamps repetidos. A regra adotada foi:

- média para variáveis numéricas contínuas;
- média circular para `wd (deg)`.

Nenhuma observação foi apagada ad hoc; a duplicidade foi tratada por agregação.

### Agregação para frequência horária

A base original possui seis medições por hora. Foram mantidos apenas os bins com as seis observações esperadas. Para os bins incompletos, houve descarte para evitar médias horárias baseadas em parte de um período.

A agregação horária foi feita com:

- média para as variáveis contínuas;
- máximo para `max. wv (m/s)`;
- média circular para `wd (deg)`.

### Regularização temporal

Depois da agregação, a série foi reindexada em uma sequência horária regular. Foi identificado um horário ausente, que foi preenchido de forma causal usando `forward fill` nas variáveis externas. Essa estratégia evita vazamento de informação futura.

A variável-alvo `T (degC)` não foi preenchida artificialmente; o instante ausente foi tratado como ausente e não incorporado ao conjunto supervisionado dos modelos.

## Engenharia de atributos

Foram criadas features causais para modelos de árvore e PLS, sempre respeitando o histórico disponível em cada instante.

### Defasagens da temperatura

Defasagens utilizadas:

- 0, 1, 2, 3, 6, 12, 24, 48, 72 e 168 horas

Essas defasagens capturam:

- condição atual;
- comportamento recente;
- comparação com a mesma hora do dia anterior;
- comparação com o mesmo ponto da semana anterior.

### Estatísticas móveis

Foram calculadas médias e desvios-padrão móveis com janelas de:

- 3, 6, 12, 24 e 168 horas

O cálculo foi efetuado com a janela deslocada para frente, preservando causalidade.

### Defasagens das variáveis externas

As variáveis meteorológicas externas foram conduzidas com defasagens temporais para garantir que apenas informação disponível até a origem da previsão fosse empregada.

### Variáveis de calendário

Também foram geradas representações cíclicas para:

- hora do dia;
- dia da semana;
- dia do ano.

Essas variáveis são conhecidas antecipadamente e, portanto, apropriadas para a previsão.

## Divisão treino/teste

A divisão foi feita cronologicamente:

- 80% iniciais: desenvolvimento e seleção de hiperparâmetros;
- 20% finais: teste final fora da amostra.

Não foi realizado embaralhamento. Em séries temporais, essa escolha é necessária para evitar que o futuro influencie o treino.

## Observações gerais sobre qualidade e uso

- O conjunto é adequado para modelagem temporal por conter observações regulares, alta resolução e múltiplas variáveis físicas correlacionadas.
- Há forte potencial de multicolinearidade entre as variáveis meteorológicas, o que torna o PLS uma abordagem especialmente interessante.
- O diagnóstico de outliers foi realizado, mas não houve remoção automática; valores extremos podem representar eventos reais e relevantes do clima.