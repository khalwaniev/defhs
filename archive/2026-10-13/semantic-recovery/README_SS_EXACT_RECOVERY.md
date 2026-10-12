# RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001 — targeted SS runtime recovery

This is a scientific **execution kit**, NOT an observed primary result. No WSL process has been run by the RS environment; the end-user must execute the WSL commands. All baseline source code and scientific data remain unmodified.

## Contract

The independently verified SS runtime is Python 3.13.5, NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, scikit-learn 1.8.0, joblib 1.5.3, threadpoolctl 3.6.0. Set OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=MKL_NUM_THREADS=2 and PYTHONNOUSERSITE=1. SS did **not** supply backend `threadpoolctl.threadpool_info` metadata, so matching the package versions is necessary but insufficient to claim backend byte parity. The kit saves `ACTUAL_BACKEND.json` for follow-up comparison.

The seven previously inspected environments did not match Python 3.13.5 plus all seven packages. The script therefore creates **one** fresh Conda prefix in the worktree and installs the exact packages, with no other sweep or solver tuning. Original D ZIP, System E ZIP, original Qwen semantic ZIP, and new likelihood CSV are hash checked. The unchanged `finalize_system_d.py` is extracted into an isolated temp directory and executed with ALL its original assertions. Its original 209-row output SHA is verified. Then `finalize_system_e_exploratory.py --preflight-only` executes the unchanged D/E OOF parity assertions, including <1e-8 full E probability replay. If either fails, stop; read-only forensic traces are saved in work/.

## WSL commands — execute once

Download **DEFHS_SS_EXACT_RUNTIME_RECOVERY_KIT.zip** into Windows Downloads.

```bash
cd /home/fikar/zingle/defhs-semantic-information
unzip -o /mnt/c/Users/fikar/Downloads/DEFHS_SS_EXACT_RUNTIME_RECOVERY_KIT.zip -d .
bash -n scripts/ss_exact_runtime_recover.sh
bash -n scripts/ss_frozen_likelihood_challenger.sh

# 60-minute hard timebox applies to environment recovery + untouched D/E replay ONLY.
# The 28F experiment runs immediately on success, without a fixed time cut-off.
timeout --signal=TERM --kill-after=60s 3600 \
  bash scripts/ss_exact_runtime_recover.sh && \
  bash scripts/ss_frozen_likelihood_challenger.sh
```

The challenger automatically tests the original 28 inputs (23 E inputs + five exact trie probabilities) under frozen true nested 5-fold OOF. It does not tune parameters or perform inference on 209 test recordings. If `DEFHS_ROOTS_ZIP` is set to an **authentic original** ZIP containing `component_roots.b36`, the script runs **all six** primary gates; otherwise it uses `evaluate_qwen14_label_likelihood_preroot.py` to run the **same five nonbootstrap gates**, with primary certification held back. The missing original roots file may be present in SS's original `DEFHS_SOL6_FINAL_EVIDENCE.zip` research environment; do not reconstruct or fabricate this file.

## If the exact D or E replay fails

Inspect `work/rs_final_semantic_information_recovery/D_UNMODIFIED_REPLAY.log`, `D_REPLAY_FAILURE_TRACE.json`, `E_UNMODIFIED_PREFLIGHT.log`, `E_REPLAY_FAILURE_TRACE.json`, `ACTUAL_BACKEND.json`. Return the complete failed assertion, System C ID 731, D ID 404, and numerical probabilities to SS. Scientific hypothesis remains untested. One timeboxed target attempted: do not sweep versions.

## If five primary gates pass but authentic roots are not yet available

Do NOT rerun or refit the frozen 28-feature candidate. Obtain the original root archive from SS and complete **only** the sixth bootstrap using the frozen 826-row OOF already generated:

```bash
cd /home/fikar/zingle/defhs-semantic-information
PY="$PWD/work/ss_d_replay_exact_py3135/bin/python"
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONNOUSERSITE=1
"$PY" scripts/ss_dependency_bootstrap_complete.py \
  --roots-zip /EXACT/PATH/TO/DEFHS_SOL6_FINAL_EVIDENCE.zip \
  --primary-result work/rs_final_semantic_likelihood_evaluation/PRIMARY_RESULT.json \
  --challenger-oof work/rs_final_semantic_likelihood_evaluation/CHALLENGER_PRIMARY_OOF.csv \
  --output work/rs_final_semantic_likelihood_evaluation/PRIMARY_CERTIFICATION.json
```

If six gates pass, frozen Q960 subgroup can be evaluated with:

```bash
"$PY" scripts/ss_likelihood_q960_audit.py \
  --e-zip evidence/DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip \
  --challenger-oof work/rs_final_semantic_likelihood_evaluation/CHALLENGER_PRIMARY_OOF.csv \
  --output work/rs_final_semantic_likelihood_evaluation/Q960_606_AUDIT.json
```

Q960 uses ORIGINAL archived `manifest_flags.hex`, supports `[6,10,13,12]`, N=41. Frozen historical E-D delta = -0.03367392841077055; do not hide it. This subgroup diagnostic is **not** the entire original VA/dtype/Q960/private-allocation robustness program. No target209 inference, no public-LB label optimization, no competition submission, and the 78 retrieval assignments remain untouched.

The experimental runner also writes `NUMERICAL_RANKING_MARGINS.json` for row-level near-tie sensitivity without changing labels, ranking, or selection thresholds.

## Limitation

The exact SS computational backend was not supplied. If D parity remains different after pinning all known package versions, compare the recorded BLAS implementation/version, linked libraries, and CPU instruction sets with the SS backend before changing anything. The complete remaining evaluation beyond primary includes retrieval/nonretrieval V-A, int16↔int32 transfer, Q960 and class-stratified 616-scenario private allocation stress, plus SS promotion review. These cannot be truthfully claimed completed by the current kit.
