# RS-DEFHS-TARGET209-SPECTROGRAM-EVIDENCE-001 — AST Recovery Knowledge Note

## Scope

This note is intentionally narrow. It records only implementation/literature facts needed to reproduce the historical AST path or to interpret later fusion work. It does not change the frozen DEFHS experiment, fit a gate, or justify any new ensemble.

## Upstream model and implementation facts

Canonical parent:

- repository: `MIT/ast-finetuned-audioset-10-10-0.4593`
- revision: `f826b80d28226b62986cc218e5cec390b1096902`
- exact `model.safetensors` SHA256: `ae0c1e2ad4e1381d851fa9bf298ba13ebc9c5a914cdee2dbe427a6583869924d`
- model card license: BSD-3-Clause
- historical Transformers version: `4.57.1`

Primary public sources inspected:

1. Pinned Hugging Face model/file:
   `https://huggingface.co/MIT/ast-finetuned-audioset-10-10-0.4593/blob/f826b80d28226b62986cc218e5cec390b1096902/model.safetensors`
2. Hugging Face AST documentation:
   `https://huggingface.co/docs/transformers/model_doc/audio-spectrogram-transformer`
3. Transformers v4.57.1 AST implementation:
   `https://github.com/huggingface/transformers/blob/v4.57.1/src/transformers/models/audio_spectrogram_transformer/`
4. Gong, Chung & Glass (2021), *AST: Audio Spectrogram Transformer*:
   `https://arxiv.org/abs/2104.01778`

The upstream file page independently reports the same SHA256 recorded by historical DEFHS provenance.

The official AST feature extractor consumes mono raw audio at 16 kHz and produces normalized log-Mel features. The pinned/historical configuration is:

- 128 Mel bins
- max 1024 time frames
- AudioSet mean `-4.2677393`
- AudioSet std `4.5689974`
- right padding
- no attention mask

Historical DEFHS code further fixes full-coverage chunks to 164,080 samples, feeds each chunk independently, and averages **softmax probabilities** over chunks.

The historical DEFHS representation is the `ASTModel.pooler_output`, i.e. the average of the classification/distillation token representations. This is consistent with the AST/Transformers implementation and is not replaced by mean pooling over all spectrogram tokens.

## What AST contributes representationally

The AST paper treats an audio spectrogram as a sequence of time-frequency patches and uses self-attention to model their global relationships. Therefore AST exposes time-frequency structure directly, while E2V/XLS-R in DEFHS are waveform SSL representations. This is a representation-level reason to test complementarity, not evidence that AST must improve DEFHS.

For this competition, the relevant empirical evidence remains stronger than any generic literature expectation:

- adapted AST seed-mean standalone PRIMARY_CV: `0.6030611992`
- C standalone PRIMARY_CV: `0.8135577912`
- AST correct / C wrong: `68`
- HARD AST correct / C wrong: `50`
- remaining C neutral<->sad cross-errors: `32`
- AST correct on those: `14`

Thus AST has genuine conditional information but is unsafe as a direct replacement.

## Neutral/sad interpretation

No literature-derived pitch/energy heuristic is authorized. Spectral/prosodic evidence may be relevant to low-arousal distinctions, but DEFHS already shows both sides of the trade-off: AST repairs 14/32 remaining C neutral<->sad errors while also disagreeing harmfully with many C-correct rows. Any future fusion must learn/validate conditional use rather than encode a hand-written “low pitch = sad” rule.

## Probability-comparability constraint

The canonical AST evidence vector is an ensemble probability:

1. softmax per spectrogram segment;
2. mean probability over a clip's segments;
3. uniform mean over the five ordinary PRIMARY_CV outer models within a seed;
4. arithmetic mean over seeds `20260930` and `20260917`.

These AST probabilities are not assumed calibrated on the same scale as C. A later fusion mission should treat raw confidence/margin comparability as an empirical question, especially because C is a nested waveform+semantic logistic meta-system and AST is a separately adapted spectrogram model.

## Later literature work

If TARGET209 AST inference succeeds and SS authorizes a fusion mission, a focused review is warranted on:

- acoustic + linguistic SER fusion;
- confidence-aware / mixture-of-experts fusion;
- spectrogram + waveform-SSL complementary representations;
- neutral/sad and low-arousal discrimination;
- valence/arousal auxiliary structure;
- small-data SER;
- target adaptation only if separately authorized.

No such methods are implemented in this recovery addendum.
