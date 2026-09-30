# Results Preview

Status: reproducible local audit completed against the supplied competition ZIP; full lightweight artifact bundle pending branch sync.

## Verified findings

- Train: 826
- Test: 209
- Total: 1,035
- Sample rate: 16 kHz for all clips
- Exact PCM duplicate groups: 21
- Exact train↔test groups: 8, affecting 8 test clips
- Near-duplicate threshold: full-waveform cosine >= 0.95
- Independent relative-time fingerprint weakest duplicate-cluster similarity: 0.974119
- Strongest non-cluster similarity: 0.209360
- Near-duplicate groups: 227
- Clips in near-duplicate groups: 467
- Train↔test near-duplicate groups: 77
- Affected test clips: 78 / 209 (37.3%)
- Train-label conflict groups: 1 (train IDs 75=neutral, 636=sad, 878=neutral)
- Every train↔test near-duplicate group has a unanimous training label.

## Validation diagnostic

Five-seed handcrafted acoustic RBF-SVM diagnostic:

- V-A row-stratified mean macro-F1: 0.680968 ± 0.014148
- V-B duplicate-safe mean macro-F1: 0.582527 ± 0.007615
- mean leakage premium: +0.098441 macro-F1

## Candidate freeze

- V-A: 5-fold stratified competition-mimic, seed 20260930.
- V-B: 5-fold stratified duplicate-group-safe, seed 20260930.
- V-C speaker/source-disjoint: not frozen because reliable speaker IDs/grouping are unavailable.

The duplicate-retrieval lane must be kept separate from general SER model selection.
