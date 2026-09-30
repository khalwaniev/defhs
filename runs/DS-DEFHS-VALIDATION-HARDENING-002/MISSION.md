# DS-DEFHS-VALIDATION-HARDENING-002

## Role
Data Scientist

## Parent authority
`14dcd47d2250b1bb2e39a4c37aadf2d92fc1db9a`

## Objective
Convert the current PASS_FREEZE_CANDIDATE into a final validation authority, or reject it with evidence.

## Scope: decision-relevant EDA only

1. Source/order structure
   - test ID ordering, train/test interleaving, contiguous regions, filename patterns;
   - bit depth, duration, loudness, silence, spectral and recording-condition clusters;
   - quantify train/test distribution similarity and subgroup imbalance.

2. Label integrity
   - audit the known duplicate-label conflict;
   - classwise acoustic separability and potential annotation-noise outliers;
   - do not relabel examples without defensible evidence.

3. Speaker/source inference
   - extract a standard pretrained speaker embedding;
   - cluster with multiple thresholds/methods;
   - test cluster stability and whether clusters explain train/test dependencies;
   - freeze V-C only if inferred groups are reliable enough to be scientific authority.

4. Duplicate retrieval stress test
   - verify near-duplicate groups under at least one independent representation;
   - quantify threshold sensitivity;
   - confirm all proposed test retrieval labels remain invariant.

5. Validation diagnostics
   - class balance per fold;
   - duplicate/source balance per fold;
   - fold difficulty and variance;
   - compare V-A/V-B on multiple cheap model families, not only one RBF-SVM;
   - test whether model ranking is stable enough for selection.

6. Freeze decision
   - freeze V-A/V-B (and V-C only if justified), or revise with explicit evidence;
   - define primary/secondary/stress-test roles;
   - define model-promotion and ensemble evidence requirements;
   - define the deterministic retrieval lane separately from SER scoring.

## Stop rule
Stop EDA when remaining analyses are unlikely to alter validation, model ranking, or final inference. Do not pursue descriptive plots without decision value.

## Required return
- `EDA_DECISION_REPORT.md`
- `SOURCE_STRUCTURE_REPORT.md`
- `LABEL_INTEGRITY_REPORT.md`
- `SPEAKER_GROUPING_REPORT.md`
- `RETRIEVAL_STRESS_TEST.json`
- `VALIDATION_STABILITY_RESULTS.json`
- `FINAL_VALIDATION_AUTHORITY.md`
- `FINAL_RETURN_TO_SS.md`

## Decision gate
Foundation-model training may begin only after this mission returns PASS_FREEZE or an explicitly revised validation authority.
