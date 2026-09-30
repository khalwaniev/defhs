#!/usr/bin/env python3
"""DS-002 joint latent-regime audit after ECAPA + ASR + eGeMAPS execution.

This script characterizes stable latent regimes. It never labels a regime
"acted" or "spontaneous" without external ground truth.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, silhouette_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.decomposition import PCA

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    sp=pd.read_csv(a.out/"SPEAKER_CLUSTER_ASSIGNMENTS.csv")
    tx=pd.read_csv(a.out/"PROMPT_CLUSTER_ASSIGNMENTS.csv")
    eg=pd.read_csv(a.out/"EGEMAPS_FEATURES.csv")
    dm=pd.read_csv(a.out/"DATA_MANIFEST.csv")
    base=dm[["Id","split","emotion","dtype","duration_seconds"]].merge(sp,on=["Id","split","filename"],how="left",suffixes=("","_sp"))
    keep_tx=[c for c in tx.columns if c=="Id" or c.startswith("prompt_sim_") or c in {"normalized_transcript","avg_logprob","no_speech_prob"}]
    base=base.merge(tx[keep_tx],on="Id",how="left")
    eg_cols=[c for c in eg.columns if c not in {"Id","split","filename","emotion"}]
    Xeg=eg.set_index("Id").loc[base.Id,eg_cols].replace([np.inf,-np.inf],np.nan)
    Xeg=SimpleImputer(strategy="median").fit_transform(Xeg); Xeg=StandardScaler().fit_transform(Xeg)
    # keep eGeMAPS contribution bounded; summarize by principal components
    pca=PCA(n_components=min(12,Xeg.shape[1]),random_state=20260930)
    Zeg=pca.fit_transform(Xeg)
    speaker_cols=[c for c in sp.columns if c.startswith("agg_d")]
    prompt_cols=[c for c in tx.columns if c.startswith("prompt_sim_")]
    # choose central thresholds only as categorical evidence; audit alternate thresholds separately.
    sc=speaker_cols[len(speaker_cols)//2] if speaker_cols else None
    pc=prompt_cols[len(prompt_cols)//2] if prompt_cols else None
    cats=pd.DataFrame({"dtype":base.dtype.astype(str)})
    if sc: cats["speaker_like"]=sp.set_index("Id").loc[base.Id,sc].astype(str).to_numpy()
    if pc: cats["prompt_like"]=tx.set_index("Id").loc[base.Id,pc].astype(str).to_numpy()
    enc=OneHotEncoder(handle_unknown="ignore",sparse_output=False,min_frequency=2)
    Zcat=enc.fit_transform(cats)
    Z=np.hstack([Zeg,Zcat])
    results=[]; labels={}
    for k in [2,3,4,5,6]:
        lab=KMeans(n_clusters=k,random_state=20260930,n_init=30).fit_predict(Z)
        labels[f"joint_k{k}"]=lab
        sil=float(silhouette_score(Z,lab))
        dtype_nmi=float(normalized_mutual_info_score(base.dtype.astype(str),lab))
        split_nmi=float(normalized_mutual_info_score(base.split.astype(str),lab))
        emotion_nmi=float(normalized_mutual_info_score(base.emotion.fillna("TEST").astype(str),lab))
        results.append({"k":k,"silhouette":sil,"dtype_nmi":dtype_nmi,"split_nmi":split_nmi,"emotion_or_test_nmi":emotion_nmi})
    L=pd.DataFrame(labels)
    adjacent=[]
    cols=list(L)
    for x,y in zip(cols[:-1],cols[1:]): adjacent.append({"a":x,"b":y,"ari":float(adjusted_rand_score(L[x],L[y]))})
    out=pd.concat([base[["Id","split","emotion","dtype","duration_seconds"]],L],axis=1)
    out.to_csv(a.out/"LATENT_REGIME_ASSIGNMENTS.csv",index=False)
    summary={
      "purpose":"latent-regime characterization after speaker/ASR/eGeMAPS evidence",
      "acted_spontaneous_ground_truth_available":False,
      "selected_speaker_cluster_column":sc,"selected_prompt_cluster_column":pc,
      "egemaps_pca_explained_variance":float(pca.explained_variance_ratio_.sum()),
      "joint_cluster_results":results,"adjacent_k_ari":adjacent,
      "interpretation_rule":"Do not name clusters acted/spontaneous. A strong stable latent partition may justify V-D-like stress only after scientific review."
    }
    (a.out/"LATENT_REGIME_AUDIT_RESULTS.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
