# Active competition state

Authority: `DEFHS-TARGET209-CONTEXT-CLEANUP-001`, 2026-10-04.

DEFHS must maximize **macro-F1 on the exact 209 supplied test WAV files** by
predicting `angry / happy / neutral / sad`. There are **826 labeled training
WAVs** and **209 unlabeled test WAVs**. Test rows are the prediction target;
training validation is evidence about generalization.

`TARGET209` means the test partition of the supplied competition package,
identified by its existing IDs, filenames and recorded waveform hashes. The
[raw-package manifest](../manifests/DEFHS_COMPETITION_DATA_20260930.json) and
[package reconciliation](../runs/DS-DEFHS-VALIDATION-HARDENING-002/OFFICIAL_PACKAGE_RECONCILIATION.md)
preserve its identity. Do not add a recording to resolve the historical
1,036-versus-1,035 organizer-prose discrepancy.

The mission describes approximately **40% of test rows contributing to Public
LB and the other 60% to Private LB**. Treat this as the mission's planning
approximation: exact counts and membership are unknown. The historical
[organizer context](../runs/DS-DEFHS-VALIDATION-HARDENING-002/OFFICIAL_COMPETITION_CONTEXT.md)
establishes 40/60 **score weights**, which alone do not verify row fractions.
Predict every test row; do not infer hidden membership from either statement.

## Active evidence hierarchy

1. **PRIMARY_CV** — existing duplicate/group-safe V-B macro-F1 on labeled
   training speech; the generalization guardrail.
2. **TARGET209_ANALYSIS** — unlabeled target-domain evidence, prediction
   disagreement and uncertainty on those exact test recordings.
3. **PUBLIC_LB** — partial real-test evidence; private performance remains unknown.

These are evidence roles, not three optimization objectives. The competition
objective remains correct TARGET209 predictions under four-class macro-F1.

## Three active model families

| Family | Emotion evidence |
| --- | --- |
| WAVEFORM | Raw waveform, SSL and emotion representations |
| SPECTROGRAM | Log-Mel and time-frequency models |
| SEMANTIC | ASR followed by a Hindi-capable language representation |

Duplicates, provenance, speaker/session hypotheses and recording/source
structure are **AUXILIARY EVIDENCE**. They are not a fourth emotion modality.
The existing certified 77-group / 78-test-clip retrieval map and its deployed
override remain unchanged; uncertain similarity is not a new test label.

The accepted submitted control and `FINAL_SYSTEM_LOCK` remain unchanged.
Wave 1's preferred pair remains an SS-review candidate, and its recorded Drive
checkpoint preservation blocker remains open. This consolidation promotes no
model and reopens no failed or closed experiment.

Read [ACTIVE_VALIDATION](ACTIVE_VALIDATION.md) and
[TARGET209_STRATEGY](TARGET209_STRATEGY.md) next. Consult
[HISTORICAL_VALIDATION_INDEX](HISTORICAL_VALIDATION_INDEX.md) only for a concrete
scientific question. [WORKFLOW](../WORKFLOW.md) still governs execution;
this consolidation authorizes no training, protected query or submission.
