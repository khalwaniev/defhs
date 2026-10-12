# DEFHS Qwen3-14B frozen likelihood — reproducible execution kit

Mission: `RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001`
Remote research branch: `rs/final-semantic-information-001`
Parent: `6b23148e21b75d10611fbb4deb2d6811b26221c3`
No Kaggle competition submission or protected test labels.

## Scope and scientific contract

1. Exact original Qwen3-14B checkpoint, prompt SHA256 `d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f`, original 5-state trie, unchanged non-thinking tokenization and dual T4 NF4 setup.
2. Compute normalized state probabilities under the ORIGINAL constrained decoder. The script also records unrestricted label-token log-likelihoods explicitly *excluding* unconstrained EOS; forced terminal EOS has probability 1 under the original trie.
3. Demand native-generation pilot parity and complete exact hard-label parity 826/826 before evaluating any supervised feature.
4. One preregistered nested challenger: System E 23-feature fusion plus five constrained state probability features, no parameter sweep. Frozen 5-fold group-safe nested OOF, robust primary gates, and fail closed when missing dependency roots.
5. No target209 inference unless SS authorizes following genuine primary **and** stress promotion.

## Stage 1 — launch GPU work from WSL (no data labels or test rows)

Download this kit to Windows `Downloads`. Then:

```bash
cd /home/fikar/zingle/defhs
git fetch origin rs/final-semantic-information-001
git worktree add -b rs/final-semantic-information-001 ../defhs-semantic-information origin/rs/final-semantic-information-001
cd ../defhs-semantic-information

# Unpack downloaded kit into worktree (the file name is fixed below)
unzip -o /mnt/c/Users/fikar/Downloads/DEFHS_QWEN_LIKELIHOOD_EXECUTION_KIT.zip -d .
python3 -m py_compile scripts/qwen14_label_likelihood_worker.py scripts/build_qwen14_label_likelihood.py scripts/evaluate_qwen14_label_likelihood.py

python3 scripts/build_qwen14_label_likelihood.py \
  --asr-zip /home/fikar/zingle/defhs-sol6-asr/work/DEFHS_QWEN3_ASR_TRAIN826_VERIFIED.zip \
  --semantic-zip /home/fikar/zingle/defhs-sol6-asr/work/DEFHS_QWENASR_QWEN14_SEMANTIC826.zip \
  --out work/rs_final_semantic_likelihood_kaggle

kaggle quota
kaggle kernels push -p work/rs_final_semantic_likelihood_kaggle --accelerator NvidiaTeslaT4 --timeout 14400
kaggle kernels status khalwaniev/rs-defhs-final-semantic-likelihood-train826-001
kaggle kernels logs khalwaniev/rs-defhs-final-semantic-likelihood-train826-001 --follow
kaggle kernels output khalwaniev/rs-defhs-final-semantic-likelihood-train826-001 -p work/rs_final_semantic_likelihood_return
```

If the local branch/worktree was already created, do not repeat `git worktree add`; use the existing worktree after confirming its head. Avoid re-pushing an already running notebook. Use the verified Kaggle output directory; it may be nested under `defhs_qwen14_likelihoods`.

Required successful artifacts in the output directory:
`CONTRACT.json`, `FEASIBILITY.json`, `UNIQUE_LIKELIHOODS.jsonl`, `QWEN14B_LIKELIHOOD_TRAIN826.csv`, `RESULT.json`.

Stop and report to SS if any feasibility, model hash, pilot parity, full parity, resource or deadline gate fails. The bundled reference E ZIP is *scientific evidence*, not the two authentic training inference ZIPs.

## Stage 2 — one supervised nested CV (only after GPU PASS)

The connected-component roots must be retrieved from the authentic `DEFHS_SOL6_FINAL_EVIDENCE.zip` (containing `component_roots.b36`), no artificial substitute. Locate it:

```bash
find /home/fikar/zingle /mnt/c/Users/fikar/Downloads -type f \
  \( -name 'DEFHS_SOL6_FINAL_EVIDENCE.zip' -o -name 'component_roots.b36' \) -print 2>/dev/null
```

Set the actual verified paths, and reuse the existing pinned System E CPU environment:

```bash
DZIP=/mnt/c/Users/fikar/Downloads/DEFHS_SYSTEM_D_FINAL_DELIVERY.zip
EZIP="$PWD/evidence/DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip"
SEMZIP=/home/fikar/zingle/defhs-sol6-asr/work/DEFHS_QWENASR_QWEN14_SEMANTIC826.zip
ROOTSZIP=/path/to/DEFHS_SOL6_FINAL_EVIDENCE.zip  # replace ONLY with authentic located archive
LIKELIHOODCSV="$PWD/work/rs_final_semantic_likelihood_return/defhs_qwen14_likelihoods/QWEN14B_LIKELIHOOD_TRAIN826.csv"

sha256sum "$DZIP" "$SEMZIP" "$EZIP" "$ROOTSZIP" "$LIKELIHOODCSV"

PY=/home/fikar/zingle/defhs-sol6-asr/work/system_e_cpu_py312/bin/python
# If the venv is elsewhere, use its verified Python 3.12 + numpy/scikit-learn setup.
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 "$PY" \
  scripts/evaluate_qwen14_label_likelihood.py \
  --d-zip "$DZIP" --e-zip "$EZIP" --semantic-zip "$SEMZIP" \
  --likelihood-csv "$LIKELIHOODCSV" --roots-zip "$ROOTSZIP" \
  --output-dir work/rs_final_semantic_likelihood_evaluation
```

The ZIP's E evidence is inspected and internally SHA verified; its original container hash is not claimed to equal the earlier registered original ZIP hash, because uploads can be repackaged.

**Important:** If `system_e_cpu_py312` is located elsewhere, do not assume the illustrated executable path exists. Find the actual interpreter with `find` and verify package versions. No newly selected sklearn version is authorized without full System E probability parity.

## Stage 3 — report, do not submit

On PRIMARY_FAIL return `PRIMARY_RESULT.json` + any CSV audit to SS, stop. On PRIMARY_PASS return the results for independent V-A, dtype, V-Q and private-allocation robustness before any target inference. Never submit to Kaggle or change the 78 certified retrieval assignments during this mission.

## GitHub sync after local kit extraction

```bash
git add scripts/qwen14_label_likelihood_worker.py \
        scripts/build_qwen14_label_likelihood.py \
        scripts/evaluate_qwen14_label_likelihood.py
git commit -m 'Add reproducible frozen Qwen14 constrained likelihood extractor and one nested E challenger'
git push -u origin rs/final-semantic-information-001
```

Do not commit the generated Kaggle notebook, which embeds training transcripts, or any model checkpoints. Only small reports and source code belong in GitHub.
