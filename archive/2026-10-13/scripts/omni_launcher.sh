#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/fikar/zingle/defhs
RUN="$ROOT/work/system_f_omni_3b"
SOURCE=/mnt/c/Users/fikar/Downloads/DEFHS_SYSTEM_F_OMNI_AUDIO_LANE.ipynb
[[ -f "$ROOT/WORKFLOW.md" ]] || { echo 'ERROR: DEFHS repo missing'; exit 2; }
[[ -f "$SOURCE" ]] || { echo "ERROR: download notebook to $SOURCE"; exit 2; }
mkdir -p "$RUN"
cp "$SOURCE" "$RUN/run.ipynb"
python3 - "$RUN" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]); nb=json.loads((p/'run.ipynb').read_text())
assert len(nb['cells'])==2, 'Unexpected notebook version'
for j,c in enumerate(nb['cells']):
 if c['cell_type']=='code': compile(''.join(c['source']),f'cell{j}','exec')
meta={
 'id':'khalwaniev/defhs-system-f-omni-audio-001',
 'title':'DEFHS System F audio-native Omni 3B',
 'code_file':'run.ipynb','language':'python','kernel_type':'notebook',
 'is_private':True,'enable_gpu':True,'enable_internet':True,
 'machine_shape':'NvidiaTeslaT4','dataset_sources':[],
 'competition_sources':['dataverse-detecting-emotions-from-hindi-speech'],
 'kernel_sources':[]
}
(p/'kernel-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
print('NOTEBOOK_COMPILED',p/'run.ipynb',flush=True)
PY
sha256sum "$RUN/run.ipynb"
echo 'Review GPU availability before submission:'
kaggle quota
kaggle kernels list --mine
echo 'Push starts a committed notebook run. If Kaggle queues it, open the notebook in Edit and run an interactive Draft Session instead.'
kaggle kernels push -p "$RUN"
kaggle kernels status khalwaniev/defhs-system-f-omni-audio-001 || true
