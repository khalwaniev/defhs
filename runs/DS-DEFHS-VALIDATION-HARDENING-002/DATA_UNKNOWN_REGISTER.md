# Data Unknown Register

| Question | State | Evidence / uncertainty | Decision policy |
|---|---|---|---|
| 1,036 prose vs 1,035 package | UNRESOLVABLE | package is exactly 1..1035; no missing supplied ID | use package authority; no invented row |
| package/schema integrity | VERIFIED | 826 train, 209 test, sample IDs match | freeze supplied schema |
| WAV encoding | VERIFIED | mono 16 kHz; int16/int32 regimes | retain format stress |
| duplicate boundaries | VERIFIED | huge similarity gap; graph stable through 0.974 | threshold 0.95 frozen |
| duplicate transformations | INFERRED | many non-byte-identical same-length/same-dtype near copies | retrieval allowed only inside frozen graph |
| label conflict | VERIFIED | IDs 75/636/878 disagree | do not auto-relabel |
| broader label noise | INFERRED / UNRESOLVABLE per-row | model disagreement is not ground truth | no model-driven relabeling |
| class structure | VERIFIED | 205 angry / 192 happy / 217 neutral / 212 sad | stratify folds |
| source/recording heterogeneity | VERIFIED | int16/int32 differ materially | V-D stress |
| stable latent source clusters | INFERRED, insufficient for authority | cross-representation ARI weak/moderate | no cluster-group primary split |
| true speaker IDs | UNRESOLVABLE | no IDs; pretrained speaker weights unavailable in current execution | no V-C freeze |
| train/test speaker overlap | UNRESOLVABLE | same reason | stress via V-B/V-D, do not claim disjointness |
| acted/spontaneous membership | UNRESOLVABLE | organizer says mixture; no labels; latent clusters not identifiable as regimes | no hard regime labels |
| prompt/script families | UNRESOLVABLE | no text; ASR model unavailable in current execution | no prompt grouping authority |
| ID/acquisition semantics | VERIFIED negative for simple leakage | runs and ID-only AUC near random | exclude ID as feature/group |
| train/test shift | INFERRED modest nonlinear residual | no-duplicate ExtraTrees AUC ~0.581; logreg ~0.494 | stress-test, do not redefine test DGP |
| test sampling mechanism | INFERRED closest to row-random mixture, not proven | IDs interleave, split AUC near chance, similar format fractions | V-A secondary estimator; V-B guardrail |
| public fraction | UNRESOLVABLE | scoring weights do not identify sample fractions | sensitivity 20–50% |
| hidden public/private assignment | UNRESOLVABLE | labels/assignment hidden | Monte Carlo sensitivity only |
| retrieval applicability | VERIFIED for frozen graph | 77 cross groups / 78 test clips; unanimous train consensus | deterministic separate retrieval lane |
