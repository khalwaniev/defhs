#!/usr/bin/env python3
"""Read-only BLAS/CPU provenance for independent D-replay comparison. No model fitting."""
import argparse, contextlib, hashlib, io, json, os, platform, subprocess, sys
from pathlib import Path
import numpy as np
import scipy
import pandas
import sklearn
import joblib
import threadpoolctl

def filehash(path):
    try:
        p=Path(path)
        with p.open("rb") as f:
            return hashlib.file_digest(f, "sha256").hexdigest()
    except (OSError, TypeError):
        return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    # Force both NumPy and SciPy BLAS to load before enumerating libraries.
    a=np.eye(8); _=a@a; _=np.linalg.svd(a)
    import scipy.linalg
    _=scipy.linalg.blas.dgemm(alpha=1.0,a=a,b=a)
    t=threadpoolctl.threadpool_info()
    for rec in t:
        rec["sha256"]=filehash(rec.get("filepath"))
    try:
        from numpy._core._multiarray_umath import __cpu_features__
        features={k:bool(v) for k,v in __cpu_features__.items()}
    except (ImportError,AttributeError):
        features=None
    out=io.StringIO()
    with contextlib.redirect_stdout(out):
        try: np.show_runtime()
        except Exception as ex: print("numpy.show_runtime error",str(ex))
    cpu=""
    try:
        cpu=subprocess.run(["lscpu"],capture_output=True,text=True,timeout=5).stdout
    except (OSError,subprocess.TimeoutExpired):
        pass
    report={
      "purpose":"Read-only independent replay backend comparison; no model fitting",
      "python":sys.version,
      "executable":sys.executable,
      "platform":platform.platform(),
      "machine":platform.machine(),
      "processor":platform.processor(),
      "libc":platform.libc_ver(),
      "packages":{ "numpy":np.__version__, "pandas":pandas.__version__,
        "scipy":scipy.__version__, "scikit-learn":sklearn.__version__,
        "joblib":joblib.__version__, "threadpoolctl":threadpoolctl.__version__ },
      "thread_env":{k:os.environ.get(k) for k in
        ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS",
        "PYTHONNOUSERSITE","PYTHONPATH","OPENBLAS_CORETYPE","NPY_DISABLE_CPU_FEATURES")},
      "threadpool_info":t,
      "numpy_runtime":out.getvalue(),
      "numpy_cpu_features":features,
      "lscpu":cpu,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,default=str)+"\n",encoding="utf-8")
    print("BACKEND_PROVENANCE_WRITTEN:",args.output)
    for rec in t:
        print("BLAS_BACKEND:",rec.get("internal_api"),rec.get("version"),
              rec.get("architecture"),"threads",rec.get("num_threads"),
              "library",rec.get("filepath"),"sha256",rec.get("sha256"))

if __name__=="__main__":
    main()
