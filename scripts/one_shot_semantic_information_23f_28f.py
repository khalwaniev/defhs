#!/usr/bin/env python3
"""DEFHS one-shot, reference-anchored 23F vs 28F nested PRIMARY_CV test.

No target inference, protected evaluation, tuning, or Kaggle submission.
Requires the user's original hash-locked external evidence. Does NOT bypass
the original System E scientific stress failure or claim frozen parity.
"""
import argparse
import collections
import hashlib
import io
import json
import os
import platform
import runpy
import sys
import tempfile
import warnings
import zipfile
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn
import threadpoolctl
from sklearn.exceptions import InconsistentVersionWarning, ConvergenceWarning
from sklearn.metrics import f1_score, confusion_matrix, precision_recall_fscore_support
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
LAB = np.array(["angry", "happy", "neutral", "sad"])
STATES = ["angry", "happy", "neutral", "sad", "unclear"]
EXPECTED = {
    "d_zip": "fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839",
    "e_zip": "dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf",
    "new_q14_zip": "cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789",
    "likelihood_csv": "66d01f825c9be4142452e6f04fb921dd8ece6c8f82aac5e0768a9941c0e4e788",
    "d_source": "b77914ef4a358e6acc19497e242ca83b769f13b3dfdacde5d8522fc4a55bf525",
    "folds": "87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b",
    "manifest": "1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469",
    "prompt": "458712cfee51e0cf65ef57d1a0deb8f81dcb70e4ecfe6ebfc73220f3aefac005",
}
def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def require(p, key):
    got = digest(p)
    assert got == EXPECTED[key], (str(p), key, "SHA256_MISMATCH", got, EXPECTED[key])
    return got

def mf(y, pred):
    return float(f1_score(y, pred, labels=LAB, average="macro", zero_division=0))

def metrics(y, pred):
    precision, recall, f1, support = precision_recall_fscore_support(
        y, pred, labels=LAB, zero_division=0)
    return {
        "n": int(len(y)), "macro_f1": mf(y, pred),
        "per_class": {str(c): {
            "precision": float(precision[i]), "recall": float(recall[i]),
            "f1": float(f1[i]), "support": int(support[i])}
            for i,c in enumerate(LAB)},
        "confusion": confusion_matrix(y, pred, labels=LAB).tolist()
    }

def compare(y, a, b, fold):
    pa, pb = LAB[a.argmax(1)], LAB[b.argmax(1)]
    correct = (pa != y) & (pb == y)
    broken = (pa == y) & (pb != y)
    moved_wrong = (pa != y) & (pb != y) & (pa != pb)
    return {
        "baseline": metrics(y, pa), "challenger": metrics(y, pb),
        "pooled_delta": mf(y, pb)-mf(y, pa),
        "baseline_fold_f1": [mf(y[fold==i],pa[fold==i]) for i in range(5)],
        "challenger_fold_f1": [mf(y[fold==i],pb[fold==i]) for i in range(5)],
        "fold_deltas": [mf(y[fold==i],pb[fold==i])-mf(y[fold==i],pa[fold==i]) for i in range(5)],
        "delete_one_fold_deltas": [mf(y[fold!=i],pb[fold!=i])-mf(y[fold!=i],pa[fold!=i]) for i in range(5)],
        "changed": int(np.sum(pa!=pb)),
        "corrections": int(correct.sum()), "breakages": int(broken.sum()),
        "wrong_to_other_wrong": int(moved_wrong.sum())
    }

def onehot(vals):
    vals=np.asarray(vals)
    assert np.isin(vals, STATES).all()
    return (vals[:,None]==np.array(STATES)[None,:]).astype(float)

def hard316(wave):
    e,x=wave[:,:4], wave[:,4:]
    p=(e+x)/2
    es,ps=np.sort(e,axis=1), np.sort(p,axis=1)
    mask=((es[:,-1]<.6)|(ps[:,-1]<.6)|((es[:,-1]-es[:,-2])<.2)|
          ((ps[:,-1]-ps[:,-2])<.2)|(e.argmax(1)!=p.argmax(1))|
          (e.argmax(1)!=x.argmax(1)))
    assert int(mask.sum()) == 316, "Frozen HARD316 membership changed"
    return mask

def locate_likelihood_columns(df, manual):
    if manual:
        assert len(manual)==5 and len(set(manual))==5 and set(manual)<=set(df)
        return manual
    patterns=[
        [f"p_{s}" for s in STATES],
        [f"prob_{s}" for s in STATES],
        [f"probability_{s}" for s in STATES],
        [f"trie_p_{s}" for s in STATES],
        [f"constrained_p_{s}" for s in STATES],
        [f"trie_prob_{s}" for s in STATES],
        [f"likelihood_{s}" for s in STATES],
    ]
    matches=[p for p in patterns if set(p)<=set(df)]
    assert len(matches)==1, (
        "Cannot uniquely identify the FIVE CONSTRAINED probabilities. "
        "Supply --prob-columns in angry happy neutral sad unclear order.",
        df.columns.tolist())
    return matches[0]

def maybe_uncertainty(ids, y, pa, pb, a):
    if not a.prompt_csv:
        return {"status": "INCOMPLETE_AUTHENTIC_PROMPT_COMPONENTS_NOT_SUPPLIED"}
    require(a.prompt_csv,"prompt")
    duppath=ROOT/"runs/DS-DEFHS-VALIDATION-HARDENING-002/DUPLICATE_GROUPS_FINAL.csv"
    assert duppath.exists()
    sys.path.insert(0,str(ROOT/"scripts"))
    from defhs_frozen_closure_utils import Evidence, labels
    ev=Evidence(ids,pd.read_csv(duppath),pd.read_csv(a.prompt_csv))
    assert len(set(ev.components))==656, "Authentic component count mismatch"
    diff=ev.boots(labels(y),labels(pb))-ev.boots(labels(y),labels(pa))
    point=mf(y,pb)-mf(y,pa)
    return {
        "status": "AUTHENTIC_656_COMPONENT_2000_DRAW_MULTIPLIER_BOOTSTRAP",
        "components":656, "draws":2000, "point":point,
        "percentile_ci95":np.quantile(diff,[.025,.975]).tolist(),
        "note":"Paired exploratory percentile interval; not a post-selection-adjusted certification."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--d-zip",type=Path,required=True)
    p.add_argument("--e-zip",type=Path,required=True)
    p.add_argument("--new-q14-zip",type=Path,required=True)
    p.add_argument("--likelihood-csv",type=Path,required=True)
    p.add_argument("--prob-columns",nargs=5,default=None,metavar="COLUMN")
    p.add_argument("--prompt-csv",type=Path,default=None)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    assert not (a.out/"RESULT.json").exists(), "One-shot result exists; no overwriting or repeated selection"
    log={"mission":"RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001-CONTINUATION",
         "status":"INCOMPLETE", "git_input_authority":"e82f6fe63f12ca99af2e128f72415e0dac0a31a9",
         "system_e_prod_authority":"a6676d9777ace9e9746802b3256cd3eb52dd7339",
         "no_test_inference":True,"protected_access":False,"kaggle_submission":False}
    print("AUTHENTICATING INPUTS",flush=True)
    got={key:require(path,key) for key,path in [
        ("d_zip",a.d_zip),("e_zip",a.e_zip),("new_q14_zip",a.new_q14_zip),
        ("likelihood_csv",a.likelihood_csv)]}
    foldpath=ROOT/"runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VB_FOLDS.csv"
    manifestpath=ROOT/"runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv"
    got["folds"]=require(foldpath,"folds")
    got["manifest"]=require(manifestpath,"manifest")
    frozen=pd.read_csv(foldpath).sort_values("Id").reset_index(drop=True)
    ids=frozen.Id.to_numpy()
    y=frozen.emotion.to_numpy()
    fold=frozen.fold.to_numpy()
    assert len(ids)==826 and len(set(ids))==826 and set(fold)==set(range(5))
    assert set(y)==set(LAB)
    q=pd.read_csv(a.likelihood_csv)
    assert "Id" in q.columns and len(q)==826 and q.Id.is_unique
    assert set(q.Id)==set(ids)
    cols=locate_likelihood_columns(q,a.prob_columns)
    pq=q.set_index("Id").loc[ids,cols].to_numpy(dtype=float)
    assert pq.shape==(826,5) and np.isfinite(pq).all() and (pq>=0).all() and (pq<=1).all()
    assert np.allclose(pq.sum(axis=1),1.0,atol=1e-6,rtol=0), "Constrained trie probabilities must sum to one"
    with zipfile.ZipFile(a.new_q14_zip) as z:
        assert z.testzip() is None
        r=json.loads(z.read("RESULT.json"))
        assert r["rows"]==826 and r["unique"]==664
        raw=z.read("QWEN14B_TRAIN826.csv")
        assert hashlib.sha256(raw).hexdigest()=="8edd8dc9899f9304db2b46475758a67330f82c3c1348317646b561f3d57f6377"
        qhard=pd.read_csv(io.BytesIO(raw)).set_index("Id")
        assert len(qhard)==826 and set(qhard.index)==set(ids)
        if "semantic_label" in q:
            assert np.array_equal(q.set_index("Id").loc[ids,"semantic_label"].to_numpy(),qhard.loc[ids,"semantic_label"].to_numpy())
    with zipfile.ZipFile(a.e_zip) as z:
        assert z.testzip() is None
        olde=pd.read_csv(io.BytesIO(z.read("SYSTEM_E_PRIMARY_OOF.csv")))
    assert np.array_equal(olde.Id.to_numpy(),ids)
    assert np.array_equal(olde.fold.to_numpy(),fold)
    assert np.array_equal(olde.emotion.to_numpy(),y)
    pref=olde[["system_E_p_"+c for c in LAB]].to_numpy()
    assert abs(mf(y,olde.system_E_pred.to_numpy())-.8774091527555827)<1e-12
    manifest=pd.read_csv(manifestpath)
    train=manifest[manifest.split=="train"].set_index("Id").loc[ids]
    assert np.array_equal(train.emotion.to_numpy(),y)
    q960=(train.samples.to_numpy()%960)==606
    assert q960.sum()==41
    assert [int(np.sum(y[q960]==c)) for c in LAB]==[6,10,13,12]
    # Temporary extraction leaves original authenticated bundle and historical files untouched.
    with tempfile.TemporaryDirectory(prefix="defhs_one_shot_") as t:
        base=Path(t)
        with zipfile.ZipFile(a.d_zip) as z:
            assert z.testzip() is None
            for n in z.namelist():
                dest=(base/n).resolve()
                assert dest==base.resolve() or base.resolve() in dest.parents, "Unsafe archive path"
            z.extractall(base)
        orig=base/"finalize_system_d.py"
        got["d_source"]=require(orig,"d_source")
        mod=runpy.run_path(str(orig),run_name="frozen_d_functions")
        assert np.array_equal(mod["LAB"],LAB)
        assert "meta_lr" in mod and "head" in mod and "HEADS" in mod
        z=np.load(base/"FIXED_PAIR_VB.npz")
        assert np.array_equal(z["Id"],ids)
        ma=np.frombuffer(bytes.fromhex((base/"defhs_prod_run/old_evidence/metadata.hex").read_text()),
                         dtype=np.uint8).astype("int64")
        assert np.array_equal(fold,ma%5) and np.array_equal(y,LAB[ma//20])
        oldd=pd.read_csv(base/"defhs_prod_run/old_evidence/CHALLENGER_PRIMARY_OOF.csv")
        assert np.array_equal(oldd.Id.to_numpy(),ids)
        pdref=oldd[["challenger_p_"+c for c in LAB]].to_numpy()
        feats=[]
        for fn in ("emotion2vec_base_meanstd.npz","xls_r_300m_meanstd.npz"):
            z=np.load(base/fn,allow_pickle=False)
            m={int(id):i for i,id in enumerate(z["Id"])}
            assert set(ids)<=set(m)
            feats.append(z["X"][[m[int(id)] for id in ids]])
        pw=np.column_stack([
            np.load(base/"E2V_CONTROL_VB.npz")["prob"],
            np.load(base/"XLSR_VB.npz")["prob"]])
        assert pw.shape==(826,8)
        sem8=pd.read_csv(base/"QWEN_SEMANTIC_OUTPUTS.csv").set_index("Id").loc[ids,"semantic_label"].to_numpy()
        with zipfile.ZipFile(base/"DEFHS_Qwen14B_train826_outputs.zip") as z:
            old14=pd.read_csv(io.BytesIO(z.read("final_semantic_train826/QWEN14B_TRAIN826.csv"))).set_index("Id").loc[ids,"semantic_label"].to_numpy()
        sem23=np.column_stack([onehot(sem8),onehot(old14),onehot(qhard.loc[ids,"semantic_label"].to_numpy())])
        assert sem23.shape==(826,15)
        local23=np.empty((826,4))
        local28=np.empty((826,4))
        warnings.simplefilter("error",ConvergenceWarning)
        with threadpool_limits(limits=2):
            for f in range(5):
                tr=fold!=f
                vl=~tr
                for k,name in enumerate(("emotion2vec_base","xls_r_300m")):
                    headpath=base/(name+"_VB_outer"+str(f)+".joblib.bin")
                    assert digest(headpath)==mod["HEADS"][name][f]
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore",InconsistentVersionWarning)
                        head=joblib.load(headpath)
                    drift=float(np.max(np.abs(head.predict_proba(feats[k][vl])-pw[vl,k*4:k*4+4])))
                    assert drift<5e-7,("Saved outer acoustic head mismatch",f,name,drift)
                inner=np.zeros((826,8))
                for block in sorted(set(fold[tr])):
                    it=tr & (fold!=block)
                    iv=tr & (fold==block)
                    assert not np.any(it & iv)
                    inner[iv]=np.column_stack([mod["head"](x,y,it,iv) for x in feats])
                x23=np.column_stack([inner[tr],sem23[tr]])
                x28=np.column_stack([x23,pq[tr]])
                assert x23.shape[1]==23 and x28.shape[1]==28
                m23=mod["meta_lr"]().fit(x23,y[tr])
                m28=mod["meta_lr"]().fit(x28,y[tr])
                v23=np.column_stack([pw[vl],sem23[vl]])
                local23[vl]=m23.predict_proba(v23)
                local28[vl]=m28.predict_proba(np.column_stack([v23,pq[vl]]))
                print("COMPLETED OUTER FOLD",f,flush=True)
    assert np.isfinite(local23).all() and np.isfinite(local28).all()
    p23=LAB[local23.argmax(1)]
    p28=LAB[local28.argmax(1)]
    pr=LAB[pref.argmax(1)]
    assert np.array_equal(pr,olde.system_E_pred.to_numpy())
    hard=hard316(pw)
    driftE=float(np.max(np.abs(local23-pref)))
    margins23=np.sort(local23,axis=1)[:,-1]-np.sort(local23,axis=1)[:,-2]
    margins28=np.sort(local28,axis=1)[:,-1]-np.sort(local28,axis=1)[:,-2]
    drift_threshold=2*driftE
    near28=(margins28<=drift_threshold)
    changed=(p23!=p28)
    report={
        **log,
        "status":"EXPLORATORY_PAIRED_COMPARISON_COMPLETE_NOT_CERTIFIED",
        "input_sha256":got,
        "feature_columns":cols,
        "runtime":{"python":sys.version.split()[0],"numpy":np.__version__,
                   "scipy":scipy.__version__,"sklearn":sklearn.__version__,
                   "pandas":pd.__version__,"joblib":joblib.__version__,
                   "threadpoolctl":threadpoolctl.__version__,
                   "machine":platform.machine(),"platform":platform.platform(),
                   "threads":threadpoolctl.threadpool_info(),
                   "thread_env":{k:os.environ.get(k) for k in
                       ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","PYTHONNOUSERSITE")}},
        "archivedE_vs_local23":compare(y,pref,local23,fold),
        "local23_vs_local28":compare(y,local23,local28,fold),
        "archivedE_vs_local28":compare(y,pref,local28,fold),
        "archive_E_replay_max_probability_drift":driftE,
        "archive_E_class_mismatches":int(np.sum(pr!=p23)),
        "HARD316":{
            "n":316,"archiveE":mf(y[hard],pr[hard]),
            "local23":mf(y[hard],p23[hard]),
            "local28":mf(y[hard],p28[hard]),
            "local28_minus_local23":mf(y[hard],p28[hard])-mf(y[hard],p23[hard])},
        "Q960_606":{
            "n":int(q960.sum()),"class_supports":[int(np.sum(y[q960]==c)) for c in LAB],
            "archiveE":mf(y[q960],pr[q960]),
            "local23":mf(y[q960],p23[q960]),
            "local28":mf(y[q960],p28[q960]),
            "local28_minus_local23":mf(y[q960],p28[q960])-mf(y[q960],p23[q960]),
            "local28_minus_archivedD":mf(y[q960],p28[q960])-mf(y[q960],LAB[pdref[q960].argmax(1)]),
            "historical_E_minus_D_failure":-0.03367392841077055
        },
        "candidate_margins":{
            "min":float(margins28.min()),
            "q01":float(np.quantile(margins28,.01)),
            "q05":float(np.quantile(margins28,.05)),
            "n_weak_relative_to_measured_E_drift":int(near28.sum()),
            "n_weak_and_changed":int(np.sum(near28 & changed)),
            "warning":"Measured E numerical drift is a diagnostic comparator, not a proven bound on 28F drift."
        },
        "uncertainty":maybe_uncertainty(ids,y,p23,p28,a),
        "frozen_status":"Original System E Q960 failure remains; no frozen primary certification and no promotion.",
    }
    v=report["local23_vs_local28"]
    classdelta={c: v["challenger"]["per_class"][c]["f1"]-v["baseline"]["per_class"][c]["f1"] for c in LAB}
    report["per_class_f1_delta_local28_minus23"]=classdelta
    report["local_23F_to_28F_corrected_ids"]=list(map(int,ids[(p23!=y)&(p28==y)]))
    report["local_23F_to_28F_broken_ids"]=list(map(int,ids[(p23==y)&(p28!=y)]))
    report["local_23F_to_28F_changed_ids"]=list(map(int,ids[p23!=p28]))
    report["changed_candidate_near_numeric_drift_ids"]=list(map(int,ids[near28 & changed]))
    probe=(v["pooled_delta"]>=.005 and sum(t>0 for t in v["fold_deltas"])>=4
           and min(classdelta.values())>=-.02 and report["HARD316"]["local28_minus_local23"]>=0
           and min(v["delete_one_fold_deltas"])>0)
    report["scientific_disposition"]=(
        "PROMISING_ONLY_RETURN_TO_SS_NO_PROMOTION" if probe else "REJECT_LOCAL_COMPARISON")
    output=pd.DataFrame({"Id":ids,"emotion":y,"fold":fold,"archive_E":pr,
         "local_23F":p23,"local_28F":p28,"HARD316":hard,"Q960_606":q960,
         "margin23":margins23,"margin28":margins28,"near_measured_E_drift":near28})
    for name,prob in (("referenceE",pref),("local23",local23),("local28",local28)):
        for j,c in enumerate(LAB):
            output[name+"_p_"+c]=prob[:,j]
    output.to_csv(a.out/"PAIRED_PRIMARY_OOF.csv",index=False,float_format="%.17g")
    (a.out/"RESULT.json").write_text(json.dumps(report,indent=2,default=str)+"\n")
    print(json.dumps({"result":report["scientific_disposition"],
         "local_gain":v["pooled_delta"],"fold_deltas":v["fold_deltas"],
         "corrected":v["corrections"],"broken":v["breakages"],
         "E_reference_numerical_drift":driftE,
         "result_file":str(a.out/"RESULT.json")},indent=2),flush=True)

if __name__=="__main__":
    main()
