#!/usr/bin/env python3
"""Descriptive paired train-OOF audit after valid standalone execution; no fusion."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pocket_mimi_train826 import CLASSES, FOLDS_SHA256, ProtocolError, dump, metrics, require, sha256

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/RS-DEFHS-POCKET-MIMI-REPRESENTATION-001"
REFERENCE_HASHES = {
    "Fixed waveform pair": "9f9ac86829230bcfde4be93a980161bf6139eaa38f3372efc822eb8edf79da45",
    "System1 emotion2vec": "14c86f6f61d633a72fd8535bec1070162e8a92f6de9c3f37ee366ff0e3d7a7b7"}
REFERENCE_SCORES = {"System C": 0.8135577912484513, "Fixed waveform pair": 0.7768156647359765,
                    "System1 emotion2vec": 0.7383745765682462}
REFERENCE_C_FOLDS = [0.7548722211207533, 0.812367374005305, 0.8494805998899284,
                     0.8250607090820787, 0.8255294348949557]


def aligned_csv(path, folds):
    d = pd.read_csv(path).sort_values("Id").reset_index(drop=True)
    require(len(d) == 826 and d.Id.nunique() == 826, "OOF must have 826 unique training IDs")
    for col in ["Id", "emotion", "fold"]:
        require(d[col].tolist() == folds[col].tolist(), f"OOF alignment failure: {col}")
    p = d[["p_" + c for c in CLASSES]].to_numpy(float)
    require(np.isfinite(p).all() and (p >= 0).all() and (p <= 1).all(), "Nonfinite/invalid OOF probabilities")
    require(np.allclose(p.sum(1), 1, rtol=0, atol=1e-8), "Invalid probability normalization")
    require(d.pred.tolist() == np.array(CLASSES)[p.argmax(1)].tolist(), "OOF labels disagree with probabilities")
    return d


def paired_counts(y, candidate, reference):
    y, candidate, reference = np.asarray(y), np.asarray(candidate), np.asarray(reference)
    cw, rw = candidate != y, reference != y
    common = cw & rw
    union = cw | rw
    return {"rows": len(y), "candidate_errors": int(cw.sum()), "reference_errors": int(rw.sum()),
            "corrections": int((~cw & rw).sum()), "breakages": int((cw & ~rw).sum()),
            "net_corrections": int((~cw & rw).sum() - (cw & ~rw).sum()),
            "both_correct": int((~cw & ~rw).sum()), "common_errors": int(common.sum()),
            "common_errors_same_prediction": int((common & (candidate == reference)).sum()),
            "common_errors_different_prediction": int((common & (candidate != reference)).sum()),
            "error_union": int(union.sum()),
            "error_jaccard": float(common.sum() / union.sum()) if union.any() else 0.0,
            "prediction_disagreements": int((candidate != reference).sum())}


def analyze(folds, candidate, references):
    y = folds.emotion.to_numpy()
    pred = candidate.pred.to_numpy()
    result = {}
    for name, ref in references.items():
        base = np.asarray(ref)
        overall = paired_counts(y, pred, base)
        overall["candidate_metrics"] = metrics(y, pred)
        overall["reference_metrics"] = metrics(y, base)
        overall["standalone_macro_f1_difference"] = metrics(y, pred)["macro_f1"] - metrics(y, base)["macro_f1"]
        overall["per_class"] = {c: paired_counts(y[y == c], pred[y == c], base[y == c]) for c in CLASSES}
        per_fold = []
        for f in range(5):
            mask = folds.fold.to_numpy() == f
            per_fold.append({"fold": f, **paired_counts(y[mask], pred[mask], base[mask]),
                "candidate_macro_f1": metrics(y[mask], pred[mask])["macro_f1"],
                "reference_macro_f1": metrics(y[mask], base[mask])["macro_f1"]})
        overall["per_fold"] = per_fold
        overall["folds_with_positive_net_corrections"] = sum(r["net_corrections"] > 0 for r in per_fold)
        overall["folds_with_better_standalone_macro_f1"] = sum(
            r["candidate_macro_f1"] > r["reference_macro_f1"] for r in per_fold)
        result[name] = overall
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-output", type=Path, required=True)
    parser.add_argument("--system-c-oof", type=Path, required=True)
    parser.add_argument("--system-c-sha256", required=True,
                        help="Trusted checksum from the canonical System C artifact authority, not inferred from scores")
    parser.add_argument("--fixed-pair-npz", type=Path, required=True)
    parser.add_argument("--emotion2vec-npz", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    fold_path = ROOT / "runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VB_FOLDS.csv"
    require(sha256(fold_path) == FOLDS_SHA256, "Frozen fold authority mismatch")
    folds = pd.read_csv(fold_path).sort_values("Id").reset_index(drop=True)
    root = args.candidate_output
    execution = json.loads((root / "EXECUTION_STATUS.json").read_text())
    require(execution["status"] == "COMPLETE_TRAIN826_AND_PRIMARY_CV", "Valid standalone execution required first")
    validated = json.loads((root / "FEATURE_VALIDATION.json").read_text())
    require(validated["status"] == "PASS" and validated["deterministic"], "Valid deterministic extraction required first")
    inv = json.loads((root / "ARTIFACT_MANIFEST.json").read_text())["files"]
    for name in ["POCKET_MIMI_OOF_PRIMARY_CV.csv", "PRIMARY_CV_RESULTS.json", "TRAIN826_PROVENANCE.json",
                 "FEATURE_VALIDATION.json", "EXECUTION_STATUS.json"]:
        require(sha256(root / name) == inv[name]["sha256"], f"Candidate artifact hash mismatch: {name}")
    provenance = json.loads((root / "TRAIN826_PROVENANCE.json").read_text())
    package = json.loads((RUN / "PHASE1_EXECUTION_PACKAGE.json").read_text())
    require(provenance["script_sha256"] == package["script_sha256"], "Candidate execution code mismatch")
    candidate = aligned_csv(root / "POCKET_MIMI_OOF_PRIMARY_CV.csv", folds)
    recorded = json.loads((root / "PRIMARY_CV_RESULTS.json").read_text())
    require(abs(metrics(folds.emotion, candidate.pred)["macro_f1"] - recorded["macro_f1"]) < 1e-14,
            "Candidate score replay failure")
    require(len(args.system_c_sha256) == 64 and sha256(args.system_c_oof) == args.system_c_sha256,
            "System C authoritative row-level checksum mismatch")
    c = aligned_csv(args.system_c_oof, folds)
    require(abs(metrics(folds.emotion, c.pred)["macro_f1"] - REFERENCE_SCORES["System C"]) < 1e-14,
            "System C reference score replay failure")
    for f, expected in enumerate(REFERENCE_C_FOLDS):
        mask = folds.fold == f
        require(abs(metrics(folds.emotion[mask], c.pred[mask])["macro_f1"] - expected) < 1e-14,
                "System C reference fold score replay failure")
    references = {"System C": c.pred.to_numpy()}
    hashes = {"System C": args.system_c_sha256}
    for name, path in [("Fixed waveform pair", args.fixed_pair_npz), ("System1 emotion2vec", args.emotion2vec_npz)]:
        require(sha256(path) == REFERENCE_HASHES[name], f"Reference binary identity mismatch: {name}")
        with np.load(path, allow_pickle=False) as z:
            require(np.array_equal(z["Id"], folds.Id), f"Reference ID alignment failure: {name}")
            p = z["prob"]
            require(p.shape == (826, 4) and np.isfinite(p).all() and (p >= 0).all() and (p <= 1).all()
                    and np.allclose(p.sum(1), 1, rtol=0, atol=1e-8), f"Invalid reference probabilities: {name}")
            pred = np.array(CLASSES)[p.argmax(1)]
        require(abs(metrics(folds.emotion, pred)["macro_f1"] - REFERENCE_SCORES[name]) < 1e-14,
                f"Reference score replay failure: {name}")
        references[name] = pred
        hashes[name] = REFERENCE_HASHES[name]
    args.output.mkdir(parents=True, exist_ok=True)
    row_audit = folds[["Id", "filename", "emotion", "fold"]].copy()
    row_audit["pocket_pred"] = candidate.pred
    for name, pred in references.items():
        stem = {"System C": "system_c", "Fixed waveform pair": "fixed_pair", "System1 emotion2vec": "emotion2vec"}[name]
        row_audit[stem + "_pred"] = pred
        row_audit[stem + "_correction"] = (candidate.pred.to_numpy() == folds.emotion.to_numpy()) & (pred != folds.emotion.to_numpy())
        row_audit[stem + "_breakage"] = (candidate.pred.to_numpy() != folds.emotion.to_numpy()) & (pred == folds.emotion.to_numpy())
    row_audit.to_csv(args.output / "COMPLEMENTARITY_ROWS.csv", index=False)
    dump(args.output / "OOF_COMPLEMENTARITY.json", {"mission": "RS-DEFHS-POCKET-MIMI-REPRESENTATION-001",
        "status": "DESCRIPTIVE_COMPARISONS_COMPLETE_PENDING_SCIENTIFIC_VERDICT",
        "membership_sha256": FOLDS_SHA256, "reference_sha256": hashes,
        "comparisons": analyze(folds, candidate, references),
        "hard_mechanism_analysis": "PENDING_EXISTING_TRAIN_SIDE_DEFINITION; no new cohorts invented",
        "complementarity_verdict": None, "final_verdict": None,
        "target209_authorization_status": "NOT_AUTHORIZED", "target209_run": False,
        "fusion_run": False, "protected_validation_queried": False, "submission": False})


if __name__ == "__main__":
    main()
