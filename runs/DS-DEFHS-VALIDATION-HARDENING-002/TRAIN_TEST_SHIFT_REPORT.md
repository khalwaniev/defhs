# Train / Test Shift Report — Closure Reissue

## Existing evidence retained

From the recovered ~402-column acoustic matrix, univariate train/test differences are mostly small. The largest standardized mean differences are around 0.20 and are concentrated in log-Mel/silence-related descriptors.

Adversarial validation:

- all clips, logistic regression: AUC 0.478 ± 0.013;
- all clips, ExtraTrees: AUC 0.489 ± 0.009;
- excluding cross-split duplicate families, logistic regression: AUC 0.494 ± 0.017;
- excluding cross-split duplicate families, ExtraTrees: AUC 0.581 ± 0.010.

Interpretation remains: no strong globally linear split signal is present, but a modest repeatable nonlinear residual signal appears after duplicate-covered examples are removed. This is not evidence that test is from a wholly different corpus.

## Closure limitation

The shift conclusion has not yet been challenged with:

- standardized openSMILE eGeMAPSv02 descriptors;
- pretrained speaker embeddings / speaker-like cluster proportions;
- ASR-derived prompt/script family proportions.

These are mandatory closure analyses.

Therefore current train/test-shift evidence remains **valid but incomplete**. It must not be promoted from “modest residual shift under current representations” to a final statement about speaker/prompt/regime shift until those artifacts exist.

Current policy remains provisional:

- preserve V-A row-level competition-mimic;
- preserve V-B duplicate-safe guardrail;
- preserve V-D recording-format stress;
- do not add V-C until speaker evidence exists;
- do not optimize against the adversarial separator.
