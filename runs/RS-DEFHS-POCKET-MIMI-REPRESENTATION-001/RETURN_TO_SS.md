# RS-DEFHS-POCKET-MIMI-REPRESENTATION-001 — Return to SS

## Mission status

**BLOCKED at Phase 0.**

This is a governance blocker, not a scientific negative result.

## What was established

Pocket-TTS is technically suitable for the intended representation-only experiment:

- official code: `kyutai-labs/pocket-tts`
- stable release: v3.3.0
- pinned release commit: `3dbee45d343d7dddd0d105468d17f8dcba14db3e`
- code license: MIT
- current weight metadata: CC-BY-4.0
- codec: continuous Mimi-derived VAE-style encoder
- waveform-only extraction: yes
- text/TTS generation required: no
- arbitrary Hindi waveform can technically be encoded: yes
- input: mono 24 kHz
- output: continuous unquantized `[B,T,32]`
- frame rate: 12.5 Hz
- primary representation frozen before scoring: temporal mean + population std = 64 features
- second representation: not authorized

Preferred exact weight authority for the codec-only study:
`kyutai/pocket-tts-without-voice-cloning/languages/english_2026-09/model.safetensors@e7205b6ee50e654a5ea19f0e9df2b0813b05e921`

The current architecture is scientifically plausible for emotion transfer: Kyutai explicitly trains the continuous codec latent with WavLM semantic distillation, while the technical report states that voice prompts preserve voice, emotion, accent, cadence, and acoustic conditions. This is a hypothesis, not evidence of DEFHS performance.

## Why execution stopped

The mission requires explicit compatibility with the official competition external-model policy.

The public DEFHS Kaggle page available to this worker confirms the task/evaluation but did not expose the external-model rule clause. The repository's own `docs/EXTERNAL_DATA_POLICY.md` is conditional: external models/data may be used only if the competition rules allow them and they are sufficiently accessible/reproducible.

No authoritative preserved DEFHS rule text was found that explicitly permits or prohibits external pretrained models.

Therefore:
`POLICY_STATUS=UNVERIFIED_EXTERNAL_MODEL_PERMISSION`

The mission's Phase-0 instruction says to STOP and return BLOCKED when model/license/policy suitability cannot be established.

## What was deliberately NOT done

- no model checkpoint was executed;
- no WAV was encoded;
- no CPU preflight was scored;
- no PRIMARY_CV query was consumed;
- no representation variant was selected from validation;
- no fusion was trained;
- no TARGET209 extraction was run;
- no protected validation was queried;
- no Public-LB tuning occurred;
- no Kaggle submission occurred.

## SS decision required

Please obtain or preserve the exact official DEFHS rule clause governing external pretrained models.

If external pretrained models are allowed under a reasonable-access standard, resume **this same mission** at Phase 1 using the already frozen `POCKET_MIMI_CONTINUOUS_MEANSTD` representation. Do not reopen representation selection.

If external pretrained models are prohibited, close this direction permanently.

FINAL_VERDICT = `BLOCKED_EXTERNAL_MODEL_POLICY_UNVERIFIED`
