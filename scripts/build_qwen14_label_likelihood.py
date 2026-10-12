#!/usr/bin/env python3
"""CPU-only immutable Qwen3-ASR + original Qwen14 hard-label contract to private Kaggle notebook.

Do not commit the generated notebook: it contains the existing training ASR
transcripts, not target audio, train emotions, or test labels.
"""
import argparse,base64,csv,gzip,hashlib,io,json,zipfile
from pathlib import Path

ASR_ZIP_SHA='2e35d61564d68f1577e70111a4fa47a4be096dea729b75252c9bea101e7206f5'
SEM_ZIP_SHA='cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789'
SEM_CSV_SHA='8edd8dc9899f9304db2b46475758a67330f82c3c1348317646b561f3d57f6377'

def sha(x):return hashlib.sha256(x).hexdigest()
def member(z,name):
    paths=[s for s in z.namelist() if s.rsplit('/',1)[-1]==name]
    assert len(paths)==1,(name,paths)
    return z.read(paths[0])

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--asr-zip',type=Path,required=True)
    p.add_argument('--semantic-zip',type=Path,required=True)
    p.add_argument('--worker',type=Path,default=Path(__file__).resolve().with_name('qwen14_label_likelihood_worker.py'))
    p.add_argument('--out',type=Path,default=Path('work/rs_final_semantic_likelihood_kaggle'))
    a=p.parse_args()
    assert sha(a.asr_zip.read_bytes())==ASR_ZIP_SHA,'ASR zip checksum mismatch'
    assert sha(a.semantic_zip.read_bytes())==SEM_ZIP_SHA,'Semantic zip checksum mismatch'
    with zipfile.ZipFile(a.asr_zip) as z:
        assert z.testzip() is None
        data=member(z,'QWEN3_ASR_TRAIN826.csv')
        res=json.loads(member(z,'ASR_TRAIN826_RESULT.json'))
        assert res.get('output_sha256')==sha(data),'Original ASR CSV hash mismatch'
    with zipfile.ZipFile(a.semantic_zip) as z:
        assert z.testzip() is None
        hard=member(z,'QWEN14B_TRAIN826.csv')
        assert sha(hard)==SEM_CSV_SHA
        sem_res=json.loads(member(z,'RESULT.json'))
        assert sem_res.get('output_sha256')==SEM_CSV_SHA
    ar=list(csv.DictReader(io.StringIO(data.decode('utf-8'))))
    sr=list(csv.DictReader(io.StringIO(hard.decode('utf-8'))))
    assert len(ar)==len(sr)==826
    assert set(ar[0])=={'Id','filename','file_sha256','language','transcript'}
    assert set(sr[0])=={'Id','semantic_label'}
    assert all(x['language']=='Hindi' and x['transcript'] for x in ar)
    refs={int(r['Id']):r['semantic_label'] for r in sr}
    assert len(refs)==826 and set(refs)=={int(r['Id']) for r in ar}
    assert all(x in {'angry','happy','neutral','sad','unclear'} for x in refs.values())
    records=[{'Id':int(x['Id']),'transcript':x['transcript']} for x in sorted(ar,key=lambda r:int(r['Id']))]
    assert len({r['transcript'] for r in records})==664
    payload={'records':records,'reference':refs,'asr_zip_sha256':ASR_ZIP_SHA,'semantic_zip_sha256':SEM_ZIP_SHA}
    raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    b64=base64.b64encode(gzip.compress(raw,mtime=0)).decode()
    source=a.worker.read_text()
    assert source.count('__PAYLOAD_GZIP_B64__')==1 and source.count('__PAYLOAD_SHA256__')==1
    code=source.replace('__PAYLOAD_GZIP_B64__',b64).replace('__PAYLOAD_SHA256__',sha(raw))
    compile(code,'run.py','exec')
    a.out.mkdir(parents=True,exist_ok=True)
    nb={'nbformat':4,'nbformat_minor':5,
        'metadata':{'kernelspec':{'name':'python3','language':'python','display_name':'Python 3'}},
        'cells':[{'cell_type':'markdown','metadata':{},'source':['# DEFHS frozen Qwen3-14B constrained label likelihoods\n','No train labels or test input. No submission.\n']},
                 {'cell_type':'code','execution_count':None,'outputs':[],'metadata':{},'source':code.splitlines(True)}]}
    (a.out/'run.ipynb').write_text(json.dumps(nb,ensure_ascii=False,indent=1)+'\n')
    meta={'id':'khalwaniev/rs-defhs-final-semantic-likelihood-train826-001',
        'title':'DEFHS frozen Qwen3-14B likelihood train826',
        'code_file':'run.ipynb','language':'python','kernel_type':'notebook','is_private':True,
        'enable_gpu':True,'enable_internet':True,'dataset_sources':[],
        'competition_sources':[],'kernel_sources':[],'machine_shape':'NvidiaTeslaT4'}
    (a.out/'kernel-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps({'status':'BUILD_PASS_INPUT_ARCHIVES_VERIFIED',
        'out':str(a.out),'rows':len(records),'unique':len({r['transcript'] for r in records}),
        'input_sha256':sha(raw),'notebook_sha256':sha((a.out/'run.ipynb').read_bytes())},indent=2))

if __name__=='__main__':main()
