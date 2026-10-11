# Verified, self-contained Kaggle train826 notebook — SOL6 post-Astra recovery

**This directory had zero-byte files in Astra's interrupted commit.** This new continuation branch contains nonempty `train826.ipynb`, `run.py` (identical executed Python source), and Kaggle `kernel-metadata.json`. The full 826 train-only identity/hash manifest is embedded; no private GitHub access or local CSV upload is needed at Kaggle runtime.

Checkpoint `Qwen/Qwen3-ASR-1.7B`, revision `b188e100bd85038c06d2812d24a39776eba774ca`, `qwen-asr==0.0.6` package, `Qwen3ASRModel.from_pretrained` and `transcribe(...,language="Hindi")`. Do not substitute the `-hf` architecture/interface.

To launch from this worktree:

```bash
kaggle quota
kaggle kernels push -p kaggle/rs_final_breakthrough_asr_train826_001 --accelerator NvidiaTeslaT4 --timeout 14400
kaggle kernels status khalwaniev/rs-defhs-final-breakthrough-asr-train826-001
kaggle kernels logs khalwaniev/rs-defhs-final-breakthrough-asr-train826-001 --follow
kaggle kernels output khalwaniev/rs-defhs-final-breakthrough-asr-train826-001 -p work/asr_train826_return
```

Complete run requires `ASR_TRAIN826_RESULT.json` reporting `PASS`, 826/826 rows, original WAV hashes, model commit and an output inventory. The first GPU execution and model loading have **not** yet been verified by SOL6. Kaggle competition submission prohibited.
