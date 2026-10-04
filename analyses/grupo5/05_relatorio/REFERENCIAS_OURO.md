# Referências - Base Ouro

Consulta e fechamento: 04/10/2026.

## Fonte institucional da série de ouro

- Deutsche Bundesbank. Série `BBEX3.D.XAU.USD.EA.AC.C05`: preço do ouro em Londres, fixing da tarde, USD por onça fina. Identificador e metadados preservados em `analyses/grupo5/outputs/protocol.json`. Portal oficial de séries: <https://www.bundesbank.de/en/statistics/time-series-and-real-time-data>.

## URL de aquisição do arquivo usado

- Deng Yishuo. `quantitative-finance/gold.daily.prices.csv`. URL registrada no protocolo V1: <https://github.com/dengyishuo/quantitative-finance/blob/master/gold.daily.prices.csv>. Este endereço é o local de aquisição do CSV, não a fonte institucional dos metadados.

## Séries externas

- Board of Governors of the Federal Reserve System (US). *Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity, Quoted on an Investment Basis* (`DGS10`). FRED, Federal Reserve Bank of St. Louis. <https://fred.stlouisfed.org/series/DGS10>.
- Board of Governors of the Federal Reserve System (US). *Federal Funds Effective Rate* (`DFF`). FRED, Federal Reserve Bank of St. Louis. <https://fred.stlouisfed.org/series/DFF>.

## Referências acadêmicas

- Breiman, L. (2001). Random Forests. *Machine Learning*, 45, 5-32. <https://doi.org/10.1023/A:1010933404324>.
- Chong, I.-G., & Jun, C.-H. (2005). Performance of some variable selection methods when multicollinearity is present. *Chemometrics and Intelligent Laboratory Systems*, 78(1-2), 103-112. <https://doi.org/10.1016/j.chemolab.2004.12.011>.
- Cleveland, R. B., Cleveland, W. S., McRae, J. E., & Terpenning, I. (1990). STL: A Seasonal-Trend Decomposition Procedure Based on Loess. *Journal of Official Statistics*, 6(1), 3-73.
- Holt, C. C. (2004). Forecasting seasonals and trends by exponentially weighted moving averages. *International Journal of Forecasting*, 20(1), 5-10. Reimpressão do relatório ONR de 1957. <https://doi.org/10.1016/j.ijforecast.2003.09.015>.
- Ljung, G. M., & Box, G. E. P. (1978). On a measure of lack of fit in time series models. *Biometrika*, 65(2), 297-303. <https://doi.org/10.1093/biomet/65.2.297>.
- Winters, P. R. (1960). Forecasting Sales by Exponentially Weighted Moving Averages. *Management Science*, 6(3), 324-342. <https://doi.org/10.1287/mnsc.6.3.324>.
- Wold, H. (1975). Path Models with Latent Variables: The NIPALS Approach. In *Quantitative Sociology*. <https://doi.org/10.1016/B978-0-12-103950-9.50017-4>.

## Bibliotecas e documentação técnica

- statsmodels. `SARIMAX`. <https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html>.
- statsmodels. `ExponentialSmoothing`. <https://www.statsmodels.org/stable/generated/statsmodels.tsa.holtwinters.ExponentialSmoothing.html>.
- statsmodels. `STL`. <https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html>.
- statsmodels. `acorr_ljungbox`. <https://www.statsmodels.org/stable/generated/statsmodels.stats.diagnostic.acorr_ljungbox.html>.
- scikit-learn. `RandomForestRegressor`. <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html>.
- scikit-learn. `PLSRegression`. <https://scikit-learn.org/stable/modules/generated/sklearn.cross_decomposition.PLSRegression.html>.
- scikit-learn. `StandardScaler`. <https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>.
- scikit-learn. `permutation_importance`. <https://scikit-learn.org/stable/modules/generated/sklearn.inspection.permutation_importance.html>.

Somente fontes efetivamente usadas na construção, interpretação ou implementação da base Ouro foram incluídas.
