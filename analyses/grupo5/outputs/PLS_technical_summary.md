# Síntese técnica do PLS Regression

## 1. Intuição

Partial Least Squares transforma as features originais em componentes latentes. Cada componente é uma combinação linear das variáveis e é construído para explicar simultaneamente a estrutura de `X` e sua covariância com o alvo `y`. Depois, a regressão é ajustada nesse espaço latente.

## 2. Componentes e covariância com o alvo

Diferentemente de uma redução não supervisionada, o PLS considera o alvo ao definir as direções latentes. Variáveis que variam em conjunto e que também ajudam a explicar `TARGET` podem ser condensadas em poucos componentes. Isso é especialmente útil quando preço atual, lags e médias móveis são fortemente correlacionados.

## 3. Diferença para regressão linear comum

A regressão linear comum estima diretamente um coeficiente por feature no espaço original e pode ficar instável sob multicolinearidade. O PLS primeiro projeta as features em componentes ordenados pela relação com o alvo e então ajusta a regressão nesses componentes. O parâmetro `n_components` controla quanta informação latente é retida e funciona como controle de complexidade.

## 4. Preparação e padronização

RF e PLS receberam as mesmas 12 features causais. Em cada origem walk-forward, o `StandardScaler` foi ajustado novamente somente na janela de treino e aplicado à linha da origem. Isso evita que média ou escala da validação/teste entrem no treinamento. `TARGET` e `TARGET_UP` não foram usados como features.

## 5. Seleção de 11 componentes

Foram avaliados de 1 a 12 componentes na validação walk-forward. Onze componentes produziram o menor MAE de validação, 2,9701, conforme o critério congelado antes do teste. Usar 11 componentes para 12 features representa uma compressão pequena: o modelo preserva quase toda a dimensionalidade disponível, mas ainda trabalha em direções latentes orientadas pela covariância com o alvo.

Esse resultado sugere que a melhor configuração validada não foi uma redução agressiva. Também indica que parte da informação útil pode estar distribuída por várias direções, apesar da multicolinearidade. O teste final não foi usado para rever os 11 componentes.

## 6. Interpretação das features

Os coeficientes padronizados permitem comparar magnitudes na escala transformada, mas sinais e tamanhos devem ser lidos com cautela quando as features são correlacionadas. Os VIP Scores medem a contribuição de cada feature para os componentes que explicam o alvo. A permutation importance mede quanto o MAE se deteriora ao embaralhar uma feature, mantendo o modelo fixo.

`GOLD_PRICE`, `GOLD_LAG_1`, `GOLD_ROLLING_MEAN_5`, `GOLD_LAG_5` e `GOLD_LAG_20` foram as principais variáveis do PLS. Treasury e Fed Funds tiveram VIP abaixo de 1 e pequena contribuição marginal neste desenho experimental.

## 7. Vantagens e limitações

As vantagens do PLS são lidar bem com multicolinearidade, produzir uma representação latente supervisionada e manter uma forma linear relativamente interpretável. As limitações incluem relações predominantemente lineares, sensibilidade à escala, interpretação menos direta dos componentes e possível instabilidade quando o regime de mercado muda.

Com 11 de 12 componentes, o benefício de compressão é limitado. O modelo também depende fortemente da persistência do preço e pode perder desempenho quando a relação entre nível, lags e externas muda.

## 8. Desempenho

O PLS venceu a validação, mas terminou em terceiro no teste com MAE 11,6002. O SARIMAX obteve 11,5988; a diferença absoluta foi aproximadamente 0,0014 de MAE. Isso é desempenho praticamente equivalente, não uma contradição.

Validação e teste cobrem períodos distintos. Variabilidade amostral, mudanças de regime e diferenças muito pequenas podem trocar a ordem sem invalidar a seleção. O teste foi usado somente para avaliação final e não alterou `n_components=11`.
