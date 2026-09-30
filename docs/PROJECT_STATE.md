# Project State

Status date: 2026-09-30

## Repository authority

Canonical repository:

`khalwaniev/defhs`

Canonical local path:

`/home/fikar/zingle/defhs`

Current active scientific branch:

`ds/validation-hardening-002`

Current active branch authority must be read from the live Git branch before execution.

Governing workflow:

`WORKFLOW.md`

## Current phase

**DS — exhaustive data understanding + validation hardening.**

Repository bootstrap is complete.

The first DS foundation mission,
`DS-DEFHS-DATA-VALIDATION-FOUNDATION-001`, returned
`PASS_FREEZE_CANDIDATE`, not final validation freeze.

The active mission is:

`DS-DEFHS-VALIDATION-HARDENING-002`

Its purpose is to eliminate all material uncertainty about the supplied data
that could affect leakage handling, grouping, validation design, private-LB
emulation, model-family selection, external-data adaptation, ensembling, or
final inference.

Serious foundation-model fine-tuning is blocked until this mission returns a
final validation authority.

## Canonical data authority

Immutable raw archive:

- Google Drive: `/DEFHS/raw/dataverse-detecting-emotions-from-hindi-speech.zip`
- file ID: `1D0DcnbK0vrJGTsvtb7-l7vnpdfNxc-nH`
- size: `99,298,085 bytes`
- SHA-256:
  `100b38e6ed69542df88c1d295932a7a4c1914cd931ee64f7c6c848f6053bf214`

Verified extracted Drive mirror:

- path: `/DEFHS/competition_extracted`
- folder ID: `1d4A0b7_t_kUSwkyZkJ6al3R-vzwmHmvq`
- verified files: 1,038
- verified WAV files: 1,035
- `rclone check`: 0 differences, 1,038 matching files

Fast local working copy:

`/home/fikar/zingle/defhs/data/raw/competition/SRCASW-BhavVaani`

Data-access authority:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_ACCESS_AUTHORITY.md`

Canonical data manifest:

`manifests/DEFHS_COMPETITION_DATA_20260930.json`

## Verified competition-data state

Current verified package facts include:

- train: 826 rows
- test: 209 rows
- supplied train+test total: 1,035 examples
- competition prose states 1,036 samples; discrepancy unresolved
- all inspected audio sample rates: 16 kHz
- median clip duration: approximately 2.88 s
- duration range: approximately 1.008 to 11.2 s
- both int16 and int32 PCM are present

Current near-duplicate evidence from DS-001:

- 227 near-duplicate groups
- 467 clips belong to those groups
- 77 train↔test groups
- 78 / 209 test clips affected
- weakest duplicate-cluster similarity: approximately 0.974119
- strongest non-cluster similarity: approximately 0.209360
- all cross-split duplicate groups have unanimous training labels
- one known conflicting training duplicate group exists

Cheap five-seed acoustic diagnostic:

- V-A row-level mean macro-F1: approximately 0.680968
- V-B duplicate-safe mean macro-F1: approximately 0.582527
- observed leakage premium: approximately +0.098441

These are evidence to be revalidated/hardened by DS-002, not permission to skip
the active mission.

## Official competition facts currently recorded

- task: Hindi speech emotion recognition
- classes: angry, happy, neutral, sad
- official metric: macro F1
- described corpus includes acted and spontaneous speech
- final score:
  `0.40 * public_score + 0.60 * private_score`

The 0.40/0.60 score weighting must not be assumed to equal the public/private
sample fraction.

Internal validation should mimic the hidden/private data-generating process as
closely and defensibly as possible, but must never be described as guaranteed
to reproduce the actual private leaderboard.

## Current bottleneck

The current bottleneck is **not model choice**.

It is establishing a final, trustworthy empirical understanding of the data and
a frozen validation/private-LB-emulation authority.

Open decision-relevant questions include, among others:

- full duplicate/transformation structure;
- label integrity and annotation-noise policy;
- speaker overlap and reliable speaker grouping;
- recording-source/batch structure;
- acted-versus-spontaneous latent structure;
- transcript/prompt/script structure;
- ID/acquisition-order information;
- train/test distribution shift;
- which validation mechanism best approximates competition evaluation;
- which validations should be primary, secondary, or stress-only;
- how to simulate the retrieval lane inside pseudo-test folds;
- how to protect validation from adaptive overfitting.

## Next decision

DS-002 must return one of:

- `PASS_FREEZE`
- `REVISE_AND_FREEZE`
- `FAIL_NOT_READY`

Only after a defensible final freeze should SS authorize the first serious RS
modeling mission (emotion-specialized / SSL / Whisper representation and
fine-tuning research).
