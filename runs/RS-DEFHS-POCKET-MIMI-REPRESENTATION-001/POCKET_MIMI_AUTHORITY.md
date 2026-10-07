# Pocket-TTS / Mimi authority audit

## Official software authority

Official repository: `kyutai-labs/pocket-tts`.

Latest released package inspected: **v3.3.0**, released 2026-09-24.

Pinned release commit:
`3dbee45d343d7dddd0d105468d17f8dcba14db3e`

Current main observed during the audit:
`41cbc84af539ea78a804ffca5f9c6edc1a22ce44`

The representation study would pin the stable v3.3.0 release rather than floating main.

Relevant source identities at the pinned release:
- `pocket_tts/config/english_2026-09.yaml` Git blob: `fd7205053ffac3e60cb08423f760707b67de5679`
- `pocket_tts/models/mimi.py` Git blob: `2656cd57f5516ad54cbe56abdd93a42482ed2388`

Software license: **MIT**.

## Official checkpoint authority

The v3.3.0 English configuration pins:
- voice-cloning weights:
  `hf://kyutai/pocket-tts/languages/english_2026-09/model.safetensors@983151f13aaeab1b13c1e5e3c2c383d49a9edf3f`
- no-voice-cloning fallback:
  `hf://kyutai/pocket-tts-without-voice-cloning/languages/english_2026-09/model.safetensors@e7205b6ee50e654a5ea19f0e9df2b0813b05e921`

The Hugging Face model metadata identifies the released weights as **CC-BY-4.0**. The voice-cloning repository is gated behind acceptance of model conditions; the no-voice-cloning repository is publicly downloadable and is the preferred authority for a codec-only representation study.

The no-voice-cloning revision `e7205b6ee50e654a5ea19f0e9df2b0813b05e921` is an observed, verified Hugging Face commit. The exact LFS SHA256 for the `english_2026-09` binary was not independently materialized in this worker runtime; therefore no binary hash is invented.

## What the audio encoder actually is

Pocket-TTS v3.3.0 uses a continuous Mimi-derived neural audio codec.

The official technical report states that, unlike original Mimi's RVQ/discrete-token path, Pocket-TTS uses **continuous latents** regularized as a VAE. WavLM is distilled into the codec's inner latent representation with cosine similarity, applied to the whole continuous latent because there is no RVQ.

The pinned config specifies:
- mono audio
- sample rate: **24,000 Hz**
- output frame rate: **12.5 Hz**
- inner latent dimension: **32**
- outer codec dimension: 512
- SEANet encoder dimension: 512
- encoder transformer: 2 layers, d_model 512, 8 heads

The pinned implementation's `MimiModel.encode_to_latent(x)`:
1. accepts float waveform tensor `[B,C,T]`;
2. pads to a multiple of the codec frame size;
3. runs SEANet encoder;
4. runs the encoder transformer;
5. downsamples to the overall 12.5-Hz frame rate;
6. returns **unquantized** latents with shape `[B,T,32]`.

No text tokenizer, FlowLM generation, language model decoding, or TTS synthesis is required for this call.

## Can arbitrary Hindi speech be encoded?

**Technically yes.** `encode_to_latent` consumes waveform only and has no text or language input. The public API also resamples arbitrary audio prompts to 24 kHz before Mimi encoding.

The released Pocket-TTS training data are English speech, so usefulness on Hindi emotion is an empirical transfer question, not something assumed by architecture.

## Conditioning / voice representation

Pocket-TTS also has a voice-conditioning path. The code projects Mimi latents through `flow_lm.speaker_proj_weight` and feeds the result into the FlowLM state. That path is specifically associated with voice cloning / acoustic conditioning.

This mission does **not** authorize it as a second representation:
- it mixes codec evidence with a TTS-specific conditioning projection;
- it is unnecessary for the clean first test;
- the voice-cloning checkpoint is gated;
- using only one architecture-grounded representation reduces adaptive search.

## Compute assessment

The technical report describes an approximately **18M-parameter codec encoder** used once per voice sample. The full Pocket-TTS system is designed for CPU and the repository supports CPU-only PyTorch installation.

Therefore a small CPU preflight is scientifically appropriate before any GPU request. No empirical runtime measurement was performed because the mission hit the Phase-0 competition-policy stop before implementation.

## Competition-policy audit

The public DEFHS Kaggle page confirms the task, macro-F1 metric, and public/private leaderboard structure, but the externally retrievable page did not expose an external-pretrained-model clause.

The project's own `docs/EXTERNAL_DATA_POLICY.md` states that external models/data may be used **only when they satisfy the competition rules and are sufficiently accessible/reproducible**.

No authoritative preserved DEFHS rule text was found in the repository that explicitly permits or prohibits external pretrained models, and no indexed official rule clause could be recovered from the competition page.

Therefore:
`POLICY_STATUS = UNVERIFIED_EXTERNAL_MODEL_PERMISSION`.

Per this mission's Phase-0 instruction, this is a mandatory STOP condition. No extraction or PRIMARY_CV probe is run until SS supplies or independently verifies the exact official external-model rule.
