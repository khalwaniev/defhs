# Project State

Status date: 2026-10-01

## Repository authority

Canonical repository: `khalwaniev/defhs`

Canonical local path: `/home/fikar/zingle/defhs`

Active corrective branch:

`ds/correlated-allocation-source-stress-patch-001`

Parent frozen DS authority:

`ds/validation-hardening-002@c7da27a0f7d0927a5070da8cf825d1415546345c`

Adversarial authority:

`audit/final-validation-data-redteam-001@5973f06e1a710017776c2f4ced60f892eaf2c76b`

Governing workflow: `WORKFLOW.md`

## Current phase

**DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001 — COMPLETE.**

Final corrective verdict:

**PATCH_AND_FREEZE**

The adversarial review identified two bounded defects in the DS-002 freeze:
uncatalogued sample-count quantization structure and incomplete correlated
hidden-allocation sensitivity. Both are now classified and controlled without
a primary-validation redesign.

## Preserved validation backbone

### V-B

**Primary representation/model-family selection authority — unchanged.**

Duplicate-family-safe CV remains the main development authority.

### V-A

**Secondary competition-mimic / retrieval-aware view — unchanged role.**

Train/test-shift wording is strengthened to:

> detectable moderate, representation-dependent nonlinear residual shift after
> cross-split duplicate removal, without evidence identifying a single
> alternate hidden grouping mechanism.

This does not justify replacing V-A or treating test as a known separate domain.

### V-C

**Authoritative speaker-like view remains rejected.**

ECAPA structure remains diagnostic/sensitivity evidence only.

### V-D

**Verified int16/int32 recording-format/source stress — unchanged.**

## Patch addition 1 — sample-count quantization stress

The red-team's `samples % 128` finding is real but is not uniquely
exceptional after multiplicity correction.

A bounded family of scientifically plausible quantizations was audited:

`16, 32, 64, 80, 128, 160, 200, 256, 320, 400, 480, 512, 640, 800, 960, 1024`.

Key conclusions:

- modulus 960 is the strongest family member by Cramer's V;
- modulus 128 bootstrap median rank is 12 / 16 and is never top-five in the
  2,000-resample exceptionality check;
- Q128 is extremely associated with dtype;
- under dependency deduplication plus narrow duration/dtype/ID conditioning,
  Q128 loses conservative family-wise significance at 0.10-second and
  0.05-second duration bins;
- the broader quantization family remains non-random.

Final classification:

**mixed duration/segmentation and source-format quantization structure.**

Frozen diagnostic stress summaries:

- Q128: `0 / 43 / 86 / 30 / 94 / OTHER`;
- Q960: `384 / 192 / 576 / 606 / 926 / OTHER`.

These are diagnostic strata only. They are not a new primary split and are not
automatically promoted as model features.

## Patch addition 2 — correlated-allocation envelope

The original class-stratified baseline emulator is retained.

A secondary correlated-allocation sensitivity envelope now covers:

- quantization/source strata;
- dtype/source;
- prompt beyond duplicates;
- speaker-like threshold sensitivities;
- latent clusters;
- duration tails;
- eGeMAPSv02 acoustic outliers;
- retrieval concentration.

Pseudo-private fractions remain:

`20% / 30% / 40% / 50%`.

Mild/moderate enrichment and depletion preserve a positive mean
`FULL_RBF_SVM` advantage in high-replication boundary checks.

The worst confirmed plausible mean margin is approximately:

`+0.00528`

A strong non-forced checked boundary remains positive at approximately:

`+0.00331`.

Mean ranking reversals are confirmed only under forced extreme compositions,
including prompt, Q960, and latent tail scenarios whose pseudo-private
prevalence is far from observed total-test prevalence.

Final ranking-risk classification:

**ONLY FAILS UNDER EXTREME STRESS**

Extreme scenarios remain tail sensitivities, not estimates of hidden
public/private membership probability.

## Retrieval

The deterministic 77-group / 78-test-clip retrieval lane is unchanged and
remains separate from ordinary SER inference.

The adversarial all-pair check found no evidence of transitive false joins.

## Protected promotion gate

`VALIDATION_VP_PROTECTED_FOLDS.csv`

Status:

**UNTOUCHED / CONFIRMATION-ONLY.**

No candidate performance from the protected seed was read, joined, or queried
during this patch.

## Canonical patch artifacts

Under:

`runs/DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001/`

- `MISSION.md`;
- `PATCH_CONFIG.json`;
- `SAMPLE_COUNT_QUANTIZATION_PATCH_REPORT.md`;
- `SAMPLE_COUNT_QUANTIZATION_RESULTS.json`;
- `SAMPLE_COUNT_QUANTIZATION_RANK_STABILITY.csv`;
- `CORRELATED_ALLOCATION_EMULATOR_SPEC.md`;
- `CORRELATED_ALLOCATION_EMULATOR_RESULTS.json`;
- `CORRELATED_ALLOCATION_RANK_STABILITY.csv`;
- `POST_REDTEAM_DATA_UNKNOWN_REGISTER.md`;
- `POST_REDTEAM_VALIDATION_AUTHORITY.md`;
- `FINAL_PATCH_RETURN_TO_SS.md`.

Reproducer:

`scripts/run_ds_defhs_correlated_allocation_source_stress_patch_001.py`

The reproducer explicitly rejects any input path containing
`VP_PROTECTED`.

## Next action

Return the bounded patch to SS.

Recommendation:

**SS should accept `PATCH_AND_FREEZE` and authorize the planned serious RS
SER modeling program under `POST_REDTEAM_VALIDATION_AUTHORITY.md`.**

Do not restart DS-002 and do not create a new primary CV.
