# Train / Test Shift Report — Final Interpretation

## Existing acoustic evidence

From the recovered approximately 402-column acoustic matrix, univariate
train/test differences are mostly small.

Adversarial validation:

- all clips, logistic regression: AUC `0.478 +/- 0.013`;
- all clips, ExtraTrees: AUC `0.489 +/- 0.009`;
- excluding cross-split duplicate families, logistic regression:
  AUC `0.494 +/- 0.017`;
- excluding cross-split duplicate families, ExtraTrees:
  AUC `0.581 +/- 0.010`.

This indicates no strong globally linear split signal, with a modest nonlinear
residual signal after duplicate-covered examples are removed.

## New standardized paralinguistic evidence

openSMILE eGeMAPSv02:

- train/test adversarial logistic AUC mean: `0.476416387656352`;
- largest absolute univariate train/test SMD: approximately `0.150`;
- V-A OOF macro-F1: `0.5753536951338543`;
- V-B OOF macro-F1: `0.5601482021030706`.

Standardized SER descriptors therefore do not expose a new material global
train/test shift.

## Speaker / prompt / latent evidence

ECAPA speaker-like clusters do not yield a stable independent grouping beyond
the duplicate graph at strict thresholds. Chance-adjusted split association is
approximately zero in the strict-to-central region.

ASR reveals some repeated prompts, but at similarity 0.90 only 15
non-singleton clusters / 46 clips add repeated-prompt structure beyond frozen
duplicate families. After duplicate-family clips are removed, prompt/class AMI
is only approximately `0.0075`.

Joint latent clustering has split NMI only approximately
`0.00034-0.00138`.

## Final conclusion

The best-supported description remains:

**broadly common train/test parent mixture with weak-to-modest residual
nonlinear shift, not a strong separate-domain split.**

The exact hidden test/public/private sampling mechanism remains unknown.

No new evidence justifies replacing V-A/V-B, creating a prompt split, or
creating a latent-regime split.

Policy:

- V-A: secondary competition-mimic view;
- V-B: primary duplicate-safe model/representation selection;
- V-D: source-format stress;
- V-C: rejected as an authoritative split;
- do not optimize a model against the adversarial separator.
