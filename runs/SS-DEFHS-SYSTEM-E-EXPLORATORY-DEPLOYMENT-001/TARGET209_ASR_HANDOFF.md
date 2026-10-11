# SS exploratory System E production — target209 ASR handoff

**Authority:** `SS-DEFHS-SYSTEM-E-EXPLORATORY-DEPLOYMENT-001`. System D protected `69ebbe3ca3c65f82e546fdf1d42e90fa885c8634`; independent System E evidence authority `00211674d5cee5896570a9b2c599b238bd1ec52d`.

**Scientific verdict remains:** System E `0.8774091528` vs D `0.8396460575` PRIMARY_CV, but **NOT PROMOTED** because Q960 remainder 606 (n=41) lost `-0.03367393` macro-F1 against frozen `-0.02` floor. SS has authorized exactly one production candidate as a separately documented exploratory exception. Kaggle competition submission is **not authorized**.

## Phase A: sealed target ASR

- Builder: `scripts/build_system_e_asr_target209.py`
- Independent verifier: `scripts/verify_system_e_asr_target209.py`
- Generated folder (after local WSL execution): `kaggle/rs_system_e_asr_target209_001/`
- Kernel: `khalwaniev/rs-defhs-system-e-asr-target209-001`
- Original executed worker source: `scripts/final_breakthrough_asr_worker.py` at commit `00211674d5cee5896570a9b2c599b238bd1ec52d`, Git blob `ac3542c7a0120222112e10f1d4a2fc3b87f805bf`.
- Official original 1,035-row manifest SHA256: `1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469`.
- Only 209 *test* identities, filenames, byte sizes, audio-header metadata and WAV SHA256 are sealed. Train826 entries and all emotion labels excluded. WAVs are loaded from the official test subtree only, verified against all 209 SHA256 and RIFF headers before GPU inference.
- Same checkpoint `Qwen/Qwen3-ASR-1.7B` revision `b188e100bd85038c06d2812d24a39776eba774ca`; same `qwen-asr==0.0.6`, `Qwen3ASRModel`, Hindi, torch.float16, batch1, max_new_tokens512, original audio-decoding library, GPU T4.
- CPU prelaunch verifier includes test-only mount regression with artificial train+test trees; fail-closed when no test path.
- Outputs: `QWEN3_ASR_TARGET209.csv`, `QWEN3_ASR_TARGET209_PROGRESS.jsonl`, `ASR_TARGET209_RESULT.json`, `OUTPUT_INVENTORY.json`. Match 209 IDs and hashes before proceeding.
- Status: **builder/verifier committed; local WSL generation, GPU launch and inference await user execution**. No scientific target labels or System E 209 predictions claimed.

## Next authorized stages, not yet executed

1. Verify 209 new transcripts and original target WAV hashes and journal.
2. Reuse byte-identical original frozen Qwen3-14B checkpoint `40c069824f4251a91eefaf281ebe4c544efd3e18`, unchanged prompt SHA `d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f`, five-state constrained decoding, four-bit NF4, dual T4. Seal only target transcript input.
3. Using original authenticated saved waveform heads, reconstruct official System D 209-row submission **byte-for-byte**; require exact SHA of incumbent production CSV before System E fitting. Preserve 78 certified retrieval decisions.
4. Build one production E 23-feature, five-fold-nested L2 logistic fusion. Report 209-row schema, all probabilities, changed IDs, cohort counts, Q960_606 11 target IDs, output SHA, clean CPU reproduction and SS report. **No leaderboard submission**.

All 209 target labels remain unknown. Retain System D public 0.88227 as fallback.
