# Current TARGET209 state

Mission: `SS-DEFHS-TARGET209-EMPIRICAL-RESET-001`. Report date: 2026-10-05.
Start: `8ba35644934a7b71cd557be65b9a2ca6b643fbf6`.

The [canonical matrix](../../docs/TEST209_PREDICTION_MATRIX.csv) now contains
209 verified test IDs and 64 columns. Original ZIP identity, test filenames,
all 209 recorded WAV hashes and original sample order pass verification.
Every row contains the accepted System1 prediction/probabilities, confidence
and margin, computed waveform disagreement, existing ASR/Qwen evidence,
labeled representation neighbors, certified retrieval and auxiliary provenance,
fold-head stability, an uncertainty mechanism and difficulty notes.

The 34 input artifacts have exact hashes and authority pointers in
[EVIDENCE_PROVENANCE](EVIDENCE_PROVENANCE.json). No model was fitted, no encoder
was run, and no protected assignment/result or Kaggle submission was accessed.
Historical scientific artifacts and the accepted system lock remain unchanged.

## Evidence categories

| Category | Test rows |
| --- | ---: |
| HIGH_CONFIDENCE | 136 |
| MEDIUM_CONFIDENCE | 13 |
| HARD | 60 |

The 136 high-confidence cases comprise 78 certified retrieval rows and 58
non-retrieval cases meeting the fixed agreement/confidence rules. Categories
are evidence triage, not test truth or calibrated correctness probabilities.
For perspective, the existing pair's PRIMARY_CV probability/margin screen still
has 35 wrong predictions among 455 high-probability rows; System1 has 113/619.
Those screens are not the full TARGET209 category rule.

Dominant HARD mechanisms: waveform model disagreement **39**; explicit
neutral/sad acoustic boundary **12**; fold-head instability **6**; low-confidence
acoustic boundary **3**. These are observed uncertainty patterns, not confirmed
test errors. [HARD_CASES.csv](HARD_CASES.csv) preserves all 60 cases.

The fixed pair's HARD-case top-two ambiguity pairs are neutral/sad **16**,
angry/neutral **11**, happy/sad **10**, angry/happy **9**, happy/neutral **9** and
angry/sad **5**. The narrower explicit neutral/sad mechanism covers IDs
`50, 72, 153, 172, 244, 440, 466, 493, 625, 884, 897, 951`.
PRIMARY_CV still has **35 neutral→sad** and **21 sad→neutral** pair errors.

## Predictions and disagreement

The following Wave 1 test vectors are **new deterministic derivations from
existing verified frozen heads and cached representations**, not imported
historical 209-row outputs. Each family averages its five ordinary PRIMARY_CV
heads; the pair averages the two families 50/50. This explicit deployment
implementation is not an all-826 XLS-R refit. Its saved heads reproduce their
original held-out OOF probabilities to numerical tolerance.

| Model | angry | happy | neutral | sad |
| --- | ---: | ---: | ---: | ---: |
| Accepted System1 | 60 | 45 | 55 | 49 |
| Original E2V five-head mean | 60 | 45 | 54 | 50 |
| Original XLS-R five-head mean | 56 | 37 | 58 | 58 |
| Fixed 50/50 pair | 62 | 42 | 54 | 51 |

| Disagreeing test rows | System1 | E2V | XLS-R | Pair |
| --- | ---: | ---: | ---: | ---: |
| System1 | 0 | 5 | 53 | 17 |
| E2V | 5 | 0 | 54 | 19 |
| XLS-R | 53 | 54 | 0 | 36 |
| Pair | 17 | 19 | 36 | 0 |

Qwen has 125 non-abstaining test labels and 84 `unclear` outputs. On the 125
comparable rows it disagrees with System1 on 52, E2V on 53, XLS-R on 59 and the
pair on 54. These compare lexical and vocal predictions, not correctness.
AST has zero comparable test probability rows. The coverage-aware complete
matrix is [MAJOR_MODEL_DISAGREEMENT.json](MAJOR_MODEL_DISAGREEMENT.json).

System1→pair changes: `24, 50, 136, 153, 237, 244, 307, 341, 361, 477, 651, 667,
671, 705, 819, 897, 907`. All 17 are HARD; **zero certified retrieval predictions
change**. Neutral/sad changes are `50, 153` neutral→sad and `244, 897` sad→neutral.
[SYSTEM1_TO_FIXED_PAIR_CHANGES.csv](SYSTEM1_TO_FIXED_PAIR_CHANGES.csv) records
every before/after label. Without test truth, corrections versus breakages are
unknown.

## Missing information for HARD cases

- AST test probabilities: missing for all 60 HARD cases and all 209 test rows.
  Existing frozen/adapted AST probabilities and inspected feature caches contain
  training IDs only. Adapted Wave 1 emotion2vec test outputs are also unavailable.
- Semantic probability vectors: missing everywhere. Qwen supplies hard lexical
  labels only; it abstains on 28 HARD cases and provides a class on 32, with 18
  conflicts against the current vocal decision. Seven of the 16 neutral/sad
  top-two cases are Qwen abstentions.
- Independent optimization-seed stability: unavailable on test. Reported
  stability is variation across existing fold-trained heads, not seed replication.
- Provenance/speaker truth: unknown. None of the HARD cases shares the strict
  ECAPA 0.10 cluster with a labeled training example. Recorded equal-length
  waveform comparisons cover 45 HARD cases, but none reaches the unchanged
  0.95 certification threshold. Representation-neighbor cosine is not duplicate
  certification. No source or speaker hypothesis becomes a test label.
- Mechanical ASR flags trigger on zero HARD cases under the declared thresholds.
  This does not establish transcript accuracy or that lexical meaning identifies
  vocal emotion.

## Current champion and public readiness

**Scientific challenger:** original emotion2vec/XLS-R fixed 50/50 pair.
**Accepted deployed reference:** System1 remains unchanged.

The exact saved-head candidate is **READY_FOR_ONE_CONTROLLED_PUBLIC_PROBE**.
PRIMARY_CV pair macro-F1 is **0.7768156647**, versus System1 **0.7383745766**
(+0.0384410882); all five fold deltas are positive, with 70 corrections and
38 breakages. This is reused development evidence, not independent confirmation.
The OOF metric uses each clip's held-out fold pair, not an in-sample average of
all five heads.

The [prepared CSV](submission_fixed_pair_cv5.csv) passes all 209 IDs, original
sample order/schema, normalized class probabilities, uniform five-head/family
weights, argmax without offsets, fixed 78-row retrieval and absence of adaptive
source/semantic/AST routing. No protected data is used in this construction.
Read [PUBLIC_SUBMISSION_READINESS](PUBLIC_SUBMISSION_READINESS.json) for the
explicit recipe and limits. SHA-256:
`1dd6b8db750ec6eee0b0f48d4148eceefcdd4bb5eaeb8454fa278597ae44818e`.

**No submission is authorized or made.** If later authorized, upload exactly this
CSV once and compare with the recorded System1 public evidence `0.79691`.
Record the returned score without retuning against it; private performance
remains unknown. The submitted control is not replaced by this readiness verdict.

The next scientific attack and parallel plan are in
[NEXT_EXPERIMENTS](NEXT_EXPERIMENTS.md).
