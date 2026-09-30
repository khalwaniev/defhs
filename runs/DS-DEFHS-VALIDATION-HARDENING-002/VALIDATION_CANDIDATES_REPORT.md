# Validation Candidates Report — Closure Reissue

## V-A — row-level competition-mimic

Five-fold stratified row-level CV, seed 20260930.

Exact membership:
`VALIDATION_VA_FOLDS.csv`

SHA-256:
`dcee356b0a66cb73c506bb71a6c57962227d6d0474efd3e4d6c404168308f3d1`

Role: secondary competition-behavior estimator where retrieval analogues may appear.

## V-B — duplicate-safe model-selection guardrail

Five-fold StratifiedGroupKFold, seed 20260930, grouping frozen duplicate families.

Exact membership:
`VALIDATION_VB_FOLDS.csv`

SHA-256:
`87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b`

Role: current primary candidate guardrail for representation/model-family selection.

## V-C — speaker-like stress

**Pending required ECAPA audit. Not frozen.**

The earlier absence of speaker weights was an execution limitation, not sufficient evidence to permanently reject speaker-like grouping.

## V-D — verified recording-format stress

Exact membership:
`VALIDATION_VD_REGIMES.csv`

SHA-256:
`f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839`

Role: stress robustness across int16/int32 recording regimes. It is not the primary competition estimator.

## Protected promotion gate

Exact duplicate-safe membership, seed 20261001:

`VALIDATION_VP_PROTECTED_FOLDS.csv`

SHA-256:
`b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c`

Membership is frozen. No exploratory candidate evaluation is authorized.

## Existing cheap-model stability

Across the executed cheap battery:

- FULL_RBF_SVM ranks highest among the cheap systems on both V-A and V-B;
- V-A SER mean is about 0.702;
- retrieval-aware V-A pipeline mean is about 0.716;
- V-B mean is about 0.623;
- V-A pseudo-test retrieval coverage is about 0.287;
- V-B correctly has zero retrieval coverage by construction.

These results support the V-A/V-B role distinction and remain valid.

## Final-status implication

The V-A/V-B backbone has survived the evidence-completion review so far, but **final validation freeze is withheld** until speaker, ASR/prompt, and eGeMAPS evidence tests whether new grouping/stress structure materially changes these roles.
