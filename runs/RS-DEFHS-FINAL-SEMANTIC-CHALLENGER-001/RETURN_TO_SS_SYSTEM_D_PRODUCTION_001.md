# RS-DEFHS-FINAL-SEMANTIC-CHALLENGER-001 — FINAL SYSTEM D PRODUCTION RETURN TO SS

**Status: SYSTEM_D_PRODUCTION_COMPLETE_PENDING_SS_SUBMISSION_APPROVAL**

**Authority:** parent `771e6dea2ac14eca37274155c4e514d16f2e2118`, branch `rs/final-semantic-challenger-001-sol6-continuation`. This continues the same frozen experiment, **not** a new model sweep. Astra's original branch, source protocol, System C, validated folds, and retrieval map were not modified. **NO Kaggle submission.**

## 1. New TARGET209 Qwen3-14B inference provenance — PASS

User-supplied Kaggle kernel `khalwaniev/defhs-frozen-qwen3-14b-target209`; archive SHA256 `40c339efcf71286162b5aaeaf668f33449c44380bec67a9103c6ee7dbb50342c`. ZIP CRC and six OUTPUT_INVENTORY file hashes pass; exactly 209 unique test IDs in official ordering and exactly 201 unique ASR Hindi transcripts. Exact source `ASR_TRANSCRIPTS.csv` SHA256 `a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01`. Reconstructed sealed 209-record input bytes SHA256 `a86f640f99a114eb6623cac4d07afd27acfb692429da0ec5ee3fea8fb615d35d` matches CONTRACT and TARGET209_PREP_MANIFEST. All 201 unique-output transcript joins are consistent; no duplicates, missing IDs, unknown output classes, or output-to-ASR mismatches.

Original sealed model `Qwen/Qwen3-14B`, revision `40c069824f4251a91eefaf281ebe4c544efd3e18`, unchanged prompt SHA256 `d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f`, unchanged NF4 dual-T4 inference, target contract `a18d8da5971db41a872206de99780d472944b09879f973f3de574984dd3471fc`. Saved CHECKPOINT reports eight pinned shard SHA256 values and pinned tokenizer SHA consistent with prior repository registry (the 29 GB model shards themselves were not transferred to the CPU sandbox); FEASIBILITY 4/4 PASS; inference RESULT complete, no protected access, no submission.

Target semantic output `QWEN14B_TARGET209.csv` SHA256:
`bf5c6b3c6ee77cfad80d680cb4e6ce5db773f7c5b857b9aaa8011d3c128a1f8f`

## 2. Frozen PRIMARY_CV / original Astra evaluator reconciliation — PASS

The **original Astra CLI itself was not executed within this isolated sandbox**; the original frozen recipe and saved evidence were independently replayed and fully reconciled. Original accepted System C PRIMARY_CV = **0.8135577912484513**. New System D = **0.8396460575108101** (+0.0260882662623588). Every one of the **826** C and D frozen VB OOF hard decisions reproduces original authoritative records. Maximum absolute System D OOF probability difference vs original SOL6 scientific OOF CSV = **2.220446049250313e-16**. Original five-fold D F1 = [0.8314253993133304,0.8253724718317742,0.831245132457283,0.8477550158261768,0.8592858663260963]; all frozen semantic/primary/robustness gates remain PASS.

Historical 10 E2V/XLS-R outer `joblib` heads were downloaded from the canonical `rs_system3_wave1_001/cpu` Drive archive; their exact ten SHA256 hashes match `PRESERVED_HEAD_PARITY.json`. Each saved head reproduces its historical outer OOF probability block within 5e-7. The 50 original nested inner acoustic fits and five C/D meta fits were recomputed with frozen sklearn 1.8 recipe (`StandardScaler` on acoustic base features, `LogisticRegression(C=1,solver=lbfgs,max_iter=5000,random_state=20261001)` on 13/18 unscaled meta inputs). For TARGET209, each outer meta head uses its **corresponding original saved outer acoustic head**; five final probability vectors are averaged, then plain argmax, followed by existing certified retrieval map.

The C 209-row production replay matches **209/209 classes and exact CSV SHA256** `8ab7c5dc291cd9d1223283245fb62130b03bf728f764c5eeedf9d2915153e2a8`. This validates the deployment recipe, not just training metrics. A refit of the original base acoustic heads under sklearn 1.8 instead of using the historical saved heads would also recover C but change D ID **111 neutral**; therefore the authentic saved heads are required. Saved-head D correctly **preserves C's angry** decision for ID 111, and it is not in the final change list.

## 3. EXACT FINAL SYSTEM D CANDIDATE

File (tracked on this branch): `runs/RS-DEFHS-FINAL-SEMANTIC-CHALLENGER-001/submission_system_d.csv`.

**SHA256: `182bfbcd5fb10b351504da6d24f3d0d33f6d05cf2786e1e1a19e80afe0e57ec9`**. Exact official `Id,emotion` schema, 209 sorted unique IDs, no abstention predictions, no additional columns. All 78 certified retrieval rows unchanged, no TARGET209 labels used in model fitting. This is **one** frozen candidate, no sweep.

**Eight exact C -> D changes:**
| Id | Frozen cohort | C | D | Old Qwen8B semantic | New Qwen14B semantic | D margin |
|---:|---|---|---|---|---|---:|
| 24 | HARD | sad | happy | unclear | happy | 0.803287 |
| 125 | HIGH_CONFIDENCE | neutral | sad | sad | sad | 0.197817 |
| 153 | HARD | neutral | sad | neutral | sad | 0.199718 |
| 236 | HIGH_CONFIDENCE | sad | neutral | neutral | neutral | 0.005515 |
| 289 | HARD | happy | sad | unclear | sad | 0.123697 |
| 606 | HIGH_CONFIDENCE | sad | neutral | neutral | neutral | 0.000254 |
| 667 | HARD | neutral | happy | neutral | happy | 0.106802 |
| 819 | HARD | neutral | happy | neutral | happy | 0.654325 |

Cohort changes: **HARD 5/60**, **MEDIUM 0/13**, **HIGH_CONFIDENCE 3/136**, retrieval 0/78. The HIGH cohort is evidence triage, *not* a calibrated probability of correctness. Case 236 margin ~0.0055 and 606 ~0.00025 are close D decision boundaries and deserve SS inspection; do **not** tune them with public LB or hidden labels.

C class counts: angry 56, happy 47, neutral 55, sad 51.
D class counts: angry 56, happy 49, neutral 53, sad 51.
No class-collapse or mass reassignment; 201 unique transcripts in input. All 209 changes relative to C are exact prospective predictions, **not** measured corrections.

## 4. SS decision

**Recommendation: ONE eligible, canonically reconciled System D candidate is ready for SS review.** Frozen scientific gates passed, exact C replay passes, exact retrieval passes, and all required output contract checks pass. Strongest scientific case for D is ordinary PRIMARY_CV improvement +0.02609 with paired bootstrap positive lower bound, plus V-A, V-D/Q and private-allocation sensitivity. Strongest caution is private allocation still unknown, and two target D decisions (236/606) are near ties. Keep C ready as a hedge. No protected evaluation accessed, no public leaderboard tuning, no submission performed.

**Action required:** SS decides whether to approve submission of the one CSV. This RS report does not authorize a Kaggle submission. Production audit (complete 209 rows, probabilities/margins), replay source script, 10 saved authenticated heads and inference logs are bundled in the downloaded continuation evidence package. The original registered source files in GitHub and Drive remain unchanged.
