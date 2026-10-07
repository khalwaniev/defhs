#!/usr/bin/env python3
import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

OUT = Path("/kaggle/working/rs_defhs_pocket_mimi_preflight_001")
OUT.mkdir(parents=True, exist_ok=True)

POCKET_REPO = "kyutai-labs/pocket-tts"
POCKET_VERSION = "3.3.0"
POCKET_COMMIT = "3dbee45d343d7dddd0d105468d17f8dcba14db3e"
CONFIG_GIT_BLOB = "fd7205053ffac3e60cb08423f760707b67de5679"
MIMI_GIT_BLOB = "2656cd57f5516ad54cbe56abdd93a42482ed2388"

HF_REPO = "kyutai/pocket-tts-without-voice-cloning"
HF_REVISION = "e7205b6ee50e654a5ea19f0e9df2b0813b05e921"
HF_FILENAME = "languages/english_2026-09/model.safetensors"

SAMPLE_RATE = 24000
LATENT_DIM = 32
FEATURE_DIM = 64
REPEAT_TOL = 1e-7
SEED = 20261007

# Keep HF acquisition explicitly public/ungated.
for key in ["HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_TOKEN"]:
    os.environ.pop(key, None)
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["HF_HOME"] = "/kaggle/working/hf_home"

def sha256_file(path: Path, chunk=8*1024*1024):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def git_blob_sha1(path: Path):
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\\0" + b).hexdigest()

def maxrss_mb():
    # Linux ru_maxrss is KiB.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

def find_competition_root():
    roots = []
    for train_csv in Path("/kaggle/input").rglob("train.csv"):
        root = train_csv.parent
        if (root / "train").is_dir() and (root / "test").is_dir() and (root / "test.csv").is_file():
            roots.append(root)
    # Prefer the mounted competition slug if several unrelated train.csv files exist.
    exact = [r for r in roots if "dataverse-detecting-emotions-from-hindi-speech" in str(r)]
    roots = exact or roots
    if len(roots) != 1:
        raise RuntimeError(f"Expected exactly one competition root, found: {[str(x) for x in roots]}")
    return roots[0]

print("INSTALLING_PINNED_POCKET_TTS", flush=True)
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "--quiet", "--no-cache-dir",
    f"git+https://github.com/{POCKET_REPO}.git@{POCKET_COMMIT}",
    "soundfile>=0.12.0"
])

import numpy as np
import pandas as pd
import torch
import safetensors.torch
import pocket_tts
from huggingface_hub import hf_hub_download
from pocket_tts.data.audio import audio_read
from pocket_tts.data.audio_utils import convert_audio
from pocket_tts.models.mimi import build_mimi
from pocket_tts.utils.config import load_config

np.random.seed(SEED)
torch.manual_seed(SEED)
torch.set_num_threads(1)
try:
    torch.use_deterministic_algorithms(True)
except Exception:
    pass

pkg_version = importlib.metadata.version("pocket-tts")
if pkg_version != POCKET_VERSION:
    raise RuntimeError(f"pocket-tts version mismatch: {pkg_version} != {POCKET_VERSION}")

pkg_dir = Path(pocket_tts.__file__).resolve().parent
config_path = pkg_dir / "config" / "english_2026-09.yaml"
mimi_source_path = pkg_dir / "models" / "mimi.py"
if git_blob_sha1(config_path) != CONFIG_GIT_BLOB:
    raise RuntimeError("Pinned config Git blob mismatch")
if git_blob_sha1(mimi_source_path) != MIMI_GIT_BLOB:
    raise RuntimeError("Pinned Mimi source Git blob mismatch")

print("DOWNLOADING_EXACT_PUBLIC_CHECKPOINT", flush=True)
ckpt = Path(hf_hub_download(
    repo_id=HF_REPO,
    filename=HF_FILENAME,
    revision=HF_REVISION,
))
ckpt_sha256 = sha256_file(ckpt)
ckpt_bytes = ckpt.stat().st_size

config = load_config(config_path)
if int(config.mimi.sample_rate) != SAMPLE_RATE:
    raise RuntimeError(f"Unexpected sample rate: {config.mimi.sample_rate}")
if int(config.mimi.inner_dim) != LATENT_DIM:
    raise RuntimeError(f"Unexpected inner_dim: {config.mimi.inner_dim}")
if float(config.mimi.frame_rate) != 12.5:
    raise RuntimeError(f"Unexpected frame_rate: {config.mimi.frame_rate}")

load_t0 = time.perf_counter()
mimi = build_mimi(config.mimi).to("cpu")
bundle = safetensors.torch.load_file(str(ckpt), device="cpu")
mimi_state = {k.removeprefix("mimi."): v for k, v in bundle.items() if k.startswith("mimi.")}
if not mimi_state:
    raise RuntimeError("Checkpoint contains no mimi.* weights")
missing, unexpected = mimi.load_state_dict(mimi_state, strict=False)
if missing or unexpected:
    raise RuntimeError(f"Mimi state mismatch: missing={missing}, unexpected={unexpected}")
mimi.eval()
model_load_seconds = time.perf_counter() - load_t0
memory_after_model_mb = maxrss_mb()

root = find_competition_root()
train_csv = root / "train.csv"
train_dir = root / "train"
df = pd.read_csv(train_csv)
required = {"Id", "filename", "emotion"}
if not required.issubset(df.columns):
    raise RuntimeError(f"train.csv missing required columns: {required - set(df.columns)}")
if len(df) != 826 or df["Id"].nunique() != 826:
    raise RuntimeError(f"Unexpected train identity: rows={len(df)}, unique_ids={df['Id'].nunique()}")

# Fixed, deterministic technical subset: first two IDs per class.
classes = ["angry", "happy", "neutral", "sad"]
parts = []
for cls in classes:
    z = df[df["emotion"] == cls].sort_values("Id").head(2)
    if len(z) != 2:
        raise RuntimeError(f"Could not select two preflight rows for class {cls}")
    parts.append(z)
sample = pd.concat(parts, ignore_index=True).sort_values("Id").reset_index(drop=True)

def extract_one(row):
    path = train_dir / str(row["filename"])
    if not path.is_file():
        raise FileNotFoundError(path)
    wav_sha = sha256_file(path)
    wav, sr = audio_read(path)
    if wav.ndim != 2:
        raise RuntimeError(f"audio_read shape invalid for {path}: {tuple(wav.shape)}")
    # audio_read already averages multichannel WAVs; convert_audio enforces mono and resamples.
    wav24 = convert_audio(wav, sr, SAMPLE_RATE, 1)
    if wav24.ndim != 2 or wav24.shape[0] != 1:
        raise RuntimeError(f"mono conversion failed for {path}: {tuple(wav24.shape)}")
    x = wav24.unsqueeze(0).to(torch.float32)
    t0 = time.perf_counter()
    with torch.inference_mode():
        latent = mimi.encode_to_latent(x)
    elapsed = time.perf_counter() - t0
    if latent.ndim != 3 or latent.shape[0] != 1 or latent.shape[2] != LATENT_DIM:
        raise RuntimeError(f"latent shape mismatch for {path}: {tuple(latent.shape)}")
    if not torch.isfinite(latent).all():
        raise RuntimeError(f"non-finite latent for {path}")
    mean = latent.mean(dim=1)
    std = latent.std(dim=1, correction=0)
    feat = torch.cat([mean, std], dim=1).squeeze(0).cpu().numpy().astype(np.float64)
    if feat.shape != (FEATURE_DIM,) or not np.isfinite(feat).all():
        raise RuntimeError(f"feature failure for {path}: shape={feat.shape}")
    return {
        "Id": int(row["Id"]),
        "filename": str(row["filename"]),
        "emotion": str(row["emotion"]),
        "source_sr": int(sr),
        "samples_24k": int(wav24.shape[-1]),
        "latent_frames": int(latent.shape[1]),
        "runtime_seconds": float(elapsed),
        "wav_sha256": wav_sha,
        "feature": feat,
    }

rows = []
for _, row in sample.iterrows():
    r = extract_one(row)
    rows.append(r)
    print(
        f"PREFLIGHT_ROW Id={r['Id']} class={r['emotion']} frames={r['latent_frames']} "
        f"runtime={r['runtime_seconds']:.6f}s",
        flush=True,
    )

# Repeat the first row from disk through the full preprocessing+encoder+pooling path.
repeat = extract_one(sample.iloc[0])
repeat_max_abs = float(np.max(np.abs(rows[0]["feature"] - repeat["feature"])))
if repeat["wav_sha256"] != rows[0]["wav_sha256"]:
    raise RuntimeError("Repeated WAV hash mismatch")
if repeat_max_abs > REPEAT_TOL:
    raise RuntimeError(
        f"Repeat extraction mismatch max_abs={repeat_max_abs} > tolerance={REPEAT_TOL}"
    )

runtimes = np.array([r["runtime_seconds"] for r in rows], dtype=float)
median_runtime = float(np.median(runtimes))
mean_runtime = float(np.mean(runtimes))
projected_826_seconds = median_runtime * 826
projected_1035_seconds = median_runtime * 1035
peak_mb = maxrss_mb()

cols = [
    "Id","filename","emotion","source_sr","samples_24k","latent_frames",
    "runtime_seconds","wav_sha256"
] + [f"f{i:02d}" for i in range(FEATURE_DIM)]
with (OUT / "PREFLIGHT_ROWS.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for r in rows:
        w.writerow([
            r["Id"],r["filename"],r["emotion"],r["source_sr"],r["samples_24k"],
            r["latent_frames"],f"{r['runtime_seconds']:.12g}",r["wav_sha256"],
            *[f"{x:.17g}" for x in r["feature"]]
        ])

summary = {
    "mission": "RS-DEFHS-POCKET-MIMI-REPRESENTATION-001",
    "status": "PASS",
    "policy_status": "PASS_EXTERNAL_MODEL_ALLOWED",
    "software": {
        "repo": POCKET_REPO,
        "version": pkg_version,
        "commit": POCKET_COMMIT,
        "config_git_blob_sha1": git_blob_sha1(config_path),
        "mimi_source_git_blob_sha1": git_blob_sha1(mimi_source_path),
    },
    "checkpoint": {
        "repo": HF_REPO,
        "revision": HF_REVISION,
        "filename": HF_FILENAME,
        "sha256": ckpt_sha256,
        "bytes": ckpt_bytes,
        "access_mode": "public_ungated",
    },
    "representation": {
        "name": "POCKET_MIMI_CONTINUOUS_MEANSTD",
        "call": "MimiModel.encode_to_latent only",
        "text_path_invoked": False,
        "tts_generation_invoked": False,
        "voice_cloning_invoked": False,
        "sample_rate_hz": SAMPLE_RATE,
        "latent_dim": LATENT_DIM,
        "frame_rate_hz": 12.5,
        "pooling": "temporal mean + population std (correction=0)",
        "feature_dim": FEATURE_DIM,
    },
    "preflight": {
        "rows": len(rows),
        "ids": [r["Id"] for r in rows],
        "classes": [r["emotion"] for r in rows],
        "all_finite": True,
        "repeat_id": rows[0]["Id"],
        "repeat_max_abs_feature_diff": repeat_max_abs,
        "repeat_tolerance": REPEAT_TOL,
        "runtime_seconds_per_wav": [r["runtime_seconds"] for r in rows],
        "mean_runtime_seconds_per_wav": mean_runtime,
        "median_runtime_seconds_per_wav": median_runtime,
        "projected_826_seconds_from_median": projected_826_seconds,
        "projected_1035_seconds_from_median": projected_1035_seconds,
        "model_build_and_weight_load_seconds": model_load_seconds,
        "peak_memory_mb": peak_mb,
        "memory_after_model_mb": memory_after_model_mb,
    },
    "environment": {
        "python": sys.version,
        "platform": platform.platform(),
        "torch": torch.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "device": "cpu",
        "torch_threads": torch.get_num_threads(),
    },
    "competition_root": str(root),
    "train_rows_verified": int(len(df)),
    "gpu_used": False,
    "kaggle_submission": False,
    "protected_validation_accessed": False,
}
(OUT / "PREFLIGHT.json").write_text(json.dumps(summary, indent=2) + "\n")
(OUT / "CHECKPOINT_SHA256.txt").write_text(f"{ckpt_sha256}  {HF_FILENAME}\n")
(OUT / "SCRIPT_SHA256.txt").write_text(f"{sha256_file(Path(__file__))}  {Path(__file__).name}\n")

print("POCKET_MIMI_PREFLIGHT=PASS", flush=True)
print(json.dumps(summary, indent=2), flush=True)
