#!/usr/bin/env python3
"""Read-only forensic audit of authenticated 826-row Qwen3-14B likelihood CSV.

NO fitting, renormalization, override, target inference or Kaggle submission.
Saves only descriptive diagnostics of the ORIGINAL unmodified CSV.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import zipfile
import io
import numpy as np
import pandas as pd

SHA="66d01f825c9be4142452e6f04fb921dd8ece6c8f82aac5e0768a9941c0e4e788"
Q14SHA="cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789"
STATES=("angry","happy","neutral","sad","unclear")
PREFIXES=("p_","prob_","probability_","trie_p_","constrained_p_",
          "trie_prob_","likelihood_")
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for block in iter(lambda:f.read(2**20),b""):h.update(block)
    return h.hexdigest()
def sf(v):
    a=np.asarray(v,dtype=float)
    finite=a[np.isfinite(a)]
    return {
        "count":int(a.size),"finite":int(finite.size),
        "min":float(np.min(finite)) if len(finite) else None,
        "p01":float(np.quantile(finite,.01)) if len(finite) else None,
        "median":float(np.median(finite)) if len(finite) else None,
        "p99":float(np.quantile(finite,.99)) if len(finite) else None,
        "max":float(np.max(finite)) if len(finite) else None,
    }
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--likelihood-csv",type=Path,required=True)
    ap.add_argument("--qwen-zip",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    assert a.likelihood_csv.is_file() and a.qwen_zip.is_file()
    h=sha(a.likelihood_csv)
    assert h==SHA,("AUTHENTIC_LIKELIHOOD_SHA_MISMATCH",h,SHA)
    zhash=sha(a.qwen_zip)
    assert zhash==Q14SHA,("QWEN_ZIP_SHA_MISMATCH",zhash,Q14SHA)
    df=pd.read_csv(a.likelihood_csv)
    assert "Id" in df and len(df)==826 and df.Id.is_unique
    assert int(df.Id.isna().sum())==0
    ids=df.Id.to_numpy()
    with zipfile.ZipFile(a.qwen_zip) as z:
        assert z.testzip() is None
        orig=pd.read_csv(io.BytesIO(z.read("QWEN14B_TRAIN826.csv")))
    assert set(df.Id)==set(orig.Id) and len(orig)==826
    aliases=[]
    for prefix in PREFIXES:
        cols=[prefix+x for x in STATES]
        if set(cols).issubset(df.columns):
            aliases.append(cols)
    candidate_cols=[]
    for col in df:
        if col in ("Id","semantic_label"):continue
        if any(str(col).lower().endswith("_"+x) for x in STATES):
            candidate_cols.append(str(col))
    dtypes={str(c):str(df[c].dtype) for c in df}
    report={
        "status":"READ_ONLY_DIAGNOSIS_NO_MODELS_FITTED",
        "csv":str(a.likelihood_csv),"csv_sha256":h,
        "qwen_zip_sha256":zhash,"rows":int(len(df)),
        "columns":list(map(str,df.columns)),
        "dtypes":dtypes,"matched_candidate_prefix_groups":aliases,
        "five_state_suffix_columns":candidate_cols,
        "Id_same_set_as_original_hard_outputs":True,
        "Id_sorted":bool(np.all(np.diff(ids)>0)),
    }
    for col in df:
        if str(col)=="Id":continue
        if pd.api.types.is_numeric_dtype(df[col]):
            report.setdefault("numeric_column_stats",{})[str(col)]=sf(df[col])
        else:
            report.setdefault("non_numeric_column_stats",{})[str(col)]={
                "non_null":int(df[col].notna().sum()),"unique":int(df[col].nunique(dropna=True)),
                "first_three":list(map(str,df[col].dropna().head(3).tolist()))}
    if "semantic_label" in df:
        local=df.set_index("Id").loc[orig.Id,"semantic_label"].astype(str)
        original=orig.set_index("Id").loc[orig.Id,"semantic_label"].astype(str)
        disagreements=(local.to_numpy()!=original.to_numpy())
        report["semantic_label_parity"]={"matching":int((~disagreements).sum()),
            "mismatching":int(disagreements.sum()),
            "mismatch_Ids":orig.Id.to_numpy()[disagreements].astype(int).tolist()}
    selected=aliases[0] if len(aliases)==1 else None
    report["exactly_one_evaluator_matched_group"]=len(aliases)==1
    if selected:
        p=df[selected].apply(pd.to_numeric,errors="coerce").to_numpy(float)
        s=p.sum(axis=1)
        delta=np.abs(s-1.0)
        tol=(1e-14,1e-12,1e-10,1e-8,1e-6,1e-4,1e-3,1e-2,1e-1)
        nbad={str(t):int(np.sum(delta>t)) for t in tol}
        report["selected_columns"]=selected
        report["five_feature_metrics"]={
            "row_sums":sf(s),
            "absolute_sum_error":sf(delta),
            "rows_deviating_by_more_than":nbad,
            "rows_sum_le_zero":int(np.sum(s<=0)),
            "rows_negative_any":int(np.sum((p<0).any(axis=1))),
            "rows_gt_one_any":int(np.sum((p>1).any(axis=1))),
            "rows_nan_any":int(np.sum(np.isnan(p).any(axis=1))),
            "rows_inf_any":int(np.sum(np.isinf(p).any(axis=1))),
            "rows_all_zero":int(np.sum((p==0).all(axis=1))),
            "min_feature":float(np.nanmin(p)),
            "max_feature":float(np.nanmax(p)),
        }
        idx=np.argsort(-np.nan_to_num(delta,nan=np.inf))[:30]
        print("\nTOP-30 MAXIMUM ROW-SUM ERRORS (original values, no changes):")
        print(df.iloc[idx][["Id"]+selected].assign(sum=s[idx],error=delta[idx]).to_string(index=False))
        audited=df[["Id"]+selected].copy()
        audited["sum_original"]=s
        audited["error_abs_sum_minus_1"]=delta
        audited["fails_original_1e6_gate"]=delta>1e-6
        a.out.mkdir(parents=True,exist_ok=True)
        audited.to_csv(a.out/"ALL_826_ROW_SUMS.csv",index=False,float_format="%.17g")
        report["largest_offending_Ids"]=df.Id.to_numpy()[idx].astype(int).tolist()
        report["sample_first_10"]=[{
            "Id":int(ids[i]),"values":[float(v) for v in p[i]],
            "sum":float(s[i]),"absolute_sum_error":float(delta[i])
        } for i in range(min(10,len(df)))]
        print("\nSUM STATISTICS:",json.dumps(report["five_feature_metrics"],indent=2))
        for prefix in ("logp_","log_prob_","raw_logp_","unrestricted_logp_"):
            cols=[prefix+x for x in STATES]
            if set(cols).issubset(df.columns):
                v=df[cols].to_numpy(float)
                expv=np.exp(v)
                report.setdefault("log_probability_group_diagnostics",{})[prefix]={
                    "column_names":cols,"exp_values_sum":sf(expv.sum(axis=1)),
                    "log_values":{col:sf(df[col].to_numpy(float)) for col in cols}}
    # Read small JSON metadata files from the extraction artifact directory,
    # displaying only schema/keys to avoid flooding logs or private transcript content.
    for root in [a.likelihood_csv.parent,a.likelihood_csv.parent.parent]:
        if not root.is_dir():continue
        for pth in sorted(root.glob("*.json"))[:30]:
            try:
                if pth.stat().st_size>3_000_000:continue
                obj=json.loads(pth.read_text())
                report.setdefault("neighboring_json_schema",[]).append({
                    "name":str(pth),"sha256":sha(pth),
                    "root_keys":sorted(list(obj))[:100] if isinstance(obj,dict) else None,
                    "type":type(obj).__name__})
            except (OSError,ValueError,UnicodeError):continue
    # Search nearby source scripts for extraction implementation, without executing them.
    sroot=a.likelihood_csv.parent.parent
    matches=[]
    if sroot.exists():
        for pth in sorted(sroot.rglob("*.py")):
            try:
                if pth.stat().st_size>500_000:continue
                for lineno,line in enumerate(pth.read_text(errors="replace").splitlines(),1):
                    if re.search(r"trie|likelihood|logsumexp|log_softmax|allowed.tokens|exp\(",line,re.I):
                        matches.append({"path":str(pth),"line":lineno,"text":line.strip()[:300]})
                        if len(matches)>=200:break
            except OSError:continue
            if len(matches)>=200:break
    report["nearby_producer_source_matches"]=matches
    a.out.mkdir(parents=True,exist_ok=True)
    dest=a.out/"LIKELIHOOD_INPUT_DIAGNOSTIC.json"
    dest.write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    print("\nVERIFIED CSV SHA256:",h)
    print("VERIFIED QWEN ZIP SHA256:",zhash)
    print("CSV COLUMNS:",list(df.columns))
    print("MATCHED 5-PROB GROUPS:",aliases)
    print("HARD-STATE PARITY:",report.get("semantic_label_parity","CSV_HAS_NO_SEMANTIC_LABEL_COLUMN"))
    print("SOURCE MATCH COUNT:",len(matches))
    print("DIAGNOSTIC_JSON:",dest)
    if selected: print("COMPLETE_826_ROW_SUMS:",a.out/"ALL_826_ROW_SUMS.csv")
    print("VERDICT: READ-ONLY DIAGNOSTIC ONLY; NO NORMALIZATION, REFIT OR SUBMISSION")
if __name__=="__main__":
    main()
