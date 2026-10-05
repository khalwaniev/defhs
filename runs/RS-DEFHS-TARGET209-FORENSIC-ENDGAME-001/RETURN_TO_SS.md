# RS-DEFHS-TARGET209-FORENSIC-ENDGAME-001 — Return to Strategic Scientist

## Governance

- START_HEAD: `3de7ff16471d8ab581055d37c1bc8c4b81ff4469`
- Protected validation queried: **NO**
- Kaggle submission: **NO**
- Manual / human labeling of TARGET209 audio: **NO**
- Certified 78-row retrieval map modified: **NO**
- Broad historical model search reopened: **NO**

The mission followed `WORKFLOW.md`: cheapest decisive provenance test first, frozen PRIMARY_CV for labeled evidence, negative evidence retained, and no promotion/submission decision taken by RS.

## Phase A — public-source / provenance reconstruction

Candidate investigated: public **BhavVani / CAMuLeNet** corpus from Goel, Hira & Gupta, Interspeech 2024.

Public evidence:
- The competition describes **SRCASW-BhavVaani** as a self-curated custom Hindi SER set with 1,036 samples, acted + spontaneous.
- The public BhavVani paper describes a Sarabhai-vs-Sarabhai-derived Hindi emotion corpus with 8,734 utterances and seven emotions.
- The current public Hugging Face metadata mirror exposes 7,991 metadata rows across train/validation/test. Audio is not openly downloadable from that mirror without the dataset access process/form.
- The mirror declares `cc-by-nc-2.0`; its dataset terms additionally restrict use to non-commercial research and prohibit redistribution.

### Deterministic filtering/order falsification

Tested rule:
1. preserve public metadata row order;
2. retain only `Anger, Enjoyment, Neutral, Sadness`;
3. map `Enjoyment -> happy`, `Anger -> angry`, `Neutral -> neutral`, `Sadness -> sad`;
4. assign retained rows densely to competition Id order.

Because any concatenation of the public train/test/validation splits must begin with one of the three splits, each possible split-start prefix was tested against known competition labels until the exact-order hypothesis was decisively falsified:

| public split starting order | known rows checked | matches | false matches | agreement |
|---|---:|---:|---:|---:|
| train | 65 | 21 | 44 | 0.32308 |
| test | 60 | 15 | 45 | 0.25000 |
| validation | 46 | 13 | 33 | 0.28261 |

These rates are incompatible with an exact deterministic identity/order construction. No rule with extremely high known-row precision was found.

Additional automated source check: across the machine-generated normalized ASR for all 1,035 competition clips, there were zero occurrences of the public source/character markers tested (`Maya, Monisha, Sahil, Rosesh/Roshesh, Indravardhan, Sarabhai`, including Hindi-script variants). This is supporting evidence only, not an audio-identity proof.

**SOURCE_RELATIONSHIP:** `NO_REPRODUCIBLE_RELATION_FOUND`  
**SOURCE_MATCH_PRECISION:** no accepted mapping; best simple-order prefix agreement = `0.32308`  
**SOURCE_TARGET209_COVERAGE:** `0/209`  
**EXACT_REPRODUCTION_RULE:** none  
**PUBLIC_AUDIO_IDENTITY:** not testable from public metadata-only access; no source label inference was propagated to TARGET209.

## Phase B — independent hard-case evidence

The existing frozen fixed E2V/XLS-R pair was used as the exact parent:
- PRIMARY_CV Macro-F1 = **0.7768156647**

A single conservative semantic perturbation was fixed before scoring:
- if Qwen semantic label is one of the four competition classes, use  
  `p' = 0.90 * p_fixed_pair + 0.10 * one_hot(Qwen)`;
- if Qwen abstains/returns `unclear`, leave the pair unchanged;
- certified retrieval rows are immutable.

Result:
- semantic Macro-F1 = **0.7896581648**
- delta = **+0.0128425001**
- fold deltas = **[+0.0067230, +0.0371279, +0.0121665, +0.0069309, +0.0013906]**
- positive folds = **5/5**
- OOF decisions changed = **29/826**
- wrong -> correct = **18**
- correct -> wrong = **8**
- wrong -> different wrong = **3**

Per-class deltas:
- angry: **-0.0028008**
- happy: **+0.0222696**
- neutral: **+0.0156016**
- sad: **+0.0162996**

On the exact 316-row hard surrogate already defined by the TARGET209 evidence builder:
- pair Macro-F1 = **0.5822591878**
- semantic Macro-F1 = **0.6109866729**
- delta = **+0.0287274852**
- all 29 changed OOF decisions are inside this hard surrogate; zero changes occur outside it.

Negative control:
- 2,000 deterministic permutations of Qwen clear labels, preserving clear/abstain positions and the Qwen class histogram;
- mean delta = **-0.0042441**
- maximum permutation delta = **+0.0110979**
- permutations reaching the observed +0.0128425 = **0/2000**.

Post-hoc sensitivity showed larger gains at higher semantic weights; those weights were **not promoted or used**. Alpha remains frozen at 0.10 to avoid opportunistic retuning.

### Real TARGET209 application of the frozen rule

The rule changes only two non-retrieval HARD predictions:
- Id 265: `angry -> neutral`; waveform-model disagreement; fixed-pair margin 0.01594.
- Id 884: `sad -> neutral`; neutral/sad acoustic boundary; fixed-pair margin 0.03988.

Certified retrieval rows changed: **0/78**.

These are **changed predictions**, not claimed corrections.

**BEST_NEW_INDEPENDENT_SIGNAL:** `QWEN_TRANSCRIPT_SEMANTIC_ALPHA_0.10`

## Phase C — transductive / synthetic adaptation

One cheap feature-space mechanism was predeclared and tested, then stopped:
- 395 numeric acoustic/domain features from the frozen full acoustic table;
- outer fold treated as unlabeled pseudo-test;
- teacher trained only on outer-train;
- pseudo-test feature mean/scale used to shift outer-train features into a synthetic pseudo-test domain;
- no pseudo-test waveform cloned;
- synthetic copy retained only when teacher confidence >= 0.70 and class prediction is stable before/after the shift;
- student uses the identical model family and original + retained synthetic rows.

Matched non-transductive parent Macro-F1 = **0.5953630854**  
Transductive student Macro-F1 = **0.5968060240**  
Delta = **+0.0014429386**

Fold deltas:
- fold 0: **-0.0098274**
- fold 1: **+0.0054427**
- fold 2: **-0.0190644**
- fold 3: **+0.0135362**
- fold 4: **+0.0185241**

Per-class deltas:
- angry: **+0.0021347**
- happy: **+0.0135864**
- neutral: **-0.0170875**
- sad: **+0.0071381**

Promotion screen: **FAIL**
- aggregate gain < +0.010;
- positive only 3/5 folds;
- neutral class declines.

Per instruction, synthetic/transductive development is terminated. No generative-audio experiment is justified.

## TARGET209 evidence table

`TARGET209_FORENSIC_EVIDENCE.csv` contains all 209 rows from the existing prediction matrix plus:
- source-recovery status;
- frozen semantic alpha;
- semantic candidate class;
- whether the semantic rule changes the fixed pair;
- semantic-signal status;
- transductive-screen status.

The original `docs/TEST209_PREDICTION_MATRIX.csv` and certified retrieval map were not modified.

## Return decision

**FINAL VERDICT: `MULTIMODAL_ADJUDICATION_PROMISING`**

Reason: provenance recovery and transductive synthetic adaptation fail their decision gates, while Qwen transcript semantics supplies statistically nontrivial, fold-consistent OOF marginal information concentrated entirely in the acoustic-hard region. The frozen conservative rule changes only two TARGET209 rows and preserves all 78 certified retrieval rows.

Return to SS before any Kaggle submission.
