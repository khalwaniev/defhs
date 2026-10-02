#!/usr/bin/env python3
"""Audit complete GPU OOF, registered marginal blends, and survivor entry."""
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.metrics import f1_score,confusion_matrix
from defhs_frozen_closure_utils import CLASSES,labels,f1,report,dump,sha256
from system3_wave1_cpu import ROOT,RUN,WORK,inputs,idhash
from run_score_push_cpu import views
from system3_wave1_verify_outputs import verify

def delta(p,base,folds,masks):
    r=views(p,folds,masks,base)
    for v,f in folds.items():
        y=labels(f.emotion);a=p[v].argmax(1);b=base[v].argmax(1);fs=f.fold.to_numpy()
        r[v]['aggregate_delta']=f1(y,a)-f1(y,b)
        r[v]['fold_deltas']=[f1(y[fs==k],a[fs==k])-f1(y[fs==k],b[fs==k]) for k in range(5)]
        r[v]['delete_fold_deltas']=[f1(y[fs!=k],a[fs!=k])-f1(y[fs!=k],b[fs!=k]) for k in range(5)]
        r[v]['corrections']=int(((a==y)&(b!=y)).sum());r[v]['breakages']=int(((a!=y)&(b==y)).sum())
        r[v]['class_deltas']=dict(zip(CLASSES,f1(y,a,per_class=True)-f1(y,b,per_class=True)))
        assert abs(f1_score(f.emotion,CLASSES[a],labels=CLASSES,average='macro')-r[v]['macro_f1'])<1e-14
        assert np.array_equal(confusion_matrix(f.emotion,CLASSES[a],labels=CLASSES),r[v]['confusion'])
    return r

def load_gpu(folder,lane,view,seed,folds,adapted_only=False):
    f=folds[view];q={arm:np.zeros((826,4)) for arm in ([lane+'1'] if adapted_only else [lane+'0',lane+'1'])};records=[]
    root=folder/f'{lane}_{view}_seed{seed}'
    for outer in range(5):
        H=f.fold.to_numpy()==outer;S=~H;g=(outer+1)%5;stop=S&(f.fold.to_numpy()==g);pilot=S&~stop
        for arm in q:
            meta=json.loads((root/f'{arm}_fold{outer}_RESULT.json').read_text())
            npz=root/f'{arm}_fold{outer}_OOF.npz';assert sha256(npz)==meta['prediction_sha256']
            z=np.load(npz);assert np.array_equal(z['Id'],f.Id[H]);q[arm][H]=z['prob']
            assert meta['prediction_ID_sha256']==idhash(f.Id[H])
            for kind,training,stopping in [('pilot',pilot,stop),('refit',S,np.zeros(826,bool))]:
                rec=meta[kind];fp=rec['fingerprint']
                assert fp['recipe_sha256']==sha256(RUN/'WAVE1_CONFIG.json')
                assert fp['training_ID_sha256']==idhash(f.Id[training]) and fp['stopping_ID_sha256']==idhash(f.Id[stopping])
                assert fp['view']==view and fp['seed']==seed and fp['fold']==outer
                assert not np.any(H&training) and not np.any(H&stopping)
                saved=json.loads((root/f'{arm}_fold{outer}_{kind}_DONE.json').read_text())
                assert saved==rec
                assert sha256(root/f'{arm}_fold{outer}_{kind}_STATE.pt')==rec['checkpoint_sha256']
                # Reconstruct the precommitted shuffle, without changing the
                # completed fit or its checkpoint. Record actually optimized
                # IDs as well as the full assigned training-set fingerprint.
                assigned=np.flatnonzero(training);used=(len(assigned)//16)*16
                schedule=[]
                for trace in rec['traces']:
                    epoch=trace['epoch']
                    order=np.random.default_rng(seed+outer*10000+epoch).permutation(assigned)
                    assert trace['training_clips']==used
                    assert trace['dropped_tail_clips']==len(assigned)-used
                    schedule.append({'epoch':epoch,'optimized_ID_sha256':idhash(f.Id.iloc[order[:used]]),
                        'dropped_tail_IDs':f.Id.iloc[order[used:]].tolist(),
                        'dropped_tail_ID_sha256':idhash(f.Id.iloc[order[used:]])})
                rec['reconstructed_training_schedule']=schedule
                if kind=='refit':assert rec['selected_epoch']==meta['selected_epoch']
            assert meta['pilot']['selected_epoch']==meta['selected_epoch']
            records.append(meta)
    for arm in q:assert np.isfinite(q[arm]).all() and np.allclose(q[arm].sum(1),1,atol=1e-6)
    return q,records

def convention(r,threshold):
    v=r['VB'];return bool(v['aggregate_delta']>=threshold and sum(x>0 for x in v['fold_deltas'])>=4 and min(v['delete_fold_deltas'])>=0 and v['strata']['CLEAN']['delta_vs_control']>=0)

def main():
    a=argparse.ArgumentParser();a.add_argument('folder',type=Path);a.add_argument('--view',default='VB',choices=['VB','VA']);a.add_argument('--seed',type=int,default=20260930);a.add_argument('--lanes',default='AB');args=a.parse_args()
    package_integrity=verify(args.folder)
    allfolds,allmasks,control,x=inputs();folds={args.view:allfolds[args.view]};masks={args.view:allmasks[args.view]}
    baseline={args.view:control[args.view]};P={args.view:np.load(WORK/f'FIXED_PAIR_{args.view}.npz')['prob']}
    measurements={};blends={};probs={};inventory=[]
    for lane in args.lanes:
        qq,records=load_gpu(args.folder,lane,args.view,args.seed,allfolds,adapted_only=args.seed==20260917)
        for arm,p in qq.items():
            probs[arm]={args.view:p}
            path=WORK/f'{arm}_{args.view}_seed{args.seed}.npz';np.savez_compressed(path,Id=folds[args.view].Id.to_numpy(),prob=p)
            inventory.append({'name':path.name,'sha256':sha256(path),'local_path':str(path),'bytes':path.stat().st_size})
        if args.seed==20260917:
            qq[lane+'0']=np.load(WORK/f'{lane}0_{args.view}_seed20260930.npz')['prob']
        matched={args.view:qq[lane+'0']};adapted={args.view:qq[lane+'1']}
        measured=delta(adapted,matched,folds,masks);frozen=delta(matched,baseline,folds,masks)
        blend={args.view:(2*P[args.view]+qq[lane+'1'])/3};result=delta(blend,P,folds,masks)
        path=WORK/f'Candidate_{lane}_{args.view}_seed{args.seed}.npz';np.savez_compressed(path,Id=folds[args.view].Id.to_numpy(),prob=blend[args.view])
        inventory.append({'name':path.name,'sha256':sha256(path),'local_path':str(path),'bytes':path.stat().st_size})
        all_epoch0=all(r['selected_epoch']==0 for r in records if r['arm']==lane+'1')
        encoder_update_retained=any(r['selected_epoch']>=3 for r in records if r['arm']==lane+'1')
        measurements[lane]={'status':'COMPLETE','view':args.view,'seed':args.seed,'matched_frozen':frozen,'adapted_vs_matched_frozen':measured,
           'package_integrity':package_integrity,
           'fold_records':records,'all_adapted_epoch_zero':all_epoch0,'encoder_update_retained':encoder_update_retained,'outer_ID_hash_audit':'PASS','independent_sklearn_metric_audit':'PASS',
           'recipe':json.loads((RUN/'WAVE1_CONFIG.json').read_text())[lane],
           'optimization_seconds':sum(r[k]['wall_seconds'] for r in records for k in ['pilot','refit']),
           'peak_gpu_memory_bytes':max(r[k]['peak_GPU_memory_bytes'] for r in records for k in ['pilot','refit'])}
        blends[lane]={'definition':f'2/3 fixed P + 1/3 {lane}1','reference':'fixed 50/50 original E2V + XLSR','results':result}
        if args.view=='VB':
            marginal=convention(result,.005);standalone=measured['VB']['aggregate_delta']>=.010 and measured['VB']['strata']['CLEAN']['delta_vs_control']>=0
            measurements[lane]['provisional_useful']=bool(standalone or marginal)
            measurements[lane]['entry_reason']={'standalone_ge010_and_CLEAN':bool(standalone),'blend_conventions':marginal,'encoder_update_retained':encoder_update_retained}
        else:
            for name,p,reference in [('frozen',matched,baseline),('adapted',adapted,baseline),('fixed_blend',blend,P)]:
                audit=pd.read_csv(ROOT/'runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001/FINALIST_VA_RETRIEVAL_AUDIT.csv').set_index('Id').loc[folds['VA'].Id]
                covered=audit.retrieval_covered.to_numpy(bool);pred=p['VA'].argmax(1).copy();pred[covered]=labels(audit.pipeline_pred)[covered]
                measurements[lane].setdefault('retrieval_aware',{})[name]={**report(labels(folds['VA'].emotion),pred,folds['VA'].fold.to_numpy()),'frozen_coverage_rows':int(covered.sum())}
    if args.view=='VB' and args.seed==20260930:
        for lane,r in measurements.items():dump(RUN/('W1_E2V_ADAPTATION_RESULTS.json' if lane=='A' else 'W1_AST_RESULTS.json'),r)
        dump(RUN/'W1_FIXED_BLEND_RESULTS.json',{'status':'COMPLETE_VB','arms':blends,'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()})
        dump(RUN/'W1_SECONDARY_CONFIRMATION.json',{'status':'ENTRY_DECIDED','provisionally_useful_survivors':[lane for lane,r in measurements.items() if r['provisional_useful']],
            'entry':'Only actual adapted survivors under registered VB conventions; VA and leading-seed2 still pending if any'})
    else:
        payload={'measurements':measurements,'fixed_blends':blends}
        if args.seed==20260917:
            payload['matched_reference_note']='Frozen arm is seed1; no extra frozen-arm seed2 experiment. Stability measures compare seed1, seed2 and their arithmetic probability average.'
            means={}
            for lane in args.lanes:
                s1=np.load(WORK/f'{lane}1_{args.view}_seed20260930.npz')['prob'];s2=probs[lane+'1'][args.view]
                mean=(s1+s2)/2;blend=(2*P[args.view]+mean)/3
                means[lane]={'seed1_vs_pair':delta({args.view:s1},P,folds,masks),'seed2_vs_pair':delta({args.view:s2},P,folds,masks),
                   'mean_probability_vs_pair':delta({args.view:mean},P,folds,masks),'fixed_blend_mean_vs_pair':delta({args.view:blend},P,folds,masks)}
                for name,p in [(lane+'1_SEED_MEAN',mean),('Candidate_'+lane+'_SEED_MEAN',blend)]:
                    path=WORK/f'{name}_{args.view}.npz';np.savez_compressed(path,Id=folds[args.view].Id.to_numpy(),prob=p)
                    inventory.append({'name':path.name,'sha256':sha256(path),'local_path':str(path),'bytes':path.stat().st_size})
            payload['seed_stability']=means
        target=RUN/f'W1_CONFIRMATION_{args.view}_seed{args.seed}.json'
        if target.exists():
            previous=json.loads(target.read_text())
            for key in ['measurements','fixed_blends','seed_stability']:
                payload[key]={**previous.get(key,{}),**payload.get(key,{})}
        dump(target,payload)
    existing=json.loads((RUN/'PROBABILITY_ARTIFACT_INVENTORY.json').read_text());existing['artifacts']+=inventory;dump(RUN/'PROBABILITY_ARTIFACT_INVENTORY.json',existing)
    print(json.dumps({'measurements':{k:{'matched':r['matched_frozen'][args.view]['macro_f1'],'adapted':r['adapted_vs_matched_frozen'][args.view]['macro_f1'],
        'useful':r.get('provisional_useful'),'epochs':[m['selected_epoch'] for m in r['fold_records'] if m['arm']==k+'1']} for k,r in measurements.items()},
        'fixed_blends':{k:r['results'][args.view]['macro_f1'] for k,r in blends.items()}},indent=2))
if __name__=='__main__':main()
