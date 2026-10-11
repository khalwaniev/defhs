#!/usr/bin/env python3
"""Post-Astra recovery of Qwen3-ASR-1.7B, train826 only. This file was previously empty."""
import base64,csv,gzip,hashlib,importlib.metadata,io,json,os,subprocess,sys,time,traceback,wave
from pathlib import Path
MODEL_ID='Qwen/Qwen3-ASR-1.7B'
MODEL_REVISION='b188e100bd85038c06d2812d24a39776eba774ca'
BACKEND='qwen-asr==0.0.6 / Qwen3ASRModel.from_pretrained / Transformers'
LANGUAGE='Hindi'
MANIFEST_B64='__MANIFEST_B64__'
MANIFEST_SHA256='__MANIFEST_SHA256__'
REQUIRED_IDS_SHA256='__REQUIRED_IDS_SHA256__'
RUN_DIR=Path('/kaggle/working') if Path('/kaggle').exists() else Path.cwd()
OUT=RUN_DIR/'QWEN3_ASR_TRAIN826.csv'
PROGRESS=RUN_DIR/'QWEN3_ASR_TRAIN826_PROGRESS.jsonl'
REPORT=RUN_DIR/'ASR_TRAIN826_RESULT.json'
INVENTORY=RUN_DIR/'OUTPUT_INVENTORY.json'
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(8<<20),b''): h.update(b)
 return h.hexdigest()
def dump(path,obj):
 tmp=path.with_suffix(path.suffix+'.tmp')
 tmp.write_text(json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 os.replace(tmp,path)
def fail(phase,message):
 dump(REPORT,{'status':'TECHNICAL_BLOCKER','phase':phase,'error':str(message),'checkpoint':MODEL_ID,'revision':MODEL_REVISION,'protected_access':False,'submitted':False})
 raise RuntimeError(f'{phase}: {message}')
def read_manifest():
 raw=gzip.decompress(base64.b64decode(MANIFEST_B64))
 assert sha_bytes(raw)==MANIFEST_SHA256,'Embedded manifest SHA mismatch'
 rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
 ids=[int(r['Id']) for r in rows]
 assert len(rows)==826 and len(set(ids))==826 and ids==sorted(ids)
 assert all(set(r)=={'Id','filename','file_bytes','file_sha256','sample_rate','channels','samples','sample_width_bits'} for r in rows)
 assert all(r['filename']==f'audio_{int(r["Id"]):06d}.wav' and len(r['file_sha256'])==64 for r in rows)
 assert sha_bytes(','.join(map(str,ids)).encode())==REQUIRED_IDS_SHA256
 return rows
def locate_audio(rows):
 # Kaggle competition_sources mount at /kaggle/input/competitions/<slug>/,
 # never directly at /kaggle/input/competitions/train.
 first,last=rows[0]['filename'],rows[-1]['filename']
 competition='dataverse-detecting-emotions-from-hindi-speech'
 roots=[Path('/kaggle/input/competitions')/competition,
        Path('/kaggle/input')/competition]
 checked=[]
 for root in roots:
  candidates=[root/'train',root/'dataset'/'train',root/'data'/'train',
              root/'Train',root]
  for p in candidates:
   checked.append(str(p))
   if p.is_dir() and (p/first).is_file() and (p/last).is_file():
    print('AUDIO_MOUNT_RESOLVED',str(p),flush=True)
    return p
  # Fail-closed bounded recursive recovery for an extra organizer-created
  # subdirectory. Never search a /test tree or arbitrary unrelated datasets.
  if root.is_dir():
   matches=sorted(p.parent for p in root.rglob(first)
                  if 'test' not in [part.lower() for part in p.parts]
                  and (p.parent/last).is_file())
   for p in matches:
    if p not in candidates:
     print('AUDIO_MOUNT_RESOLVED',str(p),flush=True)
     return p
 fail('MOUNT','Frozen 826 training WAVs not mounted under official competition root; checked='+repr(checked))
def main():
 start=time.time();rows=read_manifest();audio_dir=locate_audio(rows)
 print('PREFLIGHT: hash verifying 826 training WAVs',flush=True)
 for i,r in enumerate(rows):
  p=audio_dir/r['filename']
  if not p.is_file() or p.stat().st_size!=int(r['file_bytes']) or sha_file(p)!=r['file_sha256']: fail('WAV_HASH',f'WAV mismatch at {r["Id"]}')
  with wave.open(str(p),'rb') as w:
   if (w.getframerate(),w.getnchannels(),w.getnframes(),w.getsampwidth()*8)!=(int(r['sample_rate']),int(r['channels']),int(r['samples']),int(r['sample_width_bits'])): fail('WAV_METADATA',f'Header mismatch at {r["Id"]}')
  if i%100==0:print('PREFLIGHT_VERIFIED',i+1,flush=True)
 import torch
 if not torch.cuda.is_available():fail('CUDA','No GPU present, check Kaggle quota and NvidiaTeslaT4')
 free,total=torch.cuda.mem_get_info(0)
 if free<9*(1024**3):fail('VRAM',f'Insufficient free VRAM: {free/(1024**3):.1f}GiB')
 print('GPU',torch.cuda.get_device_name(0),'free_GiB',round(free/(1024**3),2),flush=True)
 subprocess.run([sys.executable,'-m','pip','install','-q','--disable-pip-version-check','--no-cache-dir','qwen-asr==0.0.6'],check=True)
 from huggingface_hub import model_info,snapshot_download
 info=model_info(MODEL_ID,revision=MODEL_REVISION)
 if info.sha!=MODEL_REVISION:fail('MODEL_REVISION',info.sha)
 local=Path(snapshot_download(repo_id=MODEL_ID,revision=MODEL_REVISION))
 must=['config.json','preprocessor_config.json','tokenizer_config.json','model-00001-of-00002.safetensors','model-00002-of-00002.safetensors']
 if not all((local/x).is_file() and (local/x).stat().st_size>0 for x in must):fail('MODEL_FILES','Weights/processor missing')
 hashes={n:{'bytes':(local/n).stat().st_size,'sha256':sha_file(local/n)} for n in must}
 from qwen_asr import Qwen3ASRModel
 model=Qwen3ASRModel.from_pretrained(str(local),dtype=torch.float16,device_map='cuda:0',max_inference_batch_size=1,max_new_tokens=512)
 version=importlib.metadata.version('qwen-asr')
 if version!='0.0.6':fail('ASR_PACKAGE_VERSION',version)
 completed={};expected={int(r['Id']):r for r in rows}
 if PROGRESS.is_file():
  for line in PROGRESS.read_text(encoding='utf-8').splitlines():
   if not line.strip():continue
   v=json.loads(line);key=int(v['Id'])
   if key not in expected or v['file_sha256']!=expected[key]['file_sha256'] or v['checkpoint_revision']!=MODEL_REVISION:fail('RESUME','Provenance mismatch')
   if key in completed and v!=completed[key]:fail('RESUME','Conflicting progress rows')
   completed[key]=v
 with PROGRESS.open('a',encoding='utf-8') as f:
  for index,r in enumerate(rows):
   key=int(r['Id'])
   if key in completed:continue
   result=model.transcribe(audio=str(audio_dir/r['filename']),language=LANGUAGE)
   if not isinstance(result,list) or len(result)!=1 or not isinstance(result[0].text,str):fail('ASR_RESULT',f'Invalid result for {key}')
   transcript=result[0].text.strip();detected=str(result[0].language)
   record={'Id':key,'filename':r['filename'],'file_sha256':r['file_sha256'],'checkpoint_revision':MODEL_REVISION,'requested_language':LANGUAGE,'detected_language':detected,'transcript':transcript}
   if any(c in transcript for c in '\x00\r\n'):fail('ASR_RESULT',f'Control character in transcript {key}')
   f.write(json.dumps(record,ensure_ascii=False,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno());completed[key]=record
   if (index+1)%20==0:print('ASR_PROGRESS',len(completed),'/826',flush=True)
 if len(completed)!=826:fail('ROW_COUNT',len(completed))
 with OUT.open('w',encoding='utf-8',newline='') as f:
  writer=csv.writer(f);writer.writerow(['Id','filename','file_sha256','language','transcript'])
  for r in rows:
   o=completed[int(r['Id'])];writer.writerow([r['Id'],o['filename'],o['file_sha256'],o['detected_language'],o['transcript']])
 dump(REPORT,{'status':'PASS','scope':'train826_only','rows':826,'unique_Ids':826,'model_id':MODEL_ID,'model_revision':MODEL_REVISION,'qwen_asr_version':version,'backend':BACKEND,'language_requested':LANGUAGE,'manifest_sha256':MANIFEST_SHA256,'train_ids_sha256':REQUIRED_IDS_SHA256,'weights_and_processor':hashes,'source_audio_verified':826,'gpu':torch.cuda.get_device_name(0),'elapsed_seconds':round(time.time()-start,2),'protected_access':False,'test_audio_access':False,'kaggle_submitted':False,'output_sha256':sha_file(OUT)})
 dump(INVENTORY,{'status':'PASS','files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha_file(p)} for p in (OUT,PROGRESS,REPORT)],'model_id':MODEL_ID,'revision':MODEL_REVISION})
 print('TRAIN826_ASR_COMPLETE',json.dumps({'status':'PASS','rows':826,'csv_sha256':sha_file(OUT),'inventory_sha256':sha_file(INVENTORY)}),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:
  if not REPORT.exists():dump(REPORT,{'status':'TECHNICAL_BLOCKER','error':str(e),'traceback':traceback.format_exc(),'protected_access':False,'kaggle_submitted':False})
  raise
