# DEFHS final experiment archive — 13 October 2026

This archive makes the final offline research evidence discoverable from the portfolio's default branch. Source branches, commit history and frozen scientific reports are preserved. **This is an archival record, not a claim of successful final System F deployment.**

## Completed, measured experiment

- [Qwen14B continuous-likelihood 23F vs 28F comparison](results/semantic_28f_result.json) — frozen 826-row primary comparison: System E 0.8774091528; exploratory 28F 0.8809653563; six corrections, three breakages; `REJECT_LOCAL_COMPARISON`, no scientific promotion.
- [Paired out-of-fold predictions](results/semantic_28f_paired_oof.csv) — reproducibility and error analysis for that comparison.
- [Qwen likelihood recovery scripts, provenance, and diagnostic READMEs](semantic-recovery/) — recovered on the user's WSL workstation, committed on `archive/snapshot-defhs-semantic-information-20261013`, and incorporated into default `main`.

## Exploratory and unfinished System F hypotheses

- [Independent emotion-model Kaggle notebook](notebooks/fresh_emotion_experts.ipynb) — uploaded for runtime exploration; **no completed, validated result established**.
- [Qwen2.5-Omni-3B audio-native notebook](notebooks/qwen_omni_3b.ipynb) — uploaded; **no completed inference or benefit established**.
- [New acoustic expert evaluator](scripts/audio_expert_audit.py) and [Kaggle launcher](scripts/omni_launcher.sh) — execution utilities, not evidence of achieved performance.

## Canonical scientific evidence

- [Research case study](../../docs/RESEARCH_PORTFOLIO.md)
- [Frozen validation authority](../../docs/ACTIVE_VALIDATION.md)
- [System E verified scientific report](../../runs/RS-DEFHS-FINAL-BREAKTHROUGH-001/SYSTEM_E_FINAL_SS_REPORT.md)
- [System E production reproducibility](../../runs/SS-DEFHS-SYSTEM-E-EXPLORATORY-DEPLOYMENT-001/TARGET209_FINAL_CANONICAL_VERDICT.md)
- [Post-competition release checklist](../../docs/POST_COMPETITION_ARCHIVE_CHECKLIST.md)

The repository is private. Raw competition audio, model checkpoints, environments and cache folders are not published; GitHub is used for code, small results, methods and provenance. Making a recruitment-facing **public** portfolio requires a deliberate release/license review.
