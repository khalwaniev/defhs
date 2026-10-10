# RS-DEFHS-STRONG-LLM-SEMANTIC-001 — fixed protocol

Parent: `c4206ae99ba5ee19eb06f7b72bcbbebac6cd7458` on
`rs/pocket-mimi-representation-001`. WORKFLOW.md governs. No protected validation,
public-score selection, certified-retrieval change, or submission is authorized.

## One selected model

`claude-opus-4-6`, Anthropic Messages API, API version `2023-06-01`.
Adaptive thinking, high effort, 2,048 maximum output tokens including thinking.
No temperature, examples, tools, web search, audio, predicted acoustic labels,
training labels, filenames, folds, or clip IDs enter a request. Each request
contains the fixed PROMPT.txt and one original Hindi transcript. Exact duplicate
strings share a response. There are 711 unique training strings for 826 clips.
The JSON output supplies a forced four-class label and an evidence-sufficiency
flag. For the optional fusion, insufficient evidence maps to `unclear`.

This is a different fixed prompt/output contract from historical Qwen3-8B, which
returned one of five states. Report this difference; the test measures the value
of the complete stronger semantic extractor, not an isolated parameter-count
effect. Both full-population and coverage-aware comparisons are mandatory.
No prompt, reasoning-effort, model, or decoding search is permitted after labels
are compared. Invalid/refused/truncated responses stop execution, not become
`neutral` or a rescue-prompt candidate. The provider pins the model version;
bitwise deterministic API regeneration is not guaranteed. Preserve responses.

## Stage 1: transcript-only inference and standalone evaluation

Use the sealed TRAIN826_INPUTS.json payload; it contains only Id/text, verified
against the original packaged ASR payload. Inference does not open the label or
fold files. Freeze CONFIG.json/PROMPT.txt before inference. API responses and
usage are journaled by transcript hash. Model-access failures are infrastructure
results. A $10 accounting limit is the execution default, not a promise that all
711 requests will finish within that amount. Count tokens and reserve the full
output limit before each request; report actual usage and estimated charges.
On uncertain request completion, stop rather than silently rebill or reroll.

After all 826 predictions exist, evaluate once against the original PRIMARY_CV
membership (SHA-256 `87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b`).
Report pooled four-class macro-F1, precision/recall/F1/support, 4x5 confusion,
each original fold, abstention coverage, corrections/breakages, and neutral/sad
transitions. The forced prediction is a four-class result for every clip.
The abstaining view counts `unclear` as a false negative for the true class;
it never adds an artificial fifth class to macro-F1. Historical Qwen's covered
score must not be compared as if it covered all 826 clips.

System C's row-level OOF authority is currently missing. Its aggregate metrics
cannot determine paired corrections. Before such a comparison, recover the
original artifact and independently recorded checksum; check exact Id/label/fold
alignment, overall score, and all five fold scores. A checksum computed solely
from an unverified replacement file is not provenance. The runner accepts these
as explicit inputs once recovered. No row-level C predictions are synthesized.

## Conditional Stage 2: exactly one properly nested fusion

Enter only if the complete valid training run shows new information, including
corrections of System C errors in at least three of five original folds. This
is a descriptive entry screen, not evidence that a deployable fusion improves.
If useful complementarity is absent, close the branch without fusion.

The sole candidate is C plus one-hot strong-LLM states (angry/happy/neutral/sad/
unclear): 18 features instead of C's 13. Use the existing multinomial L2
LogisticRegression recipe, C=1, lbfgs, fit_intercept=true, no class weighting,
max_iter=5000, random_state=20261001. No hyperparameter/weight selection.

For each outer PRIMARY_CV fold, exclude it from every supervised fit. Use only
the other four original fold blocks for inner base-head cross-fitting. Fit C
and C+LLM on the identical eight inner waveform probability features and the
same original five-state Qwen encoding; add only the five new states for the
candidate. Fit the original waveform heads on the outer training rows, predict
the outer-heldout rows, and apply each corresponding meta-head once. Reuse
verified cached embeddings/probabilities and the authoritative environment.
Replay the original C result before accepting the paired comparison.

Do not fit a new stacker to ordinary C OOF predictions split again into five
folds: other rows' OOF models can have consumed the outer-heldout labels.
That shortcut is not a properly nested evaluation.

Promotion screen, fixed before candidate evaluation: pooled gain at least
0.005 over replayed C, positive gain in at least 4/5 outer folds, positive net
corrections, no per-class F1 loss larger than 0.02, and no single-fold-only gain.
Report the actual evidence even if this screen fails. Validation reuse and the
small sample prevent interpreting the screen as an independent statistical proof.

## Conditional Stage 3: TARGET209

Only after the fusion screen passes, infer all 209 original test transcripts
using the same model, prompt and settings (reusing exact-string cached responses).
Use the mean of the five corresponding outer-fitted fusion predictions, argmax,
then the unchanged 78-row certified retrieval override. Verify original 209 IDs,
sample order, schema, allowed labels, zero retrieval changes, file checksum,
and every change relative to C. Changes are not known corrections.
Produce exactly one candidate and return to SS; never submit automatically.

Stages 2 and 3 are specifications, not executed or implemented deliverables in
this access-blocked checkpoint. No model is substituted for inaccessible Opus.
