# RS-DEFHS-FINAL-BREAKTHROUGH-001 — System E final return to SS

**Disposition: STOP_STRESS_GATE_FAILED. Do not promote System E.** System D (PRIMARY_CV macro-F1 `0.8396460575108101`, user-supplied public LB `0.88227`) remains the protected incumbent. Do not produce System E target209 predictions or submit to Kaggle.

## Verified input and implementation

- New Qwen3-ASR 826 training recordings: verified source archive SHA256 `2e35d61564d68f1577e70111a4fa47a4be096dea729b75252c9bea101e7206f5`.
- New frozen Qwen3-14B semantic outputs: archive SHA256 `cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789`; QWEN14B_TRAIN826.csv SHA256 `8edd8dc9899f9304db2b46475758a67330f82c3c1348317646b561f3d57f6377`. Inference PASS; 826 correct IDs, 664 distinct transcripts, 788 non-unclear output labels; no test or fold labels in the inference contract.
- Original Qwen3-14B checkpoint revision `40c069824f4251a91eefaf281ebe4c544efd3e18`, unchanged prompt SHA256 `d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f`, unchanged NF4/FP16, dual T4, deterministic 5-state decoder.
- Verified old acoustic feature files and preserved authentic outer head probabilities. Replayed System C and **System D** exactly. System D's 826/826 preserved OOF labels reproduced and maximum predicted-probability discrepancy is 2.22e-16.
- One predeclared, five-outer-fold, strictly group-nested **23-feature** System E logistic L2 C=1 fusion; original 18 System D inputs plus five Qwen3-ASR→Qwen3-14B semantic state indicators. No post-result parameter tuning.

## Semantic complementarity before fusion

Original Qwen3-8B macro-F1 `0.5172141900`; old Whisper→Qwen3-14B macro-F1 `0.5713855666`; new Qwen3-ASR→Qwen3-14B macro-F1 **`0.6914351607`**. The new expert uniquely corrects 241 examples missed by Qwen3-8B, 67 missed by Qwen3-8B and System C, and **51 missed by Qwen3-8B and System D**. Semantic screen passed; this is oracle complementarity only.

## PRIMARY_CV

| | System D | System E | E−D |
|---|---:|---:|---:|
| Pooled macro-F1 | 0.8396460575 | **0.8774091528** | **+0.0377630952** |
| HARD316 macro-F1 | 0.6998856276 | 0.7781428026 | +0.0782571750 |

Fold deltas: `[+0.02475984,+0.06010675,+0.05392484,+0.02531539,+0.02459226]`; 5/5 positive. All class F1 deltas positive: angry +0.03914933; happy +0.03514872; neutral +0.03697780; sad +0.03977653. Of 58 changed OOF labels, **42 were corrections**, **11 breakages**, and 5 wrong-to-different-wrong. All five leave-one-fold-out deltas positive. Paired 656-connected-component, 2,000-draw multiplier bootstrap conservative max-t CI95 for gain: `[+0.01888038,+0.05664581]`. **All six frozen primary gates passed.**

## Required stress

- V-A SER delta +0.02172236; V-A **retrieval pipeline** delta **+0.01926508** (D 0.87229130→E 0.89155639); V-A non-retrieval +0.02741916. 232 V-A retrieval-covered samples; retrieval mapping rule not modified.
- V-D int16→int32 +0.05789286; int32→int16 +0.08858488.
- 616 frozen private-allocation scenarios ×250 draws each: minimum scenario mean private gain +0.01510341; minimum weighted 0.4-public/0.6-private mean gain +0.01739401; maximum ranking reversal rate 0.008. These are hypothetical allocations, not hidden test split observations.
- **DECISIVE REJECTION:** qualifying **Q960 remainder 606** stratum, n=41, four-class supports [6,10,13,12], has macro-F1 delta **−0.0336739284**. Predeclared V-Q gate is delta >=−0.02 for strata with >=5 examples in every class. It fails. Two stratum decisions changed: Id 857 neutral, D sad→E happy (wrong to other wrong); Id 908 angry, D angry→E sad (one breakage). Zero corrections. The stratum is small and noisy but passes the frozen support requirement. **Do not change the stratum rule post hoc**.
- Final frozen stress gates: 6/7 pass, adequately supported V-Q stratum gate FAIL. **System E is scientifically promising but NOT PROMOTED.**

## Artifact and final scientific authority

Full local scientific evidence archive (code, OOF rows, primary/semantic and stress JSON, 616 scenarios, exact frozen projection metadata, SS report):
`DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip`, SHA256
`dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf`.
Available as a conversation artifact for user download; **not claimed to be stored in GitHub**. Keep this report and small JSON authority in GitHub and upload the full archive to managed artifact storage if continued.

No Kaggle competition submission. No System D or 78 certified target retrieval decisions modified. No protected validation or test209 labels accessed. Do not rerun/tune this failed protocol under the same scientific mission. SS may independently review and commission a materially new research hypothesis.
