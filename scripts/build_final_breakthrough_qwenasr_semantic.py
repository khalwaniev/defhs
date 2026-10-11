#!/usr/bin/env python3
"""Seal verified Qwen3-ASR train826 text into ORIGINAL frozen Qwen3-14B inference.
Continuation engineering, NOT a new prompt/model/decoder experiment.
Run locally in WSL. No target data, label field, folds or protected evaluation.
"""
import argparse, ast, base64, copy, csv, gzip, hashlib, io, json, re, subprocess, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PARENT='69ebbe3ca3c65f82e546fdf1d42e90fa885c8634'
ORIGINAL='kaggle/rs_final_semantic_train826_001/run.py'
BLOB='cd0b35bc68c13aca928a2ca8591b7be32ff2db19'
DATA='runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv'
DATA_SHA='1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469'
ASR_ZIP_SHA='2e35d61564d68f1577e70111a4fa47a4be096dea729b75252c9bea101e7206f5'
ASR_CSV_SHA='8ff77d69e8c39f6a4c4a508d9d0c7d00cfa728b8bfc650a6304c71d6974da86f'
ASR_REV='b188e100bd85038c06d2812d24a39776eba774ca'
QWEN14_REV='40c069824f4251a91eefaf281ebe4c544efd3e18'
PROMPT_SHA='d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f'
KERNEL='khalwaniev/rs-defhs-qwenasr-qwen14-semantic826-001'
OUTDIR=ROOT/'kaggle/rs_final_breakthrough_qwenasr_qwen14_train826_001'
def sha(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):return sha(Path(p).read_bytes())
def git_blob(raw):
    return hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()
def read_zip(archive):
    with zipfile.ZipFile(archive) as z:
        expected={'QWEN3_ASR_TRAIN826.csv','QWEN3_ASR_TRAIN826_PROGRESS.jsonl',
                  'ASR_TRAIN826_RESULT.json','OUTPUT_INVENTORY.json'}
        assert set(z.namelist())==expected,'Unexpected ASR ZIP member'
        inv=json.loads(z.read('OUTPUT_INVENTORY.json'))
        result=json.loads(z.read('ASR_TRAIN826_RESULT.json'))
        assert result['status']=='PASS' and inv['status']=='PASS'
        assert result['rows']==result['source_audio_verified']==result['unique_Ids']==826
        assert result['model_id']=='Qwen/Qwen3-ASR-1.7B' and result['model_revision']==ASR_REV
        assert not result['protected_access'] and not result['test_audio_access'] and not result['kaggle_submitted']
        assert result['output_sha256']==ASR_CSV_SHA
        for item in inv['files']:
            b=z.read(item['name'])
            assert len(b)==item['bytes'] and sha(b)==item['sha256'],item['name']
        b=z.read('QWEN3_ASR_TRAIN826.csv')
        assert sha(b)==ASR_CSV_SHA
        rows=list(csv.DictReader(io.StringIO(b.decode('utf-8'))))
        progress=[json.loads(s) for s in z.read('QWEN3_ASR_TRAIN826_PROGRESS.jsonl').decode().splitlines() if s]
    assert len(rows)==len(progress)==826 and len({int(r['Id']) for r in progress})==826
    return rows,progress
def build(archive,out):
    assert sha_file(archive)==ASR_ZIP_SHA,'ZIP checksum differs from certified user download'
    rows,progress=read_zip(archive)
    raw_manifest=(ROOT/DATA).read_bytes()
    assert sha(raw_manifest)==DATA_SHA,'Canonical frozen audio manifest changed'
    manifest=list(csv.DictReader(io.StringIO(raw_manifest.decode())))
    trains={int(v['Id']):v for v in manifest if v['split']=='train'}
    tests={int(v['Id']) for v in manifest if v['split']=='test'}
    assert len(trains)==826 and len(tests)==209 and set(trains).isdisjoint(tests)
    rows.sort(key=lambda r:int(r['Id']))
    assert len({int(v['Id']) for v in rows})==826 and {int(v['Id']) for v in rows}==set(trains)
    prog={int(p['Id']):p for p in progress}
    assert set(prog)==set(trains)
    for r in rows:
        assert set(r)=={'Id','filename','file_sha256','language','transcript'}
        k=int(r['Id']);src=trains[k];pr=prog[k]
        assert r['filename']==src['filename'] and r['file_sha256']==src['file_sha256']
        assert r['transcript']==pr['transcript'] and r['file_sha256']==pr['file_sha256']
        assert r['language']=='Hindi' and len(r['transcript'].strip())>0
        assert pr['checkpoint_revision']==ASR_REV
    # No label, fold, probability or target fields enter the sealed 14B notebook.
    records=[{'Id':int(r['Id']),'transcript':r['transcript']} for r in rows]
    assert len(records)==826
    n_unique=len({r['transcript'] for r in records})
    assert n_unique==664,'Unexpected new ASR transcript identity set'
    minimal=json.dumps(records,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    encoded=base64.b64encode(gzip.compress(minimal,mtime=0)).decode('ascii')
    orig_raw=subprocess.run(['git','show',f'{PARENT}:{ORIGINAL}'],cwd=ROOT,
                            check=True,capture_output=True).stdout
    assert git_blob(orig_raw)==BLOB,'Frozen original Qwen14B runner blob changed'
    orig=orig_raw.decode('utf-8')
    lines=orig.splitlines(keepends=True)
    indices=[i for i,s in enumerate(lines) if s.startswith('PAYLOAD = ')]
    assert len(indices)==1 and lines[indices[0]].endswith('\n')
    node=ast.parse(lines[indices[0]])
    old=ast.literal_eval(node.body[0].value)
    assert old['model_id']=='Qwen/Qwen3-14B' and old['revision']==QWEN14_REV
    assert sha(old['prompt'].encode())==old['prompt_sha256']==PROMPT_SHA
    assert old['source_ASR_sha256']=='a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01'
    assert len(old['model_files'])>=15
    new=copy.deepcopy(old)
    new['records_gzip_b64']=encoded
    new['input_sha256']=sha(minimal)
    new['source_ASR_sha256']=ASR_CSV_SHA
    new['qwenasr_revision']=ASR_REV
    assert old['model_files']==new['model_files'] and old['prompt']==new['prompt']
    lines[indices[0]]='PAYLOAD = '+repr(new)+'\n'
    code=''.join(lines)
    substitutions={
      'assert len(unique) == 711':f'assert len(unique) == {n_unique}',
      "'unique':711":f"'unique':{n_unique}",
      "'/kaggle/working/final_semantic_train826'":
      "'/kaggle/working/final_semantic_qwenasr_train826'",
    }
    for before,after in substitutions.items():
        assert code.count(before)==1,('unexpected frozen code',before)
        code=code.replace(before,after)
    ast.parse(code)
    # Static replay: frozen Qwen14B computation is unchanged except the sealed
    # input/contract, expected de-duplication count and output directory.
    frozen=orig
    for before,after in substitutions.items(): frozen=frozen.replace(before,after)
    assert code.split('\n',indices[0])[0]==frozen.split('\n',indices[0])[0]
    assert code.split('\n',indices[0]+1)[1]==frozen.split('\n',indices[0]+1)[1]
    out.mkdir(parents=True,exist_ok=True)
    runner=out/'run.py';runner.write_text(code,encoding='utf-8')
    meta={'id':KERNEL,'title':'RS DEFHS QwenASR Qwen14 Semantic826 001',
          'code_file':'run.py','language':'python','kernel_type':'script',
          'is_private':True,'enable_gpu':True,'enable_internet':True,
          'dataset_sources':[],'competition_sources':[],'kernel_sources':[],
          'machine_shape':'NvidiaTeslaT4'}
    (out/'kernel-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    check={'status':'STATIC_SEMANTIC_PACKAGE_PASS_GPU_NOT_RUN',
           'source_parent_commit':PARENT,'frozen_semantic_runner_blob':BLOB,
           'ASR_archive_sha256':ASR_ZIP_SHA,'ASR_csv_sha256':ASR_CSV_SHA,
           'ASR_model_revision':ASR_REV,'Qwen14_checkpoint_revision':QWEN14_REV,
           'prompt_sha256':PROMPT_SHA,'records_sha256':sha(minimal),
           'rows':826,'unique_transcripts':n_unique,'test_rows_embedded':0,
           'emotion_labels_or_folds_embedded':False,
           'unchanged_semantic_decoder':True,'run_sha256':sha_file(runner),
           'metadata_sha256':sha_file(out/'kernel-metadata.json')}
    (out/'PACKAGE_VERIFICATION.json').write_text(json.dumps(check,indent=2)+'\n')
    (out/'README.md').write_text(
      '# Frozen System D Qwen3-14B rerun on verified new Qwen3-ASR train826 text\n'
      'Static-sealed inference only. No emotion labels, folds, target209, or protected evaluation.\n'
      f'Original runner blob {BLOB}; same prompt {PROMPT_SHA}, checkpoint {QWEN14_REV}, '
      'constrained 5-state decoding, NF4 on two Tesla T4 GPUs.\n'
      'Output under /kaggle/working/final_semantic_qwenasr_train826/QWEN14B_TRAIN826.csv.\n'
      'Do not submit to DEFHS competition.\n')
    print(json.dumps(check,indent=2))
    return check
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--asr-zip',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=OUTDIR)
    a=ap.parse_args();build(a.asr_zip,a.out)
if __name__=='__main__': main()
