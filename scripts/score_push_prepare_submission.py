#!/usr/bin/env python3
"""Prepare authorized cached control/Qwen candidate with certified retrieval last."""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from defhs_frozen_closure_utils import CLASSES, P_COLS, sha256, dump

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/RS-DEFHS-SCORE-PUSH-001'
DS = ROOT / 'runs/DS-DEFHS-VALIDATION-HARDENING-002'


def main():
    p = argparse.ArgumentParser(); p.add_argument('--semantic', type=Path, required=True); a = p.parse_args()
    decision = json.loads((RUN / 'FINAL_DECISION.json').read_text())
    assert decision['selected_system'] in ['CONTROL_PLUS_FIXED_QWEN_ABSTENTION', 'CONTROL_PLUS_INT32_QWEN_ABSTENTION']
    gated = decision['selected_system'] == 'CONTROL_PLUS_INT32_QWEN_ABSTENTION'
    assert decision['semantic_deployment_verdict'] == ('PREPARE_SOURCE_GATE_CANDIDATE' if gated else 'PREPARE_FOR_SS_SUBMISSION_DECISION')
    if gated:
        gate = json.loads((RUN / 'RECOVERY_RESULTS.json').read_text())['source_gate']
        assert gate['candidate_preserved'] and gate['candidate_verdict'] == 'PREPARE_SOURCE_GATE_CANDIDATE'
        assert gate['numeric_candidate_conditions']['positive_VB'] and gate['numeric_candidate_conditions']['majority_VB_folds_positive']
        assert gate['numeric_candidate_conditions']['positive_VA'] and gate['numeric_candidate_conditions']['positive_VA_nonretrieval']
        assert gate['class_collapse_review'].startswith('PASS')
        assert sha256(a.semantic / 'QWEN_SEMANTIC_OUTPUTS.csv') == gate['cached_Qwen_sha256']
    assert json.loads((RUN / 'AUDIO_PARENT_LOCK.json').read_text())['selected_audio'] == 'CONTROL'
    old_lock = json.loads((ROOT / 'runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001/FINAL_SYSTEM_LOCK.json').read_text())
    inference = ROOT / 'work/frozen_closure/LOCKED_FINALIST_TEST_INFERENCE.csv'
    assert sha256(inference) == old_lock['test_inference_sha256']
    cache = ROOT / '.tmp/rs_system_implementation_001_frozen_screen_v3/rs_defhs_system_implementation_001/emotion2vec_base_meanstd.npz'
    assert sha256(cache) == old_lock['encoder_cache_sha256']
    sample = ROOT / 'work/score_push/sample_submission.csv'
    assert sha256(sample) == 'f31b5e849fda2e1d42b9b551a4383750ce0a57fdaee837455d8e56a14039e9c8'
    s = pd.read_csv(sample); assert list(s) == ['Id', 'emotion'] and len(s) == 209 and s.Id.is_unique
    cached = pd.read_csv(inference).set_index('Id').loc[s.Id]
    assert set(cached.index) == set(s.Id) and len(cached) == 209
    audio = CLASSES[cached[P_COLS].to_numpy().argmax(1)]
    assert np.array_equal(audio, cached.ser_pred)
    semantic = pd.read_csv(a.semantic / 'QWEN_SEMANTIC_OUTPUTS.csv').set_index('Id').loc[s.Id].semantic_label.to_numpy()
    assert np.isin(semantic, list(CLASSES) + ['unclear']).all()
    dm_path = DS / 'DATA_MANIFEST.csv'
    assert sha256(dm_path) == '1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469'
    dm = pd.read_csv(dm_path).set_index('Id').loc[s.Id]
    assert dm['split'].eq('test').all() and dm['dtype'].isin(['int16', 'int32']).all()
    eligible = dm['dtype'].eq('int32').to_numpy() if gated else np.ones(209, bool)
    if gated: assert int(eligible.sum()) == 22
    active = eligible & (semantic != 'unclear')
    pred = np.where(active, semantic, audio)
    pre_retrieval = pred.copy()
    assert np.array_equal(pred[~eligible], audio[~eligible])
    current_submission = ROOT / 'runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001/submission.csv'
    current = pd.read_csv(current_submission)
    assert list(current) == ['Id', 'emotion'] and np.array_equal(current.Id, s.Id)
    assert np.array_equal(current.emotion, cached.final_pred)
    retrieval = DS / 'RETRIEVAL_MAP_FINAL.csv'; assert sha256(retrieval) == old_lock['retrieval_map_sha256']
    mapping = pd.read_csv(retrieval); assert len(mapping) == 78 and mapping.test_Id.is_unique and not mapping.conflict.any()
    assert set(mapping.test_Id) <= set(s.Id)
    train = pd.read_csv(DS / 'VALIDATION_VB_FOLDS.csv').set_index('Id').emotion
    for row in mapping.itertuples(index=False):
        neighbors = [int(x) for x in str(row.matched_train_Ids).split(';')]
        assert train.loc[neighbors].eq(row.consensus_emotion).all()
        pred[s.Id.to_numpy() == row.test_Id] = row.consensus_emotion
    assert cached.certified_retrieval_covered.sum() == 78
    certified = s.Id.isin(mapping.test_Id).to_numpy()
    assert np.array_equal(certified, cached.certified_retrieval_covered.to_numpy(bool))
    assert np.array_equal(pred[certified], cached.final_pred.to_numpy()[certified])
    out = pd.DataFrame({'Id': s.Id, 'emotion': pred}); out.to_csv(RUN / 'submission.csv', index=False)
    check = pd.read_csv(RUN / 'submission.csv')
    assert list(check) == ['Id', 'emotion'] and len(check) == 209 and check.Id.is_unique
    assert np.array_equal(check.Id, s.Id) and set(check.Id) == set(s.Id)
    assert not check.isna().any().any() and check.emotion.isin(CLASSES).all()
    dump(RUN / 'SUBMISSION_PREPARATION.json', {'sha256': sha256(RUN / 'submission.csv'),
        'local_path': str(RUN / 'submission.csv'), 'rows': 209, 'retrieval_override_count': 78,
        'sample_ID_set_and_order': 'PASS', 'schema': ['Id', 'emotion'],
        'class_counts': check.emotion.value_counts().to_dict(), 'cached_all826_audio_inference_reused': True,
        'test_int32_rows': int(dm['dtype'].eq('int32').sum()),
        'valid_semantic_gate_rows': int(active.sum()),
        'semantic_changes_before_retrieval': int(np.sum(pre_retrieval != audio)),
        'labels_changed_vs_current_submission': int(np.sum(check.emotion.to_numpy() != current.emotion.to_numpy())),
        'changed_Ids': check.loc[check.emotion.to_numpy() != current.emotion.to_numpy(), 'Id'].tolist(),
        'current_submission_sha256': sha256(current_submission),
        'test_int16_unchanged_vs_current': bool(np.array_equal(check.emotion.to_numpy()[dm['dtype'].eq('int16')], current.emotion.to_numpy()[dm['dtype'].eq('int16')])),
        'certified_78_predictions_unchanged': True,
        'system': decision['selected_system'], 'protected_validation_accessed': False,
        'public_LB_used_for_selection': False, 'kaggle_submission_made': False})
    print('SUBMISSION_PREPARATION=PASS', sha256(RUN / 'submission.csv'))


if __name__ == '__main__': main()
