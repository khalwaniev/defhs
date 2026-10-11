# Frozen final semantic challenger protocol

Mission: RS-DEFHS-FINAL-SEMANTIC-CHALLENGER-001. Parent authority:
`021d060bc9288f4d2c2d14c37022e2898aed1d01`.
Frozen before receiving any Qwen3-14B prediction or evaluation. `WORKFLOW.md`
was read completely. One model, one prompt, one fusion; no parameter search.

## Authority and access

System C remains the incumbent. Public score **0.86997** and deadline
**2026-10-13 01:30 WIB = 2026-10-12 18:30 UTC** are supplied as verified by SS/user.
They are not claimed as independently authenticated Kaggle account observations.
Preserve C CSV SHA256
`8ab7c5dc291cd9d1223283245fb62130b03bf728f764c5eeedf9d2915153e2a8` and all 78
retrieval decisions. No protected validation is read, even after a pass. No
leaderboard-derived thresholds, hidden-label inference, or competition submission.

## One model and fixed semantic experiment

Qwen/Qwen3-14B, revision `40c069824f4251a91eefaf281ebe4c544efd3e18`.
NF4 double quantization with FP16 computation, non-thinking, exact-label greedy
decoding. The **historical Qwen3-8B prompt is unchanged**, including its `unclear`
abstention. Prompt SHA256
`d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f`.
One pass per exact unique string; repeat only the four pilot strings to verify
execution repeatability. Only transcript text enters the model. IDs, labels,
folds, waveform predictions and test transcripts are absent from model messages.
The sealed Kaggle package includes only 826 training rows / 711 unique strings.
Batch 4 and fixed 512-token padding differ from the historical batch-16 runtime;
benchmark comparisons therefore do not isolate parameter count as a causal effect.

Feasibility requires dual T4, no CPU/disk model offload, at least 2 GiB GPU memory
headroom, a measured warm-batch forecast with 2x margin <=2h, and at least six
hours left after inference for evaluation. Download, load, packages, peaks and
runtime are logged. Failure is an execution result, not negative scientific evidence.
No substitute model/configuration is automatically tried.

## Semantic evaluation before fusion

Join all 826 outputs by exact ID; no missing, duplicate or out-of-schema rows.
Check model, input, prompt, checkpoint and output checksums and pilot feasibility.
Four-class macro-F1 always averages angry/happy/neutral/sad: `unclear` counts as
a false negative, never an additional scored class. Also report coverage,
covered-only performance, all precision/recall/F1 values, confusion, five fold
scores, new corrections and breakages, and exact row IDs.

Report new correct rows unavailable to Qwen3-8B and separately unavailable to
both Qwen3-8B and C. Report neutral/sad, waveform disagreement and the **existing
316-row OOF hard surrogate**. Its historical confidence/margin constants merely
define a frozen diagnostic cohort; they never route challenger predictions.
The existing 60-row TARGET209 HARD cohort is reserved for target comparison
after passage, with no test-label accuracy claims.

Complementarity screen, all required: full four-class macro-F1 exceeds the old
Qwen value; at least 10 newly correct rows unavailable to old Qwen spanning at
least three classes; at least five corrections unavailable to both old Qwen and
C, including at least one neutral/sad correction. These operational minimums
are fixed before new outputs and cannot be relaxed to rescue a result. They
justify testing fusion; they do not establish deployable gain.

## One nested fusion

Features: 4 E2V probabilities + 4 XLS-R probabilities + 5 old-Qwen one-hot states
+ 5 new-Qwen one-hot states = 18. No confidence routing or tunable threshold.
Unweighted LogisticRegression L2 C=1, lbfgs, intercept, max_iter=5000,
random_state=20261001; no additional scaling of the meta inputs.

Five PRIMARY_CV memberships remain byte-identical. For outer fold f, form each
of the four inner blocks using base heads trained only on the other three
original blocks. StandardScaler is fitted only on that inner training subset.
Fit the meta head on these inner-OOF inputs and labels from outer-training only.
Predict outer f once using its authenticated saved waveform probabilities.
Never fit a meta head on ordinary OOF features whose generating model saw f.

C replay uses the accepted 13-input recipe and the same inner cache. It matches
the published pooled, five-fold, confusion, hard-cohort and corrections evidence.
Historical preserved heads are verified separately. Fresh sklearn 1.8 base-head
refits can differ from historical 1.7.2; the authentic probabilities, not fresh
refits, supply PRIMARY_CV outer features for **both** C and the challenger.

PRIMARY_CV gate, all required:
- pooled gain >=0.005;
- strictly positive gain in at least 4/5 folds;
- no per-class F1 loss >0.02;
- nonnegative gain in the fixed hard cohort;
- paired duplicate/prompt-component multiplier-bootstrap 95% lower bound >0;
- gain stays positive after deleting any one original fold.

## Candidate-specific robustness

Only after the primary gate, refit the unchanged C/challenger recipes with
nested fitting under frozen V-A. Apply retrieval only from unanimous labels in
outer-training families under the certified duplicate graph; report SER,
retrieval pipeline and non-retrieval separately. No C certification is borrowed.

Run both int16->int32 and int32->int16 stresses. For each, inner base/meta fits
use only the source-format training rows, subdivided by the original fold blocks.
Report frozen V-Q remainder strata: Q128 {0,43,86,30,94,OTHER}, Q960
{384,192,576,606,926,OTHER}, plus format, historical hard, non-retrieval, short/long
duration quintiles and prompt-family-beyond-duplicate cohorts.

Private-allocation sensitivity independently evaluates new VB SER and V-A
pipeline predictions. Use 250 class-stratified allocations per scenario, private
fractions {0.2,0.3,0.4,0.5}, and frozen mild/moderate subgroup odds
{0.5,2/3,1.5,2}. Baseline odds=1. Report both private macro-F1 deltas and
0.4*public+0.6*private deltas, intervals and reversal rates. These are explicit
scenarios, not estimates of hidden membership. The leaderboard is never fitted.
This scoped stress does not claim coverage of every possible latent shift.

Stress gate: V-A pipeline and non-retrieval gains nonnegative; neither V-D
direction loses >0.02; no V-Q/diagnostic stratum with >=5 examples in every class
loses >0.02; all tested plausible allocations have nonnegative mean private and
weighted gains, with weighted ranking reversal <=20%. Tiny strata are reported
as uncertain and cannot certify robustness.

## TARGET209 and SS

Only a pass across semantic, primary and new stress evidence permits preparing
the separate target inference stage. Reuse the same frozen model/prompt/runtime,
infer the exact 209 IDs and unchanged raw transcripts, and retain all 78 certified
retrieval labels. Report each change from C, including the existing HARD cohort.
Check original `Id,emotion` schema, order, 209 unique IDs, allowed labels and
SHA256. Return one candidate and the evidence to SS. **Do not submit**.

At the current handoff, Qwen3-14B inference has not executed, none of the
scientific challenger gates has been passed, and target inference is not open.
