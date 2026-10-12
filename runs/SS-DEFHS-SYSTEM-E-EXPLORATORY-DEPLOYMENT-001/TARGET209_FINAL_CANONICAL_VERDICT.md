# SS-DEFHS-SYSTEM-E-EXPLORATORY-DEPLOYMENT-001 — FINAL CANONICAL RETURN

**Disposition: VERIFIED_EXPLORATORY_PRODUCTION_CANDIDATE — SCIENTIFICALLY_NOT_PROMOTED — PENDING_SS_DECISION.**

**No Kaggle competition submission was performed or authorized.** System D remains the incumbent (previously reported public macro-F1 **0.88227**). System E is a single authorized exploratory candidate, not an accepted scientific replacement.

## Exact authority and clean replay

- Repository `khalwaniev/defhs`, branch `rs/final-breakthrough-001-sol6-semantic`; scientific authority commit `00211674d5cee5896570a9b2c599b238bd1ec52d` must remain ancestor.
- Original official 1,035-row `DATA_MANIFEST.csv` SHA256 **`1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469`**, verified on the actual user-uploaded original, **not** a synthetic substitute.
- Original authenticated System D delivery ZIP SHA256 `fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839`.
- Accepted E scientific evidence ZIP SHA256 `dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf`.
- Qwen3-ASR→Qwen3-14B train826 ZIP SHA256 `cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789`.
- Completed target209 GPU output ZIP SHA256 `3178c75f2d8d8d7703535080649cfdc4dd25a1f9f380da3f7f65773d42a0`.
- Target Qwen3-ASR CSV SHA256 `4c32a0431bff86e8e9c5153acd7225138f5790a63ff06fa001267a42ad583771`; target new Qwen14 CSV SHA256 `41ea167a669fe87084f49d5c650ef4ec949af03b2cea9f7416563dc388ae6a2a`.
- Frozen Qwen14 model revision `40c069824f4251a91eefaf281ebe4c544efd3e18` and unchanged semantic prompt SHA256 `d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f`.

Using the **unchanged** source `finalize_system_e_exploratory.py` and all these authentic inputs, a clean CPU replay independently succeeded. The original System D finalizer re-created the exact authorized `Id,emotion` CSV bytes (SHA256 **`182bfbcd5fb10b351504da6d24f3d0d33f6d05cf2786e1e1a19e80afe0e57ec9`**). All 826 original System D and System E out-of-fold probabilities reproduced with respective max absolute deltas **`2.220446049250313e-16`**. No row parity was relaxed or overridden. The E 826-row PRIMARY_CV macro-F1 remained **`0.8774091527555827`**. This is +0.0377630952 vs D (0.8396460575108101).

The original 209-row source IDs, audio SHA evidence, 200 distinct target transcripts, original saved acoustic heads, five fold-specific fixed 23-feature meta fits, and all existing 78 certified retrieval decisions were preserved. No test labels, protected validation, competition submission, weight/threshold tuning, or post-hoc subgroup overrides were used.

## Exact deliverables

Authoritative output: **`production/submission_system_e_exploratory.csv`**, `Id,emotion`, 209 sorted unique IDs, four permitted classes, **SHA256 `e47676192cbd02393a49889214238f34cb8b49df2f9772b30cb19d766589df90`**.

The entire output set is byte-for-byte identical to the previously independently computed diagnostic preview after replacing its reconstructed test manifest with the actual official canonical manifest. The standalone Python finalizer source was not modified for this run. Companion evidence:

| File | SHA256 |
|---|---|
| `production/submission_system_e_exploratory.csv` | `e47676192cbd02393a49889214238f34cb8b49df2f9772b30cb19d766589df90` |
| `production/SYSTEM_E_209_ROW_AUDIT.csv` | `28716e70d0e9e7dfd77fe49a0c7474fa64fa253bc5431fb0bf116536ed9a6c47` |
| `production/SYSTEM_D_TO_E_CHANGES.csv` | `2352cb54f6d9dec2af9e32ab60619293f9bbc4eb9ee55f9b82f1f1d4ac0136a6` |
| `production/PRODUCTION_AUDIT.json` | `0d70efcc74b2608ef5a951e3fb487a72040137f033ba4cafdaee9c8ac833f368` |
| `production/PROVENANCE_SHA256.json` | `a760d570474e4f07610d99344d283ed5b6960ffe6986b27c5a28317e1a62ea28` |
| `scripts/finalize_system_e_exploratory.py` | `3fc6328a81699c3769e06f14b5424b91c8fbf464ee9813a32013ec1005742633` |

An independent post-run consistency check passed for all 209 unique ordered IDs, both D/E probability distributions, prediction-to-audit correspondence, 78 retrieval invariants, 11 delta rows and source SHA checks. Exactly **11** final predictions differ from System D:

| Id | Frozen cohort | Q960 606? | System D | System E | E top-2 margin |
|---:|---|---|---|---|---:|
| 102 | HARD | yes | angry | sad | 0.116185 |
| 111 | HARD | no | angry | neutral | 0.041490 |
| 132 | HARD | no | angry | sad | 0.241321 |
| 153 | HARD | no | sad | neutral | 0.328685 |
| 210 | HARD | yes | sad | happy | 0.523214 |
| 236 | HIGH_CONFIDENCE | no | neutral | sad | 0.740937 |
| 244 | HARD | no | neutral | sad | 0.052190 |
| 268 | HARD | no | sad | neutral | 0.013034 |
| 307 | HARD | no | sad | angry | 0.584817 |
| 883 | HARD | no | angry | happy | 0.741828 |
| 956 | HARD | no | angry | happy | 0.616394 |

Cohorts: HARD 10, MEDIUM 0, HIGH 1. Q960 remainder 606: 2 of 11 test recordings change (102, 210). All 78 certified retrieval predictions remain identical. Class-count D → E: angry 56→52, happy 49→52, neutral 53→54, sad 51→51. **These are unknown-outcome label changes, not demonstrated corrections.**

## Scientific restriction and SS decision

- **System E is NOT scientifically promoted.** Its frozen Q960 remainder-606 validation subgroup deteriorated by `−0.03367393`, outside the predeclared `−0.02` tolerance. No new target-test evidence erases that failure.
- The 0.877409 PRIMARY_CV and 209-candidate production do **not** imply a known leaderboard result. Do not claim that E exceeds D on public or private LB.
- **SS must decide** whether the authorized exploratory candidate warrants a single controlled submission, whether to retain System D, or whether to close E. RS does not submit or override the frozen promotion verdict.
- The source, five small final output files, and this verdict document should be committed to the authorized research branch; large raw inference and evidence ZIPs remain external with SHA references, per `WORKFLOW.md`.

**Release checklist:** official manifest PASS; original D CSV byte-PASS; D/E 826 OOF PASS; target209 ASR/Qwen14 PASS; 209 IDs PASS; D/E per-row audit PASS; 78 retrieval PASS; preview parity PASS; Q960 weakness explicitly disclosed; competition submitted NO.
