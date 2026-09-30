# Final Validation Authority

## Verdict
**REVISE_AND_FREEZE**

The DS-001 candidate is retained in backbone but hardened and role-separated.

### Primary model-selection authority — V-B
Five-fold duplicate-family-safe StratifiedGroupKFold, seed 20260930. Use for representation/model-family decisions.

### Competition-mimic secondary authority — V-A
Five-fold stratified row-level CV, seed 20260930. Use to estimate row-random competition-like behavior and retrieval-aware pipeline performance.

### V-C speaker stress
Not frozen. Current evidence cannot establish reliable speaker identities.

### V-D source/format stress
Verified int16-vs-int32 leave-one-regime-out stress. Diagnostic only.

### Retrieval lane
Frozen 0.95 duplicate threshold. Test retrieval applies only to the 78 test clips in the frozen cross-split map and only where training-label consensus is unanimous. Retrieval metrics are reported separately.

### Protected promotion gate
Freeze a new duplicate-safe five-fold StratifiedGroupKFold with seed **20261001**. It has not been used for the current model battery. Fold sizes are 166/166/165/165/164 with near-identical class counts. Routine RS iteration must not query this gate; use it only for promotion checkpoints. Runtime fold CSV SHA-256: `b102eec374967672abc987afe857f689eec47fc104d96ce2f487c6caba26f46c`.

### Small-gain policy
- gains <0.005 macro-F1: do not promote without replication across seeds/folds and non-negative V-D behavior;
- gains 0.005–0.010: require consistent V-B improvement and no material source/format regression;
- larger gains: still require protected-gate confirmation before production promotion.

### Private-LB emulator
Use retrieval-aware V-A pseudo-test simulation plus public-fraction sensitivity (20–50%) and V-B non-retrieval evidence. Never claim equivalence to the hidden leaderboard.

### Label policy
Keep observed labels. The 75/636/878 conflict is a diagnostic family, not an automatic relabel target.

### Heavy artifact
`/DEFHS/ds_validation_002/ACOUSTIC_FEATURES_FULL.csv`, Drive file ID `1vi6Wgcth_3BX7izqIMBFa7I1KMTU38RK`, SHA-256 `d8769829f6e2ca351e96068e64d89b95977cca83acc4a92c14239f0f793ff42d`.

Serious modeling may now begin under this frozen role-separated authority. Any future speaker/ASR evidence may add stress diagnostics but must not silently replace V-A/V-B without a new DS validation revision.
