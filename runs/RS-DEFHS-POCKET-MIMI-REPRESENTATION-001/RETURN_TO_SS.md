# RS-DEFHS-POCKET-MIMI-REPRESENTATION-001 — execution continuation

Historical evidence is preserved:
- policy blocker was resolved;
- the no-voice-cloning checkpoint was correctly rejected because its Mimi encoder is intentionally zeroed;
- kernel v1/v2/v3 remain infrastructure incidents, not scientific evidence.

## SS checkpoint authority

SS now explicitly authorizes ONLY:

`kyutai/pocket-tts/languages/english_2026-09/model.safetensors@983151f13aaeab1b13c1e5e3c2c383d49a9edf3f`

`FULL_CHECKPOINT_ACCESSIBILITY_STATUS=PASS_REASONABLY_ACCESSIBLE`
`FULL_CHECKPOINT_USE_AUTHORIZED=YES`

The Hugging Face gate must be respected. If the user's account has not accepted Kyutai's conditions or Kaggle cannot obtain an authorized token, stop with `ACCESS_SETUP`.

## Frozen science

Unchanged:
- Pocket-TTS v3.3.0
- source commit `3dbee45d343d7dddd0d105468d17f8dcba14db3e`
- `MimiModel.encode_to_latent`
- mono deterministic 24 kHz
- continuous unquantized [T,32]
- temporal population mean + population std (correction=0)
- 64 dimensions
- no second representation
- frozen PRIMARY_CV
- fixed linear probe
- no fusion
- no TARGET209 unless verdict gate passes
- no submission

## Current state

Checkpoint validation / CPU preflight: PENDING.
PRIMARY_CV: NOT RUN.
TARGET209: NOT RUN.
GPU: NOT USED.
Submission: NONE.
