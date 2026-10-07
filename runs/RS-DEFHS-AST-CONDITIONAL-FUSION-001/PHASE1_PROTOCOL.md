# Phase-1 protocol — predeclared before results

## Population
For each frozen PRIMARY_CV outer fold independently, restrict to rows on which accepted C and accepted AST B1 hard predictions disagree.

Outcome labels (used only to evaluate/train the mechanism gate):
- AST_WIN: AST correct, C wrong
- C_WIN: C correct, AST wrong
- BOTH_WRONG: both wrong
BOTH_CORRECT is impossible in the disagreement population.

## Internal cross-fit
Within each original held-out fold, use StratifiedKFold(n_splits=4, shuffle=true, random_state=20261007) over the three outcome strata. For each internal split:
- gate-training rows and gate-evaluation rows are disjoint;
- train the binary gate only on AST_WIN vs C_WIN rows in the training partition;
- preserve BOTH_WRONG rows in the evaluation partition;
- produce an out-of-fold gate score for every disagreement row.

This is a bounded mechanism test, not a new PRIMARY_CV fusion authority.

## Primary gate
Pipeline:
- StandardScaler for continuous features
- OneHotEncoder(handle_unknown='ignore') for categorical features
- LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=5000, class_weight=None, random_state=20261007)

Target: P(AST_WIN | decisive disagreement).
Decision threshold: exactly 0.5. No threshold search.

Optional depth<=2 tree is not run unless required only as a sanity diagnostic; it cannot rescue a failed logistic gate.

## Metrics
Per original fold and pooled:
- disagreement N; AST_WIN; C_WIN; BOTH_WRONG
- ROC-AUC on AST_WIN vs C_WIN
- balanced accuracy at fixed 0.5
- predicted AST-use rate over all disagreements
- AST_WIN corrections captured
- C_WIN cases broken
- net corrections = captured - broken
- routing of BOTH_WRONG
- captured/broken counts by true class
- neutral/sad correction/breakage and neutral<->sad cross-breakage

Also compute a descriptive full-826 macro-F1 after applying only the internally cross-fitted gate decisions to C. This is mechanism evidence only and MUST NOT be called a valid new PRIMARY_CV score.

Uncertainty: 2000 stratified bootstrap resamples within original-fold/outcome strata for pooled decisive-row AUC, seed 20261007.

## Phase-1 pass gate
ALL must hold:
1. pooled AST_WIN-vs-C_WIN AUC > 0.55 AND bootstrap 95% lower bound > 0.50;
2. per-original-fold AUC > 0.50 in at least 4/5 folds;
3. captured AST wins span at least 3/4 true classes and no one class supplies >60% of captured wins;
4. aggregate neutral/sad net corrections are non-negative and neutral<->sad cross-breakages do not exceed neutral/sad AST wins captured;
5. fixed-0.5 net corrections > 0 in at least 4/5 original folds;
6. every used feature is inference-available and target-independent with an exact TARGET209 analogue;
7. conditions 1-6 collectively provide enough evidence to justify the substantially more expensive strictly nested AST refit.

Failure of any mandatory condition => FINAL_VERDICT=AST_CONDITIONAL_FUSION_CLOSED and Phase 2 is not run.
