# RS-DEFHS-TARGET209-SPECTROGRAM-EVIDENCE-001 — Final Return to SS

## Governance

This is the final continuation of the existing mission. No protected validation, Public-LB tuning, Kaggle competition submission, retrieval-map mutation, new encoder training, pseudo-labeling, or three-modality fusion occurred.

## Historical AST authority and recovery

The canonical AST expert remains B1 seed-mean from `MIT/ast-finetuned-audioset-10-10-0.4593` at revision `f826b80d28226b62986cc218e5cec390b1096902`.

The previously missing parent was recovered exactly on Kaggle:
- `model.safetensors` SHA256: `ae0c1e2ad4e1381d851fa9bf298ba13ebc9c5a914cdee2dbe427a6583869924d`
- historical parity: **30/30 model-row comparisons exact**
- hard-label mismatches: **0**
- max absolute difference: **0.0**
- mean absolute difference: **0.0**

TARGET209 inference then completed for all **209** rows. The AST evidence SHA256 is `f74b8c7b2990f0b927cdf6e9683a5d2ecb0518b97245de9df26da19aa9c54dfe`.

## Preserved labeled evidence

Adapted AST remains weak standalone (PRIMARY_CV macro-F1 **0.6030611992**) relative to A (**0.7768156647**) and C (**0.8135577912**), but it contains structured conditional information: it correctly covered 68 C errors in labeled OOF, including 50 HARD rows. This does not make AST a safe replacement.

## Stage 5 — TARGET209 descriptive evidence

Because TARGET209 labels are unknown, every result below is a **disagreement/concordance statement**, never a claimed correction.

Across 209 rows:
- AST vs A disagreement: **68**
- AST vs C disagreement: **73**
- A vs C disagreement: **17**

By frozen uncertainty stratum, AST vs C disagrees on:
- HARD: **33/60 = 55.0%**
- MEDIUM_CONFIDENCE: **6/13 = 46.2%**
- HIGH_CONFIDENCE: **34/136 = 25.0%**

Thus disagreement is enriched in the pre-existing uncertain region (39/73 HARD+MEDIUM rows vs 34/136 HIGH; descriptive odds ratio **3.44**), which supports real conditional information. However, **34 HIGH-confidence disagreements are too many for an unfitted hard gate**.

### The existing 17 C-vs-A changes

On the exact 17 nested-semantic target changes:
- AST agrees with **A on 10**
- AST agrees with **C on 5**
- AST predicts a **third class on 2**

AST corroborates C on IDs: **265, 625, 651, 657, 860**.
AST sides with A on IDs: **136, 153, 268, 343, 360, 819, 884, 897, 898, 927**.
AST gives a third class on IDs: **210, 570**.

Therefore AST does **not** broadly validate the semantic C changes. The five C-aligned rows are hypotheses for later SS-authorized fusion research, not target-label evidence.

### Qwen concordance

Qwen is non-abstaining on **125** target rows:
- C = Qwen: **88**
- A = Qwen: **71**
- AST = Qwen: **49**
- C = AST = Qwen: **48**
- C = Qwen while AST differs: **40**
- AST = Qwen while C differs: **1**
- all three different: **10**

This shows AST is genuinely less coupled to the semantic modality, but independence alone is not evidence of higher correctness.

### Certified retrieval rows

The immutable certified-retrieval set contains **78** rows. A and C disagree on **0** of them. AST disagrees with their shared label on **19/78** rows. No retrieval evidence was modified.

That conflict rate prevents using AST to override certified retrieval without a separately validated rule.

### Neutral/sad mechanism

C predicts neutral/sad on **106** target rows; AST disagrees on **36**. Of these:
- neutral↔sad cross-disagreements: **19**
- C neutral → AST sad: **16**
- C sad → AST neutral: **3**

AST's overall target distribution is angry 59, happy 38, neutral 43, sad 69, compared with C's angry 56, happy 47, neutral 55, sad 51. The strong target shift toward sad is directionally consistent with the known labeled AST neutral→sad weakness. This is a specific reason **not** to use AST as a direct neutral/sad adjudicator.

## Final scientific conclusion

AST has **real but weak conditional information** beyond the waveform+semantic system. The target disagreements are preferentially concentrated in existing uncertainty strata, consistent with the labeled correction evidence. But AST remains substantially discordant in HIGH-confidence cases, conflicts with 19 certified-retrieval rows, supports only 5 of the 17 C-vs-A target changes, and shows a pronounced sad-class shift.

**FINAL_VERDICT: `AST_WEAK_BUT_USEFUL_CONDITIONAL_SIGNAL`**

Return to SS. Do not automatically train a three-modality fusion, construct a hard AST gate, modify retrieval evidence, or submit to Kaggle. The cheapest next step, if SS authorizes further work, is a strictly labeled, nested cross-fitted conditional-fusion test that asks whether AST adds value only inside predeclared uncertainty strata while leaving HIGH-confidence and certified-retrieval rows protected.
