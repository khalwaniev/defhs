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
