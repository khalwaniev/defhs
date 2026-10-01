# RS-DEFHS-SYSTEM-DESIGN-001 — FINAL RETURN TO SS

## 1. VERIFIED STATE

Repository: `khalwaniev/defhs`

Active mission branch: `ss/evidence-synthesis-001`

Mission-start authority:
`bdf92643583331997dd8010ed017d7c482e421eb`

At mission start, `main` and the active branch were independently verified
identical: ahead 0 / behind 0.

Drive authorities verified:

- project root `/DEFHS/` —
  `1Spi0YOSIbOth6Av801b0w9zKbNAqle94`
- frozen evidence `/DEFHS/ds_validation_002/` —
  `1eVmuoGuCCh8k5zT2MacvM61QHrvHRS-P`
- knowledge warehouse `/DEFHS/knowledge/` —
  `1asWciARNwNE_OrL-_OmKWBxF3MF8uMeR`

Validation remains **PATCH_AND_FREEZE**:

- V-B primary;
- V-A secondary competition-mimic / retrieval-aware;
- V-D diagnostic;
- V-C rejected;
- Q128/Q960 diagnostic;
- correlated-allocation secondary finalist sensitivity;
- retrieval fixed and separate;
- protected seed 20261001 untouched / confirmation-only.

No validation redesign, protected candidate query, model benchmark, fine-tuning run,
or Kaggle submission was performed by Layer 1.

---

## 2. MOST IMPORTANT EXISTING EMPIRICAL FACTS

1. DEFHS has only 826 labeled training clips. Model-selection variance therefore
   matters at least as much as nominal capacity.
2. FULL_RBF_SVM is the current DIRECT_DEFHS cheap reference:
   V-B ~0.63103, V-A SER ~0.69399, V-A retrieval-aware ~0.70967.
3. The four V-B class supports are already close to balanced
   (205/192/217/212), yet happy F1 is weakest (~0.5823). Happy is therefore not
   primarily a rare-class problem.
4. Validation seed/fold variation is material; tiny isolated gains are not a
   credible promotion basis.
5. Retrieval is a high-value structural lane and should remain a certified
   deterministic override for frozen unanimous duplicate groups.
6. ASR text is strongly confounded by prompt/dependency repetition
   (338 exact repeated rows; substantial near-text clustering), so text must pass
   dependency controls before being called semantic signal.
7. eGeMAPS is weak standalone (V-B ~0.56015) but cheap and potentially
   complementary.
8. Moderate representation-dependent train/test shift remains after duplicate
   removal. Do not assume IID and do not invent a hidden domain.
9. emotion2vec supplies the strongest acquired external argument for
   cross-language frozen emotion specialization.
10. Vesper supplies a second emotion-specific mechanism with exact frozen
    upstream + scalar layer-weighting code.
11. General SSL evidence favors WavLM in several SER settings, but Vesper/WavLM
    lineage raises redundancy risk.
12. PEFT evidence is context-sensitive: selective upper-layer adaptation can
    help, but plain LoRA/full tuning can fail, and external datasets are much
    larger than DEFHS.

---

## 3. PROVISIONAL END-TO-END SYSTEM

```text
INPUT AUDIO
   |
   +--> certified frozen retrieval group?
   |       |
   |       +--> YES: deterministic unanimous retrieved label
   |       |
   |       +--> NO:
   |              frozen emotion-specialized core
   |                |- emotion2vec-family candidate
   |                |- Vesper-family candidate
   |              + at most one generic/multilingual SSL survivor
   |              + legacy acoustic RBF only if complementary
   |                    |
   |                    v
   |              simple regularized probability/logit blend
   |                    |
   |                    v
   |              ordinary argmax
   |              [optional nested/shrunk class-logit offsets]
   |
   v
FINAL LABEL
```

Core philosophy:

**frozen first → measure complementarity → adapt only if evidence earns it.**

---

## 4. CORE REPRESENTATION LANES

### Core A — emotion2vec family

First emotion-specialized candidate.

Use frozen encoder representations with a small downstream head. Begin with
mean+std pooling and L2 multinomial logistic / RBF-SVM head comparison.

Do not keep multiple emotion2vec variants as ensemble members merely because they
exist. Within-family variants must prove non-redundant value.

Execution requires exact checkpoint revision/license/policy resolution.

### Core B — Vesper-4

Second emotion-specialized candidate.

Reasons:
- compact;
- WavLM-derived but emotion-specifically pretrained;
- acquired paper shows strong SER transfer;
- exact code implements frozen upstream, trainable scalar layer weighting,
  temporal mean pooling, and small projection/classifier.

Escalate to Vesper-12 only if Vesper-4 evidence makes capacity a live question.

### Generic/multilingual discriminator

Run exactly one bounded comparison:
- WavLM-large;
- XLS-R-300m.

Keep at most one.

WavLM tests expected standalone strength.
XLS-R tests multilingual/representation diversity.

---

## 5. DIVERSITY LANES

### Existing FULL_RBF_SVM acoustic anchor

Keep it initially because:
- it is DIRECT_DEFHS;
- no new GPU cost is required;
- it has a fundamentally different feature bias.

Remove it if foundation-model OOF shows no held-out blend gain.

### eGeMAPS

Conditional diversity only.

Its weak standalone V-B result prevents core status. It survives only if a
low-weight addition improves leave-one-fold-out ensemble meta-validation.

### Transcript semantics

High-risk conditional diversity lane.

First gate is CPU-cheap TF-IDF + logistic regression on existing ASR transcripts,
with explicit prompt/dependency controls. Do not spend a GPU on a text foundation
model unless this gate succeeds.

---

## 6. CONDITIONAL HIGH-RISK LANES

1. one simple attentive-statistics pooling upgrade on the strongest frozen
   representation;
2. one upper-layer PEFT experiment if the Astra/OOF gate authorizes it;
3. one frozen text-encoder upgrade only if TF-IDF signal survives dependency
   controls;
4. bounded noise/gain augmentation only if PEFT later exhibits a robustness
   problem.

None is part of the default first run.

---

## 7. REJECTED / DEFERRED IDEAS

Rejected for the current program:

- full-model fine-tuning;
- high-dimensional stacking;
- broad HuBERT/W2V2/data2vec/UniSpeech/MMS model zoo;
- pseudo-labeling/self-training;
- public-LB iteration;
- retrieval confidence gating;
- aggressive pitch/time/speed augmentation;
- external BhavVani ingestion;
- class-imbalance machinery as the default response to happy.

Deferred unless earlier evidence reopens them:

- SenseVoice-Small;
- direct Whisper SER adaptation;
- CAMuLeNet-style co-attention network;
- complex multi-head/multi-query pooling;
- extra generic SSL families.

SenseVoice-Small is especially weak as a first-wave lane because the acquired
report's small variant does not include Hindi, its checkpoint permission is
unresolved, and its SER supervision is partly emotion2vec-derived.

---

## 8. ENSEMBLE DESIGN

Final ordinary SER ensemble size target: **2–3 non-redundant lanes**.

Selection procedure:

1. equal-weight probability averaging first;
2. pairwise error correlation, probability/logit correlation, disagreements,
   per-class complementarity, oracle headroom, marginal blend gain;
3. if unequal weighting is needed, only a coarse nonnegative simplex;
4. select/evaluate weights by **leave-one-V-B-fold-out meta-validation**:
   train weight choice on four folds, evaluate the fifth, rotate all five;
5. ablate each member;
6. refit final weights on all V-B OOF only after held-out meta-validation
   establishes the rule.

No unrestricted stacker.

Retrieval stays outside this blend and is evaluated as a separate deterministic
override in the retrieval-aware V-A pipeline.

---

## 9. EXPERIMENT LADDER

Ordered by decision value:

1. checkpoint/license/revision gate;
2. common frozen representation scaffold;
3. emotion2vec frozen screen + Vesper-4 frozen screen;
4. WavLM-large vs XLS-R-300m discriminator, keep at most one;
5. OOF complementarity analysis and first 2–3-lane ensemble;
6. eGeMAPS marginal-gain test;
7. transcript legitimacy gate with prompt/dependency controls;
8. simple attentive-statistics pooling only on selected neural lane(s);
9. one selective PEFT experiment only if its entry conditions are met;
10. nested/shrunk macro-F1 logit-offset test only after membership is locked;
11. V-A/V-D/Q/correlated-allocation finalist stresses;
12. protected confirmation only after SS explicitly locks the entire system.

The authoritative detailed ladder is:
`EXPERIMENT_LADDER.md`.

---

## 10. PROMOTE / KILL RULES

### Promote a model lane

Only if one of these is true:

- robust standalone improvement under V-B with credible fold/per-class behavior;
- slightly weaker standalone but convincingly positive held-out marginal ensemble
  gain.

### Kill a model lane

If:
- materially weaker with no diversity compensation;
- improvement is isolated to one fold or dependency stratum;
- predictions are nearly redundant with a stronger lane;
- complexity adds no held-out blend value;
- execution authority remains unresolved.

### Promote pooling/PEFT/decision calibration

Only if the improvement survives the appropriate held-out fold logic and does not
trade a small aggregate gain for a serious class-specific collapse.

Do not use an arbitrary tiny macro-F1 cutoff; compare the pattern against observed
fold/seed model-selection variability.

---

## 11. COMPUTE PLAN

### CPU

Use for:
- legal/revision audit;
- shallow heads over cached embeddings;
- TF-IDF text gate;
- OOF diagnostics;
- ensemble meta-validation;
- decision offsets;
- reports.

### 2× T4

Use the two slots for independent frozen extraction lanes:
- emotion2vec / Vesper;
- later WavLM / XLS-R.

Cache embeddings once and move head experiments to CPU.

### T4 or P100 later

Only after evidence selects one encoder:
- simple attentive pooling;
- one PEFT experiment.

Do not consume GPU quota on broad checkpoint variants.

---

## 12. HIGHEST-VALUE UNRESOLVED BOTTLENECK

**Frozen representation diversity versus one selective upper-layer PEFT
experiment after the strongest frozen parent is known.**

This is more valuable for Astra than transcript semantics because the transcript
question has an inexpensive empirical control experiment. The PEFT decision
requires integrating small-N bias/variance, cross-lingual transfer, representation
specialization, and adaptation mechanism evidence before GPU budget is committed.

---

## 13. ASTRA 6 MAX PACKET

Observed facts, competing hypotheses, evidence for/against, unknowns, exact
decision, constraints, and forbidden redo work are fully specified in:

`ASTRA_BOTTLENECK_PACKET.md`

Required Astra return:

1. choose `FROZEN_DIVERSITY_DEFAULT` or
   `ONE_SELECTIVE_PEFT_DEFAULT`;
2. give the DEFHS-specific bias/variance mechanism;
3. if PEFT is selected/triggered, select exactly one parent type, parameter
   subset, and adaptation family;
4. define the qualitative frozen-OOF entry gate;
5. define promote/kill logic using fold stability, V-A, happy, and marginal
   ensemble value;
6. define a fail-safe that terminates adaptation.

---

## 14. FULL PROMPT FOR ASTRA 6 MAX

```text
ROLE: ASTRA 6 MAX — LAYER 2 RESEARCH SCIENTIST

MISSION:
RS-DEFHS-SYSTEM-DESIGN-001
LAYER 2 OF 3 — ADAPTATION BOTTLENECK RESOLUTION

You are NOT restarting DEFHS research.
You are NOT redesigning validation.
You are NOT selecting among a broad model zoo.
You are NOT implementing the system.

Layer 1 has already completed the evidence synthesis and selected a provisional
frozen-first architecture.

READ FIRST:
runs/RS-DEFHS-SYSTEM-DESIGN-001/ASTRA_BOTTLENECK_PACKET.md

Use SYSTEM_DESIGN.md and EXPERIMENT_LADDER.md only as supporting authority.

YOUR ONE DECISION:

After the frozen representation screen identifies the strongest DEFHS encoder,
should scarce adaptation compute be spent on one bounded upper-layer PEFT
experiment, or should the default final core remain entirely frozen and spend
its model budget on representation diversity?

Observed constraints you must preserve:

- 826 labeled train clips;
- V-B primary duplicate-family-safe selection authority;
- V-A secondary competition-mimic / retrieval-aware authority;
- V-D and Q stresses diagnostic only;
- correlated-allocation envelope secondary finalist sensitivity;
- fixed certified retrieval lane remains separate;
- protected seed 20261001 remains untouched;
- no public-LB optimization;
- no new validation split;
- no assumption that external BhavVani equals competition SRCASW-BhavVaani;
- unresolved model/checkpoint terms are not permission;
- no full-model fine-tuning;
- no broad PEFT/rank/model sweep;
- at most ONE PEFT family in the first adaptation experiment.

Layer-1 provisional system:

certified retrieval hard override
    |
non-retrieval frozen emotion-specialized core
    |- emotion2vec-family
    |- Vesper-family
    + at most one WavLM-large/XLS-R-300m survivor
    + legacy acoustic RBF only if complementary
    |
simple low-dimensional probability/logit ensemble
    |
ordinary argmax, with optional nested strongly-shrunk class-logit offsets

External evidence is conflicting:
- frozen emotion2vec and Vesper have strong SER evidence;
- selective upper-layer adaptation can help in larger SER datasets;
- naive full tuning often fails;
- cross-lingual PEFT is strongly setting-dependent and plain LoRA can hurt;
- mechanistic evidence suggests late encoder layers are the natural adaptation
  target.

There is NO direct DEFHS foundation-model OOF yet. Do not fabricate it.

RETURN EXACTLY:

1. DEFAULT PATH:
   FROZEN_DIVERSITY_DEFAULT
   or
   ONE_SELECTIVE_PEFT_DEFAULT

2. DEFHS-SPECIFIC MECHANISTIC JUSTIFICATION:
   Explain the bias/variance tradeoff for 826 short Hindi SER clips.

3. IF PEFT IS SELECTED OR LATER TRIGGERED:
   - parent family type;
   - exact parameter subset to adapt;
   - ONE adaptation method;
   - what stays frozen;
   - whether pooling/layer weights train jointly;
   - how the test remains one experiment rather than a search.

4. ENTRY GATE:
   State what qualitative/structural evidence from frozen V-B OOF must exist
   before PEFT is scientifically justified. Do not invent an arbitrary tiny
   macro-F1 threshold.

5. PROMOTE / KILL LOGIC:
   Include fold stability, V-A behavior, happy-class behavior, overfit signals,
   and ensemble marginal value.

6. FAIL-SAFE:
   State when adaptation is abandoned and the frozen system is locked.

7. MINIMAL CHANGE TO LAYER-3 LADDER:
   Give only the exact edits caused by your decision.

DO NOT:
- redo literature discovery;
- summarize all 84 sources;
- rerank foundation models;
- solve transcript semantics as a separate mission;
- restart EDA;
- redesign validation;
- query protected candidate performance;
- make a Kaggle submission;
- propose multiple PEFT families to try.

Your answer must resolve the adaptation-versus-diversity architecture decision,
not create new candidate space.
```

---

## 15. FINAL GIT COMMIT SHA

Layer-1 project-state closure was committed at:

`a0cd0e40de98497c98b08e66ebdce48052e345c8`

The exact **final branch HEAD** is the commit that creates this
`FINAL_RETURN_TO_SS.md` file. Because a Git commit SHA is a hash of the commit
that contains the file, that SHA cannot be self-embedded in the same commit
without changing the hash. The closing SS message must therefore report the
resulting branch HEAD verbatim after this file is committed.

No commits are authorized after that verification as part of this Layer-1
mission.
