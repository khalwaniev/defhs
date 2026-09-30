# Data Unknown Register — Final Freeze

Mission: `DS-DEFHS-VALIDATION-HARDENING-002`

No decision-relevant question remains in a `PENDING REQUIRED AUDIT` state.

| Question | Final state | Evidence / uncertainty | Decision policy |
|---|---|---|---|
| 1,036 prose vs 1,035 supplied package | UNRESOLVABLE FROM AVAILABLE EVIDENCE | supplied package is exactly IDs 1..1035; no missing supplied ID | use supplied package authority; do not invent a row |
| package/schema integrity | VERIFIED | 826 train, 209 test; test IDs match sample submission | freeze supplied schema |
| WAV encoding | VERIFIED | all mono 16 kHz; 933 int16 / 102 int32 | retain V-D format/source stress |
| duplicate boundaries | VERIFIED | sharp similarity gap; graph stable through approximately 0.974 | threshold 0.95 frozen |
| duplicate transformations | INFERRED | accepted pairs are waveform-near-identical variants, not always byte-identical | retrieval only inside frozen graph |
| label-conflict family | VERIFIED | IDs 75 / 636 / 878 = neutral / sad / neutral | do not auto-relabel |
| broader per-row label correctness | UNRESOLVABLE FROM AVAILABLE EVIDENCE | model disagreement is not annotation ground truth | no model-driven relabeling |
| class structure | VERIFIED | 205 angry / 192 happy / 217 neutral / 212 sad | preserve stratification |
| source/recording heterogeneity | VERIFIED | int16/int32 regimes differ materially and cross-format transfer is difficult | retain V-D |
| low-level latent source clusters | INFERRED | weak/moderate cross-representation stability | diagnostic only |
| exact organizer speaker IDs | UNRESOLVABLE FROM AVAILABLE EVIDENCE | no speaker IDs supplied | never claim exact organizer identities |
| speaker-like structure | INFERRED | ECAPA executed; strict stable clusters mostly reproduce duplicate families; permissive clusters are threshold-sensitive | reject authoritative V-C; retain ECAPA diagnostics |
| train/test speaker-like overlap | INFERRED | mixed ECAPA clusters exist, including some beyond duplicates at permissive thresholds, but exact count depends on clustering threshold | no exact speaker-overlap claim |
| exact organizer acted/spontaneous labels | UNRESOLVABLE FROM AVAILABLE EVIDENCE | no per-clip regime labels supplied | never fabricate labels |
| acted/spontaneous-like latent regimes | INFERRED weak | joint k=2..6 clustering has low silhouette and moderate k sensitivity | no latent-regime validation authority |
| exact organizer prompt/script IDs | UNRESOLVABLE FROM AVAILABLE EVIDENCE | no prompt IDs supplied | never claim exact prompt identity |
| prompt/script families | INFERRED | ASR found repeated prompts; at sim 0.90 only 15 clusters / 46 clips add structure beyond duplicate families | diagnostic only; no prompt-grouped validation |
| ASR transcript content | INFERRED | Whisper audit has 1,035 non-empty Hindi decodes with strong internal consistency, but transcripts are machine-generated | structural audit evidence, not ground truth |
| standardized eGeMAPS structure | VERIFIED | openSMILE eGeMAPSv02, 88 descriptors x 1,035 rows; train/test logistic AUC mean 0.4764 | no architecture change |
| simple ID/acquisition leakage | VERIFIED negative | ID-only/runs diagnostics remain near chance expectation | exclude ID as predictive/grouping feature |
| train/test shift | INFERRED modest nonlinear residual | acoustic no-duplicate ExtraTrees AUC ~0.581; linear acoustic/eGeMAPS diagnostics near chance | stress-test; do not redefine test as separate domain |
| test sampling mechanism | INFERRED closest to row-random/common-mixture behavior, not proven | IDs interleave; global adversarial evidence weak; standardized features and latent split NMI show no strong separation | V-A secondary competition-mimic; V-B primary guardrail |
| public/private row fraction | UNRESOLVABLE FROM AVAILABLE EVIDENCE | 0.40/0.60 score weights do not reveal row fractions | sensitivity analysis at 20/30/40/50% |
| hidden public/private assignment | UNRESOLVABLE FROM AVAILABLE EVIDENCE | assignment and labels hidden | Monte Carlo sensitivity only |
| retrieval applicability | VERIFIED | 77 cross-split duplicate groups / 78 test clips; usable train labels unanimous | deterministic separate retrieval lane |
| V-A membership | VERIFIED / byte-preserved | SHA-256 dcee356b0a66cb73c506bb71a6c57962227d6d0474efd3e4d6c404168308f3d1 | preserve |
| V-B membership | VERIFIED / byte-preserved | SHA-256 87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b | preserve |
| protected promotion membership | VERIFIED / byte-preserved | seed 20261001; SHA-256 b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c | confirmation only; no exploration |
| V-D membership | VERIFIED / byte-preserved | SHA-256 f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839 | retain as diagnostic source-format stress |
| protected gate execution status | VERIFIED untouched | closure kernels did not package/query VP; final DS interpretation did not evaluate candidate models on it | remain protected |

## Final consequence

Every material observable question has now been either directly resolved,
defensibly inferred, or bounded as unresolvable from available evidence.

The remaining unknowns are epistemic metadata/hidden-label unknowns whose
decision impact is controlled by the frozen validation architecture.

Final DS disposition:

**REVISE_AND_FREEZE**
