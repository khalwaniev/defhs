# Train / Test Shift Report

Univariate train/test differences are mostly small. The largest standardized mean differences are around 0.20, concentrated in log-Mel/silence-related features.

Adversarial validation:
- all clips, logistic regression: AUC 0.478 ± 0.013
- all clips, ExtraTrees: AUC 0.489 ± 0.009
- excluding cross-split duplicate families, logistic regression: AUC 0.494 ± 0.017
- excluding cross-split duplicate families, ExtraTrees: AUC 0.581 ± 0.010

Interpretation: there is no strong globally linear train/test shift, but after removing duplicate-covered examples a modest repeatable nonlinear residual shift is detectable. This is a stress signal, not evidence that test is drawn from a wholly different corpus.

Policy: preserve row-level competition-mimic V-A, duplicate-safe V-B, and source/format stress V-D; require small gains to replicate across these views rather than optimizing to the residual adversarial separator.
