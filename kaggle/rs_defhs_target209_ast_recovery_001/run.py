#!/usr/bin/env python3
import hashlib, subprocess, sys, urllib.request
from pathlib import Path

# Pin the executor to the exact immutable Git commit that introduced the final
# recovery script. Kaggle kernels do not reliably bundle arbitrary sidecar
# source files next to code_file, so fetch it explicitly and verify the Git blob.
EXECUTOR_COMMIT = "aec22601ff5995455627af4b5a233415c507e43f"
EXECUTOR_BLOB_SHA1 = "9591a2517689e7ef05da85af1ae9adbb4f9a051f"
EXECUTOR_URL = (
    "https://raw.githubusercontent.com/khalwaniev/defhs/"
    + EXECUTOR_COMMIT
    + "/scripts/run_rs_defhs_target209_ast_recovery_001.py"
)

subprocess.check_call([
    sys.executable, "-m", "pip", "install", "--quiet", "--no-cache-dir",
    "transformers==4.57.1",
    "huggingface_hub>=0.34,<1.0",
    "hf_xet",
    "safetensors",
    "soundfile==0.13.1",
])

exe = Path("/kaggle/working/run_rs_defhs_target209_ast_recovery_001.py")
with urllib.request.urlopen(EXECUTOR_URL, timeout=120) as r:
    payload = r.read()

git_blob_sha1 = hashlib.sha1(
    b"blob " + str(len(payload)).encode() + b"\0" + payload
).hexdigest()
if git_blob_sha1 != EXECUTOR_BLOB_SHA1:
    raise RuntimeError(
        f"Executor blob mismatch: got {git_blob_sha1}, expected {EXECUTOR_BLOB_SHA1}"
    )

exe.write_bytes(payload)
subprocess.check_call([sys.executable, "-m", "py_compile", str(exe)])

cmd=[
    sys.executable,str(exe),
    "--mode","run",
    "--auto-kaggle",
    "--parent","/kaggle/working/ast_parent_f826b80",
    "--out","/kaggle/working/rs_defhs_target209_ast_recovery_001",
    "--device","cuda:0",
]
print("EXECUTOR_SOURCE="+EXECUTOR_URL, flush=True)
print("EXECUTOR_GIT_BLOB_SHA1="+git_blob_sha1, flush=True)
print("AST_RECOVERY_COMMAND="+" ".join(cmd),flush=True)
subprocess.check_call(cmd)
