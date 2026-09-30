# Validation Candidates Report — Final Freeze

## V-A — row-level competition-mimic secondary view

Five-fold stratified row-level CV, seed `20260930`.

Exact membership:

`VALIDATION_VA_FOLDS.csv`

SHA-256:

`dcee356b0a66cb73c506bb71a6c57962227d6d0474efd3e4d6c404168308f3d1`

Final role: secondary estimator of competition-like row mixing, including
retrieval-aware pseudo-test behavior.

## V-B — duplicate-safe primary selection authority

Five-fold StratifiedGroupKFold, seed `20260930`, grouped by the frozen
duplicate graph.

Exact membership:

`VALIDATION_VB_FOLDS.csv`

SHA-256:

`87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b`

Final role: primary representation/model-family selection authority.

## V-C — speaker-like stress

**REJECTED AS AN AUTHORITATIVE VALIDATION VIEW.**

ECAPA has been executed. Strict stable clustering almost entirely reproduces
duplicate families; permissive clustering adds speaker-like hypotheses but
becomes materially threshold-dependent. There is no identified cutoff that
supports a reproducible independent speaker-disjoint authority.

ECAPA clusters remain available for diagnostic analysis only.

## V-D — verified recording-format/source stress

Exact membership:

`VALIDATION_VD_REGIMES.csv`

SHA-256:

`f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839`

Final role: robustness stress across verified int16/int32 recording regimes.
It is diagnostic, not the primary competition estimator.

## Prompt/script and latent regimes

Neither ASR prompt families nor joint latent clusters justify a new frozen
validation grouping.

At prompt similarity 0.90, only 15 non-singleton prompt clusters / 46 clips add
structure beyond duplicate families, and no-duplicate train AMI with class is
approximately `0.0075`.

Joint latent clustering is weak and threshold/k-sensitive.

## Retrieval lane

Retain the deterministic duplicate retrieval lane:

- similarity threshold: `0.95`;
- 77 train-test duplicate groups;
- 78 / 209 test clips mapped;
- usable train labels unanimous in every mapped family.

Retrieval remains separate from non-retrieval SER evaluation.

## Protected promotion gate

Exact duplicate-safe membership, seed `20261001`:

`VALIDATION_VP_PROTECTED_FOLDS.csv`

SHA-256:

`b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c`

The protected gate remains untouched and is not an exploratory optimization
oracle.

## Promotion discipline

- gain < `0.005` macro-F1: do not promote without replication and
  non-negative relevant stress evidence;
- gain `0.005-0.010`: require consistent V-B improvement and no material
  V-D regression;
- larger improvements still require protected-gate confirmation before final
  promotion when the candidate has survived development selection.

## Freeze disposition

The completed ECAPA, ASR, eGeMAPS and latent-regime audits do not overturn the
V-A/V-B/V-D backbone.

Final DS disposition:

**REVISE_AND_FREEZE**
