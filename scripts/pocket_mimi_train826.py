#!/usr/bin/env python3
"""Frozen train826 extraction and PRIMARY_CV; packaged by the allowlist builder."""
import base64
import gzip
import hashlib
import io
import json
import math
import os
import platform
import resource
import subprocess
import sys
import tempfile
import time
import tomllib
import warnings
from pathlib import Path

AUTHORITY = {}  # populated by prepare_pocket_mimi_train826.py
MISSION = "RS-DEFHS-POCKET-MIMI-REPRESENTATION-001"
POCKET_COMMIT = "3dbee45d343d7dddd0d105468d17f8dcba14db3e"
CONFIG_BLOB = "fd7205053ffac3e60cb08423f760707b67de5679"
MIMI_BLOB = "2656cd57f5516ad54cbe56abdd93a42482ed2388"
HF_REPO = "kyutai/pocket-tts"
HF_REVISION = "983151f13aaeab1b13c1e5e3c2c383d49a9edf3f"
HF_FILENAME = "languages/english_2026-09/model.safetensors"
CHECKPOINT_SHA256 = "fb0dc01b0d4d2e1c905b7a3e0676e3d9c96d5ae460e24e3ab94981805babf997"
PREFLIGHT_SCRIPT_SHA256 = "de06571b0e206db519c25be1b8a550c6d1391c29cd381cf582e1788936ee6d81"
FOLDS_SHA256 = "87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b"
CLASSES = ["angry", "happy", "neutral", "sad"]
FEATURE_COLUMNS = [f"f{i:02d}" for i in range(64)]
SEED = 20261007
REPEAT_TOL = 1e-7
OUT = Path("/kaggle/working/rs_defhs_pocket_mimi_train826_001")
STAGE = "INITIALIZATION"


class ProtocolError(RuntimeError):
    """Messages are authored in this script and contain no credential values."""


def require(condition, message):
    if not bool(condition):
        raise ProtocolError(message)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def ids_sha256(ids):
    return hashlib.sha256("".join(f"{int(i)}\n" for i in ids).encode()).hexdigest()


def stage(name):
    global STAGE
    STAGE = name
    print(f"STAGE={name}", flush=True)


def load_authority():
    import pandas as pd
    require(bool(AUTHORITY), "Use the generated canonical Kaggle script, not the template")
    tables = {}
    for name, item in AUTHORITY["inputs"].items():
        raw = gzip.decompress(base64.b64decode(item["gzip_b64"]))
        require(hashlib.sha256(raw).hexdigest() == item["sha256"], f"Input hash mismatch: {name}")
        tables[name] = raw
    require(AUTHORITY["inputs"]["VALIDATION_VB_FOLDS.csv"]["sha256"] == FOLDS_SHA256,
            "PRIMARY_CV membership authority mismatch")
    folds = pd.read_csv(io.BytesIO(tables["VALIDATION_VB_FOLDS.csv"]), dtype={"duplicate_group": str})
    manifest = pd.read_csv(io.BytesIO(tables["TRAIN_WAV_MANIFEST.csv"]))
    preflight = json.loads(tables["PREFLIGHT.json"])
    pre_rows = pd.read_csv(io.BytesIO(tables["PREFLIGHT_ROWS.csv"]))
    require(preflight["status"] == "PASS", "Accepted preflight missing")
    require(preflight["checkpoint"]["sha256"] == CHECKPOINT_SHA256, "Accepted checkpoint hash mismatch")
    require(preflight["checkpoint"]["revision_resolved"] == HF_REVISION, "Accepted revision mismatch")
    require(tables["SCRIPT_SHA256.txt"].decode().split()[0] == PREFLIGHT_SCRIPT_SHA256,
            "Accepted preflight script hash mismatch")
    require(len(folds) == 826 and folds.Id.nunique() == 826, "Membership must have 826 unique IDs")
    require(set(folds.fold) == set(range(5)), "Membership must contain the existing five folds")
    require(folds.groupby("duplicate_group").fold.nunique().max() == 1, "Duplicate family crosses folds")
    require(len(manifest) == 826 and manifest.Id.nunique() == 826, "Train manifest identity invalid")
    require(set(manifest.split) == {"train"}, "Nontraining data in execution package")
    folds = folds.sort_values("Id").reset_index(drop=True)
    manifest = manifest.set_index("Id").loc[folds.Id].reset_index()
    require(folds.filename.equals(manifest.filename), "Manifest filename alignment mismatch")
    require(folds.emotion.equals(manifest.emotion), "Manifest label alignment mismatch")
    require(set(folds.emotion) == set(CLASSES), "Training labels invalid")
    require((manifest.channels == 1).all(), "Frozen preflight inputs must already be mono")
    require(len(pre_rows) == 8 and pre_rows.Id.nunique() == 8, "Preflight reference coverage invalid")
    return folds, manifest, preflight, pre_rows


def validate_features(features, folds):
    import numpy as np
    require(len(features) == 826 and features.Id.nunique() == 826, "Feature IDs missing or duplicated")
    require(features.Id.tolist() == folds.Id.tolist(), "Feature ID order/membership mismatch")
    require(features.filename.tolist() == folds.filename.tolist(), "Feature filename mapping mismatch")
    require(features.emotion.tolist() == folds.emotion.tolist(), "Feature labels misaligned")
    actual = [c for c in features if c.startswith("f") and c[1:].isdigit()]
    require(actual == FEATURE_COLUMNS, "Exactly 64 ordered feature columns are required")
    x = features[FEATURE_COLUMNS].to_numpy(dtype=np.float64)
    require(x.shape == (826, 64) and np.isfinite(x).all(), "Feature matrix shape/nonfinite failure")
    return x


def fit_fold(x, labels, membership, fold):
    import numpy as np
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from threadpoolctl import threadpool_limits
    tr = np.asarray(membership) != fold
    va = ~tr
    require(set(np.asarray(labels)[tr]) == set(CLASSES), "Training fold misses a class")
    model = make_pipeline(StandardScaler(), LogisticRegression(
        penalty="l2", C=1.0, solver="lbfgs", max_iter=5000, random_state=SEED))
    with warnings.catch_warnings(), threadpool_limits(limits=1):
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(x[tr], np.asarray(labels)[tr])
        p = model.predict_proba(x[va])
    require(list(model.classes_) == CLASSES, "Classifier probability class order mismatch")
    require(np.isfinite(p).all() and (p >= 0).all() and (p <= 1).all(), "Invalid probabilities")
    require(np.allclose(p.sum(1), 1, rtol=0, atol=1e-10), "Probability normalization failure")
    return model, p, tr, va


def metrics(y, pred):
    from sklearn.metrics import confusion_matrix, f1_score
    per = f1_score(y, pred, labels=CLASSES, average=None, zero_division=0)
    return {"macro_f1": float(per.mean()),
            "per_class_f1": dict(zip(CLASSES, map(float, per))),
            "confusion_matrix": confusion_matrix(y, pred, labels=CLASSES).tolist(),
            "confusion_matrix_class_order": CLASSES}


def evaluate(features, folds, out):
    import numpy as np
    import sklearn
    x = validate_features(features, folds)
    y = folds.emotion.to_numpy()
    membership = folds.fold.to_numpy()
    p = np.full((826, 4), np.nan)
    seen = np.zeros(826, dtype=int)
    records = []
    for fold in range(5):
        started = time.perf_counter()
        model, q, tr, va = fit_fold(x, y, membership, fold)
        require(not set(folds.duplicate_group[tr]) & set(folds.duplicate_group[va]),
                "Duplicate-family leakage in frozen split")
        p[va] = q
        seen[va] += 1
        record = {"fold": fold, "train_rows": int(tr.sum()), "validation_rows": int(va.sum()),
                  "train_ids_sha256": ids_sha256(folds.Id[tr]),
                  "validation_ids_sha256": ids_sha256(folds.Id[va]),
                  "train_validation_ids_disjoint": True, "duplicate_families_disjoint": True,
                  "fit_seconds": time.perf_counter() - started,
                  "iterations": model[-1].n_iter_.tolist(),
                  **metrics(y[va], np.array(CLASSES)[q.argmax(1)])}
        records.append(record)
        print(f"PRIMARY_CV_FOLD={fold} macro_f1={record['macro_f1']:.12g}", flush=True)
    require((seen == 1).all() and np.isfinite(p).all(), "OOF coverage failure")
    pred = np.array(CLASSES)[p.argmax(1)]
    oof = folds[["Id", "filename", "emotion", "duplicate_group", "fold"]].copy()
    oof["pred"] = pred
    for i, cls in enumerate(CLASSES):
        oof[f"p_{cls}"] = p[:, i]
    oof.to_csv(out / "POCKET_MIMI_OOF_PRIMARY_CV.csv", index=False, float_format="%.17g")
    result = {"mission": MISSION, "status": "COMPLETE", "primary_cv": "historical V-B",
              "membership_sha256": FOLDS_SHA256, "split_seed": 20260930,
              "representation": "POCKET_MIMI_CONTINUOUS_MEANSTD", "feature_dim": 64,
              "classifier": {"scaler": "StandardScaler fitted on training fold only",
                             "type": "multinomial L2 LogisticRegression", "C": 1.0,
                             "solver": "lbfgs", "max_iter": 5000, "random_state": SEED,
                             "class_weight": None, "fit_intercept": True},
              **metrics(y, pred), "fold_macro_f1": [r["macro_f1"] for r in records],
              "fold_records": records, "oof_rows": 826,
              "oof_sha256": sha256(out / "POCKET_MIMI_OOF_PRIMARY_CV.csv"),
              "incumbent_reference_macro_f1": AUTHORITY["incumbent_scores"],
              "delta_vs_incumbent_references": {
                  k: metrics(y, pred)["macro_f1"] - v for k, v in AUTHORITY["incumbent_scores"].items()},
              "sklearn_version": sklearn.__version__, "uncertainty": "NOT_PRESCRIBED_FOR_THIS_MISSION",
              "hyperparameter_search": False, "fusion_run": False,
              "protected_validation_queried": False, "target209_run": False, "submission": False}
    dump(out / "PRIMARY_CV_RESULTS.json", result)
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stage("DEPENDENCIES")
    # Same direct source-import solution as the accepted preflight.
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--no-cache-dir",
        "pydantic>=2", "sentencepiece>=0.2.1", "tokenizers>=0.21", "safetensors>=0.4.0",
        "typer>=0.10.0", "typing_extensions>=4.10.0", "fastapi>=0.100", "uvicorn>=0.13.0",
        "python-multipart>=0.0.21", "scipy>=1.5.0", "einops>=0.4.0", "huggingface_hub>=0.34,<1.0",
        "hf_xet", "requests>=2.20.0", "PyYAML>=6.0", "soundfile>=0.12.0", "scikit-learn==1.7.2"])
    import numpy as np
    import pandas as pd
    import torch
    import safetensors.torch
    from huggingface_hub import HfApi, hf_hub_download
    from packaging.version import Version
    stage("TRAIN_ONLY_AUTHORITY")
    folds, manifest, preflight, pre_rows = load_authority()
    # Discover only train.csv/train; never read test.csv or any target WAV.
    roots = [p.parent for p in Path("/kaggle/input").rglob("train.csv")
             if "dataverse-detecting-emotions-from-hindi-speech" in str(p)
             and (p.parent / "train").is_dir()]
    require(len(roots) == 1, "Expected exactly one DEFHS training mount")
    root = roots[0]
    train = pd.read_csv(root / "train.csv").sort_values("Id").reset_index(drop=True)
    require(len(train) == 826 and train.Id.nunique() == 826, "Training population invalid")
    for col in ["Id", "filename", "emotion"]:
        require(train[col].tolist() == folds[col].tolist(), f"Frozen training membership mismatch: {col}")
    paths = []
    for r in manifest.itertuples(index=False):
        path = root / "train" / str(r.filename)
        require(path.resolve().is_relative_to((root / "train").resolve()), "WAV path escapes training directory")
        require(path.is_file() and sha256(path) == r.file_sha256, f"WAV identity mismatch for training Id={r.Id}")
        paths.append(path)
    stage("PINNED_SOURCE_CHECKOUT")
    scratch = Path(tempfile.mkdtemp(prefix="pocket_mimi_train826_", dir="/tmp"))
    source = scratch / "pocket_tts_src"
    subprocess.check_call(["git", "clone", "--quiet", "https://github.com/kyutai-labs/pocket-tts.git", str(source)])
    subprocess.check_call(["git", "-C", str(source), "checkout", "--quiet", "--detach", POCKET_COMMIT])
    require(subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() == POCKET_COMMIT,
            "Pocket-TTS source commit mismatch")
    require(not subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"], text=True).strip(),
            "Pinned source is dirty")
    require(tomllib.loads((source / "pyproject.toml").read_text())["project"]["version"] == "3.3.0", "Version mismatch")
    for name, expected in [("pocket_tts/config/english_2026-09.yaml", CONFIG_BLOB),
                           ("pocket_tts/models/mimi.py", MIMI_BLOB)]:
        actual = subprocess.check_output(["git", "-C", str(source), "hash-object", str(source / name)], text=True).strip()
        require(actual == expected, f"Pinned source blob mismatch: {name}")
    sys.path.insert(0, str(source))
    from pocket_tts.data.audio import audio_read
    from pocket_tts.data.audio_utils import convert_audio
    from pocket_tts.models.mimi import build_mimi
    from pocket_tts.utils.config import load_config
    require(Version(torch.__version__.split("+")[0]) >= Version("2.5.0"), "Pocket-TTS requires torch>=2.5.0")
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True, warn_only=True)
    config = load_config(source / "pocket_tts/config/english_2026-09.yaml")
    require(str(config.weights_path) == f"hf://{HF_REPO}/{HF_FILENAME}@{HF_REVISION}", "Config checkpoint mismatch")
    require(int(config.mimi.sample_rate) == 24000 and int(config.mimi.inner_dim) == 32
            and float(config.mimi.frame_rate) == 12.5, "Frozen representation config mismatch")
    stage("GATED_CHECKPOINT_ACCESS")
    os.environ["HF_HOME"] = str(scratch / "hf_home")
    try:
        from kaggle_secrets import UserSecretsClient
        token = UserSecretsClient().get_secret("HF_TOKEN")
        require(bool(token), "HF_TOKEN is unavailable")
        info = HfApi().model_info(HF_REPO, revision=HF_REVISION, token=token)
        checkpoint = Path(hf_hub_download(repo_id=HF_REPO, filename=HF_FILENAME,
                                          revision=HF_REVISION, token=token, cache_dir=str(scratch / "hf_cache")))
    except Exception:
        raise ProtocolError("ACCESS_SETUP: authorized Kaggle HF_TOKEN or gated checkpoint access unavailable") from None
    require(info.sha == HF_REVISION, "Resolved gated revision mismatch")
    require(checkpoint.stat().st_size == 219029196 and sha256(checkpoint) == CHECKPOINT_SHA256,
            "Authorized checkpoint binary identity mismatch")
    del token
    stage("ENCODER_VALIDATION")
    started = time.perf_counter()
    bundle = safetensors.torch.load_file(str(checkpoint), device="cpu")
    state = {k.removeprefix("mimi."): v for k, v in bundle.items() if k.startswith("mimi.")}
    enc = [v for k, v in state.items() if k.startswith("encoder.")]
    require(len(enc) == 22, "Encoder tensor count mismatch")
    numel = sum(v.numel() for v in enc)
    nonzero = sum(int(torch.count_nonzero(v).item()) for v in enc)
    encoder_max = max(float(v.abs().max().item()) for v in enc)
    encoder_mean = sum(float(v.double().sum().item()) for v in enc) / numel
    encoder_std = math.sqrt(max(0.0, sum(float((v.double() ** 2).sum().item()) for v in enc) / numel - encoder_mean ** 2))
    require(numel == 2927136 and nonzero == numel and encoder_max == 3.5625 and encoder_std > 0,
            "Authorized encoder is degenerate or differs from accepted checkpoint")
    mimi = build_mimi(config.mimi).to("cpu")
    missing, unexpected = mimi.load_state_dict(state, strict=True)
    require(not missing and not unexpected, "Strict Mimi load failed")
    mimi.eval()
    for p in mimi.parameters():
        p.requires_grad_(False)
    model_load_seconds = time.perf_counter() - started
    del bundle, state, enc
    t = torch.arange(48000, dtype=torch.float32) / 24000
    synthetic = (0.30 * torch.sin(2 * math.pi * 220 * t) + 0.15 * torch.sin(2 * math.pi * 440 * t)).reshape(1, 1, -1)
    with torch.inference_mode():
        latent = mimi.encode_to_latent(synthetic)
    require(list(latent.shape) == [1, 25, 32] and torch.isfinite(latent).all() and latent.std(correction=0) > 0,
            "Synthetic latent smoke test failed")

    def extract(index):
        started = time.perf_counter()
        wav, sr = audio_read(paths[index])
        m = manifest.iloc[index]
        require(wav.ndim == 2 and wav.shape[0] == 1, "Frozen mono WAV shape mismatch")
        require(int(sr) == int(m.sample_rate) and wav.shape[-1] == int(m.samples), "WAV manifest format mismatch")
        wav24 = convert_audio(wav, sr, 24000, 1)
        x = wav24.unsqueeze(0).to(torch.float32)
        require(x.shape[:2] == (1, 1) and torch.isfinite(x).all(), "Invalid preprocessed WAV")
        encode_start = time.perf_counter()
        with torch.inference_mode():
            z = mimi.encode_to_latent(x)
        encode_seconds = time.perf_counter() - encode_start
        require(z.ndim == 3 and z.shape[0] == 1 and z.shape[1] > 0 and z.shape[2] == 32,
                "Latent must have shape [1,T,32]")
        require(torch.isfinite(z).all(), "Nonfinite latents")
        f = torch.cat([z.mean(dim=1), z.std(dim=1, correction=0)], dim=1).squeeze(0).cpu().numpy().astype(np.float64)
        require(f.shape == (64,) and np.isfinite(f).all(), "Nonfinite/invalid pooled features")
        return f, {"Id": int(m.Id), "filename": str(m.filename), "wav_sha256": str(m.file_sha256),
                   "source_sr": int(sr), "samples_24k": int(wav24.shape[-1]), "latent_frames": int(z.shape[1]),
                   "encode_seconds": encode_seconds, "end_to_end_seconds": time.perf_counter() - started}

    stage("TRAIN826_EXTRACTION")
    x = np.empty((826, 64), dtype=np.float64)
    rows = []
    started = time.perf_counter()
    for i in range(826):
        x[i], record = extract(i)
        rows.append(record)
        if (i + 1) % 25 == 0 or i == 825:
            print(f"TRAIN826_ROWS_COMPLETE={i + 1}/826", flush=True)
    extraction_seconds = time.perf_counter() - started
    stage("DETERMINISM_AND_FEATURE_VALIDATION")
    checks = []
    for r in pre_rows.itertuples(index=False):
        i = int(np.flatnonzero(folds.Id.to_numpy() == r.Id)[0])
        reference = np.array([getattr(r, c) for c in FEATURE_COLUMNS], dtype=np.float64)
        require(rows[i]["wav_sha256"] == r.wav_sha256, "Accepted preflight WAV identity mismatch")
        reference_diff = float(np.max(np.abs(x[i] - reference)))
        repeated, repeated_meta = extract(i)
        repeat_diff = float(np.max(np.abs(x[i] - repeated)))
        require(reference_diff <= REPEAT_TOL and repeat_diff <= REPEAT_TOL, "Extraction reproducibility failed")
        require(repeated_meta["wav_sha256"] == rows[i]["wav_sha256"], "Repeated WAV identity mismatch")
        checks.append({"Id": int(r.Id), "vs_accepted_preflight_max_abs_diff": reference_diff,
                       "repeat_max_abs_diff": repeat_diff, "tolerance": REPEAT_TOL})
    features = folds[["Id", "filename", "emotion"]].copy()
    features[FEATURE_COLUMNS] = x
    validate_features(features, folds)
    features.to_csv(OUT / "TRAIN826_FEATURES.csv", index=False, float_format="%.17g")
    np.savez_compressed(OUT / "TRAIN826_FEATURES.npz", Id=folds.Id.to_numpy(), X=x,
                        feature_columns=np.array(FEATURE_COLUMNS), emotion=folds.emotion.to_numpy(dtype=str))
    pd.DataFrame(rows).to_csv(OUT / "TRAIN826_WAV_PROVENANCE.csv", index=False, float_format="%.17g")
    dump(OUT / "FEATURE_VALIDATION.json", {"status": "PASS", "rows": 826, "unique_ids": 826,
        "feature_columns": FEATURE_COLUMNS, "finite": True, "all_source_wav_hashes_verified": True,
        "deterministic": True, "repeat_checks": checks, "membership_sha256": FOLDS_SHA256,
        "checkpoint_sha256": CHECKPOINT_SHA256})
    provenance = {"mission": MISSION, "status": "COMPLETE", "source_commit": POCKET_COMMIT,
        "pocket_tts_version": "3.3.0", "source_clean": True, "config_git_blob": CONFIG_BLOB,
        "mimi_git_blob": MIMI_BLOB, "checkpoint_repo": HF_REPO, "checkpoint_revision": info.sha,
        "checkpoint_path": HF_FILENAME, "checkpoint_sha256": CHECKPOINT_SHA256,
        "checkpoint_bytes": 219029196, "strict_state_load": True, "encoder_max": encoder_max,
        "encoder_std": encoder_std, "encoder_valid": True, "latent_dim": 32, "feature_dim": 64,
        "sample_rate_hz": 24000, "channels": 1, "frame_rate_hz": 12.5,
        "pooling": "temporal mean + population std (correction=0)", "device": "cpu",
        "torch_threads": 1, "torch": torch.__version__, "numpy": np.__version__, "pandas": pd.__version__,
        "python": sys.version, "platform": platform.platform(), "model_load_seconds": model_load_seconds,
        "extraction_seconds": extraction_seconds,
        "mean_encode_seconds_per_wav": float(np.mean([r["encode_seconds"] for r in rows])),
        "peak_memory_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0,
        "script_sha256": sha256(Path(__file__)), "feature_csv_sha256": sha256(OUT / "TRAIN826_FEATURES.csv"),
        "feature_npz_sha256": sha256(OUT / "TRAIN826_FEATURES.npz"), "authority": {
            k: {j: v for j, v in item.items() if j != "gzip_b64"} for k, item in AUTHORITY["inputs"].items()},
        "text_invoked": False, "tts_generation_invoked": False, "voice_conditioning_invoked": False,
        "protected_validation_queried": False, "target209_run": False, "submission": False}
    dump(OUT / "TRAIN826_PROVENANCE.json", provenance)
    (OUT / "CHECKPOINT_SHA256.txt").write_text(f"{CHECKPOINT_SHA256}  {HF_FILENAME}\n")
    (OUT / "SCRIPT_SHA256.txt").write_text(f"{sha256(Path(__file__))}  {Path(__file__).name}\n")
    stage("FROZEN_PRIMARY_CV")
    result = evaluate(features, folds, OUT)
    dump(OUT / "EXECUTION_STATUS.json", {"mission": MISSION, "status": "COMPLETE_TRAIN826_AND_PRIMARY_CV",
        "train826_extraction_status": "COMPLETE", "primary_cv_status": "COMPLETE",
        "complementarity_status": "PENDING_BOUNDED_ANALYSIS_OF_VALID_OOF",
        "target209_authorization_status": "NOT_AUTHORIZED", "target209_run": False,
        "fusion_run": False, "protected_validation_queried": False, "submission": False})
    files = {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(OUT.iterdir()) if p.is_file()}
    dump(OUT / "ARTIFACT_MANIFEST.json", {"mission": MISSION, "files": files})
    print(f"POCKET_MIMI_TRAIN826=PASS OOF_MACRO_F1={result['macro_f1']:.12g}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        OUT.mkdir(parents=True, exist_ok=True)
        # Do not serialize arbitrary exception strings: hub/secret errors may contain credentials.
        dump(OUT / "EXECUTION_FAILURE.json", {"mission": MISSION, "status": "ERROR", "stage": STAGE,
             "exception_type": type(error).__name__, "automatic_rerun": False,
             "detail": str(error) if isinstance(error, ProtocolError) else "See the failure stage; arbitrary exception text is withheld to protect credentials.",
             "scientific_or_numerical_failure": STAGE in {"ENCODER_VALIDATION", "TRAIN826_EXTRACTION",
                 "DETERMINISM_AND_FEATURE_VALIDATION", "FROZEN_PRIMARY_CV"}, "target209_run": False,
             "protected_validation_queried": False, "submission": False})
        print(f"POCKET_MIMI_TRAIN826=ERROR stage={STAGE} type={type(error).__name__}", flush=True)
        raise SystemExit(1) from None
