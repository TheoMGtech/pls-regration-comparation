# Documentação da Base 2 — Metro Interstate Traffic Volume

**Etapa:** contrato temporal da base  
**Responsável:** Bruna Carvalho Cardoso  
**Grupo 5 (especialização PLS Regression)** — pasta `analyses/grupo2` no repositório  
**Entrada:** CSV congelado em `bases/grupo2/Metro_Interstate_Traffic_Volume.csv`  
**Resultado:** dicionário de variáveis, disponibilidade temporal, limpeza e protocolo 80/20

Este texto segue o mesmo formato da documentação da base de ouro (Theo) e da base Jena: fonte, unidade, qualidade, disponibilidade das externas e decisões congeladas **antes** da modelagem.

---

## 1. Identificação da base

| Item | Valor |
|---|---|
| Nome do arquivo | `Metro_Interstate_Traffic_Volume.csv` |
| Fonte | UCI Machine Learning Repository — Metro Interstate Traffic Volume (MN Department of Transportation + Weather Underground) |
| Tema | Volume horário de veículos na I-94, sentido oeste, em Minneapolis–Saint Paul |
| Alvo | `traffic_volume` (contagem de veículos por hora) |
| Unidade do alvo | veículos / hora |
| Período bruto | 2012-10-02 09:00 → 2018-09-30 23:00 |
| Frequência original | horária, com duplicatas de timestamp e lacunas |
| Granularidade de modelagem | 1 hora |
| Horizonte | 1 hora à frente |
| Origem da previsão | último instante conhecido `t`; prever `t+1h` |
| `random_state` | 67 |
| Split externo | 80% desenvolvimento / 20% teste, **cronológico** |
| Split interno dos 80% | 70% treino + 10% validação (do total) |

O arquivo efetivamente usado é o CSV congelado do repositório. Fonte, período e unidade abaixo descrevem esse arquivo, não um recorte posterior encontrado em sites.

---

## 2. Objetivo da utilização

Comparar quatro modelos na mesma série, com as mesmas origens e o mesmo horizonte:

1. SARIMAX com variáveis externas causalmente válidas;
2. Holt-Winters como referência **univariada** (sem externas);
3. Random Forest;
4. PLS Regression (modelo de especialização do Grupo 5).

Random Forest e PLS compartilham o mesmo conjunto tabular de features, para que a comparação não seja determinada por matrizes diferentes.

---

## 3. Estrutura original do arquivo

O CSV bruto tem **48.204** linhas e 9 colunas.

| Coluna | Descrição | Unidade | Papel |
|---|---|---|---|
| `date_time` | Instante da medição | data/hora | Índice temporal |
| `traffic_volume` | Volume de tráfego na hora | veículos/h | **Alvo** |
| `holiday` | Nome do feriado (vazio se não for feriado) | texto | Externa de calendário |
| `temp` | Temperatura | kelvin | Externa meteorológica |
| `rain_1h` | Chuva na hora | mm | Externa meteorológica |
| `snow_1h` | Neve na hora | mm | Externa meteorológica |
| `clouds_all` | Cobertura de nuvens | % | Externa meteorológica |
| `weather_main` | Classe meteorológica | texto | Descritiva; não entra no modelo |
| `weather_description` | Descrição mais fina do clima | texto | Descritiva; não entra no modelo |

---

## 4. Dicionário e disponibilidade temporal

O enunciado exige declarar, para cada externa, se ela estaria disponível no momento real da previsão. Valores futuros observados **não** entram.

| Variável | Disponível em `t` para prever `t+1`? | Uso no trabalho |
|---|---|---|
| Hora, dia da semana, mês, fim de semana | Sim — calendário conhecido | seno/cosseno e dummies |
| Feriado | Sim — calendário conhecido | `is_holiday` no dia inteiro |
| `temp`, `rain_1h`, `snow_1h`, `clouds_all` **observados em t+1** | Não — vazamento | **proibido** |
| Clima **já observado até t** | Sim | `temp_lag_1`, `rain_lag_1`, `snow_lag_1`, `clouds_lag_1` |
| Previsão meteorológica oficial na origem | Não estava no arquivo | não utilizada |
| Volume futuro | Não | nunca usado como feature |

`weather_main` / `weather_description` foram excluídos da matriz: são categorias redundantes com o clima numérico e aumentariam cardinalidade sem ganho claro de disponibilidade.

---

## 5. Qualidade dos dados e decisões de limpeza

Auditoria no CSV congelado:

- **48.204** registros brutos;
- **40.575** timestamps únicos → **7.629** duplicatas de `date_time` (várias descrições de clima na mesma hora);
- maior lacuna: **7.387 horas** (~10 meses);
- nulos nominais no CSV: a coluna `holiday` vem vazia na maior parte das horas; isso **não** é ausência de tráfego.

Decisões congeladas:

1. Deduplicar timestamp (uma linha por hora).
2. **Não interpolar** a lacuna de 10 meses. O segmento modelado começa **depois** da maior lacuna: 2015-06-11 20:00 → 2018-09-30 23:00.
3. Regularizar a grade horária nesse segmento (28.972 horas).
4. Horas faltantes **dentro** do segmento (2.295): imputação **causal** do alvo — lag 168h, depois lag 24h, depois forward-fill. Nenhuma imputação usa futuro.
5. Flag `target_observed`: o MAE oficial usa somente horas originalmente observadas (26.677 no segmento).
6. Feriado informado só à meia-noite no bruto: o nome é expandido para **todas as horas daquele dia**.

Essas decisões correspondem ao `cleaning_report.json` da execução congelada.

---

## 6. Feature engineering

As mesmas features tabulares alimentam Random Forest e o conjunto `full` do PLS.

- lags do alvo: 1, 2, 3, 6, 12, 23, 24, 25, 48, 72, 167, 168, 169, 336 horas;
- janelas móveis deslocadas (`shift` antes de `rolling`): média e desvio 6h, 24h e 168h;
- calendário cíclico: hora, dia da semana, mês;
- `is_weekend`, `is_holiday`;
- clima defasado em 1 hora;
- flags `observed_lag_*` indicando se o lag correspondente era observação real.

NaN introduzido por lags/janelas: as primeiras horas da série são descartadas até a janela de 336h estar preenchida. Restam **28.636** linhas no frame de modelagem.

O PLS ainda testa três conjuntos (`full`, `no_weather`, `compact`) **só na validação**. O vencedor congelado foi `no_weather` com 15 componentes: o clima defasado não melhorou o MAE de validação nesta base.

---

## 7. Protocolo walk-forward

- Split cronológico 80/20; teste intocado até o final.
- Dentro dos 80%: treino interno + validação walk-forward (passo 11h, coprimo de 24, para cobrir todas as horas do dia).
- Em **cada origem**: reajuste com informação ≤ origem; horizonte **1 hora**.
- 258 origens de validação e **521 origens de teste**, idênticas nos quatro modelos.
- Hiperparâmetros escolhidos pelo menor MAE de validação e **congelados** no teste.
- Holt-Winters: se não converge ou gera previsão fora do intervalo causal plausível, usa o lag semanal 168h (salvaguarda numérica documentada).

---

## 8. Artefatos

- `outputs/data/cleaning_report.json`, `clean_hourly.csv`, `modeling_frame.csv`, `split_info.json`
- `outputs/results/protocol.json`, `stl_summary.json`
- `outputs/figures/01_serie_alvo.png`, `02_externas.png`, `03_perfil_horario.png`, `04_stl.png`
