# DS-002 Latent Join Patch 001

Mission: `DS-DEFHS-VALIDATION-HARDENING-002`

Parent execution authority:

`5be8dd571ed161dd96266cc117a303df232aa648`

Kaggle execution evidence:

`khalwaniev/defhs-ds002-closure`, version 2

## Failure

The latent-regime audit failed before analysis with:

`KeyError: 'filename'`

The script selected:

`Id, split, emotion, dtype, duration_seconds`

from `DATA_MANIFEST.csv`, then attempted a merge on:

`Id, split, filename`

The canonical data manifest already contains `filename`.

## Repair

Add `filename` to the selected manifest columns before the existing merge.

No clustering method, threshold, representation, model, validation design,
protected-fold policy, or interpretation rule is changed.

## Re-execution policy

Do not rerun ECAPA, ASR, or eGeMAPS.

Use the already completed version-2 ECAPA/ASR artifacts and the preserved
version-1 eGeMAPS artifact to execute only the latent-regime audit.
