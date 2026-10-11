#!/usr/bin/env python3
"""Fail-closed prelaunch audit of self-contained Qwen3-ASR train826 Kaggle notebook."""
import ast,base64,csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv'
BASE=ROOT/'kaggle/rs_final_breakthrough_asr_train826_001'
SHA='1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469'
REV='b188e100bd85038c06d2812d24a39776eba774ca'
COLS=['Id','filename','file_bytes','file_sha256','sample_rate','channels','samples','sample_width_bits']
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 raw=DATA.read_bytes();assert sha(raw)==SHA,'Frozen original data manifest changed'
 allrows=list(csv.DictReader(io.StringIO(raw.decode())))
 train=sorted((r for r in allrows if r['split']=='train'),key=lambda r:int(r['Id']))
 test={int(r['Id']) for r in allrows if r['split']=='test'}
 assert len(train)==826 and len(test)==209
 ids=[int(r['Id']) for r in train]
 assert ids==sorted(set(ids)) and not set(ids)&test
 nb_bytes=(BASE/'train826.ipynb').read_bytes()
 notebook=json.loads(nb_bytes)
 assert notebook['nbformat']==4 and len(notebook['cells'])==2
 assert all(c.get('id') for c in notebook['cells'])
 code=''.join(notebook['cells'][1]['source'])
 runner=(BASE/'run.py').read_text(encoding='utf-8')
 assert code==runner,'Notebook and run.py diverged'
 tree=ast.parse(code)
 assignments={}
 for item in tree.body:
  if isinstance(item,ast.Assign):
   for t in item.targets:
    if isinstance(t,ast.Name) and t.id in {'MODEL_ID','MODEL_REVISION','MANIFEST_B64','MANIFEST_SHA256','REQUIRED_IDS_SHA256','LANGUAGE'}:
     assignments[t.id]=ast.literal_eval(item.value)
 assert assignments['MODEL_ID']=='Qwen/Qwen3-ASR-1.7B'
 assert assignments['MODEL_REVISION']==REV
 assert assignments['LANGUAGE']=='Hindi'
 assert len(assignments['MANIFEST_B64'])>100000,'Not a self-contained sealed manifest'
 assert 'raw=base64.b64decode(MANIFEST_B64)' in code,'Unexpected compressed/backend manifest interface'
 minimal=base64.b64decode(assignments['MANIFEST_B64'])
 assert sha(minimal)==assignments['MANIFEST_SHA256']
 listed=list(csv.DictReader(io.StringIO(minimal.decode())))
 assert len(listed)==826 and list(listed[0])==COLS
 assert all(set(row)==set(COLS) for row in listed)
 for a,b in zip(train,listed):
  assert all(a[k]==b[k] for k in COLS)
 assert sha(','.join(map(str,ids)).encode())==assignments['REQUIRED_IDS_SHA256']
 meta=json.loads((BASE/'kernel-metadata.json').read_text())
 assert meta['id']=='khalwaniev/rs-defhs-final-breakthrough-asr-train826-001'
 assert meta['code_file']=='train826.ipynb' and meta['kernel_type']=='notebook'
 assert meta['enable_gpu'] and meta['enable_internet'] and meta['is_private']
 assert meta['competition_sources']==['dataverse-detecting-emotions-from-hindi-speech']
 assert "model.transcribe(audio=str(audio_dir" in code
 assert "Qwen3ASRModel.from_pretrained(str(local)" in code
 assert "qwen-asr==0.0.6" in code
 result={'status':'PRELAUNCH_STATIC_PASS_GPU_NOT_RUN','train_rows':826,'test_rows_excluded':209,'no_labels_in_runner_manifest':True,'model_revision':REV,
         'original_manifest_sha256':SHA,'embedded_manifest_sha256':sha(minimal),'runner_sha256':sha(runner.encode()),'notebook_sha256':sha(nb_bytes),
         'kernel_metadata_sha256':sha((BASE/'kernel-metadata.json').read_bytes())}
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
