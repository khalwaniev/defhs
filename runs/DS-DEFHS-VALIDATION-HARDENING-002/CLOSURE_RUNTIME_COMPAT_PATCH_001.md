# DS-002 Closure Runtime Compatibility Patch 001

Mission: `DS-DEFHS-VALIDATION-HARDENING-002`

Parent execution authority:

`c82bb7bde5fff16771c2f08f491d54a1468cdc14`

Kaggle execution:

`khalwaniev/defhs-ds002-closure`, version 1

## Scope

Runtime compatibility only.

No validation design, model ID, clustering threshold, scientific method,
protected-fold policy, or audit logic is changed.

## Version-1 evidence

ECAPA failed before model inference because SpeechBrain 1.0.3 called:

`torchaudio.list_audio_backends()`

which is absent from the current Kaggle TorchAudio runtime.

ASR downloaded the authorized pretrained model but failed at audio decoding
because the installed PyAV removed the `metadata_errors` argument still used
by faster-whisper 1.1.1.

The eGeMAPS stage succeeded and must not be recomputed merely because the
other two stages failed.

Preserved v1 eGeMAPS artifacts:

- `EGEMAPS_FEATURES.csv`
  - SHA-256 `45476151fa3eaf6fd747495a3827e769bac189cbc347459559734ceb1828a0be`
  - 1,035 rows
- `EGEMAPS_SHIFT_SUMMARY.csv`
  - SHA-256 `bb6fab1803f88f66ef7c98ca53aca4d4ae4e83f454ba11d72a37062c867afb39`
  - 88 rows
- `EGEMAPS_AUDIT_RESULTS.json`
  - SHA-256 `9533c9aa340c61cfe332906d02bc853312cfc6fbf2dfc7d299a448856cf293b4`
- `EGEMAPS_MANIFEST.json`
  - SHA-256 `712176a014a09e60dfe6f61f14640a0b7f500c74fd6e86743856f47afeafd0d6`

## Minimal compatibility changes

1. `speechbrain==1.0.3` -> `speechbrain==1.1.0`

   Reason: use the upstream release compatible with TorchAudio versions where
   `list_audio_backends()` has been removed.

2. Add `av==18.1.0`

   Reason: faster-whisper 1.1.1 still invokes
   `av.open(..., metadata_errors="ignore")`; PyAV 19 removed that API.
   PyAV 18.1.0 retains the compatible API and provides Python 3.12 wheels.

## Re-execution policy

Kaggle version 2 must:

- rerun ECAPA only;
- rerun ASR only;
- reuse the preserved version-1 eGeMAPS artifacts byte-for-byte;
- run the joint latent-regime audit only after ECAPA and ASR succeed;
- not execute or package `VALIDATION_VP_PROTECTED_FOLDS.csv`;
- not rerun main EDA or begin SER modeling.
