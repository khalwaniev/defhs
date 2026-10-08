# Frozen train826 execution

Status: **PREPARED, NOT EXECUTED — WEB_SECRET_EXECUTION_REQUIRED**.

The successful preflight is byte-verified in `preflight/`. The new execution
script is `kaggle/rs_defhs_pocket_mimi_train826_001/run.py`; its exact checksum and
allowlisted inputs are in `PHASE1_EXECUTION_PACKAGE.json`. The unchanged preflight
script is retained in its original directory.

The generated script is self-contained. It packages the original frozen V-B
membership bytes with their original hash and identity; it creates no new
competition folds. It also packages only the 826 training manifest rows, the
accepted eight-vector preflight reference, and accepted source provenance.
The input manifest's full original file hash is recorded for the train-only
selection, but no test row is included. No repository, protected artifact,
target prediction, credential, model checkpoint, or AST model is packaged.

## Manual execution

The installed Kaggle CLI 2.2.3 `kernels push` and `ApiSaveKernelRequest` expose no
secret attachment field. A push automatically executes a version, so no CLI
push or run was attempted without evidence of secret preservation.

Use the existing `khalwaniev/defhs-pocket-mimi-preflight-001` notebook. Replace
its script contents with the exact generated `run.py` above. Retain enabled
`HF_TOKEN`, enable Internet, select CPU with no GPU, and perform Save Version /
Run All. Do not enter the secret value into source, chat, or a terminal. The
existing successful preflight version remains preserved in Kaggle history.

The runner downloads only the authorized gated checkpoint, verifies its exact
revision, byte count and SHA256, validates strict Mimi loading and non-degenerate
encoder tensors, and performs a synthetic smoke test. Source code is imported
directly from the verified exact checkout as in the accepted preflight.

Every training WAV must match its frozen file hash, channel count and sample
count. All 826 rows use the same mono 24-kHz resampling, continuous `[1,T,32]`
latents, and 64-D temporal mean/population-standard-deviation pooling. Before
modeling, all eight accepted preflight vectors must agree within `1e-7`, and all
eight are re-extracted to check repeatability. Invalid identities, nonfinite
values, hash mismatches, or numerical failures stop execution.

The classifier is exactly the predeclared StandardScaler followed by multinomial
L2 LogisticRegression, `C=1`, `solver=lbfgs`, `max_iter=5000`, and
`random_state=20261007`. The scaler and classifier fit each training fold only;
the existing validation fold receives probabilities in fixed class order.
Scikit-learn is pinned to 1.7.2; convergence failures stop rather than trigger a
search. No uncertainty procedure was prescribed for this mission, so none is
added. The five ordinary PRIMARY_CV folds remain unchanged.

## Retrieve after execution

Outputs are under `rs_defhs_pocket_mimi_train826_001/`:

- `TRAIN826_FEATURES.csv` and `TRAIN826_FEATURES.npz`
- `TRAIN826_WAV_PROVENANCE.csv`, `TRAIN826_PROVENANCE.json`, and `FEATURE_VALIDATION.json`
- `POCKET_MIMI_OOF_PRIMARY_CV.csv` and `PRIMARY_CV_RESULTS.json`
- `CHECKPOINT_SHA256.txt`, `SCRIPT_SHA256.txt`, and `ARTIFACT_MANIFEST.json`
- `EXECUTION_STATUS.json`, or `EXECUTION_FAILURE.json` on failure

The runner stops after extraction and standalone PRIMARY_CV. It does not run
fusion, protected validation, TARGET209 extraction, generation, voice
conditioning, or submission. Model and source caches live in temporary storage
outside Kaggle working outputs; the scientific feature artifacts remain in the
working output directory.

On ERROR, retrieve logs and failure stage and diagnose before any rerun. No
scientific verdict is inferred from an infrastructure failure or unexecuted code.

## Bounded complementarity after valid OOF

`scripts/analyze_pocket_mimi_complementarity.py` is prepared for descriptive
corrections, breakages, error overlap, per-class structure, and distribution
across the existing five folds. It requires successful extraction/OOF manifests,
the exact candidate script hash, and authoritative reference hashes. It performs
no probability blend, weight selection, ensemble search, or label-driven cohort
construction.

The waveform-pair and emotion2vec reference binaries are locally available and
byte-verified against `PROBABILITY_ARTIFACT_INVENTORY.json`. System C's published
aggregate and fold metrics are preserved, but its row-level OOF artifact has not
been located. A trusted checksum and that artifact are required for System C
correction/error-overlap analysis; matching aggregate scores alone is insufficient
provenance. No AST results or model are used.

The existing complementarity verdict gate and any permitted train-side HARD
definitions were requested because this mission's files do not supply quantitative
criteria or a train-side HARD cohort definition. They are not replaced with new
thresholds or newly selected cohorts. The helper leaves final scientific judgment
pending. TARGET209 remains **NOT AUTHORIZED** until train evidence is evaluated
and SS explicitly authorizes that next stage.

## Local verification limits

Tests exercise corrupted membership, invalid features, held-out perturbations that
must not affect fitted training-fold parameters, and paired error-count accounting.
They use no checkpoint and no competition feature scoring. They do not establish
that full extraction has run successfully; that requires the actual Kaggle output.

One mixed-split metadata row was inadvertently previewed while locating schemas;
this is recorded in `SCOPE_AUDIT.json`. No target audio or target predictions were
accessed or used, and the new package contains training rows only.
