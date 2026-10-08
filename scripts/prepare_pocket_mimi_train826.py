#!/usr/bin/env python3
"""Package exact frozen membership and train-only provenance, without credentials."""
import base64
import csv
import gzip
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/RS-DEFHS-POCKET-MIMI-REPRESENTATION-001"
DS = ROOT / "runs/DS-DEFHS-VALIDATION-HARDENING-002"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    template = ROOT / "scripts/pocket_mimi_train826.py"
    marker = "AUTHORITY = {}  # populated by prepare_pocket_mimi_train826.py"
    code = template.read_text()
    assert code.count(marker) == 1
    source_manifest = (DS / "DATA_MANIFEST.csv").read_bytes()
    assert sha(source_manifest) == "1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469"
    reader = csv.DictReader(io.StringIO(source_manifest.decode()))
    train_rows = [r for r in reader if r["split"] == "train"]
    assert len(train_rows) == 826 and len({int(r["Id"]) for r in train_rows}) == 826
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(train_rows)
    inputs = {}
    originals = {
        "VALIDATION_VB_FOLDS.csv": DS / "VALIDATION_VB_FOLDS.csv",
        **{n: RUN / "preflight" / n for n in ["PREFLIGHT.json", "PREFLIGHT_ROWS.csv", "SCRIPT_SHA256.txt"]}}
    for name, path in originals.items():
        raw = path.read_bytes()
        inputs[name] = {"source_path": str(path.relative_to(ROOT)), "sha256": sha(raw),
                        "gzip_b64": base64.b64encode(gzip.compress(raw, mtime=0)).decode()}
    assert inputs["VALIDATION_VB_FOLDS.csv"]["sha256"] == "87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b"
    raw = buf.getvalue().encode()
    inputs["TRAIN_WAV_MANIFEST.csv"] = {"source_path": str((DS / "DATA_MANIFEST.csv").relative_to(ROOT)),
        "source_file_sha256": sha(source_manifest), "selection": "split == train; all 826 rows; original columns",
        "sha256": sha(raw), "gzip_b64": base64.b64encode(gzip.compress(raw, mtime=0)).decode()}
    payload = {"mission": "RS-DEFHS-POCKET-MIMI-REPRESENTATION-001",
        "input_repository_head": "914276fd4ac9f2fc911f82819774825318f40b71",
        "template_sha256": sha(template.read_bytes()), "inputs": inputs,
        "incumbent_scores": {"System C": 0.8135577912484513,
                             "Fixed waveform pair": 0.7768156647359765,
                             "System1 emotion2vec": 0.7383745765682462}}
    dest = ROOT / "kaggle/rs_defhs_pocket_mimi_train826_001"
    dest.mkdir(parents=True, exist_ok=True)
    generated = code.replace(marker, "AUTHORITY = " + repr(payload))
    (dest / "run.py").write_text(generated)
    metadata = json.loads((ROOT / "kaggle/rs_defhs_pocket_mimi_preflight_001/kernel-metadata.json").read_text())
    (dest / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    manifest = {"status": "PREPARED_NOT_EXECUTED", "kernel": metadata["id"],
        "execution_method": "existing secret-enabled Kaggle notebook; manual Save Version / Run All",
        "script": str((dest / "run.py").relative_to(ROOT)), "script_sha256": sha(generated.encode()),
        "template_sha256": payload["template_sha256"],
        "inputs": {k: {j: v for j, v in item.items() if j != "gzip_b64"} for k, item in inputs.items()},
        "cpu_only": True, "secret_value_embedded": False, "automatic_run_attempted": False,
        "stages": ["TRAIN826_EXTRACTION", "FROZEN_PRIMARY_CV"],
        "target209_authorization_status": "NOT_AUTHORIZED", "target209_run": False,
        "fusion_run": False, "submission": False}
    (RUN / "PHASE1_EXECUTION_PACKAGE.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"script": manifest["script"], "sha256": manifest["script_sha256"],
                      "input_names": sorted(inputs), "script_bytes": len(generated.encode())}))


if __name__ == "__main__":
    main()
