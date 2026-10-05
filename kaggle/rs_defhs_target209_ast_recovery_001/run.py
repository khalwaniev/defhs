#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path

subprocess.check_call([
    sys.executable, "-m", "pip", "install", "--quiet", "--no-cache-dir",
    "transformers==4.57.1",
    "huggingface_hub>=0.34,<1.0",
    "hf_xet",
    "safetensors",
    "soundfile==0.13.1",
])

here=Path(__file__).resolve().parent
exe=here/"run_rs_defhs_target209_ast_recovery_001.py"
if not exe.is_file():
    raise RuntimeError(f"Missing executor copied by push helper: {exe}")

cmd=[
    sys.executable,str(exe),
    "--mode","run",
    "--auto-kaggle",
    "--parent","/kaggle/working/ast_parent_f826b80",
    "--out","/kaggle/working/rs_defhs_target209_ast_recovery_001",
    "--device","cuda:0",
]
print("AST_RECOVERY_COMMAND="+" ".join(cmd),flush=True)
subprocess.check_call(cmd)
