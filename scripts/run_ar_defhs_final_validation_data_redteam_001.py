#!/usr/bin/env python3
"""Bounded non-protected reproducer for AR-DEFHS-FINAL-VALIDATION-DATA-REDTEAM-001.

Forbidden input: VALIDATION_VP_PROTECTED_FOLDS.csv.
"""
from __future__ import annotations
import argparse, collections, hashlib, io, json, math, re, zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import wavfile
from scipy.stats import chi2_contingency
from sklearn.metrics import f1_score

CLASSES=["angry","happy","neutral","sad"]
DOM={0,30,43,86,94}

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def norm_wave(x):
    if x.ndim>1: x=x.mean(axis=1)
    y=np.asarray(x,dtype=np.float64); y-=y.mean()
    n=np.linalg.norm(y)
    return y/n if n else y

def macro(g,col):
    return float(f1_score(g.emotion,g[col],average="macro",labels=CLASSES))

def jsrng(seed):
    x=seed & 0xffffffff
    def r():
        nonlocal x
        x=(1664525*x+1013904223)&0xffffffff
        return x/4294967296.0
    return r

def sample_js(arr,n,r):
    a=list(arr)
    for i in range(len(a)-1,0,-1):
        j=int(r()*(i+1)); a[i],a[j]=a[j],a[i]
    return a[:n]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--duplicate-groups",type=Path,required=True)
    ap.add_argument("--oof",type=Path,required=True)
    ap.add_argument("--prompt",type=Path,required=True)
    ap.add_argument("--latent",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    if any("VP_PROTECTED" in str(p) for p in [a.manifest,a.duplicate_groups,a.oof,a.prompt,a.latent]):
        raise RuntimeError("Protected-gate input is forbidden")
    a.out.mkdir(parents=True,exist_ok=True)

    man=pd.read_csv(a.manifest)
    dup=pd.read_csv(a.duplicate_groups)
    oof=pd.read_csv(a.oof)
    prompt=pd.read_csv(a.prompt)
    latent=pd.read_csv(a.latent)

    # Raw RIFF/container and duplicate-component pairwise check.
    chunks=collections.Counter(); overhead=[]; riff_exact=0; waves={}
    with zipfile.ZipFile(a.zip) as zf:
        infos=[i for i in zf.infolist() if i.filename.lower().endswith(".wav")]
        for i in infos:
            raw=zf.read(i)
            if raw[:4]!=b"RIFF" or raw[8:12]!=b"WAVE": raise RuntimeError(i.filename)
            riff_exact += int(int.from_bytes(raw[4:8],"little")+8==len(raw))
            pos=12; seq=[]
            while pos+8<=len(raw):
                cid=raw[pos:pos+4].decode("latin1")
                n=int.from_bytes(raw[pos+4:pos+8],"little")
                seq.append(cid); pos+=8+n+(n%2)
            chunks[tuple(seq)]+=1
            Id=int(re.search(r"audio_(\d+)\.wav$",i.filename).group(1))
            row=man.loc[man.Id.eq(Id)].iloc[0]
            overhead.append(len(raw)-int(row.samples)*(int(row.sample_width_bits)//8))
        for r in dup.itertuples(index=False):
            member=f"SRCASW-BhavVaani/{r.split}/{r.filename}"
            _,x=wavfile.read(io.BytesIO(zf.read(member)))
            waves[int(r.Id)]=norm_wave(x)

    compmins=[]; crossmins=[]
    for _,g in dup.groupby("duplicate_group"):
        ids=g.Id.astype(int).tolist()
        sims=[float(waves[ids[i]]@waves[ids[j]])
              for i in range(len(ids)) for j in range(i+1,len(ids))
              if len(waves[ids[i]])==len(waves[ids[j]])]
        compmins.append(min(sims))
        if set(g.split)=={"train","test"}:
            ti=g.loc[g.split.eq("test"),"Id"].astype(int)
            ri=g.loc[g.split.eq("train"),"Id"].astype(int)
            cross=[float(waves[t]@waves[r]) for t in ti for r in ri if len(waves[t])==len(waves[r])]
            crossmins.append(min(cross))

    # Sample-count modulo source fingerprint.
    man["remainder128"]=man.samples.astype(int)%128
    man["rescat"]=man.remainder128.where(man.remainder128.isin(DOM),-1).astype(str)
    tr=man[man.split.eq("train")].copy()
    ct=pd.crosstab(tr.rescat,tr.emotion)
    chi,p,_,_=chi2_contingency(ct)
    cram=math.sqrt(chi/(len(tr)*(min(ct.shape)-1)))
    sct=pd.crosstab(man.rescat,man.split)
    schi,sp,_,_=chi2_contingency(sct)
    scram=math.sqrt(schi/(len(man)*(min(sct.shape)-1)))

    vb=oof[oof.validation.eq("VB")].merge(tr[["Id","rescat"]],on="Id")
    vb_rank=[]
    for rc,g in vb.groupby("rescat"):
        rec={"rescat":rc,"n":int(g.Id.nunique())}
        for model,gg in g.groupby("model"): rec[model]=macro(gg,"ser_pred")
        vb_rank.append(rec)

    # Exact correlated-allocation stress used in the review.
    dmap={int(r.Id):int(r.duplicate_group) for r in dup[dup.split.eq("train")].itertuples(index=False)}
    gs=collections.defaultdict(list)
    for r in prompt[prompt.split.eq("train")].itertuples(index=False):
        gs[getattr(r,"_13",None)].append(int(r.Id))
    # pandas mangles dotted names in itertuples, so use direct indexing for prompt.
    gs=collections.defaultdict(list)
    for _,r in prompt[prompt.split.eq("train")].iterrows():
        gs[r["prompt_sim_0.90"]].append(int(r.Id))
    p90=set()
    for arr in gs.values():
        if len(arr)<2: continue
        tokens={dmap.get(i,f"s:{i}") for i in arr}
        if len(tokens)>1: p90.update(arr)
    lk43=set(latent[(latent.split.eq("train"))&(latent.joint_k4.eq(3))].Id.astype(int))

    va=oof[oof.validation.eq("VA")].copy()
    models=sorted(va.model.unique())
    ids=sorted(tr.Id.astype(int).tolist())
    def scenario(name,S,q,reps=250):
        target=round(q*len(ids)); A=sorted(S); B=[i for i in ids if i not in S]
        wins={m:0 for m in models}; dsum=0.0
        for rep in range(reps):
            r=jsrng(20261001+rep*97+round(q*1000)+len(name))
            priv=set(A+sample_js(B,target-len(A),r)) if len(A)<target else set(sample_js(A,target,r))
            pub=set(ids)-priv
            scores=[]
            for m in models:
                gp=va[(va.model.eq(m))&va.Id.isin(pub)]
                gv=va[(va.model.eq(m))&va.Id.isin(priv)]
                scores.append((m,0.4*macro(gp,"pipeline_pred")+0.6*macro(gv,"pipeline_pred")))
            scores.sort(key=lambda x:-x[1]); wins[scores[0][0]]+=1
            sd=dict(scores); dsum+=sd["FULL_RBF_SVM"]-max(v for m,v in scores if m!="FULL_RBF_SVM")
        return {"top_frequency":{m:wins[m]/reps for m in models},"mean_rbf_minus_best_alt":dsum/reps}

    result={
      "protected_gate_queried":False,
      "raw_zip":{"sha256":sha256(a.zip),"wav_count":len(infos),"riff_exact":riff_exact,
                 "chunk_sequences":{"|".join(k):v for k,v in chunks.items()},
                 "overhead_unique":sorted(set(overhead))},
      "duplicate":{"components":len(compmins),"components_below_0_95":sum(v<0.95 for v in compmins),
                   "min_component_pairwise":min(compmins),"cross_components":len(crossmins),
                   "min_cross_test_train":min(crossmins)},
      "sample_modulo":{"dominant_remainders":sorted(DOM),"label_chi2":float(chi),"label_p":float(p),
                       "label_cramers_v":float(cram),"split_chi2":float(schi),"split_p":float(sp),
                       "split_cramers_v":float(scram),"vb_subgroup_rank":vb_rank},
      "emulator":{"prompt90_beyond_n":len(p90),"latent_k4_3_n":len(lk43),
                  "prompt90_q20":scenario("prompt90_beyond",p90,0.20),
                  "latent_k4_3_q20":scenario("latent_k4_3",lk43,0.20),
                  "latent_k4_3_q30":scenario("latent_k4_3",lk43,0.30)}
    }
    (a.out/"REDTEAM_REPRO_RESULTS.json").write_text(json.dumps(result,indent=2))
    pd.DataFrame(vb_rank).to_csv(a.out/"SAMPLE_COUNT_MODULO_VB_RANK.csv",index=False)
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
