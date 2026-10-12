#!/usr/bin/env python3
"""One preregistered WavLM representation, strictly nested versus authentic E."""
import argparse,hashlib,json,time,warnings
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import log_loss,roc_auc_score
from threadpoolctl import threadpool_limits
import final_semantic_challenger as F
from defhs_frozen_closure_utils import Evidence,labels

L=F.CLASSES
E_SHA='a7a1e456883119c60a2d5e77dd8cad93ba384cd707d66e3e5918cab974903aff'
def idhash(x):return hashlib.sha256(np.asarray(x,dtype='<i8').tobytes()).hexdigest()
def nested_new(X,y,fold,ids):
    """Every inner prediction excludes BOTH outer and inner heldout labels."""
    n=len(y);out=np.zeros((n,4));inner={};audit=[]
    for outer in range(5):
        tr=fold!=outer;vl=~tr;inner[outer]=np.zeros((n,4))
        for block in range(5):
            if block==outer:continue
            it=tr&(fold!=block);iv=tr&(fold==block)
            assert not np.any((it|iv)&vl)
            inner[outer][iv]=F.head(X,y,it,iv)
            audit.append({'outer':outer,'inner':block,'fit_ids_sha256':idhash(ids[it]),'predict_ids_sha256':idhash(ids[iv]),'fit_n':int(it.sum()),'outer_overlap':0})
        out[vl]=F.head(X,y,tr,vl)
    return out,inner,audit

def original_arrays(X,y,fold,wave):
    arrays={}
    for outer in range(5):
        tr=fold!=outer;vl=~tr;inn=np.zeros_like(wave)
        for block in range(5):
            if block==outer:continue
            it=tr&(fold!=block);iv=tr&(fold==block)
            inn[iv]=np.column_stack([F.head(x,y,it,iv) for x in X])
        arrays[outer]=(inn,wave[vl])
    return arrays

def fuse(y,fold,arrays,sem,new_outer=None,new_inner=None):
    out=np.zeros((len(y),4))
    for k in range(5):
        tr=fold!=k;vl=~tr
        a=np.column_stack([arrays[k][0][tr],sem[tr]])
        b=np.column_stack([arrays[k][1],sem[vl]])
        if new_outer is not None:
            a=np.column_stack([a,new_inner[k][tr]]);b=np.column_stack([b,new_outer[vl]])
        m=F.lr();m.fit(a,y[tr]);assert np.array_equal(m.classes_,L)
        out[vl]=m.predict_proba(b)
    return out

def complement(y,ref,alt,ids,fold):
    r=F.transition(y,ref,alt);r['metrics']=F.metric(y,alt,fold)
    r['corrected_ids']=ids[(ref!=y)&(alt==y)].tolist();r['broken_ids']=ids[(ref==y)&(alt!=y)].tolist()
    r['corrections_by_fold']=[int(sum((ref!=y)&(alt==y)&(fold==k))) for k in range(5)]
    r['breakages_by_fold']=[int(sum((ref==y)&(alt!=y)&(fold==k))) for k in range(5)]
    return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--d-input',required=True,type=Path)
    ap.add_argument('--e-evidence',required=True,type=Path);ap.add_argument('--feature-dir',required=True,type=Path)
    ap.add_argument('--prompt-csv',required=True,type=Path);ap.add_argument('--out',required=True,type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    assert not (a.out/'PRIMARY_RESULTS.json').exists(),'Preserve existing result; no automatic rerun/search'
    start=time.monotonic();qpath=a.e_evidence/'SYSTEM_E_PRIMARY_OOF.csv';assert F.sha(qpath)==E_SHA
    e=pd.read_csv(qpath);f,X,wave,q8=F.load_inputs(a.d_input)
    ids=f.Id.to_numpy();fold=f.fold.to_numpy();y=f.emotion.to_numpy();ref=e.system_E_pred.to_numpy()
    assert np.array_equal(ids,e.Id) and np.array_equal(y,e.emotion) and np.array_equal(fold,e.fold)
    ep=e[['system_E_p_'+c for c in L]].to_numpy();assert np.array_equal(L[ep.argmax(1)],ref)
    assert abs(F.mf(y,ref)-.8774091527555827)<1e-14
    assert np.array_equal(q8,e.old_qwen8_state)
    inv=json.loads((a.feature_dir/'OUTPUT_INVENTORY.json').read_text())
    for n,v in inv.items():assert F.sha(a.feature_dir/n)==v['sha256'] and (a.feature_dir/n).stat().st_size==v['bytes']
    contract=json.loads((a.feature_dir/'CONTRACT.json').read_text());result=json.loads((a.feature_dir/'RESULT.json').read_text())
    assert contract['revision']=='50632bbc8b89cbaa45077f1404601d9776cfe387' and contract['dimension']==1024
    assert result['status']=='INFERENCE_COMPLETE_NOT_EVALUATED' and result['rows']==826
    assert all(json.loads((a.feature_dir/'FEASIBILITY.json').read_text())['gates'].values())
    z=np.load(a.feature_dir/'WAVLM_TRAIN826.npz',allow_pickle=False)
    assert np.array_equal(z['Id'],ids) and z['X'].shape==(826,1024) and np.isfinite(z['X']).all()
    manifest=pd.read_csv(F.DS/'DATA_MANIFEST.csv').set_index('Id').loc[ids]
    assert np.array_equal(z['file_sha256'],manifest.file_sha256)
    native=L[z['logits'][:,[0,2,7,1]].argmax(1)]
    sem=np.column_stack([F.onehot(e[c]) for c in ['old_qwen8_state','whisper_qwen14_state','new_asr_qwen14_state']])
    warnings.simplefilter('error',ConvergenceWarning)
    with threadpool_limits(2):
        arrays=original_arrays(X,y,fold,wave)
        replay=fuse(y,fold,arrays,sem)
        delta=float(abs(replay-ep).max());assert delta<1e-8 and np.array_equal(L[replay.argmax(1)],ref)
        newp,inn,audit=nested_new(z['X'],y,fold,ids)
        pred=L[newp.argmax(1)]
        r=complement(y,ref,pred,ids,fold);r['native_four_class_diagnostic']=complement(y,ref,native,ids,fold)
        novel=(ref!=y)&(pred==y)&(L[wave[:,:4].argmax(1)]!=y)&(L[wave[:,4:].argmax(1)]!=y)
        correct=(ref!=y)&(pred==y)
        gates={'ten_corrections':r['corrections']>=10,'five_unavailable_to_both_acoustics':sum(novel)>=5,
          'three_classes':len(set(y[correct]))>=3}
        r.update({'gates':{k:bool(v) for k,v in gates.items()},'new_correct_beyond_both_acoustics':int(sum(novel)),
          'new_correct_beyond_both_acoustics_ids':ids[novel].tolist(),'standalone_log_loss':float(log_loss(y,newp,labels=L)),
          'oracle_not_deployable':True,'E_probability_replay_max_abs':delta,
          'label_blind_confidence_correctness_auc':float(roc_auc_score(pred==y,newp.max(1)))})
        F.dump(a.out/'EXPERT_SCREEN.json',r);F.dump(a.out/'NESTED_FIT_AUDIT.json',audit)
        np.savez_compressed(a.out/'NEW_EXPERT_OOF.npz',Id=ids,fold=fold,prob=newp)
        if not all(gates.values()):
            F.dump(a.out/'PRIMARY_RESULTS.json',{'status':'REJECT_EXPERT_SCREEN','screen_gates':r['gates'],'wall_seconds':time.monotonic()-start});return
        candidate=fuse(y,fold,arrays,sem,newp,inn)
    cp=L[candidate.argmax(1)];stats=complement(y,ref,cp,ids,fold)
    F.dump(a.out/'NESTED_CACHE_MANIFEST.json',{'source_feature_sha256':F.sha(a.feature_dir/'WAVLM_TRAIN826.npz'),
      'new_acoustic_fits':25,'original_inner_acoustic_fits':40,'meta_fits':10,'outer_original_acoustic_probabilities_preserved':True})
    assert F.sha(a.prompt_csv)=='458712cfee51e0cf65ef57d1a0deb8f81dcb70e4ecfe6ebfc73220f3aefac005'
    dup=pd.read_csv(F.DS/'DUPLICATE_GROUPS_FINAL.csv');prompt=pd.read_csv(a.prompt_csv)
    ev=Evidence(ids,dup,prompt);assert len(set(ev.components))==656
    d=F.mf(y,cp)-F.mf(y,ref);draws=ev.boots(labels(y),labels(cp))-ev.boots(labels(y),labels(ref))
    interval=ev.intervals({'F_minus_E':(d,draws)})['F_minus_E']
    base=F.metric(y,ref,fold);fold_delta=np.array(stats['metrics']['fold_f1'])-base['fold_f1']
    class_delta={c:stats['metrics']['per_class'][c]['f1']-base['per_class'][c]['f1'] for c in L}
    hard=e.hard316.to_numpy();assert hard.sum()==316 and np.array_equal(hard,F.hard_mask(wave))
    dup_single=f.duplicate_group.map(f.duplicate_group.value_counts()).to_numpy()==1
    pg=prompt.set_index('Id').loc[ids,'prompt_sim_0.90'];prompt_single=pg.map(pg.value_counts()).to_numpy()==1
    masks={'HARD316':hard,'duplicate_singleton':dup_single,'prompt_singleton':prompt_single,
      'waveform_disagree':wave[:,:4].argmax(1)!=wave[:,4:].argmax(1),'int16':manifest.dtype.eq('int16').to_numpy(),'int32':manifest.dtype.eq('int32').to_numpy()}
    for mod,values in [(128,[0,43,86,30,94]),(960,[384,192,576,606,926])]:
        v=manifest.samples.to_numpy()%mod
        for k in values:masks[f'Q{mod}_{k}']=v==k
        masks[f'Q{mod}_OTHER']=~np.isin(v,values)
    cohorts={}
    for name,m in masks.items():
        point,boot=ev.contrast(labels(y),labels(cp),labels(ref),m)
        cohorts[name]={'n':int(sum(m)),'E':F.metric(y[m],ref[m]),'candidate':F.metric(y[m],cp[m]),'delta':point,
          'transitions':F.transition(y[m],ref[m],cp[m]),'component_percentile_95':np.quantile(boot,[.025,.975]).tolist()}
    leave=[F.mf(y[fold!=k],cp[fold!=k])-F.mf(y[fold!=k],ref[fold!=k]) for k in range(5)]
    gates={'gain_ge_005':d>=.005,'four_positive_folds':sum(fold_delta>0)>=4,'no_class_loss_gt_02':min(class_delta.values())>=-.02,
      'HARD_nonnegative':cohorts['HARD316']['delta']>=0,'delete_fold_positive':min(leave)>0,'component_max_t_lower_positive':interval['lower']>0,
      'duplicate_singleton_nonnegative':cohorts['duplicate_singleton']['delta']>=0,'prompt_singleton_nonnegative':cohorts['prompt_singleton']['delta']>=0}
    stats.update({'status':'PRIMARY_PASS_PENDING_NEW_STRESS' if all(gates.values()) else 'REJECT_PRIMARY',
      'baseline_E':base,'gain':d,'fold_deltas':fold_delta.tolist(),'class_deltas':class_delta,'leave_one_fold_out':leave,
      'paired_component_max_t_95':interval,'paired_component_percentile_95':np.quantile(draws,[.025,.975]).tolist(),
      'cohorts':cohorts,'gates':{k:bool(v) for k,v in gates.items()},'E_probability_replay_max_abs':delta,
      'E_log_loss':float(log_loss(y,ep,labels=L)),'candidate_log_loss':float(log_loss(y,candidate,labels=L)),
      'wall_seconds':time.monotonic()-start,'gpu_hours':0,'protected_validation_accessed':False,'target209_inferred':False,
      'selection_caution':'One predeclared candidate after adaptive historical research and an oracle screen. CI is conditional, not a fresh independent confirmation.'})
    output=e[['Id','emotion','fold','system_D_pred','system_E_pred','hard316']].copy()
    output['new_expert_pred']=pred;output['candidate_pred']=cp;output['component']=ev.components
    for i,c in enumerate(L):output['candidate_p_'+c]=candidate[:,i];output['new_expert_p_'+c]=newp[:,i]
    output.to_csv(a.out/'CANDIDATE_PRIMARY_OOF.csv',index=False,float_format='%.17g')
    output[cp!=ref].to_csv(a.out/'CHANGED_DECISIONS.csv',index=False,float_format='%.17g')
    F.dump(a.out/'PRIMARY_RESULTS.json',stats)
    print(json.dumps({k:stats[k] for k in ['status','gain','fold_deltas','gates','paired_component_max_t_95','corrections','breakages']}),flush=True)

if __name__=='__main__':main()
