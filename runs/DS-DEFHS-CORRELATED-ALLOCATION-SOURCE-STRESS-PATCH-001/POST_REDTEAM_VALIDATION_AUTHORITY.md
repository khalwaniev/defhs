# Post-Red-Team Validation Authority

Mission: `DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001`

## Final verdict

**PATCH_AND_FREEZE**

The adversarial review found two real bounded defects, but the corrective
analysis does not support a material redesign.

The existing validation backbone survives with two additions:

1. a diagnostic sample-count quantization stress matrix;
2. a correlated hidden-allocation sensitivity envelope for leaderboard-risk
   assessment.

## V-B — primary authority

**UNCHANGED.**

Duplicate-family-safe V-B remains the primary representation/model-family
selection authority.

The new quantization subgroup analysis shows rank heterogeneity that aggregate
V-B alone can hide, but the small-group reversals are not sufficiently certain
or independently identified to replace V-B.

Policy for serious model research:

- select model/representation families primarily on aggregate V-B;
- for close candidates, report Q128/Q960 diagnostic subgroup performance with
  uncertainty;
- do not optimize exclusively to any remainder category.

## V-A — secondary competition-mimic view

**UNCHANGED ROLE; SHIFT WORDING REVISED.**

V-A remains secondary and retrieval-aware.

Final train/test wording:

> There is detectable moderate, representation-dependent nonlinear residual
> train/test shift after cross-split duplicate removal, without evidence
> identifying a single alternate hidden grouping mechanism.

The no-cross-duplicate full-acoustic nonlinear adversarial AUC replicated at
approximately `0.620-0.644`, while same-configuration permutations center
near 0.50.

This is stronger than the previous "weak-to-modest" wording, but it does not
justify treating test as a separate known domain or replacing V-A.

## V-C — speaker-like view

**AUTHORITATIVE V-C REMAINS REJECTED.**

No new evidence overturns the ECAPA threshold/algorithm stability conclusion.

Speaker-like clusters may enter the correlated-allocation envelope only as
sensitivity strata.

## V-D — recording-format/source stress

**UNCHANGED.**

The int16/int32 regime remains a verified diagnostic source-format stress.

Sample-count quantization is correlated with dtype but is not reducible to dtype
alone, so the new quantization stress complements V-D rather than replacing it.

## New Q stress — sample-count quantization

This is a **diagnostic stress matrix**, not a new primary CV.

Freeze two complementary summaries:

### Q128 legacy/source-format view

`0 / 43 / 86 / 30 / 94 / OTHER`

### Q960 multiplicity-aware view

`384 / 192 / 576 / 606 / 926 / OTHER`

Rationale:

- Q128 captures the red-team-discovered dtype-linked structure and its rank
  reversals;
- Q960 is the strongest member of the bounded multiplicity-controlled family;
- 480 is nearly redundant with 960 and is not separately elevated.

All subgroup scores must carry uncertainty.

No remainder is promoted automatically as a predictive feature.

## Private-LB emulator authority

The emulator now has three layers.

### 1. Baseline

Retain the existing approximately IID class-stratified V-A retrieval-aware
emulator.

### 2. Plausible correlated envelope

At pseudo-private fractions 20/30/40/50%, apply class-stratified subgroup
private-membership odds:

- mild: 2/3 or 1.5;
- moderate: 1/2 or 2.

Across the broad screen, aggregate RBF mean advantage remained positive.

High-replication boundary checks confirm:

- worst confirmed plausible mean RBF-minus-best-alternative:
  approximately `+0.00528`;
- confirmed plausible reversal frequency can be nonzero per replicate, but the
  mean winner remains RBF.

Classification:

**ROBUST UNDER PLAUSIBLE STRESS**

### 3. Strong / extreme tails

Strong non-forced stress is retained as a warning layer.

A 2,000-replicate strong speaker-like depletion check still has positive mean
RBF margin approximately `+0.00331`.

Forced extreme tails can reverse mean ranking:

- prompt90 beyond-duplicate forced enrichment:
  mean RBF gap approximately `-0.00696`;
- Q960 remainder 192 forced enrichment:
  approximately `-0.00514`;
- latent k4 cluster 3 forced enrichment:
  approximately `-0.00666`.

These require enormous composition distortions. For example:

- prompt90 beyond-duplicate prevalence is about 2.87% in observed total test
  but about 24.39% in the forced 20% pseudo-private partition;
- Q960 remainder 192 is about 6.70% in observed total test but about 48.78% in
  forced pseudo-private;
- latent k4 cluster 3 is about 29.67% in observed test but about 78.66% in
  forced pseudo-private.

Final ranking-risk classification:

**ONLY FAILS UNDER EXTREME STRESS**

The original red-team forced latent attack remains a valid extreme tail, but
its reproducer is not class-stratified; it couples subgroup concentration with
class-composition shift and must not be interpreted as hidden-split
probability.

## Retrieval lane

**UNCHANGED.**

Keep the deterministic 78-test-clip retrieval lane separate from ordinary SER.

The adversarial all-pair duplicate check found no transitive false join.

## Protected promotion gate

`VALIDATION_VP_PROTECTED_FOLDS.csv`

Status:

**UNTOUCHED.**

No protected candidate performance was read or used by this patch.

The gate remains confirmation-only.

## Patched decision system

Final frozen architecture:

1. **V-B primary** model/representation selection;
2. **V-A secondary** competition-mimic / retrieval-aware evidence;
3. **V-D diagnostic** verified source-format stress;
4. **Q128/Q960 diagnostic** sample-count quantization stress;
5. **correlated-allocation envelope** for finalists / close ranking decisions;
6. **retrieval lane separate and fixed**;
7. **protected seed 20261001 confirmation-only**;
8. **no authoritative V-C**.

## Modeling authorization

This patch does not itself begin serious SER modeling.

After SS accepts this patched authority, serious RS SER modeling may proceed
without reopening DS-002.

A candidate should not be rejected merely because one extreme forced tail can
reverse cheap-model ranking. Promotion decisions should prioritize V-B,
secondary V-A/V-D/Q evidence, plausible correlated-allocation robustness, then
the protected gate at the appropriate confirmation stage.
