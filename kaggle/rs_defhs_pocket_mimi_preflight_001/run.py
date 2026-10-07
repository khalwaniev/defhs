#!/usr/bin/env python3
import csv
import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
import tomllib
from pathlib import Path

OUT = Path("/kaggle/working/rs_defhs_pocket_mimi_preflight_001")
OUT.mkdir(parents=True, exist_ok=True)

MISSION = "RS-DEFHS-POCKET-MIMI-REPRESENTATION-001"

POCKET_REPO = "kyutai-labs/pocket-tts"
POCKET_VERSION = "3.3.0"
POCKET_COMMIT = "3dbee45d343d7dddd0d105468d17f8dcba14db3e"
CONFIG_GIT_BLOB = "fd7205053ffac3e60cb08423f760707b67de5679"
MIMI_GIT_BLOB = "2656cd57f5516ad54cbe56abdd93a42482ed2388"

HF_REPO = "kyutai/pocket-tts"
HF_REVISION = "983151f13aaeab1b13c1e5e3c2c383d49a9edf3f"
HF_FILENAME = "languages/english_2026-09/model.safetensors"
EXPECTED_CONFIG_WEIGHTS = (
    "hf://kyutai/pocket-tts/languages/english_2026-09/"
    "model.safetensors@983151f13aaeab1b13c1e5e3c2c383d49a9edf3f"
)

SAMPLE_RATE = 24000
LATENT_DIM = 32
FEATURE_DIM = 64
FRAME_RATE = 12.5
REPEAT_TOL = 1e-7
SEED = 20261007

os.environ["HF_HOME"] = "/kaggle/working/hf_home"

def sha256_file(path: Path, chunk=8 * 1024 * 1024):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def maxrss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

def write_json(name, payload):
    (OUT / name).write_text(json.dumps(payload, indent=2) + "\n")

def stop_access_setup(reason, detail):
    payload = {
        "mission": MISSION,
        "status": "ACCESS_SETUP_BLOCKER",
        "reason": reason,
        "detail": detail,
        "checkpoint_repo": HF_REPO,
        "checkpoint_revision": HF_REVISION,
        "checkpoint_path": HF_FILENAME,
        "required_action": (
            "Accept the Kyutai gated model conditions on Hugging Face and make an "
            "authorized read token available to this Kaggle kernel as secret HF_TOKEN. "
            "Do not paste the token into code or logs."
        ),
        "checkpoint_downloaded": False,
        "competition_audio_processed": False,
        "primary_cv_run": False,
        "target209_run": False,
        "gpu_used": False,
        "submission": False,
    }
    write_json("ACCESS_SETUP_BLOCKER.json", payload)
    print("POCKET_MIMI_PREFLIGHT=ACCESS_SETUP_BLOCKER", flush=True)
    print(json.dumps(payload, indent=2), flush=True)
    raise SystemExit(0)

def get_hf_token():
    for key in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_TOKEN"):
        value = os.environ.get(key)
        if value:
            return value, f"environment:{key}"
    try:
        from kaggle_secrets import UserSecretsClient
        value = UserSecretsClient().get_secret("HF_TOKEN")
        if value:
            return value, "kaggle_secret:HF_TOKEN"
    except Exception:
        pass
    return None, None

def find_competition_root():
    roots = []
    for train_csv in Path("/kaggle/input").rglob("train.csv"):
        root = train_csv.parent
        if (root / "train").is_dir() and (root / "test").is_dir() and (root / "test.csv").is_file():
            roots.append(root)
    exact = [r for r in roots if "dataverse-detecting-emotions-from-hindi-speech" in str(r)]
    roots = exact or roots
    if len(roots) != 1:
        raise RuntimeError(
            f"Expected exactly one DEFHS competition root; found {[str(x) for x in roots]}"
        )
    return roots[0]

print("STAGE=PINNED_SOURCE_CHECKOUT", flush=True)
source_root = Path("/kaggle/working/pocket_tts_src")
if source_root.exists():
    subprocess.check_call(["rm", "-rf", str(source_root)])

subprocess.check_call([
    "git", "clone", "--quiet",
    f"https://github.com/{POCKET_REPO}.git",
    str(source_root),
])
subprocess.check_call([
    "git", "-C", str(source_root),
    "checkout", "--quiet", "--detach", POCKET_COMMIT,
])
source_commit = subprocess.check_output(
    ["git", "-C", str(source_root), "rev-parse", "HEAD"], text=True
).strip()
source_dirty = subprocess.check_output(
    ["git", "-C", str(source_root), "status", "--porcelain"], text=True
).strip()
if source_commit != POCKET_COMMIT:
    raise RuntimeError(f"Pocket-TTS source commit mismatch: {source_commit} != {POCKET_COMMIT}")
if source_dirty:
    raise RuntimeError(f"Pinned source checkout unexpectedly dirty: {source_dirty}")

pyproject = tomllib.loads((source_root / "pyproject.toml").read_text())
source_version = pyproject["project"]["version"]
if source_version != POCKET_VERSION:
    raise RuntimeError(f"Pocket-TTS source version mismatch: {source_version} != {POCKET_VERSION}")

config_path = source_root / "pocket_tts" / "config" / "english_2026-09.yaml"
mimi_source_path = source_root / "pocket_tts" / "models" / "mimi.py"
config_blob = subprocess.check_output(
    ["git", "-C", str(source_root), "hash-object", str(config_path)], text=True
).strip()
mimi_blob = subprocess.check_output(
    ["git", "-C", str(source_root), "hash-object", str(mimi_source_path)], text=True
).strip()
if config_blob != CONFIG_GIT_BLOB:
    raise RuntimeError(f"Pinned config blob mismatch: {config_blob} != {CONFIG_GIT_BLOB}")
if mimi_blob != MIMI_GIT_BLOB:
    raise RuntimeError(f"Pinned Mimi source blob mismatch: {mimi_blob} != {MIMI_GIT_BLOB}")
print(
    f"PINNED_SOURCE_CHECK=PASS commit={source_commit} "
    f"config_blob={config_blob} mimi_blob={mimi_blob}",
    flush=True,
)

print("STAGE=DEPENDENCIES", flush=True)
# Import from the exact checkout directly. Do not install pocket-tts itself.
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "--quiet", "--no-cache-dir",
    "pydantic>=2",
    "sentencepiece>=0.2.1",
    "tokenizers>=0.21",
    "safetensors>=0.4.0",
    "typer>=0.10.0",
    "typing_extensions>=4.10.0",
    "fastapi>=0.100",
    "uvicorn>=0.13.0",
    "python-multipart>=0.0.21",
    "scipy>=1.5.0",
    "einops>=0.4.0",
    "huggingface_hub>=0.34,<1.0",
    "hf_xet",
    "requests>=2.20.0",
    "PyYAML>=6.0",
    "soundfile>=0.12.0",
])
sys.path.insert(0, str(source_root))

import numpy as np
import pandas as pd
import torch
import safetensors.torch
from packaging.version import Version
from huggingface_hub import HfApi, hf_hub_download
from pocket_tts.data.audio import audio_read
from pocket_tts.data.audio_utils import convert_audio
from pocket_tts.models.mimi import build_mimi
from pocket_tts.utils.config import load_config

if Version(torch.__version__.split("+")[0]) < Version("2.5.0"):
    raise RuntimeError(f"Pocket-TTS requires torch>=2.5.0; runtime has {torch.__version__}")

torch.manual_seed(SEED)
np.random.seed(SEED)
torch.set_num_threads(1)
try:
    torch.use_deterministic_algorithms(True, warn_only=True)
except TypeError:
    torch.use_deterministic_algorithms(True)

config = load_config(config_path)
if str(config.weights_path) != EXPECTED_CONFIG_WEIGHTS:
    raise RuntimeError(
        f"Pinned v3.3.0 config weights_path mismatch: {config.weights_path} "
        f"!= {EXPECTED_CONFIG_WEIGHTS}"
    )
if int(config.mimi.sample_rate) != SAMPLE_RATE:
    raise RuntimeError(f"Unexpected sample rate {config.mimi.sample_rate}")
if int(config.mimi.inner_dim) != LATENT_DIM:
    raise RuntimeError(f"Unexpected inner_dim {config.mimi.inner_dim}")
if float(config.mimi.frame_rate) != FRAME_RATE:
    raise RuntimeError(f"Unexpected frame_rate {config.mimi.frame_rate}")

print("STAGE=GATED_CHECKPOINT_ACCESS", flush=True)
token, token_source = get_hf_token()
if not token:
    stop_access_setup(
        "NO_AUTHORIZED_HF_TOKEN",
        "No HF_TOKEN was available in environment variables or Kaggle Secrets.",
    )

api = HfApi()
try:
    info = api.model_info(repo_id=HF_REPO, revision=HF_REVISION, token=token)
except Exception as e:
    stop_access_setup(
        "GATED_MODEL_INFO_ACCESS_FAILED",
        f"{type(e).__name__}: {str(e)[:1200]}",
    )
resolved_revision = info.sha
if resolved_revision != HF_REVISION:
    raise RuntimeError(
        f"Hugging Face revision mismatch: resolved {resolved_revision}, expected {HF_REVISION}"
    )

try:
    ckpt = Path(hf_hub_download(
        repo_id=HF_REPO,
        filename=HF_FILENAME,
        revision=HF_REVISION,
        token=token,
    ))
except Exception as e:
    stop_access_setup(
        "GATED_CHECKPOINT_DOWNLOAD_FAILED",
        f"{type(e).__name__}: {str(e)[:1200]}",
    )

ckpt_sha256 = sha256_file(ckpt)
ckpt_bytes = ckpt.stat().st_size
print(
    f"GATED_CHECKPOINT=PASS revision={resolved_revision} "
    f"bytes={ckpt_bytes} sha256={ckpt_sha256}",
    flush=True,
)

print("STAGE=ENCODER_VALIDATION", flush=True)
load_t0 = time.perf_counter()
bundle = safetensors.torch.load_file(str(ckpt), device="cpu")
mimi_state = {
    k.removeprefix("mimi."): v
    for k, v in bundle.items()
    if k.startswith("mimi.")
}
if not mimi_state:
    raise RuntimeError("Authorized checkpoint contains no mimi.* tensors")

encoder_items = [(k, v) for k, v in mimi_state.items() if k.startswith("encoder.")]
if not encoder_items:
    raise RuntimeError("Authorized checkpoint contains no Mimi encoder.* tensors")

encoder_max = 0.0
encoder_numel = 0
encoder_nonzero = 0
encoder_sum = 0.0
encoder_sumsq = 0.0
encoder_nonzero_tensors = 0
for key, tensor in encoder_items:
    x = tensor.detach().to(torch.float64).reshape(-1)
    this_max = float(x.abs().max().item()) if x.numel() else 0.0
    encoder_max = max(encoder_max, this_max)
    encoder_numel += int(x.numel())
    nz = int(torch.count_nonzero(x).item())
    encoder_nonzero += nz
    if nz > 0:
        encoder_nonzero_tensors += 1
    encoder_sum += float(x.sum().item())
    encoder_sumsq += float((x * x).sum().item())

if encoder_numel <= 0:
    raise RuntimeError("Mimi encoder tensor set has zero elements")
encoder_mean = encoder_sum / encoder_numel
encoder_variance = max(0.0, encoder_sumsq / encoder_numel - encoder_mean * encoder_mean)
encoder_std = math.sqrt(encoder_variance)
encoder_nonzero_fraction = encoder_nonzero / encoder_numel

if encoder_max <= 0.0:
    raise RuntimeError("Authorized full checkpoint still has encoder_max == 0")
if encoder_nonzero <= 0 or encoder_std <= 0.0:
    raise RuntimeError(
        f"Authorized full checkpoint encoder is degenerate: "
        f"nonzero={encoder_nonzero}, std={encoder_std}"
    )

mimi = build_mimi(config.mimi).to("cpu")
missing, unexpected = mimi.load_state_dict(mimi_state, strict=True)
if missing or unexpected:
    raise RuntimeError(
        f"Strict Mimi state load returned missing={missing}, unexpected={unexpected}"
    )
mimi.eval()
for p in mimi.parameters():
    p.requires_grad_(False)
model_load_seconds = time.perf_counter() - load_t0
memory_after_model_mb = maxrss_mb()

# Encoder smoke test before competition audio.
seconds = 2.0
n = int(SAMPLE_RATE * seconds)
t = torch.arange(n, dtype=torch.float32) / SAMPLE_RATE
synthetic = (
    0.30 * torch.sin(2.0 * math.pi * 220.0 * t)
    + 0.15 * torch.sin(2.0 * math.pi * 440.0 * t)
).reshape(1, 1, -1)
with torch.inference_mode():
    synthetic_latent = mimi.encode_to_latent(synthetic)
if synthetic_latent.ndim != 3:
    raise RuntimeError(f"Synthetic encode rank mismatch: {tuple(synthetic_latent.shape)}")
if synthetic_latent.shape[0] != 1 or synthetic_latent.shape[2] != LATENT_DIM:
    raise RuntimeError(f"Synthetic encode shape mismatch: {tuple(synthetic_latent.shape)}")
if not torch.isfinite(synthetic_latent).all():
    raise RuntimeError("Synthetic encode produced non-finite values")
synthetic_std = float(synthetic_latent.std(correction=0).item())
if synthetic_std <= 0:
    raise RuntimeError("Synthetic encode produced a degenerate constant latent")

print(
    f"ENCODER_VALID=YES encoder_max={encoder_max:.12g} "
    f"nonzero_fraction={encoder_nonzero_fraction:.12g} "
    f"encoder_std={encoder_std:.12g} "
    f"synthetic_shape={tuple(synthetic_latent.shape)}",
    flush=True,
)

print("STAGE=COMPETITION_CPU_PREFLIGHT", flush=True)
root = find_competition_root()
train_csv = root / "train.csv"
train_dir = root / "train"
df = pd.read_csv(train_csv)
required = {"Id", "filename", "emotion"}
if not required.issubset(df.columns):
    raise RuntimeError(f"train.csv missing columns: {required - set(df.columns)}")
if len(df) != 826 or df["Id"].nunique() != 826:
    raise RuntimeError(
        f"Unexpected train identity: rows={len(df)}, unique_ids={df['Id'].nunique()}"
    )

classes = ["angry", "happy", "neutral", "sad"]
parts = []
for cls in classes:
    z = df[df["emotion"] == cls].sort_values("Id").head(2)
    if len(z) != 2:
        raise RuntimeError(f"Could not select two deterministic preflight rows for {cls}")
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
    wav24 = convert_audio(wav, sr, SAMPLE_RATE, 1)
    if wav24.ndim != 2 or wav24.shape[0] != 1:
        raise RuntimeError(f"mono/resample failure for {path}: {tuple(wav24.shape)}")
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
        f"PREFLIGHT_ROW Id={r['Id']} class={r['emotion']} "
        f"frames={r['latent_frames']} runtime={r['runtime_seconds']:.6f}s",
        flush=True,
    )

repeat = extract_one(sample.iloc[0])
repeat_max_abs = float(np.max(np.abs(rows[0]["feature"] - repeat["feature"])))
if repeat["wav_sha256"] != rows[0]["wav_sha256"]:
    raise RuntimeError("Repeated WAV identity mismatch")
if repeat_max_abs > REPEAT_TOL:
    raise RuntimeError(
        f"Repeat extraction mismatch: {repeat_max_abs} > tolerance {REPEAT_TOL}"
    )

runtimes = np.array([r["runtime_seconds"] for r in rows], dtype=float)
median_runtime = float(np.median(runtimes))
mean_runtime = float(np.mean(runtimes))
projected_826_seconds = median_runtime * 826
projected_1035_seconds = median_runtime * 1035
peak_mb = maxrss_mb()

columns = [
    "Id","filename","emotion","source_sr","samples_24k","latent_frames",
    "runtime_seconds","wav_sha256"
] + [f"f{i:02d}" for i in range(FEATURE_DIM)]
with (OUT / "PREFLIGHT_ROWS.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(columns)
    for r in rows:
        w.writerow([
            r["Id"], r["filename"], r["emotion"], r["source_sr"],
            r["samples_24k"], r["latent_frames"],
            f"{r['runtime_seconds']:.12g}", r["wav_sha256"],
            *[f"{x:.17g}" for x in r["feature"]],
        ])

summary = {
    "mission": MISSION,
    "status": "PASS",
    "full_checkpoint_accessibility_status": "PASS_REASONABLY_ACCESSIBLE",
    "full_checkpoint_use_authorized": True,
    "source": {
        "repo": POCKET_REPO,
        "version": source_version,
        "commit": source_commit,
        "clean": not bool(source_dirty),
        "config_git_blob_sha1": config_blob,
        "mimi_git_blob_sha1": mimi_blob,
    },
    "checkpoint": {
        "repo": HF_REPO,
        "revision_requested": HF_REVISION,
        "revision_resolved": resolved_revision,
        "filename": HF_FILENAME,
        "sha256": ckpt_sha256,
        "bytes": ckpt_bytes,
        "token_source": token_source,
    },
    "encoder": {
        "tensor_count": len(encoder_items),
        "nonzero_tensor_count": encoder_nonzero_tensors,
        "numel": encoder_numel,
        "nonzero_numel": encoder_nonzero,
        "nonzero_fraction": encoder_nonzero_fraction,
        "encoder_max": encoder_max,
        "encoder_mean": encoder_mean,
        "encoder_std": encoder_std,
        "valid": True,
        "synthetic_latent_shape": list(synthetic_latent.shape),
        "synthetic_latent_std": synthetic_std,
    },
    "representation": {
        "name": "POCKET_MIMI_CONTINUOUS_MEANSTD",
        "call": "MimiModel.encode_to_latent",
        "sample_rate_hz": SAMPLE_RATE,
        "latent_dim": LATENT_DIM,
        "frame_rate_hz": FRAME_RATE,
        "pooling": "temporal mean + population std (correction=0)",
        "feature_dim": FEATURE_DIM,
        "text_invoked": False,
        "tts_generation_invoked": False,
        "voice_cloning_invoked": False,
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
        "memory_after_model_mb": memory_after_model_mb,
        "peak_memory_mb": peak_mb,
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
    "primary_cv_run": False,
    "target209_run": False,
    "submission": False,
}
write_json("PREFLIGHT.json", summary)
(OUT / "CHECKPOINT_SHA256.txt").write_text(f"{ckpt_sha256}  {HF_FILENAME}\n")
(OUT / "SCRIPT_SHA256.txt").write_text(
    f"{sha256_file(Path(__file__))}  {Path(__file__).name}\n"
)

print("POCKET_MIMI_PREFLIGHT=PASS", flush=True)
print(json.dumps(summary, indent=2), flush=True)
