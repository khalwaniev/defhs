#!/usr/bin/env python3
"""One authorized A/B protected confirmation, then frozen submission preparation."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import time
import warnings
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001'
DS = ROOT / 'runs/DS-DEFHS-VALIDATION-HARDENING-002'
WORK = ROOT / 'work/protected_confirmation'
V3 = ROOT / '.tmp/rs_system_implementation_001_frozen_screen_v3/rs_defhs_system_implementation_001'
OUT = ROOT / 'work/frozen_closure'
START = '67ae599a89e98ad4c185621bf030db9df9d9b7e8'
VP_HASH = 'b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c'
ACOUSTIC_HASH = 'd8769829f6e2ca351e96068e64d89b95977cca83fb49f0ef7d0d597f11c06a53'
SAMPLE_HASH = 'f31b5e849fda2e1d42b9b551a4383750ce0a57fdaee837455d8e56a14039e9c8'
SOURCE_ZIP = Path('/mnt/c/Users/fikar/Downloads/dataverse-detecting-emotions-from-hindi-speech.zip')
CLASSES = np.array(['angry', 'happy', 'neutral', 'sad'])
NOTE = RUN / 'PROTECTED_CONFIRMATION.md'
RESULT = RUN / 'PROTECTED_CONFIRMATION.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def reference():
    # Exact historical ordinary hard-label pipeline, without probability calibration.
    return make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
                         SVC(C=10, kernel='rbf', gamma='scale'))


def finalist():
    return make_pipeline(StandardScaler(),
                         LogisticRegression(C=1, max_iter=5000, random_state=20261001))


def metrics(y, pred, folds):
    return {
        'aggregate_macro_f1': float(f1_score(y, pred, labels=CLASSES, average='macro')),
        'fold_macro_f1': [float(f1_score(y[folds == k], pred[folds == k],
                                       labels=CLASSES, average='macro')) for k in range(5)],
        'per_class_f1': dict(zip(CLASSES, f1_score(y, pred, labels=CLASSES,
                                                average=None).tolist())),
        'confusion_matrix': confusion_matrix(y, pred, labels=CLASSES).tolist(),
        'confusion_order': CLASSES.tolist(),
    }


def inputs():
    """Hash protected bytes, but do not parse protected assignments here."""
    assert git('branch', '--show-current') == 'rs/system-implementation-001'
    subprocess.run(['git', 'merge-base', '--is-ancestor', START, 'HEAD'], cwd=ROOT, check=True)
    lock = json.loads((RUN / 'FINAL_SYSTEM_LOCK.json').read_text())
    checks = {
        DS / 'VALIDATION_VP_PROTECTED_FOLDS.csv': VP_HASH,
        V3 / 'emotion2vec_base_meanstd.npz': lock['encoder_cache_sha256'],
        DS / 'RETRIEVAL_MAP_FINAL.csv': lock['retrieval_map_sha256'],
        OUT / 'LOCKED_FINALIST_ALL826_LOGISTIC.joblib': lock['serialized_model_sha256'],
        OUT / 'LOCKED_FINALIST_TEST_INFERENCE.csv': lock['test_inference_sha256'],
        ROOT / 'work/mission_inputs/ACOUSTIC_FEATURES_FULL.csv': ACOUSTIC_HASH,
        WORK / 'sample_submission.csv': SAMPLE_HASH,
    }
    inventory = {r['artifact']: r['sha256'] for r in
                 json.loads((DS / 'CANONICAL_ARTIFACT_INVENTORY.json').read_text())}
    for name in ['DATA_MANIFEST.csv', 'VALIDATION_VA_FOLDS.csv', 'VALIDATION_VB_FOLDS.csv',
                 'VALIDATION_OOF_FIXED.csv']:
        checks[DS / name] = inventory[name]
    for p, expected in checks.items():
        assert sha(p) == expected, f'Hash mismatch: {p}'
    train = pd.read_csv(DS / 'VALIDATION_VB_FOLDS.csv').sort_values('Id').reset_index(drop=True)
    dm = pd.read_csv(DS / 'DATA_MANIFEST.csv')
    sample = pd.read_csv(WORK / 'sample_submission.csv')
    assert sample.columns.tolist() == ['Id', 'emotion'] and len(sample) == 209
    assert not sample.isna().any().any() and sample.Id.is_unique
    assert set(sample.Id) == set(dm.loc[dm.split == 'test', 'Id'])
    with zipfile.ZipFile(SOURCE_ZIP) as z:
        assert z.read('SRCASW-BhavVaani/sample_submission.csv') == (WORK / 'sample_submission.csv').read_bytes()
        original_train = pd.read_csv(io.BytesIO(z.read('SRCASW-BhavVaani/train.csv')))
        original_test = pd.read_csv(io.BytesIO(z.read('SRCASW-BhavVaani/test.csv')))
    assert np.array_equal(original_test.Id, sample.Id)
    pd.testing.assert_frame_equal(train[['Id', 'filename', 'emotion']],
                                  original_train.sort_values('Id').reset_index(drop=True))
    assert len(train) == 826 and train.Id.is_unique
    z = np.load(V3 / 'emotion2vec_base_meanstd.npz', allow_pickle=False)
    assert z['X'].shape == (1035, 1536) and np.isfinite(z['X']).all()
    assert len(set(z['Id'])) == 1035 and set(z['Id']) == set(dm.Id)
    index = {int(v): i for i, v in enumerate(z['Id'])}
    xa = z['X'][[index[int(i)] for i in train.Id]]
    feat = pd.read_csv(ROOT / 'work/mission_inputs/ACOUSTIC_FEATURES_FULL.csv').set_index('Id')
    columns = json.loads((RUN / 'ACOUSTIC_PROBABILITY_PARITY.json').read_text())['acoustic_columns']
    basic = ['duration_seconds', 'amplitude_peak_fullscale', 'rms_fullscale',
             'dc_offset_fullscale', 'crest_factor', 'clip_fraction', 'silence_fraction',
             'leading_silence_seconds', 'trailing_silence_seconds', 'pause_count',
             'pause_fraction_frames', 'zcr_mean', 'spectral_centroid_mean',
             'spectral_bandwidth_mean', 'spectral_rolloff85_mean', 'spectral_flatness_mean',
             'onset_strength_mean', 'f0_yin_median', 'f0_yin_std']
    derived = [c for c in feat if (c in basic or c.startswith(('mfcc', 'dmfcc', 'logmel')))
               and pd.api.types.is_numeric_dtype(feat[c])]
    assert columns == derived
    xb = feat.loc[train.Id, columns].replace([np.inf, -np.inf], np.nan).to_numpy()
    return train, sample, xa, xb, feat, columns, {
        'hashes': {str(p.relative_to(ROOT)): h for p, h in checks.items()},
        'locked_system_file_sha256': sha(RUN / 'FINAL_SYSTEM_LOCK.json'),
        'sample_source': str(SOURCE_ZIP) + ':SRCASW-BhavVaani/sample_submission.csv',
        'sample_submission_sha256': SAMPLE_HASH,
        'sample_submission_schema': sample.columns.tolist(),
        'sample_submission_209_ids_and_original_test_order': 'PASS',
        'train_original_id_filename_label_parity': 'PASS',
    }


def verify():
    assert not RESULT.exists() and not (WORK / 'PROTECTED_ACCESS.json').exists()
    train, _, _, xb, _, columns, info = inputs()
    legacy = pd.read_csv(DS / 'VALIDATION_OOF_FIXED.csv')
    authority = json.loads((DS / 'VALIDATION_STABILITY_RESULTS.json').read_text())
    parity = {}
    for view in ['VA', 'VB']:
        f = pd.read_csv(DS / f'VALIDATION_{view}_FOLDS.csv').sort_values('Id').reset_index(drop=True)
        assert np.array_equal(f.Id, train.Id) and np.array_equal(f.emotion, train.emotion)
        y, fs = f.emotion.to_numpy(), f.fold.to_numpy()
        pred = np.empty(826, dtype=object)
        for k in range(5):
            tr, vl = fs != k, fs == k
            m = reference().fit(xb[tr], y[tr])
            pred[vl] = m.predict(xb[vl])
        old = legacy[(legacy.model == 'FULL_RBF_SVM') & (legacy.validation == view)]
        old = old.set_index('Id').loc[f.Id]
        mismatches = int(np.sum(pred != old.ser_pred.to_numpy()))
        assert mismatches == 0, f'Historical {view} reference mismatch: {mismatches}'
        r = metrics(y, pred, fs)
        expected = next(r for r in authority if r['model'] == 'FULL_RBF_SVM'
                        and r['validation'] == view and r['seed'] == 20260930)
        assert r['aggregate_macro_f1'] == expected['ser_macro_f1']
        assert r['fold_macro_f1'] == expected['fold_ser_macro_f1']
        # The canonical summary has no confusion field; its archived hard OOF
        # labels are the exact authority for that diagnostic.
        assert r['confusion_matrix'] == confusion_matrix(y, old.ser_pred, labels=CLASSES).tolist()
        parity[view] = {'hard_label_mismatches': mismatches, **r}
    info.update({'status': 'PASS', 'starting_sha': START, 'verified_head': git('rev-parse', 'HEAD'),
                 'working_tree': git('status', '--short'), 'reference_ordinary_parity': parity,
                 'acoustic_columns': columns, 'script_sha256': sha(Path(__file__)),
                 'sklearn_version': sklearn.__version__, 'protected_assignments_parsed': False})
    dump(WORK / 'PREFLIGHT.json', info)
    print(json.dumps({'preflight': 'PASS', 'reference': parity}, indent=2), flush=True)


def evaluate():
    assert not RESULT.exists(), 'Protected results already exist; do not rerun.'
    preflight = json.loads((WORK / 'PREFLIGHT.json').read_text())
    assert preflight['status'] == 'PASS' and preflight['script_sha256'] == sha(Path(__file__))
    train, _, xa, xb, _, _, info = inputs()
    assert info['hashes'] == preflight['hashes']
    note_rel = str(NOTE.relative_to(ROOT))
    note_commit = git('log', '-1', '--format=%H', '--', note_rel)
    assert subprocess.check_output(['git', 'show', f'{note_commit}:{note_rel}'], cwd=ROOT) == NOTE.read_bytes()
    assert 'IF protected aggregate macro-F1(A) > protected aggregate macro-F1(B):' in NOTE.read_text()
    with (WORK / 'PROTECTED_ACCESS.json').open('x') as f:
        json.dump({'status': 'STARTED_ONCE', 'precommit_sha': note_commit,
                   'execution_sha': git('rev-parse', 'HEAD'), 'authorized_models': ['A', 'B']}, f)
    # This is the sole protected-assignment parse in the executor.
    t = time.monotonic()
    vp = pd.read_csv(DS / 'VALIDATION_VP_PROTECTED_FOLDS.csv', dtype={'duplicate_group': str})
    vp = vp.sort_values('Id').reset_index(drop=True)
    assert vp.Id.is_unique and len(vp) == 826
    assert np.array_equal(vp.Id, train.Id) and np.array_equal(vp.emotion, train.emotion)
    assert set(vp.fold) == set(range(5)) and vp.groupby('duplicate_group').fold.nunique().max() == 1
    y, fs = vp.emotion.to_numpy(), vp.fold.to_numpy()
    pa = np.full((826, 4), np.nan)
    sa = np.empty(826, dtype=object)
    sb = np.empty(826, dtype=object)
    scores = np.full((826, 4), np.nan)
    for k in range(5):
        tr, vl = fs != k, fs == k
        a = finalist().fit(xa[tr], y[tr])
        b = reference().fit(xb[tr], y[tr])
        assert np.array_equal(a.classes_, CLASSES) and np.array_equal(b.classes_, CLASSES)
        pa[vl] = a.predict_proba(xa[vl])
        sa[vl] = CLASSES[pa[vl].argmax(axis=1)]
        sb[vl] = b.predict(xb[vl])
        scores[vl] = b.decision_function(xb[vl])
        print(f'PROTECTED_FOLD_{k}=COMPLETE_A_AND_B', flush=True)
    assert np.isfinite(pa).all() and np.isfinite(scores).all()
    assert np.allclose(pa.sum(axis=1), 1, atol=1e-12) and (pa >= 0).all()
    oof = vp[['Id', 'emotion', 'fold']].copy()
    oof['A_pred'], oof['B_pred'] = sa, sb
    for j, c in enumerate(CLASSES):
        oof[f'A_probability_{c}'] = pa[:, j]
        oof[f'B_decision_score_{c}'] = scores[:, j]
    oof_path = RUN / 'PROTECTED_CONFIRMATION_OOF.csv'
    oof.to_csv(oof_path, index=False, lineterminator='\n')
    ra, rb = metrics(y, sa, fs), metrics(y, sb, fs)
    decision = 'CONFIRM_FINALIST' if ra['aggregate_macro_f1'] > rb['aggregate_macro_f1'] else 'USE_FROZEN_REFERENCE'
    result = {'status': 'PROTECTED_CONFIRMATION_COMPLETE_SUBMISSION_PENDING',
              'starting_sha': START, 'decision_rule_precommit_sha': note_commit,
              'execution_sha': git('rev-parse', 'HEAD'), 'protected_fold_sha256': VP_HASH,
              'protected_evaluation_count': 1, 'preflight': preflight,
              'system_A': ra, 'system_B': rb, 'decision': decision,
              'selected_system': 'emotion2vec_base_L2_LOGREG' if decision == 'CONFIRM_FINALIST' else 'FULL_RBF_SVM',
              'protected_oof_sha256': sha(oof_path), 'protected_oof_path': str(oof_path),
              'B_probability_note': 'Historical SVC probability=False; preserve ordinary labels and OVR decision scores, not a new calibration.',
              'protected_wall_seconds': time.monotonic() - t, 'accelerator_hours': 0,
              'retuning_after_protected': False, 'public_lb_used_for_selection': False,
              'kaggle_submission_made': False}
    dump(RESULT, result)
    dump(WORK / 'PROTECTED_ACCESS.json', {'status': 'COMPLETED_ONCE', 'result_sha256': sha(RESULT)})
    print(json.dumps({'A': ra, 'B': rb, 'decision': decision}, indent=2), flush=True)


def prepare():
    result = json.loads(RESULT.read_text())
    assert result['status'] == 'PROTECTED_CONFIRMATION_COMPLETE_SUBMISSION_PENDING'
    train, sample, _, xb, feat, columns, _ = inputs()
    assert result['decision'] == ('CONFIRM_FINALIST' if result['system_A']['aggregate_macro_f1'] >
                                 result['system_B']['aggregate_macro_f1'] else 'USE_FROZEN_REFERENCE')
    if result['decision'] == 'CONFIRM_FINALIST':
        archived = pd.read_csv(OUT / 'LOCKED_FINALIST_TEST_INFERENCE.csv').set_index('Id').loc[sample.Id]
        prob = archived[[f'p_{c}' for c in CLASSES]].to_numpy()
        assert np.isfinite(prob).all() and np.allclose(prob.sum(axis=1), 1)
        assert np.array_equal(archived.ser_pred, CLASSES[prob.argmax(axis=1)])
        raw = archived.ser_pred.to_numpy().copy()
        inference = 'REUSED_HASH_VERIFIED_ALL826_LOCKED_FINALIST_ARCHIVED_TEST_INFERENCE'
    else:
        model = reference().fit(xb, train.emotion.to_numpy())
        xt = feat.loc[sample.Id, columns].replace([np.inf, -np.inf], np.nan).to_numpy()
        raw = model.predict(xt)
        inference = 'EXACT_HISTORICAL_REFERENCE_FIT_ALL826_ONCE'
    final = raw.copy()
    ret = pd.read_csv(DS / 'RETRIEVAL_MAP_FINAL.csv')
    assert len(ret) == 78 and ret.test_Id.is_unique and not ret.conflict.any()
    positions = {int(v): i for i, v in enumerate(sample.Id)}
    labels = train.set_index('Id').emotion.to_dict()
    covered = np.zeros(209, dtype=bool)
    for r in ret.itertuples(index=False):
        matches = [int(v) for v in str(r.matched_train_Ids).replace(';', ',').split(',')]
        assert matches and all(labels[i] == r.consensus_emotion for i in matches)
        i = positions[int(r.test_Id)]
        final[i], covered[i] = r.consensus_emotion, True
    assert covered.sum() == 78
    if result['decision'] == 'CONFIRM_FINALIST':
        assert np.array_equal(final, archived.final_pred)
        assert np.array_equal(covered, archived.certified_retrieval_covered)
    submission = pd.DataFrame({'Id': sample.Id.to_numpy(), 'emotion': final})
    path = RUN / 'submission.csv'
    assert not path.exists(), 'Submission already exists; inspect rather than overwrite.'
    submission.to_csv(path, index=False, lineterminator='\n')
    checked = pd.read_csv(path)
    assert checked.columns.tolist() == ['Id', 'emotion'] and len(checked) == 209
    assert checked.Id.is_unique and np.array_equal(checked.Id, sample.Id)
    assert set(checked.Id) == set(sample.Id) and set(checked.emotion) <= set(CLASSES)
    assert not checked.isna().any().any() and not checked.astype(str).eq('').any().any()
    assert path.read_text().splitlines()[0] == 'Id,emotion'
    result.update({'status': 'READY_FOR_SUBMISSION', 'selected_test_inference': inference,
                   'submission_path': str(path), 'submission_sha256': sha(path),
                   'submission_class_counts': {c: int(np.sum(final == c)) for c in CLASSES},
                   'retrieval_override_count': int(covered.sum()),
                   'retrieval_changed_label_count': int(np.sum(final != raw)),
                   'sample_submission_parity': 'PASS', 'submission_rows': 209,
                   'submission_schema': ['Id', 'emotion'], 'next': 'READY_FOR_SUBMISSION'})
    dump(RESULT, result)
    print(json.dumps({k: v for k, v in result.items() if k not in ['preflight', 'system_A', 'system_B']}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['verify', 'evaluate', 'prepare'])
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    warnings.simplefilter('error', ConvergenceWarning)
    with threadpool_limits(limits=2):
        {'verify': verify, 'evaluate': evaluate, 'prepare': prepare}[args.mode]()


if __name__ == '__main__':
    main()
