# Final Adversarial Return to SS

Mission: AR-DEFHS-FINAL-VALIDATION-DATA-REDTEAM-001

## 1. Exact reviewed Git authority

khalwaniev/defhs
ds/validation-hardening-002@c7da27a0f7d0927a5070da8cf825d1415546345c

The canonical DS branch was not modified.

## 2. Exact adversarial branch/head

Branch: audit/final-validation-data-redteam-001

Final head is read back externally after all review artifacts are committed so this file does not attempt to self-contain its own commit SHA.

## 3. CLAIM A verdict

MATERIAL_REVISION_REQUIRED.

The V-A/V-B/V-D backbone survives, but the private-LB emulator and robustness policy do not fully bound correlated hidden allocation or the newly identified preprocessing/source fingerprint.

## 4. Strongest attack against V-B

A previously uncatalogued sample-count modulo-128 fingerprint defines source-like strata with different V-B cheap-model rankings.

Dominant remainders: 0 / 43 / 86 / 30 / 94.

Examples:
- remainder 86, n=120: BASIC_EXTRATREES 0.6542 > FULL_RBF_SVM 0.6140;
- remainder 30, n=46: BASIC_LOGREG 0.5608 > FULL_RBF_SVM 0.5204.

Aggregate V-B still favors RBF and remains the primary authority, but candidate robustness must now be checked across this preprocessing/source stress.

## 5. Strongest attack against V-A

After excluding cross-split duplicate families, regularized nonlinear adversarial classification is stronger than the frozen wording suggests:
- full-acoustic ExtraTrees OOF AUC across three seeds: 0.6196-0.6441;
- 30 same-configuration label permutations: mean 0.5000, p95 0.5483, max 0.5576, none reach observed.

V-A remains secondary competition-mimic evidence, but not evidence of near-identical train/test distributions.

## 6. Strongest attack against the private-LB emulator

The frozen emulator omits correlated allocation.

At 20% pseudo-private with prompt-sim-0.90 beyond-duplicate rows enriched, 250 replicates give:
- BASIC_EXTRATREES top 49.2%;
- FULL_RBF_SVM top 32.4%;
- mean RBF minus best alternative -0.0064.

With joint latent k4 cluster 3 enriched:
- 20% private: FULL_LOGREG top 86.4%, RBF 4.0%, mean gap -0.0203;
- 30% private: FULL_LOGREG top 92.8%, RBF 6.8%, mean gap -0.0083.

These are adversarial sensitivity scenarios, not predictions of the real hidden assignment.

## 7. Does any plausible hidden DGP reverse model ranking?

Yes, under constructed but scientifically plausible correlated-allocation sensitivity scenarios.

This does not prove the actual hidden DGP follows them. It proves the current emulator has not bounded rank reversal under correlated hidden membership.

## 8. Duplicate/retrieval red-team result

SURVIVES.

Independent all-pair component checking:
- 227/227 components checked;
- zero components with any pair below 0.95;
- minimum within-component pairwise cosine 0.96026;
- minimum direct cross-split test-train pairwise cosine 0.96189.

No evidence justifies changing the 77 cross-split groups / 78 mapped test clips.

## 9. Speaker / prompt / latent red-team result

- Speaker: rejection of authoritative V-C survives. Strict stable ECAPA regions add too little independent coverage; broad regions become algorithm/threshold sensitive.
- Prompt: no prompt-grouped authority is justified, but beyond-duplicate prompt subsets are ranking-sensitive and must enter emulator stress.
- Latent: no acted/spontaneous-like authority is justified; unstable clusters are useful only as adversarial composition sensitivities.

## 10. Previously missed material data structure

Yes.

Sample-count modulo-128 / duration-quantization structure is a material observable preprocessing/source fingerprint.

Collapsed dominant residues plus OTHER:
- emotion association chi-square 45.0439;
- p=7.54e-05;
- Cramer's V=0.1348.

Within int16 only:
- p=2.57e-06;
- Cramer's V=0.1379.

Train/test association is weaker:
- p=0.1086;
- Cramer's V=0.0933.

Adding remainder category changes exact V-B RBF 0.63103 -> 0.63484, but does not improve V-A RBF SER. This supports diagnostic/source-stress use rather than automatic feature promotion.

## 11. Any current unknown incorrectly classified as unresolvable?

No exact unknown needs reclassification.

The 1,036 discrepancy, exact speaker IDs, exact prompt IDs, exact acted/spontaneous labels, broader annotation truth, public/private fraction and hidden assignment remain genuinely unresolved.

However, the statement that hidden public/private assignment risk was already sufficiently bounded is false under the current emulator.

## 12. CLAIM B verdict

MATERIAL_GAP_FOUND.

The final data certificate omitted a decision-relevant observable preprocessing/source structure: sample-count modulo-128 quantization.

Low-level RIFF metadata, file-overhead, corruption and ZIP-container hypotheses otherwise closed negative/nonmaterial.

## 13. Does the DS freeze remain scientifically acceptable?

Not unchanged as the final authority.

Its backbone remains defensible, but it should be reissued after a bounded corrective patch:
- preserve V-A/V-B/V-D;
- preserve V-C rejection;
- preserve retrieval;
- add preprocessing/source stress;
- expand emulator to correlated allocation.

No wholesale DS redesign is warranted.

## 14. May knowledge acquisition/modeling proceed?

Yes, with bounded conditions.

Knowledge acquisition and ordinary model development may proceed using V-B primary, V-A secondary, V-D plus the new source/preprocessing diagnostic while the corrective emulator patch is completed.

Do not use the protected promotion gate for exploratory selection. Final promotion should wait for corrected freeze/emulator authority.

## 15. Smallest corrective mission

DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001

Scope only:
1. formally characterize and freeze sample-count/preprocessing-source strata;
2. test cheap-model rank stability across them and decide diagnostic-only vs grouped stress;
3. extend the private-LB emulator at 20/30/40/50% to group-correlated allocations covering source/modulo, dtype, prompt beyond duplicates, retrieval concentration, duration/acoustic difficulty, and speaker/latent uncertainty sensitivity;
4. re-run only existing non-protected cheap OOF prediction sets;
5. reissue final validation/data authority if confirmed;
6. keep VALIDATION_VP_PROTECTED_FOLDS.csv entirely untouched;
7. do not launch expensive SER training in this corrective mission.
