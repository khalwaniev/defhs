# DEFHS — Detecting Emotions from Hindi Speech

Canonical research repository for the Kaggle competition:

`dataverse-detecting-emotions-from-hindi-speech`

## Objective

Maximize macro-F1 on the exact **209 supplied unlabeled test WAV files**, using
the **826 labeled training WAVs** and predicting:

- angry
- happy
- neutral
- sad

## Start here

A fresh SS/RS should read these compact files, in this order:

1. [ACTIVE_COMPETITION_STATE](docs/ACTIVE_COMPETITION_STATE.md)
2. [ACTIVE_VALIDATION](docs/ACTIVE_VALIDATION.md)
3. [TARGET209_STRATEGY](docs/TARGET209_STRATEGY.md)

The active evidence hierarchy is **PRIMARY_CV → TARGET209_ANALYSIS → PUBLIC_LB**.
PRIMARY_CV is the unchanged historical V-B under a simpler alias. The three
active model families are WAVEFORM, SPECTROGRAM and SEMANTIC; dataset structure
is auxiliary evidence.

[PROJECT_STATE](docs/PROJECT_STATE.md) routes to current authority first and
retains the full historical state below an explicit boundary. Use
[HISTORICAL_VALIDATION_INDEX](docs/HISTORICAL_VALIDATION_INDEX.md) only when a
specific risk question requires old evidence. **Do not recursively read
historical runs unless a concrete scientific question requires them.**
Before execution, apply [WORKFLOW](WORKFLOW.md) and the current mission / SS
handoff. The [original objective lock](docs/OBJECTIVE_LOCK.md) remains preserved
with an explicit mapping to current authority.

## Authority model

GitHub contains project logic and scientific state:

- source code;
- configs;
- validation definitions;
- tests;
- lightweight reports;
- manifests;
- mission history.

Heavy artifacts live under Google Drive:

`/DEFHS/`

Detailed historical scientific evidence is preserved under:

`runs/`

The compact active documents define the current competition objective and
evidence roles. `docs/PROJECT_STATE.md` preserves scientific state and routes
workers to those documents before historical detail.

## Repository map

- `WORKFLOW.md` — governing workflow
- `docs/ACTIVE_COMPETITION_STATE.md` — current TARGET209 objective and model families
- `docs/ACTIVE_VALIDATION.md` — PRIMARY_CV alias and active evidence hierarchy
- `docs/TARGET209_STRATEGY.md` — canonical prediction-matrix specification
- `docs/TEST209_PREDICTION_MATRIX.csv` — populated 209-row evidence matrix; unavailable probability families stay empty
- `docs/HISTORICAL_VALIDATION_INDEX.md` — on-demand archive/diagnostic map
- `docs/OBJECTIVE_LOCK.md` — preserved original objective and current-authority mapping
- `docs/PROJECT_STATE.md` — active entry point followed by preserved state history
- `docs/EXTERNAL_DATA_POLICY.md` — external-data policy
- `runs/` — detailed mission history and frozen scientific evidence
- `experiments/` — experiment registry
- `configs/` — configuration
- `scripts/` — reproducible execution utilities
- `src/defhs/` — reusable project code
- `kaggle/` — Kaggle execution packages
- `manifests/` — lightweight external-artifact manifests
- `requirements/` — mission-specific environments
- `tests/` — tests
