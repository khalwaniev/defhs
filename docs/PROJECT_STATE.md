# Project State

Status date: 2026-10-01

## Repository authority

Canonical repository: `khalwaniev/defhs`

Canonical local path: `/home/fikar/zingle/defhs`

Active branch: `ds/validation-hardening-002`

Governing workflow: `WORKFLOW.md`

## Current phase

**DS-DEFHS-VALIDATION-HARDENING-002 — COMPLETE.**

Final DS verdict:

**REVISE_AND_FREEZE**

The earlier `FAIL_NOT_READY` state has been superseded. All four mandatory
closure audits have executed and been scientifically interpreted.

## Canonical data authority

Raw archive:

- Drive path:
  `/DEFHS/raw/dataverse-detecting-emotions-from-hindi-speech.zip`;
- file ID: `1D0DcnbK0vrJGTsvtb7-l7vnpdfNxc-nH`;
- size: 99,298,085 bytes;
- SHA-256:
  `100b38e6ed69542df88c1d295932a7a4c1914cd931ee64f7c6c848f6053bf214`.

Supplied examples: 826 train + 209 test = 1,035.

The organizer prose statement of 1,036 remains an explicitly bounded metadata
unknown.

## Frozen empirical structure

- IDs exactly 1..1035;
- 227 near-duplicate groups / 467 clips;
- 77 train-test duplicate groups / 78 affected test clips;
- duplicate threshold 0.95;
- one confirmed duplicate-label conflict family: IDs 75 / 636 / 878;
- verified int16/int32 recording heterogeneity;
- global train/test separation weak, with modest nonlinear residual shift;
- Hindi ASR, ECAPA, eGeMAPS and joint latent-regime audits complete.

## Final validation architecture

### V-A

Row-level stratified five-fold CV, seed 20260930.

Role: **secondary competition-mimic / retrieval-aware view**.

SHA-256:

`dcee356b0a66cb73c506bb71a6c57962227d6d0474efd3e4d6c404168308f3d1`

### V-B

Duplicate-family-safe StratifiedGroupKFold, seed 20260930.

Role: **primary model/representation selection authority**.

SHA-256:

`87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b`

### V-C

**Rejected as an authoritative split.**

ECAPA clusters remain diagnostic only because stable strict clusters mostly
reproduce duplicate families and broader clustering is threshold-sensitive.

### V-D

Verified int16/int32 recording-format/source stress.

Role: diagnostic robustness view.

SHA-256:

`f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839`

### Protected promotion gate

Duplicate-safe seed 20261001.

SHA-256:

`b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c`

Status: **untouched / confirmation only**.

## Retrieval

Retain the deterministic separate retrieval lane for 78 / 209 test clips.

## Closure interpretation

- ECAPA: useful speaker-sensitive diagnostic, no authoritative V-C;
- ASR: repeated prompt structure exists but is mostly duplicate-contained;
- no-duplicate prompt/class AMI approximately 0.0075;
- eGeMAPS: train/test logistic AUC approximately 0.4764, no new material shift;
- joint latent regimes: weak and not suitable for a new frozen validation view.

Final reproduced diagnostics:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/FINAL_INTERPRETATION_DIAGNOSTICS.json`

Heavy closure artifacts and provenance:

`/DEFHS/ds_validation_002/`

`runs/DS-DEFHS-VALIDATION-HARDENING-002/CLOSURE_COMPLETED_ARTIFACT_MANIFEST.tsv`

## Next action

Return the final DS authority to SS for independent acceptance.

The DS evidence gate is complete. Recommend that SS authorize the first serious
SER modeling mission under V-B primary / V-A secondary / V-D stress, with
retrieval separate and the protected seed reserved for promotion confirmation.
