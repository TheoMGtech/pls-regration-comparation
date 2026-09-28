# Documentação da Base Jena Climate

## 1. Identificação da base

- **Nome do arquivo:** `jena_climate_2009_2016.csv`
- **Tipo:** arquivo CSV de observações meteorológicas em série temporal
- **Base utilizada neste trabalho:** arquivo anexado à atividade
- **Tema:** condições atmosféricas observadas em uma estação meteorológica próxima a Jena, na Alemanha
- **Período encontrado no arquivo:** de `01/01/2009 00:10` a `09/01/2012 08:10`
- **Frequência original:** uma observação a cada 10 minutos
- **Granularidade utilizada na modelagem:** horária
- **Modelo específico do grupo:** PLS Regression

> Apesar do nome do arquivo mencionar `2009_2016`, o arquivo efetivamente recebido nesta atividade termina em janeiro de 2012. A documentação e os resultados devem considerar o conteúdo real do arquivo, e não apenas o nome.

## 2. Objetivo da utilização

A base foi utilizada para construir uma série temporal horária de temperatura e comparar quatro modelos de previsão:

1. SARIMAX com variáveis externas;
2. Holt-Winters como modelo univariado;
3. Random Forest Regressor;
4. PLS Regression, modelo específico do Grupo 5.

A variável-alvo escolhida foi:

- **`T (degC)`** — temperatura do ar, em graus Celsius.

O horizonte de previsão foi definido como **uma hora à frente**. Assim, para uma origem no instante `t`, o objetivo é prever a temperatura no instante `t + 1 hora`.

## 3. Estrutura original do arquivo

O arquivo possui 15 colunas: uma coluna temporal e 14 variáveis meteorológicas numéricas.

| Coluna | Descrição | Unidade | Papel no trabalho |
|---|---|---:|---|
| `Date Time` | Data e horário da observação | data/hora | Índice temporal |
| `p (mbar)` | Pressão atmosférica | mbar | Variável externa |
| `T (degC)` | Temperatura do ar | °C | **Variável-alvo** |
| `Tpot (K)` | Temperatura potencial | K | Variável externa |
| `Tdew (degC)` | Temperatura do ponto de orvalho | °C | Variável externa |
| `rh (%)` | Umidade relativa | % | Variável externa |
| `VPmax (mbar)` | Pressão de vapor máxima | mbar | Variável externa |
| `VPact (mbar)` | Pressão de vapor atual | mbar | Variável externa |
| `VPdef (mbar)` | Déficit de pressão de vapor | mbar | Variável externa |
| `sh (g/kg)` | Umidade específica | g/kg | Variável externa |
| `H2OC (mmol/mol)` | Concentração de vapor de água | mmol/mol | Variável externa |
| `rho (g/m**3)` | Densidade do ar | g/m³ | Variável externa |
| `wv (m/s)` | Velocidade média do vento | m/s | Variável externa |
| `max. wv (m/s)` | Velocidade máxima do vento no intervalo | m/s | Variável externa |
| `wd (deg)` | Direção do vento | graus | Variável externa |

## 4. Descrição das variáveis

### 4.1 Variável temporal

### `Date Time`

Identifica o instante de cada medição. Essa coluna foi convertida para o tipo `datetime` e utilizada como índice da série temporal.

A ordenação temporal é obrigatória para:

- agregar os dados por hora;
- fazer a divisão treino-teste;
- calcular defasagens (*lags*);
- executar o walk-forward;
- evitar vazamento de informação do futuro para o passado.

### 4.2 Pressão atmosférica

### `p (mbar)`

Representa a pressão atmosférica medida em milibares. A pressão pode apresentar relação com mudanças nas condições meteorológicas e, consequentemente, com a temperatura.

### 4.3 Temperatura do ar

### `T (degC)`

Representa a temperatura do ar em graus Celsius. Foi escolhida como variável-alvo porque possui comportamento temporal claro, incluindo ciclos diários e variação sazonal.

### 4.4 Temperatura potencial

### `Tpot (K)`

Temperatura que representa a condição térmica do ar ajustada para uma referência de pressão. É uma variável meteorológica derivada e foi considerada como variável externa.

### 4.5 Temperatura de ponto de orvalho

### `Tdew (degC)`

Indica a temperatura na qual o ar precisaria ser resfriado para atingir saturação. É relacionada à quantidade de vapor de água presente na atmosfera.

### 4.6 Umidade relativa

### `rh (%)`

Representa o percentual de umidade do ar em relação à quantidade máxima de vapor que ele poderia conter na temperatura observada.

### 4.7 Pressões de vapor

- **`VPmax (mbar)`**: pressão de vapor máxima possível nas condições de temperatura observadas;
- **`VPact (mbar)`**: pressão de vapor atual;
- **`VPdef (mbar)`**: déficit entre a pressão máxima e a pressão atual.

Essas variáveis possuem relação física entre si. Portanto, apresentam potencial de multicolinearidade, aspecto relevante para o PLS Regression.

### 4.8 Umidade específica e concentração de vapor

- **`sh (g/kg)`**: quantidade de vapor de água por massa de ar;
- **`H2OC (mmol/mol)`**: concentração de vapor de água em relação à quantidade de ar.

Essas variáveis também podem apresentar correlação entre si e com `rh (%)`, `Tdew (degC)` e `VPact (mbar)`.

### 4.9 Densidade do ar

### `rho (g/m**3)`

Representa a massa de ar por unidade de volume. Pode variar conforme pressão, temperatura e composição da atmosfera.

### 4.10 Velocidade do vento

- **`wv (m/s)`**: velocidade média do vento;
- **`max. wv (m/s)`**: maior velocidade do vento no intervalo de observação.

Na agregação horária, `wv (m/s)` foi calculada pela média das observações dentro da hora. Já `max. wv (m/s)` foi calculada pelo máximo da hora, preservando a interpretação de velocidade máxima.

### 4.11 Direção do vento

### `wd (deg)`

Representa a direção do vento em graus. Essa variável é circular: 359° e 1° são direções próximas, embora a média aritmética simples resulte em 180°.

Por isso, a agregação foi feita por média circular:

1. conversão dos ângulos para radianos;
2. cálculo das médias de seno e cosseno;
3. recuperação do ângulo por `arctan2`;
4. conversão de volta para graus no intervalo `[0°, 360°)`.

Na engenharia de atributos, a direção também foi representada por seno e cosseno para evitar uma descontinuidade artificial entre 0° e 360°.

## 5. Diagnóstico do arquivo recebido

Os números abaixo foram calculados diretamente a partir do arquivo utilizado no notebook.

| Indicador | Resultado |
|---|---:|
| Linhas originais | 159.023 |
| Datas inválidas | 0 |
| Linhas após tratamento de duplicidades | 158.879 |
| Timestamps duplicados envolvidos | 288 |
| Linhas duplicadas agregadas | 144 |
| Frequência original inferida | 10 minutos |
| Observações esperadas por hora | 6 |
| Bins horários incompletos descartados | 2 |
| Linhas horárias completas | 26.479 |
| Intervalos irregulares identificados | 1 |
| Timestamps horários ausentes inseridos na regularização | 1 |
| Início da série horária | 01/01/2009 01:00 |
| Final da série horária | 09/01/2012 08:00 |

## 6. Tratamento dos dados

### 6.1 Datas

As datas foram convertidas com interpretação de formato dia/mês/ano. Não foram encontradas datas inválidas.

### 6.2 Duplicidades

Foram encontrados timestamps repetidos na base original. As duplicidades foram tratadas agrupando observações do mesmo instante:

- média para variáveis numéricas contínuas;
- média circular para `wd (deg)`.

Nenhuma observação foi removida arbitrariamente.

### 6.3 Agregação para a frequência horária

A fonte possui seis observações a cada hora. Foram mantidos apenas bins com as seis observações esperadas.

As regras foram:

- média para as variáveis meteorológicas contínuas;
- máximo para `max. wv (m/s)`;
- média circular para `wd (deg)`.

Dois bins incompletos foram descartados para não criar médias horárias baseadas em quantidade parcial de observações.

### 6.4 Regularização temporal

Depois da agregação, a série foi reindexada em uma sequência horária regular. Foi identificado um timestamp ausente.

Para as variáveis externas, o preenchimento foi feito por *forward fill*, carregando o último valor conhecido. Essa escolha é causal porque não utiliza valores futuros.

A variável-alvo não foi preenchida artificialmente. O único horário sem temperatura permaneceu como ausente e não entrou no conjunto supervisionado dos modelos.

### 6.5 Outliers

Outliers foram identificados por diagnóstico utilizando o critério do intervalo interquartil — IQR:

\[
IQR = Q_3 - Q_1
\]

Um valor foi marcado como potencial outlier quando ficou abaixo de `Q1 - 1,5 × IQR` ou acima de `Q3 + 1,5 × IQR`.

Os valores abaixo são apenas diagnósticos:

| Variável | Possíveis outliers |
|---|---:|
| `p (mbar)` | 584 |
| `T (degC)` | 45 |
| `Tpot (K)` | 74 |
| `Tdew (degC)` | 143 |
| `rh (%)` | 66 |
| `VPmax (mbar)` | 643 |
| `VPact (mbar)` | 45 |
| `VPdef (mbar)` | 2.040 |
| `sh (g/kg)` | 51 |
| `H2OC (mmol/mol)` | 48 |
| `rho (g/m**3)` | 194 |
| `wv (m/s)` | 916 |
| `max. wv (m/s)` | 649 |
| `wd (deg)` | 188 |

Nenhum ponto foi removido, winsorizado ou alterado automaticamente com base nesse diagnóstico. Em dados meteorológicos, extremos podem representar eventos reais; removê-los sem investigação poderia eliminar informação relevante.

## 7. Engenharia de atributos

Foram criadas features causais para os modelos Random Forest e PLS Regression.

### 7.1 Defasagens da temperatura

Foram utilizadas defasagens de:

```text
0, 1, 2, 3, 6, 12, 24, 48, 72 e 168 horas
```

Essas defasagens representam, por exemplo:

- condição atual;
- horas imediatamente anteriores;
- comparação com o mesmo horário do dia anterior (`24` horas);
- comparação com a mesma posição aproximada da semana anterior (`168` horas).

### 7.2 Estatísticas móveis

Foram calculadas médias e desvios-padrão móveis com janelas de:

```text
3, 6, 12, 24 e 168 horas
```

Todas as janelas foram deslocadas uma hora antes do cálculo. Assim, a feature da origem `t` não incorpora o valor que só seria observado depois da origem.

### 7.3 Defasagens das variáveis externas

As variáveis meteorológicas externas foram utilizadas com defasagens, e não como observações futuras. Isso representa o cenário em que somente o histórico observado está disponível no instante da previsão.

### 7.4 Variáveis de calendário

Foram criadas representações cíclicas para:

- hora do dia;
- dia da semana;
- dia do ano.

Essas variáveis são permitidas porque o calendário do instante futuro é conhecido antecipadamente.

## 8. Divisão entre treino e teste

A divisão foi feita cronologicamente:

- **80% iniciais:** desenvolvimento e seleção de hiperparâmetros;
- **20% finais:** teste final fora da amostra.

Não houve embaralhamento. Essa escolha é necessária em séries temporais porque embaralhar observações permitiria que informações do futuro influenciassem o treinamento.

O `random_state` utilizado nos modelos estocásticos foi:

```python
random_state = 42
```

## 9. Modelagem

### 9.1 SARIMAX

Modelo estatístico que combina componentes autorregressivos, médias móveis, diferenciação e sazonalidade. As variáveis externas foram deslocadas temporalmente para que somente informações disponíveis na origem fossem utilizadas.

### 9.2 Holt-Winters

Modelo univariado que representa nível, tendência e sazonalidade. Foi utilizado como referência clássica sem variáveis externas.

### 9.3 Random Forest

Conjunto de árvores de decisão treinadas com amostras e subconjuntos de atributos. O `random_state=42` garante reprodutibilidade do componente aleatório.

### 9.4 PLS Regression

O PLS cria componentes latentes supervisionados, buscando combinações das features que apresentem alta covariância com a temperatura futura. É adequado para este conjunto porque existem variáveis meteorológicas fisicamente relacionadas e, portanto, potencialmente colineares.

Foram avaliados:

- número de componentes latentes;
- escalonamento das variáveis;
- tolerância de convergência;
- número máximo de iterações.

A escolha do número de componentes foi feita usando validação temporal apenas no bloco de desenvolvimento.

## 10. Avaliação

A avaliação final utiliza:

- previsão walk-forward;
- horizonte de uma hora;
- mesmas origens para todos os modelos;
- MAE (*Mean Absolute Error*);
- análise do viés médio;
- desvio-padrão dos resíduos;
- ACF dos resíduos;
- teste de Ljung–Box.

O MAE é calculado por:

\[
MAE = \frac{1}{n}\sum_{t=1}^{n}|y_t - \hat{y}_t|
\]

Quanto menor o MAE, menor o erro absoluto médio da previsão.

## 11. Arquivos derivados

Os diagnósticos e resultados utilizados para esta documentação estão na pasta:

```text
resultados_grupo5_jena_horario/
```

Principais arquivos:

- `data_diagnostics.json` — diagnóstico da leitura e preparação;
- `variable_dictionary.csv` — dicionário das colunas;
- `feature_dictionary.csv` — dicionário das features;
- `stl_summary.json` — resumo da decomposição STL;
- `stl_components.csv` — componentes observado, tendência, sazonalidade e resíduo;
- `predictions_long.csv` — previsões e erros dos modelos;
- `model_comparison_mae.csv` — comparação de MAE;
- `pls_feature_importance.csv` — coeficientes, VIP e permutation importance do PLS;
- `random_forest_feature_importance.csv` — importância do Random Forest;
- `ljung_box_comparison.csv` — diagnóstico de autocorrelação dos resíduos.

## 12. Limitações

1. O arquivo recebido não cobre todo o período indicado no nome `2009_2016`; os dados disponíveis terminam em janeiro de 2012.
2. Somente uma das cinco bases previstas no enunciado foi disponibilizada nesta execução.
3. O horizonte avaliado foi de uma hora; os resultados não devem ser generalizados automaticamente para horizontes maiores.
4. As variáveis meteorológicas futuras não foram utilizadas diretamente. Em um sistema operacional, previsões meteorológicas externas poderiam ser incorporadas, mas isso constituiria outro experimento.
5. O critério IQR foi usado para diagnóstico, não para remoção automática de observações.
6. Importância de feature não implica causalidade física.
7. O desempenho dos modelos pode mudar em outra estação, período ou granularidade.

## 13. Conclusão

A Jena Climate é uma base adequada para estudar previsão de temperatura em série temporal porque contém uma sequência cronológica longa, observações regulares de variáveis atmosféricas e relações físicas entre os atributos.

A transformação para a granularidade horária reduz o ruído de alta frequência e torna explícitos os ciclos diários. A presença de variáveis correlacionadas justifica a avaliação do PLS Regression, enquanto a comparação com SARIMAX, Holt-Winters e Random Forest permite analisar diferentes famílias de modelos.

A documentação deve ser lida em conjunto com o notebook:

```text
trabalho_grupo5_pls_jena_horario.ipynb
```
