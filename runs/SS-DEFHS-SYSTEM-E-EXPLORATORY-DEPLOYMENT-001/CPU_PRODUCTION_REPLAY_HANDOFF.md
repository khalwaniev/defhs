# System E exploratory production — exact saved-head CPU replay

Status: **CPU_PREPRODUCTION_VERIFIED; AWAITING_ACTUAL_TARGET209_QWEN14_OUTPUT**.

SS exception is unchanged. This is NOT scientific promotion. A Kaggle competition submission is not authorized.

## Independently executed parity
Source inputs were recovered from previously authenticated conversation attachments. The original `DEFHS_SYSTEM_D_FINAL_DELIVERY.zip` finalizer was executed in a clean temporary directory, preserving all ten historical E2V/XLS-R heads and original fold nested fitting. It reproduced System D's exact official CSV SHA256 **`182bfbcd5fb10b351504da6d24f3d0d33f6d05cf2786e1e1a19e80afe0e57ec9`**, its original C CSV checksum and protected OOF rows/probabilities.

A new, standalone CPU finalizer independently repeated the complete System E 826-row nested OOF matrix against accepted row-level evidence:
- System E macro-F1 **0.8774091527555827**
- System D OOF max absolute discrepancy **2.220446049250313e-16**
- System E OOF max absolute discrepancy **2.220446049250313e-16**
- No protected-validation or test-label access; no Kaggle submission.

The script is **`finalize_system_e_exploratory.py`**, SHA256 `3fc6328a81699c3769e06f14b5424b91c8fbf464ee9813a32013ec1005742633` (21,060 bytes), currently **outside GitHub**, supplied in user-downloadable archive below. GitHub code commit is pending user local adoption and an end-to-end candidate reproduction after authentic target semantic files arrive.

## Self-contained CPU package

Artifact: `DEFHS_SYSTEM_E_CPU_PRODUCTION_PACKAGE.zip`
SHA256: **`8204b3c4765530158d384768a5f5ea663b6c0d6c03c6ccab770301eed8491cc3`**
Size: 15,053,751 bytes. GitHub does not contain the ZIP; it is attached to ChatGPT and should be preserved in designated artifact storage.

Contained canonical archives:
- `DEFHS_SYSTEM_D_FINAL_DELIVERY.zip` SHA `fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839`
- `DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip` SHA `dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf`
- `DEFHS_QWENASR_QWEN14_SEMANTIC826.zip` SHA `cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789`
- standalone CPU script and full README.

Expected user WSL inference directories:
- `work/system_e_target209_asr_return/`, status PASS, ASR target CSV SHA `4c32a0431bff86e8e9c5153acd7225138f5790a63ff06fa001267a42ad583771`
- `work/system_e_target209_qwen14_return/`, notebook COMPLETE and TARGET_UNIQUE 200/200 as supplied by user. The output CSV checksum is **not yet independently inspected**.

Finalizer is fail-closed on original System D exact submission parity, full System E 826 probability parity, all test/audio/transcript hashes, original Qwen14 checkpoint and prompt, 209 target IDs, 78 certified retrieval predictions, and existing Q960/ HARD/MEDIUM/HIGH auditing. A final 209-row `Id,emotion` System E candidate, SHA256, changed row audit, and reproducibility manifest will only be claimed after actual target outputs are received and inspected.

## Next step

Download 7 semantic output files + 4 ASR output files to a conversation attachment (separate `asr/` and `semantic/` paths); run finalizer and compare an independent clean-directory repeat; commit auditable code, small report, and final candidate; return to SS **without submission**.
