# RS-DEFHS-TARGET209-SPECTROGRAM-EVIDENCE-001 — Execution Recovery Instructions

## Status

`USER_EXECUTION_REQUIRED=YES`

The worker runtime cannot materialize the exact 346 MB Hugging Face Xet binary or the user's multi-hundred-MB historical checkpoint files together. The scientific mission is **not failed**. A deterministic executor is committed and must be run in an environment with the historical checkpoint outputs and one GPU.

Recommended environment: **Kaggle, one GPU only**.

Why Kaggle is preferred over local WSL for full inference:

- the local laptop is CPU-only for this CUDA workload;
- the two historical AST kernel outputs can be mounted directly as `kernel_sources`;
- the competition data can be mounted directly as a `competition_source`;
- the parent is public and can be downloaded at the exact pinned revision with internet enabled;
- the executor uses only `cuda:0`, even if Kaggle allocates a multi-GPU image.

## Exact recovery authority

Parent:

- model: `MIT/ast-finetuned-audioset-10-10-0.4593`
- revision: `f826b80d28226b62986cc218e5cec390b1096902`
- file: `model.safetensors`
- required SHA256: `ae0c1e2ad4e1381d851fa9bf298ba13ebc9c5a914cdee2dbe427a6583869924d`

Historical checkpoint sources:

- seed 20260930: `khalwaniev/defhs-system3-wave1-matched-adaptation`
- seed 20260917: `khalwaniev/defhs-system3-wave1-b-vb-20260917`

Competition source:

- `dataverse-detecting-emotions-from-hindi-speech`

## Recommended Kaggle execution

Run these commands in WSL.

### COMMAND_1 — create a safe detached worktree at the live mission branch

```bash
cd /home/fikar/zingle/defhs
git fetch origin rs/target209-spectrogram-evidence-001
git worktree add --detach /home/fikar/zingle/defhs_ast_recovery_001 origin/rs/target209-spectrogram-evidence-001
cd /home/fikar/zingle/defhs_ast_recovery_001
```

This does not change the user's current checked-out branch. If the target worktree path already exists, the command fails safely; do not reset or delete an active worktree.

### COMMAND_2 — push the preconfigured one-GPU Kaggle recovery kernel

```bash
bash scripts/push_rs_defhs_target209_ast_recovery_001.sh
```

The committed metadata mounts the exact two historical kernels plus the competition input and enables internet only so the pinned Hugging Face parent can be acquired and hash-checked.

### COMMAND_3 — inspect status

```bash
kaggle kernels status khalwaniev/defhs-target209-ast-recovery-001
```

When running, inspect logs with:

```bash
kaggle kernels logs khalwaniev/defhs-target209-ast-recovery-001 --follow
```

The executor must print one final line beginning:

```text
RS_DEFHS_AST_RECOVERY_SUMMARY=
```

If parent SHA or parity fails, the script exits nonzero **before** TARGET209 inference.

### COMMAND_4 — download kernel outputs after COMPLETE

```bash
mkdir -p /home/fikar/zingle/defhs_ast_recovery_output
kaggle kernels output khalwaniev/defhs-target209-ast-recovery-001 \
  -p /home/fikar/zingle/defhs_ast_recovery_output
```

### COMMAND_5 — print the machine-readable summary

```bash
cat /home/fikar/zingle/defhs_ast_recovery_output/rs_defhs_target209_ast_recovery_001/TARGET209_AST_RECOVERY_SUMMARY.json
```

If Kaggle flattens the output directory, locate it safely with:

```bash
find /home/fikar/zingle/defhs_ast_recovery_output -name TARGET209_AST_RECOVERY_SUMMARY.json -print
```

## Expected parity success criteria

Before any TARGET209 prediction:

- exact parent SHA256 must equal `ae0c1e2ad4e1381d851fa9bf298ba13ebc9c5a914cdee2dbe427a6583869924d`;
- all 10 checkpoint STATE SHA256 values must match `AST_AUTHORITY.json`;
- all 10 historical OOF artifact SHA256 values must match their preserved RESULT files;
- parity compares 3 deterministic held-out rows per model = 30 model-row comparisons;
- `PARITY_HARD_LABEL_MISMATCHES = 0`;
- `PARITY_MAX_ABS_DIFF <= 1e-4`;
- `PARITY_MEAN_ABS_DIFF <= 2e-5`.

Any failure is a hard stop. Do not loosen tolerance and rerun as a rescue.

## Expected output paths inside Kaggle

```text
/kaggle/working/rs_defhs_target209_ast_recovery_001/
  PARITY_PREFLIGHT.json
  AST_SEGMENT_INDEX_RECOVERY.json
  TARGET209_AST_EVIDENCE.csv
  TARGET209_AST_FOLD_SEED_PROBS.npz
  TARGET209_AST_RECOVERY_SUMMARY.json
```

The parent acquisition record is stored under:

```text
/kaggle/working/ast_parent_f826b80/PARENT_ACQUISITION.json
```

`TARGET209_AST_EVIDENCE.csv` must contain exactly 209 unique IDs and columns:

```text
Id
p_angry
p_happy
p_neutral
p_sad
predicted_class
confidence
margin
...compact provenance...
```

## What to return to ChatGPT

Paste the complete contents of:

```text
TARGET209_AST_RECOVERY_SUMMARY.json
```

and upload:

```text
TARGET209_AST_EVIDENCE.csv
```

If the run fails, paste the final error plus:

```text
PARITY_PREFLIGHT.json
```

if that file exists.

Do **not** submit the CSV to Kaggle. It is model evidence, not a competition submission.

## Local WSL fallback

Local execution is supported but not recommended for the full 10-model x 209-clip inference on the user's CPU-only laptop.

To acquire/verify the parent only:

```bash
cd /home/fikar/zingle/defhs_ast_recovery_001
python -m pip install \
  "transformers==4.57.1" \
  "huggingface_hub>=0.34,<1.0" \
  hf_xet safetensors "soundfile==0.13.1"

python scripts/run_rs_defhs_target209_ast_recovery_001.py \
  --mode acquire-parent \
  --parent "$HOME/.cache/defhs/ast_parent_f826b80"
```

If the historical `.tmp` checkpoint packages and competition extraction are still present locally, a CPU run is:

```bash
python scripts/run_rs_defhs_target209_ast_recovery_001.py \
  --mode run \
  --parent "$HOME/.cache/defhs/ast_parent_f826b80" \
  --search /home/fikar/zingle/defhs/.tmp \
  --out /home/fikar/zingle/defhs_ast_recovery_output/local \
  --device cpu
```

If the historical checkpoint roots are no longer local, do not reconstruct them manually; use the committed Kaggle path above.
