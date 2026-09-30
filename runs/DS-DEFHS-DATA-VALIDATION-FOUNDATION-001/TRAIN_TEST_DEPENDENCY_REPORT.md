# Train/Test Dependency Report

## Finding

The supplied train and test sets are not independent at the recording-source level.

A full-waveform cosine audit and an independent fixed-length relative-time
fingerprint audit identify a sharply separated near-duplicate cluster.

- threshold used: `0.95`
- weakest member of the fingerprint duplicate cluster: `0.974119`
- strongest non-cluster pair: `0.209360`
- duplicate/near-duplicate groups: **227**
- clips belonging to those groups: **467**
- train↔test groups: **77**
- affected test clips: **78 / 209**
- conflicting-label groups in train: **1**

Every train↔test duplicate group with training labels has a unanimous training
label. Therefore duplicate retrieval is a legitimate high-confidence inference
lane using only competition-provided data, but it must remain separate from
general SER validation/modeling.

The only detected conflicting train group is recorded in
`DUPLICATE_CONFLICTS.csv`.

## Consequence

Row-level random CV substantially overstates generalization. Model selection
must inspect duplicate-safe V-B in addition to competition-mimic V-A.
