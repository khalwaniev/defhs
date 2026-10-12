#!/usr/bin/env bash
# One predeclared 28-feature experiment, no tuning and no test inference.
set -Eeuo pipefail
cd "$(git rev-parse --show-toplevel)"
OUTPUT=work/rs_final_semantic_information_recovery
MARK="$OUTPUT/STRICT_D_E_PARITY_PASS.json"
PREFIX="$PWD/work/ss_d_replay_exact_py3135"
PY="$PREFIX/bin/python"
DZIP=/home/fikar/zingle/defhs-sol6-asr/work/system_e_canonical_replay/DEFHS_SYSTEM_D_FINAL_DELIVERY.zip
EZ=evidence/DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip
SZ=/home/fikar/zingle/defhs-sol6-asr/work/DEFHS_QWENASR_QWEN14_SEMANTIC826.zip
LCSV=work/rs_final_semantic_likelihood_return/defhs_qwen14_likelihoods/QWEN14B_LIKELIHOOD_TRAIN826.csv
RESULT=work/rs_final_semantic_likelihood_evaluation
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONNOUSERSITE=1
unset PYTHONPATH || true
[[ -x "$PY" && -f "$MARK" ]] || { echo 'STOP: strict D and E replay not yet verified in this exact runtime'; exit 6; }
"$PY" - "$MARK" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]));assert r['status']=='STRICT_D_E_PARITY_PASS'
print('ACCEPTED_PARITY_RECOVERY_PROVENANCE:',r)
PY

mkdir -p "$RESULT"
if [[ -f "$RESULT/PRIMARY_RESULT.json" ]]; then
  echo "STOP: primary result already exists; do not rerun one-shot experiment: $RESULT/PRIMARY_RESULT.json" >&2
  exit 7
fi

ARGS=(--d-zip "$DZIP" --e-zip "$EZ" --semantic-zip "$SZ" \
      --likelihood-csv "$LCSV" --output-dir "$RESULT")
if [[ -n "${DEFHS_ROOTS_ZIP:-}" ]]; then
  echo 'Using SS-supplied authentic component_roots.b36 evidence; six primary gates.'
  "$PY" scripts/evaluate_qwen14_label_likelihood.py "${ARGS[@]}" --roots-zip "$DEFHS_ROOTS_ZIP" \
     2>&1 | tee "$OUTPUT/CHALLENGER_PRIMARY.log"
else
  echo 'Authentic roots not yet provided: evaluating frozen five nonbootstrap gates; cannot claim primary promotion.'
  "$PY" scripts/evaluate_qwen14_label_likelihood_preroot.py "${ARGS[@]}" \
     2>&1 | tee "$OUTPUT/CHALLENGER_PRIMARY.log"
fi

[[ -f "$RESULT/PRIMARY_RESULT.json" ]] || { echo 'STOP: no primary result produced';exit 8; }
"$PY" scripts/ss_candidate_margin_audit.py \
  --challenger-oof "$RESULT/CHALLENGER_PRIMARY_OOF.csv" \
  --output "$RESULT/NUMERICAL_RANKING_MARGINS.json"

"$PY" - "$RESULT/PRIMARY_RESULT.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]));print('FROZEN_RESULT_STATUS:',r['status']);print('E:',r['baseline_macroF1'],'CHALLENGER:',r['challenger_macroF1'],'DELTA:',r['delta']);print('FOLD_DELTAS',r['fold_deltas']);print('CORRECTIONS_BREAKAGES',r['paired_changes']);print('PRIMARY_GATES',r['gates'])
PY

STATUS=$("$PY" - "$RESULT/PRIMARY_RESULT.json" <<'PY'
import json,sys
print(json.load(open(sys.argv[1]))['status'])
PY
)
if [[ "$STATUS" == "PRIMARY_PASS_PENDING_STRESS" ]]; then
  echo 'Primary 6/6 PASS; report frozen Q960 stress diagnostic; no automatic target209 inference.'
  "$PY" scripts/ss_likelihood_q960_audit.py \
    --e-zip "$EZ" \
    --challenger-oof "$RESULT/CHALLENGER_PRIMARY_OOF.csv" \
    --output "$RESULT/Q960_606_AUDIT.json"
elif [[ "$STATUS" == "STOP_PRIMARY_GATE_FAILED" ]]; then
  echo 'SCIENTIFIC STOP: frozen primary criterion failed, do not tune or run target209.'
else
  echo "NOT PROMOTED: $STATUS (authentic dependency roots and full stress still required)"
fi
