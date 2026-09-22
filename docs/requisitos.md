# Requisitos rastreáveis do Grupo 5

## Objetivo e escopo

O Grupo 5 comparará quatro modelos em cada uma de cinco bases temporais congeladas: SARIMAX, Holt-Winters, Random Forest e PLS Regression. São vinte combinações principais. Cada integrante é responsável pela pipeline completa de uma base, mas a comparação final reúne as cinco áreas. Esta fundação não ajusta modelos nem escolhe fontes ausentes.

## Bases e disponibilidade temporal

Cada base deve declarar fonte, cobertura, frequência, unidade da variável-alvo, horizonte e pelo menos duas variáveis externas. Antes da modelagem, o grupo congelará os arquivos, registrará checksum SHA-256 e documentará a fonte original, verificará lacunas, duplicidades, periodicidade, valores atípicos e decisões de limpeza.

Para cada variável externa, o dicionário precisa provar a disponibilidade no momento da origem da previsão. Calendário, feriados e promoções planejadas podem ser conhecidos antecipadamente; previsão publicada na origem pode ser usada e identificada como previsão; observações futuras, como temperatura realizada ou vendas futuras, são proibidas. Variáveis indisponíveis devem usar defasagem, previsão disponível ou ser excluídas.

## Exploração, STL e features

Cada base terá gráficos do alvo e variáveis externas, decomposição STL e interpretação de tendência, sazonalidade e resíduo, incluindo a força sazonal pelo método da aula. As features tabulares devem respeitar o horizonte e ser compartilhadas entre Random Forest e PLS quando compatíveis: lags, janelas móveis, calendário, encoding cíclico e externas temporalmente válidas. Valores ausentes introduzidos por lags e janelas serão tratados e documentados.

## Protocolo experimental

A validação walk-forward usará somente informação disponível até cada origem. Todos os modelos usarão as mesmas origens, horizonte e período final de teste. Hiperparâmetros serão selecionados antes da avaliação final, sem usar o teste final para decisão, e ficarão fixos nessa avaliação.

SARIMAX investigará ordens regulares e sazonais, período, AIC/BIC e externas. Holt-Winters será a referência univariada, sem variáveis externas. Random Forest investigará tamanho da floresta, profundidade, divisões, folhas e features. PLS Regression investigará número de componentes, padronização e demais decisões necessárias, sempre com ajuste estritamente interno a cada janela de treinamento.

## Métricas, resíduos e interpretação

MAE será calculado somente nas previsões fora da amostra. Os MAEs não serão agregados diretamente entre bases de escalas distintas; serão apresentados por base, classificados, e consolidados por vitórias e posição média. Para cada combinação serão preservados previsões, resíduos, parâmetros e tempo de execução.

Os resíduos fora da amostra terão série temporal, ACF, Ljung-Box e interpretação de viés, variabilidade e autocorrelação. A tabela consolidada de Ljung-Box ficará no relatório principal. Random Forest e PLS terão importância de features: PLS utilizará coeficientes padronizados, Permutation Importance ou VIP Scores, com método e limitações documentados; variáveis externas serão destacadas com sua disponibilidade temporal.

## Entregáveis e gestão

O relatório HTML paginado e seu PDF terão o mesmo conteúdo: resumo, participantes, bases, preparo, STL, walk-forward, modelos/tuning, MAE, resíduos, importância, explicação didática do PLS, conclusões, referências e apêndices. A apresentação oral navegará pelo HTML; não exige slides separados. A entrega final incluirá PDF, HTML autocontido, fonte do relatório, códigos, bases/fontes e consolidação de MAE.

## Desvio assumido da atividade

Por decisão explícita do grupo, este repositório não manterá o registro diário de demandas solicitado no enunciado. Isso remove o DOCX e seus checks, mas pode deixar a entrega incompleta e afetar a avaliação individual. A decisão não deve ser interpretada como dispensa concedida pelo professor.
