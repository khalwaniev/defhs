# DEFHS -- conservative primary-gate recovery without missing bootstrap archive

The original frozen 28-feature challenger, original authentic System E replay, and all six predeclared primary criteria are unchanged.

This script runs the nested System E replay and challenger and computes the first five deterministic primary gates **without** the missing component roots archive. If any of those gates fails, the preregistered challenger is scientifically rejected without needing the bootstrap; an unknown bootstrap cannot rescue an already failed requirement.

If all first five gates pass, the result is `BLOCKED_DEPENDENCY_BOOTSTRAP` (NOT `PRIMARY_PASS`) until the authenticated original `component_roots.b36` is supplied. When supplied with --roots-zip, the exact frozen 2000-draw bootstrap is computed and all six gates are enforced. No test209 inference, selection or competition submission is authorized.

## Installation

From the existing worktree:

```bash
cd /home/fikar/zingle/defhs-semantic-information
unzip -o /mnt/c/Users/fikar/Downloads/DEFHS_PREROOT_RECOVERY_PATCH.zip -d .
```

## Evaluation (no root archive required)

```bash
DZIP=/home/fikar/zingle/defhs-sol6-asr/work/system_e_canonical_replay/DEFHS_SYSTEM_D_FINAL_DELIVERY.zip
SEMZIP=/home/fikar/zingle/defhs-sol6-asr/work/DEFHS_QWENASR_QWEN14_SEMANTIC826.zip
PY=/home/fikar/zingle/defhs-sol6-asr/work/system_e_cpu_py312/bin/python

OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 "$PY" \
  scripts/evaluate_qwen14_label_likelihood_preroot.py \
  --d-zip "$DZIP" \
  --e-zip evidence/DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip \
  --semantic-zip "$SEMZIP" \
  --likelihood-csv work/rs_final_semantic_likelihood_return/defhs_qwen14_likelihoods/QWEN14B_LIKELIHOOD_TRAIN826.csv \
  --output-dir work/rs_final_semantic_likelihood_evaluation

cat work/rs_final_semantic_likelihood_evaluation/PRIMARY_RESULT.json
```

If the Python executable is missing, locate another verified Python 3.12 scientific environment; do not change solver/hyperparameters or data.

When the original roots ZIP is recovered, rerun the **same** script with `--roots-zip /actual/verified/DEFHS_SOL6_FINAL_EVIDENCE.zip` and an alternate output directory. Do not claim full scientific promotion until all frozen gates pass.
