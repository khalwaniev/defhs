#!/usr/bin/env python3
"""Reproducible initial integrity audit for the DEFHS Kaggle competition ZIP."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import wavfile


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("zip_path", type=Path)
    ap.add_argument("--out", type=Path, default=Path("artifacts/data_audit_initial"))
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    root = "SRCASW-BhavVaani"
    with zipfile.ZipFile(args.zip_path) as zf:
        train = pd.read_csv(io.BytesIO(zf.read(f"{root}/train.csv")))
        test = pd.read_csv(io.BytesIO(zf.read(f"{root}/test.csv")))

        rows = []
        hash_groups = defaultdict(list)

        for split, df in (("train", train), ("test", test)):
            for row in df.itertuples(index=False):
                member = f"{root}/{split}/{row.filename}"
                raw = zf.read(member)
                sr, x = wavfile.read(io.BytesIO(raw))
                if x.ndim > 1:
                    x = x.mean(axis=1)
                pcm_hash = hashlib.sha256(np.asarray(x).tobytes()).hexdigest()
                hash_groups[pcm_hash].append(
                    {
                        "split": split,
                        "Id": int(row.Id),
                        "filename": row.filename,
                        "emotion": getattr(row, "emotion", None),
                    }
                )
                rows.append(
                    {
                        "split": split,
                        "Id": int(row.Id),
                        "filename": row.filename,
                        "emotion": getattr(row, "emotion", None),
                        "sample_rate": int(sr),
                        "samples": int(len(x)),
                        "duration_seconds": float(len(x) / sr),
                        "dtype": str(x.dtype),
                        "pcm_sha256": pcm_hash,
                    }
                )

    meta = pd.DataFrame(rows)
    meta.to_csv(args.out / "audio_metadata.csv", index=False)

    exact_groups = [g for g in hash_groups.values() if len(g) > 1]
    (args.out / "exact_duplicate_groups.json").write_text(
        json.dumps(exact_groups, indent=2)
    )

    cross = [
        g
        for g in exact_groups
        if {r["split"] for r in g} == {"train", "test"}
    ]
    train_only = [
        g
        for g in exact_groups
        if {r["split"] for r in g} == {"train"}
    ]

    summary = {
        "train_rows": int((meta["split"] == "train").sum()),
        "test_rows": int((meta["split"] == "test").sum()),
        "total_rows": int(len(meta)),
        "sample_rates": sorted(int(v) for v in meta["sample_rate"].unique()),
        "duration_seconds": {
            "min": float(meta["duration_seconds"].min()),
            "median": float(meta["duration_seconds"].median()),
            "max": float(meta["duration_seconds"].max()),
            "mean": float(meta["duration_seconds"].mean()),
        },
        "exact_cross_split_groups": len(cross),
        "exact_cross_split_test_clips": sum(
            sum(r["split"] == "test" for r in g) for g in cross
        ),
        "exact_train_only_groups": len(train_only),
        "exact_train_only_clips": sum(len(g) for g in train_only),
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
