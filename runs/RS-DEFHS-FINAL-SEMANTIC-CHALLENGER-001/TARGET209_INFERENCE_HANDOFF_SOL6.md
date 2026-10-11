# TARGET209 Qwen3-14B inference handoff — PREPARED, NOT EXECUTED

Scientific eligibility: semantic 5/5 PASS, frozen PRIMARY_CV 6/6 PASS, candidate-specific stress 7/7 PASS. System C remains untouched, user/SS public LB 0.86997. The branch contains `scripts/prepare_target209_package_sol6.py`, a guarded **CPU-only package generator**. The target GPU inference and any leaderboard submission have **not** run. Only SS can authorize the next stage.

## Exact authority

Original parent `10286ee67c555e775e5be8cc0eb529593039d53f`. Original 826 inference runner: `kaggle/rs_final_semantic_train826_001/run.py`, SHA256 `84cf6b644b2f4c1c996a6b2e539be70bab566a81aca67631e42059ff61eb81b8`. Canonical original ASR: `ASR_TRANSCRIPTS.csv` SHA256 `a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01`. System C original submission SHA256 `8ab7c5dc291cd9d1223283245fb62130b03bf728f764c5eeedf9d2915153e2a8`. Generator checks all these hashes before it writes any target package.

Model `Qwen/Qwen3-14B`; revision `40c069824f4251a91eefaf281ebe4c544efd3e18`; prompt SHA256 `d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f`; unchanged NF4 double quant, FP16, dual-T4, non-thinking and greedy exact-label constraint. It replaces only the sealed training records with sorted **209 test IDs + raw transcripts**, updates input hash and target-specific output filename/counts; never includes labels, audio features, folds, or protected data in LLM messages. No model-configuration experimentation.

## Step A — prepare private target package (no GPU / no submission)

The source `ASR_TRANSCRIPTS.csv` must be present in WSL with the exact hash above; the downloadable SOL6 reproduction-input ZIP contains it.

```bash
cd /home/fikar/zingle/defhs
git fetch origin rs/final-semantic-challenger-001-sol6-continuation
git worktree add ../defhs-sol6-continuation origin/rs/final-semantic-challenger-001-sol6-continuation
cd ../defhs-sol6-continuation
mkdir -p work/final_semantic_inputs
unzip -oj /mnt/c/Users/fikar/Downloads/DEFHS_SOL6_REPRODUCTION_INPUTS.zip ASR_TRANSCRIPTS.csv -d work/final_semantic_inputs
python3 scripts/prepare_target209_package_sol6.py \
  --repo . \
  --asr work/final_semantic_inputs/ASR_TRANSCRIPTS.csv \
  --out work/final_semantic_target209_package
```

Expect status `READY_FOR_SS_GPU_AUTHORIZATION_NOT_SUBMITTED`, and three files: `run.py`, `kernel-metadata.json`, `TARGET209_PREP_MANIFEST.json`. They remain outside Git tracking.

## Step B — GPU inference, ONLY upon explicit SS authorization

```bash
kaggle kernels push -p work/final_semantic_target209_package --accelerator NvidiaTeslaT4 --timeout 14400
kaggle kernels status khalwaniev/rs-defhs-final-semantic-target209-001
kaggle kernels logs khalwaniev/rs-defhs-final-semantic-target209-001 --follow
kaggle kernels output khalwaniev/rs-defhs-final-semantic-target209-001 -p work/final_semantic_target209_return
```

**Do not execute Step B without SS approval.** The run generates `QWEN14B_TARGET209.csv`, `CONTRACT.json`, `CHECKPOINT.json`, `FEASIBILITY.json`, `UNIQUE_OUTPUTS.jsonl`, `RESULT.json`, and `OUTPUT_INVENTORY.json`. Before constructing a candidate check original test IDs, exactly 209 rows, five allowable semantic states, transcript join, pinned revision/prompt, all hashes and false submission/protected-access flags.

## Step C — SS-gated final candidate

Combine target 14B and old Qwen8B semantics with authenticated waveform test probabilities using the same predeclared **18-feature** model and leakage-safe production refit. Maintain all **78** certified retrieval overrides, unchanged target Id ordering and `Id,emotion` submission schema. Compare every changed prediction against System C and inspect the existing target 60-row HARD cohort. The 209-row hidden labels are unknown; no public leaderboard tuning. **Send one exact candidate and hashes to SS; Kaggle submission requires separate explicit SS authorization.**

Local experiment ZIP contains every primary OOF row, all 616 private-allocation scenarios and scientific proof of gate passage; the GitHub continuation report records the key results and provenance.
