# Current authority mapping

As of `DEFHS-TARGET209-CONTEXT-CLEANUP-001` (2026-10-04), start with
[ACTIVE_COMPETITION_STATE](ACTIVE_COMPETITION_STATE.md),
[ACTIVE_VALIDATION](ACTIVE_VALIDATION.md) and
[TARGET209_STRATEGY](TARGET209_STRATEGY.md). The operational objective is to
maximize four-class macro-F1 on the exact 209 supplied test WAV files.
`PRIMARY_CV` aliases the existing V-B; TARGET209_ANALYSIS and Public LB supply
target-domain and partial real-test evidence.

The original objective lock below is preserved verbatim as historical context.
Its final/private-leaderboard wording maps to accurate TARGET209 prediction;
the recorded 40/60 score weights remain score weights. This mapping changes no
scientific result or competition configuration.

---

# Objective Lock

## Competition

DataVerse: Detecting Emotions from Hindi Speech

Kaggle slug:

`dataverse-detecting-emotions-from-hindi-speech`

## Official target

Predict one of:

- angry
- happy
- neutral
- sad

for every test audio file.

## Official metric

Macro F1:

`(F1_angry + F1_happy + F1_neutral + F1_sad) / 4`

## Final ranking

Organizer overview states that final ranking combines:

- 40% public leaderboard score
- 60% private leaderboard score

Therefore the project must optimize robust hidden-test generalization rather
than public-LB fit.

## Project objective

Primary objective: finish #1 on the final leaderboard.

Scientific objective: maximize defensible expected private-LB macro F1 using
reproducible validation, leakage analysis, strong pretrained SER/speech
representations, justified external data, and low-variance ensembling.

## Protected principles

- Do not optimize to public-LB noise.
- Do not change validation casually after model selection begins.
- Do not allow duplicated recordings to silently inflate validation.
- Do not train on external labeled corpora merely because they are available.
- Do not spend GPU quota before cheap decisive diagnostics are exhausted.
