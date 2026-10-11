#!/usr/bin/env python3
"""Authenticate D, inventory residuals, test ONE registered nested coordinate change."""
import argparse, hashlib, json, time, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss, roc_auc_score
from threadpoolctl import threadpool_limits
from sklearn.exceptions import ConvergenceWarning
import final_semantic_challenger as fs
from defhs_frozen_closure_utils import Evidence, labels

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/RS-DEFHS-FINAL-BREAKTHROUGH-001'
DS=ROOT/'runs/DS-DEFHS-VALIDATION-HARDENING-002'
INPUT=ROOT/'work/system_d_delivery'
PRIOR=ROOT/'work/prior'
L=fs.CLASSES

def load():
    f,X,wave,q8=fs.load_inputs(INPUT)
    d=pd.read_csv(INPUT/'defhs_prod_run/old_evidence/CHALLENGER_PRIMARY_OOF.csv')
    assert fs.sha(INPUT/'defhs_prod_run/old_evidence/CHALLENGER_PRIMARY_OOF.csv')=='7548b8831654efecc4b030d1f1a8a48d1139da388a96bffa3363954cd8643590'
    assert np.array_equal(f.Id,d.Id) and np.array_equal(f.emotion,d.emotion) and np.array_equal(f.fold,d.fold)
    q14=pd.read_csv(INPUT/'DEFHS_Qwen14B_train826_outputs/final_semantic_train826/QWEN14B_TRAIN826.csv').set_index('Id').loc[f.Id].semantic_label.to_numpy()
    assert np.array_equal(q14,d.qwen14b) and np.array_equal(q8,d.qwen8b)
    p=d[['challenger_p_'+c for c in L]].to_numpy()
    assert np.isfinite(p).all() and np.allclose(p.sum(1),1) and np.array_equal(L[p.argmax(1)],d.challenger_pred)
    assert abs(fs.mf(f.emotion,d.challenger_pred)-.8396460575108101)<1e-14
    return f,X,wave,q8,q14,d,p

def get_evidence(ids):
    path=PRIOR/'PROMPT_CLUSTER_ASSIGNMENTS.csv'
    assert fs.sha(path)=='458712cfee51e0cf65ef57d1a0deb8f81dcb70e4ecfe6ebfc73220f3aefac005'
    return Evidence(ids,pd.read_csv(DS/'DUPLICATE_GROUPS_FINAL.csv'),pd.read_csv(path))

def compare(y,d,p,fold,ev):
    c=L[p.argmax(1)];r=fs.comparison(y,d,c,fold)
    delta=ev.boots(labels(y),labels(c))-ev.boots(labels(y),labels(d))
    r['component_bootstrap_ci95']=np.quantile(delta,[.025,.975]).tolist()
    r['component_count']=len(set(ev.components))
    r['delete_fold_delta']=[fs.mf(y[fold!=k],c[fold!=k])-fs.mf(y[fold!=k],d[fold!=k]) for k in range(5)]
    return r

def residual():
    f,X,w,q8,q14,old,p=load();y=f.emotion.to_numpy();d=old.challenger_pred.to_numpy();fold=f.fold.to_numpy();ids=f.Id.to_numpy()
    ev=get_evidence(ids);hard=fs.hard_mask(w);e=L[w[:,:4].argmax(1)];x=L[w[:,4:].argmax(1)]
    asr=pd.read_csv(INPUT/'ASR_TRANSCRIPTS.csv').set_index('Id').loc[ids]
    man=pd.read_csv(DS/'DATA_MANIFEST.csv').set_index('Id').loc[ids]
    prompt=pd.read_csv(PRIOR/'PROMPT_CLUSTER_ASSIGNMENTS.csv').set_index('Id').loc[ids]
    row=f.copy();row['system_d_pred']=d;row['error']=d!=y;row['hard']=hard;row['component']=ev.components
    for i,c in enumerate(L):row['system_d_p_'+c]=p[:,i]
    row['true_rank']=(np.argsort(-p,axis=1)==labels(y)[:,None]).argmax(1)+1
    for c in ['dtype','duration_seconds','samples']:row[c]=man[c].to_numpy()
    for c in ['transcript','normalized_transcript','avg_logprob','no_speech_prob','compression_ratio']:row[c]=asr[c].to_numpy()
    row['prompt_component']=prompt['prompt_sim_0.90'].to_numpy()
    experts={'e2v':e,'xlsr':x,'fixed_pair':L[((w[:,:4]+w[:,4:])/2).argmax(1)],'qwen8':q8,'qwen14':q14,'system_c':old.system_c_pred.to_numpy()}
    provenance={};rec={}
    for path in sorted((ROOT/'runs/RS-DEFHS-SCORE-PUSH-001').glob('*_VB.csv')):
        a=pd.read_csv(path).sort_values('Id');assert np.array_equal(a.Id,ids) and np.array_equal(a.emotion,y) and np.array_equal(a.fold,fold)
        experts[path.stem]=a.pred.to_numpy();provenance[path.stem]={'path':str(path.relative_to(ROOT)),'sha256':fs.sha(path),'scope':'historical OOF; diagnostic only, never used to fit a stack'}
    pocket=ROOT/'runs/RS-DEFHS-POCKET-MIMI-REPRESENTATION-001/train826/POCKET_MIMI_OOF_PRIMARY_CV.csv'
    a=pd.read_csv(pocket).sort_values('Id');assert np.array_equal(a.Id,ids) and np.array_equal(a.fold,fold) and np.array_equal(a.emotion,y)
    experts['pocket_mimi']=a.pred.to_numpy();provenance['pocket_mimi']={'sha256':fs.sha(pocket)}
    inv=json.loads((ROOT/'runs/RS-DEFHS-SYSTEM3-WAVE1-001/PROBABILITY_ARTIFACT_INVENTORY.json').read_text())['artifacts']
    for path in sorted(PRIOR.glob('*.npz')):
        entry=next(v for v in inv if v['name']==path.name);assert fs.sha(path)==entry['sha256'],path
        z=np.load(path,allow_pickle=False);assert np.array_equal(z['Id'],ids)
        prob=z['prob'];assert np.isfinite(prob).all() and np.allclose(prob.sum(1),1,atol=1e-6)
        experts[path.stem]=L[prob.argmax(1)];provenance[path.stem]=entry
    for name,a in experts.items():
        row[name]=a;t=fs.transition(y,d,a);t['oracle_correct_ids']=ids[(d!=y)&(a==y)].tolist();t['false_override_ids']=ids[(d==y)&(a!=y)].tolist()
        t['metrics']=fs.metric(y,a,fold);t['correct_by_fold']=[int(np.sum((d!=y)&(a==y)&(fold==k))) for k in range(5)]
        t['incorrect_replacements_per_available_correction']=t['breakages']/max(t['corrections'],1)
        rec[name]=t
    current=np.column_stack([e,x,q8,q14]);none=np.all(current!=y[:,None],axis=1)
    row['all_four_current_experts_wrong']=none
    masks={'all':np.ones(len(y),bool),'HARD316':hard,'waveform_disagree':e!=x,'waveform_agree':e==x,'int16':man.dtype.eq('int16').to_numpy(),'int32':man.dtype.eq('int32').to_numpy(),'qwen14_unclear':q14=='unclear','qwen14_covered':q14!='unclear','semantic_agree':q8==q14,'all_four_experts_wrong':none,'avglogprob_below_neg1':asr.avg_logprob.to_numpy()<-1,'repeated_prompt':prompt['prompt_sim_0.90'].map(prompt['prompt_sim_0.90'].value_counts()).to_numpy()>1,'repeated_duplicate':f.duplicate_group.map(f.duplicate_group.value_counts()).to_numpy()>1}
    masks['prompt_singleton']=~masks['repeated_prompt'];masks['duplicate_singleton']=~masks['repeated_duplicate']
    for mod,values in [(128,[0,43,86,30,94]),(960,[384,192,576,606,926])]:
        remainder=man.samples.to_numpy()%mod
        for v in values:masks[f'Q{mod}_{v}']=remainder==v
        masks[f'Q{mod}_OTHER']=~np.isin(remainder,values)
    for name,m in masks.items():row['cohort_'+name]=m
    subgroup={k:{'n':int(m.sum()),'errors':int(np.sum((d!=y)&m)),'metrics':fs.metric(y[m],d[m])} for k,m in masks.items()}
    cm=fs.metric(y,d,fold)
    joint=np.column_stack(list(experts.values()))
    r={'authority':'69ebbe3ca3c65f82e546fdf1d42e90fa885c8634','system_d':cm,'residual_count':int(np.sum(d!=y)),
       'expert_complementarity':rec,'cohorts':subgroup,'true_rank_on_errors':{str(k):int(np.sum((d!=y)&(row.true_rank==k))) for k in range(1,5)},
       'current_expert_oracle_residual_corrections':int(np.sum((d!=y)&~none)),
       'all_historical_expert_union_oracle_residual_corrections':int(np.sum((d!=y)&np.any(joint==y[:,None],axis=1))),
       'asr_negative_logprob_error_auc':float(roc_auc_score(d!=y,-asr.avg_logprob.to_numpy())),
       'asr_quality_caution':'ASR confidence/garbled-looking strings are not reference-transcript WER or proof of causality.',
       'dependency_components':len(set(ev.components)),'error_components':len(set(ev.components[d!=y])),
       'oracle_warning':'Oracle complementarity is not deployable gain. No historical OOF probabilities fit any new routing model.',
       'provenance':provenance}
    row.to_csv(OUT/'SYSTEM_D_RESIDUAL_AUDIT_826.csv',index=False,float_format='%.17g')
    row[row.error].to_csv(OUT/'SYSTEM_D_ERRORS_133.csv',index=False,float_format='%.17g')
    fs.dump(OUT/'RESIDUAL_RESULTS.json',r)
    print(json.dumps({k:r[k] for k in ['residual_count','current_expert_oracle_residual_corrections','all_historical_expert_union_oracle_residual_corrections','asr_negative_logprob_error_auc','dependency_components','error_components']}))
    print('EXPERTS',[(k,v['corrections'],v['breakages'],v['metrics']['macro_f1']) for k,v in rec.items()])

def clr(w):
    blocks=[]
    for start in [0,4]:
        z=np.log(np.clip(w[:,start:start+4],1e-6,1));blocks.append(z-z.mean(1,keepdims=True))
    return np.column_stack(blocks)

def cpu():
    assert not (OUT/'CPU_RESULT.json').exists(),'One evaluation; preserve prior result'
    start=time.monotonic();f,X,w,q8,q14,old,pd_old=load();fold=f.fold.to_numpy();y=f.emotion.to_numpy();d=old.challenger_pred.to_numpy()
    warnings.simplefilter('error',ConvergenceWarning)
    with threadpool_limits(2):
        cache=ROOT/'work/breakthrough_cache';a=fs.build_inner(f,X,w,cache,'VB')
        semantic=np.column_stack([fs.onehot(q8),fs.onehot(q14)])
        pd_replay=fs.fuse(f,a,semantic)
        assert np.max(abs(pd_replay-pd_old))<1e-10 and np.array_equal(L[pd_replay.argmax(1)],d)
        transformed={k:(clr(v) if k.startswith(('inner_','outer_')) else v) for k,v in a.items()}
        p=fs.fuse(f,transformed,semantic)
    r=compare(y,d,p,fold,get_evidence(f.Id));hard=fs.hard_mask(w);pred=L[p.argmax(1)]
    hard_delta=fs.mf(y[hard],pred[hard])-fs.mf(y[hard],d[hard])
    class_delta=[r['challenger']['per_class'][c]['f1']-r['C']['per_class'][c]['f1'] for c in L]
    gates={'pooled_gain_ge_005':r['delta']>=.005,'at_least_four_positive_folds':sum(v>0 for v in r['fold_deltas'])>=4,'no_class_loss_over_02':min(class_delta)>=-.02,'hard_nonnegative':hard_delta>=0,'component_ci_lower_positive':r['component_bootstrap_ci95'][0]>0,'all_delete_fold_positive':min(r['delete_fold_delta'])>0}
    r.update({'experiment':'CPU_CLR18_V1','incumbent_name':'System D','candidate_name':'CLR18','gates':gates,'status':'PRIMARY_PASS_PENDING_STRESS' if all(gates.values()) else 'REJECT',
      'hard_delta':hard_delta,'per_class_delta':dict(zip(L,class_delta)),'D_probability_replay_max_abs':float(np.max(abs(pd_replay-pd_old))),
      'wall_seconds':time.monotonic()-start,'gpu_hours':0,'nested_base_fits':50,'meta_fits':10,
      'nll_D':float(log_loss(y,pd_old,labels=L)),'nll_challenger':float(log_loss(y,p,labels=L)),
      'corrected_ids':f.Id[(d!=y)&(pred==y)].tolist(),'broken_ids':f.Id[(d==y)&(pred!=y)].tolist(),
      'protocol_sha256':fs.sha(OUT/'CPU_PROTOCOL.md'),'protected_validation_accessed':False,'target_candidate_generated':False})
    out=f[['Id','emotion','fold']].copy();out['system_d_pred']=d;out['challenger_pred']=pred
    for j,c in enumerate(L):out['p_'+c]=p[:,j]
    out.to_csv(OUT/'CPU_CLR18_OOF.csv',index=False,float_format='%.17g');fs.dump(OUT/'CPU_RESULT.json',r)
    print(json.dumps(r,indent=2))

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['residual','cpu']);args=ap.parse_args()
    {'residual':residual,'cpu':cpu}[args.stage]()
