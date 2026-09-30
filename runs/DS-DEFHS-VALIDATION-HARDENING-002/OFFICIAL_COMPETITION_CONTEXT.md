# Official Competition Context

Recorded 2026-09-30 for DS validation design.

## Competition-provided statements

The Kaggle overview/data-page information supplied for this mission states:

- dataset name: SRCASW-BhavVaani;
- language/task: Hindi speech emotion recognition;
- described corpus size: 1,036 audio samples;
- composition: both acted and spontaneous speech;
- classes: angry, happy, neutral, sad;
- official metric: macro F1, averaging per-class F1 equally;
- final competition score:
  `0.40 * Score_public + 0.60 * Score_private`;
- test labels are withheld;
- train rows map IDs/filenames to emotion labels;
- test rows expose IDs/filenames only;
- sample submission provides the operational submission schema.

The overview also frames generalization beyond already-seen voices and
expressions as a competition question.

## Important caveats

- Direct package inspection found 826 train + 209 test = 1,035 supplied
  train/test examples, one fewer than the 1,036 stated in prose.
- The 0.40/0.60 final-score weights do **not** by themselves establish the
  public/private sample fractions.
- Internal validation can only approximate the hidden/private evaluation. It
  must never be described as guaranteed to reproduce the private leaderboard.

## Authority order for implementation details

Where prose examples and actual competition files disagree, record the
discrepancy and use the supplied competition files/sample submission as the
operational schema unless an organizer clarification supersedes them.
