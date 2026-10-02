**STATUS: RECOVERY COMPLETE — SOURCE-GATED CANDIDATE READY FOR SS REVIEW.**

Recovery starting authority: `d0c7e7630b1e39e4854a5f6b1e7d123e8602e212`. Branch: `rs/score-push-001`. Final pushed SHA is supplied with this return. The previous closure was not accepted by SS; this authorized continuation supersedes it. Original measurements remain in AUDIO_RESULTS.json and SEMANTIC_RESULTS.json and in Git history.

**SOURCE-GATED QWEN**

Exactly one prescribed rule: dtype=int32 and valid cached Qwen emotion -> Qwen label; unclear or int16 -> accepted control audio. Certified retrieval is applied last, unchanged. No prompt change, threshold search, additional source rule, encoder extraction or Qwen inference occurred.

| View | Control | Source gate | Delta |
|---|---:|---:|---:|
| V-B primary | 0.73837458 | 0.75336142 | +0.01498685 |
| V-A SER | 0.80165195 | 0.81539465 | +0.01374270 |
| V-A non-retrieval | 0.73111669 | 0.75148118 | +0.02036448 |

Five V-B folds (0–4): 0.70081051, 0.72597072, 0.83072322, 0.72820546, 0.78025075.
V-B fold deltas: 0.01405160, 0.01227268, 0.01238718, 0.03056593, 0.00702288.
Five V-A folds (0–4): 0.81693786, 0.79462207, 0.82845192, 0.86694028, 0.76936284.
V-A fold deltas: 0.01778182, 0.00613662, 0.01814716, 0.01870236, 0.00784332.
All five folds improve in both views.

| Per-class F1 | Angry | Happy | Neutral | Sad |
|---|---:|---:|---:|---:|
| VB | 0.80097087 | 0.74866310 | 0.71495327 | 0.74885845 |
| VA | 0.83292978 | 0.81794195 | 0.78378378 | 0.82692308 |

Corrections/breakages: V-B 19/7 (29 actual label changes; 3 remain wrong), V-A 17/6 (26 changes; 3 remain wrong). V-A non-retrieval: 16/5. There are 80 int32 development rows, of which 56 have a valid semantic label. The largest global class-F1 loss is angry: -0.00285688 V-B and -0.00439079 V-A; there is no serious class collapse.

| Existing diagnostic | V-B gate | V-B delta | V-A gate | V-A delta |
|---|---:|---:|---:|---:|
| CLEAN | 0.76373764 | 0.02123463 | 0.78460759 | 0.02570447 |
| prompt_singleton | 0.76620466 | 0.01715648 | 0.79597535 | 0.02086472 |
| no_close_training_neighbor | 0.74943068 | 0.01582512 | 0.77286320 | 0.01806340 |
| repeated_prompt | 0.71579606 | 0.01590236 | 0.84557331 | 0.00433236 |
| excluding_Astra48 | 0.75237514 | 0.01598204 | 0.81797753 | 0.01339413 |
| int16 | 0.74878289 | 0.00000000 | 0.81643924 | 0.00000000 |
| int32 | 0.76564092 | 0.12461241 | 0.78576431 | 0.11686859 |
| joint_k4_0 | 0.75560036 | 0.03480920 | 0.79701210 | 0.05181238 |
| joint_k4_1 | 0.66865693 | 0.00655618 | 0.78723407 | 0.00634234 |
| joint_k4_2 | 0.59260320 | 0.05645865 | 0.72518259 | -0.02054391 |
| joint_k4_3 | 0.72354138 | 0.01306717 | 0.76930662 | 0.00657116 |

The prior int32 results reproduce exactly: V-B +0.12461240975030308 and V-A +0.11686858957327129. Every int16 prediction stays identical to the control. V-A joint_k4_2 regresses by 0.02054391; this existing diagnostic is retained for review and does not become another source rule.
V-A retrieval-aware score with the frozen override: 0.81898965 (control 0.80527685).

Scientific robustness: this is a rule authorized after seeing source diagnostics, not independent confirmation. The inherited conditional operator passes, with a conditional simultaneous primary interval approximately [0.00078758, 0.02918611], but that interval does not account for choosing the source rule from the previous results. Protected validation remains closed.

Competition deployment evidence: preserve the candidate. V-B, all five V-B folds, V-A, all five V-A folds, non-retrieval and CLEAN are concordantly positive; no serious class collapse appears. The signal is restricted to the documented int32 source and depends on only 80 development rows. No public-LB result was used.

**9-SCORE MAPPING AND BOUNDED REGULARIZATION**

All nine cached classes were retained: angry, disgusted, fearful, happy, neutral, other, sad, surprised, <unk>. Fixed mapping uses StandardScaler + multinomial L2 logistic C=1/max_iter=5000. Each regularization check uses C=0.01, 0.1, 1, 10 and four existing training-side inner folds per outer fold. C is selected by aggregate inner OOF macro-F1, with smallest-C exact ties, then refitted on the four outer training folds. No outer held-out label participates in C selection.

| Cached recovery | V-B | V-A | V-A non-retrieval |
|---|---:|---:|---:|
| emotion2vec_plus_base_score9_C1 | 0.50675981 | 0.50169486 | 0.49794323 |
| emotion2vec_plus_base_score9_NESTED_C | 0.50548269 | 0.50669721 | 0.50121176 |
| emotion2vec_plus_base_utterance_NESTED_C | 0.52876822 | 0.57868111 | 0.52052328 |
| emotion2vec_plus_large_score9_C1 | 0.52776628 | 0.53319357 | 0.51638250 |
| emotion2vec_plus_large_score9_NESTED_C | 0.52647183 | 0.53437950 | 0.51801637 |
| emotion2vec_plus_large_utterance_NESTED_C | 0.56174450 | 0.56882874 | 0.53949945 |

Per-fold C choices, in fold order 0–4:

- emotion2vec_plus_base_score9_NESTED_C: V-B [1.0, 10.0, 10.0, 10.0, 0.1]; V-A [0.01, 0.01, 0.1, 10.0, 0.01].
- emotion2vec_plus_base_utterance_NESTED_C: V-B [1.0, 0.01, 0.01, 0.1, 0.01]; V-A [1.0, 1.0, 10.0, 1.0, 10.0].
- emotion2vec_plus_large_score9_NESTED_C: V-B [0.1, 1.0, 1.0, 0.01, 10.0]; V-A [1.0, 10.0, 10.0, 1.0, 1.0].
- emotion2vec_plus_large_utterance_NESTED_C: V-B [0.01, 0.01, 0.01, 0.01, 0.01]; V-A [0.01, 1.0, 0.01, 0.01, 0.01].

BEST CACHED RECOVERY: emotion2vec_plus_large_utterance_NESTED_C. V-B 0.56174450; V-A 0.56882874; non-retrieval 0.53949945. It remains far below the accepted control. All six recovery lanes fail both scientific and competition judgments versus control. The optional equal blend was not entered; no additional ensemble search occurred.

A numerical implementation repair retained cached utterance float32 and the earlier two-thread BLAS setting. The initial cast/thread setting altered one C1 boundary prediction; the affected CPU utterance calculations were corrected with the same Cs/folds. Forty already-valid nine-score outer jobs were reused. All eleven C1-selected fold probabilities now reproduce their corresponding fixed/previous authority within 1e-12. This repair repeated no encoder or Qwen inference. Full diagnosis and audits are in RECOVERY_RESULTS.json.

**FINAL CANDIDATE SYSTEM**

Accepted emotion2vec_base final-frame mean+std -> StandardScaler -> multinomial L2 logistic C=1 -> argmax; dtype=int32 valid cached Qwen label overrides audio, unclear falls back; int16 retains audio; unchanged certified unanimous-label retrieval overrides last. The currently submitted control remains unchanged until SS approves deployment.

Delta versus current submitted system: V-B +0.014986846908580653; V-A +0.013742699470434272; V-A non-retrieval +0.020364483984003368.

submission.csv prepared: YES.
Canonical local path: `/home/fikar/zingle/defhs/runs/RS-DEFHS-SCORE-PUSH-001/submission.csv`.
SHA256: `ac64f17239bdac463f0f3687190580885aa97306040ce9b91204b713fffedc5d`.
209 rows; exact Id,emotion schema; exact official sample IDs and row order; no duplicate/missing IDs or values; only angry/happy/neutral/sad. All checks PASS.

Test int32 rows: 22. Valid semantic gate rows: 17. Semantic label changes before retrieval: 8. Final labels changed versus current submission: 7. Changed IDs: 68, 102, 111, 210, 235, 268, 941. Every int16 test prediction and all 78 certified retrieval predictions match the existing submission.
Final class counts: {'neutral': 57, 'angry': 56, 'sad': 53, 'happy': 43}. No rebalancing occurred.

KAGGLE SUBMISSION MADE: NO. Protected validation accessed: NO. Public LB used for selection: NO. Prompt or source-rule retuning: NO. New GPU compute: NONE. Heavy caches remain in their previously byte-verified Drive locations; no new heavy archive was necessary.

All metrics and confusion matrices were independently recomputed from saved OOF. The nested-selection audit confirms exclusion of outer folds. Exact decisions, source code, config, OOF, checks and artifact hashes are committed on the same branch. No technical blocker remains.

NEXT SS DECISION: approve or reject this prepared source-gated competition candidate. Competition submission requires explicit separate authorization.
