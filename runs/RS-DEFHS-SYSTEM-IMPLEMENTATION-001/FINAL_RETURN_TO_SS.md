# RS-DEFHS-SYSTEM-IMPLEMENTATION-001 — FINAL RETURN TO SS

Date: 2026-10-02. Status: **COMPLETE_PRE_PROTECTED_RETURN_TO_SS**.

The continuation closes legitimate mission state 3: the frozen finalist and all
remaining conditional decisions are locked, pre-protected diagnostics are
complete, and protected confirmation requires new explicit SS authorization.
This is an RS recommendation awaiting SS review, not SS acceptance.

Continuation starting local and remote SHA:
`16f271b50b1f6d4d3605b3ccb580d5667972dd45`.

Executed source/artifact snapshot SHA:
`d4c550b65b8b387fa331980d13323b6053748525`.

The final ledger/return SHA is the commit containing this file, reported after
remote HEAD verification in the closing message. It is not embedded in its own
hashed contents. Branch remains `rs/system-implementation-001`; no main merge.

## Locked system and measured results

Ordinary SER contains one member:
`iic/emotion2vec_base@v2.0.4` from ModelScope, cached frozen final frames,
mean+std pooling, StandardScaler and multinomial L2 logistic regression (`C=1`).
Decision is ordinary argmax in `angry / happy / neutral / sad` order. No class
offsets or ensemble weights remain. Certified unanimous-label retrieval remains
the separate, unchanged hard override: 77 fixed groups / 78 test clips.

| View | Macro-F1 |
|---|---:|
| V-B primary | 0.7383745765682462 |
| V-A secondary SER | 0.8016519493535111 |
| V-A fixed retrieval-aware pipeline | 0.8052768510049559 |
| V-A non-retrieval SER | 0.7311166934987506 |

V-B per-class F1: angry `0.8038277512`, happy `0.7229551451`, neutral
`0.7061611374`, sad `0.7205542725`. All folds, confusion matrices, probabilities
and per-class results are preserved. There is no test/leaderboard score.

The locked logistic recipe was fitted on all 826 cached training embeddings.
All 209 test probabilities and decisions are archived, including only the
existing 78-clip certified override. They were **not submitted**.

## Executed stages and exact bounded experiments

- Stage 0 and successful Stage 1–3 Kaggle V3 were reused. Both encoder caches,
  all OOF and input hashes were verified. No encoder/ASR extraction was repeated.
- Stage 4: recovered FULL_RBF_SVM probabilities with the existing imputer,
  scaler, `SVC(C=10, gamma=scale)` and sigmoid calibration inside three
  training-only inner folds; V-B calibration is duplicate-group-safe. The
  original uncalibrated hard labels reproduce exactly in both views. eGeMAPS
  reuses its existing imputer/scaler/logistic `C=.3` recipe and reproduces both
  recorded standalone scores.
- Evaluated seven existing one/two/three-member audio cores, equal weights first,
  the exact quarter-simplex/one-SD selector, and member deletions under five-way
  leave-one-existing-fold-out meta-validation. Conditional eGeMAPS uses only
  core versus 25% addition. Final closure reused those same selectors and
  completed the additions/ablations against the incumbent. No unrestricted
  stacker or added representation was introduced.
- Stage 5: one combined word `(1,2)` and character `(3,5)` TF-IDF logistic
  `C=.3` lane, plus a fold-safe control excluding held-out prompt90 clusters
  from fitting. Vocabularies/IDF and neighbor diagnostics use training only.
  Singleton, repeated, no-close-neighbor, mixed-cluster and CLEAN strata are
  preserved. No new language model.
- Stage 6: one prospective parent, emotion2vec, chosen before its pooling
  comparison. One linear temporal scorer, weighted mean/std and linear head;
  CPU FP32, ordinary CE/L2, fixed LR/regularization and maximum 30 epochs,
  cyclic training-only stopping, epoch zero included. Nine outer fits select
  zero epochs; one V-B fit selects four. No attention architecture sweep.
- Pre-PEFT / Stage 7: completed available head/pooling/offset controls and the
  fixed six-pair scan for both existing XLS-R head witnesses. Evaluated the
  machine gate once on the closed registry. **No PEFT experiment or GPU
  engineering preparation ran.**
- Stage 8: the exact 19 zero-sum logit vectors and one-SD minimum-norm shrinkage
  on four meta-folds, scoring the fifth. Membership was already locked.
- Stage 9: V-A, fixed retrieval audit, both V-D cross-format directions,
  Q128/Q960 subgroup intervals, 672 allocation scenarios at 75 replicates,
  four baseline fractions at 250, and 1500/2000/2000 boundary replications.

All continuation execution used CPU: **zero new accelerator-hours**. Historical
V3 quota charge remains UNKNOWN and is not reported as zero.

## Ensemble and conditional decisions

Final simultaneous marginal family has `q=3.4807950022`, using 2,000 paired
dependency-aware multiplier draws with the frozen duplicate/prompt90 unions.

| Candidate / comparison | V-B point | Marginal gain | Simultaneous lower |
|---|---:|---:|---:|
| emotion2vec + XLS-R versus emotion2vec | 0.7768156647 | +0.0384410882 | -0.0113734546 |
| emotion2vec + acoustic versus emotion2vec | 0.7575942175 | +0.0192196409 | -0.0055577570 |
| emotion2vec + conditional eGeMAPS versus emotion2vec | 0.7488241074 | +0.0104495308 | -0.0061850652 |
| Three audio members versus neural pair | 0.7793147298 | +0.0024990651 | below zero; fold/deletion checks also fail |

The neural pair improves all five fold points, but does not pass the simultaneous
credibility rule. Its positive observed gain is preserved; rejection does not
claim zero true ensemble value. The triple's acoustic member improves only two
folds and reverses after a fold deletion. No added member survives final closure.
Correlation, disagreement, per-class correction/breakage and oracle-union
ceilings are diagnostics, never membership substitutes.

eGeMAPS initially passed its narrow conditional family by a lower bound of only
`0.0000797291`. This historical pass is retained. It fails the complete final
marginal family, and V-A selects zero eGeMAPS weight. Final decision: kill.

Text blend V-B gain is `+0.0028071290`, falling to `+0.0004669319` under prompt
control; neither is robust, and no-close-neighbor gain is absent. Text is killed.
Pooling reaches standalone V-B `0.7394225674` but has no stable system value;
retain mean+std. Offsets reach `0.7319659648`, a `-0.0064086117` V-B change with
inconsistent fold choices; retain argmax. Happy was treated symmetrically.

## Terminal PEFT gate

Result: **NO_PEFT:DOWNSTREAM_NOT_CLOSED**.

- G0/G1: pass available authority/provenance and credible-parent checks.
- G2: **UNKNOWN**. Logistic/RBF and the one pooling comparison exist, but no
  scalar-mixture comparison or scaffold-time API-unavailability record exists.
  Only final-frame caches were produced. Do not retrospectively declare the
  architecture unsupported or repeat forbidden encoder extraction.
- G3: fail. Maximum available downstream upper bound `0.0308048448` exceeds
  `sigma_E=0.0174221360`; a null pooling result is not a bounded plateau.
- G4: fail. All twelve pair/head witness candidates fail necessary full/CLEAN
  simultaneous AUC and witnessed-residual criteria. Shared errors do not
  establish representation failure, irreducibility or label truth.
- G5: pass; no unpromoted frozen addition has robust system gain.
- G6: not entered because G0–G5 do not pass.

UNKNOWN fails the conjunction. Adaptation is closed under the accepted policy;
there is no rescue experiment, second parent or substituted recipe. The sole
recipe `DEFHS_UPPER_QUARTER_QV_LORA_FIXED_DOWNSTREAM_V1` was never triggered.

## Finalist stresses

V-D int16→int32 is `0.6347270616`; int32→int16 is `0.4247820352`. V-B subgroup
F1 is `0.7487828867` for 746 int16 rows and `0.6410285117` for 80 int32 rows.
Cross-format transfer remains a concrete limitation. Small Q strata have wide
intervals; e.g. Q960-606 has 41 rows, F1 `0.5580`, interval approximately
`[0.3814,0.7079]`. These diagnostics do not replace V-B or reopen selection.

Observable correlated-allocation boundary mean margins versus the accepted
cheap references remain positive: plausible `+0.0887990545`, strong tail
`+0.0778723064`, forced extreme `+0.0476597248`. Label-defined development
difficulty is reported as tail-only, never plausible hidden composition.
No scenario is assigned a probability of representing the hidden allocation.

Repeated OOF/meta-fold use and these conditional intervals do not remove
historical selection bias or constitute independent confirmation. Source/Q and
hidden transfer uncertainty remains for SS review.

## Preservation and final SS decision

V3: `gdrive:DEFHS/rs_system_implementation_001/kaggle_v3_frozen_screen`, folder
`1J4AfTLha26HGj3XHmgcWbYpX-TPG7fI9`. All 17 inventory files pass SHA256;
`rclone check --download` verifies **21/21 package files, zero differences**.
The stale original manifest self-hash is retained historically; the separate
SHA256 manifest excludes itself.

CPU package: `gdrive:DEFHS/rs_system_implementation_001/cpu_frozen_closure`,
folder `1vFKnPmUTIR4Nvc0Sn5vSTbfrL6V2HKIf`, archive
`1Xdf5knDljhGdZwHL6ITrrCZTruwrVSY5`. Archive is 54,654,350 bytes, SHA256
`5ede6c7d863784690e58333dd86f008a97073923a1f2c11a5ca95d26647e9d83`.
All 130 payload objects match the internal SHA256 manifest; independent Drive
download comparison verifies **4/4 archive/sidecar objects, zero differences**.
Final ledgers remain canonical in GitHub; the archive identifies its execution
snapshot commit. Existing local `.tmp/` work was preserved.

**Protected validation: NOT QUERIED. Kaggle competition submission: NOT MADE.**

No active execution blocker remains for pre-protected closure. Missing G2
evidence is an explicit terminal adaptation failure, not an invented PASS or
an indefinite pending adaptation run. Protected authorization is absent.

**Next SS decision:** review/accept the locked pre-protected finalist; if
proceeding, explicitly authorize one confirmation-only query of protected seed
20261001. No protected result may start another tuning loop. No submission or
main merge is authorized by this return.
