# RS-DEFHS-FINAL-SEMANTIC-CHALLENGER-001 — SOL6 continuation
**Scientific disposition: ELIGIBLE_FOR_SS_REVIEW.** Reused Astra's frozen protocol; no changes to original research branch, incumbent C, retrieval map, prompts, model configuration, split memberships or pass/fail criteria.

## Authority / reproducibility
- Parent: `10286ee67c555e775e5be8cc0eb529593039d53f`. Original protocol: `runs/RS-DEFHS-FINAL-SEMANTIC-CHALLENGER-001/PROTOCOL.md`; original evaluator: `scripts/final_semantic_challenger.py`.
- Kaggle 14B 826-row output SHA256 `02caef9f1ac4a4602a0b986b2f75314b6dfec68532645a5f530b247541b1cceb`; supplied ZIP SHA256 `5a81e3ade69e764ddcefa659e113af8449dcf9952d145204acc602e2d529bced`. All 7 ZIP outputs passed CRC/inventory checks. Original canonical Kaggle runner PAYLOAD sorted-key SHA256 exactly reproduces CONTRACT `4d9342f62f40a4cce46c5c48696f6190f9b42ad06d870343dfdcf2afee1f3fbe`.
- Model `Qwen/Qwen3-14B` revision `40c069824f4251a91eefaf281ebe4c544efd3e18`; prompt hash `d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f`; pinned eight weight-shard and tokenizer SHA values agree with CHECKPOINT; GPU FEASIBILITY 4/4 PASS.
- 826 exact train IDs, 711 unique transcripts, no missing or contradictory transcript joins against original checksum-verified ASR `a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01`. Inference output status COMPLETE; no test inference, protected validation or submission.
- Seven historical scientific inputs fetched from exact canonical Google Drive IDs, each verified against `INPUT_MANIFEST.json`. C nested 13-feature recipe reconstructed with identical historical outer waveform probabilities and frozen 50 inner fits; **826/826 C OOF class predictions matched** original authenticated `SYSTEM_C_AUTHORITY_OOF.csv`; published C score, 5 folds, hard cohort match. It is authenticated recipe replay, not original-byte archival claim.
- CPU experiment uses identical original `LogisticRegression(C=1,solver=lbfgs,max_iter=5000,random_state=20261001)`, one predeclared 18-feature nested fusion; Python packages numpy 2.3.5, pandas 2.2.3, scipy 1.17.0, sklearn 1.8.0; 656 dependency components, 2000 fixed-seed paired bootstrap draws. No encoder retraining or hyperparameter search. This is a faithful independent sandbox reimplementation rather than execution of the canonical evaluation CLI; original CLI can separately confirm.

## Semantic screen — 5/5 PASS
- Qwen8B: macro-F1 **0.5172141900**, 350/826 correct, non-abstaining 467/826; covered-only F1 0.7280251225.
- Qwen14B: macro-F1 **0.5713855666**, 417/826 correct, non-abstaining 589/826; covered-only F1 0.6915711724.
- Qwen14B vs Qwen8B: changed **231**, corrected **102**, broken **35**, wrong-to-other-wrong **94**. New correct class distribution angry 23 / happy 16 / neutral 16 / sad 47. **34 rows corrected by 14B that both old Qwen and C missed**, including neutral and sad.
- Qwen14B semantic fold F1 **[0.6319043950, 0.5361842852, 0.5413124991, 0.6313965918, 0.4984959982]**; class F1 angry 0.3794466403, happy 0.6279863481, neutral 0.6633906634, sad 0.6147186147.
- Frozen criteria: exceeds Qwen8B; >=10 novel; >=3 classes; >=5 novel beyond Qwen8B and C; >=1 novel neutral/sad. **ALL TRUE**.

## Nested waveform+semantic PRIMARY_CV — 6/6 PASS
- C: **0.8135577912484513**; challenger: **0.8396460575108101**; delta **+0.026088266262358828**; 826 rows, original five group-safe folds.
- C fold F1 **[0.7548722211, 0.8123673740, 0.8494805999, 0.8250607091, 0.8255294349]**.
- New fold F1 **[0.8314253993, 0.8253724718, 0.8312451325, 0.8477550158, 0.8592858663]**; per-fold gains **[+0.0765531782, +0.0130050978, -0.0182354674, +0.0226943067, +0.0337564314]**, 4/5 positive.
- New class F1 angry **0.8765133172**, happy **0.8519480519**, neutral **0.8046511628**, sad **0.8254716981**. All four outperform C.
- 60 OOF decisions changed vs C, **40 corrections / 18 breakages / 2 wrong-to-other-wrong**. Hard 316-row surrogate F1 **+0.0420463818**. Delete-fold deltas **[+0.0134070066,+0.0292886996,+0.0370099138,+0.0268071108,+0.0237756282]**, all positive. Paired component multiplier bootstrap 95% delta CI **[+0.0067571472,+0.0462201975]**.
- Frozen primary criteria: >=+.005 pooled; >=4/5 positive; no class drop >.02; hard cohort >=0; bootstrap lower >0; delete each fold positive. **ALL TRUE**.

## Candidate-specific V-A/V-D/V-Q/private-allocation stress — 7/7 PASS
- Newly nested V-A SER +0.0159747969; V-A unanimous-training-family retrieval pipeline **+0.01597884996** (232 retrieval-covered); V-A nonretrieval **+0.02227890168**.
- V-D int16->int32 **+0.00520835342**; V-D int32->int16 **+0.03984886986**.
- V-Q/diagnostic: 19 strata with >=5 members/class; worst (Q960_384) **-0.01517711423**, inside frozen -0.02 tolerance.
- Frozen private-allocation simulation: **616** scenario settings x **250** allocations each; both VB_SER and VA_PIPELINE, class-stratified private fractions 0.2-0.5 and frozen odds 0.5, 2/3, 1.5, 2 (baseline 1). Minimum per-scenario **mean** private delta **+0.01254255995**; minimum **mean** weighted (0.4 public+0.6 private) delta **+0.01425575407**; maximum weighted reversal rate **0.016** (1.6%, limit 20%). Individual draws can have negative outcomes; this is scoped sensitivity, NOT actual private leaderboard prediction.
- Seven frozen criteria: V-A pipeline >=0; VA nonretrieval >=0; both VD>=-.02; adequately supported VQ>=-.02; each plausible scenario mean weighted >=0; each mean private >=0; reversal frequency<=.20. **ALL TRUE**.

## SS decision and next decisive action
**`FINAL_GATE.json: ELIGIBLE_FOR_SS_REVIEW`**; System C public LB **0.86997** (reported by SS) and its immutable submission SHA256 `8ab7c5dc291cd9d1223283245fb62130b03bf728f764c5eeedf9d2915153e2a8` remain current incumbent. **No Kaggle submission authorized.** No claim about hidden/private score.

**Next:** SS may authorize the existing frozen TARGET209 Qwen3-14B inference procedure (same model/prompt/revision, same unmodified 209 ASR transcripts), followed by one all-train semantic+waveform fusion and 78 certified retrieval overrides. Inspect all changes relative to C, including existing 60 HARD target rows; verify 209 IDs, `Id,emotion` schema and SHA. Return candidate to SS; no submission without explicit approval.

Local sandbox evidence bundle includes full row-level OOF predictions and all 616 private-allocation scenario outputs; do not commit large binary checkpoints or acoustic matrices to GitHub.
