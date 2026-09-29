# Stage A findings — not final conclusions

- On the 296 frozen V1 test origins, the mean absolute next-observation gold
  move is **11.6377 USD/oz** and its median is **8.5000 USD/oz**.
- V1 Holt-Winters MAE is **11.5331 USD/oz**, 0.9910 times that natural-move
  baseline; SARIMAX and PLS are 0.9967 and 0.9968 times it, respectively.
- This establishes a strong persistence benchmark. It does not by itself prove
  a model is economically useful or useless.
- The preliminary 12-origin PLS ablation is explicitly too small and too
  untuned for ranking. It is evidence of feasible pipelines only; its results
  must not be reported as V2 performance.
- DFII10 makes a real-yield Track B possible from 2003 onward; it prevents a
  naive whole-period comparison to V1.
