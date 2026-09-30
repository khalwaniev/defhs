# Private-LB Emulator Attack

Mission: AR-DEFHS-FINAL-VALIDATION-DATA-REDTEAM-001

Protected promotion gate queried: NO.

## Existing emulator

The frozen emulator uses retrieval-aware V-A pseudo-test predictions and public-fraction scenarios at 20/30/40/50%. Its Monte Carlo allocation is class-stratified.

## Failure mechanism

Class-stratified sampling does not cover hidden public/private membership correlated by prompt/script family, preprocessing/source, difficulty, retrieval concentration, speaker-like neighborhood, or uncertain latent regime.

The red-team does not claim any constructed scenario is the true hidden assignment. The question is whether the emulator has bounded ranking risk across plausible correlated assignments.

## Discriminating test

Using existing non-protected V-A pipeline OOF predictions:

1. fix a pseudo-private fraction q;
2. identify an observable subgroup;
3. force/enrich that subgroup into pseudo-private membership;
4. random-fill remaining private slots from the complement;
5. compute public and private macro-F1;
6. combine as 0.40*public + 0.60*private;
7. repeat 250 times.

## Controls

Several attacks did not overturn the frozen winner:

- int32 enrichment: FULL_RBF_SVM top 94.4% at 20% private and >=98% at larger tested fractions;
- speaker-like d0.30 beyond-duplicate enrichment: FULL_RBF_SVM top 100% at 20/30/40/50%;
- simple shortest/longest-duration and high-ID allocations retained RBF as the top mean system.

The attack therefore does not force reversals by construction.

## Prompt-correlated allocation

Prompt-similarity-0.90 beyond-duplicate subgroup: 35 train rows.

At 20% pseudo-private:
- BASIC_EXTRATREES top 49.2%;
- FULL_RBF_SVM top 32.4%;
- BASIC_LOGREG top 15.2%;
- FULL_LOGREG top 3.2%;
- mean RBF minus best alternative = -0.0064.

At 30% private, RBF recovers to top in 68.8%, so the reversal is conditional rather than universal.

## Latent correlated allocation

Joint latent k=4, cluster 3: 231 train rows.

At 20% pseudo-private:
- FULL_LOGREG top 86.4%;
- BASIC_LOGREG top 9.6%;
- FULL_RBF_SVM top 4.0%;
- mean RBF minus best alternative = -0.0203.

At 30% pseudo-private:
- FULL_LOGREG top 92.8%;
- FULL_RBF_SVM top 6.8%;
- mean RBF minus best alternative = -0.0083.

The latent cluster is not an organizer label and is too unstable to become authoritative validation. It is used only as an adversarial correlated-allocation sensitivity.

## Verdict

MATERIAL REVISION REQUIRED.

The emulator remains useful, but it cannot be considered a sufficiently complete hidden-allocation sensitivity analysis until correlated allocation is included.

## Required patch

Without touching the protected gate, extend the emulator to include:
- sample-count/preprocessing-source strata;
- dtype/source;
- prompt beyond-duplicate strata;
- duration/acoustic strata;
- retrieval-heavy and retrieval-light compositions;
- speaker-like and latent clusters only as threshold-sensitive sensitivity scenarios;
- difficulty-correlated allocations defined from non-protected development evidence.

For every scenario report subgroup definition, private fraction, rank-reversal frequency, score-gap distribution, and whether the subgroup is sufficiently identified to affect validation grouping versus emulator stress only.
