#!/usr/bin/env python3
from __future__ import annotations

import base64
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

AUTH = "6292e2c4714b44f56b1c51acd4d3100e996c5e1b"
MISSION = "DS-DEFHS-VALIDATION-HARDENING-002"

SCRIPT_SHA256 = "8543960502ba3a71a8e4fa311032de5115a12f0152dd857a939209d579783b0e"
SCRIPT_B64 = """IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwoiIiJEUy0wMDIgam9pbnQgbGF0ZW50LXJlZ2ltZSBhdWRpdCBhZnRlciBFQ0FQQSArIEFTUiArIGVHZU1BUFMgZXhlY3V0aW9uLgoKVGhpcyBzY3JpcHQgY2hhcmFjdGVyaXplcyBzdGFibGUgbGF0ZW50IHJlZ2ltZXMuIEl0IG5ldmVyIGxhYmVscyBhIHJlZ2ltZQoiYWN0ZWQiIG9yICJzcG9udGFuZW91cyIgd2l0aG91dCBleHRlcm5hbCBncm91bmQgdHJ1dGguCiIiIgpmcm9tIF9fZnV0dXJlX18gaW1wb3J0IGFubm90YXRpb25zCmltcG9ydCBhcmdwYXJzZSwganNvbgpmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGgKaW1wb3J0IG51bXB5IGFzIG5wLCBwYW5kYXMgYXMgcGQKZnJvbSBza2xlYXJuLmNsdXN0ZXIgaW1wb3J0IEtNZWFucwpmcm9tIHNrbGVhcm4uY29tcG9zZSBpbXBvcnQgQ29sdW1uVHJhbnNmb3JtZXIKZnJvbSBza2xlYXJuLmltcHV0ZSBpbXBvcnQgU2ltcGxlSW1wdXRlcgpmcm9tIHNrbGVhcm4ubWV0cmljcyBpbXBvcnQgYWRqdXN0ZWRfcmFuZF9zY29yZSwgbm9ybWFsaXplZF9tdXR1YWxfaW5mb19zY29yZSwgc2lsaG91ZXR0ZV9zY29yZQpmcm9tIHNrbGVhcm4ucGlwZWxpbmUgaW1wb3J0IG1ha2VfcGlwZWxpbmUKZnJvbSBza2xlYXJuLnByZXByb2Nlc3NpbmcgaW1wb3J0IE9uZUhvdEVuY29kZXIsIFN0YW5kYXJkU2NhbGVyCmZyb20gc2tsZWFybi5kZWNvbXBvc2l0aW9uIGltcG9ydCBQQ0EKCmRlZiBtYWluKCk6CiAgICBhcD1hcmdwYXJzZS5Bcmd1bWVudFBhcnNlcigpOyBhcC5hZGRfYXJndW1lbnQoIi0tb3V0Iix0eXBlPVBhdGgscmVxdWlyZWQ9VHJ1ZSkKICAgIGE9YXAucGFyc2VfYXJncygpCiAgICBzcD1wZC5yZWFkX2NzdihhLm91dC8iU1BFQUtFUl9DTFVTVEVSX0FTU0lHTk1FTlRTLmNzdiIpCiAgICB0eD1wZC5yZWFkX2NzdihhLm91dC8iUFJPTVBUX0NMVVNURVJfQVNTSUdOTUVOVFMuY3N2IikKICAgIGVnPXBkLnJlYWRfY3N2KGEub3V0LyJFR0VNQVBTX0ZFQVRVUkVTLmNzdiIpCiAgICBkbT1wZC5yZWFkX2NzdihhLm91dC8iREFUQV9NQU5JRkVTVC5jc3YiKQogICAgYmFzZT1kbVtbIklkIiwic3BsaXQiLCJmaWxlbmFtZSIsImVtb3Rpb24iLCJkdHlwZSIsImR1cmF0aW9uX3NlY29uZHMiXV0ubWVyZ2Uoc3Asb249WyJJZCIsInNwbGl0IiwiZmlsZW5hbWUiXSxob3c9ImxlZnQiLHN1ZmZpeGVzPSgiIiwiX3NwIikpCiAgICBrZWVwX3R4PVtjIGZvciBjIGluIHR4LmNvbHVtbnMgaWYgYz09IklkIiBvciBjLnN0YXJ0c3dpdGgoInByb21wdF9zaW1fIikgb3IgYyBpbiB7Im5vcm1hbGl6ZWRfdHJhbnNjcmlwdCIsImF2Z19sb2dwcm9iIiwibm9fc3BlZWNoX3Byb2IifV0KICAgIGJhc2U9YmFzZS5tZXJnZSh0eFtrZWVwX3R4XSxvbj0iSWQiLGhvdz0ibGVmdCIpCiAgICBlZ19jb2xzPVtjIGZvciBjIGluIGVnLmNvbHVtbnMgaWYgYyBub3QgaW4geyJJZCIsInNwbGl0IiwiZmlsZW5hbWUiLCJlbW90aW9uIn1dCiAgICBYZWc9ZWcuc2V0X2luZGV4KCJJZCIpLmxvY1tiYXNlLklkLGVnX2NvbHNdLnJlcGxhY2UoW25wLmluZiwtbnAuaW5mXSxucC5uYW4pCiAgICBYZWc9U2ltcGxlSW1wdXRlcihzdHJhdGVneT0ibWVkaWFuIikuZml0X3RyYW5zZm9ybShYZWcpOyBYZWc9U3RhbmRhcmRTY2FsZXIoKS5maXRfdHJhbnNmb3JtKFhlZykKICAgICMga2VlcCBlR2VNQVBTIGNvbnRyaWJ1dGlvbiBib3VuZGVkOyBzdW1tYXJpemUgYnkgcHJpbmNpcGFsIGNvbXBvbmVudHMKICAgIHBjYT1QQ0Eobl9jb21wb25lbnRzPW1pbigxMixYZWcuc2hhcGVbMV0pLHJhbmRvbV9zdGF0ZT0yMDI2MDkzMCkKICAgIFplZz1wY2EuZml0X3RyYW5zZm9ybShYZWcpCiAgICBzcGVha2VyX2NvbHM9W2MgZm9yIGMgaW4gc3AuY29sdW1ucyBpZiBjLnN0YXJ0c3dpdGgoImFnZ19kIildCiAgICBwcm9tcHRfY29scz1bYyBmb3IgYyBpbiB0eC5jb2x1bW5zIGlmIGMuc3RhcnRzd2l0aCgicHJvbXB0X3NpbV8iKV0KICAgICMgY2hvb3NlIGNlbnRyYWwgdGhyZXNob2xkcyBvbmx5IGFzIGNhdGVnb3JpY2FsIGV2aWRlbmNlOyBhdWRpdCBhbHRlcm5hdGUgdGhyZXNob2xkcyBzZXBhcmF0ZWx5LgogICAgc2M9c3BlYWtlcl9jb2xzW2xlbihzcGVha2VyX2NvbHMpLy8yXSBpZiBzcGVha2VyX2NvbHMgZWxzZSBOb25lCiAgICBwYz1wcm9tcHRfY29sc1tsZW4ocHJvbXB0X2NvbHMpLy8yXSBpZiBwcm9tcHRfY29scyBlbHNlIE5vbmUKICAgIGNhdHM9cGQuRGF0YUZyYW1lKHsiZHR5cGUiOmJhc2UuZHR5cGUuYXN0eXBlKHN0cil9KQogICAgaWYgc2M6IGNhdHNbInNwZWFrZXJfbGlrZSJdPXNwLnNldF9pbmRleCgiSWQiKS5sb2NbYmFzZS5JZCxzY10uYXN0eXBlKHN0cikudG9fbnVtcHkoKQogICAgaWYgcGM6IGNhdHNbInByb21wdF9saWtlIl09dHguc2V0X2luZGV4KCJJZCIpLmxvY1tiYXNlLklkLHBjXS5hc3R5cGUoc3RyKS50b19udW1weSgpCiAgICBlbmM9T25lSG90RW5jb2RlcihoYW5kbGVfdW5rbm93bj0iaWdub3JlIixzcGFyc2Vfb3V0cHV0PUZhbHNlLG1pbl9mcmVxdWVuY3k9MikKICAgIFpjYXQ9ZW5jLmZpdF90cmFuc2Zvcm0oY2F0cykKICAgIFo9bnAuaHN0YWNrKFtaZWcsWmNhdF0pCiAgICByZXN1bHRzPVtdOyBsYWJlbHM9e30KICAgIGZvciBrIGluIFsyLDMsNCw1LDZdOgogICAgICAgIGxhYj1LTWVhbnMobl9jbHVzdGVycz1rLHJhbmRvbV9zdGF0ZT0yMDI2MDkzMCxuX2luaXQ9MzApLmZpdF9wcmVkaWN0KFopCiAgICAgICAgbGFiZWxzW2Yiam9pbnRfa3trfSJdPWxhYgogICAgICAgIHNpbD1mbG9hdChzaWxob3VldHRlX3Njb3JlKFosbGFiKSkKICAgICAgICBkdHlwZV9ubWk9ZmxvYXQobm9ybWFsaXplZF9tdXR1YWxfaW5mb19zY29yZShiYXNlLmR0eXBlLmFzdHlwZShzdHIpLGxhYikpCiAgICAgICAgc3BsaXRfbm1pPWZsb2F0KG5vcm1hbGl6ZWRfbXV0dWFsX2luZm9fc2NvcmUoYmFzZS5zcGxpdC5hc3R5cGUoc3RyKSxsYWIpKQogICAgICAgIGVtb3Rpb25fbm1pPWZsb2F0KG5vcm1hbGl6ZWRfbXV0dWFsX2luZm9fc2NvcmUoYmFzZS5lbW90aW9uLmZpbGxuYSgiVEVTVCIpLmFzdHlwZShzdHIpLGxhYikpCiAgICAgICAgcmVzdWx0cy5hcHBlbmQoeyJrIjprLCJzaWxob3VldHRlIjpzaWwsImR0eXBlX25taSI6ZHR5cGVfbm1pLCJzcGxpdF9ubWkiOnNwbGl0X25taSwiZW1vdGlvbl9vcl90ZXN0X25taSI6ZW1vdGlvbl9ubWl9KQogICAgTD1wZC5EYXRhRnJhbWUobGFiZWxzKQogICAgYWRqYWNlbnQ9W10KICAgIGNvbHM9bGlzdChMKQogICAgZm9yIHgseSBpbiB6aXAoY29sc1s6LTFdLGNvbHNbMTpdKTogYWRqYWNlbnQuYXBwZW5kKHsiYSI6eCwiYiI6eSwiYXJpIjpmbG9hdChhZGp1c3RlZF9yYW5kX3Njb3JlKExbeF0sTFt5XSkpfSkKICAgIG91dD1wZC5jb25jYXQoW2Jhc2VbWyJJZCIsInNwbGl0IiwiZW1vdGlvbiIsImR0eXBlIiwiZHVyYXRpb25fc2Vjb25kcyJdXSxMXSxheGlzPTEpCiAgICBvdXQudG9fY3N2KGEub3V0LyJMQVRFTlRfUkVHSU1FX0FTU0lHTk1FTlRTLmNzdiIsaW5kZXg9RmFsc2UpCiAgICBzdW1tYXJ5PXsKICAgICAgInB1cnBvc2UiOiJsYXRlbnQtcmVnaW1lIGNoYXJhY3Rlcml6YXRpb24gYWZ0ZXIgc3BlYWtlci9BU1IvZUdlTUFQUyBldmlkZW5jZSIsCiAgICAgICJhY3RlZF9zcG9udGFuZW91c19ncm91bmRfdHJ1dGhfYXZhaWxhYmxlIjpGYWxzZSwKICAgICAgInNlbGVjdGVkX3NwZWFrZXJfY2x1c3Rlcl9jb2x1bW4iOnNjLCJzZWxlY3RlZF9wcm9tcHRfY2x1c3Rlcl9jb2x1bW4iOnBjLAogICAgICAiZWdlbWFwc19wY2FfZXhwbGFpbmVkX3ZhcmlhbmNlIjpmbG9hdChwY2EuZXhwbGFpbmVkX3ZhcmlhbmNlX3JhdGlvXy5zdW0oKSksCiAgICAgICJqb2ludF9jbHVzdGVyX3Jlc3VsdHMiOnJlc3VsdHMsImFkamFjZW50X2tfYXJpIjphZGphY2VudCwKICAgICAgImludGVycHJldGF0aW9uX3J1bGUiOiJEbyBub3QgbmFtZSBjbHVzdGVycyBhY3RlZC9zcG9udGFuZW91cy4gQSBzdHJvbmcgc3RhYmxlIGxhdGVudCBwYXJ0aXRpb24gbWF5IGp1c3RpZnkgVi1ELWxpa2Ugc3RyZXNzIG9ubHkgYWZ0ZXIgc2NpZW50aWZpYyByZXZpZXcuIgogICAgfQogICAgKGEub3V0LyJMQVRFTlRfUkVHSU1FX0FVRElUX1JFU1VMVFMuanNvbiIpLndyaXRlX3RleHQoanNvbi5kdW1wcyhzdW1tYXJ5LGluZGVudD0yKSkKICAgIHByaW50KGpzb24uZHVtcHMoc3VtbWFyeSxpbmRlbnQ9MikpCmlmIF9fbmFtZV9fPT0iX19tYWluX18iOiBtYWluKCkK"""

EXPECTED = {'DATA_MANIFEST.csv': '1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469', 'SPEAKER_CLUSTER_ASSIGNMENTS.csv': 'a55d713d89017883f45c4d8d7f859fc4a6274445675fd5f0b962996c2af451d0', 'PROMPT_CLUSTER_ASSIGNMENTS.csv': '458712cfee51e0cf65ef57d1a0deb8f81dcb70e4ecfe6ebfc73220f3aefac005', 'EGEMAPS_FEATURES.csv': '45476151fa3eaf6fd747495a3827e769bac189cbc347459559734ceb1828a0be'}

INPUT = Path("/kaggle/input")
WORK = Path("/kaggle/working")

OUT = WORK / "ds002_latent_final"
SCRIPT = WORK / "run_ds002_latent_regime_joint_audit.py"

def now():
    return datetime.now(timezone.utc).isoformat()

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def csv_rows(path: Path) -> int:
    with path.open(
        newline="",
        encoding="utf-8",
        errors="replace",
    ) as f:
        return max(sum(1 for _ in csv.reader(f)) - 1, 0)

def dump(path: Path, obj):
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

print("===== DS002 LATENT FINAL =====", flush=True)
print("AUTH =", AUTH, flush=True)

OUT.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# Restore and verify exact patched canonical latent script.
# ------------------------------------------------------------

SCRIPT.write_bytes(base64.b64decode(SCRIPT_B64))

if sha256(SCRIPT) != SCRIPT_SHA256:
    raise RuntimeError("latent script SHA mismatch")

print("LATENT_SCRIPT_AUTHORITY=PASS", flush=True)
print("LATENT_SCRIPT_SHA256 =", SCRIPT_SHA256, flush=True)

# ------------------------------------------------------------
# Locate exactly one prior-kernel output directory containing
# the four authoritative inputs.
# ------------------------------------------------------------

required_names = set(EXPECTED)

candidates = []

for p in INPUT.rglob("DATA_MANIFEST.csv"):
    root = p.parent

    if all((root / name).is_file() for name in required_names):
        candidates.append(root)

print(
    "SOURCE_CANDIDATES =",
    [str(x) for x in candidates],
    flush=True,
)

if len(candidates) != 1:
    raise RuntimeError(
        f"Expected exactly one v2 artifact root; found {len(candidates)}"
    )

SRC = candidates[0]

print("SOURCE_ROOT =", SRC, flush=True)

# ------------------------------------------------------------
# Verify byte identity against recovered v2 authority.
# ------------------------------------------------------------

source_manifest = {}

for name, expected_sha in EXPECTED.items():
    p = SRC / name

    actual_sha = sha256(p)

    if actual_sha != expected_sha:
        raise RuntimeError(
            f"{name} hash mismatch: "
            f"{actual_sha} != {expected_sha}"
        )

    n = csv_rows(p)

    if n != 1035:
        raise RuntimeError(
            f"{name}: expected 1035 rows, got {n}"
        )

    source_manifest[name] = {
        "sha256": actual_sha,
        "bytes": p.stat().st_size,
        "rows": n,
    }

    shutil.copy2(p, OUT / name)

print("V2_INPUT_ARTIFACTS=PASS", flush=True)

dump(
    OUT / "LATENT_INPUT_AUTHORITY.json",
    {
        "mission": MISSION,
        "git_commit": AUTH,
        "source_kernel": "khalwaniev/defhs-ds002-closure",
        "source_kernel_expected_version": 2,
        "files": source_manifest,
        "protected_gate_queried": False,
    },
)

# ------------------------------------------------------------
# Record runtime versions before execution.
# ------------------------------------------------------------

probe = subprocess.run(
    [
        sys.executable,
        "-c",
        (
            "import numpy,pandas,sklearn;"
            "print('numpy='+numpy.__version__);"
            "print('pandas='+pandas.__version__);"
            "print('scikit-learn='+sklearn.__version__)"
        ),
    ],
    capture_output=True,
    text=True,
)

(OUT / "LATENT_RUNTIME_VERSIONS.txt").write_text(
    probe.stdout + probe.stderr,
    encoding="utf-8",
)

if probe.returncode != 0:
    raise RuntimeError("runtime version probe failed")

print(probe.stdout, flush=True)

# ------------------------------------------------------------
# Execute ONLY the patched latent audit.
# ------------------------------------------------------------

log_path = OUT / "04_LATENT.log"

started = now()

with log_path.open("w", encoding="utf-8") as log:
    p = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--out",
            str(OUT),
        ],
        stdout=log,
        stderr=subprocess.STDOUT,
        text=True,
    )

if p.returncode != 0:
    raise RuntimeError(
        f"latent audit failed with returncode={p.returncode}; "
        f"inspect {log_path.name}"
    )

assignments = OUT / "LATENT_REGIME_ASSIGNMENTS.csv"
results = OUT / "LATENT_REGIME_AUDIT_RESULTS.json"

if not assignments.is_file():
    raise RuntimeError("missing LATENT_REGIME_ASSIGNMENTS.csv")

if not results.is_file():
    raise RuntimeError("missing LATENT_REGIME_AUDIT_RESULTS.json")

rows = csv_rows(assignments)

if rows != 1035:
    raise RuntimeError(
        f"latent assignments expected 1035 rows, got {rows}"
    )

result_obj = json.loads(results.read_text())

if result_obj.get(
    "acted_spontaneous_ground_truth_available"
) is not False:
    raise RuntimeError(
        "latent interpretation guard unexpectedly changed"
    )

ks = [
    int(x["k"])
    for x in result_obj["joint_cluster_results"]
]

if ks != [2, 3, 4, 5, 6]:
    raise RuntimeError(
        f"unexpected latent k sequence: {ks}"
    )

finished = now()

final_manifest = {
    "mission": MISSION,
    "git_commit": AUTH,
    "execution": "LATENT_ONLY_FINAL",
    "source_kernel": "khalwaniev/defhs-ds002-closure",
    "source_kernel_expected_version": 2,
    "protected_gate_queried": False,
    "started_utc": started,
    "finished_utc": finished,
    "outputs": {
        "LATENT_REGIME_ASSIGNMENTS.csv": {
            "sha256": sha256(assignments),
            "bytes": assignments.stat().st_size,
            "rows": rows,
        },
        "LATENT_REGIME_AUDIT_RESULTS.json": {
            "sha256": sha256(results),
            "bytes": results.stat().st_size,
        },
        "04_LATENT.log": {
            "sha256": sha256(log_path),
            "bytes": log_path.stat().st_size,
        },
    },
}

dump(
    OUT / "LATENT_FINAL_MANIFEST.json",
    final_manifest,
)

print("LATENT_PROCESS_EXIT=PASS", flush=True)
print("LATENT_ROWS =", rows, flush=True)
print("LATENT_K_VALUES =", ks, flush=True)

print(
    "LATENT_ASSIGNMENTS_SHA256 =",
    final_manifest["outputs"]
    ["LATENT_REGIME_ASSIGNMENTS.csv"]["sha256"],
    flush=True,
)

print(
    "LATENT_RESULTS_SHA256 =",
    final_manifest["outputs"]
    ["LATENT_REGIME_AUDIT_RESULTS.json"]["sha256"],
    flush=True,
)

print("DS002_LATENT_FINAL=SUCCESS", flush=True)
