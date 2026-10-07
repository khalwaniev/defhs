# Frozen representation specification

Status: **predeclared but NOT EXECUTED because Phase 0 is policy-blocked**.

## Representation 1 — POCKET_MIMI_CONTINUOUS_MEANSTD

Pinned implementation:
- pocket-tts v3.3.0
- repository commit `3dbee45d343d7dddd0d105468d17f8dcba14db3e`
- `MimiModel.encode_to_latent`
- no-voice-cloning checkpoint revision `e7205b6ee50e654a5ea19f0e9df2b0813b05e921`

Input construction:
1. read competition WAV;
2. convert deterministically to mono;
3. resample deterministically to 24,000 Hz;
4. float waveform, no augmentation, no text, no synthesis;
5. feed `[1,1,T]` waveform to `mimi.encode_to_latent`.

Tensor:
- continuous, unquantized latent;
- shape `[1, frames, 32]`;
- nominal frame rate 12.5 Hz.

Pooling:
For latent sequence (Z\in\mathbb{R}^{T\times32}),

`mu_j = (1/T) * sum_t Z[t,j]`

`sigma_j = sqrt((1/T) * sum_t (Z[t,j]-mu_j)^2)`

Feature vector:
`[mu_1..mu_32, sigma_1..sigma_32]` = **64 dimensions**.

Use population standard deviation (`correction=0` / `unbiased=False`) for deterministic behavior.

## Representation 2

**NONE AUTHORIZED.**

The FlowLM voice-conditioning projection is deliberately excluded from this mission's first screen because it is a TTS/voice-cloning-specific transformation and would make the test less clean. No layer sweep, quantized token stream, hidden-state fishing, neural pooling, or alternative checkpoint search is allowed.

## Intended downstream probe if policy is cleared

Exactly the frozen PRIMARY_CV folds.

Per fold:
- StandardScaler fit on train fold only;
- multinomial L2 LogisticRegression;
- C=1.0;
- solver=lbfgs;
- max_iter=5000;
- fixed random_state=20261007.

Metric: macro-F1.

This specification is frozen before any labeled representation scoring.
