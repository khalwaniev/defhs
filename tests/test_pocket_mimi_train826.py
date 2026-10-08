"""Integrity failures and train-only fitting, without audio or checkpoint access."""
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from analyze_pocket_mimi_complementarity import paired_counts
spec = importlib.util.spec_from_file_location("pocket_runner", ROOT / "kaggle/rs_defhs_pocket_mimi_train826_001/run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class TrainOnlyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folds, cls.manifest, cls.preflight, cls.pre_rows = runner.load_authority()
        cls.features = cls.folds[["Id", "filename", "emotion"]].copy()
        cls.features[runner.FEATURE_COLUMNS] = np.ones((826, 64))

    def test_packaged_authority_contains_only_training_wavs(self):
        self.assertEqual(set(self.manifest.split), {"train"})
        self.assertEqual(self.folds.Id.tolist(), self.manifest.Id.tolist())
        self.assertEqual(len(self.pre_rows), 8)
        self.assertEqual(set(runner.AUTHORITY["inputs"]), {"VALIDATION_VB_FOLDS.csv", "TRAIN_WAV_MANIFEST.csv",
                         "PREFLIGHT.json", "PREFLIGHT_ROWS.csv", "SCRIPT_SHA256.txt"})

    def test_corrupt_membership_is_rejected(self):
        original = runner.AUTHORITY
        damaged = copy.deepcopy(original)
        damaged["inputs"]["VALIDATION_VB_FOLDS.csv"]["sha256"] = "0" * 64
        try:
            runner.AUTHORITY = damaged
            with self.assertRaisesRegex(runner.ProtocolError, "Input hash mismatch"):
                runner.load_authority()
        finally:
            runner.AUTHORITY = original

    def test_invalid_features_stop_before_modeling(self):
        cases = {}
        x = self.features.copy()
        x.loc[1, "Id"] = x.loc[0, "Id"]
        cases["duplicate"] = x
        x = self.features.copy()
        x.loc[0, "f00"] = np.inf
        cases["nonfinite"] = x
        x = self.features.drop(columns=["f63"])
        cases["missing_dimension"] = x
        x = self.features.copy()
        x["f64"] = 0
        cases["extra_dimension"] = x
        x = self.features.iloc[::-1].reset_index(drop=True)
        cases["misaligned_ids"] = x
        x = self.features.copy()
        x.loc[0, "filename"] = "wrong.wav"
        cases["wrong_wav_mapping"] = x
        for name, invalid in cases.items():
            with self.subTest(name=name), self.assertRaises(runner.ProtocolError):
                runner.validate_features(invalid, self.folds)

    def test_heldout_features_and_labels_do_not_change_fitted_model(self):
        # Synthetic fitting fixture; no competition feature extraction/scoring.
        rng = np.random.default_rng(44)
        x = rng.normal(size=(80, 64))
        labels = np.array(runner.CLASSES * 20)
        membership = np.repeat(np.arange(5), 16)
        model, p, tr, va = runner.fit_fold(x, labels, membership, 0)
        perturbed = x.copy()
        perturbed[va] += 10000
        changed_labels = labels.copy()
        changed_labels[va] = "sad"
        other, _, _, _ = runner.fit_fold(perturbed, changed_labels, membership, 0)
        np.testing.assert_array_equal(model[0].mean_, other[0].mean_)
        np.testing.assert_array_equal(model[0].scale_, other[0].scale_)
        np.testing.assert_array_equal(model[-1].coef_, other[-1].coef_)
        np.testing.assert_array_equal(model[-1].intercept_, other[-1].intercept_)
        np.testing.assert_allclose(model[0].mean_, x[tr].mean(axis=0), rtol=0, atol=1e-14)
        self.assertEqual(p.shape, (16, 4))
        np.testing.assert_allclose(p.sum(axis=1), 1, atol=1e-12)

    def test_corrections_breakages_and_common_errors_are_distinct(self):
        y = np.array(["angry", "happy", "neutral", "sad", "neutral"])
        candidate = np.array(["angry", "happy", "sad", "angry", "sad"])
        reference = np.array(["angry", "angry", "neutral", "happy", "sad"])
        r = paired_counts(y, candidate, reference)
        self.assertEqual(r["corrections"], 1)
        self.assertEqual(r["breakages"], 1)
        self.assertEqual(r["common_errors"], 2)
        self.assertEqual(r["common_errors_same_prediction"], 1)
        self.assertEqual(r["common_errors_different_prediction"], 1)
        self.assertEqual(r["both_correct"], 1)
        self.assertEqual(r["prediction_disagreements"], 3)
        self.assertEqual(r["error_jaccard"], 0.5)


if __name__ == "__main__":
    unittest.main()
