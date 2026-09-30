# Sample-Count Quantization Patch Report

Mission: `DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001`

Protected promotion gate queried: **NO**.

## Executive conclusion

The red-team was correct that sample-count quantization is a material observable
property, but the phrase **"modulo-128 preprocessing/source fingerprint" is too
specific**.

Final classification:

**MIXED DURATION/SEGMENTATION AND SOURCE-FORMAT QUANTIZATION STRUCTURE**

Do not canonize `samples % 128` as a unique source identity, do not create a
new authoritative split from it, and do not automatically add remainder as a
production feature.

Instead, add a bounded **quantization stress matrix** as a diagnostic robustness
view.

## A1 — discovery multiplicity

The canonical adversarial reproducer hard-codes:

- modulus `128`;
- dominant remainders `0 / 30 / 43 / 86 / 94`.

No preserved artifact reconstructs the exact exploratory search that selected
128 or those residues.

Therefore modulus selection is treated as adaptive.

## A2 — bounded quantization family

The correction predeclared a scientifically motivated family covering powers
of two and common 16-kHz frame/block granularities:

`16, 32, 64, 80, 128, 160, 200, 256, 320, 400, 480, 512, 640, 800, 960, 1024`.

For each modulus, the five most prevalent remainders were selected without
using emotion labels; all other residues were collapsed to `OTHER`. Emotion
association was measured by Cramer's V.

A 5,000-permutation **max-statistic across the full family** controls the
post-selection family-wise error.

Key results:

| modulus | Cramer's V | family-wise p |
|---:|---:|---:|
| 960 | 0.209780 | 0.000200 |
| 480 | 0.208403 | 0.000200 |
| 1024 | 0.199199 | 0.000200 |
| 320 | 0.192189 | 0.000200 |
| 80 | 0.191121 | 0.000200 |
| 160 | 0.191121 | 0.000200 |
| 256 | 0.186338 | 0.000200 |
| 512 | 0.173251 | 0.000200 |
| 128 | 0.134824 | 0.000600 |

Thus the broader quantization phenomenon is real, but **128 is not
exceptional**. In 2,000 bootstrap resamples, modulus 128 had median rank 12 of
16, 95% rank interval 10-16, and was never top-five.

The dominant 128 residues are also extremely associated with dtype:

- remainder-category vs dtype Cramer's V: `0.838496`;
- p approximately `5.1e-155`.

The manifest has a deterministic mapping:

- int16 -> 16-bit sample width;
- int32 -> 32-bit sample width.

Therefore sample width does not provide an independent control beyond dtype.

## A3 — duration/source conditioning

The dependency graph was reduced to one representative per duplicate family
plus singletons, excluding the known conflicting duplicate family. This yields
671 dependency-independent rows.

Permutation was then restricted within strata defined by:

- narrow duration bins;
- dtype / sample width regime;
- ID acquisition quartile.

Results:

| duration bin | 128 family-wise p | strongest family modulus | family-max p |
|---:|---:|---:|---:|
| 0.25 s | 0.01999 | 960 | 0.00050 |
| 0.10 s | 0.13293 | 960 | 0.00050 |
| 0.05 s | 0.45477 | 960 | 0.00050 |

At row level with 0.10-second duration + dtype + ID conditioning, the 128
family-wise p is `0.03148`.

Within int16 alone, the `0 / 43 / 86 / OTHER` structure remains emotion
associated:

- Cramer's V `0.13795`;
- p `2.57e-06`.

Interpretation:

- some sample-count quantization structure remains after ordinary duration,
  source-format and acquisition-region controls;
- however, the uniquely privileged `128` claim does not survive conservative
  multiplicity + dependency control;
- the evidence is most consistent with a **mixed segmentation/resampling/
  duration-quantization process whose prevalence also differs by source-format
  regime**.

Exact original preprocessing software/source identity remains unobserved.

## A4 — V-B ranking robustness

Exact non-protected V-B OOF predictions were bootstrapped by row within each
stratum. Macro-F1 is computed using all four emotion classes.

Selected results:

### modulo 128 / remainder 86

n=120.

- BASIC_EXTRATREES: F1 `0.6542`, 95% bootstrap CI `0.5445-0.7558`;
- FULL_RBF_SVM: F1 `0.6140`, CI `0.5195-0.7065`;
- point gap: `+0.0402` for ExtraTrees;
- P(ExtraTrees > RBF): `0.717`;
- top-frequency: ExtraTrees `0.525`, RBF `0.129`.

This is ranking-sensitive, but not deterministic.

### modulo 128 / remainder 30

n=46.

- BASIC_LOGREG: F1 `0.5608`, CI `0.4106-0.6935`;
- FULL_RBF_SVM: F1 `0.5204`, CI `0.3623-0.6510`;
- point gap: `+0.0404`;
- P(BasicLogReg > RBF): `0.691`;
- top-frequency: BasicLogReg `0.533`, RBF `0.225`.

The uncertainty is large and the subgroup is too small to become a ranking
authority.

### modulo 960 / remainder 192

n=85.

- FULL_LOGREG: F1 `0.5010`, CI `0.3798-0.6103`;
- FULL_RBF_SVM: F1 `0.4640`, CI `0.3354-0.5772`;
- point gap: `+0.0370`;
- P(FullLogReg > RBF): `0.740`.

### modulo 960 / remainder 606

n=41.

- BASIC_LOGREG: F1 `0.4451`, CI `0.3006-0.5736`;
- FULL_RBF_SVM: F1 `0.3801`, CI `0.2270-0.5138`;
- point gap: `+0.0651`;
- P(BasicLogReg > RBF): `0.777`.

Again, this is diagnostic sensitivity, not a new validation authority.

## Frozen patch policy

Retain V-B as the primary model/representation selection authority.

Add a **diagnostic quantization stress matrix** using:

1. legacy/source-format-linked Q128 categories:
   `0 / 43 / 86 / 30 / 94 / OTHER`;
2. multiplicity-aware representative Q960 categories:
   `384 / 192 / 576 / 606 / 926 / OTHER`.

These views must never replace aggregate V-B, and subgroup point estimates
must be accompanied by uncertainty.

No automatic remainder feature promotion is authorized.
