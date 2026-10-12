# Frozen experiment: localized emotion2vec evidence

Mission RS-DEFHS-FINAL-FIRST-PLACE-BREAKTHROUGH-001. Parent
6b23148e21b75d10611fbb4deb2d6811b26221c3, preserving E production authority
a6676d9777ace9e9746802b3256cd3eb52dd7339. New branch
rs/final-first-place-breakthrough-001-astra. This protocol precedes any new
temporal validation results. System E remains unchanged.

## Observation, alternatives, and discriminating test

Authenticated E: 102/826 errors, 74 true-class-second, 65 acoustic disagreement;
50 errors wrong in both incumbent acoustic experts and 19 wrong in all five
experts. Existing E2V alone correctly labels 27 E errors; XLS-R 29. Those are
oracle counts, not usable routing rules. Global E2V mean/std lose the allocation
of features to contiguous utterance regions. An emotional burst can be diluted
by neutral frames; alternatively all useful emotion may already be distributed
through contextual encoder frames, or errors may be ambiguous/noisy labels.

Select ONE mechanism: fixed local pooling interpreted by the existing E2V
classifier. No new pretrained model or acoustic fine-tuning. Three contiguous
equal-duration frame intervals produce three 1536-dimensional mean/std vectors.
For each proper training-side E2V head, compute its four softmax outputs on each
interval. Append the four interval-wise means and four interval-wise maxima
to unchanged E's 23 inputs: one 31-input, unscaled L2 C=1 logistic meta-model.
These local softmax values are features, NOT demonstrated calibrated local
emotion posteriors. The maximum is not renormalized. Class order stays
angry,happy,neutral,sad. No confidence threshold, window-size search or seed search.

Mathematically, global variance conflates within-region variance and variance
of region means. Applying a nonlinear classifier separately before aggregation
can distinguish sequences sharing identical global moments. This does not
prove emotional causality: phonetic content and silence are competing causes.

One matched negative control replaces contiguous windows by frame indices
0::3,1::3,2::3, distributed over the full utterance. It uses identical heads,
feature dimension and meta regularization. This control tests whether any gain
requires locality rather than generic nonlinear resampling. It is a fixed
mechanistic control, never an alternative candidate selected for deployment.

Previous learned attention was a permutation-invariant weighted global
mean/std mechanism: chosen epoch zero in 4/5 PRIMARY folds; standalone gain
0.0010479909 and system loss -0.0062182740. It was rejected. The present test
requires local grouping and adds train-only expert summaries to E; it does not
resurrect that attention model. The weak WavLM F fusion (18 corrections/18
breakages) is rejected. AST, Pocket-Mimi, emotion2vec+, source-gating and encoder
adaptation failures remain closed. FairHindiSER is implementation-blocked,
not scientifically falsified. Sol's continuous semantic likelihood experiment
is independently owned and is neither rerun nor modified here.

## Exact inference and fitting contract

Use original emotion2vec_base_frames.h5, SHA256
b292f8e18193f73d86fb518d4418e067f6aa2d52ef5786b3afdbfb5b9e20e368,
459591204 bytes, Drive ID 1YNdFI8sipsu_mbr8yL-q5ZEDaJXRZSsb.
Encoder iic/emotion2vec_base@v2.0.4, weight SHA256
4f14ddf7ba394bcafdd4bff6ae0f24ab2e4134260d4dd42c58ea791a201b02dd.
FunASR extraction revision 4a84879ae8ca4d2430953b11c49d609217d93988.
No encoder execution is needed. Every training row must reproduce the original
float32 mean/std cache bit-for-bit before local features are accepted.
For T frames, boundaries are floor(j*T/3), j=0,1,2,3; population std ddof=0.
The reducer reads only 826 training IDs, not their labels or test frames.
Contextual frame embeddings were computed from whole clips: the test concerns
pooling localization, not causally isolated waveform crops.

Frozen PRIMARY_CV SHA256
87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b.
Within outer k, each meta-training block j uses acoustic heads fit only on
folds outside {k,j}. Both acoustic scalers are fit on that same training subset.
E2V local and interleaved summaries use that very same E2V inner head.
For heldout outer k, use the authentic saved E2V head for all window summaries
and the authenticated original acoustic outer probabilities for E inputs.
Fit each meta-model on outer training labels only. Save fit/predict ID hashes.
Original 23-input E must reproduce all 826 labels and max probability error
<1e-8 before challenger evaluation. Do not relax this check after a failure.
The attached independent D replay validates D only, not this challenger.

## Falsification and promotion (no post-result changes)

Execute the one candidate and one locality control under the same five folds.
Report candidate and control oracle corrections/breakages, including whether
local window maxima recover any of the 19 all-expert failures. These descriptive
counts never authorize a row override. A model screen is not an optimization loop.

Primary GO requires ALL:
- Candidate pooled macro-F1 gain versus unchanged E >=0.005.
- Positive gain in at least 4/5 original folds and every leave-one-fold-out pool.
- No class F1 deterioration exceeding 0.02; HARD316 nonnegative.
- Duplicate-singleton and prompt-singleton gains nonnegative.
- Dependency-aware simultaneous 95% max-t lower bound for candidate-minus-E >0
  (2,000 exponential bootstrap weights, 656 duplicate/prompt components,
  seed 20260930; candidate and control contrasts included).
- Candidate pooled gain over the fixed interleaved control >0. This supports
  locality; it does not identify a causal speech-emotion mechanism.
- Every Q stratum with >=5 per class has gain >=-0.02 versus E, including Q960/606.
- Q960/606 relative to historical D >=-0.02, so the original E gate failure is
  not silently inherited as certification of a newly promoted model.

If primary fails: REJECT, no tuning, no further GPU or TARGET209 work.
If primary passes: pending new V-A retrieval/non-retrieval, V-D cross-format,
and original 616-scenario private-allocation stress evaluation; none is inferred
from E's historical results. Required non-retrieval/directional gains >=0,
minimum scenario mean private gain >0, maximum reversal probability <=0.10,
and no loss in supported Q strata beyond the above tolerance. Only then return
to SS for promotion and exact TARGET209 production. Preserve all 78 overrides.
No Kaggle submission without SS authorization. Many prior PRIMARY experiments
make confidence intervals conditional/exploratory, not independent confirmation.

## Feasibility and deadline

2026-10-12 09:15 UTC start evidence. Deadline supplied by SS is 18:30 UTC,
production priority 14:00 UTC. Live Kaggle quota/submission selection is not
authenticated here; no claim of current quota or final selection.
Eight CPU cores / 8 GiB environment, no torch/GPU necessary for this mechanism.
Original h5 exists in Drive, but connected download rejects it at 459591204
bytes against a 268435456-byte limit. This is EXECUTION_BLOCKED pending cache
access, not negative model evidence. Complete WSL/Kaggle CPU reducer and
evaluator will be delivered. No broad literature phase or GPU run is justified.
