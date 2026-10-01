# DEFHS — Detecting Emotions from Hindi Speech

Canonical research repository for the Kaggle competition:

`dataverse-detecting-emotions-from-hindi-speech`

## Objective

Maximize robust final/private-leaderboard performance under the official
four-class macro-F1 objective:

- angry
- happy
- neutral
- sad

## Start here

A new worker should read, in this order:

1. `WORKFLOW.md`
2. `docs/OBJECTIVE_LOCK.md`
3. `docs/PROJECT_STATE.md`
4. the current mission / SS handoff

Do not reconstruct the current project state by recursively reading historical
runs unless the current mission or `PROJECT_STATE.md` points to them.

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

`docs/PROJECT_STATE.md` identifies the current scientific authority and next
bottleneck.

## Repository map

- `WORKFLOW.md` — governing workflow
- `docs/OBJECTIVE_LOCK.md` — stable competition objective
- `docs/PROJECT_STATE.md` — concise current project state
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
