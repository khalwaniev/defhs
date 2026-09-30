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

## Heavy feature artifact

Path: `/DEFHS/ds_validation_002/ACOUSTIC_FEATURES_FULL.csv`

Drive file ID: `1vi6Wgcth_3BX7izqIMBFa7I1KMTU38RK`

Size: 7,787,538 bytes

Verified SHA-256:
`d8769829f6e2ca351e96068e64d89b95977cca83fb49f0ef7d0d597f11c06a53`

The Drive file was downloaded back into the execution environment and verified byte-identical to the recovered runtime matrix.

## Required future heavy artifacts

After the mandatory closure executors run, store at minimum:

- ECAPA speaker embeddings + metadata + model manifest;
- Hindi ASR transcripts + ASR manifest;
- openSMILE eGeMAPSv02 full feature matrix + manifest;
- joint latent-regime outputs.

These artifacts do not yet exist and must not be represented as completed evidence.
