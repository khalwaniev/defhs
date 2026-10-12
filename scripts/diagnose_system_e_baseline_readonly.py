#!/usr/bin/env python3
"""Read-only, reference-authenticated DEFHS System E nested baseline forensic comparison.

Does not evaluate the new likelihood challenger, change tolerances, invoke Kaggle,
modify the source scientific scripts, or inspect target/protected labels.
"""
import argparse
import hashlib
import io
import json
import os
import platform
import runpy
import sys
import tempfile
import warnings
import zipfile
from pathlib import Path

D_SHA = 'fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839'
E_SHA = 'dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf'
NEWSEM_SHA = 'cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789'
NEWSEM_CSV_SHA = '8edd8dc9899f9304db2b46475758a67330f82c3c1348317646b561f3d57f6377'
LOGLIK_SHA = '66d01f825c9be4142452e6f04fb921dd8ece6c8f82aac5e0768a9941c0e4e788'
OOF_SHA = 'a7a1e456883119c60a2d5e77dd8cad93ba384cd707d66e3e5918cab974903aff'
EXPECTED_E_F1 = 0.8774091527555827
CLASSES = ['angry', 'happy', 'neutral', 'sad']
STATES = CLASSES + ['unclear']

def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()

def sha_path(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''):
            h.update(b)
    return h.hexdigest()

def get_member(z, basename):
    names = [n for n in z.namelist() if n.split('/')[-1] == basename]
    assert len(names) == 1, ('expected exactly one ZIP member', basename, names)
    return z.read(names[0])

def check_ref_file(path, expected):
    path = Path(path)
    assert path.is_file(), ('missing file', str(path))
    actual = sha_path(path)
    assert actual == expected, ('SHA256 mismatch', str(path), actual, expected)
    return {'path': str(path.resolve()), 'size_bytes': path.stat().st_size, 'sha256': actual}

def compare(p, q, ids, folds, y, F, np):
    assert p.shape == q.shape == (826,4)
    assert np.isfinite(p).all() and np.isfinite(q).all()
    diff = np.abs(p - q)
    rp = np.asarray(CLASSES)[np.argmax(p, axis=1)]
    rq = np.asarray(CLASSES)[np.argmax(q, axis=1)]
    mism = np.flatnonzero(rp != rq)
    row_delta = np.max(diff, axis=1)
    worst = np.argsort(-row_delta, kind='stable')[:20]
    def detail(i):
        a = np.sort(p[i]); b = np.sort(q[i]);
        return {'Id': int(ids[i]), 'fold': int(folds[i]), 'emotion': str(y[i]),
            'ref_pred': str(rp[i]), 'replay_pred': str(rq[i]),
            'ref_prob': [float(v) for v in p[i]], 'replay_prob': [float(v) for v in q[i]],
            'max_abs': float(row_delta[i]),
            'ref_margin': float(a[-1] - a[-2]), 'replay_margin': float(b[-1] - b[-2])}
    result = {
        'mean_absolute_probability_difference': float(diff.mean()),
        'median_absolute_probability_difference': float(np.median(diff)),
        'p95_absolute_probability_difference': float(np.quantile(diff, .95)),
        'p99_absolute_probability_difference': float(np.quantile(diff, .99)),
        'max_absolute_probability_difference': float(diff.max()),
        'elements_exceed_1e_minus_8': int(np.sum(diff >= 1e-8)),
        'elements_exceed_1e_minus_7': int(np.sum(diff >= 1e-7)),
        'element_count': int(diff.size),
        'exact_decision_agreement': bool(len(mism)==0),
        'decision_mismatch_count': int(len(mism)),
        'decision_mismatched_ids': [int(ids[i]) for i in mism],
        'reference_macro_f1': float(F['mf'](y, rp)),
        'replay_macro_f1': float(F['mf'](y, rq)),
        'per_fold': [{
            'fold': int(f),
            'n': int(np.sum(folds == f)),
            'max_absolute_probability_difference': float(diff[folds==f].max()),
            'decision_mismatch_count': int(np.sum((rp!=rq) & (folds==f))),
        } for f in range(5)],
        'decision_mismatch_details': [detail(i) for i in mism],
        'top20_probability_discrepancy_rows': [detail(i) for i in worst],
    }
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--d-zip', required=True, type=Path)
    ap.add_argument('--e-zip', required=True, type=Path)
    ap.add_argument('--semantic-zip', required=True, type=Path)
    ap.add_argument('--likelihood-csv', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    import numpy as np
    import pandas as pd
    import scipy, sklearn, joblib, threadpoolctl
    from sklearn.exceptions import ConvergenceWarning
    verified = {
        'system_d': check_ref_file(args.d_zip, D_SHA),
        'system_e': check_ref_file(args.e_zip, E_SHA),
        'new_semantic': check_ref_file(args.semantic_zip, NEWSEM_SHA),
        'likelihood_output': check_ref_file(args.likelihood_csv, LOGLIK_SHA),
    }
    report = {
        'purpose': 'READ_ONLY_BASELINE_DIAGNOSTIC_NOT_SCIENTIFIC_CHALLENGER',
        'verified_inputs': verified,
        'runtime': {
            'python': sys.version, 'executable': sys.executable,
            'platform': platform.platform(),
            'numpy': np.__version__, 'pandas': pd.__version__,
            'scipy': scipy.__version__, 'sklearn': sklearn.__version__,
            'joblib': joblib.__version__, 'threadpoolctl': threadpoolctl.__version__,
            'env_threads': {k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'PYTHONNOUSERSITE')},
            'threadpool_info_before': threadpoolctl.threadpool_info(),
        },
        'original_parity_tolerance_unchanged': 1e-8,
        'new_challenger_computed': False,
        'kaggle_competition_submission': False,
    }
    with zipfile.ZipFile(args.e_zip) as z:
        assert z.testzip() is None
        inv = json.loads(get_member(z,'SYSTEM_E_EVIDENCE_MANIFEST.json'))
        for name, meta in inv['files'].items():
            b = get_member(z,name)
            assert len(b) == meta['bytes'] and sha_bytes(b) == meta['sha256'], name
        oof_raw = get_member(z,'SYSTEM_E_PRIMARY_OOF.csv')
        assert sha_bytes(oof_raw) == OOF_SHA
        e_ref = pd.read_csv(io.BytesIO(oof_raw)).sort_values('Id').reset_index(drop=True)
        source = get_member(z,'replay_fusion.py')
    with zipfile.ZipFile(args.semantic_zip) as z:
        assert z.testzip() is None
        semantic_raw = get_member(z,'QWEN14B_TRAIN826.csv')
        assert sha_bytes(semantic_raw)==NEWSEM_CSV_SHA
        semantic = pd.read_csv(io.BytesIO(semantic_raw)).set_index('Id')
    lik = pd.read_csv(args.likelihood_csv).set_index('Id')
    assert len(lik)==len(semantic)==len(e_ref)==826
    ids = e_ref.Id.to_numpy()
    y = e_ref.emotion.to_numpy()
    fold = e_ref.fold.to_numpy()
    assert np.array_equal(np.unique(fold), np.arange(5))
    assert len(set(ids))==826
    assert set(lik.index)==set(semantic.index)==set(ids)
    lik = lik.loc[ids]
    semantic = semantic.loc[ids]
    assert (lik.greedy==lik.reference_hard).all()
    assert np.array_equal(lik.greedy.to_numpy(),semantic.semantic_label.to_numpy())
    assert np.array_equal(lik.greedy.to_numpy(),e_ref.new_asr_qwen14_state.to_numpy())
    P = lik[['trie_p_'+s for s in STATES]].to_numpy('float64')
    assert np.isfinite(P).all() and (P>=0).all() and (P<=1).all()
    report['likelihood_sanity'] = {
        'rows': int(len(P)),
        'finite_nonnegative': True,
        'max_probability_row_normalization_residual': float(np.max(np.abs(P.sum(axis=1)-1))),
        'hard_semantic_parity': True,
    }
    assert report['likelihood_sanity']['max_probability_row_normalization_residual']<5e-5
    with tempfile.TemporaryDirectory(prefix='defhs_baseline_forensic_') as td:
        root = Path(td)
        with zipfile.ZipFile(args.d_zip) as z:
            assert z.testzip() is None
            z.extractall(root)
        saved = root/'frozen_e_replay_fusion.py'
        saved.write_bytes(source)
        F = runpy.run_path(str(saved), run_name='diagnostic_read_only')
        for name, expected_sha in F['HASHES'].items():
            if name=='PROMPT_CLUSTER_ASSIGNMENTS.csv':
                # This external root authority is not used in baseline-only replay.
                continue
            files=list(root.rglob(name))
            assert len(files)==1, (name, files)
            assert sha_path(files[0])==expected_sha, (name, 'sha mismatch')
        def unique(name):
            names=list(root.rglob(name)); assert len(names)==1,(name,names)
            return names[0]
        ids2=np.load(unique('FIXED_PAIR_VB.npz'),allow_pickle=False)['Id']
        assert np.array_equal(ids,ids2)
        old8=pd.read_csv(unique('QWEN_SEMANTIC_OUTPUTS.csv')).set_index('Id').loc[ids].semantic_label.to_numpy()
        with zipfile.ZipFile(unique('DEFHS_Qwen14B_train826_outputs.zip')) as z:
            old14=pd.read_csv(io.BytesIO(get_member(z,'QWEN14B_TRAIN826.csv'))).set_index('Id').loc[ids].semantic_label.to_numpy()
        wave=np.column_stack([np.load(unique('E2V_CONTROL_VB.npz'))['prob'],
                              np.load(unique('XLSR_VB.npz'))['prob']])
        features=[]
        for name in ('emotion2vec_base_meanstd.npz','xls_r_300m_meanstd.npz'):
            z=np.load(unique(name),allow_pickle=False)
            ix={int(i):j for j,i in enumerate(z['Id'])}
            features.append(z['X'][[ix[int(i)] for i in ids]])
        hard=F['hard_mask'](wave)
        assert np.array_equal(hard,e_ref.hard316.to_numpy()) and hard.sum()==316
        base23=np.column_stack([F['onehot'](old8),F['onehot'](old14),F['onehot'](semantic.semantic_label)])
        base18=base23[:,:10]
        warnings.simplefilter('error',ConvergenceWarning)
        with threadpoolctl.threadpool_limits(limits=2):
            arrays=F['build_inner'](fold,features,y,wave)
            pD=F['fuse'](y,fold,arrays,base18)
            pE=F['fuse'](y,fold,arrays,base23)
        pDref=e_ref[['system_D_p_'+c for c in CLASSES]].to_numpy('float64')
        pEref=e_ref[['system_E_p_'+c for c in CLASSES]].to_numpy('float64')
        report['replay_system_D_18_features_vs_E_evidence'] = compare(pDref,pD,ids,fold,y,F,np)
        report['replay_system_E_23_features_vs_E_evidence'] = compare(pEref,pE,ids,fold,y,F,np)
        report['system_E_reference_performance_verified'] = abs(F['mf'](y,np.asarray(CLASSES)[np.argmax(pEref,axis=1)])-EXPECTED_E_F1)<1e-12
        report['E_source_sha256'] = sha_bytes(source)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('BASELINE_FORENSIC_REPORT:',args.output)
    for key in ('replay_system_D_18_features_vs_E_evidence','replay_system_E_23_features_vs_E_evidence'):
        val=report[key]
        print(key,'max_abs=',val['max_absolute_probability_difference'],
            'decision_mismatches=',val['decision_mismatch_count'],
            'ids=',val['decision_mismatched_ids'],
            'ref_f1=',val['reference_macro_f1'],'replay_f1=',val['replay_macro_f1'])
    print('STRICT_PARITY_REPORT_ONLY:',report['original_parity_tolerance_unchanged'],
        'new_challenger_not_evaluated')

if __name__ == '__main__':
    main()
