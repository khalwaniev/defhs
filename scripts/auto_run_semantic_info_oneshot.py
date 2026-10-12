#!/usr/bin/env python3
"""Discover exact authenticated DEFHS evidence by SHA256 and run the one-shot CPU test.

Searches filenames only in user-specified roots; does not copy, modify or submit.
Will not substitute different archives or create synthetic training inputs.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REQUIRED={
    "d_zip": "fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839",
    "e_zip": "dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf",
    "new_q14_zip": "cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789",
    "likelihood_csv": "66d01f825c9be4142452e6f04fb921dd8ece6c8f82aac5e0768a9941c0e4e788",
}
PROMPT_SHA="458712cfee51e0cf65ef57d1a0deb8f81dcb70e4ecfe6ebfc73220f3aefac005"

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--scan-root",type=Path,action="append",required=True,
                   help="Directory containing existing research archives / likelihood CSV")
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--prob-columns",nargs=5,default=None)
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    found={}
    inspected=0
    roots=[r.expanduser().resolve() for r in a.scan_root if r.is_dir()]
    assert roots, "None of the supplied artifact search directories exists"
    omit={".git",".venv","venv","env","node_modules","site-packages","__pycache__",
          ".cache",".ipynb_checkpoints","wandb"}
    for r in roots:
        for top,dirs,files in os.walk(r,followlinks=False):
            dirs[:]=sorted(x for x in dirs if x not in omit)
            for fn in sorted(files):
                lower=fn.lower()
                if lower.endswith(".zip"):
                    if not any(x in lower for x in
                        ("defhs","system_d","system_e","semantic","qwen","train826","delivery","scientific")):
                        continue
                elif lower.endswith(".csv"):
                    if not any(x in lower for x in
                        ("likeli","trie","constrained","probability","prompt_cluster")):
                        continue
                else:
                    continue
                path=Path(top)/fn
                try:
                    if not path.is_file():continue
                    if lower.endswith(".csv") and path.stat().st_size>10_000_000:continue
                    key=sha256(path)
                except OSError:
                    continue
                inspected+=1
                for name,expected in REQUIRED.items():
                    if expected==key and name not in found:
                        found[name]=str(path)
                        print("AUTHENTIC MATCH",name,str(path),flush=True)
                if key==PROMPT_SHA and "prompt_csv" not in found:
                    found["prompt_csv"]=str(path)
                    print("AUTHENTIC MATCH", "prompt_csv",str(path),flush=True)
    record={"mission":"RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001-CONTINUATION",
            "scanned_roots":[str(x) for x in roots],
            "inspected_candidates":inspected,"found":found,
            "missing":[name for name in REQUIRED if name not in found]}
    (a.out/"ARTIFACT_DISCOVERY.json").write_text(json.dumps(record,indent=2)+"\n")
    if record["missing"]:
        print(json.dumps({"status":"BLOCKED_AUTHENTIC_INPUT_MISSING",**record},indent=2),flush=True)
        raise SystemExit(2)
    target=ROOT/"scripts/one_shot_semantic_information_23f_28f.py"
    cmd=[sys.executable,str(target),
         "--d-zip",found["d_zip"],"--e-zip",found["e_zip"],
         "--new-q14-zip",found["new_q14_zip"],
         "--likelihood-csv",found["likelihood_csv"],
         "--out",str(a.out)]
    if "prompt_csv" in found:cmd+=["--prompt-csv",found["prompt_csv"]]
    if a.prob_columns:cmd+=["--prob-columns",*a.prob_columns]
    print("RUNNING ONE SHOT EVALUATOR; no submission actions",flush=True)
    raise SystemExit(subprocess.run(cmd,check=False).returncode)

if __name__=="__main__":
    main()
