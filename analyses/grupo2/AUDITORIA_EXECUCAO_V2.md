# Auditoria da execução recebida em 01/10/2026

Esta auditoria usa os artefatos do arquivo executado `grupo2 1.zip`. Os
resultados abaixo pertencem ao protocolo v2 e não devem ser misturados com os
outputs da versão antiga.

## Integridade da execução

- Os 25 notebooks com código foram executados integralmente e sem exceções.
- Os quatro modelos possuem exatamente 229 previsões.
- Timestamps, índices de origem e `y_true` são idênticos entre os modelos.
- Todas as 229 observações pontuadas são alvos originalmente observados.
- Granularidade de 1 hora, `random_state=67` e corte cronológico 80/20 foram
  preservados.
- Cada origem reajusta o modelo e prevê somente a próxima hora.

## Resultado do teste final

1. Random Forest: MAE 155,04; RMSE 228,98; WAPE 4,53%.
2. PLS Regression: MAE 177,28; RMSE 274,26; WAPE 5,18%.
3. SARIMAX: MAE 266,24; RMSE 394,34; WAPE 7,77%.
4. Holt-Winters: MAE 314,23; RMSE 2.305,39; WAPE 9,18%.

Baselines nas mesmas origens:

- sazonal semanal (168h): MAE 301,01;
- sazonal diária (24h): MAE 554,84;
- persistência (1h): MAE 595,20.

Random Forest, PLS e SARIMAX superaram a melhor baseline. O MAE bruto não pode
ser comparado ao MAE do ouro do Grupo 5, pois as escalas são diferentes.

## Problema numérico encontrado no Holt-Winters

O Holt-Winters teve mediana do erro absoluto de apenas 114,59, mas uma única
previsão numericamente instável em 07/04/2018 às 20h foi 37.763,73 para um alvo
de 3.079. Esse erro de 34.684,73 elevou sozinho o MAE de aproximadamente 163
para 314 e tornou o RMSE pouco representativo.

Isso não é evidência de baixa qualidade geral do modelo; é uma falha numérica
do ajuste naquela origem. A versão seguinte aplica uma proteção causal:
previsões não finitas, negativas ou muito acima do máximo histórico da janela
são substituídas pela previsão sazonal semanal disponível na origem. O uso da
proteção é registrado em cada previsão e nas métricas.

## Tuning e tempo

A execução não foi instantânea:

- Random Forest final: 1.182 s (19,7 min);
- SARIMAX final: 9.384 s (2h36);
- SARIMAX realizou ainda 72 ajustes de triagem BIC e quatro candidatos
  walk-forward;
- o tuning de Random Forest levou aproximadamente 37 minutos.

Entretanto, a seleção usou apenas 30 origens para PLS/RF/Holt-Winters e 15 para
SARIMAX. Isso explica por que foi mais rápida que o Grupo 5 e deixa a escolha
mais sensível à amostra de validação.

## Reforço adotado para a próxima execução

- validação a cada 11 horas, percorrendo todas as horas do dia;
- aproximadamente 260 origens de validação em vez de 30/15;
- mesmas origens de validação para os quatro modelos;
- teste ampliado de 229 para aproximadamente 520 origens, mantendo o bloco
  cronológico final de 20%;
- cinco estruturas SARIMAX após a triagem BIC;
- assinatura do protocolo nos checkpoints, impedindo reaproveitar ranking
  produzido com origens, features ou janelas antigas;
- métricas adicionais: RMSE, mediana do erro absoluto, WAPE, viés, R², ACF dos
  resíduos e Ljung-Box em múltiplos lags;
- diagnóstico de resíduos em 168 previsões horárias consecutivas; os p-valores
  antigos eram calculados em origens espaçadas por 25 horas e não podiam ser
  interpretados como lags horários;
- proteção numérica auditável no Holt-Winters.

Essa ampliação pode levar aproximadamente 40–50 horas, dependendo do hardware.
O custo maior decorre de mais origens de validação, não de espera artificial.

## Validação da busca reforçada do PLS

A busca intermediária do PLS foi executada como teste de integração: 60 combinações
(três conjuntos de variáveis × 20 números de componentes) em 258 origens, sem
usar o teste para escolher. O vencedor foi `no_weather` com 14 componentes e
MAE de validação 233,92. Nas 229 origens finais ele obteve MAE 180,61, próximo
dos 177,28 anteriores. Isso mostra que o resultado do PLS é estável; a
validação maior reduz a chance de escolher uma configuração por acaso. A versão
final amplia o limite para 32 componentes e preserva a seleção somente dentro
do desenvolvimento.
