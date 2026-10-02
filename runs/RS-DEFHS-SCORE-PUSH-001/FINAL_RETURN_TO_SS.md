**STATUS: COMPLETED — AUTHORIZED MECHANISMS EXHAUSTED; CONTROL RETAINED.**

Starting Git SHA: `a37915427ec01cae5540cbec716a1ffc64d4aff6`. Branch: `rs/score-push-001`. Measurement commits are recorded in EXPERIMENT_REGISTRY.csv; the final pushed closure SHA is supplied with this return.

FINAL BEST SYSTEM: unchanged iic/emotion2vec_base@v2.0.4, frozen final-frame mean+std, StandardScaler, multinomial L2 LogisticRegression C=1/max_iter=5000, ordinary argmax. Certified unanimous-label hard retrieval override remains 78/209 test clips.

| System | V-B primary | V-A SER | V-A non-retrieval | V-B CLEAN |
|---|---:|---:|---:|---:|
| Control | 0.73837458 | 0.80165195 | 0.73111669 | 0.74250301 |
| Plus base: utterance mean + logistic | 0.54036535 | 0.58003575 | 0.53322962 | 0.54136479 |
| Plus large: utterance mean + logistic | 0.52066002 | 0.55589284 | 0.52000137 | 0.54217426 |
| Plus base utterance + cached XLS-R, equal | 0.72276314 | 0.78219576 | 0.71489920 | 0.70927337 |
| Control + fixed Qwen abstention | 0.75239046 | 0.77967784 | 0.74578477 | 0.77842983 |

V-A retrieval-aware: control 0.80527685; fixed Qwen fusion 0.81370347 (delta 0.00842662). This is a secondary diagnostic with the unchanged certified override.

**EMOTION2VEC+ BASE AND LARGE**

Both pinned public ModelScope models ran once over 1,035 hash-verified 16 kHz mono clips, one per T4. Official metadata lists Apache License 2.0; the separate Hugging Face cards have a custom model-license tag, so execution used the verified ModelScope source. Immutable revisions and SHA256 values for every executed model file are in MISSION_CONFIG.json. The official FunASR revision is 4a84879ae8ca4d2430953b11c49d609217d93988. The official canonical utterance representation is the mean of the returned final-frame features; meanstd was the sole cheap alternative from the same forward pass. Native scores were restricted to the four exact matching labels and renormalized without biases.

All six authorized realizations:

| Model | Realization | V-B | V-A | V-A non-retrieval |
|---|---|---:|---:|---:|
| emotion2vec_plus_base | native | 0.48137224 | 0.48137224 | 0.46928708 |
| emotion2vec_plus_base | utterance | 0.54036535 | 0.58003575 | 0.53322962 |
| emotion2vec_plus_base | meanstd | 0.50601645 | 0.57594406 | 0.48315539 |
| emotion2vec_plus_large | native | 0.48476777 | 0.48476777 | 0.46687637 |
| emotion2vec_plus_large | utterance | 0.52066002 | 0.55589284 | 0.52000137 |
| emotion2vec_plus_large | meanstd | 0.51571786 | 0.61537204 | 0.52753215 |

Best realization is selected by primary V-B, with V-A non-retrieval used only for a tie. Both best realizations use canonical utterance mean + fixed scaler/L2 logistic C1.

emotion2vec_plus_base_utterance:

- Five V-B folds (0–4): 0.44442028, 0.62180025, 0.58167034, 0.49774602, 0.55450806.
- V-B per-class F1 (angry, happy, neutral, sad): 0.57644110, 0.47154472, 0.50539957, 0.60807601.
- Disagreement with control: V-B 0.48668281; V-A 0.45157385.

emotion2vec_plus_large_utterance:

- Five V-B folds (0–4): 0.49019572, 0.54757236, 0.56024603, 0.48616812, 0.50114003.
- V-B per-class F1 (angry, happy, neutral, sad): 0.57985258, 0.46875000, 0.47982063, 0.55421687.
- Disagreement with control: V-B 0.51573850; V-A 0.47336562.

Scientific robustness: both fail the prior conservative gate; their simultaneous primary difference intervals are wholly negative. Competition deployment: both fail through large negative effects on every V-B fold, every class and existing format/regime strata. The extraction/API/checkpoint/input alignment audit found no implementation defect. No new/control blend was entered because neither new standalone was strong.

**CACHED XLS-R COMPLEMENTARITY**

The strongest new standalone was plus-base utterance. The only extra pair tested was that parent plus the existing cached XLS-R L2-logistic probabilities. Equal averaging scores V-B 0.72276314, V-A 0.78219576 and non-retrieval 0.71489920. Marginal gain over the weak new parent was +0.18239779 V-B with all five fold directions positive. This triggered the existing bounded quarter-grid, leave-one-fold-out, paired one-SD selector; it retained equal weights on every fold in both views, yielding identical metrics. There was no new XLS-R extraction, unrestricted stacker or three-member ensemble.

The pair loses 0.01561144 V-B versus the accepted control, improves only three folds, loses 0.01945619 V-A, 0.01621749 non-retrieval and 0.03322964 CLEAN. Against XLS-R alone its V-B gain is only 0.01196692, positive in three folds and negative in two. Both scientific and competition judgments reject deployment. AUDIO_DIAGNOSTICS.json records both member ablations, hard-error relationships, probability/logit correlation and disagreements.

**BEST AUDIO SYSTEM**

Control is retained and locked before semantic inference. Its delta versus the previously submitted control is zero on V-B, V-A and V-A non-retrieval. The audio-parent lock and ordinary OOF hashes are committed at a4b2b7509703c58f1fef3d0317cd3962235594cb.

**QWEN SEMANTIC**

Exactly Qwen/Qwen3-8B@b968826d9c46dd6066d109eabc6255188de91218 (Apache-2.0, public/ungated) ran in NF4 4-bit double quantization with FP16 computation. One fixed precommitted prompt, non-thinking mode and greedy five-label token grammar were used. Its input was raw cached transcript text only; Id, labels, folds, audio predictions and retrieval state never entered the chat. Each of 856 exact unique texts was inferred once and reused across 1,035 rows. No ASR, fine-tuning, prompt search, examples or threshold adjustment occurred. Test semantic outputs are cached but were not used to choose the system or prepare a submission.

Standalone on the 826 development rows: abstention 43.4625% (359 rows); coverage 467/826. Conditional accuracy 0.74946467 and macro-F1 0.72802512 on covered rows. Accuracy counting abstention as an error is 0.42372881. Covered-only metrics do not imply performance on all rows.

Fixed fusion: a valid semantic label replaces audio; unclear retains audio. No learned gate.

- V-B 0.75239046; delta 0.01401588.
- Five V-B folds (0–4): 0.69576577, 0.80500529, 0.80519844, 0.74563298, 0.70862475.
- V-B fold deltas: 0.00900686, 0.09130725, -0.01313760, 0.04799344, -0.06460312.
- V-B per-class F1 (angry, happy, neutral, sad): 0.77866667, 0.76136364, 0.70347648, 0.76605505.
- V-B corrections/breakages: 90/81; actual changed labels 191; both-wrong changes 20.
- V-A 0.77967784; delta -0.02197411; corrections/breakages 71/90.
- Five V-A folds: 0.81128514, 0.79413096, 0.72655577, 0.82551300, 0.73517399.
- V-A non-retrieval 0.74578477; delta +0.01466807; corrections/breakages 68/62.

| Ordinary diagnostic | V-B fusion | V-B delta | V-A fusion | V-A delta |
|---|---:|---:|---:|---:|
| CLEAN | 0.77842983 | 0.03592682 | 0.77986250 | 0.02095938 |
| prompt_singleton | 0.76128464 | 0.01223646 | 0.77457619 | -0.00053443 |
| no_close_training_neighbor | 0.75006734 | 0.01646178 | 0.75580218 | 0.00100238 |
| repeated_prompt | 0.73049189 | 0.03059819 | 0.78245286 | -0.05878809 |
| excluding_Astra48 | 0.75010733 | 0.01371423 | 0.78135522 | -0.02322817 |
| int16 | 0.74832811 | -0.00045478 | 0.77721586 | -0.03922338 |
| int32 | 0.76564092 | 0.12461241 | 0.78576431 | 0.11686859 |

The exact Astra48 IDs are recovered from its preserved blinded diagnostic and reproduced from the cached authority, listed in MISSION_CONFIG.json. They did not inform the frozen prompt/rule. Excluding them leaves V-B +0.01371423 and V-A -0.02322817. This prevents treating the earlier inspected rows as fresh confirmation.

**TWO JUDGMENTS**

Scientific robustness: FAIL. The fixed fusion simultaneous 95% V-B difference interval is [-0.03007638, +0.05810815]; only three of five folds improve, and one delete-fold aggregate difference is negative. These are dependency-component multiplier diagnostics conditional on reused ordinary OOF, not a new protected confirmation.

Competition deployment evidence: REJECT THE FIXED RULE. Positive CLEAN, non-retrieval, retrieval-aware and Astra-excluded evidence is real and preserved. However the +0.0140 primary gain is modest and inconsistent: fold 4 loses 0.0646, ordinary V-A loses 0.0220, and angry loses class F1 from 0.80382775 to 0.77866667 with 7 corrections against 29 breakages. On the main int16 source (746/826 rows), V-B is nearly unchanged (-0.00045478) and V-A loses 0.03922338. The 80-row int32 source accounts for the main net accuracy benefit; joint_k4_2 also shows a large V-A regression (-0.12788871). Thus a materially large, fold-consistent, concordant deployment gain is absent. Rejection does not rest on the interval crossing zero or an absolute +0.03 cutoff. The simple rule does not justify further gating under this mission; no prompt rescue or extra architecture ran.

**FINAL BEST SYSTEM / DELTA**

Existing control retained. Final deployed-system deltas versus the current submitted control: V-B 0.00000000; V-A 0.00000000; V-A non-retrieval 0.00000000. The Qwen challenger has +0.01401588 / -0.02197411 / +0.01466807 respectively and is not promoted.

submission.csv prepared: NO new submission, because neither authorized mechanism produced a clearly stronger internally supported system. The existing accepted submission is unchanged. No new all-training fit was needed after failed promotion.

Protected validation queried/accessed: NO. Public LB used for selection: NO. KAGGLE SUBMISSION MADE: NO. No prompt or fusion-rule retuning after semantic results. No PEFT, new model family or retrieval redesign.

Artifact preservation: [existing DEFHS mission area / rs_score_push_001](https://drive.google.com/drive/folders/1mDmg0W_EFFqjdmafja8ApBFDpR6byZZw). Both cached NPZ files and both Qwen outputs are preserved and byte-verified. ARTIFACT_MANIFEST.json records all sizes, SHA256 values and Drive IDs. The rclone shared-project write quota was bypassed using the connected [Google Drive plugin](https://drive.google.com/drive/folders/1mDmg0W_EFFqjdmafja8ApBFDpR6byZZw); audio checks used rclone download comparison, semantic checks used connected raw-byte download comparison.

Exact scientific artifacts: AUDIO_RESULTS.json, AUDIO_DIAGNOSTICS.json, AUDIO_PARENT_LOCK.json, SEMANTIC_RESULTS.json, aligned ordinary OOF CSVs, FINAL_DECISION.json and EXPERIMENT_REGISTRY.csv. The full fixed prompt and both inference packages are committed. No completed extraction or successful inference was repeated.

Unresolved scientific/data/technical blockers: NONE.

NEXT SS DECISION: accept mission closure with control retained. Any new semantic gating architecture requires a new explicit SS authorization. No stronger submission candidate is presented for approval.
