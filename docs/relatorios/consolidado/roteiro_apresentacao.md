# Roteiro da apresentação consolidada

Material visual principal: `relatorio_final.html`.

| Tempo | Página/seção | O que falar | Mensagem principal |
|---:|---|---|---|
| 0:00–0:40 | Capa e resumo | Apresentar objetivo, quatro modelos e situação da consolidação. | O documento distingue resultado disponível de conteúdo pendente. |
| 0:40–1:30 | Metodologia comum | Explicar corte temporal, validação walk-forward, teste final e MAE. | O teste não escolhe modelos nem hiperparâmetros. |
| 1:30–2:10 | Bases | Situar as cinco bases sem antecipar resultados ausentes. | Ouro é o estudo de caso atualmente completo. |
| 2:10–8:40 | Aula — PLS Regression | Percorrer motivação, multicolinearidade, componentes, PLS × PCA, scaling, `n_components`, séries temporais, leakage e interpretação. | PLS faz redução supervisionada; causalidade depende do protocolo temporal. |
| 8:40–10:00 | Aplicação do PLS | Mostrar o caso Ouro e apontar os quatro espaços pendentes. | Um caso não autoriza conclusão global. |
| 10:00–11:20 | Comparação e ranking por base | Ler a linha Ouro: Holt-Winters, SARIMAX, PLS e RF. | MAE é comparável dentro de cada base; não entre escalas distintas. |
| 11:20–11:50 | Ranking geral | Mostrar o quadro deliberadamente vazio. | Vitórias e posição média dependem das cinco bases. |
| 11:50–13:10 | Resíduos e interpretabilidade | Destacar Ljung-Box, feature importance e limites da leitura causal. | Diagnósticos complementam o MAE. |
| 13:10–14:30 | Conclusões e limitações | Encerrar apenas com conclusões locais confirmadas. | A conclusão global permanece pendente. |

## Bloco didático de PLS — 5 a 8 minutos

Preservar obrigatoriamente as páginas sobre PLS × PCA, scaling e escolha de
`n_components`, walk-forward/leakage e interpretação. Se o tempo for curto,
combinar oralmente motivação com multicolinearidade e séries temporais com
walk-forward.

## Pendências antes da apresentação final

- substituir os placeholders das Bases 1–4 por resultados auditados;
- preencher integrantes e responsabilidades;
- calcular vitórias e posição média somente depois das cinco bases;
- revisar a conclusão global após a consolidação factual.
