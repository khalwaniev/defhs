#!/usr/bin/env python3
"""Deterministic AST recovery executor; no training, selection, submission, or protected access."""
import argparse, hashlib, json, os, platform, sys, time
from pathlib import Path

MODEL="MIT/ast-finetuned-audioset-10-10-0.4593"
REV="f826b80d28226b62986cc218e5cec390b1096902"
CLASSES=["angry","happy","neutral","sad"]; SEEDS=[20260930,20260917]; FOLDS=range(5)
PH={"config.json":"a93d525511d77e8ecc933d09674b85099815bbbb417c228a4edd655e252fb9ff",
"preprocessor_config.json":"8d04ba5a9c6fca5d39d0de2b1fd05ecf79deb589fbba279728bbebac39934231",
"model.safetensors":"ae0c1e2ad4e1381d851fa9bf298ba13ebc9c5a914cdee2dbe427a6583869924d"}
SH={(20260930,0):"1852e8dc0766378c92231cf5d6d9c55f0ea4cacc091567fc99104abdf5dd0f18",
(20260930,1):"283d97e237a9aaba8d5ecf31bed185afb01f897af4ce1c4ecc451e480ed5620f",
(20260930,2):"301e047797ca4d09b70130115d52ab26913d0b2b97cc2b0db3c44a4e7d10bc00",
(20260930,3):"66ddfd75a7086ce6d5aad6eeb548cf67d0b0f0d28a0bc0bec7e28a8f16b26fcc",
(20260930,4):"2a7167ec729ec00ffcfb6d941361b525d565b0512cde059bff3c524f08d11e24",
(20260917,0):"6a8d39be33053bef47381346d688f590b57a91935426f1531846b12443f55659",
(20260917,1):"c3c95a0465af3f4510de2a83576dd9db56d72cd354f9186438e026643b8bfdd1",
(20260917,2):"37755c2af063af0c6a01a8b60bbeaadb62a643c478f323d5f577dd501567768a",
(20260917,3):"1cb29222ff51b9a9f305ff18264b709c822c60cc2abee58055cf4c32494a6335",
(20260917,4):"a529b14754c3a236307550df898c3b6b3955b34524b448f972d27086e7f7d61c"}
OH={(20260930,0):"0e04d2355e2a6f50481d100f385261578aa0ca1d11a0d88c4c4e7cfdc50e2e2a",
(20260930,1):"de88a3ab8bface72065eb0960e0f0a666a1d350b9c5d7e037bb7b483f590853f",
(20260930,2):"49c12c82721be1f88eb51ad8ec457ca7a7e6ea387f2558ada879b162246574e2",
(20260930,3):"2c83a687d5325831c30075017ab54605f09e3e247965b7bfb1caa442e873fc72",
(20260930,4):"1c81a0ee1700cd631b6e82d982a23886bef75e8c204e5f30686c933c04f2fd4d",
(20260917,0):"137d5c7ddb44e6c6f7a1640e75db7d6cd84f464ea5111410a6fa8a8f10876702",
(20260917,1):"3a2c87550d4fffffbc3c097eff12cbb087561a631449520318e6b798e34ffd23",
(20260917,2):"55eb7ae31be0d9741707b26c808d606e6c93b323120995c2af26378e7d5ccc3a",
(20260917,3):"aee1fcc384867e62ce5900a5e9daea21d4f3e965ac7335ee28aabe3149feadb9",
(20260917,4):"46a10cbf7e17cb380e2aafd2d7db9178a9f23e4a7fd07e0b48fff4d8dfc0f10e"}
EP={(20260930,0):4,(20260930,1):6,(20260930,2):6,(20260930,3):5,(20260930,4):5,
(20260917,0):3,(20260917,1):6,(20260917,2):7,(20260917,3):4,(20260917,4):4}
KERNEL={20260930:"defhs-system3-wave1-matched-adaptation",20260917:"defhs-system3-wave1-b-vb-20260917"}
COMP="dataverse-detecting-emotions-from-hindi-speech"; MAXT=1e-4; MEANT=2e-5

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def hard(x,m):
 if not x: raise RuntimeError(m)
def dump(p,x):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
def rec(p): p=Path(p); return {"path":str(p.resolve()),"bytes":p.stat().st_size,"sha256":sha(p)}

def parent(d,download=True):
 d=Path(d); d.mkdir(parents=True,exist_ok=True)
 if download and not all((d/f).is_file() for f in PH):
  from huggingface_hub import hf_hub_download
  for f in PH: hf_hub_download(repo_id=MODEL,filename=f,revision=REV,local_dir=str(d))
 r={}
 for f,h in PH.items():
  p=d/f; hard(p.is_file(),f"missing parent {p}"); hard(sha(p)==h,f"PARENT_HASH_FAIL {f}"); r[f]=rec(p)
 import huggingface_hub
 return {"status":"PASS","model":MODEL,"revision":REV,"files":r,"timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"huggingface_hub_version":getattr(huggingface_hub,"__version__","UNKNOWN"),"storage":str(d.resolve())}

def find(root,name,need):
 hits=[p for p in Path(root).rglob(name) if p.is_dir() and all((p/x).is_file() for x in need)]
 hard(len(hits)==1,f"{name}: expected one complete root, found {hits}"); return hits[0]
def manifest_near(p):
 for q in [p,*list(p.parents)[:5]]:
  if (q/"DATA_MANIFEST.csv").is_file(): return q/"DATA_MANIFEST.csv"
 raise RuntimeError("DATA_MANIFEST.csv not found")

def data_root(root):
 hits=[]
 for p in [Path(root),*Path(root).rglob("SRCASW-BhavVaani")]:
  if p.is_dir() and all((p/x).exists() for x in ["train","test","train.csv","test.csv","sample_submission.csv"]): hits.append(p)
 if not hits:
  for p in Path(root).rglob("*"):
   if p.is_dir() and all((p/x).exists() for x in ["train","test","train.csv","test.csv","sample_submission.csv"]): hits.append(p)
 hits=list(dict.fromkeys(map(lambda x:x.resolve(),hits)))
 hard(len(hits)==1,f"competition root ambiguity: {hits}"); return hits[0]

def segments(path,proc):
 import numpy as np, soundfile as sf
 a,sr=sf.read(path,dtype="float32"); hard(sr==16000 and a.ndim==1 and np.isfinite(a).all(),f"bad audio {path}")
 out=[]; idx=[]
 for st in range(0,len(a),164080):
  raw=a[st:st+164080]
  if len(raw)<400: raw=np.pad(raw,(0,400-len(raw)))
  real=min(1024,1+(len(raw)-400)//160)
  z=proc(raw,sampling_rate=16000,return_tensors="pt")["input_values"][0].cpu()
  hard(tuple(z.shape)==(1024,128),f"feature shape {z.shape}")
  out.append(z); idx.append({"start_sample":st,"end_sample":min(st+164080,len(a)),"real_frames":real})
 return out,idx

def restore(model,base,state_path,epoch,device):
 import torch
 model.load_state_dict(base,strict=True); s=torch.load(state_path,map_location=device,weights_only=False)
 hard("head" in s and "encoder_delta" in s,"bad STATE")
 if "selected_epoch" in s: hard(int(s["selected_epoch"])==epoch,"selected_epoch mismatch")
 miss,unexp=model.load_state_dict(s["encoder_delta"],strict=False); hard(not unexp,f"unexpected delta keys {unexp}")
 h=torch.nn.Linear(768,4).to(device); h.load_state_dict(s["head"]); h.eval(); model.eval()
 return h,{"missing_base_keys":len(miss),"delta_keys":len(s["encoder_delta"])}

def infer(model,head,segs,device):
 import numpy as np, torch
 q=[]
 with torch.no_grad():
  for z in segs:
   r=model(z.unsqueeze(0).to(device)).pooler_output[0]
   q.append(torch.softmax(head(r),-1).cpu().numpy())
 p=np.stack(q).mean(0); hard(np.isfinite(p).all() and abs(float(p.sum())-1)<1e-5,"bad probability"); return p.astype("float64")

def run(args):
 import numpy as np, pandas as pd, torch
 from transformers import ASTFeatureExtractor, ASTModel
 out=Path(args.out); out.mkdir(parents=True,exist_ok=True); pi=parent(args.parent)
 search=Path("/kaggle/input") if args.auto_kaggle else Path(args.search)
 if args.auto_kaggle:
  s1=find(search,"B_VB_seed20260930",[f"B1_fold{k}_refit_STATE.pt" for k in FOLDS]+[f"B1_fold{k}_OOF.npz" for k in FOLDS])
  s2=find(search,"B_VB_seed20260917",[f"B1_fold{k}_refit_STATE.pt" for k in FOLDS]+[f"B1_fold{k}_OOF.npz" for k in FOLDS])
  dr=data_root(search/COMP if (search/COMP).exists() else search)
 else:
  s1=Path(args.seed1) if args.seed1 else find(search,"B_VB_seed20260930",[f"B1_fold{k}_refit_STATE.pt" for k in FOLDS]+[f"B1_fold{k}_OOF.npz" for k in FOLDS])
  s2=Path(args.seed2) if args.seed2 else find(search,"B_VB_seed20260917",[f"B1_fold{k}_refit_STATE.pt" for k in FOLDS]+[f"B1_fold{k}_OOF.npz" for k in FOLDS])
  dr=Path(args.data) if args.data else data_root(search)
 roots={20260930:s1,20260917:s2}
 for s in SEEDS:
  for k in FOLDS:
   hard(sha(roots[s]/f"B1_fold{k}_refit_STATE.pt")==SH[(s,k)],f"STATE hash fail {s}/{k}")
   hard(sha(roots[s]/f"B1_fold{k}_OOF.npz")==OH[(s,k)],f"OOF hash fail {s}/{k}")
 m1=manifest_near(s1); m2=manifest_near(s2); hard(sha(m1)==sha(m2),"manifest mismatch")
 dm=pd.read_csv(m1).set_index("Id"); hard(len(dm)==1035 and dm.index.is_unique,"manifest invalid")
 sample=pd.read_csv(dr/"sample_submission.csv"); ids=sample.Id.astype(int).to_numpy()
 hard(len(ids)==209 and len(set(ids))==209 and set(ids)==set(dm.index[dm.split.eq("test")]),"TARGET209 ID mismatch")
 proc=ASTFeatureExtractor.from_pretrained(str(args.parent),local_files_only=True)
 hard(proc.sampling_rate==16000 and proc.num_mel_bins==128 and proc.max_length==1024 and proc.mean==-4.2677393 and proc.std==4.5689974 and proc.padding_side=="right" and not proc.return_attention_mask,"processor mismatch")
 model=ASTModel.from_pretrained(str(args.parent),local_files_only=True,attn_implementation="sdpa")
 hard(model.config.time_stride==10 and model.config.frequency_stride==10 and len(model.encoder.layer)==12,"parent config mismatch")
 model.eval(); [p.requires_grad_(False) for p in model.parameters()]
 base={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}; model=model.to(args.device)
 plans={}; need=set(ids.tolist())
 for s in SEEDS:
  for k in FOLDS:
   z=np.load(roots[s]/f"B1_fold{k}_OOF.npz",allow_pickle=False); oi=z["Id"].astype(int); op=z["prob"]
   sel=[0,len(oi)//2,len(oi)-1]; plans[(s,k)]=(oi,op,sel); need.update(oi[sel].tolist())
 feats={}; segidx=[]
 for i in sorted(need):
  r=dm.loc[i]; p=dr/str(r.split)/str(r.filename)
  hard(p.is_file() and sha(p)==str(r.file_sha256),f"audio hash/path fail Id={i}")
  q,ix=segments(p,proc); feats[i]=q; segidx.append({"Id":int(i),"split":str(r.split),"segments":ix})
 dump(out/"AST_SEGMENT_INDEX_RECOVERY.json",segidx)
 diffs=[]; rows=[]; hm=0
 for s in SEEDS:
  for k in FOLDS:
   head,_=restore(model,base,roots[s]/f"B1_fold{k}_refit_STATE.pt",EP[(s,k)],args.device)
   oi,op,sel=plans[(s,k)]
   for j in sel:
    q=infer(model,head,feats[int(oi[j])],args.device); d=np.abs(q-op[j].astype("float64")); mm=int(q.argmax()!=op[j].argmax())
    hm+=mm; diffs.extend(d.tolist()); rows.append({"seed":s,"fold":k,"Id":int(oi[j]),"new":q.tolist(),"historical":op[j].tolist(),"max_abs_diff":float(d.max()),"hard_label_mismatch":mm})
 par={"status":"PASS","model_row_comparisons":len(rows),"unique_audio_rows":len({x["Id"] for x in rows}),"max_abs_diff":float(max(diffs)),"mean_abs_diff":float(np.mean(diffs)),"hard_label_mismatches":hm,"max_tol":MAXT,"mean_tol":MEANT,"details":rows}
 if hm or par["max_abs_diff"]>MAXT or par["mean_abs_diff"]>MEANT: par["status"]="FAIL"
 dump(out/"PARITY_PREFLIGHT.json",par); hard(par["status"]=="PASS","PARITY_FAIL; TARGET209 inference prohibited")
 allp=np.empty((2,5,209,4),dtype="float64")
 for si,s in enumerate(SEEDS):
  for k in FOLDS:
   head,_=restore(model,base,roots[s]/f"B1_fold{k}_refit_STATE.pt",EP[(s,k)],args.device)
   for j,i in enumerate(ids): allp[si,k,j]=infer(model,head,feats[int(i)],args.device)
 seedp=allp.mean(1); final=seedp.mean(0)
 hard(np.isfinite(final).all() and np.allclose(final.sum(1),1,atol=1e-6),"aggregate probability failure")
 pred=final.argmax(1); sp=np.sort(final,axis=1)
 ev=pd.DataFrame({"Id":ids,"p_angry":final[:,0],"p_happy":final[:,1],"p_neutral":final[:,2],"p_sad":final[:,3],"predicted_class":[CLASSES[x] for x in pred],"confidence":final.max(1),"margin":sp[:,-1]-sp[:,-2],"model":"B1_AST_SEED_MEAN","model_revision":REV,"class_order":"|".join(CLASSES)})
 csv=out/"TARGET209_AST_EVIDENCE.csv"; ev.to_csv(csv,index=False)
 npz=out/"TARGET209_AST_FOLD_SEED_PROBS.npz"; np.savez_compressed(npz,Id=ids,classes=np.array(CLASSES),seeds=np.array(SEEDS),model_prob=allp.astype("float32"),seed_prob=seedp.astype("float32"),final_prob=final.astype("float32"))
 summary={"mission":"RS-DEFHS-TARGET209-SPECTROGRAM-EVIDENCE-001","addendum":"SPECTROGRAM_EXECUTION_RECOVERY","status":"AST_TARGET209_EVIDENCE_COMPLETE","parent":pi,"parity":{k:v for k,v in par.items() if k!="details"},"target209":{"rows":209,"artifact":rec(csv),"prob_artifact":rec(npz),"class_order":CLASSES},"runtime":{"python":sys.version,"platform":platform.platform(),"torch":torch.__version__,"device":args.device,"transformers":__import__("transformers").__version__,"numpy":np.__version__,"pandas":pd.__version__},"aggregation":{"segment":"mean_softmax_probability","outer_models":"uniform_mean_5","seeds":"arithmetic_mean_2"},"training":False,"kaggle_submission":False,"protected_validation":False,"retrieval_map_modified":False}
 dump(out/"TARGET209_AST_RECOVERY_SUMMARY.json",summary)
 print("RS_DEFHS_AST_RECOVERY_SUMMARY="+json.dumps({"status":summary["status"],"parent_sha256":pi["files"]["model.safetensors"]["sha256"],"parent_bytes":pi["files"]["model.safetensors"]["bytes"],"parity_rows":par["model_row_comparisons"],"parity_max_abs_diff":par["max_abs_diff"],"parity_mean_abs_diff":par["mean_abs_diff"],"parity_hard_label_mismatches":hm,"target209_rows":209,"target209_artifact":str(csv.resolve()),"target209_artifact_sha256":sha(csv),"prob_artifact_sha256":sha(npz)},sort_keys=True),flush=True)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--mode",choices=["acquire-parent","run"],default="run")
 ap.add_argument("--parent",type=Path,default=Path.home()/".cache/defhs/ast_parent_f826b80"); ap.add_argument("--out",default="runs/RS-DEFHS-TARGET209-SPECTROGRAM-EVIDENCE-001/recovery_output")
 ap.add_argument("--device",default="cpu"); ap.add_argument("--auto-kaggle",action="store_true"); ap.add_argument("--search",default="/home/fikar/zingle/defhs/.tmp"); ap.add_argument("--seed1"); ap.add_argument("--seed2"); ap.add_argument("--data")
 a=ap.parse_args()
 if a.mode=="acquire-parent":
  x=parent(a.parent); dump(a.parent/"PARENT_ACQUISITION.json",x); print("PARENT_ACQUISITION="+json.dumps({"status":"PASS","sha256":x["files"]["model.safetensors"]["sha256"],"bytes":x["files"]["model.safetensors"]["bytes"],"storage":x["files"]["model.safetensors"]["path"]},sort_keys=True)); return
 run(a)
if __name__=="__main__": main()
