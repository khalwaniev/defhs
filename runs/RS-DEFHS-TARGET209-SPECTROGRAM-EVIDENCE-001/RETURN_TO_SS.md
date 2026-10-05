# RS-DEFHS-TARGET209-SPECTROGRAM-EVIDENCE-001 — Return to SS

## Governance

Start authority: `a29e1e3ea1aee657edc314719d82821c25cc29e9`.

No protected validation, Public-LB tuning, Kaggle submission, retrieval-map mutation, new encoder training, pseudo-labeling, or three-modality fusion occurred.

## Stage 0 — historical AST authority

The historical AST family is `RS-DEFHS-SYSTEM3-WAVE1-001`, upstream `MIT/ast-finetuned-audioset-10-10-0.4593` at revision `f826b80d28226b62986cc218e5cec390b1096902`.

Exact preprocessing and model recipe were recovered. The canonical adapted expert is **B1 seed-mean**: arithmetic mean of two independently trained adapted AST seeds (20260930 and 20260917), each with five frozen V-B outer models. Class order is `angry, happy, neutral, sad`.

All ten adapted outer refit STATE checkpoints are present in Drive with hashes recorded in `AST_AUTHORITY.json`.

Executable closure nevertheless fails because the adapted STATE files store only the learned four-class head plus changed encoder top-block state and require the exact upstream parent. Historical provenance fixes that parent binary as `model.safetensors` SHA256 `ae0c1e2ad4e1381d851fa9bf298ba13ebc9c5a914cdee2dbe427a6583869924d`. It is not preserved in DEFHS Drive, and the public official binary could not be materialized in this execution runtime. No substitute was used.

## Stage 1 — labeled parity

Saved probability replay exactly reproduces historical authority.

Adapted AST seed-mean:
- Macro-F1: **0.6030611992**
- folds: **[0.5127272727, 0.6203119232, 0.6243377847, 0.5967115828, 0.6443710068]**
- per class: angry **0.6960784314**, happy **0.5426356589**, neutral **0.5506493506**, sad **0.6228813559**

Frozen AST B0:
- Macro-F1: **0.5468363348**

Versus A:
- AST correct / A wrong: **60**
- AST wrong / A correct: **202**

Versus C:
- AST correct / C wrong: **68**
- AST wrong / C correct: **239**

Thus AST is not a safe standalone replacement, but it contains nontrivial marginal information.

## Stage 2 — mechanism evidence

On the exact 316-row HARD surrogate:
- A: **0.5822591878**
- C: **0.6578392458**
- adapted AST: **0.4820009965**
- AST correct / A wrong: **41**
- AST wrong / A correct: **72**
- AST correct / C wrong: **50**
- AST wrong / C correct: **107**

The 68 C-error recoveries are broad rather than one-fold noise:
- by true class: angry 14, happy 17, neutral 18, sad 19
- by fold: 16, 15, 10, 14, 13
- HARD: 50; non-HARD: 18

Largest C-error mechanisms recovered by AST include:
- sad -> neutral: 13
- neutral -> sad: 10
- happy -> neutral: 9
- happy -> angry: 6
- neutral -> happy: 6
- angry -> happy: 5
- angry -> neutral: 5

Exact grouped evidence is in `AST_UNIQUE_CORRECTIONS_AGG.csv`; full prediction-transition correction/breakage counts are in `AST_TRANSITIONS_VS_A_C.csv`.

## Stage 3 — neutral/sad audit

A had 56 neutral<->sad cross-errors. C leaves **32** unresolved.

On those 32:
- AST correct: **14**
- AST wrong: **18**
- AST predictions: angry 1, happy 2, neutral 8, sad 21

However, of the 24 original neutral/sad cross-errors that C already corrected:
- AST correct: 9
- AST wrong: 15
- AST would make a neutral/sad cross-reversal on 14

Therefore AST has genuine neutral/sad conditional information, but no descriptive evidence supports naive replacement or an unfitted hard gate.

## Stage 4/5 — TARGET209

Not executed. Exact TARGET209 audio exists, and all ten adapted outer delta checkpoints exist, but the exact upstream parent binary required to instantiate those deltas is unavailable to this execution environment.

No `TARGET209_AST_EVIDENCE.csv` was fabricated. No TARGET209 disagreements or three-way counts are reported.

## Scientific conclusion

The labeled evidence supports **weak-but-real conditional spectrogram information** beyond C, especially in HARD and residual neutral/sad errors. It is also highly destructive when used indiscriminately.

Because exact historical TARGET209 AST inference could not be instantiated, the mission cannot establish whether AST disagreements on the 209 are concentrated in HARD/MEDIUM rather than HIGH_CONFIDENCE cases. Therefore AST is **not promoted** into three-modality fusion here.

**FINAL_VERDICT: `AST_INFERENCE_BLOCKED_MISSING_AUTHORITY`**

Return to SS; do not automatically begin fusion, pseudo-labeling, retraining, or submission.
