#!/usr/bin/env python3
"""One cached-frame CPU attention-statistics control. No encoder execution."""
from __future__ import annotations
import copy, json, time
from pathlib import Path
import h5py, joblib, numpy as np, pandas as pd, torch
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from defhs_frozen_closure_utils import *
from run_rs_defhs_frozen_closure import RUN,DS,V3,OUT,INPUT,load_contract,SEED

class PoolHead(torch.nn.Module):
    def __init__(self, baseline):
        super().__init__()
        scaler,head=baseline.steps[0][1],baseline.steps[1][1]
        dim=len(scaler.mean_)//2
        self.attention=torch.nn.Parameter(torch.zeros(dim))
        self.head=torch.nn.Linear(dim*2,4)
        self.register_buffer('mean',torch.tensor(scaler.mean_,dtype=torch.float32))
        self.register_buffer('scale',torch.tensor(scaler.scale_,dtype=torch.float32))
        self.register_buffer('att_scale',torch.tensor(np.maximum(scaler.mean_[dim:],1e-3),dtype=torch.float32))
        with torch.no_grad():
            self.head.weight.copy_(torch.tensor(head.coef_,dtype=torch.float32))
            self.head.bias.copy_(torch.tensor(head.intercept_,dtype=torch.float32))

    def forward(self,frames):
        lengths=[len(f) for f in frames]
        x=torch.cat(frames); seg=torch.repeat_interleave(torch.arange(len(frames)),torch.tensor(lengths))
        score=((x-self.mean[:x.shape[1]])/self.att_scale)@self.attention
        maxima=torch.full((len(frames),),-torch.inf).scatter_reduce(0,seg,score,reduce='amax',include_self=True)
        e=torch.exp(score-maxima[seg]); denom=torch.zeros(len(frames)).scatter_add(0,seg,e)
        w=e/denom[seg]
        mu=torch.zeros(len(frames),x.shape[1]).index_add(0,seg,w[:,None]*x)
        # Centered second moment avoids catastrophic cancellation at uniform attention.
        var=torch.zeros_like(mu).index_add(0,seg,w[:,None]*(x-mu[seg])**2)
        pooled=torch.cat([mu,torch.sqrt(torch.clamp(var,min=1e-12))],1)
        return self.head((pooled-self.mean)/self.scale)

def initialize(X,y,tr):
    m=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=5000,random_state=20261001))
    m.fit(X[tr],CLASSES[y[tr]])
    return m,PoolHead(m)

def evaluate(model,frames,indices,y):
    model.eval();logits=[]
    with torch.no_grad():
        for start in range(0,len(indices),32):logits.append(model([frames[i] for i in indices[start:start+32]]))
    z=torch.cat(logits)
    return torch.softmax(z,1).numpy(),float(torch.nn.functional.cross_entropy(z,torch.tensor(y[indices])).item())

def train_epoch(model,frames,tr,y,optimizer):
    model.train();optimizer.zero_grad()
    # Full-training-set gradient accumulated in deterministic chunks for bounded
    # CPU memory. No minibatch LR or topology search.
    for start in range(0,len(tr),32):
        ix=tr[start:start+32]
        logits=model([frames[i] for i in ix])
        loss=torch.nn.functional.cross_entropy(logits,torch.tensor(y[ix]),reduction='sum')/len(tr)
        loss.backward()
    penalty=.5*model.head.weight.square().sum()/len(tr)+.01*model.attention.square().sum()
    penalty.backward();optimizer.step()

def main():
    t=time.monotonic();torch.set_num_threads(2);torch.manual_seed(SEED);torch.use_deterministic_algorithms(True)
    folds,ev,clean,nonret,legacy,prompt=load_contract()
    s4=json.loads((RUN/'STAGE4_RESULTS.json').read_text());parent=s4['prospective_parent']
    assert parent=='emotion2vec_base_L2_LOGREG','No fallback parent is authorized'
    z=np.load(V3/'emotion2vec_base_meanstd.npz');pos={int(v):i for i,v in enumerate(z['Id'])}
    ids=folds['VB'].Id.to_numpy();X=z['X'][[pos[int(i)] for i in ids]].astype('float32')
    with h5py.File(V3/'emotion2vec_base_frames.h5') as h:frames=[torch.tensor(h[str(int(i))][:]) for i in ids]
    # All cached frames reproduce the mean+std feature cache; no encoder pass.
    cached=np.stack([np.concatenate([f.numpy().mean(0),f.numpy().std(0)]) for f in frames])
    assert np.array_equal(cached,X),'Cached pooling parity defect'
    result={};preds={};parent_probs={};systems={};records={}
    with threadpool_limits(limits=2):
        for view,f in folds.items():
            fs=f.fold.to_numpy();y=labels(f.emotion);P=np.zeros((826,4));controls=[];parities=[]
            original=valid_oof(V3/f'OOF_emotion2vec_base_{view}.csv',f,'L2_LOGREG')
            for fold in range(5):
                tr=np.where(fs!=fold)[0];va=np.where(fs==fold)[0];g=(fold+1)%5;pilot=np.where((fs!=fold)&(fs!=g))[0];stop=np.where(fs==g)[0]
                _,m=initialize(X,y,pilot);opt=torch.optim.Adam(m.parameters(),lr=.001)
                _,best=evaluate(m,frames,stop,y);best_epoch=0;wait=0;history=[{'epoch':0,'stopping_ce':best}]
                for epoch in range(1,31):
                    train_epoch(m,frames,pilot,y,opt);_,ce=evaluate(m,frames,stop,y)
                    history.append({'epoch':epoch,'stopping_ce':ce})
                    if ce<best:best=ce;best_epoch=epoch;wait=0
                    else:wait+=1
                    if wait>=5:break
                base,m=initialize(X,y,tr)
                # Serialization recovers the exact existing differentiable parent
                # recipe, not another head experiment or new parent selection.
                pb=base.predict_proba(X[va]);raw=base.decision_function(X[va])
                parity=float(np.max(np.abs(pb-original[va])))
                q0,ce0=evaluate(m,frames,va,y)
                torch_error=float(np.max(np.abs(q0-pb)))
                parities.append({'fold':fold,'sklearn_probability_max_abs':parity,'torch_zero_attention_probability_max_abs':torch_error})
                if parity>1e-4 or torch_error>2e-5:raise RuntimeError(f'Parent/cache parity failure: {parities[-1]}')
                joblib.dump(base,OUT/f'PARENT_{view}_fold{fold}.joblib')
                opt=torch.optim.Adam(m.parameters(),lr=.001)
                for epoch in range(1,best_epoch+1):train_epoch(m,frames,tr,y,opt)
                q,vce=evaluate(m,frames,va,y);_,tce=evaluate(m,frames,tr,y);P[va]=q
                torch.save(m.state_dict(),OUT/f'ATTENTION_STATS_{view}_fold{fold}.pt')
                controls.append({'fold':fold,'stopping_fold':g,'chosen_epoch':best_epoch,'pilot_history':history,'outer_train_ce':tce,'outer_validation_ce':vce,'parent_validation_ce':ce0})
                print(f'POOL {view} fold={fold} epochs={best_epoch} zero_attention_parity={torch_error:.3g}',flush=True)
            save_oof(OUT/f'OOF_ATTENTION_STATS_{view}.csv',f,P)
            eg=valid_oof(OUT/f'OOF_EGEMAPS_{view}.csv',f)
            if 'EGEMAPS_L2_LOGREG' in s4['selected_E0_members']:
                sysq,sysr=choose_probability_blend([P,eg],y,fs,ev,allowed=[(1.,0.),(.75,.25)],equal_weights=[1.,0.])
            else:sysq,sysr=P,{'heldout':report(y,P.argmax(1),fs)}
            save_oof(OUT/f'OOF_ATTENTION_SYSTEM_{view}.csv',f,sysq)
            baseq=valid_oof(OUT/f"OOF_SYSTEM_{s4['selected_E0_id']}_{view}.csv",f)
            result[view]={'standalone':report(y,P.argmax(1),fs),'replacement_system':sysr,'controls':controls,'parent_refit_parity':parities}
            preds[view]=P.argmax(1);parent_probs[view]=original;systems[view]=(sysq.argmax(1),baseq.argmax(1))
            for mask,name in [(None,'full'),(clean,'clean'),(nonret if view=='VA' else clean,'nonretrieval' if view=='VA' else 'clean_entry')]:
                records[f'{view}:{name}:P_ATTENTION-P']=ev.contrast(y,preds[view],original.argmax(1),mask)
                records[f'{view}:{name}:E_ATTENTION-E0']=ev.contrast(y,*systems[view],mask)
    ci=ev.intervals(records)
    y=labels(folds['VB'].emotion);fs=folds['VB'].fold.to_numpy()
    standalone=robust(y,preds['VB'],parent_probs['VB'].argmax(1),fs,ci['VB:full:P_ATTENTION-P'])
    system=robust(y,*systems['VB'],fs,ci['VB:full:E_ATTENTION-E0'])
    promote=standalone['pass'] and system['pass'] and ci['VB:clean:E_ATTENTION-E0']['point']>0 and ci['VA:nonretrieval:E_ATTENTION-E0']['upper']>=0
    dump(RUN/'STAGE6_RESULTS.json',{'prospective_encoder_frozen_before_pooling':parent,'candidate':'single linear temporal attention, weighted mean/std, linear head',
        'results':result,'contrast_registry':list(records),'intervals':ci,'standalone_robust':standalone,'system_robust':system,
        'decision':'PROMOTE_ATTENTION_STATS' if promote else 'KILL_ATTENTION_STATS_KEEP_MEANSTD','wall_seconds':time.monotonic()-t,
        'accelerator_hours':0,'encoder_extraction_repeated':False,'layer_mixture_status':'UNKNOWN_NO_SCAFFOLD_TIME_UNAVAILABILITY_RECORD_NO_LAYER_CACHE',
        'layer_note':'Only final-frame caches exist. No retrospective unsupported claim is made; G2 must fail if the required scalar-mixture control cannot be established under existing authority.'})
    print('STAGE6='+('PROMOTE_ATTENTION_STATS' if promote else 'KILL_ATTENTION_STATS_KEEP_MEANSTD'),flush=True)

if __name__=='__main__':main()
