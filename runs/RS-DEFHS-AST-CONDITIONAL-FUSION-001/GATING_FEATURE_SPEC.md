# Gating feature specification — frozen before Phase-1 results

The primary gate uses only inference-time, target-independent information available identically on labeled OOF rows and TARGET209.

Continuous features:
1. C maximum probability
2. C top1-top2 margin
3. C entropy
4. AST maximum probability
5. AST top1-top2 margin
6. AST entropy
7. Jensen-Shannon divergence between C and AST probability vectors

Categorical/binary features:
8. C predicted class
9. AST predicted class
10. ordered C->AST class transition
11. A agrees with C
12. A agrees with AST
13. Qwen state in {angry,happy,neutral,sad,unclear}
14. Qwen abstention
15. C agrees with Qwen (false when Qwen=unclear)

Explicitly excluded:
- Id / filename as a model feature
- true label or any feature constructed from true labels
- test identity
- certified-retrieval truth/membership as a learned feature
- manually selected class-pair indicators after seeing outcomes
- TARGET209 disagreement or the 17 C-vs-A target changes as labels
- uncertainty category as a learned feature in Phase 1 (avoids any unresolved train/target-construction mismatch)

Preprocessing: StandardScaler fitted only on continuous columns inside each gate-training partition; OneHotEncoder(handle_unknown='ignore') fitted only inside gate-training partitions. No calibration or threshold tuning.
