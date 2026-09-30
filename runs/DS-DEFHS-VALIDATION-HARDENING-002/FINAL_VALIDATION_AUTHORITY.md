# Final Validation Authority

Mission: `DS-DEFHS-VALIDATION-HARDENING-002`

## Verdict

**REVISE_AND_FREEZE**

All mandatory evidence-completion audits have executed. Their interpretation
supports the existing V-A/V-B/V-D backbone with refined final roles rather
than a redesign.

## Scientific reconciliation

### Speaker evidence

ECAPA-TDNN was executed over all 1,035 clips.

Model:

`speechbrain/spkrec-ecapa-voxceleb@0f99f2d0ebe89ac095bcc5903c4dd8f72b367286`

The strict stable clustering region overwhelmingly reproduces frozen duplicate
families. Substantial additional grouping appears only as the distance
threshold becomes more permissive, where threshold-to-threshold stability
falls materially.

Therefore speaker-like structure is useful diagnostically but does not support
a uniquely identified independent speaker-disjoint validation authority.

### Prompt/script evidence

Hindi ASR was executed over all 1,035 clips.

Model:

`mobiuslabsgmbh/faster-whisper-large-v3-turbo@0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf`

At prompt similarity 0.90, 170 non-singleton prompt clusters cover 367 clips,
but 155 clusters / 321 clips are already contained inside duplicate families.
Only 15 clusters / 46 clips add repeated-prompt structure beyond duplicate
grouping.

Training prompt/class raw NMI is approximately 0.3509, but AMI is
approximately 0.0601; after removing all duplicate-family clips, AMI falls to
approximately 0.0075.

No prompt-grouped validation is frozen.

### Standardized paralinguistic evidence

openSMILE 2.6.0 eGeMAPSv02 Functionals:

- 1,035 rows;
- 88 descriptors;
- train/test adversarial logistic AUC mean: `0.476416387656352`;
- V-A OOF macro-F1: `0.5753536951338543`;
- V-B OOF macro-F1: `0.5601482021030706`;
- maximum absolute univariate train/test SMD: approximately `0.150`.

No material new shift requires a validation redesign.

### Joint latent-regime evidence

Over k=2..6:

- silhouette approximately 0.106-0.163;
- split NMI approximately 0.00034-0.00138;
- dtype NMI approximately 0.0013-0.0558;
- adjacent-k ARI approximately 0.35-0.66.

No strong/stable latent regime is identified. Exact organizer
acted/spontaneous labels remain unresolvable.

## Frozen validation architecture

### V-A — competition-mimic secondary view

Five-fold stratified row-level CV, seed `20260930`.

Canonical membership:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VA_FOLDS.csv`

SHA-256:

`dcee356b0a66cb73c506bb71a6c57962227d6d0474efd3e4d6c404168308f3d1`

Role: secondary competition-like estimator and retrieval-aware pipeline view.

### V-B — primary duplicate-safe selection authority

Five-fold duplicate-family-safe StratifiedGroupKFold, seed `20260930`.

Canonical membership:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VB_FOLDS.csv`

SHA-256:

`87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b`

Role: primary representation/model-family selection authority. Use it to
prevent duplicate memorization from selecting SER systems.

### V-C — speaker-like stress

**REJECTED AS AUTHORITATIVE.**

Do not create a frozen speaker-disjoint split from the ECAPA threshold sweep.

ECAPA assignments may be used only as diagnostic/stress evidence unless future
independent ground truth or materially stronger identification becomes
available.

### V-D — verified recording-format/source stress

Canonical membership:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VD_REGIMES.csv`

SHA-256:

`f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839`

Role: diagnostic robustness stress across observed int16/int32 recording
regimes. It is not the primary leaderboard estimator.

## Retrieval lane

Retain the deterministic duplicate retrieval lane:

- frozen similarity threshold: `0.95`;
- 77 train-test duplicate groups;
- 78 / 209 test clips mapped;
- usable train labels unanimous within every mapped group.

Canonical map:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/RETRIEVAL_MAP_FINAL.csv`

SHA-256:

`e08f7d06c13d64a1d365d7ae6fa741d6e831dea8816de6663d4a9c0eb113d2a7`

Retrieval must remain separate from non-retrieval SER performance.

## Private-LB emulator

The retrieval-aware V-A pseudo-test simulation and 20/30/40/50% public-fraction
sensitivity remain the final internal competition emulator.

Canonical results:

`PRIVATE_LB_EMULATOR_RESULTS.json`

SHA-256:

`2c5a4d06e8dc24268b4ce410f266940977918df030fe6fa10ceaee25d400c371`

New speaker/prompt/eGeMAPS/latent evidence does not justify a structural
revision.

## Protected promotion gate

Duplicate-safe StratifiedGroupKFold, seed `20261001`.

Canonical exact membership:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VP_PROTECTED_FOLDS.csv`

SHA-256:

`b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c`

Fold sizes: 166 / 166 / 165 / 165 / 164.

The gate remains untouched by closure execution and DS interpretation. It is
not an exploratory tuning oracle.

## Promotion discipline

- improvement < `0.005` macro-F1: do not promote without replication and
  non-negative relevant stress evidence;
- improvement `0.005-0.010`: require consistent V-B evidence and no material
  V-D regression;
- larger improvements still require protected-gate confirmation before final
  promotion after development selection.

## Label policy

The 75/636/878 conflict remains observed evidence. Do not automatically
relabel or delete it. Broader model-disagreement candidates are diagnostics,
not annotation truth.

## Artifact authority

Full heavy-artifact provenance is canonical in:

`CLOSURE_COMPLETED_ARTIFACT_MANIFEST.tsv`

Primary Drive root:

`/DEFHS/ds_validation_002/`

Final reproduced interpretation diagnostics:

`FINAL_INTERPRETATION_DIAGNOSTICS.json`

## Modeling authorization

The DS scientific foundation is frozen sufficiently for serious SER modeling.

**Main RS SER modeling may begin under this validation authority once SS
independently accepts the freeze.**

RS must use V-B as the primary selection authority, V-A as the secondary
competition-mimic view, V-D as robustness stress, preserve the retrieval lane
separately, and keep the protected seed 20261001 unqueried until an appropriate
promotion decision.
