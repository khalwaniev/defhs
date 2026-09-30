# Validation Freeze Recommendation

## Recommendation

Freeze two complementary 5-fold authorities:

- **V-A**: stratified row-level competition-mimic CV, seed 20260930.
- **V-B**: stratified duplicate-group-safe CV, seed 20260930.

Use **V-B as the primary model-family/generalization guardrail** and V-A as the
competition-mimic view. Final inference may then add an explicit duplicate
retrieval lane for test clips in `TRAIN_TEST_RETRIEVAL_MAP.csv`.

A speaker/source-disjoint V-C is **not frozen yet** because the competition
provides no speaker IDs and an inferred speaker partition has not yet met a
reliability standard.

## Baseline evidence

A fixed handcrafted acoustic RBF-SVM diagnostic over five seeds gives:

- V-A mean macro-F1: **0.680968 ± 0.014148**
- V-B mean macro-F1: **0.582527 ± 0.007615**
- mean V-A − V-B gap: **0.098441**

The approximately 0.10 macro-F1 gap is material evidence that duplicate-aware
validation is necessary.

## Promotion policy

A production SER model must not be promoted from V-A alone. Prefer candidates
that improve V-B credibly; use V-A and OOF ensemble gains as secondary evidence.
Duplicate retrieval is evaluated separately.
