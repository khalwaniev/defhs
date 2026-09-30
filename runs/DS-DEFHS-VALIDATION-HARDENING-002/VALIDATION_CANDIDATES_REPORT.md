# Validation Candidates Report

## V-A — competition-mimic
Five-fold stratified row-level CV, seed 20260930. Role: estimate behavior when the supplied train/test assignment is approximately row-random and retrieval analogues can occur.

## V-B — duplicate-safe primary model-selection guardrail
Five-fold StratifiedGroupKFold, seed 20260930, grouping exact/near-duplicate families. Role: prevent duplicate memorization from selecting representations.

## V-C — speaker-disjoint
Not frozen. Speaker identity is not reliably recoverable from current executed evidence.

## V-D — verified recording-format/source stress
Leave-one-dtype-regime-out stress using int16 vs int32. Role: robustness diagnostic only; it is intentionally harder than the likely competition mixture and is not the main leaderboard estimator.

## Cheap-model stability
Across three examined seeds:
- FULL_RBF_SVM ranks highest among the cheap systems on both V-A and V-B.
- V-A SER mean ~0.702; retrieval-aware pipeline mean ~0.716.
- V-B mean ~0.623.
- retrieval coverage inside V-A pseudo-test folds averages ~0.287; V-B correctly gives zero retrieval coverage by construction.

This stable ordering supports the role distinction: V-A estimates production-like behavior; V-B is the model-family guardrail.
