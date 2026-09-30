# DS-DEFHS-VALIDATION-HARDENING-002

## Role

Data Scientist (DS).

## Parent authority

`14dcd47d2250b1bb2e39a4c37aadf2d92fc1db9a`

## Governing workflow

`WORKFLOW.md`

DS owns the empirical and validation foundation: EDA, data integrity,
preprocessing, leakage/dependency analysis, grouping/distribution shift,
metric verification, validation design, and stress testing.

## Mission

Produce the most comprehensive *scientifically useful* understanding of the
SRCASW-BhavVaani competition data that is practical before serious modeling,
then freeze an internal validation system designed to mimic the hidden/private
leaderboard data-generating process as closely and defensibly as possible.

The internal validation is an **emulator**, not a claim to reproduce the actual
private leaderboard or hidden public/private allocation.

Foundation-model training is blocked until this mission returns `PASS_FREEZE`
or an explicitly revised validation authority.

---

# Official competition facts to preserve

The competition description states that:

- SRCASW-BhavVaani is a self-curated Hindi speech-emotion corpus;
- it is described as containing 1,036 samples;
- it contains both acted and spontaneous speech;
- targets are angry, happy, neutral, sad;
- official evaluation is macro F1 over the four classes;
- final competition score is
  `0.40 * public_score + 0.60 * private_score`;
- the stated scientific goals include generalization beyond already-seen
  voices and expressions.

The supplied competition ZIP previously audited contains 1,035 train+test
examples, so the 1,036-vs-1,035 discrepancy must remain explicit until resolved.

Do not infer that the 40/60 score weights imply a 40/60 public/private sample
fraction. Determine the split fraction only if it can be verified; otherwise
treat it as unknown and perform sensitivity analysis.

---

# A. Competition package and schema forensics

Establish an exact manifest of the supplied package.

Audit:

- train/test/sample-submission row counts;
- exact column names and dtypes;
- actual submission schema versus prose examples;
- ID domain, gaps, duplicates, ordering, monotonicity, modulo/periodicity;
- filename/ID consistency;
- missing/orphan audio files;
- duplicate filenames;
- corrupted/truncated WAVs;
- WAV headers and codec/container metadata;
- sample rate, channels, sample width, PCM dtype/endian;
- duration and sample-count distributions;
- file size;
- any metadata bytes or container fields that predict split, class, source,
  speaker, recording batch, or label.

Reconcile all material discrepancies between competition prose and actual files.

---

# B. Label and target audit

For training labels:

- exact class counts and priors;
- class balance by ID region, duration, recording format, inferred source,
  speaker cluster, prompt/transcript cluster, and duplicate family;
- known duplicate-label conflict;
- every additional exact/near-duplicate label conflict;
- cross-validated outlier/mislabelling diagnostics using multiple independent
  acoustic representations;
- classwise nearest-neighbour disagreement;
- high-confidence annotation-noise candidates;
- potential ambiguous-borderline examples.

Do **not** silently relabel or remove samples. Produce evidence and an explicit
training-policy recommendation.

---

# C. Duplicate / near-duplicate / transformation forensics

The current candidate authority found 227 near-duplicate groups and 78 affected
test clips. Re-audit this exhaustively.

Test invariance to:

- PCM bit depth;
- amplitude/gain;
- DC offset;
- leading/trailing silence;
- short crops/padding;
- resampling;
- waveform normalization;
- encoding differences;
- small temporal alignment differences.

Use multiple independent similarity representations and threshold sweeps.

For every duplicate family record:

- members;
- train/test membership;
- labels;
- similarity evidence;
- transformation type if inferable;
- confidence tier;
- whether test retrieval label is invariant.

Quantify threshold stability and identify the exact region where duplicate and
non-duplicate similarity distributions separate.

Final deterministic retrieval policy must be auditable and remain separate
from general SER model validation.

---

# D. Full acoustic EDA

Characterize each clip and class using, where technically defensible:

## Basic signal statistics
- duration;
- RMS / loudness;
- peak amplitude;
- clipping;
- DC offset;
- silence fraction;
- leading/trailing silence;
- dynamic range;
- crest factor;
- zero-crossing rate;
- simple SNR/noise-floor estimates.

## Prosody
- F0/pitch distribution;
- pitch range/variance/contour;
- voiced fraction;
- intensity contour;
- temporal energy dynamics;
- pause statistics;
- speaking-rate proxies where possible.

## Spectral / voice-quality
- spectral centroid/bandwidth/rolloff/flatness;
- MFCCs and deltas;
- log-Mel statistics;
- spectral flux;
- formant proxies where robust;
- harmonicity/HNR/jitter/shimmer proxies where reliable;
- eGeMAPS;
- ComParE or a similarly standardized paralinguistic feature set.

For every material feature family:

- train distribution;
- test distribution;
- class-conditional distribution;
- duplicate/source conditional distribution;
- missing/unstable measurement rate;
- effect sizes rather than only plots.

Do not infer biological attributes such as sex/gender from voice unless the
dataset explicitly provides them.

---

# E. Recording-condition and source-corpus reconstruction

Determine whether the supposedly single dataset contains multiple recording
pipelines or source batches.

Use:

- file/codec metadata;
- sample width;
- duration;
- silence/noise characteristics;
- spectral fingerprints;
- room/channel signatures;
- low-level acoustic embeddings;
- unsupervised clustering;
- change-point analysis over ID order.

Test whether inferred source clusters:

- are stable across feature representations;
- align with ID ranges;
- align with acted/spontaneous regimes;
- align with labels;
- differ between train and test;
- explain duplicate families;
- affect validation difficulty.

No source grouping becomes authoritative unless it is stable and reproducible.

---

# F. Speaker structure

Because the official description asks whether systems generalize beyond voices,
speaker dependence is decision-critical.

Use at least one strong pretrained speaker embedding (e.g. ECAPA-TDNN/x-vector
family) and, if practical, an independent embedding method.

Perform:

- within/between similarity analysis;
- clustering across multiple thresholds and algorithms;
- cluster-stability analysis;
- duplicate-family consistency checks;
- source-condition confounding checks;
- train/test speaker-overlap estimation;
- per-speaker/cluster class diversity;
- whether speaker identity predicts emotion labels spuriously.

Freeze a speaker/source-disjoint validation V-C only if the inferred speaker
groups are sufficiently reliable. Otherwise explicitly reject V-C as
non-authoritative and retain speaker clustering only as a stress diagnostic.

---

# G. Acted-versus-spontaneous structure

The official description explicitly says the corpus mixes acted and spontaneous
speech, but no regime labels are supplied.

Investigate whether the two regimes can be recovered reliably from:

- source/recording clusters;
- transcript/script repetition;
- duration and pause structure;
- prosody;
- lexical diversity;
- speaker/source patterns;
- acoustic/self-supervised embeddings.

Do not create hard acted/spontaneous labels unless evidence supports them.

If reliable latent regimes exist, quantify train/test proportions and class
balance, and test whether validation folds preserve them.

---

# H. Transcript / lexical / prompt structure

Transcribe all clips with a strong Hindi-capable ASR model if compute permits.

Audit:

- transcript quality on a manual spot-check;
- repeated sentences/prompts;
- train/test lexical overlap;
- transcript duplicate/near-duplicate clusters;
- scripted phrase families;
- lexical diversity by inferred source/regime;
- whether prompts correlate with labels;
- whether semantic content has predictive signal independent of acoustic/source
  leakage;
- whether transcript structure helps identify acted/spontaneous/source batches.

This is primarily EDA and grouping evidence. It does not automatically authorize
a text-semantic model.

---

# I. ID/order leakage and acquisition-sequence analysis

Because IDs appear to be drawn from a shared master sequence, perform exhaustive
order analysis:

- train/test interleaving;
- split probability by ID region;
- rolling class proportions;
- runs/change points;
- periodicity and modulo effects;
- duplicate-family location;
- source/speaker/prompt cluster location;
- recording-format changes;
- class predictability from ID/order alone under leakage-safe CV.

Determine whether ID encodes acquisition batches, prompts, speakers, labels, or
recording conditions.

Any exploitable ID signal must be distinguished from fragile leaderboard
overfitting.

---

# J. Train/test distribution shift

Quantify train-vs-test shift globally and within discovered subgroups.

Use:

- univariate effect sizes / PSI-like diagnostics;
- multivariate embedding distances;
- MMD or another appropriate two-sample statistic;
- adversarial validation;
- source/speaker/prompt proportions;
- duration/prosody/acoustic feature distributions;
- duplicate-covered versus non-duplicate test subsets.

Adversarial validation must be repeated after excluding obvious duplicate pairs
so duplicate structure does not dominate the conclusion.

Identify exactly which test regions are well represented and which are
out-of-distribution relative to train.

---

# K. Validation candidates

Do not begin by assuming one split is correct.

Construct and compare candidate validation mechanisms.

## V-A — row-level competition-mimic

Five-fold stratified row-level CV using a frozen seed.

Purpose:
- approximate random row sampling from the same parent corpus;
- measure the environment in which near-duplicate retrieval can exist.

## V-B — duplicate-safe model-selection CV

All exact/near-duplicate families remain within one fold.

Purpose:
- primary guardrail for genuine SER model-family selection;
- prevent duplicate memorization from deciding which representation wins.

## V-C — speaker/source-disjoint stress CV

Freeze only if speaker/source groups are reliable.

Purpose:
- test voice/source generalization.

## V-D — source/regime-aware stress CV

If stable recording-source or acted/spontaneous regimes are discovered, design
a stress split that tests robustness to those structures.

Do not automatically use V-C or V-D as the primary competition estimator;
their role depends on evidence about the hidden test's likely generation.

---

# L. Private-LB emulator design

The goal is to mimic the hidden/private evaluation as closely as evidence
allows, **not** to claim the true private split is known.

Build a validation emulator with these principles:

1. Reproduce the official macro-F1 implementation exactly.
2. Preserve plausible test-like class/source/speaker/regime mixtures.
3. Simulate the production inference pipeline, including the deterministic
   duplicate-retrieval lane where an analogue exists inside each pseudo-test
   fold.
4. Evaluate non-retrieval clips separately so retrieval success does not mask a
   weak SER model.
5. If the actual public/private sample fraction cannot be verified, perform
   sensitivity analyses across plausible fractions rather than equating the
   0.40/0.60 score weights with data fractions.
6. For each pseudo-public/private realization calculate:
   - public macro F1;
   - private macro F1;
   - official weighted final score:
     `0.40*public + 0.60*private`;
   - full pseudo-test macro F1.
7. Use repeated Monte Carlo/group-aware pseudo-public/private partitions to
   estimate:
   - score variance;
   - model-ranking variance;
   - probability that tiny improvements reverse;
   - sensitivity to class imbalance in small hidden subsets.
8. Create one or more **protected promotion gates** that are frozen before
   foundation-model optimization and are not used as an unlimited tuning oracle.

The emulator must document what it mimics, what it cannot mimic, and why.

---

# M. Validation stability and cheap model battery

Do not freeze validation based on one RBF-SVM.

Run several low-cost, meaningfully different baselines under the identical
candidate folds, for example:

- MFCC/eGeMAPS + linear logistic/ridge;
- MFCC/eGeMAPS + RBF-SVM;
- standardized ComParE + linear/SVM;
- one inexpensive frozen pretrained speech embedding + linear classifier if
  feasible.

For each:

- per-fold macro F1;
- per-class F1;
- confusion matrix;
- seed variance;
- model ranking under V-A/V-B/(V-C/V-D if available);
- retrieval-covered versus non-retrieval performance.

Quantify whether validation selects models consistently.

---

# N. Fold-quality requirements

For every candidate fold set audit:

- row counts;
- class counts;
- duplicate-group separation;
- inferred speaker/source balance;
- acted/spontaneous or latent-regime balance if known;
- duration/acoustic distribution balance;
- train/test-like subgroup balance;
- fold difficulty;
- outlier concentration.

Fold artifacts must be deterministic and committed.

---

# O. Final validation authority

Return a final evidence-based decision:

- `PASS_FREEZE`, or
- `REVISE_AND_FREEZE`, or
- `FAIL_NOT_READY`.

The authority must define:

- primary model-selection validation;
- competition-mimic secondary validation;
- speaker/source/regime stress validations;
- protected promotion gate(s);
- private-LB emulator;
- official metric implementation;
- retrieval-lane evaluation;
- model-promotion thresholds;
- requirements for seed/fold replication;
- policy for small apparent gains;
- exact files and Git commit constituting the frozen authority.

---

# Required artifacts

At minimum:

- `OFFICIAL_PACKAGE_RECONCILIATION.md`
- `DATA_MANIFEST.csv`
- `EDA_MASTER_REPORT.md`
- `LABEL_INTEGRITY_REPORT.md`
- `DUPLICATE_FORENSICS_REPORT.md`
- `DUPLICATE_GROUPS_FINAL.csv`
- `RETRIEVAL_MAP_FINAL.csv`
- `ACOUSTIC_FEATURE_SUMMARY.csv`
- `SOURCE_STRUCTURE_REPORT.md`
- `SPEAKER_GROUPING_REPORT.md`
- `ACTED_SPONTANEOUS_REPORT.md`
- `TRANSCRIPT_STRUCTURE_REPORT.md`
- `ID_ORDER_FORENSICS_REPORT.md`
- `TRAIN_TEST_SHIFT_REPORT.md`
- `VALIDATION_CANDIDATES_REPORT.md`
- deterministic fold CSVs for every frozen validation view;
- `PRIVATE_LB_EMULATOR_SPEC.md`
- `VALIDATION_STABILITY_RESULTS.json`
- `FINAL_VALIDATION_AUTHORITY.md`
- `FINAL_RETURN_TO_SS.md`
- reproducible scripts/configs used to produce all lightweight authorities.

Large embeddings/transcripts/features may live outside GitHub if needed, but
their location, version, checksums, and producer commit must be recorded.

---


# P. Data-understanding completeness contract

The mission is not complete merely because many analyses were run.

Create and maintain a decision-relevant unknowns ledger covering every material
property of the dataset/data-generating process encountered during the mission.

Every material question must end in exactly one evidence state:

1. **VERIFIED**
   - directly established from competition files, official information, or a
     reproducible deterministic audit;

2. **INFERRED**
   - not directly labeled/observed, but supported by explicit evidence;
   - state the method, uncertainty, confidence/stability, alternative
     explanations, and whether the inference is strong enough to affect
     validation/modeling;

3. **UNRESOLVABLE FROM AVAILABLE EVIDENCE**
   - cannot be established honestly from available data;
   - explain why;
   - quantify or bound the decision impact where possible;
   - define a robust policy that does not depend on pretending the unknown is
     known.

No material assumption may remain implicit.

At minimum, explicitly close or register uncertainty for:

- 1,036 stated samples versus 1,035 supplied train+test examples;
- true speaker identities and train/test speaker overlap;
- acted-versus-spontaneous membership;
- source/acquisition batches;
- script/prompt identity;
- duplicate-family boundaries and threshold robustness;
- annotation-noise cases;
- ID/order/acquisition semantics;
- public/private sample fraction;
- hidden public/private assignment mechanism;
- whether the test distribution is generated like a row-random split,
  group-aware split, source-aware split, speaker-aware split, or mixture;
- retrieval-lane applicability and confidence;
- train/test distribution shift;
- any other discovered structure capable of changing model selection or final
  inference.

Required additional artifacts:

- `DATA_UNKNOWN_REGISTER.md`
- `DATA_UNDERSTANDING_CERTIFICATE.md`

`DATA_UNKNOWN_REGISTER.md` must contain, for every material question:

- question;
- state: VERIFIED / INFERRED / UNRESOLVABLE;
- evidence;
- uncertainty/confidence;
- competing explanations;
- decision impact;
- resulting validation/modeling policy;
- artifact/script reference.

`DATA_UNDERSTANDING_CERTIFICATE.md` is the final concise certification that:

- all material dataset questions encountered have been audited;
- no material assumption is implicit;
- remaining unknowable properties are explicitly registered;
- their decision impact is controlled by validation/stress tests/sensitivity
  analyses;
- the final validation authority does not rely on pretending an unresolved
  property is known.

A final `PASS_FREEZE` or `REVISE_AND_FREEZE` is invalid without these two
artifacts.


# Stop rule

This mission is intentionally comprehensive, but not ornamental.

Continue until there is no important unresolved question about the supplied
data that is reasonably capable of changing:

- leakage handling;
- grouping;
- validation construction;
- private-LB emulation;
- model-family selection;
- external-data adaptation strategy;
- ensemble design;
- final inference.

Do not spend time on descriptive plots or statistics that cannot affect a
scientific or competition decision.

Once this condition is met, freeze validation and return immediately to SS for
the first RS modeling mission.
