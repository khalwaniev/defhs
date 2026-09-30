# Data Unknown Register — Closure Continuation

This register deliberately distinguishes genuine epistemic unknowns from **required analyses not yet executed**. Rows marked `PENDING REQUIRED AUDIT` are not valid final evidence states; their presence is why the mission currently returns `FAIL_NOT_READY`.

| Question | Current state | Evidence / uncertainty | Decision policy |
|---|---|---|---|
| 1,036 prose vs 1,035 package | UNRESOLVABLE | package is exactly IDs 1..1035; no missing supplied ID; origin of prose mismatch absent | use supplied package authority; no invented row |
| package/schema integrity | VERIFIED | 826 train, 209 test; test IDs equal sample-submission IDs | freeze supplied schema |
| WAV encoding | VERIFIED | mono 16 kHz; 933 int16 / 102 int32 | retain format/source stress |
| duplicate boundaries | VERIFIED | huge similarity gap; graph stable through about 0.974 | threshold 0.95 frozen |
| duplicate transformations | INFERRED | many accepted pairs are waveform-near-identical but not byte-identical, with same length/dtype | retrieval only inside frozen graph |
| label conflict | VERIFIED | IDs 75 / 636 / 878 have neutral / sad / neutral | do not auto-relabel |
| broader per-row label noise | UNRESOLVABLE | model disagreement is not annotation ground truth | no model-driven relabeling |
| class structure | VERIFIED | 205 angry / 192 happy / 217 neutral / 212 sad | stratify folds |
| source/recording heterogeneity | VERIFIED | int16/int32 regimes differ materially and transfer poorly | V-D stress |
| stable low-level latent source clusters | INFERRED, insufficient for grouping authority | weak/moderate cross-representation stability | do not replace V-A/V-B with low-level clusters |
| true organizer speaker IDs | UNRESOLVABLE | no speaker IDs are supplied | never claim exact organizer identities |
| reliable speaker-like grouping | PENDING REQUIRED AUDIT | actual ECAPA embeddings have not yet been executed | no V-C freeze yet |
| train/test speaker-like overlap | PENDING REQUIRED AUDIT | depends on actual speaker embedding clustering | no overlap claim yet |
| exact organizer acted/spontaneous labels | UNRESOLVABLE | no per-clip labels are supplied | never fabricate semantic labels |
| inferable acted/spontaneous-like latent regimes | PENDING REQUIRED AUDIT | must reconsider after speaker + ASR + eGeMAPS | no hard regime grouping yet |
| exact organizer prompt/script IDs | UNRESOLVABLE | no prompt IDs supplied | never claim exact organizer prompt identity |
| inferable prompt/script families | PENDING REQUIRED AUDIT | actual Hindi ASR not yet executed | no prompt grouping authority yet |
| standardized eGeMAPS structure | PENDING REQUIRED AUDIT | openSMILE eGeMAPSv02 has not yet executed | do not claim standardized descriptor closure |
| ID/acquisition simple leakage | VERIFIED negative | runs and ID-only AUC are near row-random expectation/chance | exclude ID as predictive feature/group |
| train/test shift from current acoustic matrix | INFERRED modest nonlinear residual | no-duplicate ExtraTrees AUC ~0.581; logreg ~0.494 | stress-test; do not redefine test DGP |
| test sampling mechanism | INFERRED closest to row-random mixture, not proven | IDs interleave; global adversarial AUC near chance; format fractions similar | V-A secondary estimator; V-B guardrail |
| public sample fraction | UNRESOLVABLE | 0.40/0.60 score weights do not reveal row fractions | sensitivity analysis 20–50% |
| hidden public/private assignment | UNRESOLVABLE | assignment/labels hidden | Monte Carlo sensitivity only |
| retrieval applicability | VERIFIED for frozen graph | 77 cross-split groups / 78 test clips; unanimous usable train consensus | deterministic separate retrieval lane |
| V-A membership | VERIFIED / byte-preserved | canonical CSV SHA-256 dcee356b0a66cb73c506bb71a6c57962227d6d0474efd3e4d6c404168308f3d1 | preserve |
| V-B membership | VERIFIED / byte-preserved | canonical CSV SHA-256 87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b | preserve |
| protected promotion membership | VERIFIED / byte-preserved | seed 20261001 CSV SHA-256 b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c | do not use for exploration |
| V-D membership | VERIFIED / byte-preserved | int16/int32 regime CSV SHA-256 f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839 | preserve as stress |

## Closure consequence

Because three decision-relevant rows remain `PENDING REQUIRED AUDIT`, the completeness contract is not yet satisfied and no final data-understanding certificate may claim PASS.
