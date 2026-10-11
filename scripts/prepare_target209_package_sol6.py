#!/usr/bin/env python3
"""Prepare (do NOT execute) a sealed, label-blind 209-target Kaggle script.

Only after all frozen scientific gates pass; launching GPU inference separately
requires SS approval. Existing 826 source runner must match canonical SHA256.
Exactly preserves original Qwen model, revision, prompt, weights, quantization,
constrained decoding and zero-labelled-input model contract.
"""
from __future__ import annotations
import argparse, ast, base64, gzip, hashlib, json
from pathlib import Path
import pandas as pd

CANONICAL_RUN_SHA='84cf6b644b2f4c1c996a6b2e539be70bab566a81aca67631e42059ff61eb81b8'
ASR_SHA='a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01'
ORIGINAL_PROMPT_SHA='d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f'
ORIGINAL_REVISION='40c069824f4251a91eefaf281ebe4c544efd3e18'
C_SHA='8ab7c5dc291cd9d1223283245fb62130b03bf728f764c5eeedf9d2915153e2a8'

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def replace_exact(source,old,new,count=1):
    observed=source.count(old)
    assert observed==count,(old,observed,count)
    return source.replace(old,new)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',required=True,type=Path,help='Git checkout of exact Astra handoff commit')
    ap.add_argument('--asr',required=True,type=Path,help='Exact SHA256-verified canonical ASR_TRANSCRIPTS.csv')
    ap.add_argument('--out',required=True,type=Path,help='Locally built target inference package; do not commit transcripts')
    a=ap.parse_args()
    source_path=a.repo/'kaggle/rs_final_semantic_train826_001/run.py'
    original=source_path.read_bytes()
    assert sha(original)==CANONICAL_RUN_SHA,('frozen runner SHA',sha(original))
    asr=a.asr.read_bytes()
    assert sha(asr)==ASR_SHA,('frozen ASR SHA',sha(asr))
    d=pd.read_csv(a.asr)
    assert len(d)==1035 and d.Id.is_unique and set(d.split)=={'train','test'}
    t=d[d.split.eq('test')].sort_values('Id').reset_index(drop=True)
    assert len(t)==209 and t.Id.is_unique and t.transcript.notna().all()
    incumbent=a.repo/'runs/RS-DEFHS-NESTED-SEMANTIC-FUSION-001/submission_nested_semantic_fusion.csv'
    assert sha(incumbent.read_bytes())==C_SHA, 'Incumbent C submission authority mismatch'
    incumbent_ids=pd.read_csv(incumbent).Id.to_numpy()
    assert len(incumbent_ids)==209 and len(set(incumbent_ids))==209
    assert set(incumbent_ids)==set(t.Id), 'Candidate test IDs do not match C incumbent IDs'
    assert len(set(t.Id).intersection(d.loc[d.split.eq('train'),'Id']))==0
    assert a.out.resolve()!=source_path.parent.resolve(), 'Never overwrite original sealed 826 runner'
    original_script=original.decode('utf8')
    tree=ast.parse(original_script)
    pay=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
      and any(isinstance(z,ast.Name) and z.id=='PAYLOAD' for z in n.targets))
    assert pay['model_id']=='Qwen/Qwen3-14B' and pay['revision']==ORIGINAL_REVISION
    assert pay['prompt_sha256']==ORIGINAL_PROMPT_SHA
    assert sha(pay['prompt'].encode())==ORIGINAL_PROMPT_SHA
    original_pay=dict(pay)
    test_records=[{'Id':int(row.Id),'transcript':str(row.transcript)} for row in t.itertuples()]
    encoded=json.dumps(test_records,ensure_ascii=False,separators=(',',':')).encode('utf8')
    unique_count=len(dict.fromkeys(r['transcript'] for r in test_records))
    pay['records_gzip_b64']=base64.b64encode(gzip.compress(encoded,mtime=0)).decode('ascii')
    pay['input_sha256']=sha(encoded)
    lines=original_script.splitlines(keepends=True)
    ix=[i for i,v in enumerate(lines) if v.startswith('PAYLOAD = ')]
    assert len(ix)==1
    lines[ix[0]]='PAYLOAD = '+repr(pay)+'\n'
    script=''.join(lines)
    script=replace_exact(script,'final_semantic_train826','final_semantic_target209')
    script=replace_exact(script,"assert len(rows) == 826 and len({r['Id'] for r in rows}) == 826",
       "assert len(rows) == 209 and len({r['Id'] for r in rows}) == 209")
    script=replace_exact(script,'assert len(unique) == 711',f'assert len(unique) == {unique_count}')
    script=replace_exact(script,"'rows': 826,", "'rows': 209,")
    script=replace_exact(script,"'rows':826,'unique':711",f"'rows':209,'unique':{unique_count}")
    script=replace_exact(script,'QWEN14B_TRAIN826.csv','QWEN14B_TARGET209.csv',2)
    script=replace_exact(script,'TRAIN_UNIQUE=','TARGET_UNIQUE=')
    script=replace_exact(script,'starting frozen train826 inference','starting frozen target209 inference')
    script=replace_exact(script,"'target209_inferred':False","'target209_inferred':True")
    script=replace_exact(script,"'labels_or_test_inputs_present': False", "'labels_or_test_inputs_present': True")
    script=replace_exact(script,'No labels, folds, audio features, or test rows.', 'No labels, folds, or audio features. Contains exactly 209 unlabeled target transcripts.')
    parsed=ast.parse(script)
    now=next(ast.literal_eval(n.value) for n in parsed.body if isinstance(n,ast.Assign)
      and any(isinstance(z,ast.Name) and z.id=='PAYLOAD' for z in n.targets))
    assert {k:v for k,v in now.items() if k not in ('records_gzip_b64','input_sha256')} == {k:v for k,v in original_pay.items() if k not in ('records_gzip_b64','input_sha256')}
    assert sha(gzip.decompress(base64.b64decode(now['records_gzip_b64'])))==now['input_sha256']
    assert [r['Id'] for r in json.loads(gzip.decompress(base64.b64decode(now['records_gzip_b64'])))]==t.Id.tolist()
    assert all(set(row)=={'Id','transcript'} for row in test_records)
    assert 'QWEN14B_TRAIN826.csv' not in script and "'target209_inferred':False" not in script
    a.out.mkdir(parents=True,exist_ok=False)
    (a.out/'run.py').write_text(script)
    meta={'id':'khalwaniev/rs-defhs-final-semantic-target209-001','title':'DEFHS frozen Qwen3-14B target209',
       'code_file':'run.py','language':'python','kernel_type':'script','is_private':True,
       'enable_gpu':True,'enable_internet':True,'dataset_sources':[],
       'competition_sources':[],'kernel_sources':[],'machine_shape':'NvidiaTeslaT4'}
    (a.out/'kernel-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    manifest={'status':'READY_FOR_SS_GPU_AUTHORIZATION_NOT_SUBMITTED','source_commit':'10286ee67c555e775e5be8cc0eb529593039d53f',
       'runner_source_sha256':CANONICAL_RUN_SHA,'target_runner_sha256':sha(script.encode()),'model':'Qwen/Qwen3-14B',
       'revision':ORIGINAL_REVISION,'prompt_sha256':ORIGINAL_PROMPT_SHA,'source_asr_sha256':ASR_SHA,
       'target_input_sha256':sha(encoded),'test_rows':209,'unique_test_transcripts':unique_count,
       'input_fields':['Id','transcript'],'label_fields_present':False,'incumbent_C_sha256':C_SHA,
       'frozen_retrieval_decisions':78,'kaggle_submission_authorized':False}
    (a.out/'TARGET209_PREP_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))
    print('Created target script + metadata ONLY, NO GPU job and NO Kaggle submission.')

if __name__=='__main__':main()
