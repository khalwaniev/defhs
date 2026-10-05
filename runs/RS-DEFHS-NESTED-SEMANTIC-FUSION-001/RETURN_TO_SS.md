# RS-DEFHS-NESTED-SEMANTIC-FUSION-001 — Return to Strategic Scientist

## Governance
START_HEAD: `2772fc61bfb01931335a35c8d45dc02569ab50e7`
Branch: `rs/nested-semantic-fusion-001`
Protected validation: NO. Public-LB tuning: NO. Kaggle submission: NO. Retrieval map mutation: NO. Encoder rerun: NO. GPU: NO.

## Nesting
NESTING_AUDIT = PASS. Every outer-heldout fold was excluded from inner base fitting and meta fitting. Inner cross-fitting used only the other four frozen PRIMARY_CV blocks. Qwen semantic state is fixed transcript-only evidence joined by Id.

Historical Wave1 heads were created under scikit-learn 1.7.2; this runtime is 1.8.0. Inner cross-fitting used the unchanged recipe under 1.8.0 because 1.7.2 could not be installed offline. Authoritative outer scoring was replaced with preserved historical outer probabilities. Saved-head replay had zero outer hard-label mismatches, and this parity substitution changed zero C hard decisions.

## PRIMARY_CV
A fixed parent: 0.7768156647359765
B waveform meta: 0.7581556185862871
C semantic meta: 0.8135577912484513
C-A = +0.03674212651247477
C-B = +0.055402172662164184
B-A = -0.018660046149689413

Fold A = [0.7110354010, 0.7377822341, 0.8384120669, 0.7621760797, 0.8343086029]
Fold B = [0.6937151970, 0.7383133662, 0.8370706029, 0.7207530613, 0.7982938651]
Fold C = [0.7548722211, 0.8123673740, 0.8494805999, 0.8250607091, 0.8255294349]

C per-class F1 = angry 0.8487804878; happy 0.8351063830; neutral 0.7749419954; sad 0.7954022989.
C vs A correction structure = 70 wrong->correct, 41 correct->wrong, 15 wrong->other-wrong.
C vs B = 76, 31, 18.

Exact 316-row HARD surrogate: A 0.5822591878; B 0.5335857999; C 0.6578392458.
Exact 56-row neutral<->sad fixed-parent error cohort: B corrects 5; C corrects 24.

alpha010 reference = 0.7896581648.
C - alpha010 = +0.0238996264.

## Promotion
PASS. C exceeds A and B by >+0.005, is positive versus both in 4/5 outer folds, has no severe class collapse, and the correction gain is distributed rather than one-fold-only.

## TARGET209
Strict five-outer-model C ensemble constructed because the screen passed. Five C probability vectors were averaged, ordinary argmax taken, then the unchanged 78-row retrieval override applied.

Reconstructed fixed-pair submission SHA256 exactly matches canonical:
`1dd6b8db750ec6eee0b0f48d4148eceefcdd4bb5eaeb8454fa278597ae44818e`

Reconstructed alpha010 SHA256 exactly matches canonical:
`c4600396b719821eb33711585b7782346e679fe06fc6f77413e66e5bccb71114`

Nested candidate changes 17 rows versus fixed pair and 15 versus alpha010. Of the 17 fixed-pair changes, 13 are HARD, 4 MEDIUM_CONFIDENCE, 0 HIGH_CONFIDENCE. Retrieval rows changed = 0/78.

Candidate SHA256:
`8ab7c5dc291cd9d1223283245fb62130b03bf728f764c5eeedf9d2915153e2a8`

These are changed TARGET209 predictions, not known corrections.

FINAL_VERDICT = `NESTED_SEMANTIC_FUSION_PROMISING`

Return to SS before any Kaggle submission.
