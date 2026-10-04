#!/usr/bin/env python3
"""Audit cached evidence and populate TARGET209. No fit/encoder/protected/submission calls."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import platform
import subprocess
import zipfile
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import confusion_matrix, f1_score
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
MISSION = 'SS-DEFHS-TARGET209-EMPIRICAL-RESET-001'
RUN = ROOT / 'runs' / MISSION
DS = 'runs/DS-DEFHS-VALIDATION-HARDENING-002'
IMPL = 'runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001'
W1 = 'runs/RS-DEFHS-SYSTEM3-WAVE1-001'
SEM = 'runs/RS-DEFHS-SCORE-PUSH-001'
CLASSES = ['angry', 'happy', 'neutral', 'sad']
START = '8ba35644934a7b71cd557be65b9a2ca6b643fbf6'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(path):
    assert 'PROTECTED' not in str(path).upper() and 'VALIDATION_VP' not in str(path).upper(), path
    return Path(path)


def json_read(path):
    return json.loads(safe_path(path).read_text())


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def compact(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def validate_prob(p, rows):
    assert p.shape == (rows, 4) and np.isfinite(p).all()
    assert p.min() >= -1e-12 and p.max() <= 1 + 1e-12
    assert np.allclose(p.sum(axis=1), 1, atol=1e-7, rtol=0)


def confidences(p):
    q = np.sort(p, axis=1)
    return q[:, -1], q[:, -1] - q[:, -2]


def labels(p):
    return np.asarray(CLASSES)[np.argmax(p, axis=1)]


def metrics(y, p, folds):
    pred = labels(p)
    return {'macro_f1': float(f1_score(y, pred, labels=CLASSES, average='macro')),
            'per_class_f1': dict(zip(CLASSES, f1_score(y, pred, labels=CLASSES, average=None).tolist())),
            'confusion': confusion_matrix(y, pred, labels=CLASSES).tolist(),
            'fold_macro_f1': [float(f1_score(y[folds == k], pred[folds == k], labels=CLASSES, average='macro')) for k in range(5)]}


def nearest(x, test_indices, train_indices, train_ids, train_labels, metadata):
    x = x.astype(np.float64)
    norm = np.linalg.norm(x, axis=1, keepdims=True)
    assert np.all(norm > 0)
    unit = x / norm
    sim = unit[test_indices] @ unit[train_indices].T
    out = []
    for row in sim:
        order = np.lexsort((train_ids, -row))[:5]
        out.append([{'Id': int(train_ids[k]), 'label': str(train_labels[k]),
                     'filename': metadata.loc[int(train_ids[k]), 'filename'],
                     'cosine': float(row[k])} for k in order])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-root', type=Path, required=True)
    ap.add_argument('--competition-zip', type=Path, required=True)
    a = ap.parse_args()
    source = a.source_root.resolve()
    protocol = json_read(RUN / 'ANALYSIS_PROTOCOL.json')
    assert protocol['start_head'] == START
    inventory = {'mission': MISSION, 'start_head': START, 'runtime': {
        'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__,
        'scikit_learn': sklearn.__version__, 'joblib': joblib.__version__, 'BLAS_threads': 2},
        'artifacts': {}, 'derived_artifacts': {}, 'missing_evidence': []}
    inventory['derivation_source'] = {
        'script': 'scripts/build_target209_evidence.py', 'script_sha256': sha(Path(__file__).read_bytes()),
        'protocol_sha256': sha((RUN / 'ANALYSIS_PROTOCOL.json').read_bytes())}

    def register(name, path, expected, authority, role):
        p = safe_path(path)
        actual = sha(p.read_bytes())
        assert actual == expected, (name, actual, expected)
        inventory['artifacts'][name] = {'path': str(p), 'sha256': actual,
                                       'bytes': p.stat().st_size, 'authority': authority, 'role': role}
        return p

    raw_manifest = json_read(ROOT / 'manifests/DEFHS_COMPETITION_DATA_20260930.json')
    zpath = register('competition_zip', a.competition_zip, raw_manifest['sha256'],
                     'manifests/DEFHS_COMPETITION_DATA_20260930.json', 'Exact raw competition identity; read only')
    canonical = {r['artifact']: r['sha256'] for r in json_read(ROOT / DS / 'CANONICAL_ARTIFACT_INVENTORY.json')}
    for name in ['DATA_MANIFEST.csv', 'VALIDATION_VB_FOLDS.csv', 'DUPLICATE_GROUPS_FINAL.csv', 'RETRIEVAL_MAP_FINAL.csv']:
        register(name, ROOT / DS / name, canonical[name], DS + '/CANONICAL_ARTIFACT_INVENTORY.json', 'Frozen ordinary data/validation authority')
    dm = pd.read_csv(ROOT / DS / 'DATA_MANIFEST.csv').set_index('Id')
    folds = pd.read_csv(ROOT / DS / 'VALIDATION_VB_FOLDS.csv').sort_values('Id')
    ret = pd.read_csv(ROOT / DS / 'RETRIEVAL_MAP_FINAL.csv')
    duplicates = pd.read_csv(ROOT / DS / 'DUPLICATE_GROUPS_FINAL.csv')
    pair_rel = 'runs/DS-DEFHS-DATA-VALIDATION-FOUNDATION-001/DUPLICATE_PAIR_EVIDENCE.csv'
    pair_original = subprocess.check_output(['git', 'show', START + ':' + pair_rel], cwd=ROOT)
    pair_path = register('recorded_waveform_pair_evidence', ROOT / pair_rel, sha(pair_original),
                         'Git blob at ' + START + ':' + pair_rel, 'Existing normalized full-waveform cosine comparisons restricted to equal native sample length; not all pairs are duplicates')
    waveform_pairs = pd.read_csv(pair_path)
    with zipfile.ZipFile(zpath) as z:
        original_sample = z.read('SRCASW-BhavVaani/sample_submission.csv')
        original_test = z.read('SRCASW-BhavVaani/test.csv')
        original_train = z.read('SRCASW-BhavVaani/train.csv')
        sample = pd.read_csv(io.BytesIO(original_sample))
        test_csv = pd.read_csv(io.BytesIO(original_test)).set_index('Id')
        train_csv = pd.read_csv(io.BytesIO(original_train)).set_index('Id')
        assert list(sample) == ['Id', 'emotion'] and len(sample) == 209 and sample.Id.is_unique
        test_ids = sample.Id.to_numpy()
        assert set(test_ids) == set(test_csv.index) == set(dm[dm.split == 'test'].index)
        assert np.array_equal(test_csv.loc[test_ids].filename, dm.loc[test_ids].filename)
        assert len(train_csv) == 826 and set(train_csv.index) == set(folds.Id)
        assert np.array_equal(train_csv.loc[folds.Id].emotion, folds.emotion)
        wav_by_name = {Path(n).name: n for n in z.namelist() if n.endswith('.wav')}
        for ident in test_ids:
            name = dm.loc[ident, 'filename']
            assert sha(z.read(wav_by_name[name])) == dm.loc[ident, 'file_sha256']
    inventory['original_sample'] = {'zip_member': 'SRCASW-BhavVaani/sample_submission.csv',
                                    'sha256': sha(original_sample), 'rows': 209, 'schema': list(sample)}
    inventory['original_test'] = {'zip_member': 'SRCASW-BhavVaani/test.csv', 'sha256': sha(original_test),
                                  'all_209_recorded_WAV_hashes_verified_against_zip': True}
    assert folds.duplicate_group.groupby(folds.duplicate_group).size().sum() == 826
    assert folds.groupby('duplicate_group').fold.nunique().max() == 1
    assert len(ret) == 78 and ret.test_Id.is_unique and ret.duplicate_group.nunique() == 77
    assert not ret.conflict.astype(bool).any()
    ret_by_id = ret.set_index('test_Id')
    train_labels = folds.set_index('Id').emotion
    recorded_pairs = {int(i): [] for i in test_ids}
    for p in waveform_pairs.itertuples():
        if {p.split_a, p.split_b} != {'train', 'test'}:
            continue
        tid = int(p.Id_a if p.split_a == 'test' else p.Id_b)
        trid = int(p.Id_b if p.split_a == 'test' else p.Id_a)
        assert tid in recorded_pairs and trid in train_labels.index
        recorded_pairs[tid].append({'train_Id': trid, 'train_label': str(train_labels.loc[trid]),
                                    'full_waveform_cosine': float(p.similarity), 'native_samples': int(p.samples)})
    for row in ret.itertuples():
        ids = [int(v) for v in str(row.matched_train_Ids).replace(';', ',').split(',')]
        assert all(train_labels.loc[i] == row.consensus_emotion for i in ids)

    lock = json_read(ROOT / IMPL / 'FINAL_SYSTEM_LOCK.json')
    parent_path = register('accepted_TEST_INFERENCE', source / 'work/frozen_closure/LOCKED_FINALIST_TEST_INFERENCE.csv',
                           lock['test_inference_sha256'], IMPL + '/FINAL_SYSTEM_LOCK.json', 'Imported existing 209-row probabilities and raw/final predictions')
    current = pd.read_csv(parent_path).set_index('Id').loc[test_ids]
    pc = current[['p_' + c for c in CLASSES]].to_numpy()
    validate_prob(pc, 209)
    assert np.array_equal(labels(pc), current.ser_pred)
    covered = np.isin(test_ids, ret.test_Id)
    current_final = current.final_pred.to_numpy()
    assert np.array_equal(covered, current.certified_retrieval_covered.astype(bool))
    assert np.array_equal(current_final[~covered], labels(pc)[~covered])
    assert np.array_equal(current_final[covered], ret_by_id.loc[test_ids[covered]].consensus_emotion)
    accepted_submission = pd.read_csv(ROOT / IMPL / 'submission.csv')
    assert np.array_equal(accepted_submission.Id, test_ids) and np.array_equal(accepted_submission.emotion, current_final)
    inventory['artifacts']['accepted_submission'] = {
        'path': IMPL + '/submission.csv', 'sha256': sha((ROOT / IMPL / 'submission.csv').read_bytes()),
        'role': 'Existing current System1 final predictions; no protected confirmation content read'}

    preflight = json_read(ROOT / W1 / 'W1_PREFLIGHT.json')
    cpu_inventory = json_read(ROOT / W1 / 'PROBABILITY_ARTIFACT_INVENTORY.json')
    inventory['Wave1_head_producer'] = {
        'script': 'scripts/system3_wave1_cpu.py',
        'producer_git_commit': json_read(ROOT / W1 / 'W1_CPU_PAIR_RESULTS.json')['source_sha'],
        'ordinary_fold_authority': canonical['VALIDATION_VB_FOLDS.csv']}
    cpu_manifest = register('CPU_SHA256SUMS', source / 'work/system3_wave1/CPU_SHA256SUMS.txt',
                            cpu_inventory['CPU_preservation']['manifest_sha256'], W1 + '/PROBABILITY_ARTIFACT_INVENTORY.json', 'Existing frozen fitted-head and OOF hash authority')
    hashes = {line.split()[1]: line.split()[0] for line in cpu_manifest.read_text().splitlines() if line.strip()}
    ordinary = {row['name']: row for row in cpu_inventory['artifacts']}
    cache_base = source / '.tmp/rs_system_implementation_001_frozen_screen_v3/rs_defhs_system_implementation_001'
    representations = {}
    predictions = {}
    cv_heads = {}
    train_ids = folds.Id.to_numpy()
    train_y = folds.emotion.to_numpy()
    fold_numbers = folds.fold.to_numpy()
    with threadpool_limits(limits=2):
        for name, alias in [('emotion2vec_base', 'e2v'), ('xls_r_300m', 'xlsr')]:
            cache_name = name + '_meanstd.npz'
            path = register(cache_name, cache_base / cache_name, preflight['inputs'][cache_name]['sha256'],
                            W1 + '/W1_PREFLIGHT.json', 'Existing all-1035 raw cached mean+std features; no encoder run')
            z = np.load(path, allow_pickle=False)
            assert np.array_equal(z['Id'], dm.index) and np.isfinite(z['X']).all()
            positions = {int(v): k for k, v in enumerate(z['Id'])}
            train_idx = np.array([positions[int(i)] for i in train_ids])
            test_idx = np.array([positions[int(i)] for i in test_ids])
            representations[alias] = (z['X'], train_idx, test_idx)
            test_heads = []
            oof = np.zeros((826, 4))
            for k in range(5):
                filename = f'{name}_VB_outer{k}.joblib'
                hpath = register(filename, source / 'work/system3_wave1' / filename, hashes[filename],
                                 'CPU_SHA256SUMS', 'Existing ordinary PRIMARY_CV outer fitted head; no fitting')
                model = joblib.load(hpath)
                assert np.array_equal(model.classes_, CLASSES)
                assert int(model[0].n_samples_seen_) == int(np.sum(fold_numbers != k))
                test_heads.append(model.predict_proba(z['X'][test_idx]))
                held = fold_numbers == k
                oof[held] = model.predict_proba(z['X'][train_idx[held]])
            cv_heads[alias] = oof
            predictions[alias] = np.stack(test_heads)
            validate_prob(predictions[alias].mean(axis=0), 209)
            n = 'E2V_CONTROL_VB.npz' if alias == 'e2v' else 'XLSR_VB.npz'
            ppath = register(n, source / 'work/system3_wave1' / n, ordinary[n]['sha256'],
                             W1 + '/PROBABILITY_ARTIFACT_INVENTORY.json', 'Existing ordinary training OOF; never treated as test predictions')
            old = np.load(ppath, allow_pickle=False)
            assert np.array_equal(old['Id'], train_ids)
            delta = float(np.max(np.abs(oof - old['prob'])))
            assert delta < 1e-10, (n, delta)
            inventory['artifacts'][n]['independent_saved_head_probability_parity_max_abs'] = delta
    pe = predictions['e2v'].mean(axis=0)
    px = predictions['xlsr'].mean(axis=0)
    pp = (pe + px) * 0.5
    validate_prob(pp, 209)
    pair_cv = (cv_heads['e2v'] + cv_heads['xlsr']) * 0.5
    pp_oof_path = register('FIXED_PAIR_VB.npz', source / 'work/system3_wave1/FIXED_PAIR_VB.npz',
                           ordinary['FIXED_PAIR_VB.npz']['sha256'], W1 + '/PROBABILITY_ARTIFACT_INVENTORY.json', 'Original pair PRIMARY_CV probabilities')
    archived_pair = np.load(pp_oof_path, allow_pickle=False)
    assert np.array_equal(archived_pair['Id'], train_ids)
    assert np.max(np.abs(pair_cv - archived_pair['prob'])) < 1e-10
    raw_pair_label = labels(pp)
    pair_final = raw_pair_label.copy()
    pair_final[covered] = ret_by_id.loc[test_ids[covered]].consensus_emotion
    ce, me = confidences(pe)
    cx, mx = confidences(px)
    cp, mp = confidences(pp)
    cc, mc = confidences(pc)
    e_label, x_label, c_label = labels(pe), labels(px), labels(pc)
    head_labels = {n: np.argmax(q, axis=2) for n, q in predictions.items()}
    vote_fractions = {n: np.array([np.bincount(v[:, k], minlength=4).max() / 5 for k in range(209)]) for n, v in head_labels.items()}
    with threadpool_limits(limits=2):
        neighbors = {n: nearest(x, test_idx, tr_idx, train_ids, train_y, dm)
                     for n, (x, tr_idx, test_idx) in representations.items()}

    closure = pd.read_csv(ROOT / DS / 'CLOSURE_COMPLETED_ARTIFACT_MANIFEST.tsv', sep='\t')
    def closure_file(name, folder):
        record = closure[closure.drive_path.str.endswith('/' + name)]
        assert len(record) == 1
        row = record.iloc[0]
        path = register(name, source / 'work/mission_inputs' / folder / name, row.sha256,
                        DS + '/CLOSURE_COMPLETED_ARTIFACT_MANIFEST.tsv', 'Existing auxiliary evidence; no model execution')
        inventory['artifacts'][name].update({'drive_path': row.drive_path, 'drive_file_id': row.drive_file_id,
                                            'producer_commit': row.producer_git_commit, 'model_revision': row.model_or_runtime_revision})
        return pd.read_csv(path).set_index('Id')
    asr_all = closure_file('ASR_TRANSCRIPTS.csv', 'asr_transcripts')
    asr = asr_all.loc[test_ids]
    speaker = closure_file('SPEAKER_CLUSTER_ASSIGNMENTS.csv', 'speaker_embeddings')
    sem_inventory = {f['name']: f for f in json_read(ROOT / SEM / 'SEMANTIC_INFERENCE_MANIFEST.json')['files']}
    sem_root = source / '.tmp/rs_score_push_001_semantic_v1/rs_defhs_score_push_001_semantic'
    for name in ['QWEN_SEMANTIC_OUTPUTS.csv', 'EXECUTION_PROVENANCE.json', 'CHECKPOINT.json', 'QWEN_FIXED_PROMPT.txt', 'UNIQUE_TRANSCRIPT_OUTPUTS.jsonl']:
        register(name, sem_root / name, sem_inventory[name]['sha256'], SEM + '/SEMANTIC_INFERENCE_MANIFEST.json', 'Existing semantic hard-label evidence; no probability vectors')
    semantic_all = pd.read_csv(sem_root / 'QWEN_SEMANTIC_OUTPUTS.csv').set_index('Id')
    assert set(semantic_all.index) == set(dm.index)
    semantic = semantic_all.loc[test_ids].semantic_label
    semantic_provenance = json_read(sem_root / 'EXECUTION_PROVENANCE.json')
    inventory['semantic_recipe'] = semantic_provenance
    assert semantic_provenance['protected_validation_accessed'] is False
    journal = {r['transcript']: r['label'] for r in
               (json.loads(line) for line in (sem_root / 'UNIQUE_TRANSCRIPT_OUTPUTS.jsonl').read_text().splitlines())}
    for ident in test_ids:
        text = asr_all.loc[ident, 'transcript']
        text = '' if pd.isna(text) else str(text)
        assert journal[text] == semantic.loc[ident]
    inventory['Qwen_test_transcript_label_journal_parity'] = True
    semantic_records = asr_all.reset_index()[['Id', 'transcript']].fillna('').sort_values('Id').to_dict('records')
    assert sha(compact(semantic_records).encode()) == semantic_provenance['input_payload_sha256']
    inventory['Qwen_original_input_payload_SHA256_parity'] = True

    ast_cv = {}
    for n in ['B0_VB_seed20260930.npz', 'B1_SEED_MEAN_VB.npz']:
        path = register(n, source / 'work/system3_wave1' / n, ordinary[n]['sha256'],
                        W1 + '/PROBABILITY_ARTIFACT_INVENTORY.json', 'AST training OOF only; test probabilities unavailable')
        z = np.load(path, allow_pickle=False)
        assert np.array_equal(z['Id'], train_ids)
        ast_cv[n] = z['prob']
    inventory['missing_evidence'] = [
        {'family': 'AST test probabilities', 'reason': 'Registered B0/B1 probability artifacts contain 826 training IDs only; inspected frozen AST caches contain zero TARGET209 IDs. No AST encoder inference performed.'},
        {'family': 'all-826 XLS-R refit', 'reason': 'No verified saved all-826 XLS-R head/test artifact located. Candidate explicitly uses existing PRIMARY_CV fold heads rather than pretending an all-826 fit exists.'},
        {'family': 'semantic probabilities', 'reason': 'Verified Qwen artifact contains semantic_label including unclear, with greedy label decoding; no four-class score vector.'},
        {'family': 'test optimization-seed stability', 'reason': 'Available AST seed results are training OOF only. Waveform fold-head variation is reported separately and is not seed replication.'},
        {'family': 'speaker/session/source ground truth', 'reason': 'Metadata and ECAPA co-clusters provide auxiliary hints, not independently verified speaker IDs or hidden domain membership.'}]
    adapted_name = 'A1_VB_SHARED_INIT_CORRECTED.npz'
    apath = register(adapted_name, source / 'work/system3_wave1' / adapted_name, ordinary[adapted_name]['sha256'],
                     W1 + '/PROBABILITY_ARTIFACT_INVENTORY.json', 'Wave1 adaptation OOF only; not a TARGET209 probability artifact')
    assert not (set(np.load(apath, allow_pickle=False)['Id']) & set(test_ids))
    inventory['missing_evidence'].append({'family': 'Wave1 adapted emotion2vec test probabilities',
                                          'reason': 'The verified A1 corrected probability archive contains training OOF IDs only. wave1_e2v columns identify the original frozen E2V head mean, not adapted encoder inference.'})

    category = np.full(209, 'MEDIUM_CONFIDENCE', dtype=object)
    stable = (vote_fractions['e2v'] >= .8) & (vote_fractions['xlsr'] >= .8)
    agreement = (c_label == raw_pair_label) & (e_label == x_label) & (e_label == raw_pair_label)
    hard = (~covered) & ((cc < .60) | (cp < .60) | (mc < .20) | (mp < .20) | (~agreement) | (~stable))
    high = covered | ((~covered) & agreement & stable & (cc >= .80) & (cp >= .80) & (mc >= .50) & (mp >= .50))
    category[hard] = 'HARD'
    category[high] = 'HIGH_CONFIDENCE'
    assert not np.any(hard & high)
    existing = pd.read_csv(ROOT / 'docs/TEST209_PREDICTION_MATRIX.csv', keep_default_na=False).set_index('Id')
    assert set(existing.index) == set(test_ids)
    rows = []
    all_pairs = []
    for k, ident in enumerate(test_ids):
        ident = int(ident)
        row = existing.loc[ident].to_dict()
        row['Id'] = ident
        for prefix, prob in [('waveform', pc), ('ensemble', pp), ('wave1_e2v', pe), ('wave1_xlsr', px), ('fixed_pair_cv5', pp)]:
            for j, c in enumerate(CLASSES):
                row[prefix + '_p_' + c] = float(prob[k, j])
        sem = str(semantic.loc[ident])
        transcript = '' if pd.isna(asr.loc[ident, 'transcript']) else str(asr.loc[ident, 'transcript'])
        flags = []
        ar = asr.loc[ident]
        if not transcript.strip(): flags.append('EMPTY_TRANSCRIPT')
        if ar.detected_language != 'hi': flags.append('LANGUAGE_NOT_HI')
        for field, op, threshold, flag in [
            ('language_probability', 'lt', .8, 'LOW_LANGUAGE_CONFIDENCE'),
            ('avg_logprob', 'lt', -1., 'LOW_ASR_LOGPROB'),
            ('no_speech_prob', 'gt', .5, 'HIGH_NO_SPEECH'),
            ('compression_ratio', 'gt', 2.4, 'HIGH_COMPRESSION')]:
            if pd.notna(ar[field]) and ((float(ar[field]) < threshold) if op == 'lt' else (float(ar[field]) > threshold)):
                flags.append(flag)
        top = np.argsort(-pp[k], kind='stable')[:2]
        ambiguity = '↔'.join(CLASSES[j] for j in sorted(top))
        observed = {c_label[k], e_label[k], x_label[k], raw_pair_label[k]}
        semantic_disagrees = sem in CLASSES and sem != current_final[k]
        if covered[k]: mechanism = 'CERTIFIED_RETRIEVAL_SUPPORT'
        elif ({'neutral', 'sad'} <= observed and not agreement[k]) or (set(top) == {2, 3} and mp[k] < .2): mechanism = 'NEUTRAL_SAD_ACOUSTIC_BOUNDARY'
        elif not agreement[k]: mechanism = 'WAVEFORM_MODEL_DISAGREEMENT'
        elif not stable[k]: mechanism = 'FOLD_HEAD_INSTABILITY'
        elif mc[k] < .2 or mp[k] < .2 or cc[k] < .6 or cp[k] < .6: mechanism = 'LOW_CONFIDENCE_ACOUSTIC_BOUNDARY'
        elif flags: mechanism = 'ASR_QUALITY_LIMITATION'
        elif semantic_disagrees: mechanism = 'LEXICAL_VOCAL_DISAGREEMENT'
        else: mechanism = 'MISSING_INDEPENDENT_MODAL_CONFIRMATION'
        if covered[k]:
            r = ret_by_id.loc[ident]
            matched = [int(v) for v in str(r.matched_train_Ids).replace(';', ',').split(',')]
            duplicate = {'certified': True, 'duplicate_group': int(r.duplicate_group),
                         'matched_train_Ids': matched, 'labels': [str(train_labels.loc[i]) for i in matched],
                         'consensus': str(r.consensus_emotion), 'threshold': .95, 'map_sha256': canonical['RETRIEVAL_MAP_FINAL.csv']}
        else:
            duplicate = {'certified': False, 'note': 'No membership in the unchanged certified map; this is not proof of absence of near duplicates'}
        comparisons = sorted(recorded_pairs[ident], key=lambda r: (-r['full_waveform_cosine'], r['train_Id']))
        duplicate['recorded_equal_length_waveform_pairs'] = comparisons[:3]
        duplicate['recorded_equal_length_waveform_pair_count'] = len(comparisons)
        duplicate['recorded_pair_metric'] = 'Normalized full-waveform cosine restricted to equal native sample length; no new certification or threshold search'
        sp = {}
        for field in ['agg_d0.10', 'agg_d0.15']:
            cluster = int(speaker.loc[ident, field])
            matches = speaker[(speaker[field] == cluster) & speaker.index.isin(train_ids)].index.to_list()
            sp[field] = {'cluster': cluster, 'train_Ids': [int(i) for i in matches],
                         'interpretation': 'Existing ECAPA co-clustering only; no verified speaker identity or continuous similarity score'}
        near = neighbors['e2v'][k]
        same_dtype = sum(dm.loc[n['Id'], 'dtype'] == dm.loc[ident, 'dtype'] for n in near)
        disagreement = {'current_SER': str(c_label[k]), 'current_final': str(current_final[k]),
                        'e2v_cv5': str(e_label[k]), 'xlsr_cv5': str(x_label[k]),
                        'pair_cv5_SER': str(raw_pair_label[k]), 'pair_cv5_final': str(pair_final[k]),
                        'distinct_waveform_SER_classes': len(observed), 'Qwen_lexical_label': sem,
                        'Qwen_abstained': sem == 'unclear', 'Qwen_vs_current_final_disagree': bool(semantic_disagrees),
                        'AST': 'UNAVAILABLE_ON_TEST'}
        stability = {'e2v_fold_head_vote_fraction': float(vote_fractions['e2v'][k]),
                     'xlsr_fold_head_vote_fraction': float(vote_fractions['xlsr'][k]),
                     'e2v_fold_head_predictions': [CLASSES[int(v)] for v in head_labels['e2v'][:, k]],
                     'xlsr_fold_head_predictions': [CLASSES[int(v)] for v in head_labels['xlsr'][:, k]],
                     'optimization_seed_test_stability': 'UNAVAILABLE'}
        notes = [mechanism, 'AST test probabilities and independent seed replication unavailable']
        if sem == 'unclear': notes.append('Qwen abstains on lexical emotion')
        if semantic_disagrees: notes.append('Lexical emotion conflicts with deployed vocal prediction; no test truth available')
        if flags: notes.append('ASR flags: ' + ','.join(flags))
        if current_final[k] != pair_final[k]: notes.append('Prepared fixed CV5 pair changes current System1 prediction; correction vs breakage unknown')
        row.update({
            'predicted_class': str(current_final[k]), 'current_ser_predicted_class': str(c_label[k]),
            'confidence': float(cc[k]), 'margin': float(mc[k]),
            'confidence_probability_source': 'Accepted all-826 raw SER vector; certified override does not imply confidence=1',
            'fixed_pair_ser_predicted_class': str(raw_pair_label[k]), 'fixed_pair_predicted_class': str(pair_final[k]),
            'fixed_pair_confidence': float(cp[k]), 'fixed_pair_margin': float(mp[k]),
            'fixed_pair_changes_System1': bool(current_final[k] != pair_final[k]),
            'model_disagreement': compact(disagreement), 'seed_model_stability': compact(stability),
            'nearest_train_Ids': compact([n['Id'] for n in near]), 'nearest_train_labels': compact([n['label'] for n in near]),
            'nearest_e2v_examples': compact(near), 'nearest_xlsr_examples': compact(neighbors['xlsr'][k]),
            'duplicate_evidence': compact(duplicate), 'certified_retrieval_covered': bool(covered[k]),
            'provenance_evidence': compact({'package': 'SRCASW-BhavVaani supplied competition ZIP', 'WAV_hash_verified': True,
                                           'sample_rate': int(dm.loc[ident, 'sample_rate']), 'samples': int(dm.loc[ident, 'samples']),
                                           'duration_seconds': float(dm.loc[ident, 'duration_seconds']), 'dtype': str(dm.loc[ident, 'dtype']),
                                           'speaker_session_source_ground_truth': 'UNKNOWN'}),
            'source_domain_similarity': compact({'same_dtype_among_top5_e2v_neighbors': same_dtype, 'denominator': 5,
                                                 'interpretation': 'Recording-format match only; not hidden source/domain identity'}),
            'speaker_like_similarity': compact(sp), 'asr_transcript': transcript,
            'asr_quality_flags': compact(flags), 'semantic_label': sem,
            'uncertainty_category': str(category[k]), 'dominant_uncertainty_mechanism': mechanism,
            'ambiguity_pair': ambiguity, 'difficulty_notes': '; '.join(notes),
            'probability_provenance': compact({'accepted': 'accepted_TEST_INFERENCE', 'ensemble': 'FIXED_50_50_PRIMARY_CV5_HEADMEAN_V1',
                                              'wave1_e2v': 'existing_e2v_VB_outer0..4_HEADMEAN', 'wave1_xlsr': 'existing_xlsr_VB_outer0..4_HEADMEAN',
                                              'registry': 'runs/' + MISSION + '/EVIDENCE_PROVENANCE.json'}),
            'model_set': 'System1 all826 + ordinary CV5 E2V/XLS-R fixed mean; Qwen hard labels separate; AST test unavailable',
            'evidence_status': 'VERIFIED_EXISTING_AND_EXPLICIT_CACHED_HEAD_DERIVATIONS'})
        rows.append(row)
        all_pairs.append(ambiguity)
    matrix = pd.DataFrame(rows)
    matrix.to_csv(ROOT / 'docs/TEST209_PREDICTION_MATRIX.csv', index=False, float_format='%.17g')
    candidate = pd.DataFrame({'Id': test_ids, 'emotion': pair_final})
    candidate.to_csv(RUN / 'submission_fixed_pair_cv5.csv', index=False)
    pframe = pd.DataFrame({'Id': test_ids, 'e2v_ser': e_label, 'xlsr_ser': x_label,
                          'pair_ser': raw_pair_label, 'pair_final': pair_final, 'certified_retrieval_covered': covered})
    for prefix, p in [('e2v', pe), ('xlsr', px), ('pair', pp)]:
        for j, c in enumerate(CLASSES): pframe[prefix + '_p_' + c] = p[:, j]
    pframe.to_csv(RUN / 'FIXED_PAIR_TEST_INFERENCE.csv', index=False, float_format='%.17g')

    model_predictions = {'System1_final': current_final, 'System1_SER': c_label, 'E2V_CV5_SER': e_label,
                         'XLSR_CV5_SER': x_label, 'PAIR_CV5_SER': raw_pair_label, 'PAIR_CV5_final': pair_final}
    counts = {n: dict(Counter(map(str, p))) for n, p in model_predictions.items()}
    disagreement = {n: {m: int(np.sum(p != q)) for m, q in model_predictions.items()} for n, p in model_predictions.items()}
    major = {**model_predictions, 'Qwen_lexical': semantic.to_numpy(), 'AST_test': np.full(209, '', dtype=object)}
    major_disagreement = {}
    for name, pred in major.items():
        major_disagreement[name] = {}
        for other, q in major.items():
            valid = np.isin(pred, CLASSES) & np.isin(q, CLASSES)
            n = int(valid.sum())
            d = int(np.sum(pred[valid] != q[valid])) if n else None
            major_disagreement[name][other] = {'disagreement_count': d, 'comparable_rows': n,
                                                'rate': d / n if n else None}
    dump(RUN / 'MAJOR_MODEL_DISAGREEMENT.json', {'meaning': 'Prediction disagreement, not test error; Qwen unclear is excluded and AST unavailable has zero comparable rows',
                                               'matrix': major_disagreement})
    matrix.loc[matrix.fixed_pair_changes_System1, ['Id', 'filename', 'predicted_class', 'fixed_pair_predicted_class',
                                                 'fixed_pair_confidence', 'fixed_pair_margin', 'ambiguity_pair']].to_csv(
        RUN / 'SYSTEM1_TO_FIXED_PAIR_CHANGES.csv', index=False, float_format='%.17g')
    matrix.loc[matrix.uncertainty_category.eq('HARD')].to_csv(RUN / 'HARD_CASES.csv', index=False, float_format='%.17g')
    pd.DataFrame(disagreement).to_csv(RUN / 'MODEL_DISAGREEMENT_COUNTS.csv', index_label='model')
    pd.DataFrame(counts).reindex(CLASSES).fillna(0).astype(int).to_csv(RUN / 'CLASS_PREDICTION_COUNTS.csv', index_label='class')
    hard_mask = category == 'HARD'
    summary = {'target_rows': 209, 'categories': dict(Counter(category)),
               'category_definition': 'Precommitted evidence triage only; not calibrated correctness probability',
               'certified_retrieval_rows': int(covered.sum()), 'nonretrieval_rows': int((~covered).sum()),
               'class_counts': counts, 'model_disagreement_counts': disagreement,
               'hard_case_Ids': test_ids[hard_mask].tolist(),
               'hard_case_mechanisms': dict(Counter(matrix.loc[hard_mask, 'dominant_uncertainty_mechanism'])),
               'all_case_mechanisms': dict(Counter(matrix.dominant_uncertainty_mechanism)),
               'pair_top2_ambiguities_all': dict(Counter(all_pairs)),
               'pair_top2_ambiguities_hard': dict(Counter(matrix.loc[hard_mask, 'ambiguity_pair'])),
               'neutral_sad_boundary_hard_Ids': matrix.loc[hard_mask & matrix.dominant_uncertainty_mechanism.eq('NEUTRAL_SAD_ACOUSTIC_BOUNDARY'), 'Id'].to_list(),
               'System1_to_pair_final_transition': pd.crosstab(current_final, pair_final).reindex(index=CLASSES, columns=CLASSES, fill_value=0).to_dict(),
               'changed_vs_System1_Ids': test_ids[current_final != pair_final].tolist(),
               'changed_vs_System1_count': int(np.sum(current_final != pair_final)),
               'changed_retrieval_rows': int(np.sum((current_final != pair_final) & covered)),
               'Qwen_test_counts': dict(Counter(semantic)), 'Qwen_hard_case_counts': dict(Counter(semantic.iloc[np.flatnonzero(hard_mask)])),
               'hard_ASR_flagged_rows': int(matrix.loc[hard_mask, 'asr_quality_flags'].ne('[]').sum()),
               'hard_with_recorded_waveform_comparisons': int(sum(bool(recorded_pairs[int(i)]) for i in test_ids[hard_mask])),
               'hard_with_recorded_waveform_cosine_above_certification_threshold': int(sum(any(p['full_waveform_cosine'] >= .95 for p in recorded_pairs[int(i)]) for i in test_ids[hard_mask])),
               'missing_AST_test_rows': 209, 'missing_semantic_probability_rows': 209,
               'test_accuracy_macro_f1_or_number_of_errors': 'UNKNOWN: no test labels',
               'expected_hard_case_corrections': 'UNKNOWN: report eligible coverage and PRIMARY_CV marginal evidence rather than fabricated expected corrections'}

    baseline_cv = cv_heads['e2v']
    models_cv = {'System1': baseline_cv, 'XLSR': cv_heads['xlsr'], 'PAIR': pair_cv,
                 'AST_frozen': ast_cv['B0_VB_seed20260930.npz'], 'AST_adapted_seedmean': ast_cv['B1_SEED_MEAN_VB.npz']}
    audit = {'fold_authority_sha256': canonical['VALIDATION_VB_FOLDS.csv'], 'class_order': CLASSES,
             'scope': 'Exact existing labeled OOF predictions; aggregation unchanged; no new training, split or protected access',
             'models': {n: metrics(train_y, p, fold_numbers) for n, p in models_cv.items()}}
    cb, mb = confidences(baseline_cv)
    cpf, mpf = confidences(pair_cv)
    surrogate = ((cb < .6) | (cpf < .6) | (mb < .2) | (mpf < .2) |
                 (labels(baseline_cv) != labels(pair_cv)) | (labels(baseline_cv) != labels(cv_heads['xlsr'])))
    pair_pred = labels(pair_cv)
    ctrl_pred = labels(baseline_cv)
    audit['pair_vs_current'] = {'macro_f1_delta': audit['models']['PAIR']['macro_f1'] - audit['models']['System1']['macro_f1'],
                                'fold_deltas': (np.array(audit['models']['PAIR']['fold_macro_f1']) - np.array(audit['models']['System1']['fold_macro_f1'])).tolist(),
                                'corrections': int(np.sum((pair_pred == train_y) & (ctrl_pred != train_y))),
                                'breakages': int(np.sum((pair_pred != train_y) & (ctrl_pred == train_y))),
                                'interpretation': 'Ordinary-development evidence, not an independent test or private-score estimate'}
    assert audit['pair_vs_current']['macro_f1_delta'] > 0
    assert all(d > 0 for d in audit['pair_vs_current']['fold_deltas'])
    audit['hard_surrogate'] = {'rows': int(surrogate.sum()),
                              'definition': 'Same confidence/margin and waveform disagreement rules on single held-out OOF predictions; test-only multi-head vote stability unavailable here'}
    audit['AST_complementarity_on_surrogate'] = {}
    for name in ['AST_frozen', 'AST_adapted_seedmean']:
        ast_pred = labels(models_cv[name])
        audit['AST_complementarity_on_surrogate'][name] = {
            'oracle_recoverable_pair_errors': int(np.sum(surrogate & (pair_pred != train_y) & (ast_pred == train_y))),
            'pair_correct_AST_wrong': int(np.sum(surrogate & (pair_pred == train_y) & (ast_pred != train_y))),
            'interpretation': 'Oracle complementarity only; no legitimate routing rule is implied'}
    semantic_train = semantic_all.loc[train_ids].semantic_label.to_numpy()
    non_abstain = np.isin(semantic_train, CLASSES)
    audit['Qwen_on_surrogate'] = {'covered_rows': int(np.sum(surrogate & non_abstain)),
                                'oracle_recoverable_pair_errors': int(np.sum(surrogate & (pair_pred != train_y) & (semantic_train == train_y))),
                                'pair_correct_Qwen_wrong': int(np.sum(surrogate & non_abstain & (pair_pred == train_y) & (semantic_train != train_y))),
                                'interpretation': 'Lexical labels from already inspected ordinary data; no test emotion truth and no independent confirmation'}
    audit['Qwen_on_neutral_sad_errors'] = {
        'pair_errors': int(np.sum(((train_y == 'neutral') & (pair_pred == 'sad')) | ((train_y == 'sad') & (pair_pred == 'neutral')))),
        'Qwen_correct': int(np.sum((((train_y == 'neutral') & (pair_pred == 'sad')) | ((train_y == 'sad') & (pair_pred == 'neutral'))) & (semantic_train == train_y))),
        'Qwen_unclear': int(np.sum((((train_y == 'neutral') & (pair_pred == 'sad')) | ((train_y == 'sad') & (pair_pred == 'neutral'))) & ~non_abstain)),
        'meaning': 'Signal diagnostic only; no oracle routing is deployable'}
    audit['Qwen_full_label_evidence'] = {
        'covered_rows': int(non_abstain.sum()), 'abstained_rows': int((~non_abstain).sum()),
        'correct_covered_rows': int(np.sum(non_abstain & (semantic_train == train_y))),
        'label_cross_tab': pd.crosstab(train_y, semantic_train).to_dict()}
    audit['neutral_sad_pair_confusion'] = {'neutral_to_sad': int(np.sum((train_y == 'neutral') & (pair_pred == 'sad'))),
                                         'sad_to_neutral': int(np.sum((train_y == 'sad') & (pair_pred == 'neutral')))}
    audit['confidence_reliability'] = {}
    for name, p in [('System1', baseline_cv), ('PAIR', pair_cv)]:
        conf, mar = confidences(p)
        mask = (conf >= .8) & (mar >= .5)
        audit['confidence_reliability'][name] = {'high_probability_margin_rows': int(mask.sum()),
                                               'wrong_rows': int(np.sum(mask & (labels(p) != train_y))),
                                               'interpretation': 'High softmax/logistic confidence is not verified correctness; this is not the full test triage rule'}

    reloaded = pd.read_csv(RUN / 'submission_fixed_pair_cv5.csv')
    assert list(reloaded) == list(sample) and np.array_equal(reloaded.Id, test_ids)
    assert set(reloaded.emotion) <= set(CLASSES)
    probability_reload = pd.read_csv(RUN / 'FIXED_PAIR_TEST_INFERENCE.csv')
    stored_pp = probability_reload[['pair_p_' + c for c in CLASSES]].to_numpy()
    assert np.max(np.abs(stored_pp - pp)) < 1e-14
    readiness = {'status': 'READY_FOR_ONE_CONTROLLED_PUBLIC_PROBE_NOT_SUBMITTED',
                 'candidate': 'FIXED_50_50_PRIMARY_CV5_HEADMEAN_V1',
                 'accepted_deployed_champion': 'System1 unchanged',
                 'scientific_challenger': 'Fixed original emotion2vec/XLS-R 50/50 pair',
                 'checks': {'test_rows': 209, 'unique_IDs': 209, 'exact_original_ID_set': True,
                            'exact_original_sample_order': True, 'all_test_WAV_hashes_match_canonical_zip': True,
                            'sample_schema': ['Id', 'emotion'], 'class_order': CLASSES,
                            'probabilities_finite_normalized': True, 'equal_family_weight': True,
                            'equal_five_head_weights_within_each_family': True, 'argmax_without_offsets': True,
                            'retrieval_rows': 78, 'retrieval_map_sha256': canonical['RETRIEVAL_MAP_FINAL.csv'],
                            'retrieval_predictions_unchanged': True, 'adaptive_or_source_routing': False,
                            'semantic_or_AST_routing': False, 'protected_membership_or_performance_read': False,
                            'all_heads_ordinary_PRIMARY_CV': True, 'optimization_seed_is_not_a_protected_split': True,
                            'encoder_execution': False, 'new_fitting': False},
                 'PRIMARY_CV_evidence': audit['pair_vs_current'],
                 'limits': ['Test classifier uses uniform average of saved CV heads rather than unrecorded all-826 XLS-R refit.',
                            'OOF metric evaluates the held-out fold pair, not an in-sample average of all five heads.',
                            'PRIMARY_CV has been reused for model selection; gain is not independent confirmation.',
                            'No AST target probabilities or test optimization-seed replication.',
                            'Public subset is partial evidence; correction versus breakage and private macro-F1 remain unknown.'],
                 'submission_sha256': sha((RUN / 'submission_fixed_pair_cv5.csv').read_bytes()),
                 'authorization': 'User authorization required before any competition upload; none performed',
                 'public_probe_rule': 'Submit exactly this precommitted CSV once if authorized; compare with recorded System1 0.79691, record returned score, and do not retune against it.'}
    dump(RUN / 'TARGET209_SUMMARY.json', summary)
    dump(RUN / 'PRIMARY_CV_AUDIT.json', audit)
    dump(RUN / 'PUBLIC_SUBMISSION_READINESS.json', readiness)
    for name in ['FIXED_PAIR_TEST_INFERENCE.csv', 'submission_fixed_pair_cv5.csv', 'TARGET209_SUMMARY.json',
                 'PRIMARY_CV_AUDIT.json', 'PUBLIC_SUBMISSION_READINESS.json', 'MAJOR_MODEL_DISAGREEMENT.json',
                 'SYSTEM1_TO_FIXED_PAIR_CHANGES.csv', 'HARD_CASES.csv']:
        inventory['derived_artifacts'][name] = {'sha256': sha((RUN / name).read_bytes()),
                                              'producer': 'scripts/build_target209_evidence.py',
                                              'protocol': 'ANALYSIS_PROTOCOL.json', 'source_start': START}
    inventory['derived_artifacts']['docs/TEST209_PREDICTION_MATRIX.csv'] = {
        'sha256': sha((ROOT / 'docs/TEST209_PREDICTION_MATRIX.csv').read_bytes()), 'rows': 209,
        'producer': 'scripts/build_target209_evidence.py', 'protocol': 'ANALYSIS_PROTOCOL.json'}
    inventory['no_protected_access_no_fitting_no_encoder_execution_no_submission'] = True
    dump(RUN / 'EVIDENCE_PROVENANCE.json', inventory)
    print(compact({'category_counts': summary['categories'], 'changes_vs_System1': summary['changed_vs_System1_count'],
                   'hard_mechanisms': summary['hard_case_mechanisms'], 'readiness': readiness['status'],
                   'PRIMARY_CV_pair_gain': audit['pair_vs_current']}))


if __name__ == '__main__':
    main()
