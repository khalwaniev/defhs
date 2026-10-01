# RS-DEFHS-SYSTEM-DESIGN-001 — EXPERIMENT LADDER

## Purpose

This is the ordered implementation program for Layer 3 after Strategic Scientist
integration and Astra review.

The ladder is **decision-value ordered**. It is not permission to run every
stage. Each stage has an explicit stopping rule, and later stages are entered only
when earlier evidence makes them capable of changing the final system.

Protected validation remains untouched until a final candidate is frozen and its
use is explicitly authorized.

---

## Global execution contract

For every model/head/pooling candidate retain:

- immutable model/checkpoint revision and license evidence;
- fold assignment authority;
- configuration and random seed;
- OOF logits and class probabilities when available;
- hard OOF prediction;
- per-fold macro-F1;
- aggregate V-B macro-F1;
- per-class F1;
- confusion matrix;
- V-A secondary result;
- inference output for the 209 test clips when appropriate;
- wall-clock / accelerator / peak-memory record;
- failure or exception log.

For ensemble-worthy candidates also retain:

- pairwise error correlation;
- probability/logit correlation;
- disagreement matrix;
- per-class complementarity;
- oracle-union headroom;
- marginal blend gain;
- ensemble ablation.

Never compare models using different validation authorities.

---

## STAGE 0 — execution legality and reproducibility gate

### Question

Can the intended pretrained weights actually be used reproducibly under the
competition and source terms?

### Work

Resolve, for each model before any expensive run:

1. exact checkpoint identifier and immutable revision;
2. weight license / terms;
3. code license where relevant;
4. whether the competition permits the pretrained asset;
5. deterministic preprocessing requirements;
6. supported sample rate and waveform normalization.

Priority assets:
- selected emotion2vec checkpoint;
- Vesper-4 checkpoint;
- WavLM-large;
- XLS-R-300m.

### Compute

CPU / network metadata inspection only. No model benchmark.

### Promote

Only assets with a sufficiently resolved execution authority enter Stage 1.

### Kill / defer

Any asset with unresolved permission or irreproducible floating revision is
deferred rather than silently substituted.

### Stop condition

If both emotion-specialized lanes cannot clear this gate, return to SS because
the intended architecture has materially changed.

---

## STAGE 1 — common frozen-representation scaffold

### Question

Can all selected representations be compared under an identical small-N
downstream protocol?

### Work

Build one fold-faithful extraction/evaluation scaffold:

- 16 kHz canonical audio;
- fixed V-B folds;
- V-A secondary folds;
- no retrieval mixing into V-B;
- cache frozen per-frame or per-layer representations;
- common mean+std pooling path;
- common L2 multinomial logistic head;
- common RBF-SVM head where feasible;
- fold-internal probability calibration if RBF probabilities are exported;
- deterministic seeds.

Do not tune a model here. This stage exists to make subsequent comparisons
meaningful.

### Compute

CPU for heads/reporting; one short GPU extraction pass per encoder when needed.
Prefer T4 for extraction. Cache once and reuse.

### Promote

Scaffold reproduces deterministic fold membership and emits the full reporting
contract.

### Kill

Any representation implementation that cannot produce fold-aligned,
reproducible OOF output is not used downstream.

---

## STAGE 2 — primary frozen emotion-specialized screen

Run in parallel across the two available GPU notebook slots if convenient.

### 2A — emotion2vec-family

Test one execution-authorized base candidate first.

Bounded representation/head variants:
- final-layer mean+std + L2 logistic;
- final-layer mean+std + RBF SVM;
- scalar learned layer mixture + simple head only if the checkpoint/API permits
  a clean reproducible implementation.

Do not benchmark many emotion2vec variants. A second within-family checkpoint is
allowed only if it answers a specific capacity/supervision question created by
the first result.

### 2B — Vesper-4

Use the exact snapshot semantics:
- frozen upstream;
- last layer versus trainable scalar layer mixture;
- mean or mean+std pooling;
- simple head.

Vesper-12 is **not automatic**. Escalate only if Vesper-4 is competitive and the
result plausibly indicates capacity headroom.

### Compute

One T4 per lane is appropriate. The expensive operation is frozen extraction;
heads are CPU-cheap. Dataset size is small, so avoid repeated encoder passes.

### Decision outputs

For each lane:
- V-B aggregate/folds/per-class;
- V-A secondary result;
- happy confusion profile;
- comparison to FULL_RBF_SVM;
- pairwise error/probability relationship between the two neural lanes and the
  legacy acoustic anchor.

### Promote

A lane is promoted if either:
1. it shows a robust standalone improvement whose fold/per-class pattern is
   credible relative to observed validation variability; or
2. it is slightly weaker standalone but demonstrates a clearly positive,
   held-out marginal blend contribution.

### Kill

Kill a lane if:
- it is materially weaker without a compensating diversity benefit;
- gains are isolated to one fold or one dependency stratum;
- it is nearly prediction-identical to a stronger lane;
- results depend on an unstable high-capacity head.

### Stage stop condition

If one emotion-specialized lane dominates both standalone and complementarity,
do not keep the other merely for model count.

---

## STAGE 3 — generic/multilingual SSL discriminator

### Question

After emotion-specialized representations, does one general SSL representation
add enough orthogonal information to justify its compute and ensemble slot?

### Candidates

Exactly two:
- WavLM-large;
- XLS-R-300m.

Use the same frozen protocol as Stage 2.

### Rationale

WavLM has stronger direct external SER evidence but shares lineage with Vesper.
XLS-R offers a stronger multilingual/diversity hypothesis but weaker direct SER
evidence. This is a discriminator, not a zoo.

### Compute

Prefer parallel frozen extraction on two T4s. Reuse cached representations for
all heads.

### Promote

Keep **at most one** candidate if it:
- is competitive enough to be credible; and
- contributes held-out ensemble gain beyond the selected emotion-specialized
  lanes.

### Kill

If both are redundant or weak, final architecture remains emotion-specialized
plus the acoustic diversity anchor. Do not replace the failed screen with
HuBERT/W2V2/data2vec/UniSpeech/MMS without new evidence and SS authorization.

---

## STAGE 4 — first ensemble decision

### Inputs

Only promoted OOF lanes:
- emotion-specialized winner(s);
- optional generic/multilingual survivor;
- existing FULL_RBF_SVM acoustic anchor;
- existing eGeMAPS lane as a cheap conditional test.

### Procedure

1. Calculate pairwise OOF diagnostics.
2. Evaluate equal-weight probability average.
3. If unequal weights could matter, use only a coarse nonnegative simplex.
4. Estimate weight-selection generalization by five-way
   **leave-one-V-B-fold-out meta-validation**:
   - choose blend on four folds;
   - score the fifth;
   - rotate.
5. Repeat with one-lane-at-a-time ablations.

Do not train a meta-neural-network or unrestricted multinomial stacker.

### eGeMAPS gate

Because eGeMAPS is weak alone, test only:
- core ensemble;
- core + small eGeMAPS blend weight.

If held-out meta-fold gain is absent or unstable, permanently remove eGeMAPS.

### Compute

CPU only once probabilities/logits exist.

### Promote

Select the smallest ensemble whose held-out meta-fold results demonstrate a
credible, repeatable advantage.

### Kill

Remove any member whose deletion is neutral or beneficial.

### Stop condition

If a two-lane ensemble already captures essentially all robust gain, do not
force a third lane.

---

## STAGE 5 — transcript legitimacy gate

This stage is conditional. It can run after the first strong audio core exists,
because its main question is *incremental* signal.

### Hypothesis

ASR text contains genuine emotion-relevant semantics that complement prosody,
rather than merely identifying repeated prompts / dependency groups.

### Cheapest test

Use only existing ASR transcripts:

- word and character TF-IDF;
- strongly regularized multinomial logistic regression;
- fixed V-B folds;
- no expensive language model.

### Required dependency controls

Report:
- all V-B rows;
- transcript-cluster singleton rows;
- non-singleton rows;
- rows without a close transcript neighbor;
- prompt/dependency-control performance generated fold-safely;
- audio-core + text versus audio-core alone in those strata.

The validation folds remain unchanged; these are diagnostics, not a new primary
validation design.

### Promote

Promote a transcript lane only if:
- it adds held-out blend value to the audio core;
- the gain remains present beyond repeated/near-repeated prompt structure;
- the effect is not driven solely by mixed train/test text clusters.

If that passes, a frozen text encoder may be tested as a single upgrade.

### Kill

Kill the lane if its apparent benefit disappears on transcript singletons /
dependency-controlled strata.

### Compute

Initial gate CPU only. Frozen text encoder, if earned, can use one GPU extraction
pass.

---

## STAGE 6 — pooling upgrade

Enter only for the strongest one or two frozen neural representations.

### Question

Does selective temporal weighting capture emotion-bearing frames better than
simple summary statistics without overfitting 826 labels?

### Compare

- incumbent mean+std;
- one simple attentive-statistics pooling module.

No multi-query/multi-head sweep.

### Evaluation

Fit strictly within training folds. Compare V-B folds, per-class F1, and ensemble
marginal value.

### Promote

Only a stable held-out gain that survives ensemble re-evaluation.

### Kill

Any gain concentrated in one fold, any strong train/validation divergence, or a
pooling module that becomes redundant once blended.

### Compute

Single T4/P100 training is sufficient; use one candidate encoder at a time.

---

## STAGE 7 — PEFT trigger and one adaptation experiment

This stage is **not scheduled by default**.

### Entry conditions

All must be true:

- a single frozen encoder is clearly selected;
- its representation is competitive under V-B;
- head/layer-weight/pooling experiments have plateaued;
- a consistent residual failure pattern remains;
- external evidence provides a plausible adaptation mechanism;
- license/revision authority is complete;
- the potential gain is scientifically meaningful relative to observed
  fold/seed model-selection variability.

### Experiment

One bounded adaptation family:

- keep feature extractor / lower encoder frozen;
- adapt upper encoder blocks or upper-attention LoRA/adapter parameters;
- keep layer weights, pooling, and head trainable;
- early stopping entirely within each training fold.

Do not run full fine-tuning.
Do not launch a LoRA-rank sweep.

### Loss

Start ordinary CE. Focal/class-weighted loss is not bundled into the adaptation
experiment because DEFHS labels are nearly balanced; combining multiple changes
would destroy attribution.

### Augmentation

Default none. If needed after the first adaptation result, one separate bounded
emotion-preserving augmentation ablation may test small gain variation or modest
additive noise.

### Promote

PEFT must improve the selected frozen parent in a fold-stable way and retain or
increase ensemble marginal value. V-A should not show a contradictory collapse.

### Kill

If the effect is noisy, one-fold-driven, or loses diversity while adding little
standalone value, return to frozen architecture.

---

## STAGE 8 — macro-F1 decision calibration

Enter only after model membership is frozen.

### Baseline

Posterior/logit argmax.

### Optional test

A four-class additive logit-offset vector with strong regularization toward zero.

Select offsets inside leave-one-V-B-fold-out meta-validation. Do not tune on all
OOF rows and report the same OOF score.

### Promote

Only if held-out meta-fold improvements are coherent and V-A is directionally
consistent.

### Kill

If offsets vary strongly by held-out fold, retain argmax.

---

## STAGE 9 — finalist stress package

Only finalists receive:

- V-A secondary competition-mimic evaluation;
- V-D recording/source-format diagnostic;
- Q128 / Q960 quantization/source diagnostics where relevant;
- correlated-allocation envelope sensitivity;
- retrieval-aware pipeline evaluation on V-A;
- final ensemble ablations.

These do not replace V-B as primary model-selection authority.

### Protected confirmation

Protected seed 20261001 remains untouched until:
1. the complete system is locked;
2. no further ordinary model selection is planned;
3. SS explicitly authorizes the confirmation query.

A protected result must not trigger iterative retuning.

---

## Compute sequencing

### CPU

Use CPU for:
- license/revision audit;
- logistic/RBF heads on cached embeddings;
- text TF-IDF gate;
- OOF diagnostics;
- ensemble meta-validation;
- decision-offset meta-validation;
- final reporting.

### 2× T4

Preferred for:
- parallel frozen emotion2vec and Vesper extraction;
- parallel WavLM/XLS-R frozen extraction;
- later one-lane PEFT/pooling experiments if earned.

### 1× P100

Acceptable for a single larger extraction/adaptation job when memory or kernel
support is preferable, but there is no scientific reason to consume it before
the frozen screen.

### Quota principle

Representation extraction is cached once. No repeated GPU pass solely to vary a
CPU head.

---

## Global stopping conditions

Stop the program early when any of these becomes true:

1. two non-redundant frozen lanes form a stable ensemble and every added lane
   fails marginal-gain ablation;
2. the generic SSL discriminator adds no value after emotion-specialized lanes;
3. text/eGeMAPS controls fail;
4. PEFT fails its first bounded experiment;
5. remaining ideas require changing frozen validation or relying on unresolved
   licensing/provenance.

The correct final system can therefore be substantially simpler than this ladder.
The ladder exists to kill hypotheses, not to guarantee that later stages run.
