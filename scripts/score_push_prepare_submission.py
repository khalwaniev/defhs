#!/usr/bin/env python3
"""Prepare fixed control + Qwen abstention ONLY after a supported semantic promotion."""
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
    assert decision['selected_system'] == 'CONTROL_PLUS_FIXED_QWEN_ABSTENTION'
    assert decision['semantic_deployment_verdict'] == 'PREPARE_FOR_SS_SUBMISSION_DECISION'
    assert json.loads((RUN / 'AUDIO_PARENT_LOCK.json').read_text())['selected_audio'] == 'CONTROL'
    old_lock = json.loads((ROOT / 'runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001/FINAL_SYSTEM_LOCK.json').read_text())
    inference = ROOT / 'work/frozen_closure/LOCKED_FINALIST_TEST_INFERENCE.csv'
    assert sha256(inference) == old_lock['test_inference_sha256']
    cache = ROOT / '.tmp/rs_system_implementation_001_frozen_screen_v3/rs_defhs_system_implementation_001/emotion2vec_base_meanstd.npz'
    assert sha256(cache) == old_lock['encoder_cache_sha256']
    sample = ROOT / 'work/protected_confirmation/sample_submission.csv'
    # This is only the untouched official sample CSV, never protected folds/results.
    assert sha256(sample) == 'f31b5e849fda2e1d42b9b551a4383750ce0a57fdaee837455d8e56a14039e9c8'
    s = pd.read_csv(sample); assert list(s) == ['Id', 'emotion'] and len(s) == 209 and s.Id.is_unique
    cached = pd.read_csv(inference).set_index('Id').loc[s.Id]
    assert set(cached.index) == set(s.Id) and len(cached) == 209
    audio = CLASSES[cached[P_COLS].to_numpy().argmax(1)]
    assert np.array_equal(audio, cached.ser_pred)
    semantic = pd.read_csv(a.semantic / 'QWEN_SEMANTIC_OUTPUTS.csv').set_index('Id').loc[s.Id].semantic_label.to_numpy()
    assert np.isin(semantic, list(CLASSES) + ['unclear']).all()
    pred = np.where(semantic != 'unclear', semantic, audio)
    retrieval = DS / 'RETRIEVAL_MAP_FINAL.csv'; assert sha256(retrieval) == old_lock['retrieval_map_sha256']
    mapping = pd.read_csv(retrieval); assert len(mapping) == 78 and mapping.test_Id.is_unique and not mapping.conflict.any()
    assert set(mapping.test_Id) <= set(s.Id)
    train = pd.read_csv(DS / 'VALIDATION_VB_FOLDS.csv').set_index('Id').emotion
    for row in mapping.itertuples(index=False):
        neighbors = [int(x) for x in str(row.matched_train_Ids).split(';')]
        assert train.loc[neighbors].eq(row.consensus_emotion).all()
        pred[s.Id.to_numpy() == row.test_Id] = row.consensus_emotion
    assert cached.certified_retrieval_covered.sum() == 78
    out = pd.DataFrame({'Id': s.Id, 'emotion': pred}); out.to_csv(RUN / 'submission.csv', index=False)
    check = pd.read_csv(RUN / 'submission.csv')
    assert list(check) == ['Id', 'emotion'] and len(check) == 209 and check.Id.is_unique
    assert np.array_equal(check.Id, s.Id) and set(check.Id) == set(s.Id)
    assert not check.isna().any().any() and check.emotion.isin(CLASSES).all()
    dump(RUN / 'SUBMISSION_PREPARATION.json', {'sha256': sha256(RUN / 'submission.csv'),
        'local_path': str(RUN / 'submission.csv'), 'rows': 209, 'retrieval_override_count': 78,
        'sample_ID_set_and_order': 'PASS', 'schema': ['Id', 'emotion'],
        'class_counts': check.emotion.value_counts().to_dict(), 'cached_all826_audio_inference_reused': True,
        'system': decision['selected_system'], 'protected_validation_accessed': False,
        'public_LB_used_for_selection': False, 'kaggle_submission_made': False})
    print('SUBMISSION_PREPARATION=PASS', sha256(RUN / 'submission.csv'))


if __name__ == '__main__': main()
