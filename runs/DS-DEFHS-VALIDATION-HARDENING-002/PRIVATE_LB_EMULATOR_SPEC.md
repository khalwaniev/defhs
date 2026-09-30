# Private-LB Emulator Specification — Closure Reissue

The internal emulator does **not** claim to know the real hidden public/private assignment or public/private row fractions.

## Executed preserved emulator

For each pseudo-test evaluation:

1. expose pseudo-train labels only;
2. apply duplicate retrieval only where the pseudo-test clip has a qualifying pseudo-train family member;
3. use the SER classifier otherwise;
4. report retrieval-covered and non-retrieval performance separately;
5. compute macro-F1 exactly as the competition objective component.

Public-fraction sensitivity is evaluated at 0.20 / 0.30 / 0.40 / 0.50. These are scenarios, not estimates inferred from the 0.40/0.60 score weights.

The preserved 250-replicate class-stratified Monte Carlo study retains the cheap-model ordering at all tested fractions.

Canonical result:

`PRIVATE_LB_EMULATOR_RESULTS.json`

SHA-256:
`2c5a4d06e8dc24268b4ce410f266940977918df030fe6fa10ceaee25d400c371`

## Current intended roles

- V-A + retrieval simulation: competition-mimic evidence;
- V-B: duplicate-safe model-family evidence;
- V-D: verified format/source stress;
- protected seed 20261001: confirmation only.

## Closure limitation

Speaker-like clusters, prompt/script families, and strengthened latent regime evidence are still pending. If those reveal a test-relevant mixture mechanism not represented by current pseudo-test sampling, the emulator specification may require a bounded revision.

Therefore this emulator remains valid executed evidence, but its **finality is provisional** until the mandatory speaker/ASR/eGeMAPS closure is complete.

No hidden assignment is inferred or reverse-engineered from public scores.
