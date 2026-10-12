# F-WAVLM-ATTN1024-27F-V1 — frozen prospective test

Authority: `a6676d9777ace9e9746802b3256cd3eb52dd7339`. Registered 2026-10-12 before inspecting any new expert predictions or validation results. ONE representation, ONE expert recipe, ONE fusion; no search. The public E score 0.89505 is user-reported context, never a fitting target. E remains scientifically unpromoted because its Q960-606 gate failed; its frozen 0.8774091527555827 OOF and production CSV are the present comparison, with D preserved as fallback.

## Observation, competing explanations, discriminating test

E has 102 errors: 74 true-class rank two, 21 rank three, seven rank four. Neutral/sad contributes 34, happy/neutral 29, angry/sad 19. HARD316 contains 70 errors; waveform disagreement contains 65. Nineteen errors are wrong under all five current experts. QwenASR/Qwen14 could correct 32 E errors but would break 191 correct E decisions if blindly substituted. These are descriptive oracle counts, not correction rules or evidence of causality.

Competing explanations: (1) existing representations encode the answer but compress or miscalibrate it (Sol's separate CPU mission); (2) a distinct emotion-trained acoustic representation contains conditional information absent from E; (3) source, speaker, label ambiguity or sampling noise limits both. Test (2) with one independently trained frozen WavLM expert and properly nested train-only adaptation of its fixed embedding. Rejection does not establish a universal ceiling for acoustics.

## Exact model and mathematical representation

- `3loi/SER-Odyssey-Baseline-WavLM-Categorical`, revision `50632bbc8b89cbaa45077f1404601d9776cfe387`, MIT model-card license, ungated.
- `model.safetensors`: 1,274,511,016 bytes; SHA256 `fb52f3f472b6a5a824ac238537fa60bf39a73d74b3fa5f4a4473c012cb3d18f4`.
- Upstream `pipeline_utils.py` SHA256 `7a1033b5af29e5607a9213697be04d649464bd05dfa4b669ea6133a3900334e3`. Vendor architecture; instantiate WavLM from pinned configuration, then load all trained tensors strictly. Do not download or substitute original base weights.
- WavLM base configuration: `microsoft/wavlm-large@c1423ed94bb01d80a3f5ce5bc39f6026a0f4828c`; included locally. English MSP-Podcast supervision; no demonstrated Hindi accuracy. Published eight-class results are not numerically comparable to DEFHS. No DEFHS supervised adaptation of the encoder.
- Entire 16-kHz mono waveform, original sample count, float32 PCM decoding; fixed upstream normalization `(x - (-0.00008278621631819787))/(0.08485510250851999 + 1e-6)`. No VAD, time cropping, augmentation, transcript, label, fold or target input to extractor. Batch one avoids padding artifacts. Eval mode, FP32, no gradients.
- Frame attention `a_t = softmax(v^T tanh(W h_t))`; pooled mean and standard deviation feed the pretrained 1024-unit LayerNorm/ReLU emotion head. Primary representation is `ser_model.get_repr(pool_model(ssl_states, mask))`, exactly 1024 coordinates. This can emphasize informative vocal frames instead of uniform temporal pooling; it is a hypothesis, not proof of prosodic specificity.
- Also export all eight native logits and their single-softmax probabilities for diagnostics: Angry, Sad, Happy, Surprise, Fear, Disgust, Contempt, Neutral. These are uncalibrated source-task probabilities. Four-class diagnostic argmax restricts to indices [0,2,7,1]; no other emotions silently mapped to DEFHS. These native outputs are NOT additional fusion inputs.

## Feasibility before full run

CPU or single T4 FP32 are permitted; no training on GPU. Run four longest training clips twice, selected solely by sample count/ID. Require finite features, native-class argmax repeatability, max absolute repeated feature difference <=1e-5, full tensor-load parity, CPU peak <7 GiB or GPU reserved memory leaving >=2 GiB free, and conservative forecast `2 * total_audio_seconds * pilot_seconds / pilot_audio_seconds <= 3600 s`. Actual runtime, memory, package versions and tensor compatibility must be logged. Failure is EXECUTION_BLOCKED; do not switch model or precision based on accuracy. No measured GPU speed is claimed before such a pilot.

## One nested expert and fusion

Use unchanged five PRIMARY_CV blocks and exact angry/happy/neutral/sad order. New acoustic expert: train-only StandardScaler plus multinomial L2 LogisticRegression, C=1, lbfgs, max_iter=5000, random_state=20261001, unweighted. No PCA, tuning or early stopping. Each outer heldout block receives a head fit on the other four; each meta-training row receives new-expert probabilities from a head fit only on the other three training blocks. Original E acoustic inner heads/procedure and authentic outer probabilities remain unchanged. All expert fitting excludes the corresponding outer validation labels.

Reproduce E full 826 probabilities within 1e-8 before evaluating the challenger. E = eight original acoustic probabilities plus three five-state one-hot semantic vectors (Qwen8/Whisper14/QwenASR14): 23 features. Challenger adds ONLY four correctly nested new-expert probabilities: 27 features, same unscaled L2 C=1 logistic meta recipe. No stacker on ordinary OOF rows. Five new outer and twenty inner heads, five candidate meta fits. All 826 frozen pretrained embeddings may be extracted once because extraction uses no DEFHS labels.

First report new expert OOF complementarity against E. If fewer than ten corrections, fewer than five corrections unavailable to BOTH existing acoustic predictions, or corrections span fewer than three gold classes, stop this hypothesis before fusion. Counts are an openly recorded exploratory screen, not an independent statistical test. No confidence threshold or selective override is fitted. Conditional utility is decided by the prospective nested fusion, not oracle complementarity or source-task confidence.

## Promotion gates, fixed before results

All must pass vs unchanged E: pooled PRIMARY_CV macro-F1 gain >=0.005; at least 4/5 positive original-fold gains; no class-F1 decrease >0.02; original HARD316 nonnegative; all leave-one-fold-out gains positive; paired 656 duplicate/prompt-connected-component 2000-draw exponential bootstrap max-t 95% lower bound >0. Duplicate-singleton and prompt-singleton gains must each be nonnegative. Report full correction/breakage IDs, confusion matrices, precision/recall/F1, log loss and all fold scores. Never call a selected interval independent of previous adaptive research.

Only after primary pass: new matched nested V-A retrieval/non-retrieval comparison vs E; pipeline and non-retrieval gains >=0. Dtype transfer both directions >=-0.02. Existing Q128 and Q960 adequately supported subgroups (each class >=5) >=-0.02 vs E; additionally Q960-606 must not be worse than D by >0.02, preventing inheritance of E's failed gate. Original plausible allocation procedure: 616 class-stratified scenarios, 250 draws each, mean private and weighted (0.4 public +0.6 private) gains nonnegative, reversal frequency <=0.20. Report uncertainty and assumptions; never infer actual private membership. No protected validation.

Only after all gates: exact E production replay, matching inference on 209 WAVs, five matched expert/meta heads, fixed 78 certified retrieval assignments, official schema/order/hash, one candidate and SS review. No automatic Kaggle submission. If any gate fails, REJECT this fixed hypothesis and preserve E/D, no thresholds, variant or checkpoint rescue.

## Alternatives screened without DEFHS execution

The four-class LincolnD IEMOCAP checkpoint is accessible and simple, but its acted-to-natural title denotes scripted-to-improvised IEMOCAP, not evidence of natural Hindi transfer. The selected WavLM adds a different SSL backbone, natural-podcast supervision and attentive statistics pooling. audEERING dimensional wav2vec2 is reproducible but shares more of the wav2vec lineage and has a noncommercial research license; its three attributes do not directly supply four emotion classes. No scientific negatives are assigned to these unexecuted alternatives.

Full candidate-label likelihoods from frozen Qwen14 could expose information discarded by greedy hard labels, but likelihood is lexical evidence from transcripts already used by E and does not measure unseen prosody. Correct sequence likelihood would sum conditional token log probabilities including EOS and normalize over the five fixed candidate strings; self-reported verbal confidence is not that quantity. Deferred in favor of the more distinct acoustic test, with Sol's existing-evidence work separate.

Nemotron Hindi 4B is a text model; no evidence here demonstrates additional conditional emotion information beyond frozen Qwen14. Nemotron 3.5 ASR supports Hindi, but a third recognizer has no demonstrated conditional emotion benefit after the successful Qwen-ASR intervention. Neither is run. Prior AST, Pocket-Mimi, emotion2vec+, source gating and exact adaptation-policy failures stay closed; they do not test this WavLM representation.
