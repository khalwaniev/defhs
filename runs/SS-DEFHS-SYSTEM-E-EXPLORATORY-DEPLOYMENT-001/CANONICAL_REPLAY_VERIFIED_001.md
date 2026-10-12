# System E — canonical 209-row exploratory candidate independently verified

**Mission:** SS-DEFHS-SYSTEM-E-EXPLORATORY-DEPLOYMENT-001  
**Status:** AUTHENTIC_CANONICAL_MANIFEST_FULL_REPLAY_PASS; exploratory candidate, NOT scientific promotion; SS review required.  
**No Kaggle competition submission.** Previous public System D 0.88227 remains fallback; no leaderboard result exists for E.

## Actual successful execution

User-uploaded **original** `DATA_MANIFEST.csv` SHA256 `1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469` independently verified in the sandbox. Original System D CPU finalizer, frozen E evidence, 826 train QwenASR/Qwen14 semantics, and authentic 209 target QwenASR/Qwen14 results were replayed **unchanged**.

- System D exact official 209-row CSV **SHA256 `182bfbcd5fb10b351504da6d24f3d0d33f6d05cf2786e1e1a19e80afe0e57ec9`**, replay PASS.
- System D 826-row OOF probability maximum absolute discrepancy `2.220446049250313e-16`, PASS.
- System E 826-row OOF probability maximum absolute discrepancy `2.220446049250313e-16`, PASS.
- System E PRIMARY_CV macro-F1 `0.8774091527555827`, versus D `0.8396460575108101`, +0.0377630952.
- ASR 209-row output SHA256 `4c32a0431bff86e8e9c5153acd7225138f5790a63ff06fa001267a42ad583771`; new Qwen3-14B 209-row output SHA256 `41ea167a669fe87084f49d5c650ef4ec949af03b2cea9f7416563dc388ae6a2a`; 200 unique semantic transcripts; frozen original model/prompt checks PASS.
- Exactly 209 sorted unique predictions; 78/78 certified retrieval decisions unchanged.
- Original diagnostic preview and canonical output are **byte-for-byte identical**, including all five output/audit files. No test labels, protected validation, altered meta fitting, post-hoc overrides, or Kaggle submission.

**Final System E candidate SHA256: `e47676192cbd02393a49889214238f34cb8b49df2f9772b30cb19d766589df90`.**

Final D→E changes (not known corrections): `[102,111,132,153,210,236,244,268,307,883,956]`: HARD 10, HIGH_CONFIDENCE 1, MEDIUM 0. Among 11 Q960 remainder-606 test clips, 102 and 210 change. Class counts D→E: angry 56→52, happy 49→52, neutral 53→54, sad 51→51.

**Scientific warning:** predeclared Q960 remainder-606 stress delta `−0.03367393` breached frozen `−0.02` criterion; **System E scientific promotion failed and remains failed** despite exact candidate production. A leaderboard submission needs SS's new explicit decision.

## Full source and audit artifacts

A fully verified external handoff ZIP `DEFHS_SYSTEM_E_FINAL_CANONICAL_HANDOFF.zip` SHA256 **`c7f16f3f91be5b90349641a61d85222e69d71b5f88dcb1bb3030acfad8718a59`** contains the unchanged finalizer source, exact candidate CSV, complete 209-row D/E probabilities, 11-row transition audit, JSON SHA provenance, command log, final SS report, and a SHA-guarded GitHub publishing script. **This ZIP is delivered in the ChatGPT conversation, not stored in GitHub.** All 7 small source/result/report files must still be published from the downloaded ZIP by the user WSL script; do not treat this report alone as their presence in GitHub.

- System D evidence ZIP SHA256 `fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839`.
- System E evidence ZIP SHA256 `dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf`.
- 826 new semantic ZIP SHA256 `cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789`.
- Target209 GPU-output ZIP SHA256 `3178c75f2d8d8d7703535080649cfdc4dd25a1f9f380da3f7f65773d42a0`.

**SS disposition required:** keep D incumbent; evaluate E strictly as exploratory candidate with recorded robustness failure; submission not authorized by RS.
