# Stage 1 scaffold — common frozen representation execution package

Mission: `RS-DEFHS-SYSTEM-IMPLEMENTATION-001`

Status: **IMPLEMENTED / GPU EXECUTION PENDING**

## Scope

The package at `kaggle/rs_system_implementation_001_frozen_screen/` implements the frozen Stage-1 scaffold and the currently executable bounded Stage-2/Stage-3 screen:

- emotion2vec base only: `iic/emotion2vec_base@v2.0.4` from ModelScope;
- XLS-R-300m only: `facebook/wav2vec2-xls-r-300m@1a640f32ac3e39899438a2931f9924c02f080a54`;
- Vesper-4 remains deferred/unavailable;
- WavLM-large remains deferred on weight terms;
- no replacement models are introduced.

## Validation safety

The executable embeds byte-exact V-B and V-A fold authorities and verifies their recorded SHA256 values before use.

It does **not** package, locate, read, or query `VALIDATION_VP_PROTECTED_FOLDS.csv`.

V-B is the primary representation/model-selection view. V-A is secondary. Retrieval is not mixed into V-B.

## Representation protocol

- canonical 16 kHz audio;
- frozen encoders;
- cached frame-level representations;
- common mean+std pooling;
- L2 multinomial logistic head;
- calibrated RBF-SVM head;
- duplicate-group-safe inner calibration for V-B RBF probabilities;
- deterministic seeds;
- two-pass parity probe on three fixed V-B IDs before full extraction.

emotion2vec acquisition is hard-wired to ModelScope `hub="ms"` and exact revision `v2.0.4`. There is no Hugging Face fallback. The resolved ModelScope cache tree is SHA256-inventoried before competition extraction.

## Static smoke work completed in the chat runtime

The common pooling and OOF-head logic was exercised on synthetic fold-aligned embeddings under CPU to catch implementation/schema failures. No synthetic result is entered as scientific evidence.

Actual foundation-model extraction was not executed in the chat runtime because that runtime has no CUDA accelerator or authenticated Kaggle execution surface. No model score is claimed.

## Kaggle package inputs

- competition source: `dataverse-detecting-emotions-from-hindi-speech`;
- prior-kernel source: `khalwaniev/defhs-ds002-closure` solely to supply the canonical hashed `DATA_MANIFEST.csv`;
- internet enabled solely for the two public pretrained assets and pinned runtime dependencies.

Expected heavy outputs are written under:

`/kaggle/working/rs_defhs_system_implementation_001/`

They include frame caches, pooled arrays, OOF probabilities/predictions, Stage-1 parity records, frozen-screen results, resolved emotion2vec object hashes, environment versions and an output inventory.

## Non-actions

- protected validation: **NOT QUERIED**;
- Kaggle submission: **NOT MADE**;
- PEFT: **NOT STARTED**;
- model zoo expansion: **NO**.
