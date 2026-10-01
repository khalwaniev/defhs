# RS-DEFHS-SYSTEM-DESIGN-001 — SYSTEM DESIGN

## Executive decision

DEFHS should not begin with a broad foundation-model benchmark or full fine-tuning.

The strongest evidence-supported program is a **frozen-first, representation-diverse SER
system with a permanently separate deterministic retrieval lane**:

```text
certified duplicate retrieval?
        |
        +-- yes --> unanimous certified retrieved label
        |
        +-- no --> frozen emotion-specialized core
                     |-- emotion2vec-family representation
                     |-- Vesper-family representation
                   + one orthogonal generic/multilingual SSL finalist
                   + legacy FULL_RBF_SVM acoustic anchor if complementary
                         |
                         v
                   simple regularized probability/logit blend
                         |
                         v
                   ordinary argmax
                   [only if justified: strongly regularized class-logit offsets]
```

The working hypothesis is that **emotion specialization is more valuable than
language specialization for the first core**, while one generic/multilingual lane
is retained specifically for error diversity. Adaptation is a later conditional
experiment, not the default architecture.

No protected-fold evidence was used.

---

## 1. Evidence synthesis

### DIRECT_DEFHS

- 826 labeled train clips and 209 test clips make variance control central.
- V-B is the frozen primary duplicate-family-safe model/representation selection
  authority. V-A remains secondary competition-mimic / retrieval-aware evidence.
- FULL_RBF_SVM is the current cheap reference:
  - V-B macro-F1 ~0.63103;
  - V-A SER macro-F1 ~0.69399;
  - V-A retrieval-aware pipeline macro-F1 ~0.70967.
- V-B class support is nearly balanced:
  angry 205, happy 192, neutral 217, sad 212.
  The weak happy F1 (~0.5823 for FULL_RBF_SVM) therefore cannot be explained
  simply as a rare-class problem.
- Validation seed/fold variation is material. A candidate must therefore win by
  a pattern that survives folds and relevant secondary views, not by a tiny
  single-score increase.
- The fixed retrieval lane is extremely accurate in its validation construction
  and covers a substantial subset of V-A. It should remain a certified hard
  override, not be blurred into general SER fitting.
- ASR transcripts contain substantial repeated/near-repeated structure:
  338 exact repeated transcript rows; at similarity 0.90, 367 clips are in
  non-singleton clusters and 61 mixed train/test non-singleton clusters exist.
  Transcript signal is therefore confounded by prompt/dependency structure.
- eGeMAPS is weak standalone (V-B ~0.56015) but is cheap and has little evidence
  of simple train/test discrimination (AUC ~0.4764). It can only survive as a
  diversity lane if its *marginal* ensemble value is positive.
- Existing hard-prediction OOF diagnostics show meaningful disagreement among
  the cheap baselines, but those oracle-union headrooms are not achievable blend
  evidence. Future foundation lanes must retain probabilities/logits so marginal
  blend value can be measured directly.
- There is moderate nonlinear representation-dependent train/test shift after
  duplicate removal. Robust superiority matters more than exploiting a guessed
  hidden domain.

### STRONG / TRANSFERABLE EXTERNAL EVIDENCE

#### emotion2vec

The acquired emotion2vec paper directly supports frozen emotion-specialized
representations: a frozen upstream with a small downstream head performs strongly
on SER and the model generalizes across multiple unseen languages. In the paper's
cross-language experiments, emotion2vec consistently exceeds general SSL
baselines including data2vec 2.0 and WavLM variants on several non-English SER
datasets. This is not Hindi/DEFHS evidence, but it is strong transferable evidence
that emotion specialization can transfer across language boundaries.

#### Vesper

The acquired Vesper paper and exact repository snapshot show a compact
WavLM-derived emotion-specific encoder. Its downstream recipe is especially
appropriate for DEFHS: frozen upstream, a trainable scalar weighted sum of layer
representations, simple temporal mean pooling, and a small projection/classifier.
The paper reports gains or parity versus larger WavLM variants on several SER
benchmarks. Vesper therefore offers an implementation-ready emotion-specific lane
with a different specialization mechanism from emotion2vec.

#### General SSL and adaptation

The acquired 2025 SSL SER benchmark finds WavLM-large stronger than the tested
Wav2Vec2/HuBERT/Whisper frozen alternatives in its setting. It also reports that
naive full fine-tuning often gives little gain or degrades performance, while
selective upper-layer fine-tuning plus attentive pooling can help on a much larger
dataset. Critically, a WavLM+Wav2Vec2 ensemble was worse than its constituents,
warning against model-count-based ensembling.

The acquired cross-lingual PEFT paper shows that PEFT is context-dependent:
plain LoRA can hurt, while combinations of adapters/gating can help in some
settings. Thus PEFT is plausible but not automatically beneficial.

#### Pooling

The acquired attentive-pooling evidence supports statistics-aware temporal
aggregation, but also shows that increasing attention complexity can reduce
generalization. With only 826 labels, the DEFHS order should be:
mean / mean+std first, then at most a simple attentive-statistics pooling upgrade
on a selected representation.

#### SenseVoice and Whisper

SenseVoice-Small is not a Hindi model in the acquired report; its released small
variant supports Chinese, Cantonese, English, Japanese, and Korean. Its SER
supervision is also partly derived from emotion2vec pseudo-labeling, so it is not
an obviously orthogonal emotion lane. Checkpoint licensing remains unresolved.

Whisper evidence is mixed: CAMuLeNet reports strong Whisper-Medium transfer on
its own BhavVani dataset, but that dataset's relationship to competition
SRCASW-BhavVaani is explicitly unresolved; another acquired SSL benchmark finds
Whisper substantially weaker for audio-only SER. Whisper therefore does not earn
a first-wave direct SER lane.

---

## 2. Selected architecture

### FIXED RETRIEVAL LANE

**Rule:** for a test clip belonging to a frozen, certified cross-split duplicate
group with a unanimous observed train label, use that label as a deterministic
hard override.

Do not:
- learn a confidence gate over retrieval;
- extrapolate retrieval to weaker near-neighbor evidence;
- mix retrieval-covered rows into V-B representation selection;
- expand the duplicate graph during modeling.

V-A remains the place where retrieval-aware pipeline behavior is evaluated.

### CORE LANE A — emotion2vec-family frozen representation

**Role:** primary candidate core.

**Mechanism:** emotion-specialized self-supervised representation with both
utterance- and frame-level emotion pretraining objectives.

**First implementation:** frozen encoder; cache frame representations; compare
a deliberately small aggregation set:
1. final-layer mean+std;
2. trainable scalar layer mixture + mean+std if the implementation supports it
   reproducibly.

Downstream heads:
- L2 multinomial logistic regression;
- RBF SVM as a small-N nonlinear head, with fold-internal calibration if
  probabilities are required for ensembling.

Do not treat multiple emotion2vec checkpoints as independent ensemble lanes.
Within-family variants are a representation screen; only materially
non-redundant winners survive.

**Hard gate:** exact checkpoint revision, license, and competition compatibility
must be resolved before execution.

### CORE LANE B — Vesper frozen representation

**Role:** second emotion-specialized core with a distinct training mechanism.

Start with **Vesper-4** because it is compact and its paper demonstrates that the
compressed emotion-specific representation can exceed WavLM Base. The exact
snapshot already implements frozen-upstream scalar layer weighting.

Escalate to Vesper-12 only if Vesper-4 is competitive but clearly capacity-limited,
or if a cheap frozen comparison can change the architecture decision.

Use the same downstream reporting contract as Lane A so the OOF predictions are
directly comparable.

**Hard gate:** repository code licensing is not equivalent to checkpoint-weight
permission. Verify the actual checkpoint terms and immutable revision before use.

### CORE/DIVERSITY DISCRIMINATOR — one generic or multilingual SSL survivor

Do **not** run a zoo.

Screen only:
- **WavLM-large** for strong general SSL SER evidence;
- **XLS-R-300m** for multilingual/architectural diversity.

The purpose is not to keep both. One survives only if it provides either:
1. competitive V-B standalone strength; or
2. convincing marginal ensemble gain against the two emotion-specialized lanes.

This screen answers whether generic/multilingual information contributes anything
after emotion specialization.

WavLM has a strength advantage in external evidence but is lineage-related to
Vesper, increasing redundancy risk. XLS-R has a stronger diversity argument but
less direct SER evidence. That is exactly why a two-candidate discriminator is
worth one bounded experiment.

### DIVERSITY LANE — existing FULL_RBF_SVM acoustic anchor

Retain the existing FULL_RBF_SVM predictions as a zero-new-GPU-cost diversity
anchor until foundation OOF evidence proves it redundant.

It is not assumed to remain the strongest standalone model. Its value is that it
is DIRECT_DEFHS, cheap, and represents a fundamentally different handcrafted /
summary-acoustic bias.

### OPTIONAL DIVERSITY LANE — eGeMAPS

Do not train another large eGeMAPS program. Use the existing lane only in
post-core complementarity analysis.

Promote only if its OOF errors are sufficiently different and a simple
regularized blend improves held-out meta-fold performance without a class-specific
collapse. Otherwise kill it.

### CONDITIONAL HIGH-RISK LANE — transcript semantics

The transcript lane is **not** a core model.

Cheap first test:
- existing ASR transcripts only;
- fold-safe word/character TF-IDF + strongly regularized multinomial logistic
  regression;
- no large text model required for the first gate.

Required controls:
1. evaluate on the frozen V-B folds without changing them;
2. report performance on prompt-cluster singletons versus non-singletons;
3. compare against a fold-safe prompt/dependency control;
4. measure whether any audio+text blend gain persists on clips without close
   transcript neighbors;
5. inspect per-class gains, especially happy.

Promote text only if its *incremental* value persists beyond repeated-prompt
structure. If signal is concentrated in duplicated/near-duplicated prompt groups,
classify it as dependency exploitation and do not promote it as a general semantic
lane.

Only after passing this gate should a frozen text encoder be considered.

---

## 3. Layer use and pooling

### Layer use

Avoid high-dimensional concatenation of all hidden layers.

For each selected encoder, compare only:
- final representation;
- a trainable scalar mixture of layers with strong regularization / low parameter
  count.

For Vesper, the exact upstream code already provides a softmax scalar layer
mixture. For other encoders, implement the same conceptual form rather than a
large learned layer combiner.

### Temporal pooling

Order:
1. mean+std statistics pooling;
2. simple single-attention statistics pooling only if Stage 1 leaves clear
   headroom;
3. no multi-query / multi-head pooling search in the first program.

Short ~3-second clips do not justify a large temporal downstream network before
simple statistics have been tested.

---

## 4. Training policy

### Frozen versus PEFT versus full fine-tuning

**Default:** frozen.

PEFT is triggered only after:
- one encoder is clearly selected;
- its frozen representation is competitive under V-B;
- its head/pooling variants have plateaued;
- a stable, interpretable residual failure mode remains;
- the candidate's advantage is large enough to survive observed fold/seed
  variability;
- license/revision authority is complete.

If triggered, adapt the **upper encoder portion first**, keeping lower feature
extraction frozen. Prefer a single bounded LoRA/adapter or upper-block experiment
over a hyperparameter sweep.

**Full fine-tuning is rejected for the current program.**

### Loss and class handling

Start with ordinary unweighted cross-entropy / multinomial likelihood.

Do not import focal loss merely because it helped imbalanced external datasets.
DEFHS class supports are already close to balanced. Happy is weak despite that,
so the first explanation should be representation/decision geometry, not sampling
frequency.

Class weighting/focal loss may be reopened only if new foundation OOF evidence
shows a stable error-asymmetry that the representation itself does not address.

### Augmentation

No augmentation in the frozen representation screen.

If PEFT is triggered, allow only bounded operations with a plausible
emotion-preservation mechanism, e.g. modest additive noise or small gain
variation. Pitch shifting, aggressive time stretching, or broad speed
perturbation can alter prosody and should not be adopted without a specific
ablation.

### Pseudo-labeling

Rejected for the first system. Small-N, train/test shift, prompt repetition, and
retrieval dependence make self-training contamination risk too high relative to
the evidence.

---

## 5. Macro-F1 decision policy

Baseline decision rule: **argmax posterior/logit**.

Happy weakness does not justify hand-tuned happy thresholds.

Only after the model/ensemble is locked should Layer 3 test a four-parameter
class-logit offset vector with strong shrinkage toward zero. It must be selected
under leave-one-V-B-fold-out meta-validation, not optimized and evaluated on the
same 826 OOF predictions.

Promote only if the adjustment:
- improves held-out meta-fold macro-F1 consistently;
- does not rely on one class/fold reversal;
- remains directionally compatible with V-A.

Otherwise retain argmax.

---

## 6. Ensemble design

### Candidate count

The final ordinary SER ensemble should contain **two or at most three genuinely
different lanes**, not every candidate that scores well.

Likely final shapes:

```text
A. emotion2vec + Vesper
B. emotion2vec + Vesper + one generic/multilingual SSL
C. emotion2vec + one second neural lane + legacy RBF acoustic anchor
```

The exact membership is empirical.

### Weight selection

1. Begin with equal-weight probability averaging.
2. Measure pairwise:
   - hard-error correlation;
   - probability/logit correlation;
   - disagreements;
   - per-class complementarity;
   - oracle-union headroom;
   - marginal blend gain.
3. If unequal weights are justified, search only a low-dimensional nonnegative
   simplex / coarse grid.
4. Use **leave-one-V-B-fold-out meta-validation**:
   - choose weights on four folds;
   - evaluate on the fifth;
   - rotate across all five;
   - aggregate the held-out results.
5. Only if meta-validation demonstrates a stable benefit should final weights be
   fit on all V-B OOF rows.

No unconstrained stacking model, no learned high-dimensional meta-classifier.

V-A is a secondary corroboration view; correlated-allocation stress is applied
only to finalists where relevant.

---

## 7. Answers to the mission's critical design questions

1. **Frozen, PEFT, or full FT?** Frozen first. PEFT only after a specific
   evidence gate; full FT rejected now.
2. **Best 2–4 representation families?** emotion2vec; Vesper; one survivor of
   WavLM-large versus XLS-R-300m; legacy acoustic RBF retained as a diversity
   anchor, not a new foundation family.
3. **Emotion or Hindi specialization?** Emotion specialization first. Current
   evidence for cross-language emotion2vec transfer is stronger than evidence
   that Hindi-specific ASR representation is the best SER prior.
4. **Redundancy?** emotion2vec/data2vec are mechanistically close; Vesper/WavLM
   share lineage; SenseVoice SER supervision is partly emotion2vec-derived.
   Generic/multilingual XLS-R is the cleanest orthogonality screen.
5. **Layers?** Final layer versus scalar learned layer weighting; no broad layer
   concatenation.
6. **Pooling?** Mean+std first; simple attentive statistics conditional.
7. **Transcript lane?** Scientifically defensible only after prompt/dependency
   controls; otherwise conditional/rejected.
8. **eGeMAPS?** Diversity-only; standalone weakness precludes core status.
9. **PEFT trigger?** A selected competitive frozen encoder with stable residual
   error and plausible adaptation headroom beyond model-selection noise.
10. **What adapts first?** Upper encoder layers / upper-attention LoRA or adapter,
    with pooling/head and layer weights trainable; lower feature extractor frozen.
11. **Augmentation?** None initially; bounded noise/gain only if PEFT needs it.
12. **Happy?** Treat as a representation/decision failure, not class scarcity.
13. **Macro-F1?** Ordinary likelihood + argmax first; nested low-dimensional
    logit-offset search only after the ensemble is locked.
14. **Retrieval interaction?** Certified deterministic hard override only.
15. **Ensemble weights?** Equal first; then low-dimensional simplex weights
    validated by leave-one-fold-out meta-validation.
16. **Models not to run?** broad data2vec/HuBERT/W2V2/UniSpeech/MMS zoo,
    SenseVoice-Small, direct Whisper SER, duplicate emotion2vec variants as
    ensemble members, and high-dimensional fusion models.
17. **Smallest first ladder?** license/revision gate → emotion2vec + Vesper frozen
    screen → one WavLM/XLS-R discriminator → OOF blend analysis → conditional
    text/pooling → one PEFT experiment if earned.
18. **Astra bottleneck?** whether scarce adaptation compute should be spent on
    upper-layer PEFT of the strongest selected encoder, or whether DEFHS should
    remain a frozen multi-representation core and invest model capacity entirely
    in representation diversity.

---

## 8. Rejected / deferred ideas

### Rejected now

- full-model fine-tuning;
- high-dimensional OOF stacking;
- broad foundation-model zoo;
- pseudo-label/self-training;
- unverified external BhavVani ingestion;
- class-imbalance machinery as the default explanation for happy;
- retrieval confidence gating;
- public-LB-driven model selection.

### Deferred unless a preceding gate changes the decision

- SenseVoice-Small;
- direct Whisper SER adaptation;
- data2vec / HuBERT / Wav2Vec2 / UniSpeech-SAT / MMS as extra lanes;
- CAMuLeNet-style co-attention architecture;
- complex multi-head attentive pooling;
- aggressive waveform augmentation;
- frozen text foundation models.

---

## 9. Evidence boundaries

External SER numbers are **transferable evidence**, not DEFHS performance
predictions. In particular:

- BhavVani from Goel et al. is not assumed to be competition SRCASW-BhavVaani.
- Vesper / emotion2vec benchmark metrics and folds differ from DEFHS macro-F1
  authority.
- SenseVoice public availability does not resolve checkpoint permission.
- A model cannot enter execution until its checkpoint license, immutable revision,
  and competition external-data/model policy are resolved.

The protected seed remains confirmation-only and was not inspected in this
mission.
