#!/usr/bin/env python3
"""DS-002 Hindi ASR/prompt-structure closure. No SER modeling or protected-gate use."""
from __future__ import annotations
import argparse, hashlib, json, re, unicodedata
from pathlib import Path
import numpy as np, pandas as pd
from faster_whisper import WhisperModel
from huggingface_hub import HfApi, snapshot_download
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import normalized_mutual_info_score
from sklearn.metrics.pairwise import cosine_similarity

MODEL_ID="mobiuslabsgmbh/faster-whisper-large-v3-turbo"

def norm_text(s):
    s=unicodedata.normalize("NFKC",s or "").lower().strip()
    s=re.sub(r"[^\w\s\u0900-\u097f]"," ",s,flags=re.UNICODE)
    return re.sub(r"\s+"," ",s).strip()

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-root",type=Path,required=True); ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--revision",default=None); ap.add_argument("--device",default="cuda")
    ap.add_argument("--compute-type",default="float16")
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    tr=pd.read_csv(a.data_root/"train.csv").assign(split="train")
    te=pd.read_csv(a.data_root/"test.csv").assign(split="test",emotion=np.nan)
    df=pd.concat([tr,te],ignore_index=True).sort_values("Id").reset_index(drop=True)
    info=HfApi().model_info(MODEL_ID,revision=a.revision); rev=info.sha
    local=snapshot_download(repo_id=MODEL_ID,revision=rev)
    model=WhisperModel(local,device=a.device,compute_type=a.compute_type)
    rec=[]
    for r in df.itertuples(index=False):
        p=a.data_root/r.split/r.filename
        segs,info=model.transcribe(str(p),language="hi",beam_size=5,vad_filter=True,
                                   condition_on_previous_text=False,word_timestamps=False)
        segs=list(segs); text=" ".join(s.text.strip() for s in segs).strip()
        dur=sum(max(0.0,s.end-s.start) for s in segs)
        avg_lp=float(np.mean([s.avg_logprob for s in segs])) if segs else np.nan
        no_speech=float(np.mean([s.no_speech_prob for s in segs])) if segs else np.nan
        comp=float(np.mean([s.compression_ratio for s in segs])) if segs else np.nan
        rec.append({"Id":int(r.Id),"split":r.split,"filename":r.filename,
                    "emotion":None if pd.isna(r.emotion) else str(r.emotion),
                    "transcript":text,"normalized_transcript":norm_text(text),
                    "detected_language":getattr(info,"language",None),
                    "language_probability":getattr(info,"language_probability",None),
                    "segments":len(segs),"decoded_seconds":dur,"avg_logprob":avg_lp,
                    "no_speech_prob":no_speech,"compression_ratio":comp})
    T=pd.DataFrame(rec); T.to_csv(a.out/"ASR_TRANSCRIPTS.csv",index=False)
    texts=T.normalized_transcript.fillna("").tolist()
    vec=TfidfVectorizer(analyzer="char_wb",ngram_range=(3,5),min_df=1,norm="l2")
    X=vec.fit_transform(texts); S=cosine_similarity(X,dense_output=True)
    np.fill_diagonal(S,-1)
    thresholds=[.80,.85,.90,.95,.98]
    sweeps=[]
    assignments={}
    D=1-np.clip(S,-1,1); np.fill_diagonal(D,0)
    for sim in thresholds:
        lab=AgglomerativeClustering(n_clusters=None,distance_threshold=1-sim,metric="precomputed",linkage="average").fit_predict(D)
        assignments[f"prompt_sim_{sim:.2f}"]=lab
        mixed=sum(set(T[lab==k].split)=={"train","test"} for k in np.unique(lab) if np.sum(lab==k)>1)
        sweeps.append({"similarity_threshold":sim,"clusters":int(len(np.unique(lab))),
                       "clips_non_singleton":int(sum(np.sum(lab==k) for k in np.unique(lab) if np.sum(lab==k)>1)),
                       "train_test_mixed_non_singleton_clusters":int(mixed)})
    pd.concat([T,pd.DataFrame(assignments)],axis=1).to_csv(a.out/"PROMPT_CLUSTER_ASSIGNMENTS.csv",index=False)
    dup=pd.read_csv(a.out/"DUPLICATE_GROUPS_FINAL.csv")
    ii={int(v):i for i,v in enumerate(T.Id)}; dup_sim=[]
    for _,g in dup.groupby("duplicate_group"):
        ids=[ii[int(x)] for x in g.Id if int(x) in ii]
        for x in range(len(ids)):
            for y in range(x+1,len(ids)): dup_sim.append(float(S[ids[x],ids[y]]))
    exact=T.groupby("normalized_transcript").filter(lambda g:len(g)>=2)
    class_nmi={}
    trainmask=T.split.eq("train").to_numpy()
    y=T.loc[trainmask,"emotion"].astype(str).to_numpy()
    for c,lab in assignments.items(): class_nmi[c]=float(normalized_mutual_info_score(y,np.asarray(lab)[trainmask]))
    summary={
      "model_id":MODEL_ID,"resolved_revision":rev,"language_setting":"hi","rows":len(T),
      "empty_transcripts":int(T.normalized_transcript.eq("").sum()),
      "quality":{"avg_logprob_median":float(T.avg_logprob.median()),"language_probability_median":float(T.language_probability.median()),
                 "duplicate_text_similarity_median":float(np.median(dup_sim)) if dup_sim else None,
                 "duplicate_text_similarity_p10":float(np.quantile(dup_sim,.1)) if dup_sim else None},
      "exact_repeated_transcript_rows":int(len(exact)),"prompt_cluster_sweep":sweeps,"train_class_nmi":class_nmi
    }
    (a.out/"ASR_PROMPT_AUDIT_RESULTS.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    (a.out/"ASR_MANIFEST.json").write_text(json.dumps({"model_id":MODEL_ID,"resolved_revision":rev,
      "language":"hi","transcript_sha256":sha256(a.out/"ASR_TRANSCRIPTS.csv")},indent=2))
    print(json.dumps(summary,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
