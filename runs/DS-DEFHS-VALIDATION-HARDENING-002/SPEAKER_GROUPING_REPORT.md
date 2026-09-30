# Speaker Grouping Report

## Closure status

**PENDING REQUIRED PRETRAINED SPEAKER AUDIT.**

The earlier statement that speaker structure was epistemically `UNRESOLVABLE` was too strong. What was established was only that the first runtime lacked accessible pretrained speaker weights.

The competition still supplies no organizer speaker IDs, so **true organizer speaker identity may remain unobservable**. However, reliable speaker-like grouping and train/test speaker-like overlap may be inferable and must be tested before final validation closure.

## Required executed analysis

Canonical executor:

`scripts/run_ds002_speaker_ecapa_audit.py`

Planned representation:

`speechbrain/spkrec-ecapa-voxceleb` ECAPA-TDNN.

The executor resolves and records an immutable model revision at runtime, extracts normalized embeddings for all 1,035 clips, and audits:

- duplicate-family embedding consistency;
- pairwise similarity distribution;
- agglomerative threshold stability;
- DBSCAN stability;
- train/test mixed clusters;
- per-cluster label diversity;
- recording-dtype confounding;
- cluster stability across thresholds.

The script explicitly describes resulting clusters as **speaker-like hypotheses**, not true speaker IDs.

## Current policy

- V-C is **not frozen**.
- The V-A/V-B backbone remains preserved.
- No speaker identity is inferred from pitch, sex/gender, or low-level acoustics.
- Final closure requires actual embedding results, not merely this executor.
- If embedding evidence is stable enough, a V-C speaker-like stress view may be added. Otherwise V-C must be rejected with positive embedding evidence documenting why grouping is unreliable.

Current final-evidence state for reliable speaker-like grouping: **not yet classifiable; required audit pending**.
