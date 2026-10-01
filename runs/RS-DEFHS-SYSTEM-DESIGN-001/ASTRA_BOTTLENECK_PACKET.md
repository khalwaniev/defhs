# RS-DEFHS-SYSTEM-DESIGN-001 — ASTRA BOTTLENECK PACKET

## Primary bottleneck

**After the frozen representation screen identifies the strongest DEFHS encoder,
should scarce adaptation compute be spent on upper-layer PEFT of that encoder, or
should the final SER core remain fully frozen and spend its capacity budget on
representation diversity?**

This is the one question Layer 1 cannot resolve adequately from existing
evidence.

Do not reinterpret it as "find the best model."

---

## OBSERVED FACTS

### DEFHS

- Only 826 labeled train clips exist.
- V-B is the primary duplicate-family-safe model/representation selection view.
- V-A is secondary competition-mimic / retrieval-aware evidence.
- Fold/seed variation of the current cheap baselines is material.
- Happy is the weakest current class despite nearly balanced class support.
- Moderate representation-dependent train/test shift exists after duplicate
  removal.
- Retrieval is frozen and separate.
- Protected seed 20261001 remains untouched and confirmation-only.
- Available compute is bounded but sufficient for a few decisive T4/P100
  experiments, not an open-ended adaptation sweep.

### Frozen-representation evidence

- emotion2vec provides strong external evidence that emotion-specialized frozen
  representations can transfer across languages.
- Vesper provides strong external evidence for emotion-specific WavLM-derived
  representations, with an exact implementation using frozen upstream features
  and trainable scalar layer weighting.
- Frozen representations are unusually attractive in DEFHS because the dataset
  is tiny and hidden states can be cached for many cheap downstream tests.
- A small, diverse frozen system can combine emotion2vec, Vesper, one
  generic/multilingual SSL survivor, and the existing acoustic RBF anchor.

### Adaptation evidence

Evidence is credible but conflicting/context-dependent:

1. A 2025 SER benchmark on the much larger MSP-Podcast corpus found that naive
   full fine-tuning often provided little benefit or degradation, while selective
   upper-layer adaptation plus attentive pooling could substantially improve
   performance.
2. The acquired cross-lingual PEFT study shows that plain LoRA can hurt in some
   language/settings, while adapter/gating combinations can help in others.
3. Mechanistic LoRA evidence on Whisper indicates task specialization is
   concentrated in later encoder layers, supporting upper-layer rather than
   whole-encoder adaptation.
4. None of these studies has DEFHS's N=826, duplicate/dependency structure,
   exact four-class distribution, and frozen V-B authority.

Therefore external literature does not answer whether PEFT's bias reduction is
worth its variance cost in this specific regime.

---

## DECISION THAT REMAINS UNRESOLVED

Choose the default architecture after the first frozen screen:

### HYPOTHESIS A — FROZEN-DIVERSITY CORE

Keep all foundation encoders frozen.

Spend compute on:
- selecting the best emotion-specialized representations;
- one orthogonal generic/multilingual representation;
- simple pooling/head choices;
- low-dimensional OOF ensembling.

Rationale:
- N=826 strongly favors low-variance estimators;
- representation diversity may capture most available headroom;
- cached embeddings make evaluation reproducible and cheap;
- adaptation could overfit duplicate/prompt/source idiosyncrasies.

### HYPOTHESIS B — SELECTIVE-ADAPTATION CORE

After selecting one strongest frozen encoder, perform one carefully bounded PEFT
experiment on its upper layers/attention modules and let that adapted lane become
the dominant core, retaining one frozen diversity lane.

Rationale:
- emotion discrimination may require task-specific reshaping of high-level
  encoder states;
- external SER work shows upper-layer selective adaptation can outperform both
  frozen and fully fine-tuned models;
- current happy weakness may reflect insufficient separation in the frozen
  representation rather than head capacity.

---

## WHY THE DECISION MATTERS

This changes:

- GPU allocation;
- model variance;
- the number of final ensemble lanes;
- whether pooling/layer-selection remains the primary adaptation mechanism;
- reproducibility;
- inference artifact complexity;
- how much risk is taken before the protected confirmation.

If H1 is wrong and adaptation is skipped, DEFHS may leave representation-level
target information untapped.

If H2 is wrong and PEFT is pursued, scarce labels can be spent fitting
dataset-specific artifacts, reducing private transfer and wasting the most
expensive experimental slot.

---

## EVIDENCE SUPPORTING HYPOTHESIS A

- DIRECT_DEFHS small-N regime.
- DIRECT_DEFHS fold/seed sensitivity.
- emotion2vec and Vesper external results demonstrate substantial SER quality
  from frozen encoders.
- General SSL benchmark reports many naive full-fine-tune results that are flat
  or worse.
- Multiple strongly correlated models do not automatically create a better
  ensemble; therefore frozen diversity must be curated, but it is testable with
  low variance.
- The frozen architecture cleanly isolates prompt/source/retrieval effects.

## EVIDENCE AGAINST HYPOTHESIS A

- A shallow head may not reshape the representation enough for subtle
  emotion boundaries.
- Happy remains weak in the existing system despite balanced support, making a
  representation-level intervention plausible.
- External upper-layer adaptation work indicates later layers are where
  emotion-specific information can be improved.

---

## EVIDENCE SUPPORTING HYPOTHESIS B

- Selective upper-layer WavLM adaptation has strong SER precedent.
- Cross-lingual PEFT can recover target-language performance when the strategy is
  appropriate.
- LoRA interpretability work supports late-layer specialization while preserving
  early general features.
- PEFT can create a stronger single lane without requiring a large downstream
  model.

## EVIDENCE AGAINST HYPOTHESIS B

- External PEFT benefits are context-dependent; plain LoRA can degrade results.
- The strongest selective-fine-tuning evidence uses far more labeled data than
  DEFHS.
- N=826 makes adaptation variance and early-stopping noise substantial.
- Moderate hidden shift raises the risk that target-domain adaptation fits the
  wrong local geometry.
- PEFT may make errors more correlated with another emotion-specialized lane,
  reducing ensemble value even if standalone V-B rises.

---

## WHAT IS STILL UNKNOWN

1. At N=826, what is the expected bias/variance crossover for upper-layer PEFT
   versus frozen layer mixing in SER?
2. Which adaptation parameterization is least likely to destroy transferable
   prosodic information:
   - upper-block unfreezing;
   - upper-attention LoRA;
   - bottleneck adapter;
   - layer weighting/pooling only?
3. What evidence threshold should make PEFT worth *one* experiment without
   converting the mission into a hyperparameter search?
4. Is happy the class most likely to benefit from late-layer specialization, or
   would adaptation trade happy recall for other-class stability?
5. Should the preferred adaptation target be the best emotion-specialized lane
   or the strongest general SSL lane?

---

## WHAT ANSWER WOULD CHANGE THE SYSTEM

### If Astra selects frozen-diversity as default

Layer 3 stops after:
- frozen emotion-specialized core;
- one generic/multilingual discriminator;
- complementarity-aware ensemble;
- optional text/eGeMAPS gates.

PEFT is run only if frozen OOF evidence later triggers a clearly specified
exception.

### If Astra selects selective adaptation as default

Layer 3 reserves one bounded GPU experiment for:
- exactly one parent encoder;
- exactly one adaptation family;
- predeclared upper-layer target;
- fixed V-B comparison to its frozen parent;
- no bundled loss/augmentation changes.

The adapted lane is promoted only if it retains ensemble value as well as
standalone strength.

---

## EXACT DECISION ASTRA MUST RETURN

Return all of the following:

1. **DEFAULT PATH:** choose one:
   - `FROZEN_DIVERSITY_DEFAULT`
   - `ONE_SELECTIVE_PEFT_DEFAULT`

2. **MECHANISTIC JUSTIFICATION:** explain the bias/variance reasoning specifically
   for 826 labeled ~3-second SER clips, not generic transfer-learning advice.

3. **IF PEFT IS SELECTED OR LATER TRIGGERED:**
   - preferred parent family: emotion-specialized or general SSL;
   - preferred parameter subset to adapt;
   - one adaptation method;
   - what remains frozen;
   - whether pooling/layer weights train jointly;
   - how to avoid turning the test into a search.

4. **ENTRY GATE:** define the qualitative/structural evidence from frozen V-B OOF
   that must exist before adaptation is scientifically justified. Do not invent a
   tiny arbitrary macro-F1 threshold.

5. **PROMOTE / KILL LOGIC:** specify how fold stability, V-A, happy behavior, and
   ensemble marginal value should determine the decision.

6. **FAIL-SAFE:** state when DEFHS should abandon adaptation and lock the frozen
   system.

Astra may recommend one small additional diagnostic if it is indispensable to
make the decision, but it must not broaden the mission.

---

## CONSTRAINTS ASTRA MUST PRESERVE

- V-B remains primary.
- V-A remains secondary.
- V-D/Q stresses remain diagnostic.
- correlated-allocation remains secondary finalist sensitivity.
- protected seed 20261001 remains untouched.
- retrieval remains a separate certified deterministic override.
- no public-LB optimization.
- no new primary validation split.
- no external BhavVani ingestion or lineage assumption.
- no unresolved checkpoint/license assumption.
- at most one PEFT family in the first adaptation test.
- no full fine-tuning.
- no broad model benchmark.
- no high-dimensional stacking.

---

## WHAT ASTRA MUST NOT REDO

Do not:
- repeat broad literature discovery;
- resummarize all 84 warehouse records;
- re-rank a long list of pretrained encoders;
- redesign validation;
- redo EDA;
- propose a model zoo;
- query the protected fold;
- perform a Kaggle submission;
- solve transcript semantics as a separate primary mission.

Layer 1 has already selected the provisional frozen system. Astra's job is to
resolve the **adaptation-versus-diversity bottleneck** only.
