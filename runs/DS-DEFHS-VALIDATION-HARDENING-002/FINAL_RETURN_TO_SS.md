# Final Return to SS

Mission: `DS-DEFHS-VALIDATION-HARDENING-002`

## Final verdict
**REVISE_AND_FREEZE**

## Structural discoveries
- supplied authority is 1,035 clips, not the 1,036 stated in prose;
- train/test IDs are broadly row-random/interleaved;
- duplicate dependency is large and robust: 227 groups, 78 affected test clips;
- one known conflicting duplicate-label family;
- recording format/source heterogeneity is real (int16 vs int32) and materially affects transfer;
- global train/test shift is weak, with a modest nonlinear residual shift after duplicate-covered examples are removed;
- speaker identity, acted/spontaneous membership, and prompt/script identity remain unobservable from current executed evidence and are explicitly controlled rather than guessed.

## Frozen validation
- V-B duplicate-safe: primary model-selection guardrail.
- V-A row-level: competition-mimic secondary view.
- V-D int16/int32: source-format stress.
- V-C speaker-disjoint: not frozen.
- protected promotion seed: 20261001 duplicate-safe, routine access prohibited.

## Retrieval
Keep the deterministic frozen retrieval map for 78 test clips separate from SER modeling.

## Recommendation to SS
Authorize the first serious RS modeling mission under the frozen V-B/V-A/V-D architecture. Strong speech/emotion representations may be explored, but they must not tune against the protected gate. If later infrastructure makes ECAPA/ASR extraction available, use it to add speaker/transcript diagnostics without silently changing the current authority.

Heavy acoustic artifact: Drive `/DEFHS/ds_validation_002/ACOUSTIC_FEATURES_FULL.csv`.
