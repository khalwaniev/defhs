#!/usr/bin/env python3
"""Deterministic binary acquisition handoff for RS-DEFHS-KNOWLEDGE-ACQUISITION-001.

Downloads only the pre-approved open-access/high-value artifacts selected during
source/license audit, pins repository archives to exact commits, computes SHA256,
and uploads to the existing Drive warehouse with rclone. It intentionally does
NOT download external datasets or multi-GB model weights.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, shutil, subprocess, sys, urllib.request
from pathlib import Path

MISSION='RS-DEFHS-KNOWLEDGE-ACQUISITION-001'
REPO=Path('/home/fikar/zingle/defhs')
DEFAULT_STAGE=Path.home()/'.local/share/defhs'/MISSION/'warehouse'
PAPERS=[
 ('DEFHS-KNOW-0001__goel_2024__camulenet-bhavvani.pdf','https://www.isca-archive.org/interspeech_2024/goel24_interspeech.pdf'),
 ('DEFHS-KNOW-0002__kotian_2026__hindi-ser-benchmark.pdf','https://ijaimlds.com/ijaimlds/article/download/9/33/80'),
 ('DEFHS-KNOW-0006__ma_2024__emotion2vec.pdf','https://aclanthology.org/2024.findings-acl.931.pdf'),
 ('DEFHS-KNOW-0049__funaudiollm_2024__sensevoice.pdf','https://arxiv.org/pdf/2407.04051'),
 ('DEFHS-KNOW-0051__vesper_2024__paper.pdf','https://arxiv.org/pdf/2307.10757'),
 ('DEFHS-KNOW-0054__leygue_2025__attentive-pooling.pdf','https://www.isca-archive.org/interspeech_2025/leygue25_interspeech.pdf'),
 ('DEFHS-KNOW-0055__icasp2025__crosslingual-peft.pdf','https://arxiv.org/pdf/2409.16920'),
 ('DEFHS-KNOW-0057__emosllm_2025__audio-text-lora.pdf','https://arxiv.org/pdf/2508.14130'),
 ('DEFHS-KNOW-0058__2025__lora-whisper-ser-interpretability.pdf','https://arxiv.org/pdf/2509.08454'),
 ('DEFHS-KNOW-0059__jon_2025__mater.pdf','https://www.isca-archive.org/interspeech_2025/jon25_interspeech.pdf'),
 ('DEFHS-KNOW-0060__dutta_2025__abhinaya.pdf','https://www.isca-archive.org/interspeech_2025/dutta25_interspeech.pdf'),
 ('DEFHS-KNOW-0061__naini_2025__sernc-challenge.pdf','https://www.isca-archive.org/interspeech_2025/naini25_interspeech.pdf'),
 ('DEFHS-KNOW-0062__odyssey_2024__class-imbalance-ensemble.pdf','https://www.isca-archive.org/odyssey_2024/chen24_odyssey.pdf'),
 ('DEFHS-KNOW-0081__uniyal_2025__ssl-ser-benchmark.pdf','https://www.isca-archive.org/interspeech_2025/uniyal25_interspeech.pdf'),
 ('DEFHS-KNOW-0082__lertpetchpun_2025__sernc-framework.pdf','https://www.isca-archive.org/interspeech_2025/lertpetchpun25_interspeech.pdf'),
]
REPOS=[
 ('DEFHS-KNOW-0050__QwenAudio_SenseVoice__586bbdb2.zip','https://codeload.github.com/QwenAudio/SenseVoice/zip/586bbdb2b052f4fe19322581825228b6810a9fb3'),
 ('DEFHS-KNOW-0052__HappyColor_Vesper__2b62af3e.zip','https://codeload.github.com/HappyColor/Vesper/zip/2b62af3e15fbd526fac6d4f1d6fea279c306244d'),
]

def sha256(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def download(url:str,dst:Path):
 dst.parent.mkdir(parents=True,exist_ok=True)
 tmp=dst.with_suffix(dst.suffix+'.part')
 req=urllib.request.Request(url,headers={'User-Agent':'DEFHS-knowledge-acquisition/1.0'})
 with urllib.request.urlopen(req,timeout=120) as r, tmp.open('wb') as f:
  shutil.copyfileobj(r,f)
 if tmp.stat().st_size==0: raise RuntimeError(f'empty download: {url}')
 tmp.replace(dst)

def run(cmd):
 print('+',' '.join(map(str,cmd)),flush=True)
 subprocess.run(list(map(str,cmd)),check=True)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--stage',type=Path,default=DEFAULT_STAGE)
 ap.add_argument('--drive-remote',default=os.environ.get('DEFHS_RCLONE_REMOTE','gdrive'))
 ap.add_argument('--no-upload',action='store_true')
 a=ap.parse_args()
 stage=a.stage; run_dir=REPO/'runs'/MISSION
 (stage/'papers').mkdir(parents=True,exist_ok=True); (stage/'repositories').mkdir(parents=True,exist_ok=True)
 expected=set()
 with (run_dir/'KNOWLEDGE_MANIFEST.csv').open(newline='',encoding='utf-8') as f:
  for row in csv.DictReader(f):
   if row.get('acquisition_status')=='PENDING_BINARY_HANDOFF':
    expected.add(row['source_id'])
 selected={name.split('__',1)[0] for items in (PAPERS,REPOS) for name,_ in items}
 if selected != expected:
  missing=sorted(expected-selected); extra=sorted(selected-expected)
  raise RuntimeError(f'binary selection mismatch: missing={missing} extra={extra}')
 log=[]
 for kind,items in [('papers',PAPERS),('repositories',REPOS)]:
  for name,url in items:
   dst=stage/kind/name
   if not dst.exists(): download(url,dst)
   digest=sha256(dst)
   log.append({'kind':kind,'name':name,'url':url,'bytes':dst.stat().st_size,'sha256':digest})
   print(f'SHA256 {digest} {dst.stat().st_size} {kind}/{name}')
 checks=stage/'CHECKSUMS_SHA256.txt'
 base_checks=run_dir/'CHECKSUMS_SHA256.txt'
 binary_entries=[(x['sha256'],f"/DEFHS/knowledge/{x['kind']}/{x['name']}") for x in log]
 binary_paths={path for _,path in binary_entries}
 preserved=[]
 if base_checks.exists():
  for line in base_checks.read_text(encoding='utf-8').splitlines():
   if not any(line.endswith('  '+path) for path in binary_paths):
    preserved.append(line)
 merged=preserved+[f"{digest}  {path}" for digest,path in binary_entries]
 checks.write_text('\n'.join(merged).rstrip()+'\n',encoding='utf-8')
 (stage/'BINARY_ACQUISITION_RESULT.json').write_text(json.dumps({'mission':MISSION,'artifacts':log},indent=2),encoding='utf-8')
 if not a.no_upload:
  remote=f'{a.drive_remote}:DEFHS/knowledge'
  run(['rclone','copy',str(stage/'papers'),remote+'/papers','--checksum','--create-empty-src-dirs'])
  run(['rclone','copy',str(stage/'repositories'),remote+'/repositories','--checksum','--create-empty-src-dirs'])
  # Preserve lightweight control-layer manifests in Drive as well as GitHub.
  for fn in ['KNOWLEDGE_MANIFEST.csv','SOURCE_PROVENANCE.jsonl','ACQUISITION_LOG.jsonl','LICENSE_REGISTER.csv','DUPLICATE_SOURCE_MAP.csv','BHAVVAANI_PROVENANCE_RECONCILIATION.md','SOURCE_COVERAGE_REPORT.md','MISSING_EVIDENCE_REGISTER.md','POINTER_ONLY_REGISTER.md','WAREHOUSE_INDEX.md']:
   run(['rclone','copyto',str(run_dir/fn),remote+'/manifests/'+fn,'--checksum'])
  run(['rclone','copyto',str(checks),remote+'/manifests/CHECKSUMS_SHA256.txt','--checksum'])
  run(['rclone','copyto',str(stage/'BINARY_ACQUISITION_RESULT.json'),remote+'/manifests/BINARY_ACQUISITION_RESULT.json','--checksum'])
  run(['rclone','check',str(stage/'papers'),remote+'/papers','--one-way'])
  run(['rclone','check',str(stage/'repositories'),remote+'/repositories','--one-way'])
 print('BINARY_HANDOFF_COMPLETE')
 print('RESULT_JSON='+str(stage/'BINARY_ACQUISITION_RESULT.json'))

if __name__=='__main__': main()
