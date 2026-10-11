# Exact execution handoff

Only GPU inference requires external execution. The source snapshot and every
weight-shard URL are accessible (HTTP 200); this agent has no GPU, PyTorch,
Kaggle CLI, Kaggle credentials or Kaggle connector. This is not negative evidence
about Qwen3-14B's scientific value.

## Kaggle launch from configured WSL

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

If the worktree already exists from the initial package handoff, fetch the branch
and use `git -C ../defhs-final-semantic checkout --detach origin/rs/final-semantic-challenger-001`
after preserving any local edits. Do not re-push/re-run an already running kernel.
The inference package is unchanged by the later scientific-results commit.

Without CLI access, import `kaggle/rs_final_semantic_train826_001/train826.ipynb`
into a private Kaggle notebook, select **GPU T4 x2**, turn **Internet on**, Run All.
The notebook includes only train826 transcripts and needs no attached dataset.
Do not run the template file directly: the assembled runner contains the sealed
payload. Do not upload the entire repository as a Kaggle dataset.

Return `FEASIBILITY.json`, `RESULT.json`, `CONTRACT.json`, `CHECKPOINT.json`,
`QWEN14B_TRAIN826.csv`, `UNIQUE_OUTPUTS.jsonl` and `OUTPUT_INVENTORY.json`.
On failure return `ERROR.json` and any completed feasibility/provenance files.
The output root inside Kaggle is `/kaggle/working/final_semantic_train826/`.
Memory/runtime or access failure stops this selected-model experiment; no fallback
model or decoding configuration is automatically launched.

## CPU evaluation (RS can execute after receiving the output)

The current RS workspace already contains the authenticated waveform inputs and
C replay cache. If continuing in WSL instead, use Python 3.12 and the observed
CPU package versions to reproduce the accepted C replay:

```bash
python3.12 -m venv .venv-final-semantic
.venv-final-semantic/bin/python -m pip install numpy==2.3.5 pandas==2.2.3 scipy==1.17.0 scikit-learn==1.8.0 joblib==1.5.3
.venv-final-semantic/bin/python scripts/prepare_final_semantic_inputs.py --search-root /home/fikar/zingle/defhs --out work/final_semantic_inputs
.venv-final-semantic/bin/python scripts/final_semantic_challenger.py replay --inputs work/final_semantic_inputs
.venv-final-semantic/bin/python scripts/final_semantic_challenger.py evaluate --inputs work/final_semantic_inputs --inference work/final-semantic-return/final_semantic_train826
```

If Kaggle flattens output paths, pass `--inference work/final-semantic-return`
instead: the argument must be the directory actually containing `CONTRACT.json`.
If existing waveform files are outside the original repository, point
`--search-root` at their common directory. The collector copies only files with
the exact registered hashes. Missing files are listed with canonical private
Drive URLs; download them with the user's existing authenticated Drive access
into `work/final_semantic_inputs` and rerun the collector.

The evaluator writes the semantic comparison first. Only the fixed semantic
gate permits one 18-feature nested fusion. Only its PRIMARY_CV gate permits
new V-A, V-D/Q and private-allocation stress. A failed gate stops immediately.
Re-running evaluation over an existing `SEMANTIC_RESULTS.json` is refused;
retain evidence and diagnose any interrupted computation instead of deleting
the result or changing a prompt to retry.

No command submits a CSV. TARGET209 inference and a submission candidate remain
closed until the actual new-model scientific gates pass. Passing this script
does not authorize Kaggle submission or protected-validation access.
