from pathlib import Path
import collections, json
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.metrics import f1_score, confusion_matrix

ROOT=Path('/mnt/data/defhs_work/SRCASW-BhavVaani')
OUT=Path('/mnt/data/defhs_ds002')
train=pd.read_csv(ROOT/'train.csv')
feat=pd.read_csv(OUT/'ACOUSTIC_FEATURES_FULL.csv')
groups=pd.read_csv(OUT/'DUPLICATE_GROUPS_FINAL.csv')

Ftr=feat[feat.split=='train'].set_index('Id').loc[train.Id]
y=train.emotion.to_numpy(); ids=train.Id.to_numpy()
basic=['duration_seconds','amplitude_peak_fullscale','rms_fullscale','dc_offset_fullscale','crest_factor','clip_fraction','silence_fraction','leading_silence_seconds','trailing_silence_seconds','pause_count','pause_fraction_frames','zcr_mean','spectral_centroid_mean','spectral_bandwidth_mean','spectral_rolloff85_mean','spectral_flatness_mean','onset_strength_mean','f0_yin_median','f0_yin_std']
full=[c for c in feat.columns if (c in basic or c.startswith('mfcc') or c.startswith('dmfcc') or c.startswith('logmel')) and pd.api.types.is_numeric_dtype(feat[c])]
Xb=Ftr[basic].replace([np.inf,-np.inf],np.nan)
Xf=Ftr[full].replace([np.inf,-np.inf],np.nan)
models={
 'BASIC_LOGREG':(Xb,make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LogisticRegression(max_iter=2000,C=1))),
 'FULL_LOGREG':(Xf,make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LogisticRegression(max_iter=2000,C=.3))),
 'FULL_LINEAR_SVM':(Xf,make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LinearSVC(C=.03))),
 'FULL_RBF_SVM':(Xf,make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),SVC(C=10,kernel='rbf',gamma='scale'))),
}
gid_by_id={int(r.Id):int(r.duplicate_group) for r in groups.itertuples(index=False) if r.split=='train'}
stable={int(i):f'{int(i):06d}' for i in ids}
for gid,g in groups[groups.split=='train'].groupby('duplicate_group'):
    mids=sorted(g.Id.astype(int)); token=f'{min(mids):06d}'
    for i in mids:stable[i]=token
garr=np.array([stable[int(i)] for i in ids])

def apply_ret(base,tr,vl):
    gl=collections.defaultdict(list)
    for p in tr:
        gid=gid_by_id.get(int(ids[p]))
        if gid is not None:gl[gid].append(y[p])
    cons={g:v[0] for g,v in gl.items() if len(set(v))==1}
    out=np.array(base,dtype=object); cov=np.zeros(len(vl),bool)
    for j,p in enumerate(vl):
        gid=gid_by_id.get(int(ids[p]))
        if gid in cons: out[j]=cons[gid];cov[j]=True
    return out,cov

rows=[]; oof=[]
for seed in [20260930,20260917,42]:
  for view in ['VA','VB']:
    if view=='VA': splitter=StratifiedKFold(5,shuffle=True,random_state=seed).split(Xf,y)
    else: splitter=StratifiedGroupKFold(5,shuffle=True,random_state=seed).split(Xf,y,garr)
    splits=list(splitter)
    for name,(X,m) in models.items():
      ser=np.empty(len(y),object);pipe=np.empty(len(y),object);cov=np.zeros(len(y),bool);folds=[];foldp=[]
      for f,(tr,vl) in enumerate(splits):
        m.fit(X.iloc[tr],y[tr]);p=m.predict(X.iloc[vl]);ser[vl]=p
        pp,cc=apply_ret(p,tr,vl);pipe[vl]=pp;cov[vl]=cc
        folds.append(float(f1_score(y[vl],p,average='macro')))
        foldp.append(float(f1_score(y[vl],pp,average='macro')))
      rec={'model':name,'seed':seed,'validation':view,'ser_macro_f1':float(f1_score(y,ser,average='macro')),'pipeline_macro_f1':float(f1_score(y,pipe,average='macro')),'retrieval_coverage':float(cov.mean()),'retrieval_accuracy':float(np.mean(pipe[cov]==y[cov])) if cov.any() else None,'nonretrieval_macro_f1':float(f1_score(y[~cov],ser[~cov],average='macro')),'fold_ser_macro_f1':folds,'fold_pipeline_macro_f1':foldp,'confusion_ser':confusion_matrix(y,ser,labels=['angry','happy','neutral','sad']).tolist()}
      rows.append(rec)
      if seed==20260930:
        for i in range(len(y)):oof.append({'Id':int(ids[i]),'emotion':y[i],'model':name,'validation':view,'ser_pred':ser[i],'pipeline_pred':pipe[i],'retrieval_covered':bool(cov[i])})
json.dump(rows,open(OUT/'VALIDATION_STABILITY_RESULTS.json','w'),indent=2)
pd.DataFrame(oof).to_csv(OUT/'VALIDATION_OOF_FIXED.csv',index=False)
pc=[]
for (name,view),g in pd.DataFrame(oof).groupby(['model','validation']):
    for cls in ['angry','happy','neutral','sad']:
        yy=g.emotion.eq(cls);pp=g.ser_pred.eq(cls);tp=int((yy&pp).sum());fp=int((~yy&pp).sum());fn=int((yy&~pp).sum())
        pc.append({'model':name,'validation':view,'class':cls,'f1':2*tp/(2*tp+fp+fn),'support':int(yy.sum())})
pd.DataFrame(pc).to_csv(OUT/'VALIDATION_PER_CLASS_F1.csv',index=False)
print(json.dumps([r for r in rows if r['seed']==20260930],indent=2))
