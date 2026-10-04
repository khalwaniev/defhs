# TARGET209 strategy

Current population: `SS-DEFHS-TARGET209-EMPIRICAL-RESET-001`. Read its compact
[current TARGET209 state](../runs/SS-DEFHS-TARGET209-EMPIRICAL-RESET-001/CURRENT_TARGET209_STATE.md)
for the 209-case evidence map, 60 HARD cases and prepared fixed-pair public probe.
The original identity scaffold is now populated from verified saved evidence
and explicitly documented cached-head derivations. No training, encoder
execution, protected query or submission occurred.

Every experiment must answer:

> "How could this make more of the 209 test predictions correct?"

Judge that mechanism using PRIMARY_CV, unlabeled TARGET209_ANALYSIS and any
already authorized Public LB evidence. Macro-F1 gives each of the four classes
equal weight; raw accuracy, confidence or an easy duplicate subset alone is
not the objective. Analysis does not reveal withheld labels. No experiment,
retraining, protected query or submission is authorized by this cleanup.

## Canonical TEST209_PREDICTION_MATRIX

[TEST209_PREDICTION_MATRIX.csv](TEST209_PREDICTION_MATRIX.csv) is the canonical
one-row-per-test-ID evidence surface. Its 209 unique IDs must exactly equal the
`split=test` rows of the existing
[DATA_MANIFEST.csv](../runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv).
Keep each recorded filename and WAV hash. The initial ID order matches the
archived implementation submission, whose original sample-order parity was
already recorded; future submission preparation must still check the original
sample submission. This matrix is an analysis artifact, not a submission.

The original initialization copied **only recorded identity and source-format metadata**
from that manifest (SHA-256
`1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469`).
Prediction/evidence columns are populated only from verified artifacts or
explicit reproducible derivations. Remaining empty fields mean **not populated
here**, not zero, negative
evidence or proof that no historical computation exists. No test labels or
scientific predictions are invented.

| Required columns / evidence family | Meaning and population rule |
| --- | --- |
| `Id`, `filename`, `file_sha256` | Exact supplied test identity and recorded WAV SHA-256 |
| `source_format`, `metadata_provenance` | Existing PCM dtype and its manifest pointer; auxiliary evidence |
| `waveform_p_{class}` | WAVEFORM probabilities for angry/happy/neutral/sad |
| `spectrogram_p_{class}` | SPECTROGRAM probabilities for the same four classes |
| `semantic_p_{class}` | SEMANTIC probabilities; ASR → Hindi-capable language representation |
| `ensemble_p_{class}` | Ensemble probabilities with recorded members/weights/calibration |
| `predicted_class` | Named model/ensemble decision; explicitly record any certified override |
| `confidence`, `margin` | Chosen probability maximum and top-1 minus top-2, with probability source identified |
| `model_disagreement` | Declared comparison, e.g. disagreeing model count or probability divergence |
| `seed_model_stability` | Agreement/dispersion across explicitly named seeds/models |
| `nearest_train_Ids`, `nearest_train_labels` | Matched labeled examples and their recorded train labels; identify representation and distance in provenance |
| `duplicate_evidence` | Exact/near-duplicate evidence, certified map membership, threshold and matched IDs; unassessed is not non-duplicate |
| `provenance_evidence`, `source_domain_similarity` | Recorded provenance and source/domain comparison with method and limitations |
| `speaker_like_similarity` | Defensible speaker-like comparison only; never silently convert similarity into speaker identity |
| `asr_transcript` | Existing ASR output with model/revision and decoding provenance |
| `uncertainty_category`, `difficulty_notes` | Evidence-based category and why this case is difficult |
| `probability_provenance`, `model_set` | Artifact path/hash, producing run/commit, model revisions, class order, seed and decision recipe |
| `evidence_status` | `IDENTITY_ONLY` initially; later state which evidence has actually been populated |

The empirical reset adds explicit `wave1_e2v_p_{class}` and
`wave1_xlsr_p_{class}` vectors from each family's five ordinary PRIMARY_CV heads,
and `fixed_pair_cv5_p_{class}` from their uniform 50/50 mean. `ensemble_p_{class}`
identifies that exact candidate. `predicted_class`, `confidence` and `margin`
continue to describe accepted System1; separate `fixed_pair_*` fields describe
the candidate and its changes. Nearest-example records identify each
representation and cosine metric. The
[evidence registry](../runs/SS-DEFHS-TARGET209-EMPIRICAL-RESET-001/EVIDENCE_PROVENANCE.json)
records input hashes, recipe, source revisions and missing test artifacts.
Spectrogram/semantic probability fields remain empty because existing AST
outputs are training OOF and Qwen supplies hard lexical labels only.

`{class}` expands to the four explicit columns in order
`angry, happy, neutral, sad`. Each populated probability family must contain
four finite values in [0,1] summing to one within documented numerical tolerance.
Do not relabel logits or uncalibrated scores as probabilities. If a family has
multiple candidates, identify the selected row vector and reference the
per-model artifact; never silently mix models across rows.

Confidence/margin must refer to a named probability vector. A hard retrieval
override does not manufacture confidence=1. Similarities need their metric,
reference population and threshold. JSON arrays/objects may be CSV-quoted for
multi-example or structured evidence. Candidate uncertainty categories include
low confidence, family disagreement, instability, weak retrieval evidence,
uncertain transcript and possible source shift; assign them only from evidence.

## Reuse available evidence when a question requires it

- Certified duplicate/group evidence: existing
  [RETRIEVAL_MAP_FINAL.csv](../runs/DS-DEFHS-VALIDATION-HARDENING-002/RETRIEVAL_MAP_FINAL.csv)
  and [DUPLICATE_GROUPS_FINAL.csv](../runs/DS-DEFHS-VALIDATION-HARDENING-002/DUPLICATE_GROUPS_FINAL.csv).
  Preserve the 77 groups / 78 test clips and existing override decisions.
- Accepted system/test-inference provenance:
  [FINAL_SYSTEM_LOCK.json](../runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001/FINAL_SYSTEM_LOCK.json)
  and [ARTIFACT_MANIFEST.csv](../runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001/ARTIFACT_MANIFEST.csv).
  A submission CSV alone supplies no probabilities.
- ASR: the existing
  [closure manifest](../runs/DS-DEFHS-VALIDATION-HARDENING-002/CLOSURE_COMPLETED_ARTIFACT_MANIFEST.tsv)
  points to `/DEFHS/ds_validation_002/asr_transcripts/ASR_TRANSCRIPTS.csv`.
  Recorded SHA-256: `a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01`.
- Historical semantic outputs:
  [SEMANTIC_INFERENCE_MANIFEST.json](../runs/RS-DEFHS-SCORE-PUSH-001/SEMANTIC_INFERENCE_MANIFEST.json).
  OOF-only evidence from any family must not be presented as test predictions.

Join by ID, verify target coverage and artifact provenance, and distinguish
train-neighbor labels from predicted test classes. Keep family probabilities,
ensemble decisions and auxiliary overrides auditable. The existing class
labels, raw audio, model artifacts and scientific results stay unchanged.
