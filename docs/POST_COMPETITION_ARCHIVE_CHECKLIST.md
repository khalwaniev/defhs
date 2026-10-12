# Post-competition archive and release checklist

**Date:** 2026-10-13  
**State:** research preserved; competition ended; no further prediction/submission authorized in this archive.  
**GitHub visibility:** PRIVATE. Do not change to public as part of archival synchronization.

## Integrity-preserving source branches

The original branches should be retained independently even when the canonical index moves to `main`. Promising, failed and unfinished experiments have different scientific dispositions; their existence in the repository does **not** represent model promotion.

| Branch | Source / purpose |
|---|---|
| `rs/final-breakthrough-001-sol6-semantic` | Qwen-ASR→Qwen14B; System E scientific result and 209 deployment evidence |
| `rs/final-semantic-information-001` | Latest executable 23F/28F likelihood evaluator; fully authenticated source |
| `rs/system-e-decision-optimization-001` | Group-purged macro-F1 and expert-reliability postprocessing; negatives |
| `rs/system-f-new-information-001-astra` | WavLM attentive-pooling System F preregistration, feasibility pilot and script |
| `rs/target209-forensic-endgame-001` | Target209 error and uncertainty analysis |
| `ss/target209-empirical-reset-001` | Frozen 209-row identity and prediction matrix |
| `rs/ast-conditional-fusion-001` | AST conditional routing assessment |
| `rs/pocket-mimi-representation-001` | Pocket-Mimi feature experiment |
| `rs/fairhindiser-screen-001` | Additional Hindi SER screen |
| `rs/strong-llm-semantic-001` | LLM semantic experiments |

Other source branches and commit SHAs remain accessible via the repository's Branches view. Never delete an original scientific branch as part of portfolio preparation.

## Authenticated external artifacts: verify, do not upload raw copies indiscriminately

| Item | Expected SHA256 | Example user WSL location / handling |
|---|---|---|
| System D scientific delivery | `fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839` | `/home/fikar/zingle/defhs-sol6-asr/work/system_e_canonical_replay/DEFHS_SYSTEM_D_FINAL_DELIVERY.zip` |
| System E scientific evidence | `dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf` | `/home/fikar/zingle/defhs-semantic-information/evidence/DEFHS_SYSTEM_E_FINAL_SCIENTIFIC_EVIDENCE.zip` |
| New QwenASR→Qwen14B train826 | `cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789` | `/home/fikar/zingle/defhs-sol6-asr/work/DEFHS_QWENASR_QWEN14_SEMANTIC826.zip` |
| Qwen14B five-likelihood train826 CSV | `66d01f825c9be4142452e6f04fb921dd8ece6c8f82aac5e0768a9941c0e4e788` | `/home/fikar/zingle/defhs-semantic-information/work/rs_final_semantic_likelihood_return/defhs_qwen14_likelihoods/QWEN14B_LIKELIHOOD_TRAIN826.csv` |
| Frozen PRIMARY_CV fold membership | `87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b` | Tracked `runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VB_FOLDS.csv` |
| System E 209-row exploratory CSV | `e47676192cbd02393a49889214238f34cb8b49df2f9772b30cb19d766589df90` | Tracked `runs/SS-DEFHS-SYSTEM-E-EXPLORATORY-DEPLOYMENT-001/production/submission_system_e_exploratory.csv` |

Large evidence bundles belong in controlled archival storage, not automatically in Git. Their hashes and provenance are the GitHub-facing record.

## Pending WSL-only evidence

These outputs existed in local user sessions but **are not verified to be committed and pushed**. Do not claim that this checklist synchronizes them:

1. `/home/fikar/zingle/defhs-semantic-information/work/system_f_semantic28f_20261012/RESULT.json` — authentic 23F-vs-28F experiment, `REJECT_LOCAL_COMPARISON`, local23 0.8774091528 vs local28 0.8809653563, plus 6 corrections/3 breakages. Outcome must be archived along with paired OOF and numerical drift report if present.
2. `/home/fikar/zingle/defhs/work/system_f_fresh_emotion_001/run.ipynb` — four-expert independent SER Kaggle notebook; pushed separately to Kaggle, but no completed inference established.
3. `/home/fikar/zingle/defhs/work/system_f_omni_3b/run.ipynb` — Qwen2.5-Omni-3B audio-native notebook; pushed to Kaggle; runtime/experiment not completed at archive time.
4. Any newer WavLM GPU output, user WSL-only scripts, Kaggle logs, target209 case-analysis files, saved training histories and model provenance not yet represented by tracked small manifests.

**Before archival push:** inspect each candidate's content and Git status. Exclude credentials, access tokens, raw or derivative audio lacking redistribution permission, gated weights, cache directories, huge unlicensed binaries, and unverified pseudo-labels. Keep nonpromoted hypotheses labeled exploratory.

## Safe WSL synchronization protocol

Do not blindly `git add -A` across multiple clones. For each local worktree, record `git status --short --branch`, `git remote -v`, `git diff --stat`, and `git log -1 --oneline`; review untracked files and intentional outputs. Use an archival branch, not an unrelated ongoing research branch.

Track small results and source selectively, for example:

```bash
cd /home/fikar/zingle/defhs-semantic-information
git status --short --branch
test -f work/system_f_semantic28f_20261012/RESULT.json
mkdir -p runs/RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001
cp work/system_f_semantic28f_20261012/RESULT.json runs/RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001/POST_COMPETITION_28F_RESULT.json
git diff --check
git add runs/RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001/POST_COMPETITION_28F_RESULT.json
git diff --cached --stat
# Review the staged file before committing; push only to the intended branch.
```

If the branch or file was modified elsewhere, fetch and reconcile before pushing. Never overwrite prior evidence or force-push a scientific branch.

## Public portfolio release gate

- Confirm official competition rules and third-party dataset/checkpoint redistribution rights.
- Remove raw audio, proprietary weights, secret tokens, private user data, and non-redistributable derivatives.
- Audit commit history, not only HEAD: making an old private repo public also exposes historical blobs and branches.
- Prefer a **new clean public repository** with permissibly redistributable original code, README, synthetic example data, source/attribution links and verified aggregate science.
- Validate from a clean clone with documented environments, input prerequisites and tests.
- Cite verified PRIMARY_CV metrics and state the Q960-606 scientific non-promotion; never describe a completed System F, private leaderboard win, or hidden-label access.
- Report AI-assistance transparently and describe precisely the author's implementation, execution, scientific decisions, validation and interpretation.
