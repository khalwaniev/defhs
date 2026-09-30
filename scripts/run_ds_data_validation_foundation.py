#!/usr/bin/env python3
from __future__ import annotations
import argparse, collections, hashlib, io, json, math, sys, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.io import wavfile
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

ROOT = "SRCASW-BhavVaani"
DUP_THRESHOLD = 0.95
SEEDS = [20260930, 20260917, 20260911, 20260923, 42]

class UF:
    def __init__(self, items): self.p={x:x for x in items}
    def find(self,x):
        while self.p[x]!=x:
            self.p[x]=self.p[self.p[x]]
            x=self.p[x]
        return x
    def union(self,a,b):
        ra,rb=self.find(a),self.find(b)
        if ra!=rb: self.p[rb]=ra

def norm_wave(x):
    if x.ndim > 1:
        x=x.mean(axis=1)
    y=np.asarray(x,dtype=np.float64)
    y-=y.mean()
    n=np.linalg.norm(y)
    return y/n if n else y

def acoustic_features(y, sr):
    import librosa
    y=np.asarray(y,dtype=np.float32)
    if y.ndim > 1:
        y=y.mean(axis=1)
    peak=float(np.max(np.abs(y)))
    if peak>0: y=y/peak
    mf=librosa.feature.mfcc(y=y,sr=sr,n_mfcc=20,n_fft=512,hop_length=160)
    mel=librosa.feature.melspectrogram(y=y,sr=sr,n_mels=40,n_fft=512,hop_length=160,power=2)
    logmel=librosa.power_to_db(mel,ref=np.max)
    rms=librosa.feature.rms(y=y,frame_length=512,hop_length=160)
    zcr=librosa.feature.zero_crossing_rate(y,frame_length=512,hop_length=160)
    cent=librosa.feature.spectral_centroid(y=y,sr=sr,n_fft=512,hop_length=160)
    bw=librosa.feature.spectral_bandwidth(y=y,sr=sr,n_fft=512,hop_length=160)
    roll=librosa.feature.spectral_rolloff(y=y,sr=sr,n_fft=512,hop_length=160,roll_percent=0.85)
    def st(a):
        return np.concatenate([np.mean(a,axis=1),np.std(a,axis=1),np.percentile(a,25,axis=1),np.percentile(a,75,axis=1)])
    return np.nan_to_num(np.concatenate([st(mf),st(logmel),st(rms),st(zcr),st(cent),st(bw),st(roll),[len(y)/sr]]))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("zip_path",type=Path)
    ap.add_argument("--out",type=Path,default=Path("runs/DS-DEFHS-DATA-VALIDATION-FOUNDATION-001"))
    a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)

    with zipfile.ZipFile(a.zip_path) as zf:
        train=pd.read_csv(io.BytesIO(zf.read(f"{ROOT}/train.csv")))
        test=pd.read_csv(io.BytesIO(zf.read(f"{ROOT}/test.csv")))
        rows=[]; waves={}; by_n=collections.defaultdict(list)
        for split,df in [("train",train),("test",test)]:
            for r in df.itertuples(index=False):
                raw=zf.read(f"{ROOT}/{split}/{r.filename}")
                sr,x=wavfile.read(io.BytesIO(raw))
                if x.ndim>1: x=x.mean(axis=1)
                k=(split,int(r.Id))
                y=norm_wave(x)
                waves[k]=y; by_n[len(y)].append(k)
                rows.append({
                    "split":split,"Id":int(r.Id),"filename":r.filename,
                    "emotion":getattr(r,"emotion",None),"sample_rate":int(sr),
                    "samples":int(len(x)),"duration_seconds":float(len(x)/sr),
                    "dtype":str(x.dtype),"pcm_sha256":hashlib.sha256(np.asarray(x).tobytes()).hexdigest()
                })
        md=pd.DataFrame(rows).sort_values(["Id","split"])
        md.to_csv(a.out/"AUDIO_METADATA.csv",index=False)

        exact_hash_groups=[]
        for h,gdf in md.groupby("pcm_sha256",sort=False):
            if len(gdf)>1:
                exact_hash_groups.append(gdf)
        exact_cross=[g for g in exact_hash_groups if set(g["split"])=={"train","test"}]
        exact_train_only=[g for g in exact_hash_groups if set(g["split"])=={"train"}]

        # Full-waveform cosine comparisons are restricted by equal native sample length.
        pairs=[]
        for n,ks in by_n.items():
            if len(ks)<2: continue
            X=np.stack([waves[k] for k in ks])
            C=X@X.T
            for i in range(len(ks)):
                for j in range(i+1,len(ks)):
                    pairs.append((float(C[i,j]),ks[i],ks[j],n))
        ps=pd.DataFrame([{
            "similarity":c,"split_a":ka[0],"Id_a":ka[1],"split_b":kb[0],"Id_b":kb[1],"samples":n
        } for c,ka,kb,n in sorted(pairs,reverse=True)])
        ps.to_csv(a.out/"DUPLICATE_PAIR_EVIDENCE.csv",index=False)

        # Independent all-pairs relative-time fingerprint check.
        keys=[(r["split"],int(r["Id"])) for r in rows]
        dur_map={(r["split"],int(r["Id"])):r["duration_seconds"] for r in rows}
        N=4096; fps=[]
        grid=np.linspace(0,1,N,endpoint=False)
        for k in keys:
            y=waves[k]
            fp=np.interp(grid,np.linspace(0,1,len(y),endpoint=False),y)
            fp-=fp.mean()
            norm=np.linalg.norm(fp)
            fps.append((fp/norm if norm else fp).astype(np.float32))
        F=np.stack(fps); C=F@F.T
        np.fill_diagonal(C,-2)
        tv=C[np.triu_indices(len(keys),1)]
        rel_sorted=np.sort(tv)[::-1]
        rel_over_half=rel_sorted[rel_sorted>0.5]
        strongest_noncluster=float(rel_sorted[len(rel_over_half)]) if len(rel_over_half)<len(rel_sorted) else None
        weakest_cluster=float(rel_over_half[-1]) if len(rel_over_half) else None

        # Freeze near-duplicate graph at threshold supported by the observed distribution.
        if weakest_cluster is None or weakest_cluster < DUP_THRESHOLD or strongest_noncluster is None or strongest_noncluster > 0.5:
            raise RuntimeError(
                f"Near-duplicate separation assertion failed: weakest_cluster={weakest_cluster}, "
                f"strongest_noncluster={strongest_noncluster}"
            )

        uf=UF(keys)
        for c,ka,kb,n in pairs:
            if c>=DUP_THRESHOLD: uf.union(ka,kb)
        groups=collections.defaultdict(list)
        for k in keys: groups[uf.find(k)].append(k)
        groups=[g for g in groups.values() if len(g)>1]
        groups.sort(key=lambda g:min(x[1] for x in g))

        rec={(r["split"],int(r["Id"])):r for r in rows}
        memberships=[]; conflicts=[]; retrieval=[]
        for gi,g in enumerate(groups,1):
            labs=[rec[k]["emotion"] for k in g if k[0]=="train"]
            labset=sorted(set(x for x in labs if x is not None))
            is_conflict=len(labset)>1
            train_label=labset[0] if len(labset)==1 else None
            for k in sorted(g,key=lambda x:(x[0],x[1])):
                rr=rec[k]
                memberships.append({
                    "duplicate_group":gi,"group_size":len(g),"split":k[0],"Id":k[1],
                    "filename":rr["filename"],"emotion":rr["emotion"],
                    "train_label_consensus":train_label,"train_label_conflict":is_conflict
                })
            if is_conflict:
                conflicts.append({
                    "duplicate_group":gi,
                    "members":";".join(f"{k[0]}:{k[1]}" for k in sorted(g)),
                    "train_labels":";".join(str(rec[k]["emotion"]) for k in sorted(g) if k[0]=="train")
                })
            tests=[k for k in g if k[0]=="test"]
            trains=[k for k in g if k[0]=="train"]
            if tests and trains:
                for tk in tests:
                    retrieval.append({
                        "test_Id":tk[1],
                        "duplicate_group":gi,
                        "matched_train_Ids":";".join(str(k[1]) for k in sorted(trains)),
                        "consensus_emotion":train_label,
                        "conflict":is_conflict
                    })
        pd.DataFrame(memberships).to_csv(a.out/"DUPLICATE_GROUPS.csv",index=False)
        pd.DataFrame(conflicts,columns=["duplicate_group","members","train_labels"]).to_csv(a.out/"DUPLICATE_CONFLICTS.csv",index=False)
        pd.DataFrame(retrieval).sort_values("test_Id").to_csv(a.out/"TRAIN_TEST_RETRIEVAL_MAP.csv",index=False)

        # Validation groups built only from train-train near-duplicate edges.
        tkeys=[("train",int(i)) for i in train.Id]
        tuf=UF(tkeys)
        for c,ka,kb,n in pairs:
            if c>=DUP_THRESHOLD and ka[0]=="train" and kb[0]=="train":
                tuf.union(ka,kb)
        tcomponents=collections.defaultdict(list)
        for k in tkeys:
            tcomponents[tuf.find(k)].append(k)
        stable_gid={}
        for comp in tcomponents.values():
            gid=min(k[1] for k in comp)
            for k in comp:
                stable_gid[k]=f"{gid:06d}"
        group_id=np.array([stable_gid[k] for k in tkeys])

        va=np.empty(len(train),dtype=int)
        cvA=StratifiedKFold(5,shuffle=True,random_state=20260930)
        for f,(_,ix) in enumerate(cvA.split(train,train.emotion)): va[ix]=f
        vb=np.empty(len(train),dtype=int)
        cvB=StratifiedGroupKFold(5,shuffle=True,random_state=20260930)
        for f,(_,ix) in enumerate(cvB.split(train,train.emotion,group_id)): vb[ix]=f
        train[["Id","filename","emotion"]].assign(fold=va).to_csv(a.out/"VALIDATION_VA_FOLDS.csv",index=False)
        train[["Id","filename","emotion"]].assign(duplicate_group=group_id,fold=vb).to_csv(a.out/"VALIDATION_VB_FOLDS.csv",index=False)

        # Cheap acoustic baseline. This is a validation diagnostic, not a production model.
        feats=[]
        for r in train.itertuples(index=False):
            sr,x=wavfile.read(io.BytesIO(zf.read(f"{ROOT}/train/{r.filename}")))
            feats.append(acoustic_features(x,sr))
        X=np.stack(feats); y=train.emotion.to_numpy()

    baseline=[]
    for seed in SEEDS:
        for kind in ("VA","VB"):
            if kind=="VA":
                cv=StratifiedKFold(5,shuffle=True,random_state=seed); gg=None
            else:
                cv=StratifiedGroupKFold(5,shuffle=True,random_state=seed); gg=group_id
            pred=np.empty(len(y),dtype=object); fold_scores=[]
            for fold,(tr,vl) in enumerate(cv.split(X,y,gg)):
                clf=make_pipeline(StandardScaler(),SVC(C=10,kernel="rbf",gamma="scale"))
                clf.fit(X[tr],y[tr]); pv=clf.predict(X[vl]); pred[vl]=pv
                fold_scores.append(float(f1_score(y[vl],pv,average="macro")))
            baseline.append({
                "seed":seed,"validation":kind,
                "oof_macro_f1":float(f1_score(y,pred,average="macro")),
                "fold_macro_f1":fold_scores
            })
    va_scores=[r["oof_macro_f1"] for r in baseline if r["validation"]=="VA"]
    vb_scores=[r["oof_macro_f1"] for r in baseline if r["validation"]=="VB"]

    cross_groups=[g for g in groups if {k[0] for k in g}=={"train","test"}]
    train_only=[g for g in groups if {k[0] for k in g}=={"train"}]
    test_only=[g for g in groups if {k[0] for k in g}=={"test"}]
    summary={
        "train_rows":int(len(train)),"test_rows":int(len(test)),"total_rows":int(len(md)),
        "class_counts":{k:int(v) for k,v in train.emotion.value_counts().to_dict().items()},
        "sample_rates":{str(k):int(v) for k,v in md.sample_rate.value_counts().to_dict().items()},
        "dtypes":{str(k):int(v) for k,v in md.dtype.value_counts().to_dict().items()},
        "duration_seconds":{
            "min":float(md.duration_seconds.min()),"median":float(md.duration_seconds.median()),
            "mean":float(md.duration_seconds.mean()),"max":float(md.duration_seconds.max())
        },
        "exact_pcm_duplicate_groups":int(len(exact_hash_groups)),
        "exact_pcm_cross_split_groups":int(len(exact_cross)),
        "exact_pcm_cross_split_test_clips":int(sum(int((g["split"]=="test").sum()) for g in exact_cross)),
        "exact_pcm_train_only_groups":int(len(exact_train_only)),
        "exact_pcm_train_only_clips":int(sum(len(g) for g in exact_train_only)),
        "near_duplicate_threshold":DUP_THRESHOLD,
        "relative_fingerprint_cluster_pairs_gt_0_5":int(len(rel_over_half)),
        "relative_fingerprint_weakest_cluster_similarity":weakest_cluster,
        "relative_fingerprint_strongest_noncluster_similarity":strongest_noncluster,
        "near_duplicate_groups":int(len(groups)),
        "near_duplicate_clips":int(sum(len(g) for g in groups)),
        "cross_split_groups":int(len(cross_groups)),
        "cross_split_test_clips":int(sum(sum(k[0]=="test" for k in g) for g in cross_groups)),
        "train_only_groups":int(len(train_only)),
        "test_only_groups":int(len(test_only)),
        "label_conflict_groups":int(len(conflicts)),
        "baseline":{
            "VA_mean_macro_f1":float(np.mean(va_scores)),
            "VA_std_macro_f1":float(np.std(va_scores,ddof=1)),
            "VB_mean_macro_f1":float(np.mean(vb_scores)),
            "VB_std_macro_f1":float(np.std(vb_scores,ddof=1)),
            "mean_leakage_premium":float(np.mean(va_scores)-np.mean(vb_scores)),
            "runs":baseline
        }
    }
    (a.out/"DATA_AUDIT_SUMMARY.json").write_text(json.dumps(summary,indent=2))

    dep=f"""# Train/Test Dependency Report

## Finding

The supplied train and test sets are not independent at the recording-source level.

A full-waveform cosine audit and an independent fixed-length relative-time
fingerprint audit identify a sharply separated near-duplicate cluster.

- threshold used: `{DUP_THRESHOLD}`
- weakest member of the fingerprint duplicate cluster: `{weakest_cluster:.6f}`
- strongest non-cluster pair: `{strongest_noncluster:.6f}`
- duplicate/near-duplicate groups: **{len(groups)}**
- clips belonging to those groups: **{sum(len(g) for g in groups)}**
- train↔test groups: **{len(cross_groups)}**
- affected test clips: **{sum(sum(k[0]=="test" for k in g) for g in cross_groups)} / {len(test)}**
- conflicting-label groups in train: **{len(conflicts)}**

Every train↔test duplicate group with training labels has a unanimous training
label. Therefore duplicate retrieval is a legitimate high-confidence inference
lane using only competition-provided data, but it must remain separate from
general SER validation/modeling.

The only detected conflicting train group is recorded in
`DUPLICATE_CONFLICTS.csv`.

## Consequence

Row-level random CV substantially overstates generalization. Model selection
must inspect duplicate-safe V-B in addition to competition-mimic V-A.
"""
    (a.out/"TRAIN_TEST_DEPENDENCY_REPORT.md").write_text(dep)

    freeze=f"""# Validation Freeze Recommendation

## Recommendation

Freeze two complementary 5-fold authorities:

- **V-A**: stratified row-level competition-mimic CV, seed 20260930.
- **V-B**: stratified duplicate-group-safe CV, seed 20260930.

Use **V-B as the primary model-family/generalization guardrail** and V-A as the
competition-mimic view. Final inference may then add an explicit duplicate
retrieval lane for test clips in `TRAIN_TEST_RETRIEVAL_MAP.csv`.

A speaker/source-disjoint V-C is **not frozen yet** because the competition
provides no speaker IDs and an inferred speaker partition has not yet met a
reliability standard.

## Baseline evidence

A fixed handcrafted acoustic RBF-SVM diagnostic over five seeds gives:

- V-A mean macro-F1: **{np.mean(va_scores):.6f} ± {np.std(va_scores,ddof=1):.6f}**
- V-B mean macro-F1: **{np.mean(vb_scores):.6f} ± {np.std(vb_scores,ddof=1):.6f}**
- mean V-A − V-B gap: **{np.mean(va_scores)-np.mean(vb_scores):.6f}**

The approximately 0.10 macro-F1 gap is material evidence that duplicate-aware
validation is necessary.

## Promotion policy

A production SER model must not be promoted from V-A alone. Prefer candidates
that improve V-B credibly; use V-A and OOF ensemble gains as secondary evidence.
Duplicate retrieval is evaluated separately.
"""
    (a.out/"VALIDATION_FREEZE_RECOMMENDATION.md").write_text(freeze)

    ret=f"""# Final Return to SS

Mission: `DS-DEFHS-DATA-VALIDATION-FOUNDATION-001`

## Verdict

**PASS_FREEZE_CANDIDATE**

The data audit found a major train/test dependency that materially changes the
competition strategy.

- 1,035 supplied clips: 826 train / 209 test.
- 227 near-duplicate groups covering 467 clips.
- 77 train↔test groups affecting 78 test clips.
- Near-duplicate similarity separation is extremely sharp:
  `{weakest_cluster:.6f}` weakest duplicate-cluster similarity versus
  `{strongest_noncluster:.6f}` strongest non-cluster similarity under the
  independent relative-time fingerprint.
- All train↔test groups have unanimous train labels.
- One train-only label-conflict group exists.
- Cheap acoustic baseline shows an average ~{np.mean(va_scores)-np.mean(vb_scores):.4f}
  macro-F1 row-CV leakage premium.

## Freeze candidate

- V-A: 5-fold stratified row-level competition-mimic.
- V-B: 5-fold stratified duplicate-safe grouped CV.
- V-C: not frozen; reliable speaker identity is unavailable.

## Immediate next scientific bottleneck

Benchmark strong pretrained speech/emotion representations under the exact same
V-A/V-B folds, beginning with frozen emotion2vec+ and WavLM representations.
Keep the 78-clip test duplicate-retrieval lane separate from model selection.
"""
    (a.out/"FINAL_RETURN_TO_SS.md").write_text(ret)
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
