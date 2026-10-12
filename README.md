# DEFHS — Hindi Speech Emotion Recognition

**Research-engineering case study | October 2026 | Competition completed**

**826 labeled recordings · 209 unlabeled test recordings · 4 classes · macro-F1**

Developed and evaluated a low-data multimodal speech-emotion recognition pipeline combining **emotion2vec, XLS-R, Hindi ASR and Qwen-based semantic inference**, with explicit duplicate-safe validation, nested fusion, distribution-shift stress testing and reproducible inference.

## Results at a glance

| Frozen PRIMARY_CV model | Macro-F1 |
|---|---:|
| emotion2vec acoustic baseline | 0.73837 |
| emotion2vec + XLS-R fixed pair | 0.77682 |
| System D, acoustic–semantic ensemble | 0.83965 |
| **System E, additional Qwen3-ASR semantic evidence** | **0.87741** |

System E improved over D by **+0.03776 macro-F1** across the 826 labeled samples, with positive gains in all five original folds. An authenticated paired component-bootstrap interval was positive. **However, System E failed a predeclared quantization-related subgroup stress gate and was not scientifically promoted.** Its byte-reproduced 209-row inference is archived as an exploratory candidate.

Recorded public leaderboard scores were **0.88227 (D)** and **0.89505 (E)**, based on user-reported competition observations; they are not a final private leaderboard result, and this repository does **not** claim first place or a completed System F.

### Start here

- **[Research case study](docs/RESEARCH_PORTFOLIO.md):** objectives, data, architecture, results, ablations, robustness limits and evidence links.
- **[Final experiment archive](archive/2026-10-13/README.md):** authenticated 28F result, paired OOF, exploratory System F notebooks and Qwen recovery scripts.
- **[Post-competition archive checklist](docs/POST_COMPETITION_ARCHIVE_CHECKLIST.md):** preserved branches, external SHA256 manifests, pending local files and public-release requirements.
- [Validation authority](docs/ACTIVE_VALIDATION.md) — 5-fold duplicate-family-safe frozen V-B / PRIMARY_CV.
- [System E scientific report](runs/RS-DEFHS-FINAL-BREAKTHROUGH-001/SYSTEM_E_FINAL_SS_REPORT.md) — rigorous gains and explicit stress-gate failure.
- [System E 209-row production replay](runs/SS-DEFHS-SYSTEM-E-EXPLORATORY-DEPLOYMENT-001/TARGET209_FINAL_CANONICAL_VERDICT.md) — reproducibility and 78 certified retrieval assignments.
- [Source](scripts/) · [Kaggle execution packages](kaggle/) · [Tests](tests/) · [Experiment history](runs/).

### Scope and reproducibility

This repository stores original code, experimental protocols, reproducibility tests, audits, lightweight results and artifact manifests. Third-party datasets, model weights and larger representations are not bundled; consult the [archive checklist](docs/POST_COMPETITION_ARCHIVE_CHECKLIST.md) for authenticated prerequisites. Experimental code is **not** evidence that an experiment completed or that its candidate improved the deployed model.

**Visibility: private.** A cleaned public portfolio requires a separate review of competition rules, third-party rights, derivative data and repository history. The project used AI-assisted coding and research; only empirically verified outcomes are reported as findings.

### Historical scientific workflow

For the original step-by-step experimental authorities, see [WORKFLOW.md](WORKFLOW.md), [PROJECT_STATE.md](docs/PROJECT_STATE.md) and [HISTORICAL_VALIDATION_INDEX.md](docs/HISTORICAL_VALIDATION_INDEX.md). These documents describe the historical competition-time workflow rather than an active competition.
