# Protected confirmation and submission preparation

Starting SHA: `67ae599a89e98ad4c185621bf030db9df9d9b7e8`.
Branch: `rs/system-implementation-001`.

SS authorization: the user instruction for this continuation accepts the locked
pre-protected finalist and authorizes one confirmation-only evaluation of
`VALIDATION_VP_PROTECTED_FOLDS.csv`, SHA256
`b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c`.
At this note's precommit, its bytes have been hashed but its fold assignments
have not been read for this execution.

Compare exactly:

- A: `FINAL_SYSTEM_LOCK.json` emotion2vec_base cached final-frame mean/std,
  StandardScaler + multinomial L2 LogisticRegression(C=1, max_iter=5000),
  ordinary argmax; inherited logistic random_state=20261001.
- B: historical FULL_RBF_SVM on the frozen full acoustic feature columns,
  SimpleImputer(strategy=median) + StandardScaler +
  SVC(C=10, kernel=rbf, gamma=scale), ordinary predict; no calibration.

For each of the existing five protected folds, fit on the other four folds.
The complete aggregate OOF macro-F1, without retrieval, determines the decision:

```text
IF protected aggregate macro-F1(A) > protected aggregate macro-F1(B):
    CONFIRM_FINALIST
ELSE:
    USE_FROZEN_REFERENCE
```

Fold and per-class results and confusion matrices are diagnostic only. No
threshold, ensemble, class exception, public-leaderboard tie breaker or retuning
is allowed. Evaluate no other candidate on protected validation. Stop before
evaluation on hash, frozen-artifact, historical-reference or submission-parity
failure; stop on an implementation defect requiring a scientific choice.

Prepare the selected frozen system on all 826 training rows for the 209 test
rows. Reuse A's hash-verified archived inference if A wins. If B wins, fit its
unchanged historical recipe. Apply only the existing certified retrieval hard
override to its frozen 78 test rows. Emit `Id,emotion` in sample-submission order.
Kaggle submission is not authorized.

## Execution result

Pending. This section will be completed after the one authorized comparison.
