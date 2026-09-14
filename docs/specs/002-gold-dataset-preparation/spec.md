# Spec Preparação da base de ouro

## Comportamento esperado

A primeira base congelada deve ser construída de forma reproduzível a partir dos três CSVs em `bases/raw/`. A série do ouro preserva seu próprio calendário; DGS10 e DFF são externas observadas, preenchidas somente por avanço de valor para lacunas de calendário e defasadas uma observação para garantir disponibilidade antes da origem.

## Critérios de aceitação

1. A saída tem somente datas existentes no ouro, ordenadas e sem duplicatas.
2. `TARGET` é o ouro na próxima observação; lags e janelas não usam o futuro.
3. `TARGET_UP` não é feature e `IS_HOLIDAY` só seria incluída com fonte reproduzível.
4. O script produz a saída sem edição manual e relata a limpeza.
5. Não há implementação de modelos, tuning ou avaliação nesta etapa.
