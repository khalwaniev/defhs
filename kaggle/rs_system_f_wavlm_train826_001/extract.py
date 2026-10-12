#!/usr/bin/env python3
"""One sealed, label-blind WavLM emotion representation extraction."""
import argparse, csv, hashlib, json, os, platform, resource, sys, time, urllib.request, zipfile
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
import transformers
from safetensors.torch import load_file
from transformers import WavLMConfig, WavLMModel
import pipeline_utils as upstream

HERE=Path(__file__).resolve().parent
MODEL='3loi/SER-Odyssey-Baseline-WavLM-Categorical'
REVISION='50632bbc8b89cbaa45077f1404601d9776cfe387'
WEIGHT_SHA='fb52f3f472b6a5a824ac238537fa60bf39a73d74b3fa5f4a4473c012cb3d18f4'
SOURCE_SHA='7a1033b5af29e5607a9213697be04d649464bd05dfa4b669ea6133a3900334e3'
NATIVE=['Angry','Sad','Happy','Surprise','Fear','Disgust','Contempt','Neutral']

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def sync(device):
    if device.type=='cuda':torch.cuda.synchronize(device)

def audio_path_map(root, rows, output):
    needed={r['filename']:r for r in rows};found={}
    for p in sorted(root.rglob('*.wav')):
        if p.name in needed:
            assert sha(p)==needed[p.name]['file_sha256'],f'WAV_HASH_MISMATCH: {p.name}'
            found.setdefault(p.name,p)
    if len(found)<len(rows):
        dest=output/'verified_audio';dest.mkdir(exist_ok=True)
        for p in sorted(root.rglob('*.zip')):
            with zipfile.ZipFile(p) as z:
                for item in z.infolist():
                    name=Path(item.filename).name
                    if name in needed and name not in found:
                        b=z.read(item);assert hashlib.sha256(b).hexdigest()==needed[name]['file_sha256'],name
                        q=dest/name;q.write_bytes(b);found[name]=q
    assert set(found)==set(needed),f'Missing verified train WAVs: {len(needed)-len(found)}'
    return found

def load_model(model_dir, device):
    assert sha(HERE/'pipeline_utils.py')==SOURCE_SHA
    weights=model_dir/'model.safetensors';model_dir.mkdir(parents=True,exist_ok=True)
    if not weights.exists():
        url=f'https://huggingface.co/{MODEL}/resolve/{REVISION}/model.safetensors'
        with urllib.request.urlopen(url,timeout=60) as src,weights.with_suffix('.part').open('wb') as out:
            while b:=src.read(4*1024*1024):out.write(b)
        weights.with_suffix('.part').rename(weights)
    assert weights.stat().st_size==1274511016 and sha(weights)==WEIGHT_SHA
    cfg=json.loads((HERE/'config.json').read_text())
    assert [cfg['id2label'][str(i)] for i in range(8)]==NATIVE
    base_cfg=WavLMConfig.from_dict(json.loads((HERE/'wavlm_config.json').read_text()))
    # Upstream architecture, replacing redundant unpinned base-weight download
    # with construction from the pinned config. ALL final tensors load below.
    class FrozenBaseFactory:
        @staticmethod
        def from_pretrained(name):
            assert name=='microsoft/wavlm-large'
            return WavLMModel(base_cfg)
    upstream.AutoModel=FrozenBaseFactory
    model=upstream.SERModel(upstream.SERConfig(**cfg))
    state=load_file(str(weights),device='cpu');expected=model.state_dict()
    conversions=[]
    for old,new in [('weight_g','parametrizations.weight.original0'),('weight_v','parametrizations.weight.original1')]:
        k='ssl_model.encoder.pos_conv_embed.conv.'+old
        nk='ssl_model.encoder.pos_conv_embed.conv.'+new
        if k in state and k not in expected and nk in expected:
            state[nk]=state.pop(k);conversions.append([k,nk])
    model.load_state_dict(state,strict=True)
    del state,expected
    return model.eval().requires_grad_(False).to(device=device,dtype=torch.float32),conversions

def forward(model, path, row, device):
    assert sha(path)==row['file_sha256']
    x,sr=sf.read(path,dtype='float32',always_2d=False)
    assert sr==16000 and x.ndim==1 and len(x)==row['samples'] and np.isfinite(x).all()
    x=(x-float(model.config.mean))/(float(model.config.std)+1e-6)
    wav=torch.from_numpy(x).unsqueeze(0).to(device)
    mask=torch.ones_like(wav)
    with torch.inference_mode():
        frames=model.ssl_model(wav,attention_mask=mask).last_hidden_state
        pooled=model.pool_model(frames,mask)
        feature=model.ser_model.get_repr(pooled)
        logits=model.ser_model.out(feature)
        probs=torch.softmax(logits,dim=1)
    a,b,c=[v.squeeze(0).cpu().numpy() for v in (feature,logits,probs)]
    assert a.shape==(1024,) and b.shape==c.shape==(8,)
    assert all(np.isfinite(v).all() for v in [a,b,c]) and abs(float(c.sum())-1)<1e-6
    return a,b,c

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--audio-root',type=Path,default=Path('/kaggle/input'))
    ap.add_argument('--model-dir',type=Path,default=Path('/kaggle/working/f_wavlm_weights'))
    ap.add_argument('--out',type=Path,default=Path('/kaggle/working/F_WAVLM_TRAIN826'))
    ap.add_argument('--device',choices=['auto','cpu','cuda'],default='auto');ap.add_argument('--threads',type=int,default=4)
    ap.add_argument('--pilot-only',action='store_true');args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    rows=json.loads((HERE/'train826_contract.json').read_text())
    assert len(rows)==826 and len({r['Id'] for r in rows})==826
    assert all(set(r)=={'Id','filename','file_sha256','samples'} for r in rows)
    device=torch.device('cuda:0' if (args.device=='cuda' or args.device=='auto' and torch.cuda.is_available()) else 'cpu')
    torch.set_num_threads(args.threads);torch.manual_seed(20261012);np.random.seed(20261012)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    contract={'model':MODEL,'revision':REVISION,'weights_sha256':WEIGHT_SHA,'rows':826,'dimension':1024,'dtype':'float32',
      'native_class_order':NATIVE,'transformers':transformers.__version__,'torch':torch.__version__,
      'python':platform.python_version(),'device':str(device),'threads':args.threads,
      'input_contract_sha256':sha(HERE/'train826_contract.json'),
      'source_files':{n:sha(HERE/n) for n in ['extract.py','pipeline_utils.py','config.json','wavlm_config.json']},
      'label_blind':True,'protected_validation_accessed':False,'test209_inferred':False}
    contract['sha256']=hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    cp=args.out/'CONTRACT.json'
    if cp.exists():assert json.loads(cp.read_text())==contract,'CHANGED_CONTRACT_CANNOT_RESUME'
    dump(cp,contract)
    paths=audio_path_map(args.audio_root,rows,args.out)
    t0=time.monotonic();model,conversions=load_model(args.model_dir,device)
    if device.type=='cuda':torch.cuda.reset_peak_memory_stats(device)
    pilot=sorted(rows,key=lambda r:(-r['samples'],r['Id']))[:4]
    sync(device);start=time.monotonic();first=[forward(model,paths[r['filename']],r,device) for r in pilot];sync(device)
    seconds=time.monotonic()-start
    second=[forward(model,paths[r['filename']],r,device) for r in pilot];sync(device)
    diff=max(float(abs(a[0]-b[0]).max()) for a,b in zip(first,second))
    forecast=2*sum(r['samples'] for r in rows)/sum(r['samples'] for r in pilot)*seconds
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    reserved=torch.cuda.max_memory_reserved(device) if device.type=='cuda' else 0
    total=torch.cuda.get_device_properties(device).total_memory if device.type=='cuda' else 0
    gates={'repeat_features_le_1e5':diff<=1e-5,'repeat_native_argmax':all(a[1].argmax()==b[1].argmax() for a,b in zip(first,second)),
      'memory_headroom':(total-reserved>=2*1024**3) if device.type=='cuda' else rss<7*1024**3,
      'forecast_le_60min':forecast<=3600}
    feasibility={'status':'PASS' if all(gates.values()) else 'EXECUTION_BLOCKED','gates':gates,'pilot_ids':[r['Id'] for r in pilot],
      'seconds':seconds,'conservative_forecast_seconds':forecast,'repeat_max_abs':diff,'peak_rss_bytes':rss,
      'gpu_peak_reserved_bytes':reserved,'gpu_total_bytes':total,'state_key_conversions':conversions,'strict_all_tensor_load':True}
    dump(args.out/'FEASIBILITY.json',feasibility);print(json.dumps(feasibility),flush=True)
    if not all(gates.values()) or args.pilot_only:return
    saved=args.out/'rows';saved.mkdir(exist_ok=True);features=[];logits=[];prob=[]
    for j,r in enumerate(rows):
        p=saved/f"{r['Id']:06d}.npz"
        if p.exists():
            with np.load(p,allow_pickle=False) as z:
                assert str(z['contract'])==contract['sha256'] and str(z['wav_sha256'])==r['file_sha256']
                a,b,c=[z[k].copy() for k in ['X','logits','prob']]
        else:
            a,b,c=forward(model,paths[r['filename']],r,device)
            np.savez(p,X=a,logits=b,prob=c,contract=contract['sha256'],wav_sha256=r['file_sha256'])
        features.append(a);logits.append(b);prob.append(c)
        if (j+1)%50==0:print(f'PROGRESS {j+1}/826 seconds={time.monotonic()-t0:.1f}',flush=True)
    np.savez_compressed(args.out/'WAVLM_TRAIN826.npz',Id=np.array([r['Id'] for r in rows],dtype=np.int64),
      X=np.stack(features),logits=np.stack(logits),native_probability=np.stack(prob),native_class_order=np.array(NATIVE),
      file_sha256=np.array([r['file_sha256'] for r in rows]))
    with (args.out/'NATIVE_OUTPUTS.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Id']+['logit_'+c for c in NATIVE]+['source_p_'+c for c in NATIVE])
        w.writerows([[r['Id']]+b.tolist()+c.tolist() for r,b,c in zip(rows,logits,prob)])
    dump(args.out/'RESULT.json',{'status':'INFERENCE_COMPLETE_NOT_EVALUATED','rows':826,'seconds':time.monotonic()-t0,
      'cpu_threads':args.threads,'gpu_hours':(time.monotonic()-t0)/3600 if device.type=='cuda' else 0,
      'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'contract_sha256':contract['sha256'],
      'feature_sha256':sha(args.out/'WAVLM_TRAIN826.npz'),'test209_inferred':False,'labels_read':False,'kaggle_submission':False})
    files=['CONTRACT.json','FEASIBILITY.json','RESULT.json','WAVLM_TRAIN826.npz','NATIVE_OUTPUTS.csv']
    dump(args.out/'OUTPUT_INVENTORY.json',{n:{'sha256':sha(args.out/n),'bytes':(args.out/n).stat().st_size} for n in files})
    with zipfile.ZipFile(args.out.parent/'DEFHS_F_WAVLM_TRAIN826.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n in files+['OUTPUT_INVENTORY.json']:z.write(args.out/n,n)
    print('INFERENCE_COMPLETE_NOT_EVALUATED',flush=True)

if __name__=='__main__':main()
