#!/usr/bin/env python3
"""Registered Wave 1 authority checks and genuinely nested two-expert fusion."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, time, warnings
from pathlib import Path
import numpy as np, pandas as pd, joblib
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits
from defhs_frozen_closure_utils import CLASSES, labels, f1, report, dump, sha256, valid_oof
from run_score_push_cpu import contract, views

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'runs/RS-DEFHS-SYSTEM3-WAVE1-001'
DS=ROOT/'runs/DS-DEFHS-VALIDATION-HARDENING-002'
V3=ROOT/'.tmp/rs_system_implementation_001_frozen_screen_v3/rs_defhs_system_implementation_001'
WORK=ROOT/'work/system3_wave1'
PARENT='d78da6037ec1b73bf210f562baa30ebb1b9fa9e6'
EXPECTED={'DATA_MANIFEST.csv':'1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469',
 'DUPLICATE_GROUPS_FINAL.csv':'6aee3374e27efeb1a79397a1256a515b87e3baf4d7a01536191f6e16256e81f7',
 'VALIDATION_VB_FOLDS.csv':'87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b',
 'VALIDATION_VA_FOLDS.csv':'dcee356b0a66cb73c506bb71a6c57962227d6d0474efd3e4d6c404168308f3d1',
 'VALIDATION_VD_REGIMES.csv':'f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839',
 'RETRIEVAL_MAP_FINAL.csv':'e08f7d06c13d64a1d365d7ae6fa741d6e831dea8816de6663d4a9c0eb113d2a7'}

def source(): return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def idhash(ids): return hashlib.sha256((''.join(f'{int(i)}\n' for i in ids)).encode()).hexdigest()
def read(p):
    assert 'PROTECTED' not in str(p).upper() and 'VALIDATION_VP' not in str(p).upper()
    return pd.read_csv(p)
def inputs():
    folds,ev,masks,control=contract()
    man=read(DS/'DATA_MANIFEST.csv').set_index('Id').loc[folds['VB'].Id]
    for v in masks:
        for modulus,residues in [(128,[0,43,86,30,94]),(960,[384,192,576,606,926])]:
            rem=man.samples.to_numpy()%modulus
            for residue in residues:masks[v][f'Q{modulus}_{residue}']=rem==residue
            masks[v][f'Q{modulus}_OTHER']=~np.isin(rem,residues)
    x={}
    for name in ['emotion2vec_base','xls_r_300m']:
        z=np.load(V3/f'{name}_meanstd.npz');ix={int(i):k for k,i in enumerate(z['Id'])}
        x[name]=z['X'][[ix[int(i)] for i in folds['VB'].Id]]
    return folds,masks,control,x

def preflight():
    RUN.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='rs/system3-wave1-001'
    remote=subprocess.check_output(['git','rev-parse','origin/rs/score-push-001'],cwd=ROOT,text=True).strip();assert remote==PARENT
    files={}
    for n,h in EXPECTED.items():
        actual=sha256(DS/n);assert actual==h,(n,actual,h)
        files[n]={'path':str(DS/n),'sha256':actual}
    inv=json.loads((V3/'OUTPUT_INVENTORY.json').read_text())
    registered={r['name']:r['sha256'] for r in inv['files']}
    for n,h in [('emotion2vec_base_meanstd.npz','4b8b6feeedc83ca2712b7fd21d9683465a07f7fcb82ca0c1d625512acf64326f'),
                ('xls_r_300m_meanstd.npz',registered['xls_r_300m_meanstd.npz'])]:
        assert sha256(V3/n)==h;files[n]={'path':str(V3/n),'sha256':h}
    baseline=ROOT/'work/frozen_closure/LOCKED_FINALIST_ALL826_LOGISTIC.joblib'
    assert sha256(baseline)=='787d8da0cd2a54ea405ec319f74fb762e0336e6fdb2d9fa972a3ab4a7e774a87'
    files[baseline.name]={'path':str(baseline),'sha256':sha256(baseline)}
    dm=read(DS/'DATA_MANIFEST.csv');tr=dm[dm.split=='train'];te=dm[dm.split=='test']
    assert len(tr)==826 and len(te)==209 and dm.Id.is_unique and dm.Id.is_monotonic_increasing
    assert tr.emotion.value_counts().to_dict()=={'neutral':217,'sad':212,'angry':205,'happy':192}
    assert set(tr.emotion)==set(CLASSES)
    ret=read(DS/'RETRIEVAL_MAP_FINAL.csv');assert len(ret)==78 and ret.test_Id.is_unique and ret.duplicate_group.nunique()==77
    assert not ret.conflict.astype(bool).any() and set(ret.test_Id)<=set(te.Id)
    folds,masks,control,x=inputs()
    for name in x:
        z=np.load(V3/f'{name}_meanstd.npz');assert np.array_equal(z['Id'],dm.Id) and np.isfinite(z['X']).all()
    assert x['emotion2vec_base'].shape==(826,1536) and x['xls_r_300m'].shape==(826,2048)
    for v,f in folds.items():
        assert np.array_equal(f.Id,tr.Id) and np.array_equal(f.emotion,tr.emotion)
    assert folds['VB'].groupby('duplicate_group').fold.nunique().max()==1
    # Verify ordinary replay without touching protected artifacts.
    historical={v:valid_oof(V3/f'OOF_xls_r_300m_{v}.csv',f,'L2_LOGREG') for v,f in folds.items()}
    historical_pair={v:(control[v]+historical[v])/2 for v in folds}
    for v,expected in [('VB',.7768156647359765),('VA',.8266398472107417)]:
        assert abs(f1(labels(folds[v].emotion),historical_pair[v].argmax(1))-expected)<1e-14
    # The package has a narrow input allowlist; no repository/archive upload.
    for name in ['ASR_TRANSCRIPTS.csv','PROMPT_CLUSTER_ASSIGNMENTS.csv']:
        p=ROOT/'work/mission_inputs/asr_transcripts'/name;files[name]={'path':str(p),'sha256':sha256(p),'role':'existing diagnostic masks only'}
    rec={'status':'PASS','mission_id':'RS-DEFHS-SYSTEM3-WAVE1-001','execution_parent':PARENT,'source_sha':source(),
         'inputs':files,'train_rows':826,'test_rows':209,'class_supports':dict(zip(CLASSES,[205,192,217,212])),
         'retrieval_test_rows':78,'retrieval_groups':77,'cache_ID_order':'EXACT_MANIFEST_PARITY',
         'protected_file_read':False,'preprocessing_label_leakage':False,'historical_replay_only':True,
         'public_evidence':{'system1':.79691,'system2':.78593,'system2_verdict':'PUBLIC_TRANSFER_NEGATIVE','private_score':'UNKNOWN'},
         'GPU_launch_required_next':True}
    dump(RUN/'W1_PREFLIGHT.json',rec);print(json.dumps(rec,indent=2))

def fit(x,y,tr,vl):
    assert not np.any(tr&vl)
    m=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=5000,random_state=20261001))
    m.fit(x[tr],y[tr]);assert np.array_equal(m.classes_,CLASSES);assert m[0].n_samples_seen_==tr.sum()
    return m,m.predict_proba(x[vl])
def temperature(p,T):
    lp=np.log(np.clip(p,1e-15,1))/T;return np.exp(lp-logsumexp(lp,axis=1,keepdims=True))
def nll(y,p):return float(-np.log(np.clip(p[np.arange(len(y)),y],1e-15,1)).mean())
def cpu():
    assert json.loads((RUN/'W1_PREFLIGHT.json').read_text())['status']=='PASS'
    assert not (RUN/'W1_NESTED_FUSION_RESULTS.json').exists(),'Reuse completed evidence.'
    warnings.simplefilter('error',ConvergenceWarning)
    folds,masks,control,x=inputs();start=time.monotonic();pairs={};fusions={};heads={};audit={}
    historical={v:valid_oof(V3/f'OOF_xls_r_300m_{v}.csv',f,'L2_LOGREG') for v,f in folds.items()}
    replay={v:(control[v]+historical[v])/2 for v in folds}
    with threadpool_limits(limits=2):
        for v,f in folds.items():
            fs=f.fold.to_numpy();ys=f.emotion.to_numpy();y=labels(ys);ids=f.Id.to_numpy()
            heads[v]={n:np.zeros((826,4)) for n in x};fusions[v]=np.zeros((826,4));audit[v]=[]
            for outer in range(5):
                S=fs!=outer;H=~S;inner={n:np.zeros((S.sum(),4)) for n in x};inner_audit=[]
                for h in sorted(set(fs[S])):
                    train=S&(fs!=h);valid=S&(fs==h)
                    assert not np.any((train|valid)&H)
                    inner_audit.append({'inner_block':int(h),'training_ID_sha256':idhash(ids[train]),
                        'prediction_ID_sha256':idhash(ids[valid]),'outer_heldout_used':False})
                    for n in x:inner[n][valid[S]]=fit(x[n],ys,train,valid)[1]
                Ts={};cal={}
                for n in x:
                    opt=minimize_scalar(lambda t:nll(y[S],temperature(inner[n],t)),bounds=(.5,5),method='bounded',options={'xatol':1e-9})
                    assert opt.success;Ts[n]=float(opt.x);cal[n]=temperature(inner[n],opt.x)
                a,b=list(x)
                opt=minimize_scalar(lambda w:nll(y[S],w*cal[a]+(1-w)*cal[b])+.1*2*(w-.5)**2,
                    bounds=(0,1),method='bounded',options={'xatol':1e-9});assert opt.success
                w=float(opt.x);ps={}
                for n in x:
                    m,p=fit(x[n],ys,S,H);heads[v][n][H]=p;ps[n]=temperature(p,Ts[n])
                    joblib.dump(m,WORK/f'{n}_{v}_outer{outer}.joblib')
                fusions[v][H]=w*ps[a]+(1-w)*ps[b]
                audit[v].append({'outer_fold':outer,'training_ID_sha256':idhash(ids[S]),'prediction_ID_sha256':idhash(ids[H]),
                    'inner_splits':inner_audit,'temperatures':Ts,'weights':[w,1-w],'weight_objective':float(opt.fun),
                    'outer_heldout_used_for_meta_training':False})
                print(f'NESTED_CPU_DONE={v} fold{outer}',flush=True)
            pairs[v]=(heads[v]['emotion2vec_base']+heads[v]['xls_r_300m'])/2
    for v in folds:
        assert np.array_equal(heads[v]['emotion2vec_base'].argmax(1),control[v].argmax(1))
        assert np.array_equal(heads[v]['xls_r_300m'].argmax(1),historical[v].argmax(1))
        assert np.array_equal(pairs[v].argmax(1),replay[v].argmax(1))
    def record(p,ref):
        out=views(p,folds,masks,ref)
        for v,f in folds.items():
            y=labels(f.emotion);q=p[v].argmax(1);b=ref[v].argmax(1);fs=f.fold.to_numpy()
            out[v]['corrections']=int(((q==y)&(b!=y)).sum());out[v]['breakages']=int(((q!=y)&(b==y)).sum())
            out[v]['fold_deltas']=[f1(y[fs==k],q[fs==k])-f1(y[fs==k],b[fs==k]) for k in range(5)]
            out[v]['delete_fold_deltas']=[f1(y[fs!=k],q[fs!=k])-f1(y[fs!=k],b[fs!=k]) for k in range(5)]
        return out
    pair=record(pairs,control);fusion=record(fusions,pairs)
    comp={}
    for v in folds:
        a=heads[v]['emotion2vec_base'];b=heads[v]['xls_r_300m'];y=labels(folds[v].emotion)
        ea=a.argmax(1)!=y;eb=b.argmax(1)!=y
        comp[v]={'probability_correlation':float(np.corrcoef(a.ravel(),b.ravel())[0,1]),
          'log_probability_correlation':float(np.corrcoef(np.log(a.clip(1e-15)).ravel(),np.log(b.clip(1e-15)).ravel())[0,1]),
          'hard_error_correlation':float(np.corrcoef(ea,eb)[0,1]),'disagreement':float((a.argmax(1)!=b.argmax(1)).mean()),
          'both_wrong':int((ea&eb).sum()),'e2v_only_wrong':int((ea&~eb).sum()),'xlsr_only_wrong':int((~ea&eb).sum())}
    inventory=[]
    for v,f in folds.items():
        for n,p in [('E2V_CONTROL',heads[v]['emotion2vec_base']),('XLSR',heads[v]['xls_r_300m']),('FIXED_PAIR',pairs[v]),('NESTED_FUSION',fusions[v])]:
            path=WORK/f'{n}_{v}.npz';np.savez_compressed(path,Id=f.Id.to_numpy(),prob=p)
            inventory.append({'name':path.name,'local_path':str(path),'sha256':sha256(path),'bytes':path.stat().st_size})
    common={'source_sha':source(),'input_authority':EXPECTED,'compute':'CPU, two BLAS threads','wall_seconds':time.monotonic()-start,
            'protected_validation_read':False,'kaggle_submission_made':False}
    dump(RUN/'W1_CPU_PAIR_RESULTS.json',{**common,'HISTORICAL_REPLAY':views(replay,folds,masks,control),
        'independent_evidence':False,'outer_refit':pair,'hard_prediction_historical_parity':True,'complementarity':comp,
        'control':views(control,folds,masks,control)})
    main=fusion['VB'];promote=main['macro_f1']-pair['VB']['macro_f1']>=.005 and sum(d>0 for d in main['fold_deltas'])>=4 and min(main['delete_fold_deltas'])>=0
    promote=promote and fusion['VB']['strata']['CLEAN']['delta_vs_control']>=0 and fusion['VA']['strata']['nonretrieval']['delta_vs_control']>=0
    dump(RUN/'W1_NESTED_FUSION_RESULTS.json',{**common,'results_vs_fixed_pair':fusion,'outer_meta_audit':audit,
        'promotion_conventions_pass':bool(promote),'selection':'NESTED_FUSION' if promote else 'FIXED_50_50',
        'independence_limit':'Same reused ordinary authority; fitted components are legal train-side nested predictions'})
    dump(RUN/'PROBABILITY_ARTIFACT_INVENTORY.json',{'artifacts':inventory,'heavy_root':'gdrive:DEFHS/rs_system3_wave1_001','status':'LOCAL_PENDING_PRESERVATION'})
    print(json.dumps({'fixed_pair':{v:pair[v]['macro_f1'] for v in folds},'nested':{v:fusion[v]['macro_f1'] for v in folds},'nested_promoted':bool(promote)},indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('stage',choices=['preflight','cpu']);ns=a.parse_args()
    (preflight if ns.stage=='preflight' else cpu)()
