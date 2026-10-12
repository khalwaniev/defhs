#!/usr/bin/env python3
"""Pure reporting: numerical ranking margins; changes neither frozen gates nor predictions."""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
C=['angry','happy','neutral','sad']

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--challenger-oof',type=Path,required=True)
 ap.add_argument('--output',type=Path,required=True)
 a=ap.parse_args()
 x=pd.read_csv(a.challenger_oof)
 assert len(x)==826 and x.Id.is_unique
 out={}
 for prefix,label in [('E_p_','system_E_pred'),('challenger_p_','challenger_pred')]:
  p=x[[prefix+c for c in C]].to_numpy(float)
  assert p.shape==(826,4) and np.isfinite(p).all()
  assert np.array_equal(np.array(C)[p.argmax(axis=1)],x[label].to_numpy())
  sortedp=np.sort(p,axis=1);m=sortedp[:,-1]-sortedp[:,-2]
  top=np.argsort(m)[:15]
  out[label]={'min_top_two_margin':float(m.min()),'median_margin':float(np.median(m)),
   'count_margin_le_1e_minus_8':int((m<=1e-8).sum()),
   'count_margin_le_1e_minus_6':int((m<=1e-6).sum()),
   'count_margin_le_1e_minus_5':int((m<=1e-5).sum()),
   'count_margin_le_1e_minus_4':int((m<=1e-4).sum()),
   'lowest_margin_ids':[{'Id':int(x.Id.iloc[i]),'margin':float(m[i]),'prediction':str(x[label].iloc[i])}for i in top]}
 out['interpretation']='Ranking-margin sensitivity diagnostic only. Cannot certify stability under other software/backends without rerunning the unchanged frozen candidate under a second authenticated parity-valid environment.'
 a.output.parent.mkdir(parents=True,exist_ok=True)
 assert not a.output.exists(),'Do not overwrite audit'
 a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
