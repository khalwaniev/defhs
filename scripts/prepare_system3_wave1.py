#!/usr/bin/env python3
"""Allowlist-only Kaggle package; never upload a repository or protected file."""
import argparse,base64,gzip,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'runs/RS-DEFHS-SYSTEM3-WAVE1-001'
V3=ROOT/'.tmp/rs_system_implementation_001_frozen_screen_v3/rs_defhs_system_implementation_001'
DS=ROOT/'runs/DS-DEFHS-VALIDATION-HARDENING-002'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    a=argparse.ArgumentParser();a.add_argument('--package',choices=['cache','gpu'],required=True)
    a.add_argument('--view',default='VB',choices=['VA','VB']);a.add_argument('--seed',type=int,default=20260930)
    a.add_argument('--lane',choices=['A','B']);a.add_argument('--adapted-only',action='store_true');ns=a.parse_args()
    assert not ns.adapted_only or ns.lane is not None
    if ns.package=='cache':
        dest=ROOT/'work/system3_wave1/kaggle_cache';dest.mkdir(parents=True,exist_ok=True)
        for n in ['emotion2vec_base_meanstd.npz']:
            shutil.copy2(V3/n,dest/n)
        (dest/'dataset-metadata.json').write_text(json.dumps({'title':'DEFHS System3 Wave1 Frozen Cache',
            'id':'khalwaniev/defhs-system3-wave1-cache','licenses':[{'name':'other'}]},indent=2)+'\n')
        print(dest);return
    pre=json.loads((RUN/'W1_PREFLIGHT.json').read_text());assert pre['status']=='PASS'
    if ns.lane is not None or ns.view!='VB' or ns.seed!=20260930:
        assert ns.lane is not None,'Secondary execution must name only an eligible lane.'
        confirmation=json.loads((RUN/'W1_SECONDARY_CONFIRMATION.json').read_text())
        assert json.loads((RUN/'W1_FIXED_BLEND_RESULTS.json').read_text())['status']=='COMPLETE_VB'
        for n in ['W1_E2V_ADAPTATION_RESULTS.json','W1_AST_RESULTS.json']:
            assert json.loads((RUN/n).read_text())['status']=='COMPLETE'
        if ns.seed==20260930:
            assert ns.view=='VA' and not ns.adapted_only
            assert ns.lane in confirmation['provisionally_useful_survivors']
        else:
            assert ns.seed==20260917 and ns.adapted_only
            assert ns.lane==confirmation['leading_adapted_for_seed2']
    template=ROOT/'scripts/system3_wave1_gpu.py'
    spec=json.loads((V3/'E2V_MODELSCOPE_RESOLVED_OBJECT.json').read_text())
    payload={'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'config_sha256':sha(RUN/'WAVE1_CONFIG.json'),'preflight_verdict':'PASS','view':ns.view,'seed':ns.seed,
        'e2v_cache_sha256':pre['inputs']['emotion2vec_base_meanstd.npz']['sha256'],
        'e2v_files':{f['path']:f for f in spec['files'] if f['path'] in ['config.yaml','configuration.json','emotion2vec_base.pt']},
        'input_files':{}}
    for n in ['DATA_MANIFEST.csv','DUPLICATE_GROUPS_FINAL.csv','VALIDATION_VB_FOLDS.csv','VALIDATION_VA_FOLDS.csv']:
        p=DS/n;payload['input_files'][n]={'sha256':sha(p),'gzip_b64':base64.b64encode(gzip.compress(p.read_bytes(),mtime=0)).decode()}
    if ns.lane:
        payload['workers']=[{'lane':ns.lane,'folds':[0,2,4],'arms':[1] if ns.adapted_only else [0,1]},
                            {'lane':ns.lane,'folds':[1,3],'arms':[1] if ns.adapted_only else [0,1]}]
    suffix='' if ns.lane is None else f'_{ns.lane.lower()}_{ns.view.lower()}_{ns.seed}'
    dest=ROOT/('kaggle/rs_system3_wave1_001'+suffix);dest.mkdir(parents=True,exist_ok=True)
    code=template.read_text().replace('PAYLOAD = {}  # populated by the allowlist-only package builder','PAYLOAD = '+repr(payload))
    (dest/'run.py').write_text(code)
    base_slug='defhs-system3-wave1-matched-adaptation' if ns.lane is None else 'defhs-system3-wave1'
    base_title='DEFHS System3 Wave1 Matched Adaptation' if ns.lane is None else 'DEFHS System3 Wave1'
    slug=base_slug+suffix.replace('_','-');title=base_title+suffix.replace('_',' ')
    assert 5<=len(title)<=50,'Kaggle SaveKernel requires a title of at most50 characters.'
    meta={'id':'khalwaniev/'+slug,'title':title,
        'code_file':'run.py','language':'python','kernel_type':'script','is_private':True,'enable_gpu':True,'enable_internet':True,
        'machine_shape':'NvidiaTeslaT4','competition_sources':['dataverse-detecting-emotions-from-hindi-speech'],
        'dataset_sources':['khalwaniev/defhs-system3-wave1-cache'],'kernel_sources':[],'model_sources':[]}
    (dest/'kernel-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps({'package':str(dest),'source_sha':payload['source_sha'],'runner_sha256':sha(dest/'run.py')}))
if __name__=='__main__':main()
