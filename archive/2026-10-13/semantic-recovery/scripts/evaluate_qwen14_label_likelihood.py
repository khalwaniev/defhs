#!/usr/bin/env python3
"""One preregistered 28-feature System E + semantic likelihood nested OOF gate.

REQUIRED: authenticated System D production ZIP, E evidence ZIP, new Q14
semantic ZIP, likelihood CSV and original connected roots archive. Strictly no
protected labels or TARGET209. No tuning, sweep, alternative gates or submission.
"""
import argparse,csv,hashlib,io,json,runpy,sys,tempfile,warnings,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits
D_SHA='fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839'
NEW_SEM_SHA='cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789'
NEW_CSV_SHA='8edd8dc9899f9304db2b46475758a67330f82c3c1348317646b561f3d57f6377'
E_PRIMARY_OOF_SHA='a7a1e456883119c60a2d5e77dd8cad93ba384cd707d66e3e5918cab974903aff'
E_SCORE=.8774091527555827
CLASSES=np.array(['angry','happy','neutral','sad']);STATES=np.array(['angry','happy','neutral','sad','unclear'])

def sha(b):return hashlib.sha256(b).hexdigest()
def file_sha(p):return sha(Path(p).read_bytes())
def member(z,name):
    matches=[p for p in z.namelist() if p.split('/')[-1]==name]
    assert len(matches)==1,(name,matches)
    return z.read(matches[0])

def roots_from_zip(path):
    with zipfile.ZipFile(path) as z:
        b=member(z,'component_roots.b36')
    s=b.decode().strip().replace('\n','');assert len(s)==1652
    roots=np.array([int(s[j:j+2],36) for j in range(0,len(s),2)])
    assert roots.sum()==351348 and len(set(roots))==656
    return roots

def main():
    ap=argparse.ArgumentParser()
    for key in ['d_zip','e_zip','semantic_zip','likelihood_csv','roots_zip']:
        ap.add_argument('--'+key.replace('_','-'),type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,default=Path('work/defhs_likelihood_evaluation'))
    a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    assert file_sha(a.d_zip)==D_SHA,'Wrong System D production ZIP'
    assert file_sha(a.semantic_zip)==NEW_SEM_SHA,'Wrong new Q14 semantic archive'
    roots=roots_from_zip(a.roots_zip)
    with zipfile.ZipFile(a.semantic_zip) as z:
        assert z.testzip() is None
        raw=member(z,'QWEN14B_TRAIN826.csv')
        assert sha(raw)==NEW_CSV_SHA
        hard=pd.read_csv(io.BytesIO(raw)).set_index('Id')
    with zipfile.ZipFile(a.e_zip) as z:
        assert z.testzip() is None
        ev=json.loads(member(z,'SYSTEM_E_EVIDENCE_MANIFEST.json'))
        for name,desc in ev['files'].items():
            assert sha(member(z,name))==desc['sha256'],name
        oof_bytes=member(z,'SYSTEM_E_PRIMARY_OOF.csv')
        assert sha(oof_bytes)==E_PRIMARY_OOF_SHA
        e_oof=pd.read_csv(io.BytesIO(oof_bytes)).sort_values('Id').reset_index(drop=True)
        fusion=member(z,'replay_fusion.py')
    likelihood=pd.read_csv(a.likelihood_csv).set_index('Id')
    assert len(likelihood)==826 and likelihood.index.is_unique
    required=['greedy','reference_hard']+['trie_p_'+x for x in STATES]
    assert all(x in likelihood for x in required)
    ids=e_oof.Id.to_numpy();y=e_oof.emotion.to_numpy();fold=e_oof.fold.to_numpy()
    assert set(likelihood.index)==set(hard.index)==set(ids)
    likelihood=likelihood.loc[ids]; hard=hard.loc[ids]
    assert np.array_equal(likelihood.greedy.to_numpy(),likelihood.reference_hard.to_numpy())
    assert np.array_equal(likelihood.greedy.to_numpy(),hard.semantic_label.to_numpy())
    assert np.array_equal(likelihood.greedy.to_numpy(),e_oof.new_asr_qwen14_state.to_numpy())
    P=likelihood[['trie_p_'+x for x in STATES]].to_numpy(dtype='float64')
    assert np.isfinite(P).all() and (P>=0).all() and (P<=1).all()
    assert np.max(np.abs(P.sum(axis=1)-1))<5e-5
    with tempfile.TemporaryDirectory(prefix='defhs_nested_') as td:
        base=Path(td)
        with zipfile.ZipFile(a.d_zip) as z:
            assert z.testzip() is None
            z.extractall(base)
        fpath=base/'verified_replay_fusion.py';fpath.write_bytes(fusion)
        F=runpy.run_path(str(fpath),run_name='defhs_frozen_functions')
        for name,expected in F['HASHES'].items():
            if name=='PROMPT_CLUSTER_ASSIGNMENTS.csv': continue  # Dependency roots are separately verified.
            candidates=list(base.rglob(name));assert len(candidates)==1,(name,candidates)
            assert file_sha(candidates[0])==expected,name
        def unique(name):
            hits=list(base.rglob(name));assert len(hits)==1,(name,hits)
            return hits[0]
        ids_source=np.load(unique('FIXED_PAIR_VB.npz'),allow_pickle=False)['Id'].astype(int)
        assert np.array_equal(ids,ids_source)
        old8=pd.read_csv(unique('QWEN_SEMANTIC_OUTPUTS.csv')).set_index('Id').loc[ids].semantic_label.to_numpy()
        with zipfile.ZipFile(unique('DEFHS_Qwen14B_train826_outputs.zip')) as z:
            old14=pd.read_csv(io.BytesIO(member(z,'QWEN14B_TRAIN826.csv'))).set_index('Id').loc[ids].semantic_label.to_numpy()
        wave=np.column_stack([np.load(unique('E2V_CONTROL_VB.npz'))['prob'],
                              np.load(unique('XLSR_VB.npz'))['prob']])
        assert len(wave)==826
        features=[]
        for name in ['emotion2vec_base_meanstd.npz','xls_r_300m_meanstd.npz']:
            z=np.load(unique(name),allow_pickle=False)
            index={int(val):j for j,val in enumerate(z['Id'])}
            features.append(z['X'][[index[int(k)] for k in ids]])
        hard316=F['hard_mask'](wave)
        assert hard316.sum()==316 and np.array_equal(hard316,e_oof.hard316.to_numpy())
        old_sem=np.column_stack([F['onehot'](old8),F['onehot'](old14),F['onehot'](hard.semantic_label)])
        full_sem=np.column_stack([old_sem,P])
        warnings.simplefilter('error',ConvergenceWarning)
        with threadpool_limits(limits=2):
            arrays=F['build_inner'](fold,features,y,wave)
            pE=F['fuse'](y,fold,arrays,old_sem)
            refP=e_oof[['system_E_p_'+c for c in CLASSES]].to_numpy()
            parity=float(np.max(np.abs(pE-refP)))
            assert parity<1e-8,('System E true nested OOF parity FAILED',parity)
            assert abs(F['mf'](y,CLASSES[np.argmax(pE,axis=1)])-E_SCORE)<1e-12
            pNew=F['fuse'](y,fold,arrays,full_sem)
    aPred=CLASSES[pE.argmax(axis=1)];bPred=CLASSES[pNew.argmax(axis=1)]
    A=F['metric'](y,aPred,fold);B=F['metric'](y,bPred,fold)
    delta=float(B['macro_f1']-A['macro_f1'])
    fold_deltas=[float(B['fold_f1'][i]-A['fold_f1'][i]) for i in range(5)]
    class_deltas={k:float(B['per_class'][k]['f1']-A['per_class'][k]['f1']) for k in CLASSES}
    hard_delta=float(F['mf'](y[hard316],bPred[hard316])-F['mf'](y[hard316],aPred[hard316]))
    leave=[float(F['mf'](y[fold!=i],bPred[fold!=i])-F['mf'](y[fold!=i],aPred[fold!=i]))for i in range(5)]
    components=sorted(set(roots));ci={r:i for i,r in enumerate(components)}
    weights=np.random.Generator(np.random.PCG64(20260930)).exponential(1,(2000,len(components)))[:,[ci[r] for r in roots]]
    indexes={c:j for j,c in enumerate(CLASSES)}
    yv=np.array([indexes[x] for x in y]); av=np.array([indexes[x] for x in aPred]); bv=np.array([indexes[x] for x in bPred])
    def boot_f1(pred):
        matrix=np.stack([weights[:,(yv==k)&(pred==j)].sum(axis=1) for k in range(4) for j in range(4)],axis=1).reshape(-1,4,4)
        den=matrix.sum(axis=1)+matrix.sum(axis=2)
        return np.divide(2*np.diagonal(matrix,axis1=1,axis2=2),den,out=np.zeros_like(den),where=den>0).mean(1)
    draws=boot_f1(bv)-boot_f1(av)
    sd=float(np.std(draws,ddof=1))
    q=float(np.quantile(np.abs((draws-delta)/sd),.95,method='higher')) if sd>0 else float('inf')
    ci=[float(delta-q*sd),float(delta+q*sd)]
    gates={'gain_ge_0_005':delta>=.005,
       'at_least_4_positive_folds':sum(v>0 for v in fold_deltas)>=4,
       'no_per_class_loss_gt_0_02':min(class_deltas.values())>=-.02,
       'hard316_nonnegative':hard_delta>=0,
       'leave_one_fold_positive':min(leave)>0,
       'dependency_bootstrap_lower_positive':ci[0]>0}
    rows=[]
    for i,k in enumerate(ids):
        item={'Id':int(k),'emotion':str(y[i]),'fold':int(fold[i]),'system_E_pred':str(aPred[i]),'challenger_pred':str(bPred[i]),'hard316':bool(hard316[i])}
        for j,c in enumerate(CLASSES):
            item['E_p_'+c]=float(pE[i,j]);item['challenger_p_'+c]=float(pNew[i,j])
        rows.append(item)
    pd.DataFrame(rows).to_csv(a.output_dir/'CHALLENGER_PRIMARY_OOF.csv',index=False,float_format='%.17g')
    report={'mission':'RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001',
        'status':'PRIMARY_PASS_PENDING_STRESS' if all(gates.values()) else 'STOP_PRIMARY_GATE_FAILED',
        'source':'E authentic fixed nested 23 features + 5 frozen constrained likelihoods, L2 C=1',
        'baseline_macroF1':A['macro_f1'],'challenger_macroF1':B['macro_f1'],
        'delta':delta,'fold_deltas':fold_deltas,'class_deltas':class_deltas,
        'hard316_delta':hard_delta,'leave_fold_deltas':leave,
        'paired_changes':F['transition'](y,aPred,bPred),
        'per_class_baseline':A['per_class'],'per_class_challenger':B['per_class'],
        'ci95_max_t':ci,'bootstrap_components':len(components),'bootstrap_draws':len(draws),
        'gates':gates,'baseline_probability_parity_max_abs':parity,
        'hard_semantic_state_parity':True,'retrieval_map_unchanged':True,
        'no_protected_access':True,'target209_not_inferred':True,'submitted':False}
    (a.output_dir/'PRIMARY_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if not all(gates.values()):print('STOP: do not run TARGET209, do not tune fusion, report to SS',flush=True)
    else: print('PRIMARY PASS ONLY: required frozen V-A/dtype/Q960/private allocation stress before production',flush=True)

if __name__=='__main__':main()
