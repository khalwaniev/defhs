#!/usr/bin/env python3
"""Q960_606 frozen subgroup paired D/E/new diagnostic after primary PASS only.
Uses authenticated E scientific evidence manifest and original immutable flag bits.
Not a substitute for full V-A/dtype/Q960/private-allocation stress.
"""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd

D=['angry','happy','neutral','sad']

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--e-zip',type=Path,required=True)
 ap.add_argument('--challenger-oof',type=Path,required=True)
 ap.add_argument('--output',type=Path,required=True)
 a=ap.parse_args()
 assert hashlib.sha256(a.e_zip.read_bytes()).hexdigest()=='dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf'
 with zipfile.ZipFile(a.e_zip) as z:
  manifest=json.loads(z.read('SYSTEM_E_EVIDENCE_MANIFEST.json'))
  for name,rec in manifest['files'].items():
   assert hashlib.sha256(z.read(name)).hexdigest()==rec['sha256']
  official=pd.read_csv(io.BytesIO(z.read('SYSTEM_E_PRIMARY_OOF.csv'))).sort_values('Id').reset_index(drop=True)
  flags=np.frombuffer(bytes.fromhex(z.read('manifest_flags.hex').decode()),dtype='>u2').astype(int)
 new=pd.read_csv(a.challenger_oof).sort_values('Id').reset_index(drop=True)
 assert len(official)==len(new)==len(flags)==826
 assert np.array_equal(official.Id,new.Id) and np.array_equal(official.emotion,new.emotion)
 assert np.array_equal(official.system_E_pred,new.system_E_pred)
 cohort=(flags&(256<<3))!=0  # Exact frozen Q960_606 bit encoding.
 assert int(cohort.sum())==41,int(cohort.sum())
 Y=official.emotion.to_numpy()[cohort]
 supports={c:int((Y==c).sum()) for c in D}
 assert [supports[c] for c in D]==[6,10,13,12],supports
 def mf(t,p):
  return float(np.mean([(2*((t==c)&(p==c)).sum()/((t==c).sum()+(p==c).sum()) if ((t==c).sum()+(p==c).sum()) else 0) for c in D]))
 pred={k:official[k].to_numpy()[cohort] for k in ('system_D_pred','system_E_pred')}
 pred['challenger_pred']=new.challenger_pred.to_numpy()[cohort]
 f1={k:mf(Y,v) for k,v in pred.items()}
 assert abs(f1['system_E_pred']-f1['system_D_pred']+0.03367392841077055)<1e-12,f1
 bad=np.where(pred['system_E_pred']!=pred['challenger_pred'])[0]
 ids=official.Id.to_numpy()[cohort]
 report={'status':'Q960_606_SUBGROUP_DIAGNOSTIC','n':41,'support':supports,
         'frozen_D_F1':f1['system_D_pred'],'frozen_E_F1':f1['system_E_pred'],
         'challenger_F1':f1['challenger_pred'],
         'E_minus_D':f1['system_E_pred']-f1['system_D_pred'],
         'challenger_minus_D':f1['challenger_pred']-f1['system_D_pred'],
         'challenger_minus_E':f1['challenger_pred']-f1['system_E_pred'],
         'predeclared_Q960_D_baseline_noninferiority_pass':(f1['challenger_pred']-f1['system_D_pred'])>=-0.02,
         'changed_vs_E_ids':[int(ids[i]) for i in bad],
         'changed_vs_E':len(bad),'full_stress_complete':False}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
