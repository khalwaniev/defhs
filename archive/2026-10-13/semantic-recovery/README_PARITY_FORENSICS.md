# DEFHS read-only baseline parity forensics

This package contains only `diagnose_system_e_baseline_readonly.py`. It does not alter the original System D finalizer, frozen System E scripts, reference CSVs, model settings, or the strict 1e-8 probability-parity gate.

To execute, unzip into existing worktree and run from its root:

```bash
cd /home/fikar/zingle/defhs-semantic-information
unzip -o /mnt/c/Users/fikar/Downloads/DEFHS_PARITY_FORENSIC_DIAGNOSTICS.zip -d .
PY=/home/fikar/zingle/defhs-sol6-asr/work/system_e_cpu_py312/bin/python
DZIP=/home/fikar/zingle/defhs-sol6-asr/work/system_e_canonical_replay/DEFHS_SYSTEM_D_FINAL_DELIVERY.zip
SEMZIP=/home/fikar/zingle/defhs-sol6-asr/work/DEFHS_QWENASR_QWEN14_SEMANTIC826.zip
OUT=work/rs_final_semantic_likelihood_diagnostics
mkdir -p "$OUT"
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONNOUSERSITE=1 "$PY" scripts/diagnose_system_e_d_oof_replay.py --bundle "$DZIP" --output "$OUT/D_ORIGINAL_TRACE.json" | tee "$OUT/D_ORIGINAL_TRACE.txt"
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONNOUSERSITE=1 "$PY" scripts/diagnose_system_e_baseline_readonly.py \
  --d-zip "$DZIP" \
  --e-zip evidence/DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip \
  --semantic-zip "$SEMZIP" \
  --likelihood-csv work/rs_final_semantic_likelihood_return/defhs_qwen14_likelihoods/QWEN14B_LIKELIHOOD_TRAIN826.csv \
  --output "$OUT/E_BASELINE_TRACE.json" | tee "$OUT/E_BASELINE_TRACE.txt"
"$PY" -m pip freeze --all > "$OUT/ENVIRONMENT_PACKAGES.txt"
git status --short > "$OUT/GIT_STATUS.txt"
sha256sum "$DZIP" "$SEMZIP" evidence/DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip work/rs_final_semantic_likelihood_return/defhs_qwen14_likelihoods/QWEN14B_LIKELIHOOD_TRAIN826.csv > "$OUT/INPUT_SHA256.txt"
zip -j "$OUT/DIAGNOSTIC_RETURN.zip" "$OUT/D_ORIGINAL_TRACE.json" "$OUT/E_BASELINE_TRACE.json" "$OUT/ENVIRONMENT_PACKAGES.txt" "$OUT/GIT_STATUS.txt" "$OUT/INPUT_SHA256.txt"
```

Return `DIAGNOSTIC_RETURN.zip`. The script reads the original authenticated evidence and reruns only the D and E baseline; **it does not evaluate the new challenger**, perform target inference, touch the protected validation, or submit to Kaggle. Original D assertions are not removed or patched; trace hooks only inspect frames at their original sites. This does not claim scientific validity.
