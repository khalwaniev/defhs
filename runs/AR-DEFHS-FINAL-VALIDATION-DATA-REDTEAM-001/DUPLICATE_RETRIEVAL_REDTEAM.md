# Duplicate / Retrieval Red-Team

Mission: AR-DEFHS-FINAL-VALIDATION-DATA-REDTEAM-001

## Existing authority under attack

- threshold 0.95;
- 227 duplicate components;
- 77 train-test components;
- 78 mapped test clips;
- unanimous usable training labels for mapped components.

## Connected-component chaining attack

The canonical raw ZIP was re-read. Every frozen duplicate component was reconstructed from DUPLICATE_GROUPS_FINAL.csv. Each waveform was mean-centered, L2-normalized and compared to every other member of the same component at native sample length.

Results:
- components checked: 227;
- components with any within-component pair cosine <0.95: 0;
- minimum within-component pairwise cosine: 0.9602607;
- train-test components checked: 77;
- minimum direct test-to-train pairwise cosine: 0.9618880.

No component is being held together solely by a weak transitive bridge under this independent check.

## Container false-join attack

All 1,035 raw WAVs contain only canonical fmt and data RIFF chunks with exact RIFF length and 44-byte overhead. No encoder/INFO/LIST/bext metadata was found that could explain waveform duplicate matches as metadata artifacts.

## Missed transformed copies

The frozen audit already used native-waveform comparison plus an independent relative-time fingerprint and found a wide duplicate/non-duplicate gap. ECAPA and ASR expose semantic/speaker neighbors outside the graph, but those do not establish transformed waveform copies.

The red-team did not establish a new crop/pad/resample/speed/pitch duplicate family with defensible evidence.

## Verdict

SURVIVES_ADVERSARIAL_REVIEW.

The 78-test-clip retrieval lane remains justified and separate from ordinary SER model selection. No mapped row was identified as fragile to component transitivity.
