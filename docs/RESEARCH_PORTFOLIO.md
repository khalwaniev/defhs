# DEFHS — research case study (October 2026)

**Project:** Detecting Emotions from Hindi Speech (Kaggle / DataVerse)  
**Task:** Four-class speech emotion recognition (angry, happy, neutral, sad)  
**Data:** 826 labeled Hindi speech recordings; 209 unlabeled test recordings  
**Official metric:** Macro-F1  
**Status:** Competition concluded. This is a retrospective research archive, **not** a winning-system claim.

## Research question

Can complementary acoustic and transcript-derived semantic information improve speech emotion recognition under a very small labeled-data regime while controlling duplicate leakage, correlated samples, and distribution shift?

The project explored waveform encoders, audio representation pooling, speech-to-text and Hindi semantic inference, group-safe meta-learning, retrieval-based recognition for certified near-duplicates, and prospective stress tests. All reported test predictions were produced without the hidden test labels.

## Main verified results

| Method / milestone | Frozen PRIMARY_CV macro-F1 | Interpretation |
|---|---:|---|
| System 1: emotion2vec_base pooled embeddings + logistic regression | 0.7383745766 | Early reproducible acoustic control |
| Fixed waveform pair (emotion2vec + XLS-R) | 0.7768156647 | Positive acoustic complementarity |
| System D | 0.8396460575 | Acoustic–semantic stacked ensemble |
| System E | **0.8774091528** | Added Qwen3-ASR to Qwen3-14B semantic information |

System E improved on System D by **0.0377630952 absolute macro-F1** in the frozen 826-row OOF comparison. Five out of five folds improved; 42 wrong labels were corrected and 11 correct labels were broken (five wrong-to-other-wrong changes). The authentic 656-dependency-component paired bootstrap's simultaneous interval for E–D was **[+0.01888038, +0.05664581]**.

**Critical limitation:** System E **failed one predeclared recording-length/quantization stress gate**, losing 0.03367393 macro-F1 versus System D in the eligible Q960 remainder-606 subgroup (n=41). It passed 6/7 stress gates, but the original scientific protocol therefore **did not promote it**. The 209-row System E production inference was separately reproduced byte-for-byte and preserved the 78 certified retrieval assignments; a reproducible candidate does not imply validated superiority on hidden data.

**Leaderboard scores recorded in project communications (not independently reproduced from GitHub alone):** System D public macro-F1 0.88227; System E public macro-F1 0.89505. These are **public** observations, not private leaderboard results. **No final private ranking or 209-label accuracy is asserted here.**

## Key technical contributions

### 1. Data provenance and evaluation design
- Audio metadata, duplicate-family forensics, label conflict checks, prompt similarity and source-format investigations.
- Five-fold, duplicate-family-safe StratifiedGroupKFold with frozen fold assignments; honest separation of train-only fitting and outer-fold evaluation.
- Explicit audit of potential retrieval overlap: 78 test recordings assigned to certified retrieval-covered groups; held separate from learned SER decisions.
- Alternative allocation and shift-stress views, including sample-length quantization effects and dtype transfer; uncertainty limits and failure modes recorded.

### 2. Complementary audio and linguistic evidence
- Frozen **emotion2vec_base** and **XLS-R** waveform representations with classical calibrated classifiers.
- Distinct speech-to-text and large-language-model paths: Qwen3-8B, Whisper-transcript→Qwen3-14B, and Qwen3-ASR→Qwen3-14B five-state semantic inference.
- A **23-feature** System E meta-classifier: eight acoustic class probabilities plus three five-state semantic one-hot vectors, with nested logistic fits rather than fitting a meta-model on its own training labels.

### 3. Research engineering and reliability
- Deterministic artifact inventories, dataset/checkpoint hashes, saved-fold inference, and replay-parity tests for all 826 labeled and 209 test IDs.
- Python/Kaggle/WSL experiment packages, model and environment provenance, model- and subgroup-specific negative findings.
- Decision discipline that distinguishes source-task metrics, exploratory CV improvements, predeclared stress-gate failures, and leaderboard observations.

### 4. Negative findings and unfinished branches
- Continuous Qwen14B five-state likelihoods were evaluated locally on October 12 against the authentic 23-feature E reference: a 28-feature exploratory challenger scored **0.8809653563** versus **0.8774091528**, with six corrections and three breakages, but one fold deteriorated and the Q960 issue did not improve. **Not promoted.** The corresponding run output remains in the user's local WSL workspace and should be archived separately; the source is already versioned.
- A group-purged decision-theory study found weak/non-robust macro-F1 gains and harmful expert-reliability switching; neither rule was promoted.
- AST conditional routing, Pocket-Mimi representation, and various postprocessing / adaptation hypotheses produced negative or inconclusive findings.
- The independent WavLM and audio-native Omni System F candidate lanes were exploratory; **no complete production System F or 0.97-performing system was demonstrated**.

## Evidence navigation

| Purpose | Primary source |
|---|---|
| Frozen validation and reproducibility | [Active validation](ACTIVE_VALIDATION.md) · [Final validation authority](../runs/DS-DEFHS-VALIDATION-HARDENING-002/FINAL_VALIDATION_AUTHORITY.md) |
| Data forensics and evaluation threats | [EDA master report](../runs/DS-DEFHS-VALIDATION-HARDENING-002/EDA_MASTER_REPORT.md) · [Adversarial review](../runs/AR-DEFHS-FINAL-VALIDATION-DATA-REDTEAM-001/FINAL_ADVERSARIAL_RETURN_TO_SS.md) |
| System E architecture, gains, and scientific limitation | [System E scientific report](../runs/RS-DEFHS-FINAL-BREAKTHROUGH-001/SYSTEM_E_FINAL_SS_REPORT.md) |
| Byte-reproducible 209-row E candidate | [System E production audit](../runs/SS-DEFHS-SYSTEM-E-EXPLORATORY-DEPLOYMENT-001/TARGET209_FINAL_CANONICAL_VERDICT.md) |
| System E classifier source | [Finalizer](../scripts/finalize_system_e_exploratory.py) |
| Target209 uncertainty and case analysis | [TARGET209 strategy](TARGET209_STRATEGY.md) · [Evidence matrix](TEST209_PREDICTION_MATRIX.csv) |
| Residual-error characterization | [System F residual checkpoint](../runs/RS-DEFHS-SYSTEM-F-FIRST-PRINCIPLES-001/RESIDUAL_CHECKPOINT.json) |
| Preregistered WavLM study | [System F protocol](../runs/RS-DEFHS-SYSTEM-F-FIRST-PRINCIPLES-001/PROTOCOL.md) |
| Continuous Qwen likelihood evaluator | [23F vs 28F evaluator](../scripts/one_shot_semantic_information_23f_28f.py) |
| Decision-optimization null results | [Decision optimization report](../runs/RS-DEFHS-SYSTEM-E-DECISION-OPTIMIZATION-001/RETURN_TO_SS.md) |
| External artifacts and release readiness | [Archive checklist](POST_COMPETITION_ARCHIVE_CHECKLIST.md) |

**Branch provenance:** A substantial portion of the scientific code and evidence was developed on topic branches. Those original branches are intentionally preserved; they are **not** all silently merged or treated as an accepted final model. See the archive checklist for the branch map.

## Reproducibility and public-release restrictions

Source files, lightweight feature summaries, audit CSVs, and manifests are tracked in GitHub. Some large artifacts—original competition WAVs, model weights, 826/209 inference bundles and frozen representations—were kept externally under `/DEFHS/` (Google Drive) or local `work/` folders. This Git repository **alone is not a fully runnable, self-contained reproduction package**. Do not invent or redistribute missing inputs.

The repository remains **private** while competition-data licensing, sensitive prediction/transcript audit outputs, source checkpoint terms, and third-party redistribution permissions are reviewed. A future public portfolio should prioritize original code, synthetic fixtures, permitted aggregate metrics, methodology and carefully vetted examples; do not assume private test-row outputs or third-party raw recordings may be published.

This was an AI-assisted research-engineering workflow. A portfolio account should distinguish owned scientific decisions, independently executed tests and verified output artifacts from AI-generated proposals and unexecuted experiments.

## Further scientific value

The central lesson is that sound validation can reject an apparently better candidate even when its pooled OOF and public leaderboard score increase. The project demonstrates scientific work on **low-data multilingual SER, complementary acoustic and semantic representations, nested ensembles, duplicate-aware evaluation, reproducibility, and robustness under dataset shift**, rather than a claimed leaderboard victory.
