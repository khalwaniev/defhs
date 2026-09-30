# DEFHS — DataVerse: Detecting Emotions from Hindi Speech

Canonical research repository for the Kaggle competition:

`dataverse-detecting-emotions-from-hindi-speech`

## Objective

Maximize the official final competition score, with emphasis on robust private-leaderboard performance rather than public-LB overfitting.

Official evaluation: macro F1 over four classes:

- angry
- happy
- neutral
- sad

Final competition ranking uses the organizer's weighted public/private leaderboard score.

## Governing workflow

`WORKFLOW.md` is the governing scientific workflow for this project.

GitHub is the canonical live source of truth for code, validation definitions,
experiment records, lightweight reports, manifests, and project state.

Large data, checkpoints, embeddings, predictions, and bulky outputs must not be
committed to GitHub. Keep them in Kaggle, Google Drive, or other external
storage and record pointers/checksums in `manifests/`.

## Initial verified local data facts

Inspection of the supplied competition ZIP on 2026-09-30 found:

- train rows: 826
- test rows: 209
- total audio files represented by train/test: 1,035
- sample rate: 16 kHz for all inspected clips
- target classes: angry, happy, neutral, sad
- exact PCM-identical train→test duplicate matches: 8 test clips
- exact PCM-identical train-only duplicate groups: 13 groups / 27 clips

A stronger duplicate/near-duplicate audit is required before validation is frozen.

## Current scientific direction

Do not treat the problem as a generic small SER benchmark.

Current candidate families, to be tested under one frozen validation authority:

1. emotion2vec+ Large
2. WavLM Large
3. Whisper encoder representations
4. openSMILE/eGeMAPS or ComParE + RBF-SVM
5. optional HuBERT/XLS-R diversity lane
6. optional transcript-semantic branch if validated
7. duplicate/near-duplicate retrieval layer kept separate from the general SER model

External data must only be promoted when it improves target-domain validation.
Same-language Hindi SER data is higher priority than blindly pooling unrelated
English SER corpora.

## Repository map

- `WORKFLOW.md` — governing workflow
- `docs/OBJECTIVE_LOCK.md` — official objective, metric, constraints
- `docs/PROJECT_STATE.md` — current verified project state
- `docs/DATA_AUDIT_INITIAL.md` — initial integrity findings
- `docs/VALIDATION_PLAN.md` — validation authority proposal
- `docs/EXTERNAL_DATA_POLICY.md` — external-data policy and acquisition rules
- `experiments/EXPERIMENT_REGISTRY.csv` — append-only experiment index
- `manifests/` — pointers/checksums for heavy external artifacts
- `scripts/` — reproducible utilities
- `src/defhs/` — reusable project code
- `configs/` — experiment configuration
- `tests/` — tests

## First mission after repository bootstrap

Freeze a trustworthy data/validation authority before expensive model work:

1. reproduce metadata/integrity audit;
2. build exact + near-duplicate groups;
3. inspect conflicting labels;
4. estimate speaker/source grouping where feasible;
5. define ordinary competition-mimic CV and leakage-safe grouped CV;
6. benchmark a cheap acoustic baseline;
7. only then launch foundation-model experiments.

Do not use leaderboard feedback as the validation authority.
