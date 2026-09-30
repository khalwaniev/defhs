# EDA Master Report — DS-DEFHS-VALIDATION-HARDENING-002

Status: **final-closure continuation in progress; final freeze not yet justified**.

## Preserved verified foundation

The following evidence has survived the independent closure review and remains valid:

- canonical package: 826 train + 209 test = 1,035 supplied clips;
- IDs form exactly 1..1035 with no missing supplied ID;
- all supplied WAVs are mono 16 kHz;
- 933 int16 and 102 int32 recordings;
- 227 near-duplicate connected groups containing 467 clips;
- 77 train↔test duplicate groups affecting 78 test clips;
- 257 high-similarity duplicate edges;
- duplicate-pair minimum about 0.974119 versus next non-cluster waveform similarity about 0.209360;
- duplicate membership is stable through approximately 0.974 similarity;
- one conflicting training duplicate family: IDs 75 / 636 / 878 with neutral / sad / neutral;
- ID/order diagnostics are consistent with a heavily interleaved, broadly row-random train/test assignment rather than trivial ID leakage;
- verified int16/int32 source/recording heterogeneity materially changes transfer difficulty;
- all-data adversarial validation is near chance; after excluding cross-split duplicate families a modest nonlinear residual split signal remains (ExtraTrees mean AUC about 0.581);
- V-A and V-B cheap-model results, retrieval simulation, and public/private-fraction sensitivity remain valid.

## Canonical artifact repair completed

The closure continuation recovered transient artifacts and now preserves exact canonical copies in GitHub and in:

`/DEFHS/ds_validation_002/canonical_evidence/`

Canonical membership files now exist for:

- V-A row-level folds;
- V-B duplicate-safe folds;
- protected duplicate-safe promotion folds (seed 20261001);
- V-D int16/int32 regime membership.

The protected membership SHA-256 is:
`b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c`.

The protected gate has **not** been queried for exploratory candidate performance.

## Heavy acoustic artifact

`/DEFHS/ds_validation_002/ACOUSTIC_FEATURES_FULL.csv`

Drive file ID: `1vi6Wgcth_3BX7izqIMBFa7I1KMTU38RK`

Size: 7,787,538 bytes

Verified SHA-256:
`d8769829f6e2ca351e96068e64d89b95977cca83fb49f0ef7d0d597f11c06a53`

This corrects the checksum transcribed in the earlier provisional authority.

## Remaining mandatory evidence

Three controlling-mission analyses have **not yet been executed successfully**:

1. pretrained speaker-verification embeddings over all 1,035 clips;
2. Hindi ASR over all 1,035 clips followed by prompt/script analysis;
3. standardized openSMILE eGeMAPSv02 extraction and validation/shift audit.

Therefore reliable speaker-like grouping, train/test speaker-like overlap, prompt/script families, and the strengthened acted/spontaneous reconsideration cannot yet receive final evidence states.

Execution-ready reproducible scripts are now canonical:

- `scripts/run_ds002_speaker_ecapa_audit.py`
- `scripts/run_ds002_asr_prompt_audit.py`
- `scripts/run_ds002_opensmile_egemaps_audit.py`
- `scripts/run_ds002_latent_regime_joint_audit.py`
- `requirements/ds002_closure.txt`

The current ChatGPT runtime has the private audio and can perform CPU analyses, but it has no usable network path for acquiring the required public pretrained weights/packages. A secure GitHub Actions workaround is also not available because the raw archive is private in Google Drive and no authenticated Drive secret can be injected through the available GitHub tools. The data has not been made public merely to bypass this limitation.

## Current validation interpretation

The V-A/V-B backbone remains the strongest current candidate and has not been falsified:

- V-B: primary duplicate-safe model-selection guardrail;
- V-A: secondary competition-mimic/retrieval-aware view;
- V-D: verified recording-format stress;
- V-C: pending actual speaker-embedding evidence;
- protected seed 20261001: membership frozen, routine evaluation prohibited.

This is a **provisional preserved architecture**, not a final accepted freeze.

## Closure decision

Because the governing closure explicitly requires actual speaker embeddings, actual Hindi ASR, and standardized paralinguistic evidence before final acceptance, this mission currently returns:

**FAIL_NOT_READY**

This verdict means the existing science is preserved but evidence completion is unfinished. It does not invalidate the current V-A/V-B results.
