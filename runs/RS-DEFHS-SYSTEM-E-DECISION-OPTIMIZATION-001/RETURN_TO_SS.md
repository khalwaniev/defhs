# RETURN TO SS — RS-DEFHS-SYSTEM-E-DECISION-OPTIMIZATION-001

**Verdict: CLOSE_DECISION_THEORY_BRANCH — NO PROMOTION, NO NEW SUBMISSION.**

Canonical start: `a6676d9777ace9e9746802b3256cd3eb52dd7339`, new branch `rs/system-e-decision-optimization-001`. Fully authenticated System E (`0.8774091527555827` PRIMARY_CV), original candidate SHA256 `e47676192cbd02393a49889214238f34cb8b49df2f9772b30cb19d766589df90`; original E Q960/606 failure **−0.03367392841077055** is binding. User-reported E public LB `0.89505` is not a new result of this mission. No competition submissions, no new test candidate.

## Two predeclared, group-purged, outer-fold-safe tests

All class priors and expert reliability parameters are fitted from training-side labels only, **excluding any training component linked by the 656-component bootstrap graph to outer-heldout rows** (excluded 7, 6, 10, 7, 7 per fold). The original OOF probabilities are fixed. No target labels, threshold sweep, nested model refit or heldout-label-based decision. Both methods are specified **before** evaluation.

| Metric | E argmax | A: joint macro-F1 | B: expert reliability |
|---|---:|---:|---:|
| Pooled macro-F1 | 0.8774091528 | **0.8799316081** | **0.8670270986** |
| Delta | — | +0.0025224553 | −0.0103820541 |
| Changed rows | — | 6 | 38 |
| Corrections / breakages / wrong→wrong | — | 3 / 1 / 2 | 12 / 21 / 5 |
| HARD316 delta | — | +0.00574793 | −0.01441187 |
| INT16 subgroup delta | — | +0.00278770 | −0.01047034 |
| INT32 subgroup delta | — | −0.00001266 | −0.01301592 |
| Q960/606 delta versus E | — | 0 | −0.07075887 |
| Q960/606 delta versus D | −0.03367393 | −0.03367393 | −0.10443280 |
| Bootstrap simultaneous max-t CI95 for gain | — | [−0.00420024,+0.00924515] | [−0.02900621,+0.00824210] |

A fold deltas: `[-0.00597210,0,-0.00005273,+0.01800815,0]`; **only one improved fold**. B fold deltas: `[-0.02372711,-0.01170900,-0.00620374,+0.01179063,-0.02130541]`; **four deteriorated folds**. Two-family multiplicity-adjusted 95% intervals use 2,000 exponential-multiplier replicates over 656 authenticated dependency components (seed 20260930). These are bootstrap uncertainty bounds, not proof of a positive effect.

**A mechanism:** deterministic, transductive greedy ascent on the *ratio-of-expectations* macro-F1 approximation, with outer-train empirical priors and joint unlabeled outer-fold posterior matrices. It does **not** compute exact E[macro-F1] and depends on probability calibration and assumed class prevalence. Strict deployability would require the same batch-wise transductive contract, including careful handling of certified retrieval assignments. No target output created because it failed promotion.

**B mechanism:** when E and new semantic expert disagree, switch to the expert only if expert is E's second posterior-ranked class and a Beta(1,1) class-conditional semantic-precision **lower 95% bound**, fitted on outer training examples, exceeds E's top-1 probability. Conservative adjudication still breaks 21 correctly predicted rows. The expert label is already one of E's 23 features, so comparing marginal expert accuracy against E's conditioned posterior can double-count correlated evidence; no calibrated improvement shown.

**OOF posterior diagnostic:** ECE (10 fixed-width confidence bins) `0.01768627`, multiclass logloss `0.35355280`, multiclass Brier `0.18283459`. Per-class average E predicted prevalence and empirical class prevalence differ by <0.003. This suggests reasonable **aggregate** calibration, not validation of exact conditional probabilities. Residual oracle headroom: 102 E errors; truth rank-2 in 74; new Qwen semantic correct in 32; q also rank-2 on 29 of those. These counts are **not selectable using inference-time labels**.

**V-A / cross-format limitation:** Original accepted V-A retrieval pipeline E `0.8915563853`, D `0.8722913049`; original frozen cross-format E−D deltas `+0.05789286` (int16→int32) and `+0.08858488` (int32→int16). Original V-A artifact has hard labels only, not class posterior matrices. The decision policies were **not** evaluated on V-A or retrained cross-format posteriors: do not misrepresent VB dtype subgroup analysis as V-D generalization. Given no robust primary gain, Phase C stops before spending compute on rebuilding V-A or cross-format data.

**Authenticity:** source scientific ZIP SHA256 `dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf`; baseline D archive `fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839`; official E canonical bundle `c7f16f3f91be5b90349641a61d85222e69d71b5f88dcb1bb3030acfad8718a59`. E PRIMARY OOF CSV `a7a1e456883119c60a2d5e77dd8cad93ba384cd707d66e3e5918cab974903aff`. Exact original production replay PASS, unchanged 209 prediction SHA, 78/78 certified retrieval assignments protected.

**Implementation:** ~CPU seconds for two decision rules plus 2,000 dependency bootstraps; no GPU; read-only original evidence. Reproduction is in `scripts/decision_audit_system_e.py` and `runs/RS-DEFHS-SYSTEM-E-DECISION-OPTIMIZATION-001/DECISION_TESTS.json` with 826-row prediction audit. Keep original E deployment and production package; **no challenger candidate SHA or submission**.

**Final disposition:** Both families CLOSED_NOT_PROMOTED. Do not try unpredeclared threshold tweaks, resurrect rejected transforms, or probe public LB. Await SS's new independent complementary expert if Astra provides one, under exact original nested procedure. No Kaggle competition submission performed.