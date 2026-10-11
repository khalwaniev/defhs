#!/usr/bin/env python3
"""Independent prelaunch audit for sealed SS-authorized TARGET209 ASR notebook."""
import ast,base64,csv,gzip,hashlib,io,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'kaggle/rs_system_e_asr_target209_001'
DATA=ROOT/'runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv'
DATA_SHA='1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469'
REV='b188e100bd85038c06d2812d24a39776eba774ca'
KERNEL='khalwaniev/rs-defhs-system-e-asr-target209-001'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    p=OUT
    result=json.loads((p/'PACKAGE_VERIFICATION.json').read_text())
    assert result['status']=='TARGET209_ASR_STATIC_VERIFIED_GPU_NOT_EXECUTED'
    assert result['rows']==209 and result['train_rows_excluded']==826
    for name,obj in result['files'].items():
        b=(p/name).read_bytes()
        assert len(b)==obj['size'] and sha(b)==obj['sha256'],name
    code=(p/'run.py').read_text(encoding='utf-8')
    meta=json.loads((p/'kernel-metadata.json').read_text())
    nb=json.loads((p/'target209.ipynb').read_text())
    assert meta['id']==KERNEL
    assert meta['kernel_type']=='notebook' and meta['code_file']=='target209.ipynb'
    assert meta['is_private'] and meta['enable_gpu'] and meta['enable_internet']
    assert meta['competition_sources']==['dataverse-detecting-emotions-from-hindi-speech']
    assert ''.join(nb['cells'][1]['source'])==code
    tree=ast.parse(code);vals={}
    for n in tree.body:
        if isinstance(n,ast.Assign):
            for v in n.targets:
                if isinstance(v,ast.Name) and v.id in ('MANIFEST_B64','MANIFEST_SHA256','REQUIRED_IDS_SHA256','MODEL_ID','MODEL_REVISION','LANGUAGE'):
                    vals[v.id]=ast.literal_eval(n.value)
    assert vals['MODEL_ID']=='Qwen/Qwen3-ASR-1.7B'
    assert vals['MODEL_REVISION']==REV
    assert vals['LANGUAGE']=='Hindi'
    assert "print('TARGET209_ASR_COMPLETE',json.dumps({'status':'PASS','rows':209" in code, 'Incorrect target completion count'
    assert "print('TRAIN826_ASR_COMPLETE'" not in code
    embedded=gzip.decompress(base64.b64decode(vals['MANIFEST_B64']))
    assert sha(embedded)==vals['MANIFEST_SHA256']==result['embedded_test_manifest_sha256']
    assert sha(DATA.read_bytes())==DATA_SHA
    manifest=list(csv.DictReader(io.StringIO(DATA.read_text())))
    train={int(r['Id']) for r in manifest if r['split']=='train'}
    test=sorted((r for r in manifest if r['split']=='test'),key=lambda r:int(r['Id']))
    rows=list(csv.DictReader(io.StringIO(embedded.decode())))
    assert len(test)==len(rows)==209 and len(train)==826
    assert list(rows[0])==['Id','filename','file_bytes','file_sha256','sample_rate','channels','samples','sample_width_bits']
    assert rows==[{k:r[k] for k in rows[0]} for r in test]
    ids=[int(q['Id']) for q in rows]
    assert len(set(ids))==209 and set(ids).isdisjoint(train)
    assert sha(','.join(map(str,ids)).encode())==vals['REQUIRED_IDS_SHA256']==result['target_ids_sha256']
    # Decode and inference implementation remains pinned; no manual label logic.
    for line in [
       "Qwen3ASRModel.from_pretrained(str(local),dtype=torch.float16,device_map='cuda:0',max_inference_batch_size=1,max_new_tokens=512)",
       "model.transcribe(audio=str(audio_dir/r['filename']),language=LANGUAGE)",
       "qwen-asr==0.0.6",
       "'source_audio_verified':209",
       "'test_audio_access':True",
       "'protected_access':False",
    ]:assert line in code,line
    locate=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='locate_audio')
    fn=ast.Module(body=[locate],type_ignores=[])
    def err(kind,msg):raise RuntimeError(kind+': '+str(msg))
    with tempfile.TemporaryDirectory() as tmp:
        rt=Path(tmp)
        fake={'Path':lambda value:rt/str(value).lstrip('/'),'fail':err}
        exec(compile(fn,'locate_audio','exec'),fake)
        roots=rt/'kaggle/input/competitions/dataverse-detecting-emotions-from-hindi-speech'
        a,b=rows[0]['filename'],rows[-1]['filename']
        train_dir=roots/'SRCASW-BhavVaani/train';train_dir.mkdir(parents=True)
        (train_dir/a).touch();(train_dir/b).touch()
        try:fake['locate_audio'](rows)
        except RuntimeError as ex:assert str(ex).startswith('MOUNT:')
        else:raise AssertionError('TARGET209 mount illegally accepted TRAIN WAVs')
        test_dir=roots/'SRCASW-BhavVaani/test';test_dir.mkdir()
        (test_dir/a).touch();(test_dir/b).touch()
        assert fake['locate_audio'](rows)==test_dir
        (test_dir/a).unlink();(test_dir/b).unlink()
        direct=roots/'test';direct.mkdir()
        (direct/a).touch();(direct/b).touch()
        assert fake['locate_audio'](rows)==direct
    assert result['gpu_not_executed'] and not result['kaggle_competition_submission']
    print('TARGET209_ASR_PRELAUNCH_PASS: 209 manifest WAVs; labels excluded; pinned model; test-only mount; source hashes; notebook parity')
    print('NOTE: GPU inference not yet executed. Do not submit competition entry.')
if __name__=='__main__':main()
