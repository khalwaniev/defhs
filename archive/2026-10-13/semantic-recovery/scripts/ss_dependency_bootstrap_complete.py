#!/usr/bin/env python3
"""Finish exactly the frozen 656-component max-t bootstrap from already computed one-shot 28F OOF.
Does not fit models, does not alter original PRERoot PRIMARY_RESULT.json, no target/test inference.
"""
import argparse,hashlib,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
C=np.array(['angry','happy','neutral','sad'])

def mf(y,p):
 den=np.array([(y==k).sum()+(p==k).sum() for k in C],float)
 num=np.array([2*np.sum((y==k)&(p==k)) for k in C],float)
 return float(np.divide(num,den,out=np.zeros(4),where=den>0).mean())

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--roots-zip',type=Path,required=True)
 ap.add_argument('--primary-result',type=Path,required=True)
 ap.add_argument('--challenger-oof',type=Path,required=True)
 ap.add_argument('--output',type=Path,required=True)
 a=ap.parse_args()
 result=json.loads(a.primary_result.read_text())
 assert result['status']=='BLOCKED_DEPENDENCY_BOOTSTRAP','Only apply to the original five-gate PASS, not to FAILs or reruns'
 assert all(result['gates'][k] for k in ['gain_ge_0_005','at_least_4_positive_folds','no_per_class_loss_gt_0_02','hard316_nonnegative','leave_one_fold_positive'])
 oof=pd.read_csv(a.challenger_oof).sort_values('Id')
 assert len(oof)==826 and oof.Id.is_unique
 assert len(set(oof.fold))==5
 y=oof.emotion.to_numpy();a0=oof.system_E_pred.to_numpy();b=oof.challenger_pred.to_numpy()
 assert abs(mf(y,a0)-result['baseline_macroF1'])<1e-12
 assert abs(mf(y,b)-result['challenger_macroF1'])<1e-12
 delta=mf(y,b)-mf(y,a0)
 assert abs(delta-result['delta'])<1e-12
 with zipfile.ZipFile(a.roots_zip) as z:
  hits=[x for x in z.namelist() if x.split('/')[-1]=='component_roots.b36']
  assert len(hits)==1,(hits,'Authentic root filename missing or ambiguous')
  s=z.read(hits[0]).decode().strip().replace('\n','')
 assert len(s)==1652
 roots=np.array([int(s[i:i+2],36) for i in range(0,len(s),2)])
 assert roots.sum()==351348 and len(set(roots))==656
 comps=sorted(set(roots));ix={r:i for i,r in enumerate(comps)}
 weights=np.random.Generator(np.random.PCG64(20260930)).exponential(1,(2000,len(comps)))[:,[ix[r] for r in roots]]
 v={k:i for i,k in enumerate(C)}
 yi=np.array([v[t] for t in y]); ai=np.array([v[t] for t in a0]); bi=np.array([v[t] for t in b])
 def boot_f1(p):
  mat=np.stack([weights[:,(yi==k)&(p==j)].sum(axis=1) for k in range(4) for j in range(4)],axis=1).reshape(-1,4,4)
  den=mat.sum(axis=1)+mat.sum(axis=2)
  return np.divide(2*np.diagonal(mat,axis1=1,axis2=2),den,out=np.zeros_like(den),where=den>0).mean(1)
 draws=boot_f1(bi)-boot_f1(ai)
 sd=float(np.std(draws,ddof=1))
 q=float(np.quantile(np.abs((draws-delta)/sd),.95,method='higher')) if sd>0 else float('inf')
 interval=[float(delta-q*sd),float(delta+q*sd)]
 good=interval[0]>0
 out={'status':'PRIMARY_PASS_PENDING_STRESS' if good else 'STOP_PRIMARY_GATE_FAILED',
      'certification':'frozen sixth dependency bootstrap gate computed from unchanged, fitted one-shot outer OOF',
      'primary_result_sha256':hashlib.sha256(a.primary_result.read_bytes()).hexdigest(),
      'challenger_oof_sha256':hashlib.sha256(a.challenger_oof.read_bytes()).hexdigest(),
      'root_archive_sha256':hashlib.sha256(a.roots_zip.read_bytes()).hexdigest(),
      'pooled_delta':delta,'components':len(comps),'draws':len(draws),
      'max_t_95_interval':interval,'dependency_bootstrap_lower_positive':good,
      'other_five_frozen_gates':result['gates'],'target209_inferred':False,'submitted':False}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 assert not a.output.exists(),'Do not overwrite a prior scientific certificate'
 a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
