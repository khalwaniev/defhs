#!/usr/bin/env python3
"""CPU-only self-contained Kaggle notebook builder; reconstructed after Astra's interrupted session."""
import argparse,base64,csv,gzip,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED_DATA_SHA='1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469'
TEMPLATE_NAME='scripts/final_breakthrough_asr_worker.py'
FIELDS=['Id','filename','file_bytes','file_sha256','sample_rate','channels','samples','sample_width_bits']
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=ROOT);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 repo=a.repo.resolve();out=a.out.resolve();manifest=repo/'runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv';src=repo/TEMPLATE_NAME
 raw=manifest.read_bytes()
 assert sha(raw)==EXPECTED_DATA_SHA,f'DATA_MANIFEST not frozen: {sha(raw)}'
 allrows=list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
 train=sorted((r for r in allrows if r['split']=='train'),key=lambda r:int(r['Id']))
 test=[r for r in allrows if r['split']=='test'];ids=[int(r['Id']) for r in train]
 assert len(train)==826 and len(test)==209 and len(set(ids))==826 and set(ids).isdisjoint({int(r['Id']) for r in test})
 assert all(r['file_sha256'] and r['file_bytes'] and r['emotion'] in {'angry','happy','neutral','sad'} for r in train)
 buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=FIELDS,lineterminator='\n');w.writeheader()
 for row in train:w.writerow({k:row[k] for k in FIELDS})
 frozen=buf.getvalue().encode('utf-8');fh=sha(frozen)
 code=src.read_text(encoding='utf-8')
 assert code and all(x in code for x in ['__MANIFEST_B64__','__MANIFEST_SHA256__','__REQUIRED_IDS_SHA256__'])
 encoded=base64.b64encode(gzip.compress(frozen,mtime=0)).decode()
 code=code.replace('__MANIFEST_B64__',encoded).replace('__MANIFEST_SHA256__',fh).replace('__REQUIRED_IDS_SHA256__',sha(','.join(map(str,ids)).encode()))
 assert '__MANIFEST_' not in code and '__REQUIRED_IDS_' not in code
 compile(code,'run.py','exec')
 out.mkdir(parents=True,exist_ok=True)
 (out/'run.py').write_text(code,encoding='utf-8')
 notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'cells':[
 {'cell_type':'markdown','id':'defhs-asr-intro','metadata':{},'source':['# DEFHS Qwen3-ASR train826 — recovery from interrupted Astra package\n','**Scope:** 826 WAVs, no test, no protected labels; exact frozen hashes.\n']},
 {'cell_type':'code','id':'defhs-asr-runner','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(keepends=True)}]}
 (out/'train826.ipynb').write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
 metadata={'id':'khalwaniev/rs-defhs-final-breakthrough-asr-train826-001','title':'DEFHS final breakthrough ASR train826','code_file':'train826.ipynb','language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':True,'enable_internet':True,'dataset_sources':[],'competition_sources':['dataverse-detecting-emotions-from-hindi-speech'],'kernel_sources':[],'machine_shape':'NvidiaTeslaT4'}
 (out/'kernel-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
 readme='''# Emergency ASR train826 inference — reconstructed from empty Astra files

1. Metadata is a private Kaggle *notebook*, GPU NvidiaTeslaT4, Internet ON, official DEFHS competition input.
2. Run embedded Qwen3-ASR-1.7B via qwen_asr.Qwen3ASRModel, pinned commit b188e100bd85038c06d2812d24a39776eba774ca and qwen-asr==0.0.6.
3. Preflight byte-for-byte verifies all 826 train WAVs against frozen DATA_MANIFEST.csv; no train emotion labels are shipped.
4. Local WAV decoding is managed by qwen-asr with explicit language="Hindi"; no extra resampling or alternate tokenizer/processor.
5. Exports QWEN3_ASR_TRAIN826.csv, ASR_TRAIN826_RESULT.json, OUTPUT_INVENTORY.json and progress JSONL. No Kaggle competition submission.
6. Kaggle upload is not scientific evidence. Check logs for 826 records and PASS inventory.
7. Notebook's code cell is executable without GitHub connectivity. Qwen/Qwen3-ASR-1.7B != Qwen/Qwen3-ASR-1.7B-hf.
'''
 (out/'README.md').write_text(readme,encoding='utf-8')
 import ast;ast.parse(code)
 obj=json.loads((out/'train826.ipynb').read_text());assert obj['nbformat']==4 and len(obj['cells'])==2 and ''.join(obj['cells'][1]['source'])==code
 assert all(p.stat().st_size for p in out.iterdir() if p.is_file())
 package={p.name:{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(out.iterdir()) if p.is_file()}
 check={'status':'PACKAGE_STATIC_PASS_GPU_NOT_EXECUTED','original_data_sha256':EXPECTED_DATA_SHA,'training_count':826,'test_count_excluded':209,'train_ids_sha256':sha(','.join(map(str,ids)).encode()),'manifest_embedded_sha256':fh,'model_revision':'b188e100bd85038c06d2812d24a39776eba774ca','files':package,'no_labels_in_embedded_manifest':True}
 (out/'PACKAGE_VERIFICATION.json').write_text(json.dumps(check,indent=2)+'\n')
 print(json.dumps({'status':check['status'],'rows':826,'out':str(out),'source_checkpoint':check['model_revision'],'package':{k:v['sha256'] for k,v in package.items()}},indent=2))
if __name__=='__main__':main()
