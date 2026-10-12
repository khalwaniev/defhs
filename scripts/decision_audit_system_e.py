#!/usr/bin/env python3
"""RS-DEFHS-SYSTEM-E-DECISION-OPTIMIZATION-001 — read-only, two frozen tests.

All label-derived quantities computed from the training side of outer fold.
A transductive decoder uses *only* unlabeled held-out posterior batch and train priors.
B uses semantic expert per-class correctness Wilson/Beta lower credible estimates
from outer training labels, not OOF held-out labels.
Neither method tunes a parameter or trains on outer-heldout results.
"""
import hashlib, io, json, zipfile, os
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import beta
from sklearn.metrics import log_loss

HERE=Path(__file__).resolve().parent
BASE=Path(os.environ.get('DEFHS_DECISION_INPUT_ROOT', str(HERE/'evidence')))
E=BASE/'DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip'
D=BASE/'DEFHS_SYSTEM_D_FINAL_DELIVERY.zip'
CAN=BASE/'DEFHS_SYSTEM_E_FINAL_CANONICAL_HANDOFF.zip'
C=np.array(['angry','happy','neutral','sad'])
K=4


def sha(b):return hashlib.sha256(b).hexdigest()

def mf(y,p):
    den=np.array([np.sum(y==c)+np.sum(p==c) for c in C],float)
    num=np.array([2*np.sum((y==c)&(p==c)) for c in C],float)
    return float(np.divide(num,den,out=np.zeros(4),where=den>0).mean())

def f1_per_class(y,p):
    return {c:float(2*np.sum((y==c)&(p==c))/(np.sum(y==c)+np.sum(p==c))) for c in C}

def changes(y,a,b):
    m=a!=b
    return dict(changed=int(m.sum()), corrections=int(((a!=y)&(b==y)).sum()),breakages=int(((a==y)&(b!=y)).sum()),wrong_to_wrong=int(((a!=y)&(b!=y)&m).sum()))

def joint_macro_surrogate(prob,prior,baseline=None,locked=None):
    """Greedy coordinate-ascent on ratio-of-expectations 4-class macro F1.
    E[TP_c]=sum_{pred c}p_ic, E[Y_c]=n*prior[c]. No E[ratio] claim.
    Independent of labels, deterministic stable tie/order. Uses all heldout
    probabilities jointly; deployment must use *one* same transductive batch.
    """
    p=np.asarray(prob,dtype=np.float64)
    n=len(p)
    labels=p.argmax(1).copy() if baseline is None else np.asarray(baseline,int).copy()
    fixed=np.zeros(n,dtype=bool) if locked is None else np.asarray(locked,bool)
    assert p.shape==(n,4) and np.allclose(p.sum(1),1,atol=1e-7)
    assert np.all(prior>0) and abs(prior.sum()-1)<1e-12
    support=n*prior
    counts=np.bincount(labels,minlength=4).astype(float)
    tp=np.array([np.sum(p[labels==c,c]) for c in range(4)],float)
    def val(k,nt=tp,nc=counts):return 2*nt[k]/(support[k]+nc[k])
    prev=sum(val(c) for c in range(4))/4
    changed=0
    for _ in range(n*4):
        a=labels
        b_add=p
        a_drop=p[np.arange(n),a]
        old_a=2*tp[a]/(support[a]+counts[a]); new_a=2*(tp[a]-a_drop)/(support[a]+counts[a]-1)
        old_b=2*tp/(support+counts);new_b=2*(tp[None,:]+b_add)/(support[None,:]+counts[None,:]+1)
        delta=(new_a-old_a)[:,None]+new_b-old_b[None,:]
        delta[np.arange(n),a]=-np.inf
        delta[fixed,:]=-np.inf
        bi,bj=np.unravel_index(np.argmax(delta),delta.shape)
        gain=float(delta[bi,bj])/4
        if not np.isfinite(gain) or gain<=1e-12:break
        src=a[bi];dst=bj
        counts[src]-=1;counts[dst]+=1
        tp[src]-=p[bi,src];tp[dst]+=p[bi,dst]
        a[bi]=dst;changed+=1
        after=sum(val(c) for c in range(4))/4
        assert after>=prev-1e-11, ('objective monotonic',prev,after)
        prev=after
    return labels,dict(changes=changed,surrogate=float(prev),expected_supports=support.tolist())

def expert_wilson(prob, expert, ytrain, qtrain):
    """Class-conditional expert reliability, Beta(1,1) lower 95% bound.
    On disagreement, only use q if it is E's rank-2 class and the conservative
    expert precision estimate exceeds E's top predicted probability.
    All reliability estimates come from outer training labels ONLY.
    """
    pred=prob.argmax(1).copy()
    ranks=np.argsort(prob,axis=1)
    precision={}
    changes=[]
    for s in C:
        mask=qtrain==s
        k=int(np.sum(ytrain[mask]==s));n=int(mask.sum())
        precision[s]={'correct':k,'total':n,'lower05':float(beta.ppf(.05,k+1,n-k+1))}
    for i,state in enumerate(expert):
        if state not in precision: continue
        j=np.where(C==state)[0][0]
        if j==pred[i]:continue
        if j!=ranks[i,-2]:continue
        if precision[state]['lower05']>prob[i,pred[i]]:
            changes.append(i);pred[i]=j
    return pred,precision,changes

def calibration(y,P):
    ix=np.searchsorted(C,y)
    brier=float(np.mean(np.sum((P-np.eye(4)[ix])**2,axis=1)))
    ce=float(log_loss(y,P,labels=C))
    conf=P.max(axis=1);right=(P.argmax(axis=1)==ix)
    # Equally spaced confidence bins, a frozen diagnostic not a calibrator.
    bins=np.linspace(0,1,11);ece=0.;d=[]
    for k,(lo,hi) in enumerate(zip(bins[:-1],bins[1:])):
        mask=(conf>=lo)&((conf<=hi) if k==len(bins)-2 else (conf<hi))
        if not np.any(mask):continue
        gap=float(np.mean(right[mask])-np.mean(conf[mask]))
        ece+=float(mask.mean()*abs(gap))
        d.append({'left':float(lo),'right':float(hi),'n':int(mask.sum()),'accuracy':float(right[mask].mean()),'confidence':float(conf[mask].mean()),'gap_acc_minus_conf':gap})
    return dict(logloss=ce,brier=brier,ece_10bins=ece,bins=d,
        per_class_mean_pred={c:float(P[:,j].mean()) for j,c in enumerate(C)},
        per_class_true_rate={c:float(np.mean(y==c)) for c in C})

def group_bootstrap(y,ref,proposals,roots):
    rg=np.random.Generator(np.random.PCG64(20260930))
    component=np.unique(roots)
    mapping={v:i for i,v in enumerate(component)}
    idx=np.array([mapping[v] for v in roots]); assert len(component)==656
    W=rg.exponential(1.,size=(2000,len(component)))[:,idx]
    yi=np.searchsorted(C,y)
    def wscore(pred):
        pi=np.searchsorted(C,pred)
        cells=np.stack([W[:,(yi==k)&(pi==l)].sum(1) for k in range(4) for l in range(4)],axis=1).reshape(-1,4,4)
        den=cells.sum(axis=1)+cells.sum(axis=2)
        return np.divide(2*np.diagonal(cells,axis1=1,axis2=2),den,out=np.zeros_like(den),where=den>0).mean(1)
    scores=wscore(ref)
    samples=np.stack([wscore(p)-scores for p in proposals],axis=0)
    points=np.array([mf(y,p)-mf(y,ref) for p in proposals])
    sds=np.std(samples,axis=1,ddof=1)
    z=(samples-points[:,None])/sds[:,None]
    max_t=np.max(np.abs(z),axis=0)
    q=float(np.quantile(max_t,.95,method='higher'))
    return [dict(delta=float(point),naive_ci95=np.quantile(row,[.025,.975]).tolist(),multiplicity_max_t_ci95=[float(point-q*sd),float(point+q*sd)],sd=float(sd)) for point,row,sd in zip(points,samples,sds)]

def main():
    expected={'E':'dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf',
              'D':'fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839',
              'CAN':'c7f16f3f91be5b90349641a61d85222e69d71b5f88dcb1bb3030acfad8718a59'}
    for k,p in [('E',E),('D',D),('CAN',CAN)]:assert sha(p.read_bytes())==expected[k],(k,'SHA mismatch')
    with zipfile.ZipFile(E) as z:
        b=z.read('SYSTEM_E_PRIMARY_OOF.csv')
        df=pd.read_csv(io.BytesIO(b))
        oof_sha=sha(b)
        flags=np.frombuffer(bytes.fromhex(z.read('manifest_flags.hex').decode()),dtype='>u2').astype(int)
        # Flag bit encoding is documented in accepted stress script.
        assert len(flags)==826 and flags.sum()==379846
    with zipfile.ZipFile(CAN) as z:
        test=pd.read_csv(io.BytesIO(z.read('production/SYSTEM_E_209_ROW_AUDIT.csv')))
        cand=z.read('production/submission_system_e_exploratory.csv')
        assert sha(cand)=='e47676192cbd02393a49889214238f34cb8b49df2f9772b30cb19d766589df90'
    with zipfile.ZipFile(BASE/'DEFHS_SOL6_FINAL_EVIDENCE.zip') as z:
        roots_text=z.read('component_roots.b36').decode().strip().replace('\n','')
    roots=np.array([int(roots_text[j:j+2],36) for j in range(0,len(roots_text),2)])
    assert len(roots)==826 and len(np.unique(roots))==656
    assert len(df)==826 and df.Id.is_unique and np.array_equal(df.Id.values,np.sort(df.Id.values))
    y=df.emotion.to_numpy(); folds=df.fold.to_numpy();assert set(folds)==set(range(5))
    P=df[['system_E_p_'+c for c in C]].to_numpy()
    baseline=C[P.argmax(1)]
    assert np.array_equal(baseline,df.system_E_pred.values)
    assert abs(mf(y,baseline)-0.8774091527555827)<1e-12
    assert np.allclose(P.sum(axis=1),1,atol=1e-12)
    q=df.new_asr_qwen14_state.to_numpy()
    A=baseline.copy();B=baseline.copy();fold_record=[]
    for f in range(5):
        te=folds==f
        tr=(folds!=f)&~np.isin(roots,roots[te])
        assert not np.intersect1d(roots[tr],roots[te]).size
        prior=np.array([np.mean(y[tr]==c) for c in C]);assert np.all(prior>0)
        decoded,info=joint_macro_surrogate(P[te],prior)
        A[te]=C[decoded]
        b,expert_stats,b_changes=expert_wilson(P[te],q[te],y[tr],q[tr])
        B[te]=C[b]
        fold_record.append({'fold':int(f),'train_n':int(tr.sum()),'excluded_cross_fold_group_n':int(np.sum(folds!=f)-np.sum(tr)),'eval_n':int(te.sum()),'train_prior':prior.tolist(),
          'A':info,'B_precision_train_only':expert_stats,'B_changed_eval_n':len(b_changes),
          'base_f1':mf(y[te],baseline[te]),'A_f1':mf(y[te],A[te]),'B_f1':mf(y[te],B[te])})
    qmask=(flags & (256<<3))!=0;assert qmask.sum()==41
    dtype=(flags&1)!=0;assert dtype.sum()==746
    hard=df.hard316.to_numpy(bool);assert int(hard.sum())==316
    va=None
    with zipfile.ZipFile(E) as z:
        va=pd.read_csv(io.BytesIO(z.read('SYSTEM_E_VA_OOF.csv')))
    def collect(pred):
        out={'macro_f1':mf(y,pred),'gain_vs_E':mf(y,pred)-mf(y,baseline),
             'per_class_f1':f1_per_class(y,pred),'changes':changes(y,baseline,pred),
             'fold_deltas':[mf(y[folds==k],pred[folds==k])-mf(y[folds==k],baseline[folds==k]) for k in range(5)],
             'hard316_delta':mf(y[hard],pred[hard])-mf(y[hard],baseline[hard]),
             'INT16_delta':mf(y[dtype],pred[dtype])-mf(y[dtype],baseline[dtype]),
             'INT32_delta':mf(y[~dtype],pred[~dtype])-mf(y[~dtype],baseline[~dtype]),
             'Q960_606_delta':mf(y[qmask],pred[qmask])-mf(y[qmask],baseline[qmask]),
             'changed_ids':df.Id.values[pred!=baseline].astype(int).tolist()}
        out['Q960_606_vs_D']=mf(y[qmask],pred[qmask])-mf(y[qmask],df.system_D_pred.values[qmask])
        return out
    bo=group_bootstrap(y,baseline,[A,B],roots)
    result={'mission':'RS-DEFHS-SYSTEM-E-DECISION-OPTIMIZATION-001',
       'authority':{'E_primary_oof_rows':826,'E_baseline':mf(y,baseline),'original_E_test_sha256':sha(cand),'retrieval_test_fixed':78,'promotion_Q960_failed_original':True},
       'source_sha256':{'E_evidence_zip':expected['E'],'D_delivery_zip':expected['D'],'canonical_handoff_zip':expected['CAN'],
          'E_primary_oof_csv':oof_sha},
       'hypotheses':{'A':{'policy':'fold-train class prior + unlabeled fold-batch joint expected macro-F1 surrogate greedy coordinate improvement; NO heldout labels in decision; ratio-of-expectations NOT exact E[macro-F1]', 'result':collect(A),'paired_bootstrap':bo[0]},
          'B':{'policy':'fold-train Beta(1,1) per-expert-label lower 95% precision; switch E to Qwen14 only if q is E second-highest posterior and lower bound > E top confidence; NO heldout labels in decision','result':collect(B),'paired_bootstrap':bo[1]}},
       'calibration':calibration(y,P),
       'residual_oracle':{'errors':int((baseline!=y).sum()),'truth_rank2_errors':int(np.sum((baseline!=y)&(np.argsort(P,axis=1)[:,-2]==np.searchsorted(C,y)))),
          'q_correct_on_E_error':int(np.sum((baseline!=y)&(q==y))),
          'q_second_and_correct_on_E_error':int(np.sum((baseline!=y)&(q==y)&(np.argsort(P,axis=1)[:,-2]==np.searchsorted(C,y))))},
       'fold_training_contracts':fold_record,
       'VA_original_reference':{'D':mf(va.emotion.to_numpy(),va.D_pipeline.to_numpy()),'E':mf(va.emotion.to_numpy(),va.E_pipeline.to_numpy()),'candidate_VA_probabilities_available':False},
       'scope_notes':['F1 joint surrogate assumes calibration and uses single heldout unlabeled batch; not exact metric expectation',
         'B train-side semantic precision trained exclusively from training y and q, not from unsafe pooled E OOF training-side probabilities',
         'INT16/INT32 reported as VB subgroup diagnostics, not authentic frozen cross-format transfer',
         'Q960_606 must not be used to select/tune candidate after seeing it',
         'Two candidate families tested and reported together with max-t multiplicity correction; no parameter search',
         'System E frozen Q960 failure remains unaltered']}
    (HERE/'DECISION_TESTS.json').write_text(json.dumps(result,indent=2))
    pd.DataFrame({'Id':df.Id,'emotion':y,'fold':folds,'E':baseline,'A':A,'B':B,'Qwen_new':q}).to_csv(HERE/'DECISION_OOF.csv',index=False)
    for name in ['A','B']:
        h=result['hypotheses'][name]
        print(name,'score',h['result']['macro_f1'],'gain',h['result']['gain_vs_E'], 'changed',h['result']['changes'],
              'fold',np.round(h['result']['fold_deltas'],6),'CI',h['paired_bootstrap']['multiplicity_max_t_ci95'])
    print('CALIB',json.dumps({k:v for k,v in result['calibration'].items() if k!='bins'}))
    print('ORACLE',result['residual_oracle'])
    print('VALIDATION_BACKUP',json.dumps(result['VA_original_reference']))

if __name__=='__main__':main()