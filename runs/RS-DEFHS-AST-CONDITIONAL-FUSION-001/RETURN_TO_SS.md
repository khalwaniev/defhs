# RS-DEFHS-AST-CONDITIONAL-FUSION-001 — Return to SS

## Authority and governance

Start authority: `22c2995aefa959c6f1e0712b4e574083e45b1671` / tree `7c6d63d7ce56b716b3943f09e036d84c837169dd`.

Branch: `rs/ast-conditional-fusion-001`.

Protected validation: NO. Public-LB tuning: NO. Kaggle submission: NO. Certified retrieval modification: NO. GPU: NO.

The accepted C authority was replayed before Phase 1. Replay reproduced C macro-F1 **0.8135577912484513**, all five accepted fold scores, and the accepted confusion matrix exactly. A replay had zero hard-label mismatches against its canonical artifact.

## Phase 1

Among the **349** labeled rows where AST and C disagree:
- AST_WIN: **68**
- C_WIN: **239**
- BOTH_WRONG: **42**

The predeclared within-original-fold, four-way internally cross-fitted L2 logistic gate produced:
- pooled AST_WIN-vs-C_WIN ROC-AUC: **0.8115308885**
- bootstrap 95% AUC interval: **[0.7585497170, 0.8614970465]**
- pooled balanced accuracy at fixed 0.5: **0.6440745754**
- per-fold AUC: **[0.84135, 0.69275, 0.76596, 0.86835, 0.84615]**
- predicted AST-use: **55/349 = 15.76%**
- AST corrections captured: **25**
- C-correct cases broken: **19**
- pooled net corrections: **+6**

Per-fold net corrections were:
**[+7, -1, -2, +2, 0]**.

Only **2/5** original folds had strictly positive net corrections.

Neutral/sad did not trigger the separate catastrophe condition: 14 AST wins were captured, 12 C-correct rows were broken, net +2, with 7 neutral<->sad cross-breakages.

Captured AST wins were not one-class-only: angry 8, happy 3, neutral 7, sad 7.

## Why Phase 1 fails despite the strong AUC

The protocol predeclared that **all** pass conditions must hold. In particular, the fixed 0.5 low-capacity gate had to yield positive net corrections in at least **4/5** original folds.

It achieved only **2/5**.

The internally cross-fitted mechanism-only full-dataset macro-F1 is 0.8201936191 versus C 0.8135577912, a descriptive +0.0066358278. This is **not a valid new PRIMARY_CV fusion authority**, and the mission explicitly forbids allowing a pooled improvement to rescue unstable fold behavior.

Therefore the hypothesis is narrowed as follows:

- **supported:** AST_WIN versus C_WIN has reproducible rank/separability structure;
- **rejected:** the predeclared simple fixed-decision gate converts that structure into sufficiently stable corrections for expensive strictly nested fusion.

## Stop decision

`PHASE1_STATUS=FAIL`

`PHASE2_RUN=NO`

No AST refitting, no conditional TARGET209 routing, no target changes, and no GPU work are authorized.

**FINAL_VERDICT = `AST_CONDITIONAL_FUSION_CLOSED`**

Retain C unchanged and return to SS. Do not rescue the hypothesis with threshold tuning, feature sweeps, separate class-pair gates, AST weighting, or a gate zoo.
