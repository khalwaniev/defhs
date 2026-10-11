#!/usr/bin/env python3
"""Independent label-blind prelaunch check: frozen Qwen3-14B TARGET209 package."""
import ast,base64,csv,gzip,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'kaggle/rs_system_e_qwen14_target209_001'
DATA=ROOT/'runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv'
DATA_SHA='1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469'
CSV_SHA='4c32a0431bff86e8e9c5153acd7225138f5790a63ff06fa001267a42ad583771'
MODEL_REV='40c069824f4251a91eefaf281ebe4c544efd3e18'
PROMPT_SHA='d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    checks=json.loads((OUT/'PACKAGE_VERIFICATION.json').read_text())
    assert checks['status']=='SYSTEM_E_QWEN14_TARGET209_STATIC_PASS_GPU_NOT_EXECUTED'
    assert checks['rows']==209 and checks['no_train_rows'] and checks['no_emotion_labels_or_folds']
    assert checks['scientific_gate_Q960_passed'] is False
    assert sha(DATA.read_bytes())==DATA_SHA
    m=list(csv.DictReader(io.StringIO(DATA.read_text())))
    test={int(v['Id']) for v in m if v['split']=='test'}
    train={int(v['Id']) for v in m if v['split']=='train'}
    assert len(test)==209 and len(train)==826 and not test.intersection(train)
    run=(OUT/'run.py').read_bytes()
    assert sha(run)==checks['run_sha256']
    assert sha((OUT/'kernel-metadata.json').read_bytes())==checks['metadata_sha256']
    tree=ast.parse(run.decode())
    literal=None
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id=='PAYLOAD':
                    assert literal is None
                    literal=ast.literal_eval(node.value)
    assert literal['model_id']=='Qwen/Qwen3-14B'
    assert literal['revision']==checks['qwen14_model_revision']==MODEL_REV
    assert sha(literal['prompt'].encode())==literal['prompt_sha256']==PROMPT_SHA
    assert literal['source_ASR_sha256']==checks['asr_output_sha256']==CSV_SHA
    raw=gzip.decompress(base64.b64decode(literal['records_gzip_b64']))
    assert sha(raw)==literal['input_sha256']==checks['input_sha256']
    rows=json.loads(raw)
    assert len(rows)==209 and len({x['Id'] for x in rows})==209
    assert [x['Id'] for x in rows]==sorted(test)
    assert all(set(x)=={'Id','transcript'} for x in rows)
    assert all(isinstance(r['transcript'],str) and r['transcript'].strip() for r in rows)
    assert checks['unique_transcripts']==len({r['transcript'] for r in rows})
    meta=json.loads((OUT/'kernel-metadata.json').read_text())
    assert meta['id']=='khalwaniev/rs-defhs-system-e-qwen14-target209-001'
    assert meta['is_private'] and meta['enable_gpu'] and meta['enable_internet']
    assert meta['competition_sources']==[] and meta['dataset_sources']==[]
    assert meta['code_file']=='run.py' and meta['kernel_type']=='script'
    code=run.decode()
    for word in ("assert len(rows) == 209 and len({r['Id'] for r in rows}) == 209",
                 "QWEN14B_TARGET209.csv",
                 "'target209_inferred':True",
                 "load_in_4bit=True",
                 "bnb_4bit_quant_type='nf4'",
                 "enable_thinking=False",
                 "max_memory={0: '13GiB', 1: '13GiB'}"):
        assert word in code,word
    assert "QWEN14B_TRAIN826.csv" not in code
    assert "'kaggle_submission':False" in code
    print("SYSTEM_E_QWEN14_TARGET209_PRELAUNCH_PASS")
    print(json.dumps({'rows':len(rows),'unique_transcripts':checks['unique_transcripts'],
                      'input_sha256':checks['input_sha256'],'runner_sha256':checks['run_sha256'],
                      'semantic_checkpoint':MODEL_REV,'label_fields_embedded':False,
                      'Kaggle_submission':False},indent=2))
if __name__=='__main__':main()
