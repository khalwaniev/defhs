#!/usr/bin/env python3
"""One-shot SS-authorized System E Qwen3-ASR TARGET209 sealed Kaggle package.

Derive from the exact, already executed train826 ASR worker. Change ONLY
scope (209 target WAVs), manifest, mount, output names and target reporting.
Same revision, qwen-asr 0.0.6, FP16, input preprocessing and decoding.
No train labels, model tuning, protected validation or submission.
"""
import argparse, ast, base64, csv, gzip, hashlib, io, json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUTHORITY='00211674d5cee5896570a9b2c599b238bd1ec52d'
ORIGINAL='scripts/final_breakthrough_asr_worker.py'
ORIGINAL_BLOB='ac3542c7a0120222112e10f1d4a2fc3b87f805bf'
MANIFEST='runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv'
MANIFEST_SHA='1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469'
REV='b188e100bd85038c06d2812d24a39776eba774ca'
KERNEL='khalwaniev/rs-defhs-system-e-asr-target209-001'
OUT=ROOT/'kaggle/rs_system_e_asr_target209_001'
COLS=['Id','filename','file_bytes','file_sha256','sample_rate','channels','samples','sample_width_bits']
def sha(b):return hashlib.sha256(b).hexdigest()
def git_blob(b):return hashlib.sha1(('blob '+str(len(b))+'\0').encode()+b).hexdigest()
def exactly(s,a,b):
    assert s.count(a)==1,(a,s.count(a))
    return s.replace(a,b)
def go(override):
    data=(ROOT/MANIFEST).read_bytes()
    assert sha(data)==MANIFEST_SHA,'Original split/hash authority changed'
    records=list(csv.DictReader(io.StringIO(data.decode('utf-8'))))
    test=sorted((r for r in records if r['split']=='test'),key=lambda r:int(r['Id']))
    train=[r for r in records if r['split']=='train']
    ids=[int(r['Id']) for r in test]
    assert len(records)==1035 and len(train)==826 and len(test)==209
    assert ids==sorted(set(ids))
    assert {int(r['Id']) for r in test}.isdisjoint(int(r['Id']) for r in train)
    assert all(not r['emotion'] and r['filename']==f'audio_{r["Id"].zfill(6)}.wav' for r in test)
    assert all(len(r['file_sha256'])==64 and int(r['file_bytes'])>0 for r in test)
    sio=io.StringIO(newline='')
    cw=csv.DictWriter(sio,fieldnames=COLS,lineterminator='\n');cw.writeheader()
    for r in test:cw.writerow({k:r[k] for k in COLS})
    raw=sio.getvalue().encode('utf-8')
    zipped=base64.b64encode(gzip.compress(raw,mtime=0)).decode('ascii')
    orig=subprocess.run(['git','show',f'{AUTHORITY}:{ORIGINAL}'],cwd=ROOT,check=True,capture_output=True).stdout
    assert git_blob(orig)==ORIGINAL_BLOB,'Original executed worker source mismatch'
    code=orig.decode('utf-8')
    src=code

    # All model code (download, float16, package 0.0.6, transcribe, 512 tokens)
    # must remain unchanged. All textual edits below are exact-match/fail-closed.
    for a,b in [
        ('train826 only','TARGET209 only'),
        ("OUT=RUN_DIR/'QWEN3_ASR_TRAIN826.csv'","OUT=RUN_DIR/'QWEN3_ASR_TARGET209.csv'"),
        ("PROGRESS=RUN_DIR/'QWEN3_ASR_TRAIN826_PROGRESS.jsonl'","PROGRESS=RUN_DIR/'QWEN3_ASR_TARGET209_PROGRESS.jsonl'"),
        ("REPORT=RUN_DIR/'ASR_TRAIN826_RESULT.json'","REPORT=RUN_DIR/'ASR_TARGET209_RESULT.json'"),
        ("assert len(rows)==826 and len(set(ids))==826","assert len(rows)==209 and len(set(ids))==209"),
        ("print('PREFLIGHT: hash verifying 826 training WAVs'","print('PREFLIGHT: hash verifying 209 official TARGET WAVs'"),
        ("if len(completed)!=826:fail('ROW_COUNT',len(completed))","if len(completed)!=209:fail('ROW_COUNT',len(completed))"),
        ("'/826',flush=True","'/209',flush=True"),
        ("'scope':'train826_only','rows':826,'unique_Ids':826","'scope':'target209_only','rows':209,'unique_Ids':209"),
        ("'train_ids_sha256':REQUIRED_IDS_SHA256","'target_ids_sha256':REQUIRED_IDS_SHA256"),
        ("'source_audio_verified':826","'source_audio_verified':209"),
        ("'test_audio_access':False","'test_audio_access':True"),
        ("print('TRAIN826_ASR_COMPLETE',json.dumps({'status':'PASS','rows':826",
         "print('TARGET209_ASR_COMPLETE',json.dumps({'status':'PASS','rows':209"),
    ]: code=exactly(code,a,b)

    # Strictly target-only mount discovery. Train folders cannot pass.
    begin=code.index('def locate_audio(rows):')
    end=code.index('def main():',begin)
    original_mount=src[src.index('def locate_audio(rows):'):src.index('def main():')]
    assert 'SRCASW' not in original_mount and "'test' not in" in original_mount
    target_mount='''def locate_audio(rows):
 # Only official competition test WAV folder(s); never fall back to train.
 first,last=rows[0]['filename'],rows[-1]['filename']
 competition='dataverse-detecting-emotions-from-hindi-speech'
 roots=[Path('/kaggle/input/competitions')/competition,
        Path('/kaggle/input')/competition]
 checked=[]
 for root in roots:
  candidates=[root/'test',root/'Test',root/'dataset'/'test',
              root/'data'/'test',root/'SRCASW-BhavVaani'/'test']
  for p in candidates:
   checked.append(str(p))
   if p.is_dir() and (p/first).is_file() and (p/last).is_file():
    print('TARGET_AUDIO_MOUNT_RESOLVED',str(p),flush=True)
    return p
  if root.is_dir():
   matches=sorted({p.parent for p in root.rglob(first)
                   if 'test' in [part.lower() for part in p.relative_to(root).parts[:-1]]
                   and (p.parent/last).is_file()})
   for p in matches:
    if p not in candidates:
     print('TARGET_AUDIO_MOUNT_RESOLVED',str(p),flush=True)
     return p
 fail('MOUNT','209 target WAVs not found in official test tree; checked='+repr(checked))
'''
    code=code[:begin]+target_mount+code[end:]
    for const,value in [('MODEL_ID','Qwen/Qwen3-ASR-1.7B'),('MODEL_REVISION',REV),
                        ('LANGUAGE','Hindi')]:
        found={}
        for n in ast.parse(code).body:
            if isinstance(n,ast.Assign):
                for t in n.targets:
                    if isinstance(t,ast.Name) and t.id==const:found[const]=ast.literal_eval(n.value)
        assert found[const]==value
    # Compare unchanged inference procedure *exactly* with frozen source.
    for token in [
       "subprocess.run([sys.executable,'-m','pip','install','-q','--disable-pip-version-check','--no-cache-dir','qwen-asr==0.0.6'],check=True)",
       "model=Qwen3ASRModel.from_pretrained(str(local),dtype=torch.float16,device_map='cuda:0',max_inference_batch_size=1,max_new_tokens=512)",
       "result=model.transcribe(audio=str(audio_dir/r['filename']),language=LANGUAGE)",
       "info=model_info(MODEL_ID,revision=MODEL_REVISION)",
       "local=Path(snapshot_download(repo_id=MODEL_ID,revision=MODEL_REVISION))",
    ]:
        assert token in code and token in src,('frozen-inference changed',token)
    for token in ['TRAIN826_ASR_COMPLETE','826 training WAVs','train826_only']:
        assert token not in code,token
    assert '__MANIFEST_B64__' in code and '__MANIFEST_SHA256__' in code
    code=exactly(code,'__MANIFEST_B64__',zipped)
    code=exactly(code,'__MANIFEST_SHA256__',sha(raw))
    code=exactly(code,'__REQUIRED_IDS_SHA256__',sha(','.join(map(str,ids)).encode()))
    ast.parse(code)
    out=override or OUT;out.mkdir(parents=True,exist_ok=True)
    run=out/'run.py';run.write_text(code,encoding='utf-8')
    notebook={'nbformat':4,'nbformat_minor':5,
      'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
                  'language_info':{'name':'python'}},
      'cells':[
        {'cell_type':'markdown','id':'defhs-e-target-intro','metadata':{},
         'source':['# System E — frozen Qwen3-ASR TARGET209 inference\\n',
         'SS-authorized exploratory candidate production; strict WAV SHA checks; no labels or submission.\\n']},
        {'cell_type':'code','id':'defhs-e-target-code','execution_count':None,
         'metadata':{},'outputs':[],'source':code.splitlines(keepends=True)}]}
    nb=out/'target209.ipynb';nb.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+'\n')
    meta={'id':KERNEL,'title':'rs-defhs-system-e-asr-target209-001',
          'code_file':'target209.ipynb','language':'python','kernel_type':'notebook',
          'is_private':True,'enable_gpu':True,'enable_internet':True,
          'dataset_sources':[],'competition_sources':['dataverse-detecting-emotions-from-hindi-speech'],
          'kernel_sources':[],'machine_shape':'NvidiaTeslaT4'}
    (out/'kernel-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    assert ''.join(json.loads(nb.read_text())['cells'][1]['source'])==code
    # Verify embedded frozen 209-manifest directly from generated executable AST.
    consts={t.id:ast.literal_eval(n.value) for n in ast.parse(code).body if isinstance(n,ast.Assign)
            for t in n.targets if isinstance(t,ast.Name)
            and t.id in ('MANIFEST_B64','MANIFEST_SHA256','REQUIRED_IDS_SHA256')}
    rep=gzip.decompress(base64.b64decode(consts['MANIFEST_B64']))
    assert rep==raw and sha(rep)==consts['MANIFEST_SHA256']
    packaged=list(csv.DictReader(io.StringIO(rep.decode())))
    assert len(packaged)==209 and [int(q['Id']) for q in packaged]==ids
    assert all(set(q)==set(COLS) for q in packaged)
    assert not any('emotion' in q for q in packaged)
    inv={p.name:{'size':p.stat().st_size,'sha256':sha(p.read_bytes())}
         for p in [run,nb,out/'kernel-metadata.json']}
    status={'status':'TARGET209_ASR_STATIC_VERIFIED_GPU_NOT_EXECUTED',
      'mission':'SS-DEFHS-SYSTEM-E-EXPLORATORY-DEPLOYMENT-001',
      'scientific_exception':'System E Q960 gate failed; not promoted',
      'source_commit':AUTHORITY,'source_worker_blob':ORIGINAL_BLOB,
      'official_manifest_sha256':MANIFEST_SHA,'embedded_test_manifest_sha256':sha(raw),
      'target_ids_sha256':sha(','.join(map(str,ids)).encode()),
      'rows':209,'train_rows_excluded':826,'test_has_no_labels':True,
      'model':'Qwen/Qwen3-ASR-1.7B','revision':REV,'backend':'qwen-asr==0.0.6',
      'runtime':'torch.float16 / single Tesla T4 / batch1 / Hindi / max_new_tokens512',
      'gpu_not_executed':True,'kaggle_competition_submission':False,
      'files':inv}
    (out/'PACKAGE_VERIFICATION.json').write_text(json.dumps(status,indent=2)+'\n')
    (out/'README.md').write_text(
      '# System E authorized exploratory Qwen3-ASR TARGET209\\n\\n'
      'Built from exact frozen, prior successfully executed ASR train826 worker. '
      'All 209 target WAV sizes, SHA256 and RIFF metadata verified before GPU inference. '
      'No labeled train data, test labels or protected validation enter the notebook.\\n\\n'
      'Expected Kaggle output QWEN3_ASR_TARGET209.csv, '
      'QWEN3_ASR_TARGET209_PROGRESS.jsonl, ASR_TARGET209_RESULT.json, OUTPUT_INVENTORY.json.\\n'
      'No Kaggle competition submission; report results to SS.\\n')
    print(json.dumps(status,indent=2))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path)
    args=ap.parse_args();go(args.out)
if __name__=='__main__':main()
