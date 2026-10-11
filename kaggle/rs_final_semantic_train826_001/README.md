# Frozen Qwen3-14B train826 run

This package contains only IDs and existing transcripts for the 826 labeled
recordings. It contains no labels, validation membership, acoustic predictions,
test transcripts, or Kaggle competition attachment. IDs never enter the prompt.

Model: `Qwen/Qwen3-14B`, revision
`40c069824f4251a91eefaf281ebe4c544efd3e18`; NF4 double quantization, FP16,
non-thinking, the unchanged historical Qwen3-8B prompt and exact-label decoding.
One configuration, batch 4, two T4 GPUs, fixed 512-token padded input.

## Run from the configured WSL repository

```bash
cd /home/fikar/zingle/defhs
git fetch origin rs/final-semantic-challenger-001
git worktree add ../defhs-final-semantic origin/rs/final-semantic-challenger-001
cd ../defhs-final-semantic
kaggle quota
kaggle kernels push -p kaggle/rs_final_semantic_train826_001 --accelerator NvidiaTeslaT4 --timeout 14400
kaggle kernels status khalwaniev/rs-defhs-final-semantic-train826-001
kaggle kernels logs khalwaniev/rs-defhs-final-semantic-train826-001 --follow
kaggle kernels output khalwaniev/rs-defhs-final-semantic-train826-001 -p work/final-semantic-return
```

Alternatively import `train826.ipynb` into a **private** Kaggle notebook, enable
Internet, select **GPU T4 x2**, and Run All. The notebook is self-contained.

The runner downloads 29.55 GB of pinned files and needs 34 GiB free cache disk.
Estimated resident weight storage is approximately 10 GB combined across the
two GPUs; this is an estimate, not a measured Kaggle result. It performs a
fixed label-blind pilot before the full run. It stops on a checksum failure,
CPU offload, insufficient memory margin, unstable repeated labels, a projected
inference time over two hours, or less than six hours remaining for evaluation.
The projection uses the warmed measured batch time with a 2x margin.

Return the entire `final_semantic_train826` output directory, especially
`FEASIBILITY.json`, `RESULT.json`, `CONTRACT.json`, `CHECKPOINT.json`,
`QWEN14B_TRAIN826.csv`, and `UNIQUE_OUTPUTS.jsonl` (or `ERROR.json` on failure).
No competition submission is made by any command above.

Current status: source access and pinned revision verified; actual GPU memory,
runtime, and prediction quality await this run. An execution failure does not
constitute negative scientific evidence.
