#!/usr/bin/env bash
# RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001: ONE SS-authorized exact runtime recovery.
# Read-only canonical artifacts. Only creates a separate Conda prefix and work/ reports.
set -Eeuo pipefail
cd "$(git rev-parse --show-toplevel)"
DZIP=/home/fikar/zingle/defhs-sol6-asr/work/system_e_canonical_replay/DEFHS_SYSTEM_D_FINAL_DELIVERY.zip
EZ=evidence/DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip
SZ=/home/fikar/zingle/defhs-sol6-asr/work/DEFHS_QWENASR_QWEN14_SEMANTIC826.zip
LCSV=work/rs_final_semantic_likelihood_return/defhs_qwen14_likelihoods/QWEN14B_LIKELIHOOD_TRAIN826.csv
OUTPUT=work/rs_final_semantic_information_recovery
PREFIX="$PWD/work/ss_d_replay_exact_py3135"
CONDA="$HOME/miniforge3/bin/conda"
mkdir -p "$OUTPUT"
rm -f "$OUTPUT/STRICT_D_E_PARITY_PASS.json"  # Revoke only this run's old success sentinel.
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONNOUSERSITE=1
unset PYTHONPATH || true
export DZIP EZ SZ LCSV OUTPUT PREFIX

# Verify immutable inputs before constructing any runtime. No reference changes permitted.
python3 - <<'PY'
import hashlib,os,zipfile
expected={
'DZIP':'fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839',
'EZ':'dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf',
'SZ':'cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789',
'LCSV':'66d01f825c9be4142452e6f04fb921dd8ece6c8f82aac5e0768a9941c0e4e788'}
for k,v in expected.items():
 path=os.environ[k]
 with open(path,'rb') as f:
  h=hashlib.file_digest(f,'sha256').hexdigest()
 print('INPUT',k,h,'PASS' if h==v else 'FAIL',flush=True)
 if h!=v:raise SystemExit('STOP: authenticated input mismatch '+k)
with zipfile.ZipFile(os.environ['DZIP']) as z:
 b=z.read('finalize_system_d.py')
 assert hashlib.sha256(b).hexdigest()=='b77914ef4a358e6acc19497e242ca83b769f13b3dfdacde5d8522fc4a55bf525'
 print('UNMODIFIED_D_FINALIZER_SHA PASS',flush=True)
PY

if [[ ! -x "$PREFIX/bin/python" ]]; then
  if [[ -d "$PREFIX" ]]; then
    echo 'STOP: partial existing exact prefix; do not overwrite automatically:' "$PREFIX" >&2
    exit 4
  fi
  [[ -x "$CONDA" ]] || { echo "Missing conda binary: $CONDA" >&2; exit 5; }
  echo 'ONE TARGETED INSTALL: Python 3.13.5 plus seven independently verified packages.'
  "$CONDA" create --yes --no-default-packages --prefix "$PREFIX" --channel conda-forge 'python=3.13.5' 'pip'
  "$PREFIX/bin/python" -m pip install --disable-pip-version-check --only-binary=:all: --no-cache-dir \
    'numpy==2.3.5' 'pandas==2.2.3' 'scipy==1.17.0' \
    'scikit-learn==1.8.0' 'joblib==1.5.3' 'threadpoolctl==3.6.0'
fi
PY="$PREFIX/bin/python"

# Hard version check: do not silently substitute packages.
"$PY" - <<'PY'
import json,sys,platform
import numpy,pandas,scipy,sklearn,joblib,threadpoolctl
wanted={'numpy':'2.3.5','pandas':'2.2.3','scipy':'1.17.0','sklearn':'1.8.0','joblib':'1.5.3','threadpoolctl':'3.6.0'}
mods={'numpy':numpy,'pandas':pandas,'scipy':scipy,'sklearn':sklearn,'joblib':joblib,'threadpoolctl':threadpoolctl}
assert sys.version_info[:3]==(3,13,5),(sys.version,'Python patch mismatch')
for name,expected in wanted.items():
 actual=mods[name].__version__
 assert actual==expected,(name,actual,expected)
print('EXACT_SS_PYTHON_AND_SEVEN_PACKAGES_PASS',sys.version.split()[0],flush=True)
import numpy as np
np.dot(np.ones((4,4)),np.ones((4,4)))
info={'python':sys.version,'executable':sys.executable,'packages':{k:m.__version__ for k,m in mods.items()},'threadpools':threadpoolctl.threadpool_info(),'platform':platform.platform()}
from pathlib import Path
Path('work/rs_final_semantic_information_recovery/ACTUAL_BACKEND.json').write_text(json.dumps(info,indent=2)+'\n')
print('COMPUTATIONAL_BACKEND_CAPTURED; independent SS backend metadata was not provided; exact backend parity cannot be claimed.',flush=True)
PY

# Run unchanged original D script in extracted temp tree, preserving original assertions.
if ! "$PY" - <<'PY' | tee "$OUTPUT/D_UNMODIFIED_REPLAY.log"
import hashlib,os,subprocess,sys,tempfile,zipfile
from pathlib import Path
with tempfile.TemporaryDirectory(prefix='ss_exact_D_') as temp:
 base=Path(temp)
 with zipfile.ZipFile(os.environ['DZIP']) as z:z.extractall(base)
 script=base/'finalize_system_d.py'
 assert hashlib.sha256(script.read_bytes()).hexdigest()=='b77914ef4a358e6acc19497e242ca83b769f13b3dfdacde5d8522fc4a55bf525'
 env={**os.environ,'DEFHS_SYSTEM_D_BASE':str(base)}
 p=subprocess.run([sys.executable,str(script)],cwd=str(base),env=env,capture_output=True,text=True)
 print('ORIGINAL_D_STDOUT:\n',p.stdout[-10000:],flush=True)
 print('ORIGINAL_D_STDERR:\n',p.stderr[-10000:],flush=True)
 print('ORIGINAL_D_EXIT_CODE',p.returncode,flush=True)
 assert p.returncode==0,'STOP: unmodified original D finalizer assertion failure'
 out=base/'DEFHS_SYSTEM_D_FINAL'/'submission_system_d.csv'
 assert out.exists(),'D output missing'
 sha=hashlib.sha256(out.read_bytes()).hexdigest()
 print('D_PRODUCTION_SHA256',sha,flush=True)
 assert sha=='182bfbcd5fb10b351504da6d24f3d0d33f6d05cf2786e1e1a19e80afe0e57ec9'
 print('ORIGINAL_SYSTEM_D_SOURCE_AND_OUTPUT_ALL_GATES_PASS',flush=True)
PY
then
  echo 'STRICT D REPLAY FAILED. Running original source read-only D forensic trace.' >&2
  "$PY" scripts/diagnose_system_e_d_oof_replay.py \
    --bundle "$DZIP" --output "$OUTPUT/D_REPLAY_FAILURE_TRACE.json" \
    > "$OUTPUT/D_REPLAY_FAILURE_TRACE.log" 2>&1 || true
  tail -45 "$OUTPUT/D_REPLAY_FAILURE_TRACE.log" || true
  exit 12
fi

# Reproduce original E scientific full OOF with its original 1e-8 assertions.
# This finalizer internally reruns D once more and verifies original outputs.
if ! "$PY" scripts/finalize_system_e_exploratory.py \
  --d-zip "$DZIP" \
  --e-zip "$EZ" \
  --train-new-q14-zip "$SZ" \
  --preflight-only 2>&1 | tee "$OUTPUT/E_UNMODIFIED_PREFLIGHT.log"
then
  echo 'STRICT E REPLAY FAILED. Running separate read-only baseline probability trace.' >&2
  "$PY" scripts/diagnose_system_e_baseline_readonly.py \
    --d-zip "$DZIP" --e-zip "$EZ" --semantic-zip "$SZ" \
    --likelihood-csv "$LCSV" \
    --output "$OUTPUT/E_REPLAY_FAILURE_TRACE.json" \
    > "$OUTPUT/E_REPLAY_FAILURE_TRACE.log" 2>&1 || true
  tail -35 "$OUTPUT/E_REPLAY_FAILURE_TRACE.log" || true
  exit 13
fi

# Marker written ONLY after both untouched original D and E checks succeed.
"$PY" - <<'PY'
import json,os,hashlib
from pathlib import Path
p=Path(os.environ['OUTPUT'])/'STRICT_D_E_PARITY_PASS.json'
p.write_text(json.dumps({'status':'STRICT_D_E_PARITY_PASS',
'original_D_source_sha256':'b77914ef4a358e6acc19497e242ca83b769f13b3dfdacde5d8522fc4a55bf525',
'ss_target_python':'3.13.5','ss_target_sklearn':'1.8.0',
'original_parity_assertions_unchanged':True,'submission':False,
'backend_evidence':'ACTUAL_BACKEND.json'},indent=2)+'\n')
print('STRICT_D_E_PARITY_PASS; CHALLENGER_NOW_AUTHORIZED',flush=True)
PY
