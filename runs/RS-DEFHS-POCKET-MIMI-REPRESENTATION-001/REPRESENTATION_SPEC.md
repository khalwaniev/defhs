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

## Active authority after SS checkpoint patch and successful preflight

The initial checkpoint entry above is historical and rejected because its encoder
is intentionally zeroed. The active checkpoint is ONLY
`kyutai/pocket-tts/languages/english_2026-09/model.safetensors` at revision
`983151f13aaeab1b13c1e5e3c2c383d49a9edf3f`, SHA256
`fb0dc01b0d4d2e1c905b7a3e0676e3d9c96d5ae460e24e3ab94981805babf997`.
The canonical preflight passed with a real, non-degenerate encoder. Its script
SHA256 is `de06571b0e206db519c25be1b8a550c6d1391c29cd381cf582e1788936ee6d81`.

Representation 2 remains NONE. All representation and downstream classifier
choices above remain frozen. Existing train WAVs are mono (826/826), and the new
runner checks that fact and uses the identical upstream deterministic resampling
and pooling calls; it introduces no alternative channel-mixing rule. The eight
accepted real-audio preflight vectors provide an additional numerical parity gate
before full features can enter modeling.
