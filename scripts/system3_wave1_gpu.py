#!/usr/bin/env python3
"""Two independent GPU lanes, registered pilots/refits, checkpointed fold jobs."""
from __future__ import annotations
import base64, gzip, hashlib, json, math, multiprocessing as mp, os, random
import subprocess, sys, time, traceback, urllib.request
from pathlib import Path
PAYLOAD = {}  # populated by the allowlist-only package builder
OUT=Path('/kaggle/working/rs_system3_wave1_001')
INPUT=Path('/kaggle/input')
CLASSES=['angry','happy','neutral','sad']

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def dump(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+f'.{os.getpid()}.tmp');tmp.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n');tmp.replace(p)
def ih(ids):return hashlib.sha256(''.join(f'{int(i)}\n' for i in ids).encode()).hexdigest()
def seed_all(seed):
    import numpy as np, torch
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
def atomic_torch(p,obj):
    import torch
    tmp=p.with_suffix('.tmp');torch.save(obj,tmp);tmp.replace(p)

def load_parent(lane,device):
    import torch
    if lane=='A':
        from funasr import AutoModel
        root=Path('/tmp/system3_e2v');root.mkdir(parents=True,exist_ok=True)
        spec=PAYLOAD['e2v_files']
        for n in ['config.yaml','configuration.json','emotion2vec_base.pt']:
            f=root/n
            import fcntl
            with (root/(n+'.lock')).open('w') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                if not f.exists():
                    url=f'https://modelscope.cn/api/v1/models/iic/emotion2vec_base/repo?Revision=v2.0.4&FilePath={n}'
                    with urllib.request.urlopen(url,timeout=180) as r,f.open('wb') as w:
                        while True:
                            b=r.read(1<<20)
                            if not b:break
                            w.write(b)
            assert sha(f)==spec[n]['sha256'],n
        model=AutoModel(model=str(root),device=device,disable_update=True).model
        blocks=model.blocks;dim=1536
        assert len(blocks)==8
        meta={'model':'iic/emotion2vec_base','revision':'v2.0.4','file_hashes':spec,'shared_blocks':8,'representation':'valid final frames masked mean+std population std'}
    else:
        from transformers import ASTModel,ASTFeatureExtractor
        name='MIT/ast-finetuned-audioset-10-10-0.4593';rev='f826b80d28226b62986cc218e5cec390b1096902'
        processor=ASTFeatureExtractor.from_pretrained(name,revision=rev)
        assert processor.sampling_rate==16000 and processor.num_mel_bins==128 and processor.max_length==1024
        assert processor.mean==-4.2677393 and processor.std==4.5689974 and processor.padding_side=='right'
        assert not processor.return_attention_mask
        model=ASTModel.from_pretrained(name,revision=rev,attn_implementation='sdpa').to(device)
        assert model.config.time_stride==10 and model.config.frequency_stride==10
        blocks=model.encoder.layer;dim=768
        meta={'model':name,'revision':rev,'processor':processor.to_dict(),'blocks':len(blocks),
              'representation':'average classification/distillation tokens; probability average of full-coverage segments'}
        root=Path(model.config._name_or_path)
        from huggingface_hub import snapshot_download
        root=Path(snapshot_download(name,revision=rev,local_files_only=True))
        meta['file_hashes']={str(f.relative_to(root)):sha(f) for f in root.rglob('*') if f.is_file() and f.suffix in ['.json','.bin','.safetensors']}
    model.eval()
    for p in model.parameters():p.requires_grad_(False)
    dump(OUT/f'{lane}_PARENT_PROVENANCE.json',meta)
    return model,blocks,dim,(processor if lane=='B' else None)

class ClipInputs:
    def __init__(self,records,processor,lane,seed):
        import numpy as np,soundfile as sf,torch
        self.lane=lane;self.seed=seed;self.wav={};self.feats={};self.ids={}
        for r in records:
            a,sr=sf.read(r['path'],dtype='float32');assert sr==16000 and a.ndim==1
            assert len(a)==r['samples'] and np.isfinite(a).all()
            i=int(r['Id']);self.ids[i]=r['duplicate_group']
            if lane=='A':self.wav[i]=torch.from_numpy(a)
            else:
                segments=[]
                # Exactly 1024 Kaldi frames: 400 + 1023*160 samples.
                window=164080
                for start in range(0,len(a),window):
                    raw=a[start:start+window]
                    if len(raw)<400:raw=np.pad(raw,(0,400-len(raw)))
                    real_frames=min(1024,1+(len(raw)-400)//160)
                    z=processor(raw,sampling_rate=16000,return_tensors='pt')['input_values'][0].cpu()
                    assert z.shape==(1024,128)
                    segments.append((z,real_frames,start,min(start+window,len(a))))
                self.feats[i]=segments
        if lane=='B':
            dump(OUT/'AST_SEGMENT_INDEX.json',[{'Id':i,'duplicate_group':self.ids[i],
                'segments':[{'start_sample':s,'end_sample':e,'real_frames':r} for _,r,s,e in seg]} for i,seg in self.feats.items()])
    def get(self,i,epoch,augment=False):
        import numpy as np,torch
        if self.lane=='A':return self.wav[int(i)]
        seg=[]
        for k,(z,real,_,_) in enumerate(self.feats[int(i)]):
            x=z.clone()
            if augment:
                key=f'{self.seed}|{int(i)}|{epoch}|{k}|specaugment'
                rng=np.random.default_rng(int(hashlib.sha256(key.encode()).hexdigest()[:16],16))
                if rng.random()<.5:
                    fw=int(rng.integers(0,9));tw=int(rng.integers(0,min(16,int(.1*real))+1))
                    if fw:
                        start=int(rng.integers(0,129-fw));x[:real,start:start+fw]=0
                    if tw:
                        start=int(rng.integers(0,real-tw+1));x[start:start+tw,:]=0
                assert torch.equal(x[real:],z[real:]),'SpecAugment touched padding'
            seg.append(x)
        return seg

def e2v_rep(model,wav,device):
    import torch
    import torch.nn.functional as F
    x=wav.to(device);x=F.layer_norm(x,x.shape).view(1,-1)
    r=model.extract_features(x,padding_mask=None,mask=False,remove_extra_tokens=True)
    z=r['x'][0]
    if r['padding_mask'] is not None:z=z[~r['padding_mask'][0]]
    assert z.shape[1]==768 and len(z)>0
    return torch.cat([z.mean(0),z.std(0,correction=0)])

def schedule_groups(encoder,blocks,head,lane,adapt):
    groups=[]
    named=[('head',list(head.named_parameters()),1e-3,1)]
    if adapt:
        top=list(range(len(blocks)-4,len(blocks)))
        for j in top:
            p=list(blocks[j].named_parameters());lr=(1e-5 if lane=='A' else 2e-5)*(.8**(len(blocks)-1-j))
            named.append((f'block{j}',p,lr,3 if j>=len(blocks)-2 else 5))
    for name,params,lr,active in named:
        for decay in [True,False]:
            ps=[p for n,p in params if (p.ndim>1 and 'bias' not in n and 'norm' not in n.lower())==decay]
            if ps:groups.append({'params':ps,'lr':0.,'base_lr':lr,'activation_epoch':active,
                                 'weight_decay':.05 if decay else 0.,'name':name})
    return groups

def worker(lane,gpu,records,view,optimization_seed,resume_root,fold_list=None,arms=None):
    import numpy as np,pandas as pd,torch
    import torch.nn.functional as F
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from threadpoolctl import threadpool_limits
    torch.set_num_threads(2);torch.cuda.set_device(gpu);device=f'cuda:{gpu}'
    torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
    torch.backends.cuda.matmul.allow_tf32=False
    seed_all(optimization_seed)
    encoder,blocks,dim,processor=load_parent(lane,device)
    # Parents remain in eval mode; the registered head has explicit 0.2 dropout.
    # Gradients still flow through the active encoder blocks in evaluation mode.
    parent_state={n:t.detach().cpu().clone() for n,t in encoder.state_dict().items()}
    clips=ClipInputs(records,processor,lane,optimization_seed)
    folds=pd.read_csv(OUT/f'VALIDATION_{view}_FOLDS.csv').sort_values('Id').reset_index(drop=True)
    ids=folds.Id.to_numpy();fs=folds.fold.to_numpy();y=np.array([CLASSES.index(e) for e in folds.emotion])
    cache=np.load(next(INPUT.rglob('emotion2vec_base_meanstd.npz')));ix={int(i):k for k,i in enumerate(cache['Id'])}
    assert sha(next(INPUT.rglob('emotion2vec_base_meanstd.npz')))==PAYLOAD['e2v_cache_sha256']
    x=cache['X'][[ix[int(i)] for i in ids]]
    history=[];batch=16;micro=2
    frozen_ast={}
    lane_dir=OUT/f'{lane}_{view}_seed{optimization_seed}';lane_dir.mkdir(exist_ok=True)
    if resume_root:
        import shutil
        p=Path(resume_root)/lane_dir.name
        if p.exists():shutil.copytree(p,lane_dir,dirs_exist_ok=True)
    def initialize(training,fold):
        seed_all(optimization_seed+fold)
        encoder.load_state_dict(parent_state)
        for p in encoder.parameters():p.requires_grad_(False)
        encoder.eval();head=torch.nn.Linear(dim,4).to(device)
        if lane=='A':
            with threadpool_limits(limits=2):
                fit=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=5000,random_state=20261001)).fit(x[training],folds.emotion.to_numpy()[training])
            assert list(fit.classes_)==CLASSES
            scaler=(torch.tensor(fit[0].mean_,dtype=torch.float32,device=device),torch.tensor(fit[0].scale_,dtype=torch.float32,device=device))
            with torch.no_grad():
                head.weight.copy_(torch.tensor(fit[1].coef_,device=device,dtype=torch.float32));head.bias.copy_(torch.tensor(fit[1].intercept_,device=device,dtype=torch.float32))
            pp=torch.softmax(head((torch.tensor(x,dtype=torch.float32,device=device)-scaler[0])/scaler[1]),1).detach().cpu().numpy()
            authority=fit.predict_proba(x)
            assert np.max(np.abs(pp-authority))<2e-5 and np.array_equal(pp.argmax(1),authority.argmax(1))
        else:scaler=None
        return head,scaler
    def probability(head,scaler,i,epoch,training,adapt):
        if lane=='A':
            if not adapt or epoch<=2:
                r=torch.tensor(x[np.searchsorted(ids,i)],device=device,dtype=torch.float32)
            else:r=e2v_rep(encoder,clips.get(i,epoch),device)
            r=(r-scaler[0])/scaler[1]
            if training:r=F.dropout(r,p=.2,training=True)
            return torch.softmax(head(r),-1)
        ps=[]
        use_frozen=not adapt or epoch<=2
        cache_key=(int(i),int(epoch) if training else 0)
        if use_frozen and cache_key not in frozen_ast:
            with torch.no_grad():
                frozen_ast[cache_key]=[encoder(z.unsqueeze(0).to(device)).pooler_output[0].detach().cpu()
                                      for z in clips.get(i,epoch,augment=training)]
        reps=frozen_ast[cache_key] if use_frozen else clips.get(i,epoch,augment=training)
        for z in reps:
            if use_frozen:r=z.to(device)
            else:r=encoder(z.unsqueeze(0).to(device)).pooler_output[0]
            if training:r=F.dropout(r,p=.2,training=True)
            ps.append(torch.softmax(head(r),-1))
        return torch.stack(ps).mean(0)
    def eval_ids(head,scaler,indices,epoch,adapt):
        encoder.eval();head.eval();ps=[]
        with torch.no_grad():
            for j in indices:ps.append(probability(head,scaler,int(ids[j]),epoch,False,adapt).cpu().numpy())
        p=np.stack(ps)
        return p,float(-np.log(p[np.arange(len(indices)),y[indices]].clip(1e-15)).mean())
    def train_fit(training,stopping,fold,adapt,kind,epochs=None):
        name=f'{lane}{int(adapt)}_fold{fold}_{kind}'
        done=lane_dir/f'{name}_DONE.json';ckpt=lane_dir/f'{name}_STATE.pt'
        fingerprint={'recipe_sha256':PAYLOAD['config_sha256'],'lane':lane,'view':view,'seed':optimization_seed,'fold':fold,
            'adapt':adapt,'kind':kind,'training_ID_sha256':ih(ids[training]),'stopping_ID_sha256':ih(ids[stopping]),'epochs':epochs}
        head,scaler=initialize(training,fold)
        groups=schedule_groups(encoder,blocks,head,lane,adapt);opt=torch.optim.AdamW(groups)
        if done.exists():
            r=json.loads(done.read_text());assert r['fingerprint']==fingerprint
            state=torch.load(ckpt,map_location=device,weights_only=False)
            head.load_state_dict(state['head']);encoder.load_state_dict(state['encoder_delta'],strict=False)
            return head,scaler,r
        limit=20 if epochs is None else epochs
        indices=np.flatnonzero(training);stops=np.flatnonzero(stopping)
        steps=len(indices)//batch;assert steps>0
        best=0;bad=0;start_epoch=1;traces=[];runtime=0.;bestce=None
        best_path=lane_dir/f'{name}_BEST.pt'
        if len(stops):_,bestce=eval_ids(head,scaler,stops,0,False)
        if not best_path.exists():atomic_torch(best_path,{'head':head.state_dict(),'encoder_delta':{},'epoch':0})
        if ckpt.exists():
            saved=torch.load(ckpt,map_location=device,weights_only=False);assert saved['fingerprint']==fingerprint
            encoder.load_state_dict(saved['encoder_delta'],strict=False);head.load_state_dict(saved['head']);opt.load_state_dict(saved['optimizer'])
            best=saved['best_epoch'];bestce=saved['best_ce'];bad=saved['bad'];traces=saved['traces'];start_epoch=saved['epoch']+1;runtime=saved['runtime_seconds']
            random.setstate(saved['rng_python']);np.random.set_state(saved['rng_numpy']);torch.set_rng_state(saved['rng_torch'].cpu());torch.cuda.set_rng_state(saved['rng_cuda'].cpu(),gpu)
            if epochs is None and bad>=4:start_epoch=limit+1
        torch.cuda.reset_peak_memory_stats(gpu)
        selected_names={n for n,_ in head.named_parameters()}
        encoder_names={n for n,_ in encoder.named_parameters() if any(n.startswith(('blocks.' if lane=='A' else 'encoder.layer.')+str(j)+'.') for j in range(len(blocks)-4,len(blocks)))} if adapt else set()
        started=time.monotonic();examples=0
        for epoch in range(start_epoch,limit+1):
            active=0 if not adapt or epoch<=2 else (2 if epoch<=4 else 4)
            for p in encoder.parameters():p.requires_grad_(False)
            for block in list(blocks)[len(blocks)-active:] if active else []:
                for p in block.parameters():p.requires_grad_(True)
            encoder.eval();head.train();order=np.random.default_rng(optimization_seed+fold*10000+epoch).permutation(indices)
            losses=[];ep_start=time.monotonic()
            for step in range(steps):
                opt.zero_grad(set_to_none=True)
                for g in opt.param_groups:
                    global_progress=(epoch-1+step/steps)/20
                    lrscale=global_progress/.1 if global_progress<.1 else .5*(1+math.cos(math.pi*(global_progress-.1)/.9))
                    active_epoch=g['activation_epoch'];ramp=min(1.,epoch-active_epoch+step/steps) if active_epoch>1 else 1.
                    g['lr']=g['base_lr']*max(0.,lrscale)*max(0.,ramp) if epoch>=active_epoch else 0.
                chosen=order[step*batch:(step+1)*batch]
                for offset in range(0,batch,micro):
                    # Clip-level gradients; all segments share one clip weight.
                    micro_losses=[]
                    for j in chosen[offset:offset+micro]:
                        p=probability(head,scaler,int(ids[j]),epoch,True,adapt)
                        loss=-torch.log(p[y[j]].clamp_min(1e-15));micro_losses.append(loss);losses.append(float(loss.detach()))
                    (torch.stack(micro_losses).sum()/batch).backward()
                torch.nn.utils.clip_grad_norm_([p for g in opt.param_groups for p in g['params'] if p.requires_grad],1.)
                opt.step();examples+=batch
            ce=None
            if len(stops):_,ce=eval_ids(head,scaler,stops,epoch,adapt)
            if epochs is not None:best=epoch
            elif ce<bestce:
                bestce=ce;best=epoch;bad=0
                atomic_torch(best_path,{'head':head.state_dict(),'encoder_delta':{n:t for n,t in encoder.state_dict().items() if n in encoder_names},'epoch':epoch})
            else:bad+=1
            traces.append({'epoch':epoch,'train_CE':float(np.mean(losses)),'stop_CE':ce,'active_top_blocks':active,
                           'wall_seconds':time.monotonic()-ep_start,'training_clips':steps*batch,'dropped_tail_clips':len(indices)-steps*batch})
            state={'fingerprint':fingerprint,'head':head.state_dict(),'encoder_delta':{n:t for n,t in encoder.state_dict().items() if n in encoder_names},
                   'optimizer':opt.state_dict(),'epoch':epoch,'best_epoch':best,'best_ce':bestce,'bad':bad,'traces':traces,
                   'rng_python':random.getstate(),'rng_numpy':np.random.get_state(),'rng_torch':torch.get_rng_state(),'rng_cuda':torch.cuda.get_rng_state(gpu),
                   'runtime_seconds':runtime+time.monotonic()-started}
            atomic_torch(ckpt,state)
            print(f'{lane}{int(adapt)} {view} fold{fold} {kind} epoch{epoch} stopCE={ce} best={best}',flush=True)
            if epochs is None and bad>=4:break
        if epochs is None:
            winner=torch.load(best_path,map_location=device,weights_only=False);head.load_state_dict(winner['head']);encoder.load_state_dict(parent_state);encoder.load_state_dict(winner['encoder_delta'],strict=False)
            # Persist selected state, while retaining optimizer/RNG continuation.
            state=torch.load(ckpt,map_location=device,weights_only=False) if ckpt.exists() else {'optimizer':opt.state_dict(),'rng_python':random.getstate(),'rng_numpy':np.random.get_state(),'rng_torch':torch.get_rng_state(),'rng_cuda':torch.cuda.get_rng_state(gpu)}
            state.update({'fingerprint':fingerprint,'head':head.state_dict(),'encoder_delta':winner['encoder_delta'],'selected_epoch':best})
            atomic_torch(ckpt,state)
        elif limit==0:
            atomic_torch(ckpt,{'fingerprint':fingerprint,'head':head.state_dict(),'encoder_delta':{},'optimizer':opt.state_dict(),'selected_epoch':0,
                'rng_python':random.getstate(),'rng_numpy':np.random.get_state(),'rng_torch':torch.get_rng_state(),'rng_cuda':torch.cuda.get_rng_state(gpu)})
        r={'fingerprint':fingerprint,'selected_epoch':best,'best_stopping_CE':bestce,'traces':traces,
           'wall_seconds':runtime+time.monotonic()-started,'peak_GPU_memory_bytes':torch.cuda.max_memory_allocated(gpu),
           'examples_per_second':examples/max(time.monotonic()-started,1e-9),'microbatch':micro,'accumulation':batch//micro,
           'trainable_parameter_counts':{'head':sum(p.numel() for p in head.parameters()),'top2':sum(p.numel() for b in list(blocks)[-2:] for p in b.parameters()) if adapt else 0,
                                        'top4':sum(p.numel() for b in list(blocks)[-4:] for p in b.parameters()) if adapt else 0},
           'checkpoint_sha256':sha(ckpt),'encoder_pretrained_layers_mode':'eval; gradient-enabled only for active blocks',
           'AMP':False,'scheduler_denominator_epochs':20,'effective_batch':16,'augmentation':'NONE' if lane=='A' else 'registered deterministic per-ID/per-epoch mild SpecAugment'}
        dump(done,r);return head,scaler,r
    # A tiny live parity check is required for the differentiable API, not a
    # repeated extraction package. All other frozen features are reused.
    if lane=='A':
        diffs=[]
        for j in [0,1,2]:
            with torch.no_grad():live=e2v_rep(encoder,clips.get(int(ids[j]),0),device).cpu().numpy()
            diffs.append(float(np.max(np.abs(live-x[j]))))
        assert max(diffs)<2e-5,diffs
        dump(OUT/'A_DIFFERENTIABLE_API_PARITY.json',{'Ids':ids[:3].tolist(),'max_abs_feature_differences':diffs,'tolerance':2e-5})
    # One complete matched pair for each outer fold; no outer-label decisions.
    for fold in (range(5) if fold_list is None else fold_list):
        H=fs==fold;S=~H;g=(fold+1)%5;stop=S&(fs==g);pilot=S&~stop
        for adapt in ([False,True] if arms is None else [bool(a) for a in arms]):
            stem=f'{lane}{int(adapt)}_fold{fold}'
            output=lane_dir/f'{stem}_OOF.npz';decision=lane_dir/f'{stem}_RESULT.json'
            if decision.exists():
                r=json.loads(decision.read_text());assert sha(output)==r['prediction_sha256'];history.append(r);continue
            _,_,pilot_rec=train_fit(pilot,stop,fold,adapt,'pilot')
            head,scaler,refit_rec=train_fit(S,np.zeros(len(ids),bool),fold,adapt,'refit',pilot_rec['selected_epoch'])
            p,_=eval_ids(head,scaler,np.flatnonzero(H),pilot_rec['selected_epoch'],adapt)
            assert np.isfinite(p).all() and np.allclose(p.sum(1),1,atol=1e-6)
            np.savez_compressed(output,Id=ids[H],prob=p)
            r={'arm':lane+str(int(adapt)),'view':view,'fold':fold,'seed':optimization_seed,'selected_epoch':pilot_rec['selected_epoch'],
               'pilot':pilot_rec,'refit':refit_rec,'prediction_ID_sha256':ih(ids[H]),'prediction_sha256':sha(output),
               'outer_heldout_used_for_stopping':False,'source_sha':PAYLOAD['source_sha']}
            dump(decision,r);history.append(r);print(f'VALID_OUTER_FOLD_COMPLETE={lane}{int(adapt)} {view} fold{fold}',flush=True)
    if lane=='B' and frozen_ast:
        keys=sorted(frozen_ast);flat=[];indptr=[0]
        for key in keys:
            flat.extend([z.numpy() for z in frozen_ast[key]]);indptr.append(len(flat))
        np.savez_compressed(lane_dir/f'FROZEN_AST_FEATURES_GPU{gpu}.npz',Id=np.array([k[0] for k in keys]),
            epoch=np.array([k[1] for k in keys]),indptr=np.array(indptr),X=np.stack(flat),
            seed=np.array(optimization_seed),config_sha256=np.array(PAYLOAD['config_sha256']))
    suffix='' if fold_list is None else '_folds'+''.join(map(str,fold_list))
    dump(OUT/f'{lane}_{view}_seed{optimization_seed}{suffix}_RESULTS.json',{'status':'COMPLETE','folds':history,'source_sha':PAYLOAD['source_sha'],
         'protected_validation_read':False,'kaggle_submission_made':False})

def safe_worker(*args):
    try:worker(*args)
    except Exception as e:
        lane=args[0];dump(OUT/f'{lane}_GPU{args[1]}_ERROR.json',{'error':str(e),'traceback':traceback.format_exc()});traceback.print_exc();raise

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    os.environ['TOKENIZERS_PARALLELISM']='false'
    subprocess.check_call([sys.executable,'-m','pip','install','--quiet','--no-cache-dir',
        'modelscope==1.40.1','transformers==4.57.1','librosa==0.11.0','soundfile==0.13.1','scikit-learn==1.7.2',
        'git+https://github.com/modelscope/FunASR.git@4a84879ae8ca4d2430953b11c49d609217d93988'])
    import pandas as pd,torch,importlib.metadata
    assert torch.cuda.is_available() and torch.cuda.device_count()>=2
    assert PAYLOAD['preflight_verdict']=='PASS'
    for name,spec in PAYLOAD['input_files'].items():
        assert 'PROTECTED' not in name.upper() and 'VALIDATION_VP' not in name.upper()
        raw=gzip.decompress(base64.b64decode(spec['gzip_b64']));assert hashlib.sha256(raw).hexdigest()==spec['sha256']
        (OUT/name).write_bytes(raw)
    dm=pd.read_csv(OUT/'DATA_MANIFEST.csv');dup=pd.read_csv(OUT/'DUPLICATE_GROUPS_FINAL.csv')
    dupmap=dict(zip(dup.Id,dup.duplicate_group));roots=[]
    for p in INPUT.rglob('train.csv'):
        if (p.parent/'train').is_dir() and (p.parent/'test').is_dir():roots.append(p.parent)
    assert len(set(roots))==1,roots
    records=[]
    for r in dm[dm.split=='train'].sort_values('Id').itertuples(index=False):
        p=roots[0]/r.split/r.filename;assert sha(p)==r.file_sha256 and r.sample_rate==16000 and r.channels==1
        records.append({'Id':int(r.Id),'path':str(p),'samples':int(r.samples),'duplicate_group':str(dupmap.get(r.Id,r.Id))})
    assignments=PAYLOAD.get('workers',[{'lane':'A'},{'lane':'B'}])
    dump(OUT/'GPU_EXECUTION_PROVENANCE.json',{'payload_sha':PAYLOAD['config_sha256'],'source_sha':PAYLOAD['source_sha'],
        'gpu_names':[torch.cuda.get_device_name(i) for i in range(2)],'audio_hashes_verified':len(records),
        'packages':{n:importlib.metadata.version(n) for n in ['torch','numpy','pandas','scikit-learn','funasr','transformers','soundfile','modelscope']},
        'protected_validation_read':False,'kaggle_submission_made':False,'parallel_assignments':[{**spec,'GPU':k} for k,spec in enumerate(assignments)]})
    ctx=mp.get_context('spawn');workers=[]
    for gpu,assignment in enumerate(assignments):
        lane=assignment['lane']
        w=ctx.Process(target=safe_worker,args=(lane,gpu,records,PAYLOAD.get('view','VB'),PAYLOAD.get('seed',20260930),PAYLOAD.get('resume_root'),assignment.get('folds'),assignment.get('arms')))
        w.start();workers.append(w)
    for w in workers:w.join()
    dump(OUT/'JOB_EXIT_STATUS.json',{'worker_exitcodes':[w.exitcode for w in workers]})
    dump(OUT/'SHA256_MANIFEST.json',{'files':[{'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='SHA256_MANIFEST.json']})
    assert all(w.exitcode==0 for w in workers),'Inspect exact saved worker traceback; no scientific rescue.'
    print('W1_GPU_EXECUTION=SUCCESS\nPROTECTED_VALIDATION_NOT_ACCESSED=TRUE\nKAGGLE_SUBMISSION_NOT_MADE=TRUE',flush=True)

if __name__=='__main__':main()
