# Unknown Register Red-Team

Mission: AR-DEFHS-FINAL-VALIDATION-DATA-REDTEAM-001

## 1,036 prose vs 1,035 supplied examples

Attack: inspect the canonical raw ZIP and ID/file inventory.

Evidence: exactly 1,035 WAVs are present; supplied IDs are exactly 1..1035; no hidden or missing supplied row is exposed by archive structure.

Verdict: UNRESOLVABLE classification remains correct. The reason for the organizer prose discrepancy is not recoverable from the supplied package.

## Exact organizer speaker IDs

Attack: ECAPA threshold, algorithm-choice and perturbation stability.

Evidence: the strict stable speaker-like region mostly reproduces duplicate identity; broader independent coverage is threshold/algorithm sensitive.

Verdict: remains UNRESOLVABLE. No inferred cluster should be renamed as organizer speaker identity.

## Exact organizer prompt/script IDs

Attack: ASR exact/fuzzy repeats and beyond-duplicate prompt groups.

Evidence: prompt-like structure is observable, but machine transcripts do not reveal organizer prompt identifiers.

Verdict: remains UNRESOLVABLE. Prompt proxies remain diagnostics and emulator stresses.

## Exact acted/spontaneous labels

Attack: joint ECAPA/prompt/eGeMAPS/source latent clusters.

Evidence: no stable uniquely identified two-regime partition emerges.

Verdict: remains UNRESOLVABLE. Do not name latent clusters acted or spontaneous.

## Broader annotation truth

Attack: duplicate conflict plus model/representation disagreement.

Evidence: only IDs 75/636/878 provide directly contradictory duplicate-family labels. Model disagreement is not annotation truth.

Verdict: remains UNRESOLVABLE beyond direct conflicts. No new relabeling authority.

## Public/private row fraction

Attack: inspect package metadata and reject the inference that 0.40/0.60 score weights reveal row fractions.

Evidence: no row-fraction metadata is supplied.

Verdict: remains UNRESOLVABLE.

## Hidden public/private assignment

Attack: group-correlated pseudo-allocation scenarios.

Evidence: actual assignment remains unknowable, but plausible correlated allocations can reverse cheap-model rankings.

Verdict: UNRESOLVABLE classification is correct; the claim that its decision impact was already sufficiently bounded is not correct. This requires an emulator patch, not reclassification.

## Missed observable: preprocessing source fingerprint

The red-team found sample-count modulo-128 structure absent from the final register:
- dominant residues 0/43/86/30/94;
- label association Cramer's V about 0.135;
- V-B model-rank differences across strata;
- weak train/test association, so it is not merely a test-split marker.

This is not an unresolvable unknown. It is a missed observable decision-relevant preprocessing/source fingerprint and should be added to the data authority with a dedicated diagnostic stress.
