# RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001 — Frozen scientific protocol

Parent commit: `6b23148e21b75d10611fbb4deb2d6811b26221c3`. System E production authority: `a6676d9777ace9e9746802b3256cd3eb52dd7339`. No competition submission authorized.

## Feasibility result

The original checked-in runner `kaggle/rs_final_semantic_train826_001/run.py` uses `Qwen/Qwen3-14B`, checkpoint revision `40c069824f4251a91eefaf281ebe4c544efd3e18`, NF4 double quantization, FP16 compute, balanced dual T4, 512-token left padding, the original frozen system prompt SHA256 `d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f`, `enable_thinking=False`, and a token-ID constrained greedy trie on `angry,happy,neutral,sad,unclear`.

Algorithmic extraction is feasible: for each transcript, calculate conditional token log probabilities at distinct trie prefixes. At every branching point, normalize only over the original allowed next tokens. The resulting complete-label trie path log probabilities exponentiate to five numbers summing to one; forced EOS at each terminal leaf contributes log probability zero. Save unrestricted label-token sequence log probabilities separately as diagnostics, explicitly excluding unconstrained EOS. Greedy native `generate` is NOT synonymous with argmax over complete path probabilities.

No new model, alternate prompt, label-informed construction, calibration sweep or target inference is permitted at this gate.

## Frozen one-shot test

1. Verify authentic Qwen3-ASR train826 ZIP SHA256 `2e35d61564d68f1577e70111a4fa47a4be096dea729b75252c9bea101e7206f5` and original Qwen3-14B semantic train826 ZIP SHA256 `cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789`. Require exactly 826 distinct training IDs and 664 unique transcripts. No labels/folds in Kaggle inputs.
2. Verify the original tokenizer state sequences, hash-locked prompt/checkpoint, native-generation pilot parity, repeatability, GPU memory margin, runtime forecast and original hard-state parity 826/826 before further evaluation.
3. Baseline: reproduce System E's entire original 826-row nested probability matrix, maximum absolute discrepancy < 1e-8 and pooled macro-F1 `0.8774091527555827`.
4. Challenger: original frozen 23 inputs PLUS exactly five original constrained trie state probabilities (28 inputs). Original L2 LogisticRegression C=1, no scaling or routing, five V-B outer folds with true four-inner-fold acoustic crossfitting and heldout-safe meta heads. No hyperparameter search.
5. Primary criteria: pooled gain >=0.005, strictly positive >=4/5 folds, no per-class loss >0.02, fixed HARD316 nonnegative, positive leave-one-fold-out deltas, 656-component 2000-draw bootstrap conservative 95% lower confidence bound >0. Stop if any fail.
6. Only primary pass permits independent frozen V-A retrieval/nonretrieval, both dtype directions, supported V-Q including Q960-606 and private-allocation robustness tests; the historical System E Q960 failure is not relaxed.
7. Only a credible post-stress pass permits authentic 209-row production replay, immutable 78 certified retrieval assignments and exact incumbent System E CSV byte parity. SS alone decides Kaggle submission.

## Current status

Algorithmic gate supported by inspected original source. GPU, full 826 likelihood output and nested test are **NOT EXECUTED** in the current environment; no scientific gain asserted. The original source input archives are known to exist in the user's WSL workspace but have not been locally rehashed during this takeover. Scientific status: `PENDING_AUTHENTIC_EXTERNAL_EXECUTION`.
