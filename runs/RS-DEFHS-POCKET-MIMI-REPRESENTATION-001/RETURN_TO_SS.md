# RS-DEFHS-POCKET-MIMI-REPRESENTATION-001 — Return to SS

## Mission status

**BLOCKED / INVALID under the currently frozen checkpoint authority.**

This is not a negative scientific result for Mimi.

## Policy

The earlier competition-policy blocker remains resolved:

`POLICY_STATUS=PASS_EXTERNAL_MODEL_ALLOWED`

## Decisive technical finding

The frozen checkpoint authority is:

`kyutai/pocket-tts-without-voice-cloning/languages/english_2026-09/model.safetensors@e7205b6ee50e654a5ea19f0e9df2b0813b05e921`

That checkpoint cannot support the intended representation extraction.

At the pinned Pocket-TTS v3.3.0 source commit
`3dbee45d343d7dddd0d105468d17f8dcba14db3e`,
the official `training/scripts/precompute_latents.py` implementation loads Mimi and checks the maximum magnitude of `encoder.*` weights. If the maximum is zero, it aborts and states that the weights ship an all-zero Mimi encoder (a release without voice cloning) and that weights with a real encoder are required.

Kyutai's no-voice-cloning release construction intentionally zeroes `mimi.encoder*` tensors.

The mission's frozen representation,
`POCKET_MIMI_CONTINUOUS_MEANSTD`,
depends directly on `MimiModel.encode_to_latent`, which requires the encoder. Therefore continuing with the ungated no-voice-cloning checkpoint would produce a scientifically invalid/degenerate probe.

## Kernel incidents

Versions 1–3 all failed before checkpoint download/Mimi inference:
- v1: installed-package Git-blob provenance check;
- v2: exact VCS commit verified, but packaged bytes were not valid Git-object provenance;
- v3: editable installation was not importable in the already-running interpreter.

Those are infrastructure incidents, not scientific results.

The subsequent source audit found the more fundamental checkpoint problem before a v4 was run.

## What was NOT done

- no valid Mimi representation extracted;
- no 826-row train cache;
- no PRIMARY_CV probe;
- no complementarity analysis;
- no TARGET209 extraction;
- no GPU;
- no Kaggle submission;
- C unchanged.

## SS decision required

The same v3.3.0 config also references the encoder-capable full checkpoint:

`kyutai/pocket-tts/languages/english_2026-09/model.safetensors@983151f13aaeab1b13c1e5e3c2c383d49a9edf3f`

That repository is gated by acceptance of Kyutai's terms. Using it for representation extraction would be a checkpoint-authority change. The continuation explicitly prohibited testing other Pocket-TTS checkpoints, so RS did **not** switch silently.

SS should decide one of two actions:

1. explicitly authorize the exact full encoder-capable checkpoint above, after confirming its access terms satisfy the competition reasonableness rule; then resume the same frozen 64-D representation with no other scientific changes; or
2. close Pocket-Mimi.

`FINAL_VERDICT=INVALID_FROZEN_CHECKPOINT_ZEROED_MIMI_ENCODER`
