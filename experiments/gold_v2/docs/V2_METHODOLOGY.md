# V2 methodology

V2 asks whether forecast error is meaningful relative to the natural one-step
movement of gold, whether persistence explains the result, and whether external
blocks add information beyond gold dynamics.

The three targets are level (`TARGET`), delta (`TARGET - GOLD_PRICE`) and log
return (`log(TARGET / GOLD_PRICE)`). Return and delta predictions will be
reconstructed to price before the primary MAE in USD/oz is compared.

All external series carry an event date and conservative availability rule. In
the absence of a documented intraday timestamp, `available_date = event_date +
one calendar day`; joins are backward as-of only. No nearest, forward, or
backfill merge is allowed.

Track A contains the long-history core and is the only candidate for a fair V1
comparison. Track B adds DFII10 from its available period and reports common
dates explicitly. Track C is reserved for retrospective EPU/GPR research and
cannot replace an official result without vintage analysis.

Stage A uses no tuning and no re-evaluation of the frozen test. Its ablation is
a twelve-origin feasibility screen on V1 validation dates with a fixed two-
component PLS; it establishes data viability only. Stage B, if approved, will
run the complete temporal evaluation, selected models, block permutation, VIP,
and stability analysis.
