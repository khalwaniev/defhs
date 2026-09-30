# Duplicate Forensics Report

The DS-001 dependency finding was reproduced and hardened.

- high-similarity pair edges: 257
- connected near-duplicate groups: 227
- clips in groups: 467
- train↔test groups: 77
- affected test clips: 78 / 209
- minimum accepted duplicate-pair similarity: 0.97411865
- next strongest non-cluster waveform similarity: 0.20935953
- label-conflict groups: 1

The graph is invariant from threshold 0.21 through 0.974; at 0.975 it begins losing real members. This wide gap makes the 0.95 operational threshold conservative rather than finely tuned.

All 257 accepted edges share sample count and dtype. Many are not byte-identical PCM/files, so the structure includes near-copies/recording variants rather than only literal duplicate files.

All train↔test groups with usable training labels have a unanimous training-label consensus. The retrieval lane therefore remains high-confidence and logically separate from SER model selection.

Policy: keep retrieval deterministic and threshold-frozen; never allow retrieval performance to substitute for non-retrieval SER evidence.
