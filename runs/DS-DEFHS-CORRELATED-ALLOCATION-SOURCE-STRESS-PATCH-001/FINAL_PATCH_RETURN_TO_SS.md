# Final Patch Return to SS

Mission:

`DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001`

## Verdict

**PATCH_AND_FREEZE**

## Parent authorities

Canonical DS freeze reviewed:

`ds/validation-hardening-002@c7da27a0f7d0927a5070da8cf825d1415546345c`

Adversarial review:

`audit/final-validation-data-redteam-001@5973f06e1a710017776c2f4ced60f892eaf2c76b`

Corrective branch:

`ds/correlated-allocation-source-stress-patch-001`

The exact final Git HEAD is reported externally after final repository
readback; a file cannot contain the SHA of the commit that contains itself.

## Defect 1 — sample-count modulo / quantization

Disposition:

**VALIDATED IN BROADER FORM AND INCORPORATED.**

The red-team correctly found material sample-count structure, but `%128` is
not uniquely exceptional.

Across a predeclared 16-modulus family:

- 960 has Cramer's V approximately 0.2098;
- 128 has approximately 0.1348;
- 128 bootstrap median rank is 12/16;
- after dependency deduplication and 0.10-second duration/dtype/ID conditioning,
  128 family-wise p is approximately 0.133;
- the broader family maximum remains significant at p approximately 0.0005.

Final classification:

**mixed duration/segmentation and source-format quantization structure**.

Patch:

- add Q128/Q960 diagnostic stress;
- keep V-B primary;
- do not create a quantization primary split;
- do not promote remainder automatically as a feature.

## Defect 2 — correlated private allocation

Disposition:

**VALIDATED AS SENSITIVITY AND BOUNDED BY EXPLICIT POLICY.**

The original forced attacks demonstrate real tail sensitivity, but they do not
establish hidden-split probability.

The patch adds class-stratified enrichment/depletion curves at private
fractions 20/30/40/50%, spanning mild, moderate, strong and extreme levels.

High-replication boundary checks show:

- confirmed mild/moderate worst mean RBF margin remains positive,
  approximately +0.00528;
- strong non-forced checked boundary remains positive,
  approximately +0.00331;
- mean reversals occur only under forced extreme composition.

Final ranking-risk classification:

**ONLY FAILS UNDER EXTREME STRESS**

## Train/test shift wording

Reissue as:

**detectable moderate, representation-dependent nonlinear residual shift,
without evidence identifying a single alternate hidden grouping mechanism.**

This does not change V-A from secondary status.

## Final architecture

- V-B: primary;
- V-A: secondary;
- V-D: diagnostic;
- V-C: authoritative view remains rejected;
- Q128/Q960: diagnostic quantization stress;
- correlated-allocation envelope: secondary ranking-risk evidence;
- retrieval: unchanged, separate;
- protected seed 20261001: untouched, confirmation-only.

## Protected gate

**NOT QUERIED.**

## Smallest next action to SS

Accept this bounded patch and resume the planned serious RS SER modeling
program under `POST_REDTEAM_VALIDATION_AUTHORITY.md`.

Do not reopen DS-002 and do not create a new primary CV.
