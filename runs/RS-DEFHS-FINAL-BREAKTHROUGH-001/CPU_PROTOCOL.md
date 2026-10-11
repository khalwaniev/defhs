# One frozen CPU hypothesis: acoustic probability geometry

Authority: `69ebbe3ca3c65f82e546fdf1d42e90fa885c8634`.
Incumbent: System D, PRIMARY_CV 0.8396460575108101, exact target CSV
SHA256 182bfbcd5fb10b351504da6d24f3d0d33f6d05cf2786e1e1a19e80afe0e57ec9.
Frozen before computing challenger predictions. Development reuse and selection
after incumbent error analysis are acknowledged; this is not independent confirmation.

Observation: 93 of D's 133 errors have a correct current individual expert;
95 errors rank the true label second under D. Unconditional expert replacement
has substantial false-override risk. Class prediction totals are already close
to training supports. A scalar temperature cannot change argmax at all.

Competing explanations: missing information; expert miscalibration; incorrect
functional form for combining acoustic evidence and lexical evidence.

Test ONLY the functional-form hypothesis. Replace each four-dimensional acoustic
probability vector by centered log probabilities,
`log(max(p,1e-6)) - mean(log(max(p,1e-6)))`. The numerical floor is fixed and is
not a confidence-routing threshold. Retain both five-state semantic one-hots,
18 total inputs, identical unscaled L2 logistic C=1, lbfgs, max_iter=5000,
random_state=20261001, intercept, no class weights. No alternatives, mixtures,
thresholds, C search or rescue. This tests probability coordinates and their
interaction with fixed regularization, not an isolated causal calibration effect.

For every frozen outer block, reuse/recompute genuinely inner-OOF acoustic
features from the other three blocks. Fit the meta head on outer-training
labels only. Held-out probabilities are the authentic archived original heads,
identical to D. No ordinary-OOF second-stage shortcut. Reproduce D before scoring.
No additional fit to D's full-data OOF decisions. Raw versus transformed inputs
are the sole candidate distinction. Preserve class order angry,happy,neutral,sad.

Primary gates, ALL required: pooled macro-F1 gain >=0.005; strictly positive in
>=4/5 folds; no class F1 drop >0.02; frozen HARD316 delta >=0; paired 2000-draw
duplicate/prompt-0.90-component multiplier-bootstrap 95% lower delta >0; positive
gain after deleting any one fold. Report exact corrections/breakages and all
class precision/recall/F1. If any gate fails, reject this entire CPU hypothesis;
do not tune a second probability transform or class rule.

Only a primary pass permits candidate-specific V-A pipeline/nonretrieval,
V-D directions, V-Q and private-allocation checks at least as stringent as D:
nonnegative V-A pipeline/nonretrieval; no V-D or supported diagnostic loss >.02;
nonnegative scenario mean private and weighted gains, weighted reversal <=20%.
Retain original private fraction/odds scope and distinguish scenarios from hidden
membership. No target production from a failed primary test.

Protected validation, Kaggle submission, public-score tuning and retrieval-map
modification are prohibited. System D remains the incumbent regardless of this
exploratory test. No GPU required.
