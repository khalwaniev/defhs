# DS-DEFHS-DATA-VALIDATION-FOUNDATION-001

## Role

Data Scientist.

## Authority

- Repository: `khalwaniev/defhs`
- Parent authority: `6b0a760e9b973c9c953c571ef8a32b1e031ce39d`
- Branch: `ds/data-validation-foundation-001`
- Governing workflow: `WORKFLOW.md`

## Objective

Freeze the first trustworthy DEFHS data and validation authority before expensive model work.

## Required evidence

1. Reproduce train/test counts, class counts, audio format, durations, and exact PCM duplicates.
2. Build gain/encoding/silence-tolerant near-duplicate fingerprints and groups.
3. Quantify train-train and train-test dependencies and identify conflicting labels.
4. Inspect whether filenames/IDs/order encode source or collection structure.
5. Estimate speaker/source group structure where scientifically defensible.
6. Construct and save:
   - V-A competition-mimic stratified CV;
   - V-B duplicate-safe grouped CV;
   - V-C speaker/source stress CV if grouping is reliable.
7. Implement the official macro-F1 scorer.
8. Run a cheap reproducible acoustic baseline on V-A and V-B to quantify leakage premium.
9. Produce a concise freeze recommendation with known limitations.

## Constraints

- No leaderboard-driven validation design.
- No GPU foundation-model training in this mission.
- Do not silently resolve conflicting duplicate labels.
- Near-duplicate thresholds must be supported by similarity distributions / diagnostics, not arbitrary choices.
- Save all lightweight fold/group artifacts and reports in GitHub.
- Heavy audio/features remain outside GitHub.

## Required return artifacts

- `DATA_AUDIT_SUMMARY.json`
- `AUDIO_METADATA.csv`
- `DUPLICATE_GROUPS.csv`
- `DUPLICATE_CONFLICTS.csv`
- `TRAIN_TEST_DEPENDENCY_REPORT.md`
- `VALIDATION_VA_FOLDS.csv`
- `VALIDATION_VB_FOLDS.csv`
- optional `VALIDATION_VC_FOLDS.csv`
- `BASELINE_VALIDATION_RESULTS.json`
- `VALIDATION_FREEZE_RECOMMENDATION.md`
- `FINAL_RETURN_TO_SS.md`

## Decision gate

Do not freeze validation unless duplicate/source dependencies are explicitly represented and the baseline demonstrates that the folds behave as intended.
