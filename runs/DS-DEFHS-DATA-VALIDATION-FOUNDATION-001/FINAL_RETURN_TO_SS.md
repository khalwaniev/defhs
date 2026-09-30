# Final Return to SS

Mission: `DS-DEFHS-DATA-VALIDATION-FOUNDATION-001`

## Verdict

**PASS_FREEZE_CANDIDATE**

The data audit found a major train/test dependency that materially changes the
competition strategy.

- 1,035 supplied clips: 826 train / 209 test.
- 227 near-duplicate groups covering 467 clips.
- 77 train↔test groups affecting 78 test clips.
- Near-duplicate similarity separation is extremely sharp:
  `0.974119` weakest duplicate-cluster similarity versus
  `0.209360` strongest non-cluster similarity under the
  independent relative-time fingerprint.
- All train↔test groups have unanimous train labels.
- One train-only label-conflict group exists.
- Cheap acoustic baseline shows an average ~0.0984
  macro-F1 row-CV leakage premium.

## Freeze candidate

- V-A: 5-fold stratified row-level competition-mimic.
- V-B: 5-fold stratified duplicate-safe grouped CV.
- V-C: not frozen; reliable speaker identity is unavailable.

## Immediate next scientific bottleneck

Benchmark strong pretrained speech/emotion representations under the exact same
V-A/V-B folds, beginning with frozen emotion2vec+ and WavLM representations.
Keep the 78-clip test duplicate-retrieval lane separate from model selection.
