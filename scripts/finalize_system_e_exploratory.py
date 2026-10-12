#!/usr/bin/env python3
"""DEFHS System E exploratory production. SS authorized candidate; NOT submission.

Fails closed unless System D reproduces byte-for-byte and System E reproduces
its complete frozen 826 OOF probability matrix. Deploys only the predeclared
23 inputs and original ten saved waveform heads. NO test labels, no overrides.
"""
import argparse, collections, csv, hashlib, io, json, os, runpy, subprocess, sys, tempfile, warnings, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.exceptions import InconsistentVersionWarning, ConvergenceWarning
from sklearn.metrics import f1_score
from threadpoolctl import threadpool_limits

D_ZIP_SHA = 'fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839'
E_ZIP_SHA = 'dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf'
TRAIN_ZIP_SHA = 'cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789'
D_SHA = '182bfbcd5fb10b351504da6d24f3d0d33f6d05cf2786e1e1a19e80afe0e57ec9'
TARGET_ASR_SHA = '4c32a0431bff86e8e9c5153acd7225138f5790a63ff06fa001267a42ad583771'
MANIFEST_SHA = '1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469'
TRAIN_NEW_Q14_SHA = '8edd8dc9899f9304db2b46475758a67330f82c3c1348317646b561f3d57f6377'
Q14_REV='40c069824f4251a91eefaf281ebe4c544efd3e18'
PROMPT_SHA='d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f'
TEST_CONTRACT_INPUT_SHA='d2f253be8c2c06c431f869f02e1d8203f5fb1d291adc1251fc7fa4bdb07baa73'
TEST_ASR_IDS_SHA='d71971079edf16597973364358b94b3d0e69556bffe25e3db137a86b643365f2'
CLASSES=np.array(['angry','happy','neutral','sad'])
STATES=np.array(['angry','happy','neutral','sad','unclear'])
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(p):return sha(Path(p).read_bytes())
def unique_file(root,name):
    matches=list(Path(root).rglob(name))
    assert len(matches)==1,(name, list(map(str,matches)))
    return matches[0]
def read_outputs(root,csv_name,result_name='RESULT.json'):
    files={n:unique_file(root,n) for n in [csv_name,result_name,'CONTRACT.json','FEASIBILITY.json','CHECKPOINT.json','OUTPUT_INVENTORY.json','UNIQUE_OUTPUTS.jsonl']}
    assert len({p.parent for p in files.values()})==1,'All semantic files must share directory'
    inv=json.loads(files['OUTPUT_INVENTORY.json'].read_text());result=json.loads(files[result_name].read_text());contract=json.loads(files['CONTRACT.json'].read_text());feas=json.loads(files['FEASIBILITY.json'].read_text());ck=json.loads(files['CHECKPOINT.json'].read_text())
    assert all(len((files[n]).read_bytes())==v['bytes'] and digest(files[n])==v['sha256'] for n,v in inv.items())
    assert set(inv)==set(files)-{'OUTPUT_INVENTORY.json'}
    assert result['status']=='INFERENCE_COMPLETE_NOT_EVALUATED'
    assert result['rows']==209 and result['unique']==200
    assert contract['rows']==209 and contract['model']==ck['model_id']=='Qwen/Qwen3-14B'
    assert contract['revision']==ck['revision']==Q14_REV and contract['prompt_sha256']==PROMPT_SHA
    assert contract['input_sha256']==TEST_CONTRACT_INPUT_SHA
    assert contract['model_input_fields']==['transcript']
    assert feas['status']=='PASS' and all(feas['gates'].values())
    assert result['target209_inferred'] and not result['protected_validation_accessed'] and not result['kaggle_submission']
    assert digest(files[csv_name])==result['output_sha256']
    df=pd.read_csv(files[csv_name]);assert df.columns.tolist()==['Id','semantic_label']
    assert len(df)==209 and df.Id.is_unique and df.semantic_label.isin(STATES).all()
    journal=[json.loads(x) for x in files['UNIQUE_OUTPUTS.jsonl'].read_text().splitlines() if x.strip()]
    assert len(journal)==200 and len({r['transcript'] for r in journal})==200
    assert set(r['contract_sha256'] for r in journal)=={contract['sha256']}
    assert all(r['label'] in STATES for r in journal)
    return df,result,contract,journal

def verify_target_asr(root,manifest):
    csv_path=unique_file(root,'QWEN3_ASR_TARGET209.csv')
    journal_path=unique_file(root,'QWEN3_ASR_TARGET209_PROGRESS.jsonl')
    result_path=unique_file(root,'ASR_TARGET209_RESULT.json')
    inventory_path=unique_file(root,'OUTPUT_INVENTORY.json')
    assert len({x.parent for x in [csv_path,journal_path,result_path,inventory_path]})==1
    inv=json.loads(inventory_path.read_text());res=json.loads(result_path.read_text())
    assert inv['status']==res['status']=='PASS'
    assert res['rows']==res['unique_Ids']==res['source_audio_verified']==209
    assert res['model_id']=='Qwen/Qwen3-ASR-1.7B' and res['model_revision']=='b188e100bd85038c06d2812d24a39776eba774ca'
    assert res['qwen_asr_version']=='0.0.6' and res['test_audio_access']
    assert not res['protected_access'] and not res['kaggle_submitted']
    assert res['target_ids_sha256']==TEST_ASR_IDS_SHA
    assert res['output_sha256']==digest(csv_path)==TARGET_ASR_SHA
    files={f['name']:f for f in inv['files']};assert set(files)=={csv_path.name,journal_path.name,result_path.name}
    for p in [csv_path,journal_path,result_path]:
        v=files[p.name];assert len(p.read_bytes())==v['bytes'] and digest(p)==v['sha256']
    df=pd.read_csv(csv_path).sort_values('Id').reset_index(drop=True)
    assert df.columns.tolist()==['Id','filename','file_sha256','language','transcript']
    assert len(df)==209 and df.Id.is_unique and df.transcript.notna().all()
    rows=[json.loads(line) for line in journal_path.read_text().splitlines() if line.strip()]
    assert len(rows)==209 and len({r['Id'] for r in rows})==209
    journal={int(r['Id']):r for r in rows}
    test={int(r['Id']):r for r in manifest if r['split']=='test'}
    train={int(r['Id']) for r in manifest if r['split']=='train'}
    assert set(df.Id)==set(test)==set(journal) and len(test)==209 and len(train)==826 and not train.intersection(test)
    for row in df.itertuples():
        m=test[int(row.Id)];j=journal[int(row.Id)]
        assert not m['emotion'] and row.filename==m['filename']==j['filename']
        assert row.file_sha256==m['file_sha256']==j['file_sha256']
        assert row.transcript==j['transcript'] and row.language=='Hindi'
        assert j['checkpoint_revision']==res['model_revision']
    return df

def train_new_semantics(path,ids):
    assert digest(path)==TRAIN_ZIP_SHA
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        inv=json.loads(z.read('OUTPUT_INVENTORY.json'))
        for name,v in inv.items():
            b=z.read(name);assert len(b)==v['bytes'] and sha(b)==v['sha256']
        result=json.loads(z.read('RESULT.json'));contract=json.loads(z.read('CONTRACT.json'))
        assert result['status']=='INFERENCE_COMPLETE_NOT_EVALUATED' and result['rows']==826 and result['unique']==664
        assert not result['target209_inferred'] and not result['protected_validation_accessed']
        assert contract['model']=='Qwen/Qwen3-14B' and contract['revision']==Q14_REV and contract['prompt_sha256']==PROMPT_SHA
        b=z.read('QWEN14B_TRAIN826.csv')
        assert sha(b)==result['output_sha256']==TRAIN_NEW_Q14_SHA
    df=pd.read_csv(io.BytesIO(b)).set_index('Id');assert set(df.index)==set(ids) and len(df)==826
    assert df.semantic_label.isin(STATES).all()
    return df.loc[ids].semantic_label.to_numpy()

def onehot(seq):
    arr=np.asarray(seq);assert np.isin(arr,STATES).all()
    return (arr[:,None]==STATES[None,:]).astype('float64')

def run(args):
    for path,h in [(args.d_zip,D_ZIP_SHA),(args.e_zip,E_ZIP_SHA),(args.train_new_q14_zip,TRAIN_ZIP_SHA)]:
        assert digest(path)==h,(path,'archive sha',digest(path),h)
    with tempfile.TemporaryDirectory(prefix='defhs_e_clean_') as temp:
        base=Path(temp)
        with zipfile.ZipFile(args.d_zip) as z:
            assert z.testzip() is None
            z.extractall(base)
        with zipfile.ZipFile(args.e_zip) as z:
            assert z.testzip() is None
            e_oof=pd.read_csv(io.BytesIO(z.read('SYSTEM_E_PRIMARY_OOF.csv')))
            manifest=json.loads(z.read('SYSTEM_E_EVIDENCE_MANIFEST.json'))
            for fn, rec in manifest.items() if isinstance(manifest,dict) else []:
                if isinstance(rec,dict) and 'sha256' in rec and fn in z.namelist():
                    assert sha(z.read(fn))==rec['sha256'],fn
        env=dict(os.environ,DEFHS_SYSTEM_D_BASE=str(base))
        original=base/'finalize_system_d.py'
        cp=subprocess.run([sys.executable,str(original)],env=env,cwd=str(base),capture_output=True,text=True)
        assert cp.returncode==0,('SYSTEM_D_REPLAY_FAILED',cp.stdout[-1200:],cp.stderr[-1200:])
        produced_d=base/'DEFHS_SYSTEM_D_FINAL/submission_system_d.csv'
        assert digest(produced_d)==D_SHA,'System D exact byte-for-byte production PARITY FAILURE'
        assert produced_d.read_bytes()==(base/'DEFHS_SYSTEM_D_FINAL/submission_system_d.csv').read_bytes()
        module=runpy.run_path(str(original),run_name='frozen_d_functions')
        LAB=module['LAB'];assert np.array_equal(LAB,CLASSES)
        asr=pd.read_csv(base/'ASR_TRANSCRIPTS.csv').set_index('Id')
        ids=np.load(base/'FIXED_PAIR_VB.npz')['Id']
        ma=np.frombuffer(bytes.fromhex((base/'defhs_prod_run/old_evidence/metadata.hex').read_text()),dtype=np.uint8).astype('int64')
        fold=ma%5;y=LAB[ma//20]
        assert np.array_equal(y,asr.loc[ids].emotion.to_numpy())
        old8=pd.read_csv(base/'QWEN_SEMANTIC_OUTPUTS.csv').set_index('Id')
        with zipfile.ZipFile(base/'DEFHS_Qwen14B_train826_outputs.zip') as z:
            old14=pd.read_csv(io.BytesIO(z.read('final_semantic_train826/QWEN14B_TRAIN826.csv'))).set_index('Id')
        q8_train=onehot(old8.loc[ids].semantic_label)
        old14_train=onehot(old14.loc[ids].semantic_label)
        new14_train_labels=train_new_semantics(args.train_new_q14_zip,ids)
        new14_train=onehot(new14_train_labels)
        Xe=[];Xt=[]
        target=np.sort(asr.index[asr.split.eq('test')].to_numpy())
        assert len(target)==209 and not set(ids).intersection(target)
        for name in ('emotion2vec_base_meanstd.npz','xls_r_300m_meanstd.npz'):
            z=np.load(base/name,allow_pickle=False)
            index={int(v):i for i,v in enumerate(z['Id'])}
            Xe.append(z['X'][[index[int(x)] for x in ids]])
            Xt.append(z['X'][[index[int(x)] for x in target]])
        pw=np.column_stack([np.load(base/'E2V_CONTROL_VB.npz')['prob'],np.load(base/'XLSR_VB.npz')['prob']])
        original_d_oof=pd.read_csv(base/'defhs_prod_run/old_evidence/CHALLENGER_PRIMARY_OOF.csv')
        assert np.array_equal(original_d_oof.Id,ids) and np.array_equal(e_oof.Id,ids)
        assert np.array_equal(e_oof.emotion.to_numpy(),y) and np.array_equal(e_oof.fold.to_numpy(),fold)
        probsE=np.empty((826,4));probsD=np.empty((826,4));testwave=[];inner={}
        # Original 50 group-aware inner waveform fits, saved outer heads, same C=1 L2 logistics.
        warnings.simplefilter('error',ConvergenceWarning)
        with threadpool_limits(limits=2):
            for f in range(5):
                tr=fold!=f;vl=~tr;arr=[]
                for k,name in enumerate(['emotion2vec_base','xls_r_300m']):
                    h=base/f'{name}_VB_outer{f}.joblib.bin'
                    assert digest(h)==module['HEADS'][name][f]
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore',InconsistentVersionWarning)
                        model=joblib.load(h)
                    assert np.max(np.abs(model.predict_proba(Xe[k][vl])-pw[vl,k*4:(k+1)*4]))<5e-7
                    arr.append(model.predict_proba(Xt[k]))
                testwave.append(np.column_stack(arr))
                arr_inner=np.zeros((826,8))
                for block in sorted(set(fold[tr])):
                    it=tr&(fold!=block);iv=tr&(fold==block)
                    arr_inner[iv]=np.column_stack([module['head'](x,y,it,iv) for x in Xe])
                inner[f]=arr_inner
            dtest=[];etest=[];dtest_fold=[];etest_fold=[]
            for f in range(5):
                tr=fold!=f;vl=~tr
                oldmeta=np.column_stack([inner[f][tr],q8_train[tr],old14_train[tr]])
                newmeta=np.column_stack([oldmeta,new14_train[tr]])
                d=module['meta_lr']().fit(oldmeta,y[tr]);e=module['meta_lr']().fit(newmeta,y[tr])
                probsD[vl]=d.predict_proba(np.column_stack([pw[vl],q8_train[vl],old14_train[vl]]))
                probsE[vl]=e.predict_proba(np.column_stack([pw[vl],q8_train[vl],old14_train[vl],new14_train[vl]]))
        refD=original_d_oof[['challenger_p_'+x for x in CLASSES]].to_numpy()
        refE=e_oof[['system_E_p_'+x for x in CLASSES]].to_numpy()
        maxD=float(np.max(np.abs(probsD-refD)))
        maxE=float(np.max(np.abs(probsE-refE)))
        assert maxD<1e-8,('System D OOF probability parity',maxD)
        assert maxE<1e-8,('System E OOF probability parity',maxE)
        assert np.array_equal(CLASSES[probsD.argmax(1)],e_oof.system_D_pred)
        assert np.array_equal(CLASSES[probsE.argmax(1)],e_oof.system_E_pred)
        e_score=float(f1_score(y,CLASSES[probsE.argmax(1)],labels=CLASSES,average='macro'))
        assert abs(e_score-0.8774091527555827)<1e-12,('E OOF macro-f1',e_score)
        print(json.dumps({'status':'SYSTEM_D_AND_E_OOF_REPLAY_PASS','D209_SHA256':D_SHA,'D_OOF_max_abs':maxD,'E_OOF_max_abs':maxE,'System_E_PRIMARY_CV':e_score},indent=2),flush=True)
        if args.preflight_only:
            return
        assert args.official_manifest and args.target_asr_dir and args.target_semantic_dir
        assert digest(args.official_manifest)==MANIFEST_SHA
        official=list(csv.DictReader(open(args.official_manifest,newline='',encoding='utf-8')))
        target_asr=verify_target_asr(args.target_asr_dir,official)
        new_semantic,result,contract,journal=read_outputs(args.target_semantic_dir,'QWEN14B_TARGET209.csv')
        assert np.array_equal(new_semantic.Id,target) and np.array_equal(target_asr.Id,target)
        unique=set(target_asr.transcript)
        assert len(unique)==200
        records=[{'Id':int(r.Id),'transcript':r.transcript} for r in target_asr.itertuples()]
        raw=json.dumps(records,ensure_ascii=False,separators=(',',':')).encode('utf-8')
        assert sha(raw)==contract['input_sha256']
        match={r['transcript']:r['label'] for r in journal}
        assert set(match)==unique
        for r in target_asr.itertuples():
            assert match[r.transcript]==new_semantic.set_index('Id').loc[r.Id,'semantic_label']
        new_test=onehot(new_semantic.set_index('Id').loc[target].semantic_label)
        old_test8=onehot(old8.loc[target].semantic_label)
        with zipfile.ZipFile(base/'DEFHS_Qwen14B_TARGET209_outputs.zip') as z:
            old_test14=pd.read_csv(io.BytesIO(z.read('final_semantic_target209/QWEN14B_TARGET209.csv'))).set_index('Id')
        old_test14=onehot(old_test14.loc[target].semantic_label)
        # Exactly five original fold-specific D/E meta heads on authenticated saved test-wave features.
        with threadpool_limits(limits=2):
            for f in range(5):
                tr=fold!=f
                d=module['meta_lr']().fit(np.column_stack([inner[f][tr],q8_train[tr],old14_train[tr]]),y[tr])
                e=module['meta_lr']().fit(np.column_stack([inner[f][tr],q8_train[tr],old14_train[tr],new14_train[tr]]),y[tr])
                dtest_fold.append(d.predict_proba(np.column_stack([testwave[f],old_test8,old_test14])))
                etest_fold.append(e.predict_proba(np.column_stack([testwave[f],old_test8,old_test14,new_test])))
        dprob=np.mean(dtest_fold,axis=0);eprob=np.mean(etest_fold,axis=0)
        dser=CLASSES[dprob.argmax(1)];eser=CLASSES[eprob.argmax(1)]
        df=pd.read_csv(produced_d).sort_values('Id')
        assert np.array_equal(df.Id,target)
        d_final=dser.copy();e_final=eser.copy()
        retrieval=dict(zip(map(int,module['RID'].split(',')),CLASSES[[int(x) for x in module['RLABEL']]]))
        assert len(retrieval)==78
        for i,id in enumerate(target):
            if int(id) in retrieval:
                d_final[i]=e_final[i]=retrieval[int(id)]
        assert module['sha'](module['csvbytes'](target,d_final))==D_SHA
        assert np.array_equal(d_final,df.emotion),('System D 209 decisions are not exactly replayed')
        assert all(d_final[np.where(target==id)[0][0]]==label for id,label in retrieval.items())
        hard=set(map(int,module['HARD'].split(',')))
        medium=set(map(int,module['MED'].split(',')))
        assert len(hard)==60 and len(medium)==13
        q960={int(r['Id']) for r in official if r['split']=='test' and int(r['samples'])%960==606}
        assert q960=={102,184,210,235,529,541,567,610,742,817,941}
        out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
        candidate_bytes=module['csvbytes'](target,e_final)
        outfile=out/'submission_system_e_exploratory.csv'
        outfile.write_bytes(candidate_bytes)
        assert pd.read_csv(outfile).columns.tolist()==['Id','emotion']
        assert len(pd.read_csv(outfile))==209 and len(set(target))==209
        assert set(e_final)<=set(CLASSES)
        rows=[];changed=[]
        for i,id in enumerate(target):
            k=int(id);cohort='HARD' if k in hard else 'MEDIUM_CONFIDENCE' if k in medium else 'HIGH_CONFIDENCE'
            rec={'Id':k,'cohort':cohort,'Q960_remainder_606':k in q960,
                'certified_retrieval':k in retrieval,
                'system_D_final':str(d_final[i]),'system_E_final':str(e_final[i]),
                'system_D_raw':str(dser[i]),'system_E_raw':str(eser[i]),
                'Qwen8_state':str(old8.loc[k].semantic_label),
                'Whisper_Qwen14_state':str(CLASSES[old_test14[i,:4].argmax()] if not old_test14[i,-1] else 'unclear'),
                'QwenASR_Qwen14_state':str(new_semantic.set_index('Id').loc[k,'semantic_label']),
                'D_margin':float(np.sort(dprob[i])[-1]-np.sort(dprob[i])[-2]),
                'E_margin':float(np.sort(eprob[i])[-1]-np.sort(eprob[i])[-2])}
            for j,lab in enumerate(CLASSES):
                rec['D_p_'+lab]=float(dprob[i,j]);rec['E_p_'+lab]=float(eprob[i,j])
            rows.append(rec)
            if d_final[i]!=e_final[i]:
                assert k not in retrieval
                changed.append(rec)
        audit=pd.DataFrame(rows)
        audit.to_csv(out/'SYSTEM_E_209_ROW_AUDIT.csv',index=False,float_format='%.17g')
        pd.DataFrame(changed,columns=audit.columns).to_csv(out/'SYSTEM_D_TO_E_CHANGES.csv',index=False,float_format='%.17g')
        diffs=collections.Counter(q['cohort'] for q in changed)
        outcome={'mission':'SS-DEFHS-SYSTEM-E-EXPLORATORY-DEPLOYMENT-001','status':'EXPLORATORY_CANDIDATE_PRODUCED_SS_REVIEW_REQUIRED',
            'scientific_system_E_promoted':False,'failure':'Q960_606 -0.03367393 < -0.02 frozen tolerance',
            'original_System_D_SHA256':D_SHA,'System_D_bit_for_bit_reproduced':True,
            'System_D_826_max_abs_probability_difference':maxD,
            'System_E_826_max_abs_probability_difference':maxE,
            'System_E_primary_cv':e_score,
            'target_new_ASR_SHA256':TARGET_ASR_SHA,'target_new_semantic_SHA256':result['output_sha256'],
            'target_semantic_unique_transcripts':200,
            'E_candidate_SHA256':sha(candidate_bytes),'candidate_rows':209,
            'certified_retrieval_unchanged':len(retrieval),'target_labels_used':False,
            'protected_validation_accessed':False,'kaggle_competition_submission':False,
            'changed_count':len(changed),'changed_ids':[r['Id'] for r in changed],
            'changed_by_cohort':dict(diffs),'q960_target_n':len(q960),
            'q960_target_changed_ids':[r['Id'] for r in changed if r['Q960_remainder_606']],
            'class_D':{c:int(np.sum(d_final==c)) for c in CLASSES},
            'class_E':{c:int(np.sum(e_final==c)) for c in CLASSES}}
        (out/'PRODUCTION_AUDIT.json').write_text(json.dumps(outcome,indent=2)+'\n')
        (out/'PROVENANCE_SHA256.json').write_text(json.dumps({'baseline_zip':D_ZIP_SHA,'E_evidence_zip':E_ZIP_SHA,
            'train_new_Qwen14_zip':TRAIN_ZIP_SHA,'target_asr_csv':TARGET_ASR_SHA,
            'target_Qwen14_csv':result['output_sha256'],
            'submission_D':D_SHA,'submission_E':sha(candidate_bytes),
            'audit':digest(out/'SYSTEM_E_209_ROW_AUDIT.csv')},indent=2)+'\n')
        print(json.dumps(outcome,indent=2),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--d-zip',required=True,type=Path)
    ap.add_argument('--e-zip',required=True,type=Path)
    ap.add_argument('--train-new-q14-zip',required=True,type=Path)
    ap.add_argument('--target-asr-dir',type=Path)
    ap.add_argument('--target-semantic-dir',type=Path)
    ap.add_argument('--official-manifest',type=Path)
    ap.add_argument('--out',type=Path)
    ap.add_argument('--preflight-only',action='store_true')
    a=ap.parse_args()
    assert a.preflight_only or (a.out and a.target_asr_dir and a.target_semantic_dir and a.official_manifest)
    run(a)
