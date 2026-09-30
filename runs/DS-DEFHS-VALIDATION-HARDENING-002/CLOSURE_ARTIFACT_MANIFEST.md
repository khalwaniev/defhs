# DS-002 Closure Artifact Manifest

## Canonical Drive evidence folder

Path: `/DEFHS/ds_validation_002/canonical_evidence/`

Folder ID: `1COwvq5qYSgBjJs6hnf-vCp94lIRH7VFF`

The lightweight files below were recovered from the valid runtime state, uploaded to Drive, committed to GitHub, and checked for text-byte parity between the preserved Drive copy and GitHub content.

| Artifact | SHA-256 | Drive file ID |
|---|---|---|
| DATA_MANIFEST.csv | 1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469 | 1K72qAYnm3k1vHLyTQK6hZ-A30sJGFs3A |
| DUPLICATE_GROUPS_FINAL.csv | 6aee3374e27efeb1a79397a1256a515b87e3baf4d7a01536191f6e16256e81f7 | 1RXVO1LJn7Rg_D6F7plF8-U9FVyuFeS-g |
| RETRIEVAL_MAP_FINAL.csv | e08f7d06c13d64a1d365d7ae6fa741d6e831dea8816de6663d4a9c0eb113d2a7 | 1JsnJCryDsbOV7GWUAkzi4cCS7uZ3WGcx |
| ACOUSTIC_FEATURE_SUMMARY.csv | 57f0172cc2d231c547f803e44fc8e9dee7d8ac83acc4a92c14239f0f793ff42d | 1vQFIBN4Zp6x050dxKhZpB5mI9d_kUhvK |
| VALIDATION_STABILITY_RESULTS.json | b8eb8c096fe4430cb2230c64dc672f1dafa60384a2db0b9f56bcbd288999f28a | 1VaqM0slmugdtURZ0Zdwk5GowOS4SJvQa |
| VALIDATION_OOF_FIXED.csv | 46bdb12a5651dd51e3d6fe07f9060f7264f5fa2c93a1a97b60ca5965580412aa | 1Dz-2BEoNI6H6kZkcrirBsBlBl0nftfHw |
| VALIDATION_PER_CLASS_F1.csv | e73a63cc71587567d2924a43d7a737445d9dd91ab0c66ce45e57f2d3880a2542 | 1zVijRltb2znI8onarkk5IpBtmrRBdrcb |
| PRIVATE_LB_EMULATOR_RESULTS.json | 2c5a4d06e8dc24268b4ce410f266940977918df030fe6fa10ceaee25d400c371 | 1lLAtEptu1UVo12z-HX04nuGX1uk3aR5a |
| VALIDATION_VA_FOLDS.csv | dcee356b0a66cb73c506bb71a6c57962227d6d0474efd3e4d6c404168308f3d1 | 1DnSBTewpadR1hzof9Hb_Es9gt16_9N-4 |
| VALIDATION_VB_FOLDS.csv | 87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b | 1AQxmJTSA5SaawTiw0AVJAUk1su7ICoRK |
| VALIDATION_VP_PROTECTED_FOLDS.csv | b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c | 1oXOX8CK-X5uy1BsFEhdou-5q6ZFRkq5t |
| VALIDATION_VD_REGIMES.csv | f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839 | 1EthIHmlX13PNfrQGAgmgaiE-L83JZTCF |

## Heavy acoustic feature artifact

Path: `/DEFHS/ds_validation_002/ACOUSTIC_FEATURES_FULL.csv`

Drive file ID: `1vi6Wgcth_3BX7izqIMBFa7I1KMTU38RK`

Size: 7,787,538 bytes

Verified SHA-256:

`d8769829f6e2ca351e96068e64d89b95977cca83fb49f0ef7d0d597f11c06a53`

Producer/reproducer:

- script: `scripts/run_ds_defhs_validation_hardening_002_features.py`;
- script introduction commit: `1f240e3089c4d7bcb29687c246384e3a70ee8ed2`;
- original runtime artifact was produced before that repository preservation commit from the same recovered implementation;
- the Drive copy was downloaded back and verified byte-identical to the recovered runtime matrix during the final closure continuation.

## Closure execution assets

The remaining mandatory analyses have canonical executors:

- `scripts/run_ds002_speaker_ecapa_audit.py`;
- `scripts/run_ds002_asr_prompt_audit.py`;
- `scripts/run_ds002_opensmile_egemaps_audit.py`;
- `scripts/run_ds002_latent_regime_joint_audit.py`;
- `requirements/ds002_closure.txt`.

They must record their own resolved model/package revisions and artifact hashes at execution time.

## Completed closure heavy artifacts

The mandatory closure executors have now run. Scientific interpretation and
the final validation freeze remain pending DS review.

Canonical Drive root:

`/DEFHS/ds_validation_002/`

Drive root folder ID:

`1eVmuoGuCCh8k5zT2MacvM61QHrvHRS-P`

### Speaker / ECAPA

Folder:

`/DEFHS/ds_validation_002/speaker_embeddings/`

Folder ID:

`1goM8ZW1wwcqQv_8SLOIy36YQ8zGM5YZE`

Primary embedding artifact:

- `SPEAKER_EMBEDDINGS_ECAPA.npy`
- Drive ID: `1qim89ihez0eokdkMISZzeWOnOwMnllhH`
- bytes: `795008`
- SHA-256:
  `a96716b5d53942cd6a3044c49c44d1e7cd0ced56416857513a62e131f4a98f42`
- shape: `(1035, 192)`
- model:
  `speechbrain/spkrec-ecapa-voxceleb`
- immutable revision:
  `0f99f2d0ebe89ac095bcc5903c4dd8f72b367286`

### ASR / prompt structure

Folder:

`/DEFHS/ds_validation_002/asr_transcripts/`

Folder ID:

`1Zz3w-I5sUeXQaiDKdYU-ABf_obiA9K-c`

Primary transcript artifact:

- `ASR_TRANSCRIPTS.csv`
- Drive ID: `1d-SvtL_PmzTqL5cICf1DfgfXYUjdV1o7`
- bytes: `268870`
- SHA-256:
  `a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01`
- rows: `1035`
- model:
  `mobiuslabsgmbh/faster-whisper-large-v3-turbo`
- immutable revision:
  `0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf`

### openSMILE eGeMAPS

Folder:

`/DEFHS/ds_validation_002/egemaps/`

Folder ID:

`1Knp7t2E2pOk1fDfzE8-FJCBLsFGXTIQz`

Primary feature artifact:

- `EGEMAPS_FEATURES.csv`
- Drive ID: `19gvsZfhZyhNu_TwK4gzVS17bOTAryYUM`
- bytes: `1769625`
- SHA-256:
  `45476151fa3eaf6fd747495a3827e769bac189cbc347459559734ceb1828a0be`
- rows: `1035`
- openSMILE: `2.6.0`
- feature set: `eGeMAPSv02`
- level: `Functionals`
- descriptors: `88`

### Joint latent regimes

Folder:

`/DEFHS/ds_validation_002/latent_regimes/`

Folder ID:

`1coVc17HYrgEJnxdew_yrL5ZUTDP6XFRO`

Primary assignment artifact:

- `LATENT_REGIME_ASSIGNMENTS.csv`
- Drive ID: `10U5rNKDUNSQ5DZaz1T3eqs3OKABzPkpT`
- bytes: `39752`
- SHA-256:
  `1a67ab36c67b4d8762ee2fadfd55a77b3f68782a5ae1b56073e2a31887556bab`
- rows: `1035`

Audit results:

- `LATENT_REGIME_AUDIT_RESULTS.json`
- Drive ID: `1IeHHsiDyr1YsV5f32vZKNFlhZww5C5X4`
- SHA-256:
  `7096ad7690c5056a411e224898e7979457db849c26e059b2bef055cd417af5ce`

The latent executor explicitly does not label clusters acted/spontaneous without
external ground truth.

### Complete closure inventory

The complete closure artifact table is:

`CLOSURE_COMPLETED_ARTIFACT_MANIFEST.tsv`

It records all preserved closure outputs and provenance with:

- Drive path;
- Drive file ID;
- byte size;
- SHA-256;
- source Kaggle kernel/version;
- producer Git commit;
- model/runtime revision where applicable.

The final uploaded preservation inventory is:

- Drive ID:
  `1nbtfkypqGxH8XH78dnyV8lj8vlRkdAvf`
- SHA-256:
  `28ee56aa6bfa139d45588609e7eea96a05ead527f877a509f96637281be10827`

The protected `VALIDATION_VP_PROTECTED_FOLDS.csv` was not used by these
closure executions.
