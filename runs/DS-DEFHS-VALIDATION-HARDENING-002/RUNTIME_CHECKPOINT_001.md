# DS-DEFHS-VALIDATION-HARDENING-002 — Runtime Checkpoint 001

Checkpoint purpose: preserve completed continuation work before any further expensive analysis.

## Authority
- starting authority: `6f431b1bbdca353d4a8b8ce9cc7a74cbe5bc74a5`
- branch: `ds/validation-hardening-002`
- canonical raw ZIP SHA-256: `100b38e6ed69542df88c1d295932a7a4c1914cd931ee64f7c6c848f6053bf214`
- canonical raw ZIP size: 99,298,085 bytes

## Reproduced / completed evidence
- 826 train + 209 test = 1,035 supplied examples.
- IDs are a complete permutation of 1..1035 with no train/test overlap.
- All 1,035 WAVs are mono 16 kHz; 933 int16 and 102 int32.
- Duplicate graph reproduced: 257 high-similarity edges, 227 connected groups, 467 clips.
- 77 train↔test groups affect 78 / 209 test clips.
- Duplicate-pair gap remains extreme: minimum accepted pair similarity 0.97411865; next strongest non-cluster waveform similarity 0.20935953.
- Duplicate grouping is invariant across a broad threshold interval through approximately 0.974.
- One train-only conflicting family remains IDs 75 / 636 / 878 with labels neutral / sad / neutral.
- Acoustic feature matrix contains 1,035 rows and ~402 columns.
- ID-only split predictability is near chance (mean AUC ~0.508); train/test ordering is broadly consistent with row-random assignment.
- Adversarial validation on all clips is near chance for both logistic regression and ExtraTrees.
- After excluding cross-split duplicate families, logistic regression remains near chance but ExtraTrees gives a modest repeatable nonlinear split signal: mean AUC 0.58055, SD 0.01048 across three saved seeds. Treat as a distribution-shift stress signal, not proof of a separate corpus.
- Validation battery has been run across V-A / V-B with multiple low-cost model families and retrieval-aware pseudo-test logic.

## Heavy artifact authority
Full acoustic feature matrix is stored outside GitHub:
- Drive folder: `/DEFHS/ds_validation_002/`
- Drive folder ID: `1eVmuoGuCCh8k5zT2MacvM61QHrvHRS-P`
- file: `ACOUSTIC_FEATURES_FULL.csv`
- Drive file ID: `1vi6Wgcth_3BX7izqIMBFa7I1KMTU38RK`
- local/runtime SHA-256: `d8769829f6e2ca351e96068e64d89b95977cca83acc4a92c14239f0f793ff42d`
- size: 7,787,538 bytes
- producer: runtime `defhs_feature_audit.py`

## Runtime script checksums
- `defhs_core_analysis.py`: 88be1ef7b70556774fbcb949b22d8929455b3ce12ed965c32a0d214d51dbb8c0
- `defhs_feature_audit.py`: 1b22fc115eb14c9a68b8c63b290365a2ce24b6780379230c4415eb132726d6fb
- `defhs_validation_battery.py`: 91481c2e29c1e00182f528cc8c54f7d66c8052a0eb8f8ba80581fc3eeeb15ff7

This is an intermediate checkpoint, not a final validation freeze.
