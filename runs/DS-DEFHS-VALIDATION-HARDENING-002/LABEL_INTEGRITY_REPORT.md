# Label Integrity Report

## Verified conflict
Exactly one near-duplicate training family contains conflicting labels:
- IDs 75 / 636 / 878
- labels neutral / sad / neutral

This family is retained as an annotation-conflict diagnostic. No automatic relabeling is authorized.

## Model-disagreement diagnostics
A conservative four-model V-B OOF disagreement screen produced many consensus-misclassified examples. This is **not** evidence that those labels are wrong: model error, class overlap, speaker/source effects, and annotation noise are competing explanations.

Policy:
- do not relabel training rows from model disagreement;
- isolate the known duplicate conflict in diagnostics;
- later RS models may report robustness with and without the conflict family, but the official observed labels remain training authority.
