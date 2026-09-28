# Plano - Spec 004

1. Documentar e travar o contrato causal da base de ouro no primeiro notebook.
2. Auditar dados, aprovar features e período sazonal antes de qualquer tuning.
3. Executar as grades congeladas somente no trecho de validação; salvar ranking, previsões de validação, MAE e tempo por origem.
4. Revisar e aceitar manualmente o vencedor determinado pelo critério pré-fixado.
5. Confirmar os vencedores em walk-forward de validação e solicitar nova aprovação humana.
6. Somente após essa aprovação, habilitar uma etapa separada para as 296 origens de teste com parâmetros congelados; calcular importâncias pós-hoc sem realimentar decisões.
7. Produzir resíduos, Ljung-Box e comparação local usando os artefatos finais.

Cada etapa depende da decisão humana registrada no `protocol.json`; nenhum notebook de relatório faz parte deste plano.
