# RS-DEFHS-TARGET209-FORENSIC-ENDGAME-001 — Bounded SS Review Addendum

## Authority and constraints

Start authority: `d913cd27c56cfe26b5f0d4c6d0c437a7b333b730` on `rs/target209-forensic-endgame-001`.

The semantic rule remains frozen at **alpha = 0.10**. This addendum did not redo source recovery or Phase C, did not tune alpha or inspect larger semantic weights, did not query protected validation, did not submit to Kaggle, and did not modify the certified 78-row retrieval map.

## Task 1 — transition-specific OOF audit

The frozen alpha=0.10 rule changes exactly 29 PRIMARY_CV OOF decisions. The complete row-level audit is in `OOF_TRANSITION_AUDIT.csv`; all exact-transition aggregates are in `OOF_TRANSITION_SUMMARY.csv`.

### angry -> neutral

- N: **3**
- WRONG_TO_CORRECT: **2**
- CORRECT_TO_WRONG: **1**
- WRONG_TO_OTHER_WRONG: **0**
- NET_CORRECTIONS: **+1**

Rows: Id 280 (wrong->correct), Id 413 (correct->wrong), Id 988 (wrong->correct).

There is no empirical reversal against the semantic rule for this transition.

### sad -> neutral

- N: **7**
- WRONG_TO_CORRECT: **3**
- CORRECT_TO_WRONG: **2**
- WRONG_TO_OTHER_WRONG: **2**
- NET_CORRECTIONS: **+1**

Rows: Id 14, 33, 66, 143, 439, 722, 908.

There is no empirical reversal against the semantic rule for this transition.

No minimum sample-size threshold is imposed; these counts are reported descriptively as requested.

## Task 2 — mechanism concordance

Detailed row evidence is in `MECHANISM_CONCORDANCE.csv`.

### TARGET209 Id 265 analogue: WAVEFORM_MODEL_DISAGREEMENT, angry <-> neutral

For all 3 OOF `angry -> neutral` changes:
- E2V and XLS-R disagree: **3/3**
- E2V/XLS-R labels span exactly angry vs neutral: **3/3**
- fixed-pair top two classes are angry and neutral: **3/3**
- fixed-pair margin < 0.20: **3/3**

This is strong descriptive concordance with Id 265. No fitted gate is created.

### TARGET209 Id 884 analogue: NEUTRAL_SAD_ACOUSTIC_BOUNDARY, neutral <-> sad

For all 7 OOF `sad -> neutral` changes:
- E2V and XLS-R disagree: **7/7**
- E2V/XLS-R labels span exactly neutral vs sad: **6/7**
- fixed-pair top two classes are neutral and sad: **7/7**
- fixed-pair margin < 0.20: **7/7**

The one non-exact E2V/XLS-R span is Id 908 (angry vs sad), but its fixed-pair top-two boundary is still sad vs neutral with margin 0.07081. Overall this is strong descriptive concordance with Id 884. No fitted gate is created.

## Task 3 — V-A diagnostic only

The existing historical `FIXED_PAIR_VA.npz` was replayed mechanically with the same frozen alpha=0.10 rule and the existing Qwen semantic labels. No retraining and no alpha retuning occurred.

- V-A fixed-pair Macro-F1: **0.8266398472**
- V-A alpha=0.10 Macro-F1: **0.8390360541**
- Delta: **+0.0123962069**
- Changed decisions: **15**
- Fold deltas: **[+0.0233526, +0.0253328, +0.0000000, +0.0063979, +0.0059632]**

This result is **DIAGNOSTIC_ONLY** and is not model-selection authority.

## Task 4 — candidate submission artifact

Candidate created:
`runs/RS-DEFHS-TARGET209-FORENSIC-ENDGAME-001/submission_semantic_alpha010.csv`

It was constructed mechanically from:
`runs/SS-DEFHS-TARGET209-EMPIRICAL-RESET-001/submission_fixed_pair_cv5.csv`

Only these rows differ:
- Id 265: `angry -> neutral`
- Id 884: `sad -> neutral`

Verification:
- rows: **209**
- schema identical: **YES**
- ID set/order identical: **YES**
- rows different from fixed pair: **2**
- certified retrieval rows changed: **0/78**
- Kaggle submission made: **NO**

SHA256:
- source: `1dd6b8db750ec6eee0b0f48d4148eceefcdd4bb5eaeb8454fa278597ae44818e`
- candidate: `c4600396b719821eb33711585b7782346e679fe06fc6f77413e66e5bccb71114`

Byte sizes:
- source: **2094**
- candidate: **2100**

Exact byte edits and unified diff are recorded in `CANDIDATE_BYTE_DIFF.txt`.

## Recommendation

Neither target transition shows a transition-specific empirical reversal; both have **NET_CORRECTIONS = +1**, both show strong mechanism concordance with their corresponding TARGET209 hard case, and the independent V-A replay is directionally consistent.

**FINAL_RECOMMENDATION: `PROMOTE_SEMANTIC_ALPHA010_FOR_PUBLIC_PROBE`**

This is a recommendation to SS only. No submission has been made.
