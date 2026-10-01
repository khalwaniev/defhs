#!/usr/bin/env python3
"""CPU continuation of cached DEFHS Stage 4/5. Explicitly excludes protected folds."""
from __future__ import annotations
import argparse, itertools, json, time
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
from sklearn.pipeline import make_pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from threadpoolctl import threadpool_limits
from defhs_frozen_closure_utils import *

RUN = Path('runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001')
DS = Path('runs/DS-DEFHS-VALIDATION-HARDENING-002')
V3 = Path('.tmp/rs_system_implementation_001_frozen_screen_v3/rs_defhs_system_implementation_001')
INPUT = Path('work/mission_inputs')
OUT = Path('work/frozen_closure')
SEED = 20260930

def load_contract():
    OUT.mkdir(parents=True,exist_ok=True)
    hashes = {}
    paths = [DS / x for x in ['DATA_MANIFEST.csv','DUPLICATE_GROUPS_FINAL.csv','VALIDATION_OOF_FIXED.csv','VALIDATION_VA_FOLDS.csv','VALIDATION_VB_FOLDS.csv','VALIDATION_VD_REGIMES.csv','RETRIEVAL_MAP_FINAL.csv']]
    inventory = {r['artifact']:r['sha256'] for r in json.loads((DS/'CANONICAL_ARTIFACT_INVENTORY.json').read_text())}
    for p in paths:
        assert sha256(p)==inventory[p.name],p
        hashes[str(p)]=sha256(p)
    completed = pd.read_csv(DS/'CLOSURE_COMPLETED_ARTIFACT_MANIFEST.tsv',sep='\t')
    for p in INPUT.rglob('*'):
        if not p.is_file(): continue
        if p.name=='ACOUSTIC_FEATURES_FULL.csv': expected='d8769829f6e2ca351e96068e64d89b95977cca83fb49f0ef7d0d597f11c06a53'
        else:
            row = completed[completed.drive_path.str.endswith('/'+p.name)]
            assert len(row)==1,p
            expected=row.sha256.iloc[0]
        assert sha256(p)==expected,p
        hashes[str(p)]=expected
    for r in json.loads((V3/'OUTPUT_INVENTORY.json').read_text())['files']:
        p=V3/r['name']; assert p.stat().st_size==r['bytes'] and sha256(p)==r['sha256'],p
        hashes[str(p)]=r['sha256']
    folds = {v:pd.read_csv(DS/f'VALIDATION_{v}_FOLDS.csv',dtype={'duplicate_group':str}).sort_values('Id').reset_index(drop=True) for v in ['VA','VB']}
    assert np.array_equal(folds['VA'].Id,folds['VB'].Id)
    dup = pd.read_csv(DS/'DUPLICATE_GROUPS_FINAL.csv')
    prompt = pd.read_csv(INPUT/'asr_transcripts/PROMPT_CLUSTER_ASSIGNMENTS.csv')
    ev = Evidence(folds['VB'].Id,dup,prompt)
    counts = prompt.groupby('prompt_sim_0.90').Id.transform('size')
    repeated = set(prompt.loc[counts>1,'Id'])
    dup_repeat = set(dup.Id)
    clean = ~folds['VB'].Id.isin(repeated|dup_repeat).to_numpy()
    legacy = pd.read_csv(DS/'VALIDATION_OOF_FIXED.csv')
    ret = legacy[(legacy.model=='FULL_RBF_SVM')&(legacy.validation=='VA')].set_index('Id').loc[folds['VA'].Id]
    nonret = ~ret.retrieval_covered.to_numpy(bool)
    dump(RUN/'CONTINUATION_INPUT_VERIFICATION.json',{'hashes':hashes,'status':'PASS','train_rows':826,'test_rows':209,
        'bootstrap_components':len(set(ev.components)),'clean_rows':int(clean.sum()),'VA_nonretrieval_rows':int(nonret.sum()),
        'protected_validation_queried':False,'kaggle_submission_made':False})
    return folds, ev, clean, nonret, legacy, prompt

def probability_heads(folds):
    feat = pd.read_csv(INPUT/'ACOUSTIC_FEATURES_FULL.csv').set_index('Id')
    basic=['duration_seconds','amplitude_peak_fullscale','rms_fullscale','dc_offset_fullscale','crest_factor','clip_fraction','silence_fraction','leading_silence_seconds','trailing_silence_seconds','pause_count','pause_fraction_frames','zcr_mean','spectral_centroid_mean','spectral_bandwidth_mean','spectral_rolloff85_mean','spectral_flatness_mean','onset_strength_mean','f0_yin_median','f0_yin_std']
    cols = [c for c in feat if (c in basic or c.startswith(('mfcc','dmfcc','logmel'))) and pd.api.types.is_numeric_dtype(feat[c])]
    eg = pd.read_csv(INPUT/'egemaps/EGEMAPS_FEATURES.csv').set_index('Id')
    ec = [c for c in eg if c not in ['split','filename','emotion']]
    assert len(ec)==88
    meta = {'acoustic_columns':cols,'egemaps_columns':ec,'seed':SEED,'calibration':'sigmoid inner-3-fold; VB duplicate-group-safe', 'parity':{}}
    legacy=pd.read_csv(DS/'VALIDATION_OOF_FIXED.csv')
    for view, f in folds.items():
        y=f.emotion.to_numpy(); groups=folds['VB'].duplicate_group.to_numpy(); fs=f.fold.to_numpy()
        X=feat.loc[f.Id,cols].replace([np.inf,-np.inf],np.nan).to_numpy()
        Xe=eg.loc[f.Id,ec].replace([np.inf,-np.inf],np.nan).to_numpy()
        P=np.zeros((826,4)); Pe=P.copy(); hard=np.empty(826,object)
        for fold in range(5):
            tr=np.where(fs!=fold)[0]; vl=np.where(fs==fold)[0]
            base=make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),SVC(C=10,kernel='rbf',gamma='scale'))
            base.fit(X[tr],y[tr]); hard[vl]=base.predict(X[vl])
            cv=list(StratifiedGroupKFold(3,shuffle=True,random_state=SEED+fold).split(X[tr],y[tr],groups[tr])) if view=='VB' else list(StratifiedKFold(3,shuffle=True,random_state=SEED+fold).split(X[tr],y[tr]))
            cal=CalibratedClassifierCV(estimator=base,method='sigmoid',cv=cv)
            cal.fit(X[tr],y[tr]); P[vl]=cal.predict_proba(X[vl])
            e=make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LogisticRegression(C=.3,max_iter=2000))
            e.fit(Xe[tr],y[tr]); Pe[vl]=e.predict_proba(Xe[vl])
            joblib.dump(cal,OUT/f'FULL_RBF_SVM_CAL_{view}_fold{fold}.joblib')
            joblib.dump(e,OUT/f'EGEMAPS_{view}_fold{fold}.joblib')
        old=legacy[(legacy.model=='FULL_RBF_SVM')&(legacy.validation==view)].set_index('Id').loc[f.Id].ser_pred.to_numpy()
        mismatch=int(np.sum(hard!=old)); assert mismatch==0,(view,mismatch)
        meta['parity'][view]={'uncalibrated_hard_mismatches':mismatch,'original':report(labels(y),labels(hard),fs),'calibrated':report(labels(y),P.argmax(1),fs),'egemaps':report(labels(y),Pe.argmax(1),fs)}
        expected=json.loads((INPUT/'egemaps/EGEMAPS_AUDIT_RESULTS.json').read_text())['validation'][view]['oof_macro_f1']
        assert abs(meta['parity'][view]['egemaps']['macro_f1']-expected)<1e-12
        save_oof(OUT/f'OOF_FULL_RBF_SVM_CAL_{view}.csv',f,P)
        save_oof(OUT/f'OOF_EGEMAPS_{view}.csv',f,Pe)
    dump(RUN/'ACOUSTIC_PROBABILITY_PARITY.json',meta)
    print('PROBABILITY_HEADS=SUCCESS',flush=True)

def get_lanes(folds):
    lanes={}
    for view,f in folds.items():
        lanes[view]={n:valid_oof(V3/f'OOF_{family}_{view}.csv',f,'L2_LOGREG') for n,family in [('emotion2vec_base_L2_LOGREG','emotion2vec_base'),('xls_r_300m_L2_LOGREG','xls_r_300m')]}
        lanes[view]['FULL_RBF_SVM_CAL']=valid_oof(OUT/f'OOF_FULL_RBF_SVM_CAL_{view}.csv',f)
    return lanes

def pair_diagnostics(probs,y):
    rows=[]
    for a,b in itertools.combinations(sorted(probs),2):
        pa,pb=probs[a],probs[b]; ha,hb=pa.argmax(1),pb.argmax(1); ea,eb=ha!=y,hb!=y
        la,lb=np.log(np.clip(pa,1e-12,1)),np.log(np.clip(pb,1e-12,1))
        la-=la.mean(1,keepdims=True);lb-=lb.mean(1,keepdims=True)
        perclass={}
        for c in range(4):
            m=y==c
            perclass[str(CLASSES[c])]={'support':int(m.sum()),'a_wrong_b_correct':int((m&ea&~eb).sum()),'b_wrong_a_correct':int((m&eb&~ea).sum()),'both_wrong':int((m&eb&ea).sum())}
        oracle=np.where(~ea,ha,np.where(~eb,hb,ha))
        rows.append({'a':a,'b':b,'hard_error_correlation':float(np.corrcoef(ea.astype(float),eb.astype(float))[0,1]),
            'probability_correlation':float(np.corrcoef(pa.ravel(),pb.ravel())[0,1]),'centered_log_probability_correlation':float(np.corrcoef(la.ravel(),lb.ravel())[0,1]),
            'per_class_probability_correlation':{str(CLASSES[c]):float(np.corrcoef(pa[:,c],pb[:,c])[0,1]) for c in range(4)},
            'disagreement':float(np.mean(ha!=hb)),'both_wrong':int((ea&eb).sum()),'per_class_complementarity':perclass,
            'oracle_union_macro_f1':f1(y,oracle),'oracle_note':'diagnostic ceiling only; never an achievable ensemble score'})
    return rows

def stage4(folds,ev,clean,nonret,legacy):
    lanes=get_lanes(folds); names=sorted(lanes['VB']); subsets=[s for n in range(1,4) for s in itertools.combinations(names,n)]
    pred={v:{} for v in folds}; probs={v:{} for v in folds}; result={v:{} for v in folds}
    for v,f in folds.items():
        y=labels(f.emotion); fs=f.fold.to_numpy()
        for s in subsets:
            key='+'.join(s)
            if len(s)==1:
                q=lanes[v][s[0]]; r={'equal':report(y,q.argmax(1),fs),'heldout':report(y,q.argmax(1),fs),'selections':[]}
            else:q,r=choose_probability_blend([lanes[v][n] for n in s],y,fs,ev)
            probs[v][key]=q;pred[v][key]=q.argmax(1);result[v][key]=r
            save_oof(OUT/f'OOF_SYSTEM_{key}_{v}.csv',f,q)
    # Contrast registry enumerated without using outcomes: every candidate against
    # all of its proper member subsets, full/CLEAN VB and nonretrieval VA.
    contrasts={}; specs=[]
    for s in subsets:
        if len(s)<2:continue
        a='+'.join(s)
        for t in subsets:
            if set(t)<set(s):
                b='+'.join(t)
                for v,mask,label in [('VB',None,'full'),('VB',clean,'clean'),('VA',nonret,'nonretrieval')]:
                    k=f'{v}:{label}:{a} - {b}'; specs.append((k,v,mask,a,b));contrasts[k]=ev.contrast(labels(folds[v].emotion),pred[v][a],pred[v][b],mask)
    ints=ev.intervals(contrasts); checks={}
    for k,v,m,a,b in specs:
        checks[k]=robust(labels(folds[v].emotion),pred[v][a],pred[v][b],folds[v].fold.to_numpy(),ints[k]) if m is None else ints[k]
    # Start from strongest standalone; additions require all member ablations
    # credible, clean point-positive, no VA credible contradiction.
    strongest=max(names,key=lambda n:(result['VB'][n]['heldout']['macro_f1'],n))
    eligible=[]
    for s in subsets:
        if len(s)==1:continue
        a='+'.join(s); good=True
        for n in s:
            b='+'.join(x for x in s if x!=n)
            main=checks[f'VB:full:{a} - {b}']; cl=ints[f'VB:clean:{a} - {b}']; va=ints[f'VA:nonretrieval:{a} - {b}']
            good &= main['pass'] and cl['point']>0 and va['upper']>=0
        if strongest not in s:
            good=False # no weaker alternate set displaces the clear incumbent without its contrast
        if good:eligible.append(s)
    selected=min(eligible,key=lambda s:(len(s),-result['VB']['+'.join(s)]['heldout']['macro_f1'],s)) if eligible else (strongest,)
    core='+'.join(selected)
    # Conditional eGeMAPS small-weight test (0 or 1/4); baseline is core, never 1/2.
    egresult={}; egpred={}
    for v,f in folds.items():
        eg=valid_oof(OUT/f'OOF_EGEMAPS_{v}.csv',f)
        q,r=choose_probability_blend([probs[v][core],eg],labels(f.emotion),f.fold.to_numpy(),ev,allowed=[(1.,0.),(.75,.25)],equal_weights=[1.,0.])
        egresult[v]=r;egpred[v]=q.argmax(1)
        save_oof(OUT/f'OOF_CORE_PLUS_EGEMAPS_{v}.csv',f,q)
    ei=ev.intervals({f'{v}:{mname}':ev.contrast(labels(folds[v].emotion),egpred[v],pred[v][core],m) for v,m,mname in [('VB',None,'full'),('VB',clean,'clean'),('VA',nonret,'nonretrieval')]})
    er=robust(labels(folds['VB'].emotion),egpred['VB'],pred['VB'][core],folds['VB'].fold.to_numpy(),ei['VB:full'])
    egpass=er['pass'] and ei['VB:clean']['point']>0 and ei['VA:nonretrieval']['upper']>=0
    # Parent J_SELECT: both heads, neural reference gains and E0 ablations.
    js={}; parent_predictions={}; eligibility={}
    for v,f in folds.items():
        y=labels(f.emotion)
        old=legacy[(legacy.model=='FULL_RBF_SVM')&(legacy.validation==v)].set_index('Id').loc[f.Id]
        ref=labels(old.ser_pred)
        for n,family in [('emotion2vec_base_L2_LOGREG','emotion2vec_base'),('xls_r_300m_L2_LOGREG','xls_r_300m')]:
            p=lanes[v][n].argmax(1); rb=valid_oof(V3/f'OOF_{family}_{v}.csv',f,'RBF_SVM_CAL').argmax(1)
            parent_predictions[(v,n)]=p
            mask=None if v=='VB' else nonret
            js[f'{v}:{n}-REFERENCE']=ev.contrast(y,p,ref,mask)
            js[f'{v}:{n}-RBF']=ev.contrast(y,p,rb,mask)
            if n in selected and len(selected)>1:
                minus='+'.join(x for x in selected if x!=n)
                js[f'{v}:E0-minus-{n}']=ev.contrast(y,pred[v][core],pred[v][minus],mask)
    ji=ev.intervals(js)
    for n in ['emotion2vec_base_L2_LOGREG','xls_r_300m_L2_LOGREG']:
        y=labels(folds['VB'].emotion); p=parent_predictions[('VB',n)]
        ref=labels(legacy[(legacy.model=='FULL_RBF_SVM')&(legacy.validation=='VB')].set_index('Id').loc[folds['VB'].Id].ser_pred)
        r=robust(y,p,ref,folds['VB'].fold.to_numpy(),ji[f'VB:{n}-REFERENCE'])
        credibility=r['pass'] and ji[f'VA:{n}-REFERENCE']['upper']>=0
        eligibility[n]={'reference_credibility':r,'VA_nonretrieval_reference':ji[f'VA:{n}-REFERENCE'],
            'not_credibly_inferior_to_same_encoder_RBF':ji[f'VB:{n}-RBF']['upper']>=0,'in_E0':n in selected,'credible':bool(credibility)}
    parent='emotion2vec_base_L2_LOGREG' if 'emotion2vec_base_L2_LOGREG' in selected and eligibility['emotion2vec_base_L2_LOGREG']['credible'] else ('xls_r_300m_L2_LOGREG' if 'xls_r_300m_L2_LOGREG' in selected and eligibility['xls_r_300m_L2_LOGREG']['credible'] else None)
    # No identity change may occur after this saved prospective-parent record.
    out={'phase':'STAGE4','systems':result,'contrast_registry':list(contrasts),'contrasts':checks,
        'pairwise':{v:pair_diagnostics(lanes[v],labels(f.emotion)) for v,f in folds.items()},
        'selected_E0_members':selected,'selected_E0_id':core,'eligible_systems':eligible,
        'egemaps':{'results':egresult,'intervals':ei,'robust':er,'decision':'PROMOTE' if egpass else 'KILL_PERMANENTLY'},
        'prospective_parent':parent,'parent_J_SELECT':ji,'parent_eligibility':eligibility,
        'historical_selection_limit':'Conditional OOF intervals/meta-folds do not remove earlier adaptive selection or make nested-independent validation.'}
    dump(RUN/'STAGE4_RESULTS.json',out)
    print(json.dumps({'stage4_selected':selected,'prospective_parent':parent,'VB':result['VB'][core]['heldout'],'VA':result['VA'][core]['heldout'],'egemaps':out['egemaps']['decision']},indent=2),flush=True)

def text_head(f,transcripts,prompt,control=False):
    texts=transcripts.set_index('Id').loc[f.Id].normalized_transcript.fillna('').to_numpy()
    cluster=prompt.set_index('Id').loc[f.Id]['prompt_sim_0.90'].to_numpy()
    y=f.emotion.to_numpy(); fs=f.fold.to_numpy(); p=np.zeros((826,4)); near=np.zeros(826,bool); counts=[]
    for fold in range(5):
        tr=np.where(fs!=fold)[0];va=np.where(fs==fold)[0]
        if control:tr=tr[~np.isin(cluster[tr],cluster[va])]
        vf=FeatureUnion([('word',TfidfVectorizer(ngram_range=(1,2),min_df=1,sublinear_tf=True)),('char',TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=1,sublinear_tf=True))])
        m=make_pipeline(vf,LogisticRegression(C=.3,max_iter=5000,random_state=SEED))
        m.fit(texts[tr],y[tr]);p[va]=m.predict_proba(texts[va])
        # Train-only text-neighbor diagnostic, no vocabulary from held-out rows.
        nv=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=1)
        x=nv.fit_transform(texts[tr]); xv=nv.transform(texts[va])
        near[va]=cosine_similarity(xv,x).max(1)>=.90
        counts.append({'fold':fold,'training_rows':len(tr),'heldout_rows':len(va)})
    return p,near,counts

def stage5(folds,ev,clean,nonret,prompt):
    s4=json.loads((RUN/'STAGE4_RESULTS.json').read_text()); core=s4['selected_E0_id']
    transcripts=pd.read_csv(INPUT/'asr_transcripts/ASR_TRANSCRIPTS.csv')
    counts=prompt.groupby('prompt_sim_0.90').Id.transform('size')
    repeat=set(prompt.loc[counts>1,'Id']);mixed=set()
    for _,g in prompt.groupby('prompt_sim_0.90'):
        if set(g.split)=={'train','test'}:mixed.update(map(int,g.Id))
    outputs={}; cs={}; arrays={}
    for v,f in folds.items():
        y=labels(f.emotion);fs=f.fold.to_numpy(); audio=valid_oof(OUT/f'OOF_SYSTEM_{core}_{v}.csv',f)
        outputs[v]={}
        for control in [False,True]:
            key='PROMPT_CONTROL' if control else 'TFIDF_TEXT'
            p,near,ct=text_head(f,transcripts,prompt,control)
            q,b=choose_probability_blend([audio,p],y,fs,ev)
            save_oof(OUT/f'OOF_{key}_{v}.csv',f,p);save_oof(OUT/f'OOF_AUDIO_PLUS_{key}_{v}.csv',f,q)
            masks={'all':np.ones(826,bool),'prompt_singleton':~f.Id.isin(repeat).to_numpy(),'prompt_non_singleton':f.Id.isin(repeat).to_numpy(),
                   'no_close_training_neighbor':~near,'mixed_train_test_cluster':f.Id.isin(mixed).to_numpy(),'outside_mixed_train_test_cluster':~f.Id.isin(mixed).to_numpy(),'clean':clean}
            strata={}
            for name,m in masks.items():
                strata[name]={'rows':int(m.sum()),'text':f1(y[m],p.argmax(1)[m]),'audio':f1(y[m],audio.argmax(1)[m]),'blend':f1(y[m],q.argmax(1)[m])}
                cs[f'{v}:{key}:{name}']=ev.contrast(y,q.argmax(1),audio.argmax(1),m)
            outputs[v][key]={'standalone':report(y,p.argmax(1),fs),'blend':b,'strata':strata,'fold_training_counts':ct}
            arrays[(v,key)]=(q.argmax(1),audio.argmax(1))
    ci=ev.intervals(cs); tests={}
    for key in ['TFIDF_TEXT','PROMPT_CONTROL']:
        a,b=arrays[('VB',key)]
        tests[key]=robust(labels(folds['VB'].emotion),a,b,folds['VB'].fold.to_numpy(),ci[f'VB:{key}:all'])
    promote=tests['TFIDF_TEXT']['pass'] and tests['PROMPT_CONTROL']['pass'] and all(ci[f'VB:{k}:{m}']['point']>0 for k in tests for m in ['prompt_singleton','no_close_training_neighbor','outside_mixed_train_test_cluster','clean'])
    dump(RUN/'STAGE5_RESULTS.json',{'results':outputs,'contrast_registry':list(cs),'intervals':ci,'robust':tests,
        'decision':'PROMOTE_REQUIRES_SINGLE_UPGRADE_DECISION' if promote else 'KILL_TEXT_LANE','model':'one word+character TFIDF logistic C0.3','new_ASR_or_LM':False})
    print(json.dumps({'stage5':'PROMOTE' if promote else 'KILL_TEXT_LANE','robust':tests},indent=2),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['heads','4','5'],required=True);a=ap.parse_args()
    t=time.monotonic()
    with threadpool_limits(limits=2):
        folds,ev,clean,nonret,legacy,prompt=load_contract()
        if a.stage=='heads':probability_heads(folds)
        elif a.stage=='4':stage4(folds,ev,clean,nonret,legacy)
        else:stage5(folds,ev,clean,nonret,prompt)
    print(f'CPU_STAGE_WALL_SECONDS={time.monotonic()-t:.3f}',flush=True)

if __name__=='__main__':main()
