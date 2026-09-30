# Project State

Status date: 2026-09-30

## Repository authority
Canonical repository: `khalwaniev/defhs`

Canonical local path: `/home/fikar/zingle/defhs`

Active branch: `ds/validation-hardening-002`

Governing workflow: `WORKFLOW.md`

## Current phase
**DS-DEFHS-VALIDATION-HARDENING-002 completed with `REVISE_AND_FREEZE`.**

The DS-001 `PASS_FREEZE_CANDIDATE` backbone was reproduced and hardened. Serious RS modeling may now begin under the final validation authority in:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/FINAL_VALIDATION_AUTHORITY.md`

## Canonical data authority
- Drive ZIP: `/DEFHS/raw/dataverse-detecting-emotions-from-hindi-speech.zip`
- file ID: `1D0DcnbK0vrJGTsvtb7-l7vnpdfNxc-nH`
- size: 99,298,085 bytes
- SHA-256: `100b38e6ed69542df88c1d295932a7a4c1914cd931ee64f7c6c848f6053bf214`
- verified extracted mirror: `/DEFHS/competition_extracted`
- supplied examples: 826 train + 209 test = 1,035

The competition prose statement of 1,036 samples remains unresolved; the supplied package is the operational authority.

## Final structural findings
- IDs are exactly 1..1035 and train/test assignment is broadly interleaved/random-like by ID.
- 227 near-duplicate groups cover 467 clips.
- 77 train↔test groups affect 78 test clips.
- duplicate graph is stable through approximately 0.974 similarity; frozen threshold remains 0.95.
- one conflicting duplicate-label family: IDs 75 / 636 / 878.
- recording-format/source heterogeneity is real: 933 int16 and 102 int32 clips.
- global train/test shift is weak; a modest nonlinear residual shift remains after excluding cross-split duplicate families.
- true speaker IDs, acted/spontaneous membership, prompt/script identity and hidden public/private assignment are not observable from the current package and are explicitly controlled rather than guessed.

## Frozen validation architecture
- **V-B**: duplicate-safe 5-fold CV, primary model-selection guardrail.
- **V-A**: row-level stratified 5-fold CV, competition-mimic secondary view.
- **V-D**: int16/int32 recording-format stress.
- **V-C**: not frozen because reliable speaker identities are unavailable.
- deterministic duplicate retrieval remains a separate inference lane for the 78 mapped test clips.
- a new duplicate-safe protected promotion seed `20261001` is reserved for promotion checkpoints and must not be used as an unlimited tuning oracle.

## Heavy derived artifact
Drive folder: `/DEFHS/ds_validation_002/`

Full acoustic matrix:
- file ID: `1vi6Wgcth_3BX7izqIMBFa7I1KMTU38RK`
- SHA-256: `d8769829f6e2ca351e96068e64d89b95977cca83acc4a92c14239f0f793ff42d`

## Next action
Return to SS. The next scientific bottleneck is serious speech/emotion representation modeling under the frozen V-B/V-A/V-D authority, with protected-gate access reserved for promotion decisions.
