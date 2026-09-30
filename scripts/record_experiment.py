#!/usr/bin/env python3
"""Append a lightweight experiment record to the canonical registry."""
from __future__ import annotations

import argparse
import csv
import subprocess
from datetime import date
from pathlib import Path

FIELDS = [
    "experiment_id","date","status","hypothesis","baseline","change","validation",
    "config","git_commit","compute","result","verdict","artifact_locations","notes",
]

def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return ""

def main() -> None:
    p = argparse.ArgumentParser()
    for field in FIELDS:
        if field in {"date", "git_commit"}:
            continue
        p.add_argument(f"--{field.replace('_','-')}", default="")
    p.add_argument("--registry", default="experiments/EXPERIMENT_REGISTRY.csv")
    a = p.parse_args()

    row = {f: getattr(a, f, "") for f in FIELDS}
    row["date"] = date.today().isoformat()
    row["git_commit"] = git_head()

    path = Path(a.registry)
    with path.open("a", newline="") as fh:
        csv.DictWriter(fh, fieldnames=FIELDS).writerow(row)

if __name__ == "__main__":
    main()
