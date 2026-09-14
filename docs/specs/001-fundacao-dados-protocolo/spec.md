# Spec Fundação de dados e protocolo experimental

## Comportamento esperado

O projeto deve impedir que a modelagem comece com bases não congeladas, variáveis externas sem disponibilidade temporal declarada ou previsão que use dados futuros. Deve existir uma configuração versionada para até cinco bases e cada base modelável deve declarar ao menos duas variáveis externas, horizonte e evidência de disponibilidade.

O protocolo final deverá aplicar as mesmas origens e horizonte aos quatro modelos. A seleção de hiperparâmetros ocorrerá antes do teste final. Quando código e esta spec discordarem sobre comportamento, esta spec prevalece até revisão explícita.

## Critérios de aceitação

1. A configuração aceita no máximo cinco bases e rejeita uma base com menos de duas externas.
2. Toda externa usa uma das classificações de disponibilidade definidas e contém evidência textual.
3. Uma feature cuja disponibilidade é posterior à origem da previsão é rejeitada.
4. Nenhum modelo é implementado nesta feature.
