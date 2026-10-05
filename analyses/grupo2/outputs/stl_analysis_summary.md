# Síntese da decomposição STL — Base 2

A STL foi estimada **somente no desenvolvimento** (80%), com período 24 (ciclo diário de uma série horária). Um ano de amostra interna foi usado para o gráfico (`stl_summary.json`).

1. **Há tendência?** Sim, mas suave. A média da tendência no início da amostra (~3.463) é próxima da do fim (~3.451). Não há tendência explosiva de longo prazo no segmento 2015–2018; o nível médio do tráfego é estável.
2. **Como a tendência muda?** Oscila com férias e mudanças de regime semanal, sem quebra estrutural forte no recorte posterior à lacuna.
3. **Existe sazonalidade relevante?** Sim. A força sazonal foi **0,806** no período 24. Isso é sazonalidade diária nítida (vale noturno, pico matinal e vespertino).
4. **E o ciclo semanal?** A STL oficial usou m=24, alinhada ao SARIMAX. O Holt-Winters, na validação, preferiu sazonalidade **168** (semana) sem tendência. As duas escalas convivem: o dia organiza o perfil; a semana organiza feriados e fins de semana.
5. **Como se comporta o residual?** Concentra incidentes, clima extremo e feriados que o ciclo médio não captura. Não deve ser lido como erro de medição automático.

A STL do teste não foi inspecionada para escolher modelo. Figura: `04_stl.png`.
