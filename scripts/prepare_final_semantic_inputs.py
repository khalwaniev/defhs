#!/usr/bin/env python3
"""Collect existing private scientific artifacts by exact hash; no new downloads.

Search only approved basenames. Never open protected validation files.
Missing inputs are reported with canonical Drive links in INPUT_MANIFEST.json.
"""
import argparse,hashlib,json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--search-root',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    specs=json.loads((ROOT/'runs/RS-DEFHS-FINAL-SEMANTIC-CHALLENGER-001/INPUT_MANIFEST.json').read_text())['external_inputs']
    a.out.mkdir(parents=True,exist_ok=True);missing=[]
    for name,s in specs.items():
        if not s.get('required_for_evaluation'):continue
        target=a.out/name
        if target.exists():
            assert sha(target)==s['sha256'],f'Existing destination checksum mismatch: {target}'
            continue
        candidates=[p for p in a.search_root.rglob(name) if p.is_file()
            and 'PROTECTED' not in str(p).upper() and 'VALIDATION_VP' not in str(p).upper()]
        match=next((p for p in candidates if sha(p)==s['sha256']),None)
        if match is None:missing.append({'name':name,'download':s['drive_url'],'sha256':s['sha256']})
        else:shutil.copyfile(match,target)
    print(json.dumps({'status':'MISSING_INPUTS' if missing else 'READY','missing':missing},indent=2))
    if missing:raise SystemExit(2)
if __name__=='__main__':main()
