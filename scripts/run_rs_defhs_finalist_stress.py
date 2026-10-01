#!/usr/bin/env python3
"""Locked finalist VD/Q/retrieval/correlated-allocation diagnostics on CPU."""
from __future__ import annotations
import hashlib,json,time
import joblib,numpy as np,pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from defhs_frozen_closure_utils import *
from run_rs_defhs_frozen_closure import RUN,DS,V3,OUT,INPUT,load_contract
from run_ds_defhs_correlated_allocation_source_stress_patch_001 import partition,beyond,ODDS,MODELS,SEED

def summaries(ev,y,pred,mask):
    b=ev.boots(y,pred,mask)
    return {'n':int(mask.sum()),'classes_present':CLASSES[np.unique(y[mask])].tolist(),
        'macro_f1':f1(y[mask],pred[mask]),'per_class_f1':dict(zip(CLASSES,f1(y[mask],pred[mask],per_class=True))),
        'conditional_dependency_multiplier_ci95':np.quantile(b,[.025,.975]).tolist(),'uncertainty_note':'Tiny strata are uncertain; absent classes do not establish robustness.'}

def retrieval_audit(f,y,ser,dup,legacy):
    fs=f.fold.to_numpy();ids=f.Id.to_numpy();mapg=dict(zip(dup.Id,dup.duplicate_group));out=ser.copy();covered=np.zeros(826,bool)
    for fold in range(5):
        tr=np.where(fs!=fold)[0];va=np.where(fs==fold)[0];unanimous={}
        for gid in sorted(set(mapg.values())):
            vals=[y[i] for i in tr if mapg.get(int(ids[i]))==gid]
            if vals and len(set(vals))==1:unanimous[gid]=vals[0]
        for i in va:
            gid=mapg.get(int(ids[i]))
            if gid in unanimous:out[i]=unanimous[gid];covered[i]=True
    old=legacy[(legacy.model=='FULL_RBF_SVM')&(legacy.validation=='VA')].set_index('Id').loc[ids]
    assert np.array_equal(covered,old.retrieval_covered.to_numpy(bool))
    assert np.array_equal(out[covered],labels(old.pipeline_pred)[covered])
    return out,covered

def get_subgroups(man,prompt,speaker,latent,eg,dup,ret,legacy,ids,y,coverage):
    train=man[man.split.eq('train')];test=man[man.split.eq('test')];dupmap=dict(zip(dup.Id.astype(int),dup.duplicate_group.astype(int)));subs={}
    r128=man.set_index('Id').samples.astype(int)%128;r960=man.set_index('Id').samples.astype(int)%960
    for r in [0,43,86,30,94]:subs[f'quant128_r{r}']=set(r128[r128.eq(r)].index.astype(int))
    for r in [192,606]:subs[f'quant960_r{r}']=set(r960[r960.eq(r)].index.astype(int))
    subs['dtype_int32']=set(man[man.dtype.eq('int32')].Id.astype(int));subs['prompt90_beyond_duplicate']=beyond(prompt,'prompt_sim_0.90',dupmap)
    for d in ['0.25','0.30','0.35']:subs[f'speaker_d{d}_beyond_duplicate']=beyond(speaker,f'agg_d{d}',dupmap)
    for k in sorted(latent.joint_k4.unique()):subs[f'latent_k4_{int(k)}']=set(latent[latent.joint_k4.eq(k)].Id.astype(int))
    q20,q80=train.duration_seconds.quantile([.2,.8]);subs['duration_short20']=set(man[man.duration_seconds<=q20].Id.astype(int));subs['duration_long20']=set(man[man.duration_seconds>=q80].Id.astype(int))
    cols=[c for c in eg if c not in ['Id','split','filename','emotion']];tr=eg[eg.split.eq('train')]
    sc=StandardScaler().fit(tr[cols]);pc=PCA(n_components=.9,svd_solver='full').fit(sc.transform(tr[cols]));dist=np.linalg.norm(pc.transform(sc.transform(eg[cols])),axis=1);threshold=np.quantile(dist[eg.split.eq('train')],.8)
    subs['egemaps_outlier20']=set(eg.loc[dist>=threshold,'Id'].astype(int));subs['retrieval_covered']=set(ids[coverage])|set(ret.test_Id.astype(int))
    va=legacy[legacy.validation.eq('VA')];correct=np.stack([labels(va[va.model.eq(m)].set_index('Id').loc[ids].pipeline_pred)==y for m in MODELS]).sum(0)
    subs['development_difficulty_tail']=set(ids[correct<=1])
    return subs

def envelope(ids,y,pred,subgroups,man):
    train_ids=set(ids);test_ids=set(man.loc[man.split.eq('test'),'Id']);records=[]
    def scenario(name,S,q,level,od,B):
        sm=np.array([i in S for i in ids]);seed=int(hashlib.sha256(f'{name}|{q}|{level}|{SEED}'.encode()).hexdigest()[:8],16);rg=np.random.default_rng(seed)
        scores={m:np.empty(B) for m in pred};preval=np.empty(B)
        for b in range(B):
            private=partition(rg,ids,CLASSES[y],sm,q,od);public=~private;preval[b]=sm[private].mean()
            for m,p in pred.items():scores[m][b]=.4*f1(y[public],p[public])+.6*f1(y[private],p[private])
        others=[m for m in pred if m!='FINALIST'];gap=scores['FINALIST']-np.max(np.stack([scores[m] for m in others]),axis=0)
        bucket='baseline' if level=='baseline' else ('development_difficulty_tail' if name=='development_difficulty_tail' else ('plausible' if level.startswith(('mild','moderate')) else ('strong_tail' if level.startswith('strong') else 'extreme_tail')))
        return {'subgroup':name,'private_fraction':q,'level':level,'odds':None if np.isinf(od) else od,'bucket':bucket,'replicates':B,
            'train_prevalence':len(S&train_ids)/len(ids),'test_prevalence':None if name=='development_difficulty_tail' else len(S&test_ids)/209,
            'pseudo_private_prevalence':float(preval.mean()),'mean_scores':{m:float(s.mean()) for m,s in scores.items()},
            'finalist_minus_best_comparator_mean':float(gap.mean()),'finalist_reversal_frequency':float((gap<0).mean()),'gap_quantiles':np.quantile(gap,[.025,.5,.975]).tolist()}
    for q in [.2,.3,.4,.5]:records.append(scenario('baseline',set(),q,'baseline',1,250))
    for name,S in subgroups.items():
        for q in [.2,.3,.4,.5]:
            for level,od in ODDS.items():records.append(scenario(name,S,q,level,od,75))
    # Boundary check for each risk layer, chosen by the pre-existing envelope
    # procedure. This is replication of the same diagnostic, not model selection.
    boundaries=[]
    for bucket,B in [('plausible',1500),('strong_tail',2000),('extreme_tail',2000)]:
        row=min((r for r in records if r['bucket']==bucket),key=lambda r:r['finalist_minus_best_comparator_mean'])
        boundaries.append(scenario(row['subgroup'],subgroups[row['subgroup']],row['private_fraction'],row['level'],ODDS[row['level']],B))
    plausible=next(r for r in boundaries if r['bucket']=='plausible');extreme=next(r for r in boundaries if r['bucket']=='extreme_tail')
    classification='MATERIALLY_FRAGILE_UNDER_MODEST_CORRELATION' if plausible['finalist_minus_best_comparator_mean']<0 else ('ONLY_FAILS_UNDER_EXTREME_STRESS' if extreme['finalist_minus_best_comparator_mean']<0 else 'ROBUST_UNDER_TESTED_STRESS')
    return {'score':'0.40 public macro-F1 + 0.60 private macro-F1','models':list(pred),'baseline_replicates':250,'broad_screen_replicates':75,
        'broad_scenarios':len(records)-4,'boundaries':boundaries,'classification':classification,'scenarios':records,
        'interpretation':'Diagnostic against accepted cheap reference and parent ablation; no probability assigned to hidden allocation. Rejected candidate systems do not reopen membership.'}

def main():
    t=time.monotonic();folds,ev,clean,nonret,legacy,prompt=load_contract()
    member=json.loads((RUN/'FROZEN_MEMBERSHIP_CLOSURE.json').read_text());assert member['selected_members']==['emotion2vec_base_L2_LOGREG']
    man=pd.read_csv(DS/'DATA_MANIFEST.csv');dup=pd.read_csv(DS/'DUPLICATE_GROUPS_FINAL.csv');ret=pd.read_csv(DS/'RETRIEVAL_MAP_FINAL.csv')
    ids=folds['VB'].Id.to_numpy();dm=man.set_index('Id').loc[ids];y=labels(folds['VB'].emotion);pred={};results={};strata={}
    for v,f in folds.items():
        d=pd.read_csv(OUT/f'FINAL_DECISIONS_{v}.csv');assert np.array_equal(d.Id,ids);pred[v]=labels(d.pred)
        masks={'all':np.ones(826,bool),'CLEAN':clean,'INT16':dm.dtype.eq('int16').to_numpy(),'INT32':dm.dtype.eq('int32').to_numpy()}
        for mod,groups in [(128,[0,43,86,30,94]),(960,[384,192,576,606,926])]:
            rem=dm.samples.to_numpy()%mod
            for r in groups:masks[f'Q{mod}_{r}']=rem==r
            masks[f'Q{mod}_OTHER']=~np.isin(rem,groups)
        strata[v]={name:summaries(ev,y,pred[v],m) for name,m in masks.items()}
        results[v]=report(y,pred[v],f.fold.to_numpy())
    pipe,cov=retrieval_audit(folds['VA'],y,pred['VA'],dup,legacy)
    pipeline={'report':report(y,pipe,folds['VA'].fold.to_numpy()),'coverage_rows':int(cov.sum()),'coverage_fraction':float(cov.mean()),
        'retrieval_accuracy':float(np.mean(pipe[cov]==y[cov])),'nonretrieval':summaries(ev,y,pred['VA'],~cov),'fixed_certified_test_coverage':78,
        'audit':'exact frozen fold-safe unanimity coverage/labels match legacy audit; no new graph or learned gate'}
    pd.DataFrame({'Id':ids,'emotion':CLASSES[y],'ser_pred':CLASSES[pred['VA']],'pipeline_pred':CLASSES[pipe],'retrieval_covered':cov}).to_csv(OUT/'FINALIST_VA_RETRIEVAL_AUDIT.csv',index=False)
    # Reproduce both leave-one-format-out directions using the cached finalist
    # representation and the identical logistic fitting rule.
    z=np.load(V3/'emotion2vec_base_meanstd.npz');ix={int(v):i for i,v in enumerate(z['Id'])};X=z['X'][[ix[int(i)] for i in ids]]
    cross={}
    with threadpool_limits(limits=2):
        for source,target in [('int16','int32'),('int32','int16')]:
            tr=dm.dtype.eq(source).to_numpy();vl=dm.dtype.eq(target).to_numpy();model=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=5000,random_state=20261001))
            model.fit(X[tr],CLASSES[y[tr]]);q=model.predict_proba(X[vl]);p=np.zeros(826,int);p[vl]=q.argmax(1)
            cross[f'{source}_to_{target}']={'training_rows':int(tr.sum()),'validation':summaries(ev,y,p,vl),'diagnostic_only':True}
            joblib.dump(model,OUT/f'VD_{source}_TO_{target}.joblib')
        speaker=pd.read_csv(INPUT/'speaker_embeddings/SPEAKER_CLUSTER_ASSIGNMENTS.csv');latent=pd.read_csv(INPUT/'latent_regimes/LATENT_REGIME_ASSIGNMENTS.csv');eg=pd.read_csv(INPUT/'egemaps/EGEMAPS_FEATURES.csv')
        sub=get_subgroups(man,prompt,speaker,latent,eg,dup,ret,legacy,ids,y,cov)
        comparison={'FINALIST':pipe}
        for name in MODELS:
            comparison[name]=labels(legacy[(legacy.model==name)&(legacy.validation=='VA')].set_index('Id').loc[ids].pipeline_pred)
        env=envelope(ids,y,comparison,sub,man)
    dump(RUN/'STAGE9_STRESS_RESULTS.json',{'membership':member['selected_members'],'VB_primary':results['VB'],'VA_secondary':results['VA'],'VA_retrieval_pipeline':pipeline,
        'VD_Q_subgroup_diagnostics':strata,'VD_cross_format':cross,'correlated_allocation':env,'final_ablation':'single SER member: no dispensable SER member; compare certified retrieval override separately',
        'wall_seconds':time.monotonic()-t,'accelerator_hours':0,'protected_validation_queried':False,'kaggle_submission_made':False,'status':'COMPLETE_PRE_PROTECTED'})
    print(json.dumps({'stage9':'COMPLETE_PRE_PROTECTED','VB':results['VB']['macro_f1'],'VA_SER':results['VA']['macro_f1'],'VA_pipeline':pipeline['report']['macro_f1'],
        'VD':cross,'correlated_classification':env['classification'],'wall_seconds':time.monotonic()-t},indent=2),flush=True)

if __name__=='__main__':main()
