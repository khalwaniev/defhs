#!/usr/bin/env python3
"""DS-DEFHS-VALIDATION-HARDENING-002: pretrained speaker-structure closure.

Extracts ECAPA-TDNN embeddings for all 1,035 competition clips and audits
speaker-like structure. It does NOT assert inferred clusters are true organizer
speaker IDs and does NOT evaluate the protected promotion gate.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
import torch, torchaudio
from huggingface_hub import HfApi, snapshot_download
from sklearn.cluster import AgglomerativeClustering, DBSCAN
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from speechbrain.inference.speaker import EncoderClassifier

MODEL_ID="speechbrain/spkrec-ecapa-voxceleb"

def sha256(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024), b""): h.update(b)
    return h.hexdigest()

def load_manifest(root: Path) -> pd.DataFrame:
    tr=pd.read_csv(root/"train.csv").assign(split="train")
    te=pd.read_csv(root/"test.csv").assign(split="test", emotion=np.nan)
    return pd.concat([tr,te],ignore_index=True).sort_values("Id").reset_index(drop=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-root",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--revision",default=None,help="HF revision; if omitted resolve current immutable SHA first")
    ap.add_argument("--device",default="cuda" if torch.cuda.is_available() else "cpu")
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    info=HfApi().model_info(MODEL_ID,revision=a.revision)
    resolved=info.sha
    local=snapshot_download(repo_id=MODEL_ID,revision=resolved)
    clf=EncoderClassifier.from_hparams(source=local,run_opts={"device":a.device})
    df=load_manifest(a.data_root)
    embs=[]; meta=[]
    for r in df.itertuples(index=False):
        p=a.data_root/r.split/r.filename
        wav,sr=torchaudio.load(str(p))
        if wav.shape[0]>1: wav=wav.mean(0,keepdim=True)
        if sr!=16000: wav=torchaudio.functional.resample(wav,sr,16000)
        with torch.inference_mode():
            z=clf.encode_batch(wav.to(a.device)).detach().cpu().numpy().reshape(-1)
        z=z.astype(np.float32); z/=max(float(np.linalg.norm(z)),1e-12)
        embs.append(z)
        meta.append({"Id":int(r.Id),"split":r.split,"filename":r.filename,
                     "emotion":None if pd.isna(r.emotion) else str(r.emotion)})
    E=np.stack(embs)
    np.save(a.out/"SPEAKER_EMBEDDINGS_ECAPA.npy",E)
    md=pd.DataFrame(meta); md.to_csv(a.out/"SPEAKER_EMBEDDING_METADATA.csv",index=False)
    C=E@E.T
    dup=pd.read_csv(a.out/"DUPLICATE_GROUPS_FINAL.csv") if (a.out/"DUPLICATE_GROUPS_FINAL.csv").exists() else None
    idx={int(v):i for i,v in enumerate(md.Id)}
    dup_sims=[]
    if dup is not None:
        for _,g in dup.groupby("duplicate_group"):
            ii=[idx[int(x)] for x in g.Id if int(x) in idx]
            for x in range(len(ii)):
                for y in range(x+1,len(ii)): dup_sims.append(float(C[ii[x],ii[y]]))
    rng=np.random.default_rng(20260930); non=[]
    dup_gid={}
    if dup is not None:
        for r in dup.itertuples(index=False): dup_gid[int(r.Id)]=int(r.duplicate_group)
    while len(non)<min(20000,len(md)*(len(md)-1)//2):
        i,j=rng.integers(0,len(md),2)
        if i==j: continue
        if dup_gid.get(int(md.Id.iloc[i]))==dup_gid.get(int(md.Id.iloc[j])) and int(md.Id.iloc[i]) in dup_gid: continue
        non.append(float(C[i,j]))
    thresholds=[0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50]
    assignments={}; rows=[]
    for d in thresholds:
        lab=AgglomerativeClustering(n_clusters=None,distance_threshold=d,metric="cosine",linkage="average").fit_predict(E)
        assignments[f"agg_d{d:.2f}"]=lab
        ncl=len(np.unique(lab)); mixed=0; covered=0
        for k in np.unique(lab):
            q=md[lab==k]
            if len(q)>=2:
                covered+=len(q)
                if set(q.split)=={"train","test"}: mixed+=1
        rows.append({"method":"agglomerative","distance_threshold":d,"clusters":ncl,
                     "clips_in_non_singletons":covered,"train_test_mixed_clusters":mixed})
    for eps in [0.10,0.15,0.20,0.25,0.30,0.35]:
        lab=DBSCAN(eps=eps,min_samples=2,metric="cosine",n_jobs=-1).fit_predict(E)
        assignments[f"dbscan_e{eps:.2f}"]=lab
        rows.append({"method":"dbscan","distance_threshold":eps,
                     "clusters":int(len(set(lab))-(-1 in set(lab))),
                     "clips_in_non_singletons":int(np.sum(lab>=0)),
                     "train_test_mixed_clusters":int(sum(set(md[lab==k].split)=={"train","test"} for k in set(lab) if k>=0))})
    A=pd.DataFrame(assignments)
    out=pd.concat([md,A],axis=1); out.to_csv(a.out/"SPEAKER_CLUSTER_ASSIGNMENTS.csv",index=False)
    aris=[]
    aggcols=[c for c in A if c.startswith("agg_")]
    for x,y in zip(aggcols[:-1],aggcols[1:]):
        aris.append({"a":x,"b":y,"ari":float(adjusted_rand_score(A[x],A[y]))})
    dtype_path=a.out/"DATA_MANIFEST.csv"
    dtype_nmi={}
    if dtype_path.exists():
        dm=pd.read_csv(dtype_path).set_index("Id")
        dtype=np.array([str(dm.loc[int(i),"dtype"]) for i in md.Id])
        for c in aggcols: dtype_nmi[c]=float(normalized_mutual_info_score(dtype,A[c]))
    summary={
      "model_id":MODEL_ID,"resolved_revision":resolved,"device":a.device,
      "embedding_shape":list(E.shape),
      "duplicate_similarity":{"n":len(dup_sims),"min":min(dup_sims) if dup_sims else None,
                              "median":float(np.median(dup_sims)) if dup_sims else None},
      "nonduplicate_similarity":{"n":len(non),"p50":float(np.median(non)),"p95":float(np.quantile(non,.95)),
                                 "p99":float(np.quantile(non,.99))},
      "adjacent_threshold_ari":aris,"dtype_nmi":dtype_nmi,
      "cluster_sweep":rows,
      "interpretation_rule":"Clusters are speaker-like hypotheses only; true organizer speaker IDs are not asserted."
    }
    (a.out/"SPEAKER_AUDIT_RESULTS.json").write_text(json.dumps(summary,indent=2))
    manifest={"artifact":"SPEAKER_EMBEDDINGS_ECAPA.npy","model_id":MODEL_ID,"resolved_revision":resolved,
              "shape":list(E.shape),"dtype":str(E.dtype),"sha256":sha256(a.out/"SPEAKER_EMBEDDINGS_ECAPA.npy"),
              "metadata_sha256":sha256(a.out/"SPEAKER_EMBEDDING_METADATA.csv")}
    (a.out/"SPEAKER_EMBEDDING_MANIFEST.json").write_text(json.dumps(manifest,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
