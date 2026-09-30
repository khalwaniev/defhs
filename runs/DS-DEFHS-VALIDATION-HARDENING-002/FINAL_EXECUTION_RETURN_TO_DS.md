# Final Execution Return to DS

Mission: `DS-DEFHS-VALIDATION-HARDENING-002`

Status:

**EXECUTION_COMPLETE_AWAITING_DS_INTERPRETATION**

This return records bounded closure execution only. It does **not** issue
`PASS_FREEZE` or `REVISE_AND_FREEZE`. Scientific interpretation and final
validation freeze remain the responsibility of the DS mission.

## Final Git execution authority before this return

`6292e2c4714b44f56b1c51acd4d3100e996c5e1b`

## Executions

### Closure kernel version 1

Kernel:

`khalwaniev/defhs-ds002-closure`, version 1

Git authority:

`c82bb7bde5fff16771c2f08f491d54a1468cdc14`

Outcome:

- eGeMAPS: SUCCESS;
- ECAPA: failed before inference because SpeechBrain 1.0.3 was incompatible
  with the Kaggle TorchAudio runtime;
- ASR: failed at decode because the active PyAV API was incompatible with
  faster-whisper 1.1.1;
- latent: skipped because ECAPA/ASR dependencies were unavailable;
- protected VP gate queried: NO.

### Closure kernel version 2

Kernel:

`khalwaniev/defhs-ds002-closure`, version 2

Git authority:

`5be8dd571ed161dd96266cc117a303df232aa648`

Minimal execution-only compatibility changes:

- `speechbrain==1.1.0`;
- `av==18.1.0`.

Outcome:

- ECAPA: SUCCESS;
- ASR: SUCCESS;
- eGeMAPS: reused byte-for-byte from version 1;
- latent: failed before analysis due a deterministic join bug:
  `KeyError: 'filename'`;
- protected VP gate queried: NO.

### Final latent-only kernel

Kernel:

`khalwaniev/defhs-ds002-latent-final`, version 1

Git authority:

`6292e2c4714b44f56b1c51acd4d3100e996c5e1b`

Repair:

- added the already-existing `filename` field from `DATA_MANIFEST.csv` to the
  left-hand manifest selection before the existing
  `Id, split, filename` merge;
- no clustering, representation, threshold, interpretation rule, or
  validation design changed.

Outcome:

- latent-regime audit: SUCCESS;
- assignments: 1,035 rows;
- evaluated k: 2, 3, 4, 5, 6;
- local preflight versus Kaggle:
  assignments byte-identical and material result difference count = 0;
- protected VP gate queried: NO.

## Completed mandatory evidence

### ECAPA speaker-like audit

Model:

`speechbrain/spkrec-ecapa-voxceleb`

Resolved immutable revision:

`0f99f2d0ebe89ac095bcc5903c4dd8f72b367286`

Embedding shape:

`(1035, 192)`

Key descriptive evidence:

- duplicate-pair embedding similarity median:
  `0.9999968409538269`;
- nonduplicate similarity p95:
  `0.38857135772705076`;
- nonduplicate similarity p99:
  `0.5092418485879889`;
- cluster assignments remain speaker-like hypotheses only; organizer speaker
  IDs are not asserted.

### Hindi ASR / prompt audit

Model:

`mobiuslabsgmbh/faster-whisper-large-v3-turbo`

Resolved immutable revision:

`0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf`

Evidence:

- rows: 1,035;
- empty transcripts: 0;
- exact repeated-transcript rows: 338;
- duplicate text-similarity median: 1.0;
- train-class NMI across prompt sweeps is approximately 0.350-0.353.

Transcripts remain machine-generated audit evidence, not organizer ground truth.

### eGeMAPS audit

Runtime:

- openSMILE `2.6.0`;
- feature set `eGeMAPSv02`;
- level `Functionals`;
- descriptors: 88;
- rows: 1,035.

Evidence:

- train/test adversarial logistic AUC mean:
  `0.476416387656352`;
- V-A OOF macro-F1:
  `0.5753536951338543`;
- V-B OOF macro-F1:
  `0.5601482021030706`.

### Joint latent-regime audit

Evidence:

- acted/spontaneous ground truth available: NO;
- selected central speaker-like column: `agg_d0.30`;
- selected central prompt-like column: `prompt_sim_0.90`;
- eGeMAPS PCA explained variance:
  `0.6422806137275557`;
- silhouette range over k=2..6:
  approximately `0.1061` to `0.1626`;
- split NMI range:
  approximately `0.00034` to `0.00138`;
- dtype NMI range:
  approximately `0.00131` to `0.05579`.

The executor does not name latent clusters acted/spontaneous.

## Artifact preservation

Canonical Drive root:

`/DEFHS/ds_validation_002/`

Drive root folder ID:

`1eVmuoGuCCh8k5zT2MacvM61QHrvHRS-P`

Verified closure folders:

- `speaker_embeddings/`
  - folder ID `1goM8ZW1wwcqQv_8SLOIy36YQ8zGM5YZE`
- `asr_transcripts/`
  - folder ID `1Zz3w-I5sUeXQaiDKdYU-ABf_obiA9K-c`
- `egemaps/`
  - folder ID `1Knp7t2E2pOk1fDfzE8-FJCBLsFGXTIQz`
- `latent_regimes/`
  - folder ID `1coVc17HYrgEJnxdew_yrL5ZUTDP6XFRO`
- `provenance/`
  - folder ID `1Kg11Wvq74kTGxmsheaWN6g8V_OkGo1sM`

Drive preservation was verified after upload. The closure folders/files were
reported as not shared.

Full filename, byte-size, SHA-256, Drive file ID, kernel/version, producer
commit, and model/runtime provenance are recorded in:

`CLOSURE_COMPLETED_ARTIFACT_MANIFEST.tsv`

The uploaded preservation inventory itself is:

- Drive file ID:
  `1nbtfkypqGxH8XH78dnyV8lj8vlRkdAvf`
- SHA-256:
  `28ee56aa6bfa139d45588609e7eea96a05ead527f877a509f96637281be10827`

## Protected validation authority

`VALIDATION_VP_PROTECTED_FOLDS.csv` was not packaged or queried by the closure
executions.

No exploratory decision in this execution return uses the protected VP gate.

## Required DS continuation

The execution worker stops here.

DS should now interpret the completed evidence and, under the existing
governing mission:

1. update the speaker/transcript/acted-spontaneous/source/shift reports;
2. decide whether V-C is scientifically reliable enough to freeze;
3. reconcile the latent-regime evidence with V-D and the existing validation
   backbone;
4. reissue the unknown register and validation certificate;
5. reissue `FINAL_VALIDATION_AUTHORITY.md` with the DS-selected
   `PASS_FREEZE` or `REVISE_AND_FREEZE` disposition;
6. return the resulting validation authority to SS.

No main SER modeling authorization is issued by this execution return.
