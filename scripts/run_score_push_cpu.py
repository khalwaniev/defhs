#!/usr/bin/env python3
"""Bounded ordinary-development audio/semantic experiments. Protected stays closed."""
from __future__ import annotations
import argparse, json, subprocess, time, warnings
from pathlib import Path
import joblib, numpy as np, pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from defhs_frozen_closure_utils import *

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/RS-DEFHS-SCORE-PUSH-001'
OLD = ROOT / 'runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001'
DS = ROOT / 'runs/DS-DEFHS-VALIDATION-HARDENING-002'
WORK = ROOT / 'work/score_push'
V3 = ROOT / '.tmp/rs_system_implementation_001_frozen_screen_v3/rs_defhs_system_implementation_001'
CFG = json.loads((RUN / 'MISSION_CONFIG.json').read_text())


def source():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def read(path):
    assert 'PROTECTED' not in str(path).upper() and 'VALIDATION_VP' not in str(path).upper()
    return pd.read_csv(path)


def contract():
    WORK.mkdir(parents=True, exist_ok=True)
    inventory = {r['artifact']: r['sha256'] for r in json.loads((DS / 'CANONICAL_ARTIFACT_INVENTORY.json').read_text())}
    for name in ['VALIDATION_VA_FOLDS.csv', 'VALIDATION_VB_FOLDS.csv', 'DATA_MANIFEST.csv', 'DUPLICATE_GROUPS_FINAL.csv', 'RETRIEVAL_MAP_FINAL.csv']:
        assert sha256(DS / name) == inventory[name], name
    files = {'ASR_TRANSCRIPTS.csv': 'a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01',
             'PROMPT_CLUSTER_ASSIGNMENTS.csv': 'FROM_MANIFEST'}
    manifest = pd.read_csv(DS / 'CLOSURE_COMPLETED_ARTIFACT_MANIFEST.tsv', sep='\t')
    for name, expected in files.items():
        p = ROOT / 'work/mission_inputs/asr_transcripts' / name
        if expected == 'FROM_MANIFEST':
            row = manifest[manifest.drive_path.str.endswith('/' + name)]; assert len(row) == 1
            expected = row.sha256.iloc[0]
        assert sha256(p) == expected, name
    folds = {v: read(DS / f'VALIDATION_{v}_FOLDS.csv').sort_values('Id').reset_index(drop=True) for v in ['VA', 'VB']}
    ids = folds['VB'].Id.to_numpy()
    assert len(ids) == 826 and len(set(ids)) == 826
    assert np.array_equal(folds['VA'].Id, ids) and np.array_equal(folds['VA'].emotion, folds['VB'].emotion)
    prompt = read(ROOT / 'work/mission_inputs/asr_transcripts/PROMPT_CLUSTER_ASSIGNMENTS.csv')
    dup = read(DS / 'DUPLICATE_GROUPS_FINAL.csv')
    ev = Evidence(ids, dup, prompt)
    repeated = set(prompt.loc[prompt.groupby('prompt_sim_0.90').Id.transform('size') > 1, 'Id'])
    singleton = ~np.isin(ids, list(repeated))
    clean = singleton & ~np.isin(ids, dup.Id)
    audit = read(OLD / 'FINALIST_VA_RETRIEVAL_AUDIT.csv').set_index('Id').loc[ids]
    nonret = ~audit.retrieval_covered.to_numpy(bool)
    dm = read(DS / 'DATA_MANIFEST.csv').set_index('Id').loc[ids]
    latent_path = ROOT / 'work/mission_inputs/latent_regimes/LATENT_REGIME_ASSIGNMENTS.csv'
    expected = manifest[manifest.drive_path.str.endswith('/LATENT_REGIME_ASSIGNMENTS.csv')].sha256.iloc[0]
    assert sha256(latent_path) == expected
    latent = read(latent_path).set_index('Id').loc[ids]
    texts = read(ROOT / 'work/mission_inputs/asr_transcripts/ASR_TRANSCRIPTS.csv').set_index('Id').loc[ids].normalized_transcript.fillna('').to_numpy()
    masks = {}
    strata_path = WORK / 'STRATA.npz'
    if strata_path.exists():
        z = np.load(strata_path); assert np.array_equal(z['Id'], ids)
    else:
        saved = {'Id': ids}
        for v, f in folds.items():
            near = np.zeros(826, bool)
            for k in range(5):
                tr, vl = f.fold.to_numpy() != k, f.fold.to_numpy() == k
                vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=1)
                xt = vec.fit_transform(texts[tr]); xv = vec.transform(texts[vl])
                near[vl] = cosine_similarity(xv, xt).max(axis=1) >= .90
            saved[v + '_no_close'] = ~near
        np.savez_compressed(strata_path, **saved); z = np.load(strata_path)
    for v in folds:
        masks[v] = {'all': np.ones(826, bool), 'CLEAN': clean,
            'prompt_singleton': singleton, 'repeated_prompt': ~singleton,
            'no_close_training_neighbor': z[v + '_no_close'],
            'excluding_Astra48': ~np.isin(ids, CFG['astra_exploratory']['ids']),
            'int16': dm.dtype.eq('int16').to_numpy(), 'int32': dm.dtype.eq('int32').to_numpy()}
        for k in sorted(set(latent.joint_k4)):
            masks[v][f'joint_k4_{k}'] = latent.joint_k4.eq(k).to_numpy()
        if v == 'VA': masks[v]['nonretrieval'] = nonret
    control = {v: valid_oof(OLD / f'FINAL_FROZEN_OOF_{v}.csv', f) for v, f in folds.items()}
    assert abs(f1(labels(folds['VB'].emotion), control['VB'].argmax(1)) - .7383745765682462) < 1e-14
    return folds, ev, masks, control


def views(prob, folds, masks, control):
    result = {}
    for v, f in folds.items():
        y, pred, base = labels(f.emotion), prob[v].argmax(1), control[v].argmax(1)
        result[v] = {**report(y, pred, f.fold.to_numpy()), 'accuracy': float(np.mean(pred == y)),
            'disagreement_with_control': float(np.mean(pred != base)),
            'strata': {name: {'rows': int(m.sum()), 'macro_f1': f1(y[m], pred[m]),
                'control_macro_f1': f1(y[m], base[m]), 'delta_vs_control': f1(y[m], pred[m]) - f1(y[m], base[m]),
                'corrections': int(np.sum(m & (base != y) & (pred == y))),
                'breakages': int(np.sum(m & (base == y) & (pred != y)))} for name, m in masks[v].items()}}
    return result


def uncertainty(probs, base, folds, masks, ev):
    contrasts = {}
    for name, p in probs.items():
        for v, stratum in [('VB', 'all'), ('VB', 'CLEAN'), ('VA', 'all'), ('VA', 'nonretrieval')]:
            contrasts[f'{name}:{v}:{stratum}'] = ev.contrast(labels(folds[v].emotion), p[v].argmax(1), base[v].argmax(1), masks[v][stratum])
    return ev.intervals(contrasts)


def judgments(name, result, ci, prob, base, folds, materiality=.02):
    main = robust(labels(folds['VB'].emotion), prob['VB'].argmax(1), base['VB'].argmax(1), folds['VB'].fold.to_numpy(), ci[f'{name}:VB:all'])
    strict = main['pass'] and ci[f'{name}:VB:CLEAN']['point'] > 0 and ci[f'{name}:VA:nonretrieval']['upper'] >= 0
    vb, va = result['VB'], result['VA']
    positive_folds = sum(d > 0 for d in main['fold_differences'])
    concordant = (ci[f'{name}:VB:all']['point'] > 0 and positive_folds >= 4
        and min(main['delete_fold_differences']) > 0
        and ci[f'{name}:VB:CLEAN']['point'] > 0
        and ci[f'{name}:VA:all']['point'] > 0 and ci[f'{name}:VA:nonretrieval']['point'] > 0)
    return {'scientific_robustness': {'old_conservative_gate_pass': bool(strict), 'primary': main,
                'CLEAN': ci[f'{name}:VB:CLEAN'], 'VA': ci[f'{name}:VA:all'], 'VA_nonretrieval': ci[f'{name}:VA:nonretrieval']},
            'competition_deployment_evidence': {'concordant_observed_gain': bool(concordant),
                'VB_delta': ci[f'{name}:VB:all']['point'], 'positive_VB_folds': positive_folds,
                'VA_delta': ci[f'{name}:VA:all']['point'], 'VA_nonretrieval_delta': ci[f'{name}:VA:nonretrieval']['point'],
                'CLEAN_delta': ci[f'{name}:VB:CLEAN']['point'],
                'materiality_reference_met': bool(ci[f'{name}:VB:all']['point'] >= materiality),
                'automatic_interval_veto': False, 'per_class_and_regime_diagnostics': 'reported in results; inspect before final promotion'}}


def audio(a):
    assert not (RUN / 'AUDIO_RESULTS.json').exists(), 'Reuse recorded audio results; do not repeat.'
    folds, ev, masks, control = contract(); probs = {'CONTROL': control}; definitions = {}
    cache_files = {}
    extraction = json.loads((a.extraction / 'EXTRACTION_RESULTS.json').read_text())
    for model, meta in extraction.items():
        if meta['status'] != 'PASS': continue
        p = a.extraction / meta['artifact']; assert sha256(p) == meta['sha256']; cache_files[model] = str(p)
        z = np.load(p, allow_pickle=False); assert len(z['Id']) == 1035 and len(set(z['Id'])) == 1035
        ix = {int(r): i for i, r in enumerate(z['Id'])}
        for rep in ['native', 'utterance', 'meanstd']:
            name = model + '_' + rep; probs[name] = {}
            for v, f in folds.items():
                pos = [ix[int(i)] for i in f.Id]
                if rep == 'native': q = z['native'][pos].astype(float)
                else:
                    x = z[rep][pos]; q = np.zeros((826, 4)); fs = f.fold.to_numpy()
                    for k in range(5):
                        tr, vl = fs != k, fs == k
                        m = make_pipeline(StandardScaler(), LogisticRegression(C=1, max_iter=5000, random_state=20261001))
                        m.fit(x[tr], f.emotion.to_numpy()[tr]); assert np.array_equal(m.classes_, CLASSES)
                        q[vl] = m.predict_proba(x[vl])
                assert np.isfinite(q).all() and np.allclose(q.sum(1), 1)
                probs[name][v] = q
                save_oof(RUN / f'OOF_{name}_{v}.csv', f, q)
            definitions[name] = {'model': model, 'representation': rep,
                'head': 'native restricted renormalized four-class scores' if rep == 'native' else 'StandardScaler + L2 logistic C1 max_iter5000',
                'hypothesis': 'Stronger pretrained emotion recognition/representation improves ordinary held-out emotion classification',
                'cache_sha256': meta['sha256'], 'source_sha': source()}
    assert definitions, 'No executable audio candidate available.'
    results = {n: views(p, folds, masks, control) for n, p in probs.items()}
    ci = uncertainty({n: p for n, p in probs.items() if n != 'CONTROL'}, control, folds, masks, ev)
    decisions = {n: judgments(n, results[n], ci, p, control, folds) for n, p in probs.items() if n != 'CONTROL'}
    best_per_model = {m: max([n for n in definitions if definitions[n]['model'] == m],
        key=lambda n: (results[n]['VB']['macro_f1'], results[n]['VA']['strata']['nonretrieval']['macro_f1'], n)) for m in cache_files}
    strongest_new = max(best_per_model.values(), key=lambda n: (results[n]['VB']['macro_f1'], results[n]['VA']['strata']['nonretrieval']['macro_f1'], n))
    # Exactly the authorized pairs: best realization per new model + control,
    # and strongest new standalone + the one existing cached XLS-R lane.
    xlsr = {v: valid_oof(V3 / f'OOF_xls_r_300m_{v}.csv', f, 'L2_LOGREG') for v, f in folds.items()}
    probs['CACHED_XLSR'] = xlsr
    pairs = [(n, 'CONTROL') for n in best_per_model.values()
             if results[n]['VB']['macro_f1'] > results['CONTROL']['VB']['macro_f1']]
    pairs.append((strongest_new, 'CACHED_XLSR'))
    pair_meta, pair_probs = {}, {}
    for parent, other in pairs:
        name = parent + '+EQUAL+' + other
        p = {v: (probs[parent][v] + probs[other][v]) / 2 for v in folds}
        pair_probs[name] = p; pair_meta[name] = {'members': [parent, other], 'weights': [.5, .5], 'method': 'equal'}
        results[name] = views(p, folds, masks, control)
    pair_ci = uncertainty(pair_probs, control, folds, masks, ev)
    # Marginal evidence against the new standalone is registered for every pair.
    marginal = {}
    for n, p in pair_probs.items():
        parent = pair_meta[n]['members'][0]
        for v, stratum in [('VB', 'all'), ('VB', 'CLEAN'), ('VA', 'all'), ('VA', 'nonretrieval')]:
            marginal[f'{n}:{v}:{stratum}'] = ev.contrast(labels(folds[v].emotion), p[v].argmax(1), probs[parent][v].argmax(1), masks[v][stratum])
    marginal_ci = ev.intervals(marginal)
    coarse = {}
    for n, p in pair_probs.items():
        decisions[n] = judgments(n, results[n], pair_ci, p, control, folds)
        parent, other = pair_meta[n]['members']; k = f'{n}:VB:all'
        fold_delta = robust(labels(folds['VB'].emotion), p['VB'].argmax(1), probs[parent]['VB'].argmax(1), folds['VB'].fold.to_numpy(), marginal_ci[k])
        promising = (marginal_ci[k]['point'] > 0 and sum(d > 0 for d in fold_delta['fold_differences']) >= 4
            and marginal_ci[f'{n}:VB:CLEAN']['point'] >= 0 and marginal_ci[f'{n}:VA:nonretrieval']['point'] >= 0)
        pair_meta[n].update({'marginal_vs_parent': {k.split(':', 1)[1]: v for k, v in marginal_ci.items() if k.startswith(n + ':')},
                            'marginal_fold_behavior': fold_delta, 'equal_promising': bool(promising)})
        if promising:
            cn = parent + '+COARSE+' + other; coarse[cn] = {}; choices = {}
            for v, f in folds.items():
                q, r = choose_probability_blend([probs[parent][v], probs[other][v]], labels(f.emotion), f.fold.to_numpy(), ev)
                coarse[cn][v] = q; choices[v] = r
            pair_meta[cn] = {'members': [parent, other], 'method': 'quarter_grid_fold_safe_one_SD', 'choices': choices}
            results[cn] = views(coarse[cn], folds, masks, control)
    if coarse:
        coarse_ci = uncertainty(coarse, control, folds, masks, ev)
        for n, p in coarse.items(): decisions[n] = judgments(n, results[n], coarse_ci, p, control, folds)
    probs.update(pair_probs); probs.update(coarse)
    eligible = [n for n, d in decisions.items() if d['competition_deployment_evidence']['concordant_observed_gain']]
    chosen = max(eligible, key=lambda n: (results[n]['VB']['macro_f1'], results[n]['VA']['strata']['nonretrieval']['macro_f1'], n)) if eligible else 'CONTROL'
    # The deployment judgment is based on concordant observed evidence, with
    # scientific uncertainty kept separate under the SS pre-result addendum.
    definition = {'members': [chosen], 'weights': [1.], 'method': 'standalone'} if chosen not in pair_meta else pair_meta[chosen].copy()
    if definition['method'] == 'quarter_grid_fold_safe_one_SD':
        aa, bb = definition['members']; y = labels(folds['VB'].emotion); equal = (probs[aa]['VB'] + probs[bb]['VB']) / 2
        candidates = grid(2); qs = [w[0] * probs[aa]['VB'] + w[1] * probs[bb]['VB'] for w in candidates]
        j = min(range(len(qs)), key=lambda j: (-f1(y, qs[j].argmax(1)), np.count_nonzero(candidates[j]), np.sum((np.array(candidates[j]) - .5) ** 2), candidates[j]))
        gain = f1(y, qs[j].argmax(1)) - f1(y, equal.argmax(1)); sd = np.std(ev.boots(y, qs[j].argmax(1)) - ev.boots(y, equal.argmax(1)), ddof=1)
        definition['weights'] = list(candidates[j]) if gain > sd else [.5, .5]
        definition['deployment_weight_rule'] = 'same fixed grid and one-SD selector on all ordinary OOF; meta-fold behavior reported'
    for v, f in folds.items():
        save_oof(RUN / f'AUDIO_PARENT_OOF_{v}.csv', f, probs[chosen][v])
        for n in pair_probs | coarse:
            save_oof(RUN / f'OOF_{n}_{v}.csv', f, probs[n][v])
    result = {'source_sha': source(), 'config_sha256': sha256(RUN / 'MISSION_CONFIG.json'),
        'control': results['CONTROL'], 'realizations': {n: {'configuration': definitions.get(n, pair_meta.get(n)), 'results': results[n],
            'judgments': decisions[n]} for n in decisions}, 'best_per_model': best_per_model,
        'strongest_new_standalone_before_cached_XLSR': strongest_new, 'pair_diagnostics': pair_meta,
        'selected_audio': chosen, 'cache_files': cache_files, 'extraction_status': extraction,
        'selection_limit': 'Ordinary-development model selection and conditional OOF uncertainty; protected is closed; no public-LB selection',
        'protected_validation_accessed': False, 'kaggle_submission_made': False}
    dump(RUN / 'AUDIO_RESULTS.json', result)
    dump(RUN / 'AUDIO_PARENT_LOCK.json', {'selected_audio': chosen, 'definition': definition,
        'realization_definitions': definitions, 'cache_files': cache_files,
        'results': results[chosen], 'source_sha': source(), 'locked_before_semantic_inference': True,
        'OOF_sha256': {v: sha256(RUN / f'AUDIO_PARENT_OOF_{v}.csv') for v in folds},
        'scientific_robustness': decisions.get(chosen, {}).get('scientific_robustness'),
        'competition_deployment_evidence': decisions.get(chosen, {}).get('competition_deployment_evidence')})
    print(json.dumps({'best_per_model': best_per_model, 'selected_audio': chosen, 'selected_results': results[chosen]}, indent=2, default=lambda x: x.item()), flush=True)


def semantic(a):
    assert not (RUN / 'SEMANTIC_RESULTS.json').exists(), 'Reuse recorded results; no prompt rescue.'
    folds, ev, masks, control = contract()
    lock_path = RUN / 'AUDIO_PARENT_LOCK.json'
    lock = json.loads(lock_path.read_text()); assert lock['locked_before_semantic_inference']
    provenance = json.loads((a.semantic / 'EXECUTION_PROVENANCE.json').read_text())
    assert provenance['audio_parent_lock_sha256'] == sha256(lock_path)
    assert provenance['prompt_sha256'] == CFG['qwen']['prompt_sha256']
    assert provenance['source_ASR_sha256'] == 'a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01'
    assert provenance['model'] == CFG['qwen']['model_id'] and provenance['revision'] == CFG['qwen']['revision']
    assert provenance['input_fields_to_model'] == ['transcript'] and not provenance['enable_thinking']
    for r in json.loads((a.semantic / 'OUTPUT_INVENTORY.json').read_text())['files']:
        p = a.semantic / r['name']; assert p.stat().st_size == r['bytes'] and sha256(p) == r['sha256']
    status = json.loads((a.semantic / 'SEMANTIC_INFERENCE_RESULT.json').read_text()); assert status['status'] == 'PASS'
    table = read(a.semantic / 'QWEN_SEMANTIC_OUTPUTS.csv').set_index('Id')
    assert len(table) == 1035 and table.index.is_unique
    assert table.semantic_label.isin(list(CLASSES) + ['unclear']).all()
    parent = {}
    for v, f in folds.items():
        assert sha256(RUN / f'AUDIO_PARENT_OOF_{v}.csv') == lock['OOF_sha256'][v]
        parent[v] = valid_oof(RUN / f'AUDIO_PARENT_OOF_{v}.csv', f)
    ids = folds['VB'].Id.to_numpy(); sem = table.loc[ids].semantic_label.to_numpy()
    covered = sem != 'unclear'
    index = np.array([list(CLASSES).index(label) if label != 'unclear' else -1 for label in sem])
    fused = {v: p.copy() for v, p in parent.items()}
    for v, p in fused.items():
        p[covered] = np.eye(4)[index[covered]]
        save_oof(RUN / f'SEMANTIC_FUSION_OOF_{v}.csv', folds[v], p, semantic_label=sem)
    y = labels(folds['VB'].emotion)
    result = views(fused, folds, masks, parent)
    diagnostics = {}
    standalone = {'coverage': float(covered.mean()), 'abstention_rate': float((~covered).mean()),
        'covered_rows': int(covered.sum()), 'total_rows': 826,
        'accuracy_counting_abstention_as_error': float(np.mean(index == y)),
        'accuracy_on_covered': float(np.mean(index[covered] == y[covered])) if covered.any() else None,
        'macro_f1_on_covered': f1(y[covered], index[covered]) if covered.any() else None,
        'per_class_F1_on_covered': dict(zip(CLASSES, f1(y[covered], index[covered], per_class=True))) if covered.any() else None,
        'confusion_columns': list(CLASSES) + ['unclear'],
        'confusion': np.bincount(5*y + np.where(covered, index, 4), minlength=20).reshape(4,5),
        'label_counts': {label: int(np.sum(sem == label)) for label in list(CLASSES) + ['unclear']}}
    for v, f in folds.items():
        audio_pred, fusion_pred = parent[v].argmax(1), fused[v].argmax(1)
        strata = dict(masks[v])
        for k in range(5): strata[f'fold_{k}'] = f.fold.to_numpy() == k
        diagnostics[v] = {}
        for name, mask in strata.items():
            active = mask & covered; changed = active & (fusion_pred != audio_pred)
            correction = changed & (audio_pred != y) & (fusion_pred == y)
            breakage = changed & (audio_pred == y) & (fusion_pred != y)
            diagnostics[v][name] = {'rows': int(mask.sum()), 'covered': int(active.sum()),
                'abstention_rate': float(np.mean(~covered[mask])), 'actual_label_changes': int(changed.sum()),
                'corrections': int(correction.sum()), 'breakages': int(breakage.sum()),
                'net_correct_rows': int(correction.sum() - breakage.sum()),
                'changed_both_wrong': int(np.sum(changed & (audio_pred != y) & (fusion_pred != y))),
                'covered_semantic_accuracy': float(np.mean(index[active] == y[active])) if active.any() else None,
                'fusion_macro_f1': f1(y[mask], fusion_pred[mask]),
                'audio_macro_f1': f1(y[mask], audio_pred[mask]),
                'delta': f1(y[mask], fusion_pred[mask]) - f1(y[mask], audio_pred[mask])}
        diagnostics[v]['per_class'] = {str(c): {'rows': int(np.sum(y == k)),
            'abstained': int(np.sum((y == k) & ~covered)),
            'corrections': int(np.sum((y == k) & (audio_pred != y) & (fusion_pred == y))),
            'breakages': int(np.sum((y == k) & (audio_pred == y) & (fusion_pred != y)))} for k,c in enumerate(CLASSES)}
    contrasts = {}
    for v, stratum in [('VB','all'), ('VB','CLEAN'), ('VA','all'), ('VA','nonretrieval'),
            ('VB','excluding_Astra48'), ('VA','excluding_Astra48'), ('VB','prompt_singleton'),
            ('VB','no_close_training_neighbor')]:
        contrasts[f'QWEN:{v}:{stratum}'] = ev.contrast(y, fused[v].argmax(1), parent[v].argmax(1), masks[v][stratum])
    ci = ev.intervals(contrasts)
    judgment = judgments('QWEN', result, ci, fused, parent, folds, materiality=.03)
    judgment['competition_deployment_evidence'].update({
        'excluding_Astra48_VB': ci['QWEN:VB:excluding_Astra48'],
        'excluding_Astra48_VA': ci['QWEN:VA:excluding_Astra48'],
        'prompt_singleton_VB': ci['QWEN:VB:prompt_singleton'],
        'no_close_training_neighbor_VB': ci['QWEN:VB:no_close_training_neighbor'],
        'rough_03_signal_is_not_absolute_cutoff': True,
        'override_consistency': 'fold/stratum corrections and breakages above; no learned gate'})
    record = {'experiment_id': 'SP-QWEN-FIXED-ABSTENTION',
        'hypothesis': 'Pretrained Hindi semantics with abstention corrects missing audio errors outside repeated prompts',
        'source_sha': source(), 'input_output_path': str(a.semantic), 'provenance': provenance,
        'audio_parent': lock['selected_audio'], 'prompt_sha256': CFG['qwen']['prompt_sha256'],
        'fusion_rule': 'valid label replaces audio; unclear retains audio',
        'standalone': standalone, 'fusion': result, 'override_diagnostics': diagnostics,
        'judgments': judgment, 'simultaneous_intervals': ci,
        'Astra48': CFG['astra_exploratory'],
        'test_semantic_rows_cached_but_not_selected_or_scored': 209,
        'no_retuning': True, 'protected_validation_accessed': False, 'public_LB_used_for_selection': False,
        'kaggle_submission_made': False}
    dump(RUN / 'SEMANTIC_RESULTS.json', record)
    print(json.dumps({'standalone': standalone, 'VB': result['VB']['macro_f1'],
        'VA': result['VA']['macro_f1'], 'VA_nonretrieval': result['VA']['strata']['nonretrieval'],
        'judgments': judgment}, indent=2, default=lambda v: v.tolist() if isinstance(v,np.ndarray) else v.item()), flush=True)


def main():
    p = argparse.ArgumentParser(); p.add_argument('--stage', choices=['audio', 'semantic'], required=True)
    p.add_argument('--extraction', type=Path); p.add_argument('--semantic', type=Path); a = p.parse_args()
    warnings.simplefilter('error', ConvergenceWarning)
    with threadpool_limits(limits=2):
        if a.stage == 'audio':
            assert a.extraction is not None; audio(a)
        else:
            assert a.semantic is not None; semantic(a)


if __name__ == '__main__': main()
