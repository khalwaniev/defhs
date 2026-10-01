# Adversarial Review Report

Mission: AR-DEFHS-FINAL-VALIDATION-DATA-REDTEAM-001

Reviewed authority: ds/validation-hardening-002@c7da27a0f7d0927a5070da8cf825d1415546345c
Review branch: audit/final-validation-data-redteam-001
Protected promotion gate queried: NO.

## Executive verdict

- CLAIM A — VALIDATION: MATERIAL_REVISION_REQUIRED
- CLAIM B — DATA UNDERSTANDING: MATERIAL_GAP_FOUND

The red-team does not find grounds to discard the V-A/V-B/V-D backbone, create an authoritative speaker-disjoint V-C, weaken duplicate-safe selection, or alter the 78-test-clip retrieval lane.

Two bounded defects were found:

1. The private-LB emulator only sampled class-stratified approximately IID hidden allocations and did not bound group-correlated public/private allocation risk. Existing cheap-model rankings can reverse under plausible observable subgroup enrichment.
2. A previously unreported sample-count modulo-128 preprocessing/source fingerprint is materially associated with training labels and with V-B subgroup model ranking.

The smallest response is a targeted validation/emulator patch, not a restart of DS or a new SER campaign.

## Evidence boundary

Only non-protected evidence was used: exact frozen Git authority, V-A/V-B/V-D artifacts, non-protected OOF predictions, duplicate/retrieval evidence, ECAPA, ASR/prompt, eGeMAPS, latent outputs, the canonical raw ZIP, and derived acoustic features.

VALIDATION_VP_PROTECTED_FOLDS.csv was not read, scored, joined to predictions, or used for tuning.

## V-B attack: unmodeled preprocessing/source structure

Existing claim -> V-B is the primary duplicate-safe model/representation selection authority.

Failure mechanism -> a dependency outside the duplicate graph can define source/preprocessing strata with different model rankings while aggregate V-B averages them together.

Test -> inspect raw package structure, identify interpretable source fingerprints, and stratify exact V-B OOF predictions.

Evidence -> sample count modulo 128 is dominated by remainders 0, 43, 86, 30 and 94. After collapsing those five plus OTHER, label association is chi-square 45.0439, p=7.54e-05, Cramer's V=0.1348. Within int16 only, 0/43/86/OTHER remains associated with emotion (p=2.57e-06, V=0.1379). Train/test association is weaker and non-significant (p=0.1086, V=0.0933).

Exact V-B subgroup examples:
- remainder 0, n=414: FULL_RBF_SVM 0.6506;
- remainder 43, n=136: FULL_RBF_SVM 0.6392;
- remainder 86, n=120: BASIC_EXTRATREES 0.6542 > FULL_RBF_SVM 0.6140;
- remainder 30, n=46: BASIC_LOGREG 0.5608 > FULL_RBF_SVM 0.5204;
- remainder 94, n=56: FULL_RBF_SVM 0.4506;
- OTHER, n=54: FULL_RBF_SVM 0.5131.

Adding a one-hot remainder category to the full acoustic representation on the exact V-B folds moves FULL_RBF_SVM 0.63103 -> 0.63484 (+0.00381) and FULL_LOGREG 0.60047 -> 0.60389 (+0.00342). The same augmentation does not improve V-A RBF SER (0.69399 -> 0.69178).

Consequence -> keep V-B primary, but add a sample-count/preprocessing-source diagnostic stress. Do not promote the modulo feature automatically.

## V-A attack: nonlinear residual train/test shift

Existing claim -> V-A is a defensible secondary row-level competition-mimic view.

Failure mechanism -> train/test allocation may contain nonlinear acoustic/source structure missed by ID and linear diagnostics.

Test -> after excluding all cross-split duplicate-family members, run regularized nonlinear adversarial classifiers and a label-permutation null.

Evidence -> on 872 rows (131 test), full-acoustic ExtraTrees with min_samples_leaf=3, max_features=sqrt, balanced classes, and five-fold CV gives OOF AUC 0.63571, 0.64406, 0.61958 across three seeds. Thirty same-configuration label permutations have mean 0.50001, p95 0.54829, max 0.55762, and 0/30 reach the weakest observed AUC. Basic-feature RandomForest gives 0.56290-0.59164; HistGradientBoosting gives 0.51922-0.57209.

Consequence -> V-A remains secondary, but the frozen phrase weak-to-modest residual nonlinear shift is too soft. The evidence supports detectable, representation-dependent moderate nonlinear residual shift, without identifying a replacement hidden grouping.

## Private-LB emulator attack

Existing claim -> class-stratified 20/30/40/50% Monte Carlo adequately bounds hidden public/private uncertainty for cheap-model ranking.

Failure mechanism -> hidden public/private membership may be correlated by prompt, source, difficulty, retrieval concentration, speaker-like neighborhood, or latent regime.

Test -> force/enrich an observable subgroup into pseudo-private membership, random-fill to a fixed private fraction, and score 0.40*public + 0.60*private over existing non-protected V-A pipeline OOF predictions for 250 replicates.

Evidence:
- prompt-similarity-0.90 beyond-duplicate subgroup, 35 train rows, 20% private: BASIC_EXTRATREES top 49.2%, FULL_RBF_SVM 32.4%, BASIC_LOGREG 15.2%, FULL_LOGREG 3.2%; mean RBF minus best alternative = -0.0064.
- joint latent k=4 cluster 3, 231 train rows, 20% private: FULL_LOGREG top 86.4%, FULL_RBF_SVM 4.0%; mean gap -0.0203.
- same latent stress at 30% private: FULL_LOGREG top 92.8%, FULL_RBF_SVM 6.8%; mean gap -0.0083.

These are sensitivity scenarios, not claims about the actual hidden split.

Consequence -> the current emulator does not bound correlated hidden allocation risk. Extend it before treating it as final private-LB robustness authority.

## Duplicate / retrieval attack

Existing claim -> threshold 0.95 yields a robust 77-group / 78-test-clip retrieval lane.

Failure mechanism -> connected-component chaining could join endpoints that are not themselves convincing duplicates.

Test -> re-read canonical WAVs and compute normalized native-waveform cosine for every within-component pair and every cross-split test-train pair.

Evidence:
- 227 components checked;
- zero components contain a pair below 0.95;
- minimum within-component pairwise cosine 0.96026;
- 77 cross-split components checked;
- minimum direct cross-split test-train cosine 0.96189.

Consequence -> no evidence of transitive false joins. Retrieval survives unchanged.

## Raw container completeness

The canonical ZIP SHA-256 matches the manifest: 100b38e6ed69542df88c1d295932a7a4c1914cd931ee64f7c6c848f6053bf214.

All 1,035 WAVs have exactly fmt and data chunks, exact RIFF length, and 44 bytes of non-PCM container overhead. No LIST/JUNK/bext/software fingerprint exists. ZIP timestamps form packaging batches aligned mainly with split and broad ID windows and do not establish an independent label/source mechanism.

The material new property is sample-count modularity described above.

## Speaker attack

Agglomerative-vs-DBSCAN ARI is 0.9885 at d0.20, 0.9486 at d0.25, 0.6067 at d0.30 and 0.2731 at d0.35. The stable d0.20/d0.25 region adds only 6 and 33 beyond-duplicate clips; broader coverage loses algorithm/threshold identification. 75% embedding-dimension subsampling ARI also declines from about 0.992 at d0.20 to 0.856 at d0.35.

Consequence -> authoritative V-C remains rejected.

## Prompt and latent attacks

Prompt structure remains too small for a primary prompt-grouped validation, but it is ranking-sensitive. At prompt similarity 0.90, the beyond-duplicate OOF subset has 35 train rows and BASIC_EXTRATREES 0.5479 > FULL_RBF_SVM 0.4553. It therefore belongs in correlated-allocation emulator stress.

Joint latent clusters remain too weak and k-sensitive to be named acted/spontaneous or become authoritative grouping. They are still useful adversarial composition sensitivities.

## Label integrity

No second duplicate-family label conflict was established beyond IDs 75/636/878. Model or neighbor disagreement is not annotation truth. No relabeling/deletion is justified.

## Final scientific interpretation

The backbone survives but the freeze does not survive unchanged.

Required bounded correction:
- preserve V-B as primary;
- preserve V-A as secondary;
- preserve V-D;
- continue rejecting authoritative V-C;
- preserve retrieval unchanged;
- add sample-count/preprocessing-source stress;
- extend the emulator to correlated hidden-allocation scenarios;
- keep the protected seed untouched until normal promotion confirmation.
