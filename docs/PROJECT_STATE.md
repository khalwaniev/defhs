# Project State

Status date: 2026-09-30

## Repository authority

Canonical repository: `khalwaniev/defhs`

Canonical local path: `/home/fikar/zingle/defhs`

Active branch: `ds/validation-hardening-002`

Governing workflow: `WORKFLOW.md`

## Current phase

**DS-DEFHS-VALIDATION-HARDENING-002 — final evidence-completion closure.**

Current verdict:

**FAIL_NOT_READY**

The earlier `REVISE_AND_FREEZE` at `44422afbcc880ef0a46044ae7c81f5f9393540a3` is retained only as a historical provisional freeze candidate. Independent SS review correctly identified missing canonical artifacts plus unexecuted speaker/ASR/standardized-paralinguistic evidence.

The artifact/fold-preservation gap has now been repaired. The scientific execution gap remains.

## Canonical data authority

Raw archive:

- Drive path: `/DEFHS/raw/dataverse-detecting-emotions-from-hindi-speech.zip`
- file ID: `1D0DcnbK0vrJGTsvtb7-l7vnpdfNxc-nH`
- size: 99,298,085 bytes
- SHA-256: `100b38e6ed69542df88c1d295932a7a4c1914cd931ee64f7c6c848f6053bf214`

Supplied examples: 826 train + 209 test = 1,035.

The competition prose statement of 1,036 remains a genuine unresolved metadata discrepancy.

## Preserved verified structure

- IDs exactly 1..1035;
- train/test assignment heavily interleaved and broadly row-random by simple ID diagnostics;
- 227 near-duplicate groups / 467 clips;
- 77 train↔test groups / 78 affected test clips;
- duplicate threshold gap remains extremely sharp;
- one conflicting duplicate-label family: IDs 75 / 636 / 878;
- int16/int32 recording heterogeneity is verified;
- global train/test shift weak, with modest nonlinear residual shift after cross-split duplicates are removed;
- V-A/V-B cheap-model and retrieval-aware evidence preserved;
- private-LB fraction sensitivity preserved.

## Exact canonical validation memberships

- V-A: `VALIDATION_VA_FOLDS.csv`, SHA-256 `dcee356b0a66cb73c506bb71a6c57962227d6d0474efd3e4d6c404168308f3d1`
- V-B: `VALIDATION_VB_FOLDS.csv`, SHA-256 `87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b`
- protected seed 20261001: `VALIDATION_VP_PROTECTED_FOLDS.csv`, SHA-256 `b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c`
- V-D: `VALIDATION_VD_REGIMES.csv`, SHA-256 `f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839`

The protected gate remains unqueried for routine optimization.

## Heavy artifact authority

Full acoustic matrix:

- Drive: `/DEFHS/ds_validation_002/ACOUSTIC_FEATURES_FULL.csv`
- file ID: `1vi6Wgcth_3BX7izqIMBFa7I1KMTU38RK`
- size: 7,787,538 bytes
- verified SHA-256: `d8769829f6e2ca351e96068e64d89b95977cca83fb49f0ef7d0d597f11c06a53`

Canonical recovered lightweight evidence is mirrored under:

`/DEFHS/ds_validation_002/canonical_evidence/`

## Remaining bottleneck

Final validation acceptance is blocked on actual execution of:

- pretrained ECAPA speaker embeddings;
- Hindi ASR / prompt structure;
- openSMILE eGeMAPSv02;
- joint acted/spontaneous latent-regime reconsideration.

Canonical executors are committed in `scripts/run_ds002_*`.

## Next action

Return to SS. Do not start main SER modeling. Execute only the bounded closure in a network-enabled environment with secure access to the private competition data, then reissue the final evidence states and validation authority.
