#!/usr/bin/env python3
"""Label-blind reduction of authenticated emotion2vec frames; never reads test frames."""
import argparse, hashlib, json, time
from pathlib import Path
import h5py
import numpy as np
import pandas as pd

FRAME_SHA = 'b292f8e18193f73d86fb518d4418e067f6aa2d52ef5786b3afdbfb5b9e20e368'
MEANSTD_SHA = '4b8b6feeedc83ca2712b7fd21d9683465a07f7fcb82ca0c1d625512acf64326f'
FOLD_SHA = '87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b'
ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def pool(x):
    # Exactly the authenticated float32 population-std recipe.
    return np.concatenate([x.mean(axis=0), x.std(axis=0, ddof=0)])

def reduce_frames(x):
    assert x.ndim == 2 and x.shape[1] == 768 and x.shape[0] >= 6
    assert x.dtype == np.float32 and np.isfinite(x).all()
    bounds = [len(x)*j//3 for j in range(4)]
    local = np.stack([pool(x[bounds[j]:bounds[j+1]]) for j in range(3)])
    # Prespecified negative control: spread each window over the entire utterance.
    interleaved = np.stack([pool(x[j::3]) for j in range(3)])
    return local, interleaved, bounds

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--frames',required=True,type=Path)
    p.add_argument('--meanstd',required=True,type=Path)
    p.add_argument('--folds',type=Path,default=ROOT/'runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VB_FOLDS.csv')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); start=time.monotonic()
    assert not a.out.exists(), 'Preserve the existing output; use a fresh output path.'
    for path,expected in [(a.frames,FRAME_SHA),(a.meanstd,MEANSTD_SHA),(a.folds,FOLD_SHA)]:
        assert sha(path)==expected, f'Unauthenticated input: {path.name}'
    # Read only identity, never training labels, from the frozen membership file.
    ids=pd.read_csv(a.folds,usecols=['Id']).Id.sort_values().to_numpy(dtype=np.int64)
    assert len(ids)==826 and len(set(ids))==826
    z=np.load(a.meanstd,allow_pickle=False); pos={int(i):k for k,i in enumerate(z['Id'])}
    local=[];control=[];lengths=[];boundaries=[]
    with h5py.File(a.frames,'r') as h:
        assert all(str(int(i)) in h for i in ids)
        for i in ids:
            x=h[str(int(i))][:]
            assert np.array_equal(pool(x),z['X'][pos[int(i)]]), f'Global pooling parity failed: {i}'
            lo,co,bs=reduce_frames(x); local.append(lo);control.append(co)
            lengths.append(len(x));boundaries.append(bs)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('wb') as w:
        np.savez_compressed(w,Id=ids,local=np.stack(local),interleaved=np.stack(control),
                            lengths=np.array(lengths),boundaries=np.array(boundaries))
    j={'status':'REDUCTION_COMPLETE_NOT_EVALUATED','rows':826,'window_count':3,'window_dimension':1536,
       'encoder':'iic/emotion2vec_base','revision':'v2.0.4',
       'encoder_weight_sha256':'4f14ddf7ba394bcafdd4bff6ae0f24ab2e4134260d4dd42c58ea791a201b02dd',
       'frame_sha256':FRAME_SHA,'meanstd_sha256':MEANSTD_SHA,'fold_sha256':FOLD_SHA,
       'output_sha256':sha(a.out),'bytes':a.out.stat().st_size,'seconds':time.monotonic()-start,
       'global_pooling_exact_rows':826,'labels_read':False,'target209_frames_read':False,
       'gpu_hours':0,'code_sha256':sha(__file__),
       'local_vs_interleaved_max_abs':float(np.max(np.abs(np.stack(local)-np.stack(control))))}
    a.out.with_suffix('.json').write_text(json.dumps(j,indent=2)+'\n')
    print(json.dumps(j,indent=2))

if __name__=='__main__': main()
