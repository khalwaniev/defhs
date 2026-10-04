# Next scientific attack

The objective is more correct TARGET209 predictions under four-class macro-F1.
The highest-value first attack is **emotion-aligned Hindi semantic fusion with
the fixed waveform pair**. This is a research priority, not a demonstrated new
champion. The largest unfilled measurement family is spectrogram evidence on
test; the current two-expert pair uses two WAVEFORM representations.

## Why this ordering

There are 60 HARD cases, including 16 with neutral/sad as the top-two pair.
Qwen supplies a lexical class for 32 HARD cases and abstains on 28; 18 lexical
classes conflict with System1. On the 316 PRIMARY_CV cases matching the
confidence/disagreement part of the HARD rule, Qwen is correct on 63 pair errors
but wrong on 34 pair-correct, non-abstaining cases. For the pair's 56
neutral/sad errors, Qwen is correct on 28 and abstains on 25.

Adapted AST is correct on 41 pair errors in that labeled surrogate but wrong
on 72 pair-correct cases; frozen AST is correct on 36 and wrong on 94. These
are **oracle complementarity counts**, not gains from a legitimate decision
rule. Standalone PRIMARY_CV macro-F1 is 0.60306 for the adapted AST seed mean,
0.54684 for frozen AST and 0.77682 for the pair.

This favors a cheap, supervised semantic marginal-value test before another
large acoustic training program. It does not justify replacing vocal predictions
with Qwen labels or calling text sentiment the true speech emotion. A new
experiment is justified by the changed waveform parent and its observed error
complementarity; it must beat that parent and a matched text-free control,
rather than repeat the previous source/dtype routing recipe.

Numerical expected corrections on test are **not identifiable** from these
unlabeled recordings. The counts below are reachable cohorts and labeled
signal opportunities, not invented predictions of recovered test labels.
PRIMARY_CV corrected/broken decisions and per-class macro-F1 determine whether
any opportunity becomes a useful experiment.

| Priority | Bounded next experiment | TARGET209 reach / expected-value basis | Required evidence before promotion |
| --- | --- | --- | --- |
| 1 | One fixed semantic fusion against the 50/50 parent, using existing Qwen class/abstention evidence | 32 HARD cases have a concrete semantic class; 28 have an explicit missing/ambiguous lexical signal. The 63/34 labeled complementarity counts motivate the cheapest discriminating study | Nested, train-side-only meta predictions; gain against both parent and matched text-free combiner; report corrections, breakages, all four class F1s and neutral/sad effects |
| 2 | Infer the 209 clips with already trained, verified frozen/adapted AST PRIMARY_CV models; no retraining | All 60 HARD cases lack spectrogram probabilities. Existing 41 recoverable versus 72 harmful surrogate disagreements limit confidence in direct AST routing | Complete ID/provenance/seed matrix; establish distinct useful errors on existing PRIMARY_CV before any ensemble membership |
| 3 | Blind transcript audit on the 28 HARD Qwen abstentions, followed only if warranted by one Hindi-capable semantic representation | Distinguish ASR word errors from intrinsically ambiguous/neutral text; do not assume all 28 are fixable by semantics | Preserve original transcripts; record corrections as transcription evidence only; use no invented target emotion labels; show supervised four-class marginal value on PRIMARY_CV |
| 4 | One targeted emotion-supervision study for low-arousal neutral/sad separation, after the first two attacks | Sixteen HARD top-two neutral/sad cases and 56 known PRIMARY_CV cross-confusions provide the concrete target; benefit and transfer remain unmeasured | Legitimate, reproducible external data/model authority; matched competition-only controls under existing folds; broad-corpus search and repeat encoder-family screens are not justified |
| 5 | Targeted auxiliary-evidence audit only where a new concrete defect is identified | The fixed retrieval map already covers 78 cases; none of the 60 HARD cases has a qualifying recorded waveform comparison or strict labeled speaker co-cluster. Expected incremental value is currently low | Preserve map, labels and threshold; no emotion labels inferred from source format, embedding similarity or speaker hypotheses |

Waveform representation work becomes a priority only if these studies identify
missing acoustic emotion information. Six HARD cases are dominated by fold-head
instability, but merely changing the RNG seed of the same deterministic logistic
problem is not a new emotion signal. Do not restart model-family screening or
revive a closed adaptation recipe without a materially different hypothesis.
External supervision is a training resource, not a fourth emotion modality;
the three active families remain WAVEFORM, SPECTROGRAM and SEMANTIC.

## Concrete first semantic experiment

Use a fixed regularized multinomial meta head, with the two waveform probability
vectors plus the five Qwen class/abstention indicators. Compare it with the same
meta head without Qwen and with the fixed arithmetic 50/50 parent. Fix the
feature transform and regularization before execution. No dtype, provenance or
public-score-dependent routing is allowed.

For each existing PRIMARY_CV outer fold, generate inner waveform predictions
using only that outer training population; fit the meta head there and score
the outer held-out fold once. Globally saved OOF vectors cannot simply be used
for outer meta training: some generating heads saw that outer held-out fold.
Reuse encoder caches; bounded CPU head fitting supplies the needed nesting.
Do not change any fold assignment or use protected validation. A raw in-sample
or oracle gain does not earn membership.

Use 0.005 macro-F1 as a predeclared material-gain screen, positive direction in
at least four existing folds, and inspect class-level corrections/breakages.
If apparent value is small or ambiguous, replicate the bounded study rather
than tune another routing rule on public feedback. The first study's verdict
must attribute value to semantics over its matched text-free control.

Any later external-supervision work must follow
[EXTERNAL_DATA_POLICY](../../docs/EXTERNAL_DATA_POLICY.md), including the required
matched comparisons before promoting an external encoder. This reset does not
promote an external corpus or reopen licensing assumptions.

## Parallel execution plan

This is a proposed plan; no new training/encoder job or delegated chat has been
launched by this mission.

1. **RS-SEMANTIC, CPU:** run the bounded nested semantic comparison and its
   matched text-free control. Return fold/class corrected-versus-broken evidence
   and candidate probabilities with exact provenance.
2. **RS-SPECTROGRAM, one GPU inference lane:** verify the existing ordinary
   PRIMARY_CV AST checkpoints, run fixed 209-row inference, and fill the missing
   spectrogram columns. Hold adaptation/training fixed. Return test disagreement
   and labeled marginal evidence; do not select a checkpoint on test confidence.
3. **DS-EVIDENCE, read-only:** audit the 28 HARD transcript abstentions and the
   small number of ambiguous labeled-neighbor relationships. Keep transcription,
   possible source artifacts and emotion truth separate. Review external-data
   authority only if the low-arousal supervision hypothesis survives.
4. **SS:** own the common parent, frozen folds and experiment boundaries.
   Optionally perform the single prepared public probe only after explicit user
   authorization. Integrate evidence after the bounded jobs close; Public LB
   stays partial evidence and protected validation stays closed.

All workers use this 209-case matrix and the unchanged PRIMARY_CV. They do not
recursively read historical runs. Results are joined by exact test ID; every
job must answer which HARD cohort it could resolve and how PRIMARY_CV supports
that claim. No public submission or model promotion is automatic.
