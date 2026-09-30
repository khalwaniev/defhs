# Acted / Spontaneous Report

The organizers state that the corpus includes both acted and spontaneous speech, but the supplied package provides no per-clip regime labels.

## Closure status

**PENDING JOINT RECONSIDERATION AFTER SPEAKER + ASR + eGeMAPS.**

The previous hard `UNRESOLVABLE` verdict was issued before the required pretrained speaker and ASR audits were executed. That verdict is therefore not retained as final evidence.

Existing low-level evidence remains valid:

- int16/int32 recording heterogeneity is real;
- duration, silence/pause, and spectral structure differ across source/format regimes;
- low-level unsupervised source clusters are not stable enough to be renamed acted/spontaneous.

## Required joint analysis

After the mandatory speaker, ASR, and standardized eGeMAPS artifacts exist, run:

`scripts/run_ds002_latent_regime_joint_audit.py`

The joint audit combines:

- speaker-like clusters;
- prompt/transcript clusters;
- eGeMAPS paralinguistics;
- recording dtype/source structure;
- duration and related observable structure.

It may establish stable **latent regimes**, but it is explicitly prohibited from naming a cluster "acted" or "spontaneous" without evidence that supports that semantic interpretation.

## Current policy

- no per-clip acted/spontaneous labels;
- do not equate int16/int32 with acted/spontaneous;
- V-D remains a verified recording-format stress only;
- final evidence state must be reissued after the joint audit.

Current acted/spontaneous evidence state: **not yet classifiable for final closure**.
