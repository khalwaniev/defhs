# Final Validation Authority — Closure Reissue

## Verdict

**FAIL_NOT_READY**

This verdict does **not** invalidate the preserved V-A/V-B science. It means the independent closure standard is not yet satisfied because mandatory speaker, ASR/prompt, and standardized paralinguistic audits remain unexecuted.

## Preserved provisional validation backbone

### V-A — competition-mimic secondary view

Five-fold stratified row-level CV, seed 20260930.

Canonical membership:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VA_FOLDS.csv`

SHA-256:

`dcee356b0a66cb73c506bb71a6c57962227d6d0474efd3e4d6c404168308f3d1`

Role: approximate row-random competition behavior and allow retrieval analogues inside pseudo-test evaluation.

### V-B — duplicate-safe model-selection guardrail

Five-fold duplicate-family-safe StratifiedGroupKFold, seed 20260930.

Canonical membership:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VB_FOLDS.csv`

SHA-256:

`87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b`

Role: prevent exact/near-duplicate memorization from selecting a representation or model family.

### V-C — speaker-like stress

**Not frozen. Mandatory pretrained speaker audit pending.**

Do not infer speaker IDs from low-level pitch/acoustic features. V-C may be added only after the ECAPA audit establishes sufficiently reliable speaker-like grouping.

### V-D — verified recording-format/source stress

Canonical membership/regime definition:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VD_REGIMES.csv`

SHA-256:

`f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839`

Role: stress transfer across verified int16/int32 recording regimes. It remains diagnostic, not the primary leaderboard estimator.

## Protected promotion gate

Duplicate-safe StratifiedGroupKFold, seed 20261001.

Canonical exact membership:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VP_PROTECTED_FOLDS.csv`

SHA-256:

`b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c`

Fold sizes: 166 / 166 / 165 / 165 / 164.

This membership is frozen byte-for-byte. It has not been authorized as an exploratory tuning oracle and must remain protected.

## Retrieval lane

The deterministic duplicate-retrieval logic remains valid:

- frozen similarity threshold: 0.95;
- 77 train↔test groups;
- 78 / 209 test clips mapped;
- usable train labels are unanimous inside every mapped cross-split group.

Canonical map:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/RETRIEVAL_MAP_FINAL.csv`

SHA-256:

`e08f7d06c13d64a1d365d7ae6fa741d6e831dea8816de6663d4a9c0eb113d2a7`

Retrieval must remain separate from non-retrieval SER performance.

## Current private-LB emulator

The existing retrieval-aware V-A pseudo-test simulation and public-fraction sensitivity remain valid evidence. The actual public fraction and hidden assignment remain unknown.

Canonical results:

`PRIVATE_LB_EMULATOR_RESULTS.json`

SHA-256:

`2c5a4d06e8dc24268b4ce410f266940977918df030fe6fa10ceaee25d400c371`

The emulator remains an emulator, never a claim of equivalence to the real private leaderboard.

## Heavy acoustic authority

Drive path:

`/DEFHS/ds_validation_002/ACOUSTIC_FEATURES_FULL.csv`

Drive file ID:

`1vi6Wgcth_3BX7izqIMBFa7I1KMTU38RK`

Size: 7,787,538 bytes

Verified SHA-256:

`d8769829f6e2ca351e96068e64d89b95977cca83fb49f0ef7d0d597f11c06a53`

This hash supersedes the incorrectly transcribed checksum in the previous provisional authority.

## Required evidence before freeze

Final `PASS_FREEZE` or `REVISE_AND_FREEZE` is blocked until:

- actual ECAPA speaker embeddings are extracted and audited;
- actual Hindi ASR transcripts are produced and prompt structure audited;
- actual openSMILE eGeMAPSv02 descriptors are extracted and analyzed;
- acted/spontaneous latent structure is reconsidered jointly;
- the resulting evidence is preserved and the unknown register/certificate are reissued.

## Modeling authorization

**Do not start the main RS SER modeling mission from this reissued authority.**

Return to SS with `FAIL_NOT_READY` and execute only the bounded evidence-completion closure.
