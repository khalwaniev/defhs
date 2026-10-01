"""Deterministic operators from RS2 policy 5/12/15. No protected-fold access."""
from __future__ import annotations
import hashlib, itertools, json
from pathlib import Path
import numpy as np
import pandas as pd

CLASSES = np.array(['angry', 'happy', 'neutral', 'sad'])
P_COLS = ['p_' + c for c in CLASSES]

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def dump(path, x):
    def conv(v):
        if isinstance(v, np.ndarray): return v.tolist()
        if isinstance(v, np.generic): return v.item()
        if isinstance(v, Path): return str(v)
        raise TypeError(type(v).__name__)
    Path(path).write_text(json.dumps(x, indent=2, default=conv, allow_nan=False) + '\n')

def labels(y):
    return np.array([list(CLASSES).index(str(v)) for v in y])

def f1(y, p, weights=None, per_class=False):
    y, p = np.asarray(y), np.asarray(p)
    w = np.ones(len(y)) if weights is None else np.asarray(weights)
    cm = np.bincount(4*y+p, weights=w, minlength=16).reshape(4, 4)
    d = cm.sum(0) + cm.sum(1)
    v = np.divide(2*np.diag(cm), d, out=np.zeros(4), where=d>0)
    return v if per_class else float(v.mean())

def report(y, pred, folds):
    return {'macro_f1': f1(y, pred), 'fold_macro_f1': [f1(y[folds==f], pred[folds==f]) for f in range(5)],
            'per_class_f1': dict(zip(CLASSES, f1(y, pred, per_class=True))),
            'confusion': np.bincount(4*y+pred, minlength=16).reshape(4, 4).tolist()}

class Evidence:
    def __init__(self, ids, dup, prompt):
        all_ids = sorted(set(map(int, prompt.Id)) | set(map(int, ids)))
        parent = {i: i for i in all_ids}
        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]; i = parent[i]
            return i
        def union(i, j):
            a,b = find(i), find(j)
            parent[max(a,b)] = min(a,b)
        for df, col in [(dup, 'duplicate_group'), (prompt, 'prompt_sim_0.90')]:
            for _,g in df.groupby(col):
                vals = sorted(map(int, g.Id))
                for v in vals[1:]: union(vals[0], v)
        comps = np.array([f'{find(int(i)):06d}' for i in ids])
        order = sorted(set(comps)); ci = {c:i for i,c in enumerate(order)}
        self.components = comps
        self.mult = np.random.Generator(np.random.PCG64(20260930)).exponential(1, (2000,len(order)))[:, [ci[c] for c in comps]]
        self.y = None
        self.cache = {}

    def boots(self, y, pred, mask=None):
        mask = np.ones(len(y),bool) if mask is None else np.asarray(mask)
        key = (np.asarray(pred,dtype=np.int8).tobytes(), mask.tobytes())
        if key in self.cache: return self.cache[key]
        yi, pi, w = y[mask], pred[mask], self.mult[:,mask]
        # Vectorized weighted confusion counts. Same component draws in every view.
        cm = np.stack([w[:,(yi==a)&(pi==b)].sum(1) for a in range(4) for b in range(4)], 1).reshape(-1,4,4)
        denom = cm.sum(1)+cm.sum(2)
        score = np.divide(2*np.diagonal(cm,axis1=1,axis2=2),denom,out=np.zeros_like(denom),where=denom>0).mean(1)
        self.cache[key] = score
        return score

    def intervals(self, contrasts):
        # contrasts: immutable pre-enumerated name -> (point, paired draws)
        sd = {k: float(np.std(v[1],ddof=1)) for k,v in contrasts.items()}
        z = [np.abs((v[1]-v[0])/sd[k]) for k,v in contrasts.items() if sd[k]>1e-14]
        q = float(np.quantile(np.max(z,axis=0),.95,method='higher')) if z else 0.
        return {k: {'point':float(v[0]), 'sd':sd[k], 'lower':float(v[0]-q*sd[k]), 'upper':float(v[0]+q*sd[k]), 'q':q} for k,v in contrasts.items()}

    def contrast(self, y, a, b, mask=None):
        m = np.ones(len(y),bool) if mask is None else mask
        return f1(y[m],a[m])-f1(y[m],b[m]), self.boots(y,a,m)-self.boots(y,b,m)

def robust(y,a,b,folds,interval):
    ds = [f1(y[folds==f],a[folds==f])-f1(y[folds==f],b[folds==f]) for f in range(5)]
    delete = [f1(y[folds!=f],a[folds!=f])-f1(y[folds!=f],b[folds!=f]) for f in range(5)]
    return {'pass':bool(interval['point']>0 and interval['lower']>0 and sum(d>0 for d in ds)>=4 and min(delete)>0),
            'fold_differences':ds, 'delete_fold_differences':delete, 'interval':interval}

def grid(n):
    g = [tuple(v/4 for v in w) for w in itertools.product(range(5),repeat=n) if sum(w)==4]
    eq = tuple([1/n]*n)
    return sorted(set(g+[eq]))

def choose_probability_blend(probs, y, folds, ev, allowed=None, equal_weights=None):
    # Caller passes lane IDs in immutable lexicographic order.
    n = len(probs); eq = np.array([1/n]*n if equal_weights is None else equal_weights)
    candidates = grid(n) if allowed is None else allowed
    qs = [np.einsum('k,knc->nc',w,np.asarray(probs)) for w in candidates]
    ps = [q.argmax(1) for q in qs]; equal_q = np.einsum('k,knc->nc',eq,np.asarray(probs)); equal_p = equal_q.argmax(1)
    out = np.zeros_like(equal_q); selections = []
    for fold in range(5):
        tr = folds!=fold; va = ~tr
        scores = np.array([f1(y[tr],p[tr]) for p in ps])
        order = sorted(range(len(candidates)),key=lambda j:(-scores[j],np.count_nonzero(candidates[j]),float(np.sum((np.array(candidates[j])-eq)**2)),tuple(candidates[j])))
        best = order[0]
        gain = scores[best]-f1(y[tr],equal_p[tr])
        sd = float(np.std(ev.boots(y,ps[best],tr)-ev.boots(y,equal_p,tr),ddof=1))
        use = gain>sd
        w = np.array(candidates[best]) if use else eq
        out[va] = np.einsum('k,knc->nc',w,np.asarray(probs)[:,va])
        selections.append({'fold':fold,'weights':w.tolist(),'best_training_gain':float(gain),'paired_sd':sd,'coarse_selected':bool(use)})
    return out, {'equal':report(y,equal_p,folds),'heldout':report(y,out.argmax(1),folds),'selections':selections,'grid':candidates}

def choose_offsets(p,y,folds,ev):
    vectors = [np.array(v)*np.log(2) for v in itertools.product((-1,0,1),repeat=4) if sum(v)==0]
    assert len(vectors)==19
    logp = np.log(np.clip(p,1e-12,1)); base = p.argmax(1)
    preds = [(logp+b).argmax(1) for b in vectors]
    out = base.copy(); selected = []
    for f in range(5):
        tr = folds!=f; va = ~tr
        scores = np.array([f1(y[tr],a[tr]) for a in preds])
        best = sorted(range(19),key=lambda j:(-scores[j],tuple(vectors[j])))[0]
        sd = float(np.std(ev.boots(y,preds[best],tr)-ev.boots(y,base,tr),ddof=1))
        eligible = [j for j in range(19) if scores[j]>=scores[best]-sd-1e-15]
        j = min(eligible,key=lambda j:(float(np.sum(vectors[j]**2)),tuple(vectors[j])))
        out[va]=preds[j][va]
        selected.append({'fold':f,'offset':vectors[j].tolist(),'paired_sd':sd,'best_training_f1':scores[best]})
    return out, selected

def valid_oof(path, folds, head=None):
    d = pd.read_csv(path)
    if head is not None: d = d[d['head'].eq(head)]
    d = d.sort_values('Id').reset_index(drop=True)
    assert np.array_equal(d.Id,folds.Id) and np.array_equal(d.emotion,folds.emotion)
    assert np.array_equal(d.fold,folds.fold) and d.Id.nunique()==826
    p = d[P_COLS].to_numpy(float)
    assert np.isfinite(p).all() and (p>=0).all() and (p<=1).all()
    assert np.allclose(p.sum(1),1,atol=1e-8)
    assert np.array_equal(CLASSES[p.argmax(1)],d.pred)
    return p

def save_oof(path,folds,p,**extra):
    d = folds[['Id','emotion','fold']].copy()
    d['pred'] = CLASSES[p.argmax(1)]
    for j,c in enumerate(P_COLS): d[c]=p[:,j]
    for k,v in extra.items(): d[k]=v
    d.to_csv(path,index=False)
