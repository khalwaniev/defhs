#!/usr/bin/env python3
"""DS-002 standardized paralinguistic closure using openSMILE eGeMAPSv02."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np, pandas as pd, opensmile
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data-root",type=Path,required=True); ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    tr=pd.read_csv(a.data_root/"train.csv").assign(split="train")
    te=pd.read_csv(a.data_root/"test.csv").assign(split="test",emotion=np.nan)
    df=pd.concat([tr,te],ignore_index=True).sort_values("Id").reset_index(drop=True)
    smile=opensmile.Smile(feature_set=opensmile.FeatureSet.eGeMAPSv02,feature_level=opensmile.FeatureLevel.Functionals)
    rows=[]
    for r in df.itertuples(index=False):
        p=a.data_root/r.split/r.filename; q=smile.process_file(str(p)).reset_index(drop=True)
        d=q.iloc[0].to_dict(); d.update({"Id":int(r.Id),"split":r.split,"filename":r.filename,
          "emotion":None if pd.isna(r.emotion) else str(r.emotion)}); rows.append(d)
    F=pd.DataFrame(rows); F.to_csv(a.out/"EGEMAPS_FEATURES.csv",index=False)
    feature_cols=[c for c in F if c not in {"Id","split","filename","emotion"}]
    # train/test adversarial diagnostic on standardized features
    X=F[feature_cols].replace([np.inf,-np.inf],np.nan); ysplit=F.split.eq("test").astype(int).to_numpy()
    auc=[]
    for seed in [20260930,20260917,42]:
        cv=StratifiedKFold(5,shuffle=True,random_state=seed); p=np.zeros(len(F))
        for trix,vix in cv.split(X,ysplit):
            m=make_pipeline(SimpleImputer(strategy="median"),StandardScaler(),LogisticRegression(max_iter=2000,C=.3,class_weight="balanced"))
            m.fit(X.iloc[trix],ysplit[trix]); p[vix]=m.predict_proba(X.iloc[vix])[:,1]
        auc.append(float(roc_auc_score(ysplit,p)))
    # exact frozen V-A/V-B memberships, never protected VP
    train=F[F.split=="train"].copy().set_index("Id")
    val={}
    for view,file in [("VA","VALIDATION_VA_FOLDS.csv"),("VB","VALIDATION_VB_FOLDS.csv")]:
        folds=pd.read_csv(a.out/file).set_index("Id")
        yy=train.emotion.astype(str).to_numpy(); XX=train[feature_cols]
        foldarr=folds.loc[train.index,"fold"].to_numpy(); pred=np.empty(len(train),dtype=object); fs=[]
        for f in sorted(np.unique(foldarr)):
            tri=np.where(foldarr!=f)[0]; vi=np.where(foldarr==f)[0]
            m=make_pipeline(SimpleImputer(strategy="median"),StandardScaler(),LogisticRegression(max_iter=2000,C=.3))
            m.fit(XX.iloc[tri],yy[tri]); pred[vi]=m.predict(XX.iloc[vi]); fs.append(float(f1_score(yy[vi],pred[vi],average="macro")))
        val[view]={"oof_macro_f1":float(f1_score(yy,pred,average="macro")),"fold_macro_f1":fs}
    dm=pd.read_csv(a.out/"DATA_MANIFEST.csv").set_index("Id")
    # standardized mean-difference rankings train vs test and dtype
    effect=[]
    for c in feature_cols:
        z=pd.to_numeric(F[c],errors="coerce")
        aa=z[F.split=="train"]; bb=z[F.split=="test"]; sp=np.sqrt((aa.var()+bb.var())/2)
        effect.append({"feature":c,"train_test_smd":float((bb.mean()-aa.mean())/sp) if sp>0 else 0.0})
    pd.DataFrame(effect).sort_values("train_test_smd",key=lambda x:x.abs(),ascending=False).to_csv(a.out/"EGEMAPS_SHIFT_SUMMARY.csv",index=False)
    summary={"opensmile_version":opensmile.__version__,"feature_set":"eGeMAPSv02","feature_level":"Functionals",
      "feature_count":len(feature_cols),"train_test_logreg_auc_runs":auc,
      "train_test_logreg_auc_mean":float(np.mean(auc)),"validation":val}
    (a.out/"EGEMAPS_AUDIT_RESULTS.json").write_text(json.dumps(summary,indent=2))
    (a.out/"EGEMAPS_MANIFEST.json").write_text(json.dumps({"opensmile_version":opensmile.__version__,
      "features_sha256":sha256(a.out/"EGEMAPS_FEATURES.csv"),"rows":len(F),"features":len(feature_cols)},indent=2))
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
