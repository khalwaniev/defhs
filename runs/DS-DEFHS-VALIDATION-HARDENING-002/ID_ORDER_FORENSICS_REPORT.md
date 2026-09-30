# ID / Order Forensics Report

IDs span exactly 1..1035. Train/test assignment is heavily interleaved rather than contiguous.

Diagnostics:
- observed train/test runs: 331
- random-assignment expectation: ~334.6
- runs z-score: -0.35
- ID-only adversarial split AUC mean: ~0.508
- strongest tested modulo association was not significant at conventional thresholds
- same-label rates across short/medium ID lags remain near the four-class chance scale

Encoding regimes are also interleaved through the ID range; int32 clips do not form one contiguous acquisition block.

Conclusion: there is no defensible evidence that raw ID/order itself is a useful leakage feature or a basis for validation grouping. ID remains an identifier, not a modeling feature.
