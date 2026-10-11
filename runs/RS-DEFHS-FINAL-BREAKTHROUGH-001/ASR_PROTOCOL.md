# RS-DEFHS-FINAL-BREAKTHROUGH-001 — Frozen ASR hypothesis; SOL6 reconstruction

## Authority
Parent Astra commit `ab2147c7be342a71e67003e2314c7cf104cf6031`; protected System D `69ebbe3ca3c65f82e546fdf1d42e90fa885c8634`. Astra's ASR files were zero bytes; GPT-6 SOL reconstructed these executable assets **after** the interruption on 2026-10-11. This is NOT recovered original source and NO valid new-ASR scientific experiment has yet occurred. Rejected CLR18 remains closed.

## Single predeclared information experiment
Qwen3-ASR-1.7B transcripts of original **826 train WAVs**, explicit Hindi, followed separately by the exact previously frozen Qwen3-14B emotion-semantic model/prompt and exactly ONE nested System E evaluation. Preserve System D evidence/architecture, five frozen PRIMARY_CV blocks, group nesting and all 78 certified retrieval decisions. No public score selection or protected evaluation.

## Checkpoint and execution contract
`Qwen/Qwen3-ASR-1.7B` on Hugging Face, pinned model commit `b188e100bd85038c06d2812d24a39776eba774ca`. Use official `qwen-asr==0.0.6` Transformers backend `qwen_asr.Qwen3ASRModel.from_pretrained`; NOT the distinct `Qwen/Qwen3-ASR-1.7B-hf` `AutoProcessor` interface. FP16 single GPU 0 (NvidiaTeslaT4), batch 1, `max_new_tokens=512`, `transcribe(audio=original_local_WAV,language="Hindi")`. The library implements input normalization/preprocessing. The generated notebook includes the exact frozen subset manifest and does not embed labels, folds, or test audio.

Original `DATA_MANIFEST.csv` SHA256: `1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469`. Every train WAV checked for exact SHA256, length and RIFF header before inference. All 209 test rows excluded.

## Artifacts, integrity and limitations
Executable self-contained checked-in Kaggle notebook: `kaggle/rs_final_breakthrough_asr_train826_001/train826.ipynb`; backup checked-in `run.py` and CPU notebook builder `scripts/build_final_breakthrough_package.py`. Static notebook/schema/interface checks do not prove GPU runtime. Official checkpoint download, pip installation, Kaggle GPU quota and data mount remain runtime feasibility gates. Output `QWEN3_ASR_TRAIN826.csv` (826, five columns `Id,filename,file_sha256,language,transcript`), `ASR_TRAIN826_RESULT.json`, progress JSONL, and `OUTPUT_INVENTORY.json`. A failed run is `TECHNICAL_BLOCKER`, never negative scientific evidence. No leaderboard submission.

Once the verified 826 new transcripts arrive, assess actual differences against saved Whisper ASR transcripts (NOT word error rates without references), run pinned Qwen3-14B on new transcripts, and then apply frozen nested validation/promote-or-reject gates. No System E or TARGET209 output before an approved positive experiment.
