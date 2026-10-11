# Return to SS — final semantic challenger

**Recommendation: retain System C (public 0.86997) unchanged. Execute the one
sealed Qwen3-14B Kaggle run immediately if dual-T4 capacity is available. No
new-model improvement has yet been established.**

Status: **AWAITING EXTERNAL GPU EXECUTION**, not scientifically negative.
Deadline supplied by SS: **13 October 2026, 01:30 WIB / 12 October, 18:30 UTC**.
Parent: `021d060bc9288f4d2c2d14c37022e2898aed1d01`.
Research branch: `rs/final-semantic-challenger-001`.
The inference-only launch commit is `2ced9b1c8bb7dc33518b3938703f8c9231c3b332`.
The final evidence commit is the head containing this report, returned explicitly
in the RS response. The original branch and incumbent files are not modified.

## Verified existing-model results

The earlier AST replay was inspected. Its exact artifact IDs recovered the
waveform matrices, preserved historical outer probabilities/heads and complete
Qwen3-8B semantic outputs, all checksum-verified. C's 826 row-level predictions
were reconstructed by the accepted nested recipe. Pooled score, every fold,
confusion matrix, hard cohort and corrections/breakages match the published C
authority exactly. `SYSTEM_C_AUTHORITY_OOF.csv` records the rows and probabilities.
This is an authenticated recipe replay; an archived original C row-file checksum
is not available in the accepted report, so byte-identical archival recovery is
not claimed.

| System | Full four-class macro-F1 | Coverage | Correct / 826 |
|---|---:|---:|---:|
| Historical Qwen3-8B semantics | 0.5172141900 | 467/826 (56.54%) | 350 |
| Incumbent System C | 0.8135577912 | 826/826 | 671 |
| New Qwen3-14B semantics | Not run | Unknown | Unknown |
| New waveform + semantic fusion | Not run | Unknown | Unknown |

Qwen abstentions count as false negatives in the four scored classes. Its
covered-only macro-F1 is **0.7280251225**; that is not
its full-population score.

| PRIMARY_CV fold | Qwen3-8B | System C | Challenger |
|---|---:|---:|---|
| 0 | 0.4899370133 | 0.7548722211 | Pending |
| 1 | 0.5347153589 | 0.8123673740 | Pending |
| 2 | 0.5381290639 | 0.8494805999 | Pending |
| 3 | 0.5684858698 | 0.8250607091 | Pending |
| 4 | 0.4396759954 | 0.8255294349 | Pending |

| Class F1 | Qwen3-8B | System C | Challenger |
|---|---:|---:|---|
| angry | 0.2786885246 | 0.8487804878 | Pending |
| happy | 0.5652173913 | 0.8351063830 | Pending |
| neutral | 0.6418604651 | 0.7749419954 | Pending |
| sad | 0.5830903790 | 0.7954022989 | Pending |

C makes 29 neutral->sad and 20 sad->neutral errors. Against the fixed waveform
pair, C supplies **70 corrections / 41 breakages**, plus 15 wrong-to-other-wrong
changes. Its historical 316-row hard-surrogate macro-F1 is **0.6578392458**.
There are 283 waveform-disagreement rows. Old Qwen still correctly labels 22
rows C misses; this is an oracle diagnostic, not an authorized override rule.
New-model corrections, breakages and private-allocation effects are **unknown**.

## Model and transcript evidence

One model selected: `Qwen/Qwen3-14B`, revision
`40c069824f4251a91eefaf281ebe4c544efd3e18`, NF4 double quantization, FP16.
The same historical label-blind prompt and constrained decoding are retained.
Independent MMLU-ProX Hindi five-shot results are 53.7 vs 47.0 for 14B vs 8B;
these are general linguistic evidence, not DEFHS emotion results. Details and
primary sources are in `MODEL_SELECTION.md`.

All eight pinned weight URLs returned HTTP 200. Model weights were not
transferred into this CPU-only environment. The snapshot is about 29.55 GB;
resident weight storage is estimated around 10 GB combined across two GPUs.
Actual dual-T4 memory/runtime remain **unmeasured**. The runner measures them
and enforces a two-hour inference forecast plus a six-hour evaluation reserve
before the full pass. No API key is required.

The original ASR file is checksum-verified: 1035 rows = 826 train + 209 test,
zero empty texts, 711 unique train strings, and exact text parity with the old
Qwen package. Median transcript length is 27 characters; three ASR rows have
average log probability below -1. There is no independent reference transcript
or WER measurement. Do not call ASR correctness certified.

## Scientific gate and limitations

`PROTOCOL.md` freezes one 18-input nested L2 logistic fusion, unchanged original
folds, all fitting boundaries and numerical gates before any new outputs.
Primary promotion requires >=0.005 pooled gain, >=4/5 positive folds, no class
loss >0.02, nonnegative hard-cohort gain, positive dependency-bootstrap lower
bound and positive leave-one-fold-out gains. Only passage opens new candidate
V-A/retrieval, V-D/Q and scoped private-allocation sensitivity tests. No old
robustness result certifies this challenger. No protected split is queried.

An initial fresh-refit parity check stopped at an XLS-R mismatch. Investigation
confirmed all ten preserved heads reproduce historical decisions, with maximum
probability difference 3.9807408914e-7. Full fresh sklearn-1.8 refits differ on
five XLS-R hard decisions from the historical saved probabilities. Both C and
the proposed challenger therefore use the same authentic outer probabilities;
fresh inner heads use the accepted sklearn-1.8 recipe. This distinction is
recorded in `PRESERVED_HEAD_PARITY.json` and `NESTING_REPLAY_AUDIT.json`.

Six offline tests pass, including an outer-label perturbation test that leaves
that fold's inner features and predictions exactly unchanged, abstention scoring,
closed output states, sealed inference inputs and incumbent/retrieval hashes.
GPU code and candidate stress results have not been executed. A missing returned
inference contract fails closed before any new semantic result is written.

## Compute and target effects

Completed C replay: **5.284699 seconds** wall,
50 base fits + five C meta fits; preliminary aborted parity check: ten base fits.
Ten saved-head prediction checks. Other parsing/audit CPU time is not separately
metered. **0 GPU hours, 0 paid API calls, 0 Qwen3-14B predictions/tokens**.

No new TARGET209 inference, candidate CSV or Kaggle submission was made.
Incumbent test-label changes: **0**; certified retrieval changes: **0/78**.
C CSV SHA256:
`8ab7c5dc291cd9d1223283245fb62130b03bf728f764c5eeedf9d2915153e2a8`.
Its schema, 209 IDs and all 78 retrieval labels have been checked unchanged.

`EXECUTION_HANDOFF.md` and the Kaggle package contain complete launch, output
collection and CPU-evaluation commands. Return the inference directory to RS.
If the selected configuration is infeasible, stop without trying another model.
If the measured scientific gates fail, preserve C and close this challenger.

The primary question remains unanswered: deeper linguistic understanding is
worth this one bounded test, but there is currently no evidence that it closes
any of the 0.09547 public-score gap to the supplied leader score. No private
performance prediction or hidden-label inference is warranted.
