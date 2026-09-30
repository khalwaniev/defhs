#!/usr/bin/env python3
"""Reproduce PATCH-001 quantization and correlated-allocation diagnostics.

Uses only explicitly supplied non-protected artifacts. Any input path containing
VP_PROTECTED is rejected before file reads.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, nchypergeom_fisher
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

SEED=20261001
CLASSES=['angry','happy','neutral','sad']
MODELS=['BASIC_EXTRATREES','BASIC_LOGREG','FULL_LOGREG','FULL_RBF_SVM']
MODULI=[16,32,64,80,128,160,200,256,320,400,480,512,640,800,960,1024]
ODDS={'mild_depletion':2/3,'moderate_depletion':.5,'strong_depletion':.25,
      'extreme_depletion':0.,'mild_enrichment':1.5,'moderate_enrichment':2.,
      'strong_enrichment':4.,'extreme_enrichment':float('inf')}


def args():
    p=argparse.ArgumentParser()
    for k in ['manifest','duplicate_groups','oof','prompt','speaker','latent','egemaps','retrieval']:
        p.add_argument('--'+k.replace('_','-'),dest=k,type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--maxstat-permutations',type=int,default=5000)
    p.add_argument('--conditional-permutations',type=int,default=2000)
    p.add_argument('--rank-bootstrap',type=int,default=3000)
    p.add_argument('--envelope-replicates',type=int,default=250)
    return p.parse_args()


def cramers(cat,y):
    ct=pd.crosstab(pd.Series(cat),pd.Series(y)); chi,p,_,_=chi2_contingency(ct,correction=False)
    return float(chi),float(p),math.sqrt(chi/(len(y)*(min(ct.shape)-1)))


def macro(y,p):
    cm=np.zeros((4,4),int); m={c:i for i,c in enumerate(CLASSES)}
    np.add.at(cm,([m[x] for x in y],[m[x] for x in p]),1)
    tp=np.diag(cm); d=cm.sum(0)+cm.sum(1)
    return float(np.divide(2*tp,d,out=np.zeros(4,float),where=d>0).mean())


def maxstat_v(cats,y,rng,B):
    obs={m:cramers(c,y)[2] for m,c in cats.items()}; null=np.empty(B)
    for b in range(B):
        yp=rng.permutation(y); null[b]=max(cramers(c,yp)[2] for c in cats.values())
    return obs,null


def fixed_categories(man,df,m):
    top=(man.samples.astype(int)%m).value_counts().head(5).index.astype(int).tolist()
    r=df.samples.astype(int)%m
    return top,np.where(r.isin(top),r.astype(str),'OTHER')


def dep_dedup(train,dup):
    d=dup[dup.split.eq('train')][['Id','duplicate_group','train_label_conflict']]
    z=train.merge(d,on='Id',how='left')
    z['dep']=np.where(z.duplicate_group.notna(),'d'+z.duplicate_group.fillna(-1).astype(int).astype(str),'s'+z.Id.astype(str))
    bad=set(d[d.train_label_conflict.astype(str).str.lower().eq('true')].duplicate_group)
    out=[]
    for _,g in z.groupby('dep'):
        if g.duplicate_group.notna().any() and g.duplicate_group.dropna().iloc[0] in bad: continue
        if g.emotion.nunique()==1: out.append(g.sort_values('Id').iloc[0])
    return pd.DataFrame(out).reset_index(drop=True)


def conditional_family(man,df,width,B,seed):
    cats={m:fixed_categories(man,df,m)[1] for m in MODULI}; y=df.emotion.to_numpy()
    obs={m:cramers(c,y)[2] for m,c in cats.items()}
    key=(np.floor(df.duration_seconds/width).astype(int).astype(str)+'|'+df.dtype.astype(str)+'|'+
         pd.cut(df.Id,[-1,259,518,777,10**9],labels=False).astype(str))
    groups=[np.where(key.to_numpy()==k)[0] for k in key.unique()]
    rg=np.random.default_rng(seed); mx=np.empty(B); n128=np.empty(B)
    for b in range(B):
        yp=y.copy()
        for ix in groups:
            if len(ix)>1: yp[ix]=yp[ix][rg.permutation(len(ix))]
        vals={m:cramers(c,yp)[2] for m,c in cats.items()}; mx[b]=max(vals.values()); n128[b]=vals[128]
    best=max(obs,key=obs.get)
    return {'n':len(df),'duration_bin_seconds':width,'n_strata':len(groups),
            'remainder128_v':obs[128],
            'remainder128_familywise_p':(int((mx>=obs[128]).sum())+1)/(B+1),
            'family_max_modulus':best,'family_max_v':obs[best],
            'family_max_fwer_p':(int((mx>=obs[best]).sum())+1)/(B+1)}


def rank_boot(vb,train,mod,rems,B):
    z=train[['Id','emotion','samples']].copy(); r=z.samples.astype(int)%mod
    z['stratum']=np.where(r.isin(rems),r.astype(str),'OTHER'); z=vb.merge(z[['Id','emotion','stratum']],on=['Id','emotion'])
    rg=np.random.default_rng(SEED+mod); rows=[]
    for s,g in z.groupby('stratum'):
        ids=np.sort(g.Id.unique()); yy=g.drop_duplicates('Id').set_index('Id').loc[ids].emotion.to_numpy()
        pp={m:g[g.model.eq(m)].set_index('Id').loc[ids].ser_pred.to_numpy() for m in MODELS}
        point={m:macro(yy,pp[m]) for m in MODELS}; boots={m:np.empty(B) for m in MODELS}; tops={m:0. for m in MODELS}
        for b in range(B):
            ix=rg.integers(0,len(ids),len(ids)); sc={m:macro(yy[ix],pp[m][ix]) for m in MODELS}; win=max(sc.values())
            for m in MODELS: boots[m][b]=sc[m]; tops[m]+=abs(sc[m]-win)<1e-12
        winner=max(point,key=point.get); rec={'modulus':mod,'stratum':s,'n':len(ids),'point_winner':winner,'point_winner_gap_vs_rbf':point[winner]-point['FULL_RBF_SVM']}
        for m in MODELS:
            rec[f'{m}_f1']=point[m]; rec[f'{m}_ci_lo']=float(np.quantile(boots[m],.025)); rec[f'{m}_ci_hi']=float(np.quantile(boots[m],.975)); rec[f'{m}_p_top']=tops[m]/B
        if winner!='FULL_RBF_SVM': rec['p_point_winner_gt_rbf']=float(np.mean(boots[winner]>boots['FULL_RBF_SVM']))
        rows.append(rec)
    return rows


def beyond(df,col,dupmap):
    out=set()
    for _,g in df.groupby(col):
        if len(g)<2: continue
        tok={('d',dupmap[i]) if i in dupmap else ('s',i) for i in g.Id.astype(int)}
        if len(tok)>1: out.update(g.Id.astype(int))
    return out


def partition(rg,ids,y,sub,q,odds):
    priv=np.zeros(len(ids),bool)
    for cls in CLASSES:
        ix=np.where(y==cls)[0]; k=min(max(int(round(q*len(ix))),1),len(ix)-1); mark=sub[ix]
        M=len(ix); K=int(mark.sum())
        if odds==float('inf'): x=min(k,K)
        elif odds==0: x=max(0,k-(M-K))
        else: x=int(nchypergeom_fisher.rvs(M,K,k,odds,random_state=rg))
        aa=ix[mark]; bb=ix[~mark]; pick=[]
        if x: pick.extend(rg.choice(aa,x,replace=False))
        if k-x: pick.extend(rg.choice(bb,k-x,replace=False))
        priv[np.asarray(pick,int)]=True
    return priv


def main():
    a=args(); paths=[a.manifest,a.duplicate_groups,a.oof,a.prompt,a.speaker,a.latent,a.egemaps,a.retrieval]
    if any('VP_PROTECTED' in str(p).upper() for p in paths): raise RuntimeError('protected promotion-gate input is forbidden')
    a.out.mkdir(parents=True,exist_ok=True)
    man=pd.read_csv(a.manifest); dup=pd.read_csv(a.duplicate_groups); oof=pd.read_csv(a.oof)
    prompt=pd.read_csv(a.prompt); speaker=pd.read_csv(a.speaker); latent=pd.read_csv(a.latent); eg=pd.read_csv(a.egemaps); retr=pd.read_csv(a.retrieval)
    train=man[man.split.eq('train')].copy().reset_index(drop=True); test=man[man.split.eq('test')].copy().reset_index(drop=True); dupmap=dict(zip(dup.Id.astype(int),dup.duplicate_group.astype(int)))

    cats={m:fixed_categories(man,train,m)[1] for m in MODULI}; rg=np.random.default_rng(SEED)
    obs,null=maxstat_v(cats,train.emotion.to_numpy(),rg,a.maxstat_permutations)
    fam=[]
    for m in MODULI:
        top,c=fixed_categories(man,train,m); chi,p,v=cramers(c,train.emotion)
        fam.append({'modulus':m,'top5':top,'chi2':chi,'raw_p':p,'cramers_v':v,'fwer_p':(int((null>=v).sum())+1)/(len(null)+1)})
    ded=dep_dedup(train,dup)
    cond=[conditional_family(man,ded,w,a.conditional_permutations,SEED+int(w*10000)) for w in [.25,.10,.05]]
    rank=rank_boot(oof[oof.validation.eq('VB')],train,128,[0,43,86,30,94],a.rank_bootstrap)+rank_boot(oof[oof.validation.eq('VB')],train,960,[384,192,576,606,926],a.rank_bootstrap)
    pd.DataFrame(rank).to_csv(a.out/'SAMPLE_COUNT_QUANTIZATION_RANK_STABILITY.csv',index=False)
    qres={'mission':'DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001','protected_gate_queried':False,'moduli':MODULI,
          'family_results':sorted(fam,key=lambda x:-x['cramers_v']),'conditional_dependency_dedup':cond,
          'interpretation':'MIXED_DURATION_SEGMENTATION_AND_SOURCE_FORMAT_QUANTIZATION','remainder128_exceptional':False,
          'decision':'diagnostic Q128/Q960 stress; no authoritative split; no automatic feature promotion'}
    (a.out/'SAMPLE_COUNT_QUANTIZATION_RESULTS.json').write_text(json.dumps(qres,indent=2))

    ids=np.sort(train.Id.astype(int).to_numpy()); y=train.set_index('Id').loc[ids].emotion.to_numpy(); va=oof[oof.validation.eq('VA')]
    pred={m:va[va.model.eq(m)].set_index('Id').loc[ids].pipeline_pred.to_numpy() for m in MODELS}
    train_ids=set(ids); test_ids=set(test.Id.astype(int)); subs={}
    r128=man.set_index('Id').samples.astype(int)%128; r960=man.set_index('Id').samples.astype(int)%960
    for r in [0,43,86,30,94]: subs[f'quant128_r{r}']=set(r128[r128.eq(r)].index.astype(int))
    for r in [192,606]: subs[f'quant960_r{r}']=set(r960[r960.eq(r)].index.astype(int))
    subs['dtype_int32']=set(man[man.dtype.eq('int32')].Id.astype(int)); subs['prompt90_beyond_duplicate']=beyond(prompt,'prompt_sim_0.90',dupmap)
    for d in ['0.25','0.30','0.35']: subs[f'speaker_d{d}_beyond_duplicate']=beyond(speaker,f'agg_d{d}',dupmap)
    for k in sorted(latent.joint_k4.unique()): subs[f'latent_k4_{int(k)}']=set(latent[latent.joint_k4.eq(k)].Id.astype(int))
    q20,q80=train.duration_seconds.quantile([.2,.8]); subs['duration_short20']=set(man[man.duration_seconds<=q20].Id.astype(int)); subs['duration_long20']=set(man[man.duration_seconds>=q80].Id.astype(int))
    feats=[c for c in eg.columns if c not in ['Id','split','filename','emotion']]; et=eg[eg.split.eq('train')]
    ss=StandardScaler().fit(et[feats]); pc=PCA(n_components=.9,svd_solver='full').fit(ss.transform(et[feats])); dist=np.linalg.norm(pc.transform(ss.transform(eg[feats])),axis=1); th=np.quantile(dist[eg.split.eq('train')],.8)
    subs['egemaps_outlier20']=set(eg.loc[dist>=th,'Id'].astype(int)); cov=va.groupby('Id').retrieval_covered.first(); subs['retrieval_covered']=set(cov[cov.astype(bool)].index.astype(int))|set(retr.test_Id.astype(int))
    prevalence=[]; rows=[]; scen=[]
    for name,S in subs.items():
        trp=len(S&train_ids)/len(train); tep=len(S&test_ids)/len(test); prevalence.append({'subgroup':name,'train_prevalence':trp,'test_prevalence':tep})
        sm=np.array([i in S for i in ids],bool)
        for q in [.2,.3,.4,.5]:
            for level,od in ODDS.items():
                rg=np.random.default_rng(int(hashlib.sha256(f'{name}|{q}|{level}|{SEED}'.encode()).hexdigest()[:8],16)); scores={m:[] for m in MODELS}; gaps=[]; pv=[]
                for _ in range(a.envelope_replicates):
                    priv=partition(rg,ids,y,sm,q,od); pub=~priv; pv.append(float(sm[priv].mean())); sc={m:.4*macro(y[pub],pred[m][pub])+.6*macro(y[priv],pred[m][priv]) for m in MODELS}; gaps.append(sc['FULL_RBF_SVM']-max(v for m,v in sc.items() if m!='FULL_RBF_SVM'))
                    for m in MODELS: scores[m].append(sc[m])
                bucket='plausible' if level.startswith(('mild','moderate')) else ('strong_tail' if level.startswith('strong') else 'extreme_tail')
                rec={'subgroup':name,'private_fraction':q,'level':level,'bucket':bucket,'train_prevalence':trp,'test_prevalence':tep,'pseudo_private_prevalence':float(np.mean(pv)),'rbf_minus_best_alt_mean':float(np.mean(gaps)),'rank_reversal_frequency':float(np.mean(np.array(gaps)<0))}
                scen.append(rec)
                for m in MODELS: rows.append({**rec,'model':m,'mean_score':float(np.mean(scores[m])),'top_frequency':float(np.mean(np.array(scores[m])==np.max(np.column_stack([scores[x] for x in MODELS]),axis=1)))})
    sdf=pd.DataFrame(scen); pd.DataFrame(rows).to_csv(a.out/'CORRELATED_ALLOCATION_RANK_STABILITY.csv',index=False)
    env={b:{'worst_mean_rbf_gap':float(g.rbf_minus_best_alt_mean.min()),'max_reversal_frequency':float(g.rank_reversal_frequency.max())} for b,g in sdf.groupby('bucket')}
    eres={'mission':'DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001','protected_gate_queried':False,'score':'0.40*public_macro_f1+0.60*private_macro_f1','private_fractions':[.2,.3,.4,.5],'odds':{k:('infinity' if np.isinf(v) else v) for k,v in ODDS.items()},'prevalence':prevalence,'risk_envelope':env,'decision':'correlated envelope is secondary sensitivity; V-B primary; retrieval separate; protected confirmation-only'}
    (a.out/'CORRELATED_ALLOCATION_EMULATOR_RESULTS.json').write_text(json.dumps(eres,indent=2))
    print(json.dumps({'quantization_top':qres['family_results'][:5],'conditional':cond,'risk_envelope':env},indent=2))

if __name__=='__main__': main()
