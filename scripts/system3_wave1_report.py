#!/usr/bin/env python3
"""Summarize complete registered Wave1 outputs without fitting or selection."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from defhs_frozen_closure_utils import dump
ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/RS-DEFHS-SYSTEM3-WAVE1-001'

def read(name):
    return json.loads((RUN / name).read_text())

def csv_write(name, rows):
    assert rows
    with (RUN / name).open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--final', action='store_true')
    args = parser.parse_args()
    cpu = read('W1_CPU_PAIR_RESULTS.json')
    secondary = read('W1_SECONDARY_CONFIRMATION.json')
    if args.final:
        assert secondary['status'] == 'COMPLETE'
        assert cpu['protected_validation_read'] is False
        assert cpu['kaggle_submission_made'] is False
        if secondary.get('leading_adapted_for_seed2'):
            for view in ['VB', 'VA']:
                assert (RUN / f'W1_CONFIRMATION_{view}_seed20260917.json').is_file()
    recipes = {'E2V_CONTROL': cpu['control'], 'FIXED_PAIR': cpu['outer_refit'],
               'NESTED_FUSION': read('W1_NESTED_FUSION_RESULTS.json')['results_vs_fixed_pair']}
    fits = []
    def add_measurement(lane, measurement, seed):
        view = measurement['view']
        for arm, key in [(lane+'0', 'matched_frozen'), (lane+'1', 'adapted_vs_matched_frozen')]:
            # Adapted-only seed2 does not create another matched frozen recipe.
            if seed == 20260917 and arm.endswith('0'):
                continue
            recipes.setdefault(f'{arm}_seed{seed}', {}).update(measurement[key])
        for fold in measurement['fold_records']:
            for kind in ['pilot', 'refit']:
                fit = fold[kind]
                fits.append({'arm': fold['arm'], 'view': view, 'seed': seed,
                    'fold': fold['fold'], 'fit': kind, 'selected_epoch': fit['selected_epoch'],
                    'epochs_executed': len(fit['traces']), 'wall_seconds': fit['wall_seconds'],
                    'examples_per_second': fit['examples_per_second'],
                    'peak_GPU_memory_bytes': fit['peak_GPU_memory_bytes'],
                    'training_ID_sha256': fit['fingerprint']['training_ID_sha256'],
                    'stopping_ID_sha256': fit['fingerprint']['stopping_ID_sha256'],
                    'prediction_ID_sha256': fold['prediction_ID_sha256'],
                    'checkpoint_sha256': fit['checkpoint_sha256'], 'source_sha': fold['source_sha']})
    for lane, name in [('A', 'W1_E2V_ADAPTATION_RESULTS.json'), ('B', 'W1_AST_RESULTS.json')]:
        add_measurement(lane, read(name), 20260930)
    for lane, blend in read('W1_FIXED_BLEND_RESULTS.json')['arms'].items():
        recipes[f'Candidate_{lane}_seed20260930'] = blend['results']
    for view, seed in [('VA', 20260930), ('VB', 20260917), ('VA', 20260917)]:
        path = RUN / f'W1_CONFIRMATION_{view}_seed{seed}.json'
        if not path.exists():
            continue
        result = json.loads(path.read_text())
        for lane, measurement in result['measurements'].items():
            add_measurement(lane, measurement, seed)
        for lane, blend in result['fixed_blends'].items():
            recipes.setdefault(f'Candidate_{lane}_seed{seed}', {}).update(blend['results'])
        for lane, stability in result.get('seed_stability', {}).items():
            recipes.setdefault(f'{lane}1_seed_mean', {}).update(stability['mean_probability_vs_pair'])
            recipes.setdefault(f'Candidate_{lane}_seed_mean', {}).update(stability['fixed_blend_mean_vs_pair'])
    rows, gaps = [], []
    for recipe, results in recipes.items():
        for view in ['VB', 'VA']:
            if view not in results:
                continue
            r = results[view]
            rows.append({'recipe': recipe, 'view': view, 'macro_F1': r['macro_f1'],
                'five_folds': json.dumps(r['fold_macro_f1']),
                'per_class': json.dumps(r['per_class_f1'], sort_keys=True),
                'CLEAN_macro_F1': r['strata']['CLEAN']['macro_f1'],
                'nonretrieval_macro_F1': r['strata']['nonretrieval']['macro_f1'] if view == 'VA' else ''})
            metrics = [(f'{view}_macro_F1', r['macro_f1'])]
            if view == 'VB': metrics.append(('CLEAN_VB_macro_F1', r['strata']['CLEAN']['macro_f1']))
            if view == 'VA': metrics.append(('VA_nonretrieval_macro_F1', r['strata']['nonretrieval']['macro_f1']))
            for metric, score in metrics:
                gaps.append({'recipe': recipe, 'metric': metric, 'current_score': score,
                    'target': .90, 'distance_to_090': .90-score})
    csv_write('W1_METRIC_SUMMARY.csv', rows)
    csv_write('TARGET_GAP_TO_090.csv', gaps)
    csv_write('COMPUTE_FIT_SUMMARY.csv', fits)
    dump(RUN / 'COMPUTE_SUMMARY.json', {'status': 'COMPLETE' if args.final else 'PARTIAL',
        'CPU_pair_wall_seconds': cpu['wall_seconds'],
        'GPU_fit_wall_seconds_sum': sum(x['wall_seconds'] for x in fits),
        'GPU_peak_memory_bytes': max(x['peak_GPU_memory_bytes'] for x in fits),
        'fit_count': len(fits),
        'limits': 'Fit wall time includes fit-side I/O; excludes model preparation and outer inference. Account GPU quota is recorded separately; summed fit time is not billed accelerator time.'})
    print(json.dumps({'status': 'COMPLETE' if args.final else 'PARTIAL',
        'recipes': len(recipes), 'metric_rows': len(rows), 'fit_records': len(fits)}))
if __name__ == '__main__':
    main()
