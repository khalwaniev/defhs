# Correlated-Allocation Emulator Specification

Mission: `DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001`

Protected promotion gate queried: **NO**.

## Purpose

This specification does not attempt to predict the hidden public/private
membership.

Its purpose is to bound model-ranking risk when hidden allocation is correlated
with observable or inferred structure.

Three evidence layers must remain distinct:

1. **baseline emulator** — approximately IID, class-stratified allocation;
2. **plausible correlated sensitivity** — mild/moderate subgroup enrichment or
   depletion;
3. **tail stress** — strong or forced extreme subgroup concentration.

No sensitivity scenario is assigned a probability of being the real hidden
split.

## Baseline

Retain the existing retrieval-aware V-A emulator as the reference.

The patch re-evaluates the same cheap candidate set:

- `BASIC_EXTRATREES`;
- `BASIC_LOGREG`;
- `FULL_LOGREG`;
- `FULL_RBF_SVM`.

Only existing non-protected V-A pipeline OOF predictions are scored.

## Exact metric mechanics

For every partition:

- compute macro-F1 over the four official emotion classes separately on
  pseudo-public and pseudo-private rows;
- combine:

`0.40 * public_macro_f1 + 0.60 * private_macro_f1`.

The 0.40/0.60 score weights are not interpreted as row fractions.

The correlated envelope explicitly tests pseudo-private fractions:

`0.20 / 0.30 / 0.40 / 0.50`.

## Allocation model

Within each emotion class, subgroup membership changes the odds of assignment
to pseudo-private.

Counts are drawn from Fisher's noncentral hypergeometric distribution, then
rows are sampled uniformly conditional on the subgroup count.

This keeps class composition approximately fixed while isolating correlated
allocation risk.

Private-membership odds:

| level | odds ratio | interpretation |
|---|---:|---|
| mild depletion | 2/3 | plausible sensitivity |
| moderate depletion | 1/2 | plausible sensitivity |
| strong depletion | 1/4 | strong tail |
| extreme depletion | 0 | forced tail |
| baseline | 1 | approximately random |
| mild enrichment | 1.5 | plausible sensitivity |
| moderate enrichment | 2 | plausible sensitivity |
| strong enrichment | 4 | strong tail |
| extreme enrichment | infinity | forced tail |

The red-team's original forced-allocation attack is retained separately as an
extreme reference. Its reproducer does not class-stratify the forced subgroup
allocation, so its strongest latent scenario couples subgroup concentration
with class-composition shift. It is valid as a tail stress, not as an estimate
of hidden-split probability.

## Stress strata

The envelope includes:

### sample-count / quantization

- Q128 residues: 0, 43, 86, 30, 94;
- Q960 rank-sensitive residues: 192 and 606.

### verified source-format

- int32 versus complement.

### prompt

- prompt-similarity-0.90 non-singleton structure extending beyond duplicate
  families.

### speaker-like sensitivities

- ECAPA agglomerative d0.25, d0.30 and d0.35 clusters extending beyond the
  duplicate graph.

These remain threshold-sensitive diagnostics, never organizer speaker IDs.

### latent regimes

- each joint k=4 cluster.

These remain unnamed sensitivity strata.

### duration / paralinguistic extremeness

- shortest training-duration 20% threshold, applied to all rows;
- longest training-duration 20% threshold;
- top 20% eGeMAPSv02 PCA-distance acoustic outlier score, threshold fitted on
  train and applied to test.

### retrieval composition

- retrieval-covered versus non-covered rows.

### development difficulty tail

- V-A rows on which at most one of four cheap pipelines is correct.

This last stratum is label-defined and therefore has no observable test
prevalence; it is tail stress only, never a hidden-group claim.

## Prevalence reporting

Every observable stratum reports:

- train prevalence;
- actual total-test prevalence;
- pseudo-private prevalence;
- pseudo-public prevalence;
- private/train enrichment ratio;
- deviation from observable total-test prevalence.

A forced allocation that moves a rare test subgroup to a very large
pseudo-private prevalence must be labeled extreme even if it reverses ranking.

## Replication

The full envelope uses a broad 672-scenario screen to find the boundary of the
risk surface.

Decision-boundary scenarios are then re-run at 1,500-2,000 replicates.

Final qualitative classification is based on the high-replication boundary
checks, not on a single coarse scenario.

## Final decision rule

Use:

- `ROBUST UNDER PLAUSIBLE STRESS` when mild/moderate correlations preserve
  the mean winner;
- `ONLY FAILS UNDER EXTREME STRESS` when mean ranking reverses only in forced
  tail compositions;
- `MATERIALLY FRAGILE UNDER MODEST CORRELATION` when mild/moderate tilts
  produce a stable material reversal.

The correlated envelope is secondary risk evidence. It does not replace V-B.
