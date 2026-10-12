#!/usr/bin/env python3
"""Read-only, leakage-conscious diagnostic for new audio-native expert vs System E.

NO threshold selection, promotion, hidden labels, competition submission, or retraining.
"""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.metrics import f1_score,confusion_matrix
C=['angry','happy','neutral','sad']
Z='dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf'

def h(p):
 d=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):d.update(b)
 return d.hexdigest()

def f1(y,p):return float(f1_score(y,p,labels=C,average='macro',zero_division=0))

p=argparse.ArgumentParser()
p.add_argument('--system-e-zip',type=Path,required=True)
p.add_argument('--system-e-test-audit',type=Path,required=True)
p.add_argument('--omni-csv',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
assert h(a.system_e_zip)==Z,'Unexpected System E source evidence ZIP'
with zipfile.ZipFile(a.system_e_zip) as z:
 ref=pd.read_csv(io.BytesIO(z.read('SYSTEM_E_PRIMARY_OOF.csv')))
train=ref.sort_values('Id').reset_index(drop=True)
assert len(train)==826 and train.Id.is_unique
assert f1(train.emotion,train.system_E_pred)==0.8774091527555827
te=pd.read_csv(a.system_e_test_audit).sort_values('Id').reset_index(drop=True)
assert len(te)==209 and te.Id.is_unique
raw=pd.read_csv(a.omni_csv)
assert len(raw)==1035 and raw.Id.is_unique and set(raw.split)=={'train','test'}
assert set(raw.loc[raw.split=='train','Id'])==set(train.Id)
assert set(raw.loc[raw.split=='test','Id'])==set(te.Id)
O=raw.set_index('Id')
trp=O.loc[train.Id,'prediction'].fillna('unclear').to_numpy()
tp=O.loc[te.Id,'prediction'].fillna('unclear').to_numpy()
y=train.emotion.to_numpy();base=train.system_E_pred.to_numpy()
valid=np.isin(trp,C);trbase=base==y;tralt=trp==y
fix=(~trbase)&tralt;breaks=trbase&(~tralt)&valid
moved=(~trbase)&(~tralt)&(trp!=base)&valid
report={'n_train':826,'n_test':209,'baseline_E_f1':f1(y,base),
 'independent_expert_score':f1(y,trp),'valid_train':int(valid.sum()),
 'changed_train_vs_E':int(((trp!=base)&valid).sum()),
 'corrections':int(fix.sum()),'breakages':int(breaks.sum()),
 'wrong_to_other_wrong':int(moved.sum()),
 'new_expert_rescued_E_error_ids':train.Id[fix].astype(int).tolist(),
 'new_expert_broke_E_correct_ids':train.Id[breaks].astype(int).tolist(),
 'gold_classes_of_corrections':{c:int((fix&(y==c)).sum()) for c in C},
 'fold_complementarity':[],
 'not_a_candidate':True,'not_an_independently_fitted_nested_fusion':True,
 'target_labels_never_accessed':True}
for f in sorted(set(train.fold)):
 m=(train.fold.to_numpy()==f)
 report['fold_complementarity'].append({'fold':int(f),'n':int(m.sum()),'E_f1':f1(y[m],base[m]),
  'expert_f1':f1(y[m],trp[m]),'corrected_E_errors':int(fix[m].sum()),
  'broken_E_correct':int(breaks[m].sum()),
  'changed':int(((trp!=base)&valid&m).sum())})
# E test output never contains any protected ground truth; produce analysis-only disagreements.
tv=np.isin(tp,C)
test=pd.DataFrame({'Id':te.Id,'E':te.system_E_final,'omni':tp,
  'certified_retrieval':te.certified_retrieval,'cohort':te.cohort,
  'E_margin':te.E_margin})
test['disagrees']=tv & (tp!=test.E)
test['eligible_for_review']=test.disagrees&(~test.certified_retrieval)
report['test_valid_predictions']=int(tv.sum())
report['test_disagreements_before_certification']=int(test.disagrees.sum())
report['test_disagreements_noncertified']=int(test.eligible_for_review.sum())
report['test_certified_count']=int(te.certified_retrieval.sum())
assert report['test_certified_count']==78
# No selected threshold and no test label changes: files are diagnostic evidence only.
a.out.mkdir(exist_ok=True,parents=True)
if (a.out/'AUDIO_EXPERT_VS_E.json').exists():
 raise SystemExit('An evaluation already exists at --out; choose an independent directory')
(a.out/'AUDIO_EXPERT_VS_E.json').write_text(json.dumps(report,indent=2)+'\n')
test.sort_values(['eligible_for_review','E_margin'],ascending=[False,True]).to_csv(a.out/'TARGET209_REVIEW_ONLY.csv',index=False)
print(json.dumps({k:v for k,v in report.items() if k not in ('new_expert_rescued_E_error_ids','new_expert_broke_E_correct_ids','fold_complementarity')},indent=2))
print('PER_FOLD',report['fold_complementarity'])
