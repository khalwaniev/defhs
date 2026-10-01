#!/usr/bin/env python3
"""Close frozen membership, RS2 gate and bounded offsets using cached OOF only."""
from __future__ import annotations
import itertools,json,time
from pathlib import Path
import numpy as np,pandas as pd
from defhs_frozen_closure_utils import *
from run_rs_defhs_frozen_closure import RUN,DS,V3,OUT,INPUT,load_contract,get_lanes

def weighted_auc(score,y,positive,mult):
    # Sorted tie groups implement half-credit ties for arbitrary row weights.
    ix=np.argsort(score,kind='stable');s=score[ix];pos=(y[ix]==positive)
    starts=np.r_[0,np.flatnonzero(s[1:]!=s[:-1])+1]
    wp=np.add.reduceat(mult[:,ix]*pos,starts,axis=1)
    wn=np.add.reduceat(mult[:,ix]*(~pos),starts,axis=1)
    num=(wp*(np.cumsum(wn,axis=1)-.5*wn)).sum(1)
    return num/(wp.sum(1)*wn.sum(1))

def auc_evidence(ev,y,score,a,b,mask):
    m=mask & ((y==a)|(y==b))
    if len(np.unique(y[m]))!=2:return None
    point=float(weighted_auc(score[m],y[m],a,np.ones((1,int(m.sum()))))[0])
    boot=weighted_auc(score[m],y[m],a,ev.mult[:,m])
    return point,boot

def frozen_candidates(folds,ev):
    s4=json.loads((RUN/'STAGE4_RESULTS.json').read_text());s6=json.loads((RUN/'STAGE6_RESULTS.json').read_text())
    lanes=get_lanes(folds);parent='emotion2vec_base_L2_LOGREG'
    if s6['decision']=='PROMOTE_ATTENTION_STATS':
        for v,f in folds.items():lanes[v][parent]=valid_oof(OUT/f'OOF_ATTENTION_STATS_{v}.csv',f)
    names=sorted(lanes['VB']);subsets=[s for n in range(1,4) for s in itertools.combinations(names,n)]
    systems={v:{} for v in folds};details={v:{} for v in folds};members={};deletions={}
    for v,f in folds.items():
        y=labels(f.emotion);fs=f.fold.to_numpy()
        eg=valid_oof(OUT/f'OOF_EGEMAPS_{v}.csv',f)
        for s in subsets:
            key='+'.join(s)
            if len(s)==1:q=lanes[v][s[0]];r={'heldout':report(y,q.argmax(1),fs),'equal':report(y,q.argmax(1),fs),'selections':[]}
            else:q,r=choose_probability_blend([lanes[v][n] for n in s],y,fs,ev)
            systems[v][key]=q;details[v][key]=r;members[key]=s
        # eGeMAPS remains the pre-existing low-weight conditional adjunct. It
        # never enters an unconstrained equal-weight three-member search.
        for s in subsets:
            if len(s)>2:continue
            key='+'.join(s);ekey=key+'+EGEMAPS_CONDITIONAL'
            q,r=choose_probability_blend([systems[v][key],eg],y,fs,ev,allowed=[(1.,0.),(.75,.25)],equal_weights=[1.,0.])
            systems[v][ekey]=q;details[v][ekey]=r;members[ekey]=(*s,'EGEMAPS_CONDITIONAL')
        systems[v]['EGEMAPS_ABLATION_ONLY']=eg;details[v]['EGEMAPS_ABLATION_ONLY']={'heldout':report(y,eg.argmax(1),fs)}
    for key,s in members.items():
        if len(s)<2:continue
        for n in s:
            rem=tuple(x for x in s if x!=n)
            if rem==('EGEMAPS_CONDITIONAL',):minus='EGEMAPS_ABLATION_ONLY'
            elif 'EGEMAPS_CONDITIONAL' in rem:minus='+'.join(x for x in rem if x!='EGEMAPS_CONDITIONAL')+'+EGEMAPS_CONDITIONAL'
            else:minus='+'.join(rem)
            deletions[(key,n)]=minus
    contrasts={};specs={}
    # Every member deletion and candidate vs prospective-parent/E0 comparison
    # is enumerated before computing any uncertainty estimate.
    e0=parent+'+EGEMAPS_CONDITIONAL' if 'EGEMAPS_L2_LOGREG' in s4['selected_E0_members'] else parent
    pairs=set(deletions.values()); comparisons={(k,b) for (k,n),b in deletions.items()}|{(k,b) for k in members for b in [parent,e0] if k!=b}
    for k,b in sorted(comparisons):
        for v,mask,name in [('VB',None,'full'),('VB',ev.clean,'clean'),('VA',ev.nonret,'nonretrieval')]:
            c=f'{v}:{name}:{k} - {b}';specs[c]=(v,mask,k,b)
            contrasts[c]=ev.contrast(labels(folds[v].emotion),systems[v][k].argmax(1),systems[v][b].argmax(1),mask)
    ci=ev.intervals(contrasts);checks={}
    for c,(v,m,k,b) in specs.items():
        checks[c]=robust(labels(folds[v].emotion),systems[v][k].argmax(1),systems[v][b].argmax(1),folds[v].fold.to_numpy(),ci[c]) if m is None else ci[c]
    qualified=[parent]
    for k,s in members.items():
        if len(s)<2 or parent not in s:continue
        good=True
        for n in s:
            b=deletions[(k,n)]
            good &= checks[f'VB:full:{k} - {b}']['pass'] and ci[f'VB:clean:{k} - {b}']['point']>0 and ci[f'VA:nonretrieval:{k} - {b}']['upper']>=0
        if good:qualified.append(k)
    # Smallest qualified system; no third member without credible deletion value.
    selected=min(qualified,key=lambda k:(-details['VB'][k]['heldout']['macro_f1'],len(members[k]),k))
    # If a smaller qualified candidate is not credibly worse than the winner,
    # its measured marginal is neutral and it is preferred. These comparisons
    # are precisely its member deletions, already registered above.
    changed=True
    while changed:
        changed=False
        for n in members[selected]:
            b=deletions.get((selected,n))
            if b in qualified and not checks[f'VB:full:{selected} - {b}']['pass']:
                selected=b;changed=True;break
    for v,f in folds.items():save_oof(OUT/f'OOF_FINAL_FROZEN_{v}.csv',f,systems[v][selected])
    dump(RUN/'FROZEN_MEMBERSHIP_CLOSURE.json',{'systems':details,'members':members,'deletions':{k+' minus '+n:b for (k,n),b in deletions.items()},
        'contrast_registry':list(contrasts),'contrasts':checks,'selected_id':selected,'selected_members':members[selected],
        'qualified':qualified,'prospective_parent':parent,'policy_limitation':'Conditional OOF uncertainty and reused meta-folds are not an independent test.'})
    return systems,details,members,deletions,selected,parent

def gate_and_offsets(folds,ev,clean,nonret,legacy,systems,members,deletions,selected,parent):
    y=labels(folds['VB'].emotion);fs=folds['VB'].fold.to_numpy();contrasts={};record={};offsets={};meta={};heads={}
    s6=json.loads((RUN/'STAGE6_RESULTS.json').read_text())
    # Closed registry of actual parent realizations; an absent scalar mixture is
    # UNKNOWN, never represented by a fabricated probability matrix.
    for v,f in folds.items():
        p=valid_oof(V3/f'OOF_emotion2vec_base_{v}.csv',f,'L2_LOGREG')
        rb=valid_oof(V3/f'OOF_emotion2vec_base_{v}.csv',f,'RBF_SVM_CAL')
        att=valid_oof(OUT/f'OOF_ATTENTION_STATS_{v}.csv',f)
        heads[v]={'L2_LOGREG':p,'RBF_SVM_CAL':rb,'ATTENTION_STATS':att}
        if s6['decision']=='PROMOTE_ATTENTION_STATS':p=att
        e=systems[v][selected];yi=labels(f.emotion);mask=None if v=='VB' else nonret
        for name,q in [('P',p),('E',e)]:
            op,sel=choose_offsets(q,yi,f.fold.to_numpy(),ev);offsets[(v,name)]=op;meta[(v,name)]=sel
            contrasts[f'{v}:offset_{name}-{name}']=ev.contrast(yi,op,q.argmax(1),mask)
        old=legacy[(legacy.model=='FULL_RBF_SVM')&(legacy.validation==v)].set_index('Id').loc[f.Id]
        contrasts[f'{v}:P-REFERENCE']=ev.contrast(yi,p.argmax(1),labels(old.ser_pred),mask)
        for name,q in heads[v].items():
            contrasts[f'{v}:{name}-P']=ev.contrast(yi,q.argmax(1),p.argmax(1),mask)
            # Rerun the identical conditional blending comparator. Final E is
            # currently the actual closed membership; any head swap preserves
            # all other frozen lanes and the inherited selectors.
            rem=[n for n in members[selected] if n!=parent]
            if rem==['EGEMAPS_CONDITIONAL']:
                eg=valid_oof(OUT/f'OOF_EGEMAPS_{v}.csv',f)
                eq,_=choose_probability_blend([q,eg],yi,f.fold.to_numpy(),ev,allowed=[(1.,0.),(.75,.25)],equal_weights=[1.,0.])
            elif not rem:eq=q
            else:
                lane=get_lanes(folds)[v];audio=[q]+[lane[n] for n in rem if n!='EGEMAPS_CONDITIONAL']
                eq,_=choose_probability_blend(audio,yi,f.fold.to_numpy(),ev)
                if 'EGEMAPS_CONDITIONAL' in rem:
                    eg=valid_oof(OUT/f'OOF_EGEMAPS_{v}.csv',f)
                    eq,_=choose_probability_blend([eq,eg],yi,f.fold.to_numpy(),ev,allowed=[(1.,0.),(.75,.25)],equal_weights=[1.,0.])
            contrasts[f'{v}:E_{name}-E']=ev.contrast(yi,eq.argmax(1),e.argmax(1),mask)
        if len(members[selected])>1:
            minus=deletions[(selected,parent)]
            contrasts[f'{v}:E-P_ABLATION']=ev.contrast(yi,e.argmax(1),systems[v][minus].argmax(1),mask)
        record[v]={'P':p,'E':e}
    witness={}; all_masks={v:{'full':np.ones(826,bool),'clean':clean} if v=='VB' else {'nonretrieval':nonret} for v in folds}
    # Six pairs, both existing XLS-R heads. A head is a realization of the same
    # family, never an independent new representation witness.
    for wh in ['L2_LOGREG','RBF_SVM_CAL']:
        for a,b in itertools.combinations(range(4),2):
            key=f'{CLASSES[a]}|{CLASSES[b]}|xls_r_300m|{wh}';wr={}
            for v,f in folds.items():
                yi=labels(f.emotion);p,e=record[v]['P'],record[v]['E'];w=valid_oof(V3/f'OOF_xls_r_300m_{v}.csv',f,wh)
                ps=np.log(np.clip(p[:,a],1e-12,1))-np.log(np.clip(p[:,b],1e-12,1));ws=np.log(np.clip(w[:,a],1e-12,1))-np.log(np.clip(w[:,b],1e-12,1))
                wrong_pair=((yi==a)&(p.argmax(1)==b)&(e.argmax(1)==b))|((yi==b)&(p.argmax(1)==a)&(e.argmax(1)==a))
                s=clean & wrong_pair & (w.argmax(1)==yi)
                for q in heads[v].values():s &= q.argmax(1)!=yi
                if v=='VA':s &= nonret
                oracle=e.argmax(1).copy();oracle[s]=yi[s]
                wr[v]={'witnessed_rows':f.Id[s].tolist(),'folds_with_witness':sorted(set(f.fold[s].tolist())),
                    'independent_components':len(set(ev.components[s])), 'oracle_ceiling_only':f1(yi,oracle)-f1(yi,e.argmax(1)), 'pair_fold_auc_differences':[]}
                for mname,m in all_masks[v].items():
                    ap=auc_evidence(ev,yi,ps,a,b,m);aw=auc_evidence(ev,yi,ws,a,b,m)
                    if ap is not None and aw is not None:contrasts[f'{v}:{mname}:AUC:{key}']=(aw[0]-ap[0],aw[1]-ap[1])
                om=np.ones(826,bool) if v=='VB' else nonret
                contrasts[f'{v}:ORACLE:{key}']=ev.contrast(yi,oracle,e.argmax(1),om)
                for fold in range(5):
                    m=clean & (f.fold.to_numpy()==fold)
                    ap=auc_evidence(ev,yi,ps,a,b,m);aw=auc_evidence(ev,yi,ws,a,b,m)
                    wr[v]['pair_fold_auc_differences'].append(None if ap is None else aw[0]-ap[0])
                # Source deletion summaries reuse fixed strata only.
                dm=pd.read_csv(DS/'DATA_MANIFEST.csv').set_index('Id').loc[f.Id]
                deletes={}
                for col,groups in [('dtype',sorted(dm.dtype.unique())),('Q128',[0,43,86,30,94,'OTHER']),('Q960',[384,192,576,606,926,'OTHER'])]:
                    if col=='dtype':values=dm.dtype.to_numpy()
                    else:
                        mod=int(col[1:]);raw=dm.samples.to_numpy()%mod;values=np.array([str(i) if i in groups else 'OTHER' for i in raw])
                    for group in groups:
                        keep=clean & (values!=str(group));ap=auc_evidence(ev,yi,ps,a,b,keep);aw=auc_evidence(ev,yi,ws,a,b,keep)
                        gain=f1(yi[values!=str(group)],oracle[values!=str(group)])-f1(yi[values!=str(group)],e.argmax(1)[values!=str(group)])
                        deletes[f'{col}:{group}']={'pair_auc_difference':None if ap is None else aw[0]-ap[0],'oracle_headroom':gain,'evaluable':ap is not None}
                wr[v]['source_stratum_deletions']=deletes
            witness[key]=wr
    ci=ev.intervals(contrasts);sigma=float(np.std(ev.boots(y,record['VB']['E'].argmax(1)),ddof=1))
    rp=robust(y,record['VB']['P'].argmax(1),labels(legacy[(legacy.model=='FULL_RBF_SVM')&(legacy.validation=='VB')].set_index('Id').loc[folds['VB'].Id].ser_pred),fs,ci['VB:P-REFERENCE'])
    offset_checks={name:robust(y,offsets[('VB',name)],record['VB'][name].argmax(1),fs,ci[f'VB:offset_{name}-{name}']) for name in ['P','E']}
    downstream=[k for k in ci if k.startswith('VB:') and ('-P' in k or '-E' in k) and k not in ['VB:P-REFERENCE','VB:E-P_ABLATION'] and not ':AUC:' in k]
    max_upper=max(ci[k]['upper'] for k in downstream)
    actionable=[]
    for key,wr in witness.items():
        auc_keys=[f'VB:{m}:AUC:{key}' for m in ['full','clean']]
        available=all(k in ci for k in auc_keys)
        full_adv=available and all(ci[k]['lower']>0 for k in auc_keys)
        fd=wr['VB']['pair_fold_auc_differences'];fold_pass=sum(d is not None and d>0 for d in fd)>=4
        residual_pass=len(wr['VB']['folds_with_witness'])>=4 and ci[f'VB:ORACLE:{key}']['lower']>sigma
        va_key=f'VA:nonretrieval:AUC:{key}'
        va=va_key in ci and ci[va_key]['point']>0 and ci[va_key]['upper']>=0 and wr['VA']['oracle_ceiling_only']>0
        wr['available_gate_tests']={'full_and_clean_auc_lower_positive':bool(full_adv),'four_positive_clean_fold_aucs':bool(fold_pass),'residual_four_fold_and_lower_above_sigma':bool(residual_pass),'VA_nonretrieval_compatible':bool(va)}
        # No partial conjunction may be called actionable. All remaining
        # dependency/deletion requirements would need PASS too.
        wr['actionable']='FAIL' if not (full_adv and fold_pass and residual_pass and va) else 'UNKNOWN_REQUIRES_COMPLETE_DELETION_INTERVALS'
        if wr['actionable']=='PASS':actionable.append(key)
    membership_record=json.loads((RUN/'FROZEN_MEMBERSHIP_CLOSURE.json').read_text())
    pending_additions=[]
    for k,s in members.items():
        if k==selected or not set(members[selected])<set(s):continue
        c=f'VB:full:{k} - {selected}'
        if c in membership_record['contrasts'] and membership_record['contrasts'][c].get('pass',False):pending_additions.append(k)
    gate={
        'G0':{'status':'PASS','reason':'Existing Stage0 authority; verified exact input hashes; serialized matching logistic recipe'},
        'G1':{'status':'PASS' if rp['pass'] and parent in members[selected] and ci['VA:P-REFERENCE']['upper']>=0 else 'FAIL','reference':rp},
        'G2':{'status':'UNKNOWN','reason':'Logistic/RBF and one pooling comparison completed; no scalar-mixture OOF or scaffold-time architectural/API unavailability record. No encoder re-extraction permitted.'},
        'G3':{'status':'PASS' if max_upper<=sigma and not any(c['pass'] for c in offset_checks.values()) else 'FAIL','maximum_downstream_upper_bound':max_upper,'sigma_E':sigma,'offset_checks':offset_checks},
        'G4':{'status':'FAIL' if not actionable else 'UNKNOWN','reason':'No fully qualifying pair/witness; partial tests and oracle ceilings cannot authorize PEFT'},
        'G5':{'status':'PASS' if not pending_additions else 'FAIL','reason':'All fixed frozen membership candidates, conditional eGeMAPS, text and pooling decisions closed','unpromoted_robust_additions':pending_additions},
        'G6':{'status':'NOT_ENTERED','reason':'G0-G5 conjunction does not pass; no GPU engineering or adaptation training'}}
    first='NO_CREDIBLE_PARENT' if gate['G1']['status']!='PASS' else 'DOWNSTREAM_NOT_CLOSED'
    dump(RUN/'PEFT_GATE_RESULT.json',{'policy_version':'ADAPTATION_POLICY pre-OOF v1','policy_sha256':sha256('runs/RS-DEFHS-ADAPTATION-POLICY-001/ADAPTATION_POLICY.md'),
        'selected_P':parent,'selected_E':selected,'gate':gate,'result':'NO_PEFT:'+first,'adaptation_closed':True,'experiment_run':False,
        'recipe_if_triggered':'DEFHS_UPPER_QUARTER_QV_LORA_FIXED_DOWNSTREAM_V1','contrast_registry':list(contrasts),'J_ENTRY_intervals':ci,
        'pair_witnesses':witness,'sigma_E':sigma,'supported_layer_control':'UNKNOWN','protected_validation_queried':False})
    # Membership is now locked. Stage8 uses exactly the same 19-vector rule,
    # with the coherent fold and VA requirements imposed after scoring.
    echeck=offset_checks['E'];coherent=echeck['pass'] and ci['VA:offset_E-E']['point']>=0
    vectors=np.array([meta[('VB','E')][f]['offset'] for f in range(5)])
    stable=bool(np.all(vectors==vectors[0]))
    promote=coherent and stable
    out={}
    for v,f in folds.items():
        base=record[v]['E'].argmax(1);chosen=offsets[(v,'E')] if promote else base
        df=pd.DataFrame({'Id':f.Id,'emotion':f.emotion,'fold':f.fold,'pred':CLASSES[chosen]});df.to_csv(OUT/f'FINAL_DECISIONS_{v}.csv',index=False)
        out[v]={'argmax':report(labels(f.emotion),base,f.fold.to_numpy()),'offset_diagnostic':report(labels(f.emotion),offsets[(v,'E')],f.fold.to_numpy()),'selected':report(labels(f.emotion),chosen,f.fold.to_numpy()),'fold_offsets':meta[(v,'E')]}
    dump(RUN/'STAGE8_OFFSET_RESULTS.json',{'results':out,'diagnostic_P_offsets':{v:meta[(v,'P')] for v in folds},'E_gain':echeck,'VA_compatibility':ci['VA:offset_E-E'],
        'fold_offsets_stable':stable,'decision':'PROMOTE_SHRUNK_OFFSETS' if promote else 'KEEP_ARGMAX','membership_locked_before_offsets':members[selected],'19_vector_grid':True})
    print(json.dumps({'final_members':members[selected],'PEFT':'NO_PEFT:'+first,'offset_decision':'PROMOTE_SHRUNK_OFFSETS' if promote else 'KEEP_ARGMAX','VB':out['VB']['selected'],'VA':out['VA']['selected']},indent=2),flush=True)

def main():
    folds,ev,clean,nonret,legacy,prompt=load_contract();ev.clean=clean;ev.nonret=nonret
    systems,details,members,deletions,selected,parent=frozen_candidates(folds,ev)
    gate_and_offsets(folds,ev,clean,nonret,legacy,systems,members,deletions,selected,parent)

if __name__=='__main__':main()
