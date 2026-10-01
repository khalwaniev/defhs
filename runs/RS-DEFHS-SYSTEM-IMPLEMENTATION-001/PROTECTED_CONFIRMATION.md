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

Status: **READY_FOR_SUBMISSION**. Decision: **CONFIRM_FINALIST**.

Decision-rule precommit: `4bcd9468bb5759ba1ee2813a0ffdd128bd8ca13a`.
Executor commit: `aa16f60043152115de92dd446e593286eecf2fe0`.

Before protected access, all requested hashes passed and the original competition
ZIP supplied the sample submission. FULL_RBF_SVM reproduced every ordinary
V-A/V-B hard prediction (zero mismatches), all five fold scores and aggregate
scores: V-A `0.6939938030859938`, V-B `0.6310269549043466`.

The protected comparison was executed once, on CPU, with only A and B. Ordinary
SER predictions determine its aggregate result; retrieval is applied only to the
final test submission. Archived OOF preserves A probabilities, both hard labels,
and B's uncalibrated OVR decision scores. No calibration was added to B.

| Protected result | A: locked finalist | B: historical reference |
|---|---:|---:|
| Aggregate macro-F1 | 0.7376693938891288 | 0.6109463795639095 |
| Fold 0 macro-F1 | 0.6984307052372849 | 0.6292271427543514 |
| Fold 1 macro-F1 | 0.7080006747862448 | 0.5850888999793314 |
| Fold 2 macro-F1 | 0.7488996722806072 | 0.6453234203394664 |
| Fold 3 macro-F1 | 0.8175677429160629 | 0.5991601092832283 |
| Fold 4 macro-F1 | 0.7135771790362753 | 0.5893320859065688 |
| angry F1 | 0.7920792079207921 | 0.6537530266343826 |
| happy F1 | 0.7329842931937173 | 0.5445544554455446 |
| neutral F1 | 0.6906474820143885 | 0.6232558139534884 |
| sad F1 | 0.734966592427617 | 0.6222222222222222 |

Confusion matrices: rows=true, columns=predicted, in angry/happy/neutral/sad order.

A:

```text
160 15 19 11
13 140 16 23
14 21 144 38
12 14 21 165
```

B:

```text
135 48 12 10
34 110 29 19
14 31 134 38
25 23 38 126
```

Selected system: **emotion2vec_base_L2_LOGREG**, unchanged mean/std, scaler,
L2 logistic C=1 and argmax. Reused the hash-verified archived all-826 fitted
model's 209 test inference rows; no additional test inference fit was needed.

Submission: `submission.csv`, SHA256
`523e6327e5ad0791ace145fc8f224bd6686a6d7977fa5501c4757380e54215c8`.

- Schema: exactly `Id,emotion`, 209 rows, no index/blank/duplicate/missing IDs.
- Original sample-submission ID set and exact row order: **PASS**.
- Class counts: angry 60, happy 45, neutral 55, sad 49; no rebalancing.
- Frozen certified retrieval override applied to exactly 78 rows.
  It changes 0 labels because raw A already agrees on those rows.
- Saved OOF metrics were independently checked from confusion counts and the
  submission was read back for schema, order, labels, retrieval and SHA parity.
- RETUNING AFTER PROTECTED: **NO**.
- PUBLIC LB USED FOR SELECTION: **NO**.
- KAGGLE SUBMISSION MADE: **NO**.

No killed candidate was evaluated on protected validation, no new encoder
extraction or GPU execution ran, no large preservation archive was created, and
no main merge occurred. Existing `.tmp/` work remains preserved.

Exact local submission path:
`/home/fikar/zingle/defhs/runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001/submission.csv`.

NEXT: **READY_FOR_SUBMISSION**. Uploading to Kaggle awaits a separate instruction.
