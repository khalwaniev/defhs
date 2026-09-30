# Private-LB Emulator Specification — Final Freeze

The internal emulator does **not** claim to know the real hidden public/private
assignment or public/private row fractions.

## Executed emulator

For each pseudo-test evaluation:

1. expose pseudo-train labels only;
2. apply duplicate retrieval only where the pseudo-test clip has a qualifying
   pseudo-train family member;
3. use the SER classifier otherwise;
4. report retrieval-covered and non-retrieval performance separately;
5. compute macro-F1 exactly as the competition metric component.

Public-fraction sensitivity is evaluated at `0.20 / 0.30 / 0.40 / 0.50`.
These are scenarios, not estimates inferred from the 0.40/0.60 final-score
weights.

The preserved 250-replicate class-stratified Monte Carlo study retains the
cheap-model ordering at all tested fractions.

Canonical result:

`PRIVATE_LB_EMULATOR_RESULTS.json`

SHA-256:

`2c5a4d06e8dc24268b4ce410f266940977918df030fe6fa10ceaee25d400c371`

## Final roles

- V-A + retrieval simulation: competition-mimic evidence;
- V-B: duplicate-safe model/representation selection evidence;
- V-D: verified format/source stress;
- protected seed 20261001: confirmation only.

## Closure reconciliation

The completed ECAPA, ASR/prompt, eGeMAPS and joint latent-regime audits do not
identify a stable additional test-relevant mixture mechanism that warrants a
structural revision of the emulator:

- strict reliable ECAPA clustering mostly reproduces duplicate families;
- prompt structure beyond the duplicate graph is limited;
- no-duplicate prompt/class AMI is approximately 0.0075;
- eGeMAPS train/test logistic AUC is approximately 0.476;
- joint latent split NMI is approximately 0.00034-0.00138.

Therefore the existing emulator is retained **without structural revision**.

It remains an emulator, not a guarantee of private-LB equivalence.

No hidden assignment is inferred or reverse-engineered from leaderboard
scores.
