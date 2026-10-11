#!/usr/bin/env python3
"""Single frozen semantic challenger. Never queries protected folds or Kaggle.

replay: rebuild accepted C using authoritative waveform inputs and inner fits.
evaluate: consume sealed inference outputs, then (only if complementary) one
nested 18-feature logistic fusion. Stress checks are required before target work.
"""
import argparse, hashlib, json, time, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT/'runs/RS-DEFHS-FINAL-SEMANTIC-CHALLENGER-001'
DS = ROOT/'runs/DS-DEFHS-VALIDATION-HARDENING-002'
CLASSES = np.array(['angry','happy','neutral','sad'])
STATES = np.array(['angry','happy','neutral','sad','unclear'])
HASHES = {
 'QWEN_SEMANTIC_OUTPUTS.csv':'a2dad2feeac7cc817716ae4eb0cd8724c2f169c06262d45d8e00e66345e1569b',
 'emotion2vec_base_meanstd.npz':'4b8b6feeedc83ca2712b7fd21d9683465a07f7fcb82ca0c1d625512acf64326f',
 'xls_r_300m_meanstd.npz':'24bd935cc0271d5ae427acfed96a0237161b646e1bdcc1f2cb80c48abdcfa5fc',
 'FIXED_PAIR_VB.npz':'9f9ac86829230bcfde4be93a980161bf6139eaa38f3372efc822eb8edf79da45',
 'E2V_CONTROL_VB.npz':'14c86f6f61d633a72fd8535bec1070162e8a92f6de9c3f37ee366ff0e3d7a7b7',
 'XLSR_VB.npz':'f8a7cab17c88e98056d45fcad44479f1254acd68dbc7507e585f2197e1c87402'}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p, v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def idhash(ids): return hashlib.sha256(np.asarray(ids,dtype='<i8').tobytes()).hexdigest()
def mf(y,p):
    y=np.asarray(y);p=np.asarray(p)
    den=np.array([np.sum(y==c)+np.sum(p==c) for c in CLASSES],dtype=float)
    num=np.array([2*np.sum((y==c)&(p==c)) for c in CLASSES],dtype=float)
    return float(np.divide(num,den,out=np.zeros(4),where=den>0).mean())
def metric(y,p,fold=None):
    y=np.asarray(y);p=np.asarray(p)
    if not len(y): return {'n':0,'macro_f1':None}
    pr,rc,f,s=precision_recall_fscore_support(y,p,labels=CLASSES,zero_division=0)
    states=STATES if np.any(p=='unclear') else CLASSES
    out={'n':len(y),'macro_f1':mf(y,p),'accuracy':float(np.mean(y==p)),
      'per_class':{c:{'precision':float(pr[i]),'recall':float(rc[i]),'f1':float(f[i]),'support':int(s[i])} for i,c in enumerate(CLASSES)},
      'confusion_columns':states.tolist(),
      'confusion':[[int(np.sum((y==c)&(p==q))) for q in states] for c in CLASSES]}
    if fold is not None:out['fold_f1']=[mf(y[fold==i],p[fold==i]) for i in range(5)]
    return out
def transition(y,a,b):
    y=np.asarray(y);a=np.asarray(a);b=np.asarray(b)
    return {'changed':int(np.sum(a!=b)),'corrections':int(np.sum((a!=y)&(b==y))),
      'breakages':int(np.sum((a==y)&(b!=y))),
      'wrong_to_other_wrong':int(np.sum((a!=y)&(b!=y)&(a!=b))),
      'neutral_sad_cross_breakages':int(np.sum((a==y)&(a!=b)&np.isin(a,['neutral','sad'])&np.isin(b,['neutral','sad'])))}
def onehot(q):
    q=np.asarray(q);assert np.isin(q,STATES).all()
    return (q[:,None]==STATES[None,:]).astype(float)
def lr(): return LogisticRegression(C=1,solver='lbfgs',max_iter=5000,random_state=20261001)
def head(X,y,tr,vl):
    assert not np.any(tr&vl)
    m=make_pipeline(StandardScaler(),lr());m.fit(X[tr],y[tr])
    assert np.array_equal(m.classes_,CLASSES) and m[0].n_samples_seen_==tr.sum()
    return m.predict_proba(X[vl])
def load_inputs(inputs):
    for n,h in HASHES.items(): assert sha(inputs/n)==h,(n,'checksum')
    assert sha(DS/'VALIDATION_VB_FOLDS.csv')=='87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b'
    f=pd.read_csv(DS/'VALIDATION_VB_FOLDS.csv').sort_values('Id').reset_index(drop=True)
    assert len(f)==826 and f.Id.is_unique and set(f.fold)==set(range(5))
    ids=f.Id.to_numpy();y=f.emotion.to_numpy();X=[];outer=[]
    for feature,prob in [('emotion2vec_base_meanstd.npz','E2V_CONTROL_VB.npz'),('xls_r_300m_meanstd.npz','XLSR_VB.npz')]:
        z=np.load(inputs/feature,allow_pickle=False);ix={int(v):i for i,v in enumerate(z['Id'])}
        X.append(z['X'][[ix[int(v)] for v in ids]])
        z=np.load(inputs/prob,allow_pickle=False);ix={int(v):i for i,v in enumerate(z['Id'])}
        outer.append(z['prob'][[ix[int(v)] for v in ids]])
    z=np.load(inputs/'FIXED_PAIR_VB.npz',allow_pickle=False)
    assert np.array_equal(z['Id'],ids) and np.max(np.abs((outer[0]+outer[1])/2-z['prob']))<1e-12
    q=pd.read_csv(inputs/'QWEN_SEMANTIC_OUTPUTS.csv').set_index('Id').loc[ids].semantic_label.to_numpy()
    return f,X,np.column_stack(outer),q
def build_inner(f,X,outer_prob,cache,view):
    fs=f.fold.to_numpy();ids=f.Id.to_numpy();y=f.emotion.to_numpy()
    cache.mkdir(parents=True,exist_ok=True);arrays={};audit=[];start=time.monotonic()
    for outer in range(5):
        tr=fs!=outer;vl=~tr;inner=np.zeros((len(f),8));fold_audit=[]
        for block in sorted(set(fs[tr])):
            it=tr&(fs!=block);iv=tr&(fs==block)
            assert not np.any((it|iv)&vl)
            inner[iv]=np.column_stack([head(x,y,it,iv) for x in X])
            fold_audit.append({'inner_block':int(block),'base_fit_n':int(it.sum()),'base_predict_n':int(iv.sum()),
                'fit_ids_sha256':idhash(ids[it]),'predict_ids_sha256':idhash(ids[iv]),'outer_overlap':0})
        rp=np.column_stack([head(x,y,tr,vl) for x in X])
        if outer_prob is not None:
            op=outer_prob[vl]
            mismatches=[int(np.sum(rp[:,s:s+4].argmax(1)!=op[:,s:s+4].argmax(1))) for s in (0,4)]
            diff=float(np.max(np.abs(rp-op)))
        else: op=rp;diff=0.
        arrays[f'inner_{outer}']=inner;arrays[f'outer_{outer}']=op
        audit.append({'outer_fold':outer,'train_n':int(tr.sum()),'heldout_n':int(vl.sum()),
          'train_ids_sha256':idhash(ids[tr]),'heldout_ids_sha256':idhash(ids[vl]),
          'inner_splits':fold_audit,'fresh_refit_hard_mismatches':mismatches if outer_prob is not None else [0,0],
          'outer_probability_max_abs_replay_diff':diff})
        print(f'{view}_INNER_READY={outer}',flush=True)
    arrays['Id']=ids;arrays['fold']=fs
    np.savez_compressed(cache/f'{view}_inner.npz',**arrays)
    dump(cache/f'{view}_audit.json',{'view':view,'outer':audit,'wall_seconds':time.monotonic()-start,
      'base_fits':50,'scaler_fit_on_base_training_only':True,'heldout_labels_in_meta_fit':False})
    return arrays
def fuse(f,arrays,semantic):
    ids=f.Id.to_numpy();fs=f.fold.to_numpy();y=f.emotion.to_numpy();out=np.zeros((len(f),4))
    assert np.array_equal(ids,arrays['Id']) and np.array_equal(fs,arrays['fold'])
    for outer in range(5):
        tr=fs!=outer;vl=~tr
        train=np.column_stack([arrays[f'inner_{outer}'][tr],semantic[tr]])
        valid=np.column_stack([arrays[f'outer_{outer}'],semantic[vl]])
        m=lr();m.fit(train,y[tr]);assert np.array_equal(m.classes_,CLASSES)
        out[vl]=m.predict_proba(valid)
    return out
def hard_mask(wave):
    e=wave[:,:4];x=wave[:,4:];p=(e+x)/2
    es=np.sort(e,axis=1);ps=np.sort(p,axis=1)
    return ((es[:,-1]<.6)|(ps[:,-1]<.6)|((es[:,-1]-es[:,-2])<.2)|
      ((ps[:,-1]-ps[:,-2])<.2)|(e.argmax(1)!=p.argmax(1))|(e.argmax(1)!=x.argmax(1)))
def replay(inputs,cache):
    t=time.monotonic();f,X,wave,q=load_inputs(inputs)
    arrays=build_inner(f,X,wave,cache,'VB')
    pc=fuse(f,arrays,onehot(q));c=CLASSES[pc.argmax(1)]
    y=f.emotion.to_numpy();fs=f.fold.to_numpy();hard=hard_mask(wave)
    authority=json.loads((ROOT/'runs/RS-DEFHS-NESTED-SEMANTIC-FUSION-001/RESULTS.json').read_text())
    m=metric(y,c,fs)
    assert abs(m['macro_f1']-authority['PRIMARY_CV_C'])<1e-12
    assert np.allclose(m['fold_f1'],authority['FOLD_F1_C'],atol=1e-12,rtol=0)
    assert m['confusion']==authority['CONFUSION_C']
    assert int(hard.sum())==316 and abs(mf(y[hard],c[hard])-authority['HARD_SURROGATE']['C'])<1e-12
    a=CLASSES[((wave[:,:4]+wave[:,4:])/2).argmax(1)]
    tr=transition(y,a,c)
    assert tr['corrections']==70 and tr['breakages']==41
    df=f[['Id','emotion','fold','duplicate_group']].copy()
    df['system_c_pred']=c;df['qwen8b']=q;df['hard_surrogate']=hard
    df['waveform_disagreement']=wave[:,:4].argmax(1)!=wave[:,4:].argmax(1)
    for i,label in enumerate(CLASSES):
        df['c_p_'+label]=pc[:,i];df['e2v_p_'+label]=wave[:,i];df['xlsr_p_'+label]=wave[:,4+i]
    df.to_csv(RUN/'SYSTEM_C_AUTHORITY_OOF.csv',index=False,float_format='%.17g')
    covered=q!='unclear'
    evidence={'status':'EXACT_PUBLISHED_AUTHORITY_REPLAY_PASS','system_c':m,
      'qwen8b':metric(y,q,fs),'qwen8b_coverage':float(covered.mean()),
      'qwen8b_covered_only':metric(y[covered],q[covered]),'c_vs_fixed_waveform_pair':tr,
      'hard_surrogate':metric(y[hard],c[hard]),'rowlevel_sha256':sha(RUN/'SYSTEM_C_AUTHORITY_OOF.csv'),
      'wall_seconds':time.monotonic()-t,'gpu_hours':0,
      'provenance':'Reconstruction from checksum-verified AST INPUT_AUTHORITY artifacts; all published C score, fold, confusion, hard-cohort and correction checks pass. No archived original C row-file checksum exists in the accepted report; this is an authenticated recipe replay, not a byte-identical archive claim.',
      'protected_validation_read':False}
    dump(RUN/'SYSTEM_C_REPLAY.json',evidence)
    dump(cache/'CONTRACT.json',{'VB_inner_sha256':sha(cache/'VB_inner.npz'),
        'oof_sha256':evidence['rowlevel_sha256'],'input_hashes':HASHES})
    print(json.dumps({'C':m['macro_f1'],'Qwen8B':evidence['qwen8b']['macro_f1'],'wall_seconds':evidence['wall_seconds']}),flush=True)

def comparison(y,c,d,fs=None):
    a=metric(y,c,fs);b=metric(y,d,fs)
    out={'C':a,'challenger':b,'delta':None if not len(y) else b['macro_f1']-a['macro_f1'],
        'transitions':transition(y,c,d)}
    if fs is not None:out['fold_deltas']=(np.array(b['fold_f1'])-np.array(a['fold_f1'])).tolist()
    return out

def semantic_gate(y,old,new,c):
    novel=(new==y)&(old!=y);both=novel&(c!=y)
    return {'macro_f1_strictly_better_than_qwen8b':mf(y,new)>mf(y,old),
      'at_least_10_new_correct_rows':int(novel.sum())>=10,
      'new_correct_rows_span_at_least_3_classes':len(set(y[novel]))>=3,
      'at_least_5_corrections_unavailable_to_both_C_and_Qwen8B':int(both.sum())>=5,
      'includes_new_neutral_or_sad_correction':bool(np.any(both&np.isin(y,['neutral','sad'])))}

def verify_inference(path,ids):
    import ast,base64,gzip
    runner=ROOT/'kaggle/rs_final_semantic_train826_001/run.py'
    tree=ast.parse(runner.read_text())
    payload=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets))
    contract=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    c=json.loads((path/'CONTRACT.json').read_text());r=json.loads((path/'RESULT.json').read_text())
    feasible=json.loads((path/'FEASIBILITY.json').read_text());ck=json.loads((path/'CHECKPOINT.json').read_text())
    assert c['sha256']==contract and c['model']==payload['model_id'] and c['revision']==payload['revision']
    assert feasible['status']=='PASS' and all(feasible['gates'].values())
    assert r['status']=='INFERENCE_COMPLETE_NOT_EVALUATED' and r['rows']==826
    assert not r['protected_validation_accessed'] and not r['target209_inferred'] and not r['kaggle_submission']
    assert ck['revision']==payload['revision'] and ck['model_id']==payload['model_id']
    observed={x['name']:x for x in ck['files']}
    for name,spec in payload['model_files'].items():
        assert observed[name]['bytes']==spec['bytes']
        if spec['sha256']: assert observed[name]['sha256']==spec['sha256']
    assert sha(path/'QWEN14B_TRAIN826.csv')==r['output_sha256']
    table=pd.read_csv(path/'QWEN14B_TRAIN826.csv')
    assert list(table.columns)==['Id','semantic_label'] and len(table)==826 and table.Id.is_unique
    assert set(table.Id)==set(ids) and table.semantic_label.isin(STATES).all()
    raw=gzip.decompress(base64.b64decode(payload['records_gzip_b64']));rows=json.loads(raw)
    by_id={int(x['Id']):x['transcript'] for x in rows};by_text={}
    for row in table.itertuples():
        text=by_id[int(row.Id)]
        if text in by_text: assert by_text[text]==row.semantic_label
        by_text[text]=row.semantic_label
    assert len(by_text)==711
    return table.set_index('Id').loc[ids].semantic_label.to_numpy(),r

def evaluate(inputs,cache,inference):
    start=time.monotonic();f,X,wave,old=load_inputs(inputs)
    assert not (RUN/'SEMANTIC_RESULTS.json').exists(), 'One sealed evaluation only; retain prior evidence'
    replay_info=json.loads((RUN/'SYSTEM_C_REPLAY.json').read_text())
    assert sha(RUN/'SYSTEM_C_AUTHORITY_OOF.csv')==replay_info['rowlevel_sha256']
    cc=json.loads((cache/'CONTRACT.json').read_text())
    assert cc['VB_inner_sha256']==sha(cache/'VB_inner.npz') and cc['input_hashes']==HASHES
    base=pd.read_csv(RUN/'SYSTEM_C_AUTHORITY_OOF.csv');assert np.array_equal(base.Id,f.Id)
    c=base.system_c_pred.to_numpy();y=f.emotion.to_numpy();fs=f.fold.to_numpy()
    new,infer_info=verify_inference(inference,f.Id.to_numpy())
    hard=hard_mask(wave);wd=wave[:,:4].argmax(1)!=wave[:,4:].argmax(1)
    novel=(new==y)&(old!=y);beyond_c=novel&(c!=y);covered=new!='unclear'
    sg=semantic_gate(y,old,new,c)
    sr={'status':'PASS' if all(sg.values()) else 'STOP_NO_STRONG_COMPLEMENTARY_EVIDENCE',
      'criteria':sg,'new_semantic':metric(y,new,fs),'old_semantic':metric(y,old,fs),
      'coverage':float(covered.mean()),'covered_only':metric(y[covered],new[covered]),
      'new_vs_old':transition(y,old,new),'novel_correct_n':int(novel.sum()),
      'correct_unavailable_to_old_Qwen_and_C':int(beyond_c.sum()),
      'by_true_class':{label:transition(y[y==label],old[y==label],new[y==label]) for label in CLASSES},
      'hard_cohort':metric(y[hard],new[hard]),'waveform_disagreement':metric(y[wd],new[wd]),
      'neutral_sad':metric(y[np.isin(y,['neutral','sad'])],new[np.isin(y,['neutral','sad'])]),
      'inference_compute':infer_info}
    dump(RUN/'SEMANTIC_RESULTS.json',sr)
    errors=base[['Id','emotion','fold','system_c_pred','qwen8b','hard_surrogate','waveform_disagreement']].copy()
    errors['qwen14b']=new;errors['new_correct_unavailable_to_qwen8b']=novel
    errors['new_correct_unavailable_to_both']=beyond_c
    errors.to_csv(RUN/'SEMANTIC_ROW_COMPARISON.csv',index=False)
    if not all(sg.values()):
        dump(RUN/'FINAL_GATE.json',{'status':sr['status'],'target209_authorized':False,'system_c_preserved':True})
        print(sr['status']);return
    arrays=dict(np.load(cache/'VB_inner.npz',allow_pickle=False))
    pd_=fuse(f,arrays,np.column_stack([onehot(old),onehot(new)]));d=CLASSES[pd_.argmax(1)]
    comp=comparison(y,c,d,fs)
    from defhs_frozen_closure_utils import Evidence,labels
    dup=pd.read_csv(DS/'DUPLICATE_GROUPS_FINAL.csv');prompt=pd.read_csv(inputs/'PROMPT_CLUSTER_ASSIGNMENTS.csv')
    ev=Evidence(f.Id.to_numpy(),dup,prompt)
    draws=ev.boots(labels(y),labels(d))-ev.boots(labels(y),labels(c))
    ci=np.quantile(draws,[.025,.975]).tolist()
    perclass_delta={k:comp['challenger']['per_class'][k]['f1']-comp['C']['per_class'][k]['f1'] for k in CLASSES}
    hardcomp=comparison(y[hard],c[hard],d[hard])
    delete=[mf(y[fs!=i],d[fs!=i])-mf(y[fs!=i],c[fs!=i]) for i in range(5)]
    gates={'pooled_delta_at_least_0_005':comp['delta']>=.005,
      'positive_in_at_least_4_of_5_folds':sum(v>0 for v in comp['fold_deltas'])>=4,
      'no_class_drop_over_0_02':min(perclass_delta.values())>=-.02,
      'hard_cohort_nonnegative':hardcomp['delta']>=0,
      'dependency_bootstrap_lower_gt_zero':ci[0]>0,
      'all_delete_fold_deltas_positive':min(delete)>0}
    errors['challenger_pred']=d
    for i,label in enumerate(CLASSES):errors['challenger_p_'+label]=pd_[:,i]
    errors.to_csv(RUN/'CHALLENGER_PRIMARY_OOF.csv',index=False,float_format='%.17g')
    result={'status':'PASS_PENDING_STRESS' if all(gates.values()) else 'STOP_PRIMARY_GATE_FAILED',
      'comparison':comp,'criteria':gates,'per_class_deltas':perclass_delta,
      'paired_dependency_bootstrap_95':ci,'delete_fold_deltas':delete,
      'hard_cohort':hardcomp,'waveform_disagreement':comparison(y[wd],c[wd],d[wd]),
      'neutral_sad':comparison(y[np.isin(y,['neutral','sad'])],c[np.isin(y,['neutral','sad'])],d[np.isin(y,['neutral','sad'])]),
      'protocol':'18 raw inputs = 4 E2V + 4 XLSR + 5 old-Qwen + 5 new-Qwen; same L2 logistic; inner heads exclude outer fold',
      'protected_validation_read':False,'wall_seconds':time.monotonic()-start}
    dump(RUN/'PRIMARY_RESULTS.json',result)
    if not all(gates.values()):
        dump(RUN/'FINAL_GATE.json',{'status':result['status'],'target209_authorized':False,'system_c_preserved':True})
        print(result['status']);return
    stress(inputs,cache,f,X,old,new,c,d,hard)

def stress(inputs,cache,f,X,old,new,c,d,hard):
    """New challenger-specific V-A, cross-format, V-Q, private-allocation evidence."""
    from scipy.stats import nchypergeom_fisher
    start=time.monotonic();ids=f.Id.to_numpy();y=f.emotion.to_numpy();fs=f.fold.to_numpy()
    va=pd.read_csv(DS/'VALIDATION_VA_FOLDS.csv').set_index('Id').loc[ids].reset_index()
    assert np.array_equal(va.emotion,y)
    a=build_inner(va,X,None,cache,'VA')
    cq=onehot(old);dq=np.column_stack([cq,onehot(new)])
    ca=CLASSES[fuse(va,a,cq).argmax(1)];da=CLASSES[fuse(va,a,dq).argmax(1)]
    dup=pd.read_csv(DS/'DUPLICATE_GROUPS_FINAL.csv');train_dup=dup[dup.split=='train']
    group=dict(zip(train_dup.Id,train_dup.duplicate_group));covered=np.zeros(len(f),bool)
    cr=ca.copy();dr=da.copy();afs=va.fold.to_numpy()
    for k in range(5):
        consensus={}
        for gid in set(group.values()):
            vals=[y[i] for i in range(len(ids)) if afs[i]!=k and group.get(int(ids[i]))==gid]
            if vals and len(set(vals))==1:consensus[gid]=vals[0]
        for i in np.where(afs==k)[0]:
            gid=group.get(int(ids[i]))
            if gid in consensus:cr[i]=dr[i]=consensus[gid];covered[i]=True
    assert np.array_equal(cr[covered],dr[covered])
    va_result={'SER':comparison(y,ca,da,afs),'retrieval_pipeline':comparison(y,cr,dr,afs),
      'nonretrieval':comparison(y[~covered],ca[~covered],da[~covered]),'retrieval_rows':int(covered.sum()),
      'retrieval_accuracy':float(np.mean(cr[covered]==y[covered])),
      'coverage_method':'frozen duplicate graph; unanimous labels from the outer training fold only'}
    pd.DataFrame({'Id':ids,'emotion':y,'fold':afs,'C_SER':ca,'D_SER':da,'C_pipeline':cr,
        'D_pipeline':dr,'retrieval_covered':covered}).to_csv(RUN/'CHALLENGER_VA_OOF.csv',index=False)
    man=pd.read_csv(DS/'DATA_MANIFEST.csv').set_index('Id').loc[ids]
    cross={}
    for source,target in [('int16','int32'),('int32','int16')]:
        tr=man.dtype.eq(source).to_numpy();vl=~tr;inner=np.zeros((len(f),8))
        for k in range(5):
            it=tr&(fs!=k);iv=tr&(fs==k)
            assert not np.any((it|iv)&vl)
            inner[iv]=np.column_stack([head(x,y,it,iv) for x in X])
        op=np.column_stack([head(x,y,tr,vl) for x in X]);pred=[]
        for sem in [cq,dq]:
            m=lr();m.fit(np.column_stack([inner[tr],sem[tr]]),y[tr])
            pred.append(m.predict(np.column_stack([op,sem[vl]])))
        cross[source+'_to_'+target]={'training_n':int(tr.sum()),'comparison':comparison(y[vl],*pred),
            'outer_format_labels_used_in_fit':False}
    masks={'INT16':man.dtype.eq('int16').to_numpy(),'INT32':man.dtype.eq('int32').to_numpy(),
        'HARD':hard,'VA_NONRETRIEVAL':~covered}
    for mod,res in [(128,[0,43,86,30,94]),(960,[384,192,576,606,926])]:
        rem=man.samples.to_numpy()%mod
        for v in res:masks[f'Q{mod}_{v}']=rem==v
        masks[f'Q{mod}_OTHER']=~np.isin(rem,res)
    prompt=pd.read_csv(inputs/'PROMPT_CLUSTER_ASSIGNMENTS.csv');pgroup=dict(zip(prompt.Id,prompt['prompt_sim_0.90']))
    prompt_multi=set()
    for _,g in prompt.groupby('prompt_sim_0.90'):
        families={('d',group[int(v)]) if int(v) in group else ('s',int(v)) for v in g.Id}
        if len(g)>1 and len(families)>1:prompt_multi.update(map(int,g.Id))
    masks['PROMPT_BEYOND_DUPLICATE']=np.isin(ids,list(prompt_multi))
    lo,hi=np.quantile(man.duration_seconds,[.2,.8])
    masks['SHORT20']=man.duration_seconds.to_numpy()<=lo;masks['LONG20']=man.duration_seconds.to_numpy()>=hi
    strata={};qualified=[]
    for name,mask in masks.items():
        comp=comparison(y[mask],c[mask],d[mask]);supports=[int(np.sum(y[mask]==cl)) for cl in CLASSES]
        adequate=min(supports)>=5
        strata[name]={'comparison':comp,'class_supports':supports,'adequate_support_for_gate':adequate}
        if adequate:qualified.append(comp['delta'])
    # Fixed emulator scenarios, not estimates of actual hidden allocation.
    scenarios=[];bucket=[('baseline',np.zeros(len(y),bool))]+list(masks.items())
    for view,cp,dp in [('VB_SER',c,d),('VA_PIPELINE',cr,dr)]:
        for name,mask in bucket:
            for fraction in [.2,.3,.4,.5]:
                for odds in ([1.] if name=='baseline' else [.5,2/3,1.5,2.]):
                    seed=int(hashlib.sha256(f'{view}|{name}|{fraction}|{odds}|20261011'.encode()).hexdigest()[:8],16)
                    rng=np.random.default_rng(seed);gaps=[];private_gaps=[]
                    for _ in range(250):
                        private=np.zeros(len(y),bool)
                        for label in CLASSES:
                            ix=np.where(y==label)[0];n=len(ix);k=min(max(round(fraction*n),1),n-1);mark=mask[ix];K=int(mark.sum())
                            if K==0:x=0
                            elif K==n:x=k
                            else:x=int(nchypergeom_fisher.rvs(n,K,k,odds,random_state=rng))
                            private[rng.choice(ix[mark],x,replace=False)]=True
                            private[rng.choice(ix[~mark],k-x,replace=False)]=True
                        pg=mf(y[private],dp[private])-mf(y[private],cp[private])
                        ug=mf(y[~private],dp[~private])-mf(y[~private],cp[~private])
                        private_gaps.append(pg);gaps.append(.4*ug+.6*pg)
                    scenarios.append({'view':view,'subgroup':name,'private_fraction':fraction,'odds':odds,
                      'replicates':250,'weighted_delta_mean':float(np.mean(gaps)),
                      'weighted_delta_quantiles':np.quantile(gaps,[.025,.5,.975]).tolist(),
                      'reversal_frequency':float(np.mean(np.array(gaps)<0)),
                      'private_delta_mean':float(np.mean(private_gaps)),
                      'private_delta_quantiles':np.quantile(private_gaps,[.025,.5,.975]).tolist()})
    criteria={'VA_pipeline_nonnegative':va_result['retrieval_pipeline']['delta']>=0,
      'VA_nonretrieval_nonnegative':va_result['nonretrieval']['delta']>=0,
      'VD_each_direction_drop_at_most_0_02':min(v['comparison']['delta'] for v in cross.values())>=-.02,
      'adequately_supported_VQ_drop_at_most_0_02':bool(qualified) and min(qualified)>=-.02,
      'plausible_allocation_weighted_mean_nonnegative':min(v['weighted_delta_mean'] for v in scenarios)>=0,
      'plausible_allocation_private_mean_nonnegative':min(v['private_delta_mean'] for v in scenarios)>=0,
      'plausible_allocation_reversal_at_most_0_20':max(v['reversal_frequency'] for v in scenarios)<=.20}
    result={'status':'PASS' if all(criteria.values()) else 'STOP_STRESS_GATE_FAILED','criteria':criteria,
      'VA':va_result,'VD_cross_format':cross,'VD_Q_subgroups':strata,'private_allocation':scenarios,
      'private_allocation_scope':'Frozen recording-format, quantization, duration, prompt, difficulty and retrieval scenarios only; unmeasured shifts remain possible. Class-stratified allocations are scenarios, not hidden assignment estimates.',
      'wall_seconds':time.monotonic()-start,'protected_validation_read':False,'new_candidate_results':True}
    dump(RUN/'STRESS_RESULTS.json',result)
    dump(RUN/'FINAL_GATE.json',{'status':'ELIGIBLE_FOR_SS_REVIEW' if all(criteria.values()) else result['status'],
      'target209_authorized':all(criteria.values()),'kaggle_submission_authorized':False,
      'system_c_preserved':True,'protected_gate_unqueried':True})
    print(result['status'],flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['replay','evaluate']);ap.add_argument('--inputs',type=Path,required=True)
    ap.add_argument('--inference',type=Path)
    ap.add_argument('--cache',type=Path,default=ROOT/'work/final_semantic_cache');a=ap.parse_args()
    RUN.mkdir(parents=True,exist_ok=True)
    warnings.simplefilter('error',ConvergenceWarning)
    with threadpool_limits(limits=2):
        if a.mode=='replay':replay(a.inputs,a.cache)
        else:
            assert a.inference is not None
            evaluate(a.inputs,a.cache,a.inference)

if __name__=='__main__':main()
