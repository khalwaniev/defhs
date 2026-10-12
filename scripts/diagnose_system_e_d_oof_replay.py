#!/usr/bin/env python3
"""Read-only forensic replay of sealed System D to explain local OOF parity failures.

Loads the untouched archived System D finalizer in a temporary directory and
samples original frame variables directly BEFORE the original assertions.
Does NOT disable/assert-patch checks, change model code or create Kaggle output.
"""
import argparse,contextlib,hashlib,io,json,os,runpy,sys,tempfile,zipfile
from pathlib import Path

D_SHA="fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839"
SOURCE_SHA="b77914ef4a358e6acc19497e242ca83b769f13b3dfdacde5d8522fc4a55bf525"
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bundle",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    assert digest(a.bundle)==D_SHA, "System D archive does not match authenticated SHA256"
    import numpy as np,pandas,scipy,sklearn,joblib,threadpoolctl
    record={"purpose":"diagnostic only; original assertions remain active",
        "python":sys.version.split()[0],"executable":sys.executable,
        "numpy":np.__version__,"pandas":pandas.__version__,"scipy":scipy.__version__,
        "sklearn":sklearn.__version__,"joblib":joblib.__version__,
        "threadpoolctl":threadpoolctl.__version__,
        "openblas_threads_env":os.environ.get("OPENBLAS_NUM_THREADS"),
        "omp_threads_env":os.environ.get("OMP_NUM_THREADS"),
        "mkl_threads_env":os.environ.get("MKL_NUM_THREADS"),
        "original_source_sha256":SOURCE_SHA,"submission_performed":False}
    with tempfile.TemporaryDirectory(prefix="defhs_d_parity_debug_") as d:
        root=Path(d)
        with zipfile.ZipFile(a.bundle) as z:
            assert z.testzip() is None
            z.extractall(root)
        script=root/"finalize_system_d.py"
        assert digest(script)==SOURCE_SHA
        seen=set()
        def inspect(frame,event,arg):
            if event!="line" or frame.f_code.co_filename!=str(script):
                return inspect
            line=frame.f_lineno
            if line in (141,143) and line not in seen:
                seen.add(line)
                loc=frame.f_locals
                lab=frame.f_globals["LAB"]
                ids=loc["ids"]
                if line==141:
                    pred=loc["c_oof"]; ref=lab[(loc["ma"]%20)//5]
                    idx=np.flatnonzero(pred!=ref)
                    record["C_OOF"]={"mismatch_count":int(len(idx)),
                        "mismatched_ids":[int(ids[i]) for i in idx]}
                else:
                    pred=loc["d_oof"]
                    prior=loc["old_record"]
                    ref=prior.challenger_pred.to_numpy()
                    idx=np.flatnonzero(pred!=ref)
                    probs=np.asarray(loc["dp_oof"])
                    ref_probs=prior[["challenger_p_"+str(c) for c in lab]].to_numpy()
                    delta=np.abs(probs-ref_probs)
                    record["D_OOF"]={
                        "mismatch_count":int(len(idx)),
                        "mismatched_ids":[int(ids[i]) for i in idx],
                        "probability_max_abs_delta":float(delta.max()),
                        "probability_mean_abs_delta":float(delta.mean()),
                        "row_details":[{"Id":int(ids[i]),"fold":int(loc["fold"][i]),
                            "expected":str(ref[i]),"observed":str(pred[i]),
                            "reference_probability":[float(v) for v in ref_probs[i]],
                            "observed_probability":[float(v) for v in probs[i]],
                            "max_row_abs_delta":float(delta[i].max()),
                            "reference_margin":float(np.ptp(np.sort(ref_probs[i])[-2:])),
                            "observed_margin":float(np.ptp(np.sort(probs[i])[-2:]))
                            } for i in idx]}
            return inspect
        previous=os.environ.get("DEFHS_SYSTEM_D_BASE")
        os.environ["DEFHS_SYSTEM_D_BASE"]=str(root)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                try:
                    sys.settrace(inspect)
                    runpy.run_path(str(script),run_name="__main__")
                    record["original_script_status"]="PASS"
                except BaseException as ex:
                    record["original_script_status"]="FAIL"
                    record["original_failure"]=type(ex).__name__+": "+str(ex)
                finally:
                    sys.settrace(None)
        finally:
            if previous is None:os.environ.pop("DEFHS_SYSTEM_D_BASE",None)
            else:os.environ["DEFHS_SYSTEM_D_BASE"]=previous
    body=json.dumps(record,indent=2)+"\n"
    print(body,end="")
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(body,encoding="utf-8")
if __name__=="__main__":main()
