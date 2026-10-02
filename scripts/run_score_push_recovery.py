#!/usr/bin/env python3
"""SS-authorized cached CPU recovery. No encoder, LLM, protected or Kaggle calls."""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, subprocess, time, warnings
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from defhs_frozen_closure_utils import *
from run_score_push_cpu import contract, views, uncertainty, judgments

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/RS-DEFHS-SCORE-PUSH-001'
DS = ROOT / 'runs/DS-DEFHS-VALIDATION-HARDENING-002'
SCRATCH = ROOT / 'work/score_push_recovery'
QWEN = ROOT / '.tmp/rs_score_push_001_semantic_v1/rs_defhs_score_push_001_semantic/QWEN_SEMANTIC_OUTPUTS.csv'
_CACHE = {}


def source():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def cached_inputs():
    manifest = json.loads((RUN / 'ARTIFACT_MANIFEST.json').read_text())
    digests = {r['name']: r['sha256'] for r in manifest['artifacts']}
    audio = json.loads((RUN / 'AUDIO_RESULTS.json').read_text())
    for model, path in audio['cache_files'].items():
        p = ROOT / path; assert sha256(p) == digests[p.name], p
        z = np.load(p); assert len(z['Id']) == 1035 and len(set(z['Id'])) == 1035
        assert z['raw_native_scores'].shape == (1035, 9)
        assert np.isfinite(z['raw_native_scores']).all() and np.isfinite(z['utterance']).all()
        assert np.allclose(z['raw_native_scores'].sum(1), 1, atol=1e-6)
    assert sha256(QWEN) == digests[QWEN.name]
    semantic = pd.read_csv(QWEN).set_index('Id')
    assert len(semantic) == 1035 and semantic.index.is_unique
    assert semantic.semantic_label.isin(list(CLASSES) + ['unclear']).all()
    return audio, semantic, digests


def load_record():
    p = RUN / 'RECOVERY_RESULTS.json'
    if p.exists(): return json.loads(p.read_text())
    return {'mission_id': 'RS-DEFHS-SCORE-PUSH-001',
        'recovery_starting_sha': 'd0c7e7630b1e39e4854a5f6b1e7d123e8602e212',
        'config_sha256': sha256(RUN / 'RECOVERY_CONFIG.json'),
        'encoder_extraction_repeated': False, 'Qwen_inference_repeated': False,
        'protected_validation_accessed': False, 'public_LB_used_for_selection': False,
        'kaggle_submission_made': False}


def source_gate():
    record = load_record(); assert 'source_gate' not in record, 'Reuse recorded source gate.'
    folds, ev, masks, control = contract()
    _, semantic, digests = cached_inputs()
    ids = folds['VB'].Id.to_numpy(); sem = semantic.loc[ids].semantic_label.to_numpy()
    active = masks['VB']['int32'] & (sem != 'unclear')
    assert int(masks['VB']['int32'].sum()) == 80
    q = {v: p.copy() for v, p in control.items()}
    for v, p in q.items():
        p[active] = np.eye(4)[labels(sem[active])]
        save_oof(RUN / f'RECOVERY_SOURCE_GATE_OOF_{v}.csv', folds[v], p,
            semantic_label=sem, dtype=np.where(masks[v]['int32'], 'int32', 'int16'), semantic_gate_active=active)
    result = views(q, folds, masks, control)
    old = json.loads((RUN / 'SEMANTIC_RESULTS.json').read_text())
    diagnostics = {}; reproduced = {}
    for v, f in folds.items():
        y = labels(f.emotion); pa, pg = control[v].argmax(1), q[v].argmax(1)
        assert np.array_equal(pa[masks[v]['int16']], pg[masks[v]['int16']])
        got, expected = result[v]['strata']['int32'], old['fusion'][v]['strata']['int32']
        for key in ['macro_f1', 'control_macro_f1', 'delta_vs_control', 'corrections', 'breakages']:
            assert got[key] == expected[key], (v, key, got[key], expected[key])
        reproduced[v] = {'status': 'EXACT_PARITY', **got}
        diagnostics[v] = {'active_valid_semantic_rows': int(active.sum()),
            'actual_label_changes': int(np.sum(pg != pa)),
            'corrections': int(np.sum((pa != y) & (pg == y))),
            'breakages': int(np.sum((pa == y) & (pg != y))),
            'folds': [{
                'fold': k, 'int32_rows': int(np.sum(masks[v]['int32'] & f.fold.eq(k).to_numpy())),
                'active_valid_semantic': int(np.sum(active & f.fold.eq(k).to_numpy())),
                'corrections': int(np.sum((pa != y) & (pg == y) & f.fold.eq(k).to_numpy())),
                'breakages': int(np.sum((pa == y) & (pg != y) & f.fold.eq(k).to_numpy())),
                'delta': f1(y[f.fold == k], pg[f.fold == k]) - f1(y[f.fold == k], pa[f.fold == k])}
                for k in range(5)],
            'per_class': {str(c): {
                'delta_F1': result[v]['per_class_f1'][c] - f1(y, pa, per_class=True)[j],
                'corrections': int(np.sum((y == j) & (pa != y) & (pg == y))),
                'breakages': int(np.sum((y == j) & (pa == y) & (pg != y)))} for j,c in enumerate(CLASSES)}}
    # Original component multiplier operator is diagnostic only after this
    # source rule was authorized in response to the already-observed results.
    ci = uncertainty({'SOURCE_GATE': q}, control, folds, masks, ev)
    judgment = judgments('SOURCE_GATE', result, ci, q, control, folds)
    judgment['scientific_robustness'].update({'independent_confirmation': False,
        'interpretation': 'Post-diagnostic source-rule selection; conditional ordinary-OOF interval, not independent scientific confirmation'})
    audio_va = pd.read_csv(ROOT / 'runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001/FINALIST_VA_RETRIEVAL_AUDIT.csv').set_index('Id').loc[ids]
    pred = q['VA'].argmax(1).copy(); covered = audio_va.retrieval_covered.to_numpy(bool)
    pred[covered] = labels(audio_va.pipeline_pred)[covered]
    retrieval_va = report(labels(folds['VA'].emotion), pred, folds['VA'].fold.to_numpy())
    retrieval_va.update({'covered_rows': int(covered.sum()), 'override_unchanged': True})
    numeric = {'positive_VB': result['VB']['macro_f1'] > old['fusion']['VB']['strata']['all']['control_macro_f1'],
        'positive_VB_folds': sum(row['delta'] > 0 for row in diagnostics['VB']['folds']),
        'majority_VB_folds_positive': sum(row['delta'] > 0 for row in diagnostics['VB']['folds']) >= 3,
        'positive_VA': result['VA']['strata']['all']['delta_vs_control'] > 0,
        'positive_VA_nonretrieval': result['VA']['strata']['nonretrieval']['delta_vs_control'] > 0,
        'all_four_classes_predicted': len(set(q['VB'].argmax(1))) == 4 and len(set(q['VA'].argmax(1))) == 4}
    record['source_gate'] = {'experiment_id': 'SP-RECOVERY-SOURCE-INT32-QWEN',
        'hypothesis': 'Semantics restores documented weak int32 audio transfer without breaking the main int16 source',
        'source_sha': source(), 'configuration': json.loads((RUN / 'RECOVERY_CONFIG.json').read_text())['source_gate'],
        'cached_Qwen_sha256': digests[QWEN.name], 'results': result,
        'corrections_breakages': diagnostics, 'int32_previous_result_reproduction': reproduced,
        'VA_retrieval_aware': retrieval_va, 'judgments': judgment,
        'numeric_candidate_conditions': numeric, 'class_collapse_review': 'Per-class table requires execution-engineer review before candidate preparation',
        'adaptive_authorization': True, 'independent_scientific_confirmation': False,
        'OOF_sha256': {v: sha256(RUN / f'RECOVERY_SOURCE_GATE_OOF_{v}.csv') for v in folds}}
    dump(RUN / 'RECOVERY_RESULTS.json', record)
    print(json.dumps({'source_gate': result, 'conditions': numeric, 'corrections_breakages': diagnostics}, indent=2, default=lambda x:x.item()), flush=True)


def fitted(C, x, y, training, validation):
    assert not np.any(training & validation)
    assert len(set(y[training])) == 4
    model = make_pipeline(StandardScaler(), LogisticRegression(C=float(C), max_iter=5000, random_state=20261001))
    model.fit(x[training], y[training]); assert np.array_equal(model.classes_, CLASSES)
    assert model[0].n_samples_seen_ == int(training.sum())
    return model.predict_proba(x[validation])


def fit_outer(task):
    warnings.simplefilter('error', ConvergenceWarning)
    model, rep, kind, view, outer, cache_path, cache_sha, config_sha, measurement_sha = task
    key = (cache_path, rep, view)
    if key not in _CACHE:
        z = np.load(cache_path); f = pd.read_csv(DS / f'VALIDATION_{view}_FOLDS.csv').sort_values('Id').reset_index(drop=True)
        pos = {int(v): i for i,v in enumerate(z['Id'])}
        # Retain the stored dtype. The previous utterance authority scales
        # float32 and used two BLAS threads; changing either can alter a
        # boundary prediction through finite-tolerance LBFGS numerics.
        x = z[rep][[pos[int(i)] for i in f.Id]]
        _CACHE[key] = x, f
    x, f = _CACHE[key]; fs = f.fold.to_numpy(); y = f.emotion.to_numpy()
    train, validation = fs != outer, fs == outer
    name = model + ('_score9_C1' if kind == 'fixed' else '_' + ('score9' if rep == 'raw_native_scores' else 'utterance') + '_NESTED_C')
    output = SCRATCH / f'{name}_{view}_fold{outer}.npz'
    fingerprint = {'protocol': 'existing_fold_nested_C_v1', 'name': name, 'view': view, 'outer': outer,
        'cache_sha256': cache_sha, 'config_sha256': config_sha, 'fold_sha256': sha256(DS / f'VALIDATION_{view}_FOLDS.csv')}
    if rep == 'utterance': fingerprint['numeric_policy'] = 'stored_float32_and_legacy_BLAS_2'
    if output.exists():
        saved = np.load(output); meta = json.loads(str(saved['metadata']))
        assert meta['fingerprint'] == fingerprint
        return name, view, outer, saved['prob'], meta
    start = time.monotonic(); scores = {}; inner_audit = []
    with threadpool_limits(limits=2 if rep == 'utterance' else 1):
        if kind == 'fixed': chosen = 1.
        else:
            cfg = json.loads((RUN / 'RECOVERY_CONFIG.json').read_text())['regularization_check']
            inner_prob = {str(C): np.zeros((int(train.sum()), 4)) for C in cfg['C']}
            training_positions = np.flatnonzero(train)
            for inner in sorted(set(fs[train])):
                itrain = train & (fs != inner); ival = train & (fs == inner)
                assert not np.any(itrain & validation) and not np.any(ival & validation)
                inner_audit.append({'inner_fold': int(inner), 'fit_rows': int(itrain.sum()),
                    'validation_rows': int(ival.sum()), 'outer_rows_used': 0})
                for C in cfg['C']:
                    inner_prob[str(C)][ival[training_positions]] = fitted(C, x, y, itrain, ival)
            scores = {str(C): f1(labels(y[train]), inner_prob[str(C)].argmax(1)) for C in cfg['C']}
            chosen = min(cfg['C'], key=lambda C: (-scores[str(C)], C))
        prob = fitted(chosen, x, y, train, validation)
    meta = {'fingerprint': fingerprint, 'source_sha': measurement_sha, 'C': float(chosen),
        'inner_training_side_scores': scores, 'inner_audit': inner_audit,
        'outer_fit_rows': int(train.sum()), 'outer_heldout_rows': int(validation.sum()),
        'outer_heldout_used_for_C_selection': False, 'wall_seconds': time.monotonic() - start}
    np.savez_compressed(output, prob=prob, metadata=np.asarray(json.dumps(meta)))
    return name, view, outer, prob, meta


def recovery_audio():
    record = load_record(); assert 'cached_audio' not in record, 'Reuse recorded recovery results.'
    folds, ev, masks, control = contract(); audio, _, digests = cached_inputs()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    tasks = []; config_sha = sha256(RUN / 'RECOVERY_CONFIG.json'); measurement_sha = source()
    for model, path in audio['cache_files'].items():
        for rep, kind in [('raw_native_scores','fixed'), ('raw_native_scores','nested'), ('utterance','nested')]:
            for view in folds:
                for outer in range(5):
                    tasks.append((model, rep, kind, view, outer, str(ROOT / path), digests[Path(path).name], config_sha, measurement_sha))
    probs, audit = {}, {}; started = time.monotonic()
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fit_outer, task): task for task in tasks}
        done = 0
        for future in concurrent.futures.as_completed(futures):
            name, view, outer, prob, meta = future.result()
            probs.setdefault(name, {}).setdefault(view, np.zeros((826,4)))[folds[view].fold.eq(outer)] = prob
            audit.setdefault(name, {}).setdefault(view, {})[str(outer)] = meta
            done += 1; print(f'CPU_RECOVERY_OUTER_DONE={done}/{len(tasks)} {name} {view} fold{outer} C={meta["C"]}', flush=True)
    for name, p in probs.items():
        for v,f in folds.items():
            assert np.isfinite(p[v]).all() and np.allclose(p[v].sum(1),1)
            save_oof(RUN / f'RECOVERY_OOF_{name}_{v}.csv', f, p[v])
    result = {n: views(p, folds, masks, control) for n,p in probs.items()}
    ci = uncertainty(probs, control, folds, masks, ev)
    decision = {n: judgments(n,result[n],ci,p,control,folds) for n,p in probs.items()}
    strongest = max(probs, key=lambda n:(result[n]['VB']['macro_f1'],result[n]['VA']['strata']['nonretrieval']['macro_f1'],n))
    # One fixed optional complementarity entry condition, written before recovery
    # scoring: within 0.01 VB and no >0.02 VA/nonretrieval regression.
    rr = result[strongest]
    competitive = rr['VB']['macro_f1'] >= .7383745765682462-.01 and rr['VA']['macro_f1'] >= .8016519493535111-.02 and rr['VA']['strata']['nonretrieval']['macro_f1'] >= .7311166934987506-.02
    blend = {'executed': False, 'reason': 'No cached recovered lane is meaningfully competitive under recorded optional-entry definition'}
    if competitive:
        name = strongest + '+EQUAL+CONTROL'; p = {v:(probs[strongest][v]+control[v])/2 for v in folds}
        z = views(p,folds,masks,control); bci = uncertainty({name:p},control,folds,masks,ev)
        blend = {'executed': True, 'members': [strongest,'CONTROL'], 'weights':[.5,.5],
            'results': z, 'judgments': judgments(name,z,bci,p,control,folds)}
        for v,f in folds.items(): save_oof(RUN/f'RECOVERY_OOF_{name}_{v}.csv',f,p[v])
    record['cached_audio'] = {'source_sha': measurement_sha, 'wall_seconds':time.monotonic()-started,
        'compute':'CPU only; four processes; stored dtype; two BLAS threads for utterance to reproduce prior C1 authority, one for score9',
        'realizations':{n:{'results':result[n],'judgments':decision[n],'nested_C_audit':audit[n],
            'OOF_sha256':{v:sha256(RUN/f'RECOVERY_OOF_{n}_{v}.csv') for v in folds}} for n in probs},
        'strongest_recovery':strongest,'optional_blend':blend,
        'C_selection':'four inner existing training-side folds per outer fold; aggregate inner OOF macro-F1; lowest-C exact tie; no outer validation label used'}
    dump(RUN/'RECOVERY_RESULTS.json',record)
    print('CPU_RECOVERY_COMPLETED',strongest,rr['VB']['macro_f1'],flush=True)


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--stage',choices=['source','audio'],required=True); a=parser.parse_args()
    warnings.simplefilter('error',ConvergenceWarning)
    with threadpool_limits(limits=1):
        if a.stage=='source': source_gate()
        else: recovery_audio()


if __name__=='__main__': main()
