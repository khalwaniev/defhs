# RS-DEFHS-ADAPTATION-POLICY-001 — ADAPTATION POLICY

Version: pre-OOF policy v1, 2026-10-01. Status: complete, pending SS integration.
Evidence/input HEAD: `5d81af578cd67c4e9826d270c11abbe1812652c1`.

## 1. EXECUTIVE DECISION

**FROZEN_DIVERSITY_PRIOR.** Complete the small frozen screen and select a simple
representation-diversity ensemble first. Reserve no automatic adaptation run.
An experiment is triggered only by the conjunction in Section 6. The actual
trigger is currently **PENDING_FROZEN_OOF**, not empirically passed or failed.

The permitted exception is exactly one **upper-quarter query/value LoRA**
experiment on one deterministically selected frozen parent. Its layer mixture,
pooling, classifier and preprocessing remain fixed. Only the specified low-rank
encoder parameters change. Run two fixed optimization seeds, then judge the
seed-average lane and both seeds against the exact parent and frozen system.

The central distinction is an **actionable representation hypothesis**, not
proof of a representation bottleneck. Shared mistakes, low margins or a weak
happy F1 alone cannot identify representation failure. Require a different
already-screened frozen neural representation to demonstrate discrimination of
the affected class pair, while the permitted frozen blends and downstream
controls still leave stable errors. If this evidence is absent, adaptation ends.

No expected DEFHS score, theoretical PEFT gain, private-LB prediction or
checkpoint-use permission is implied.

## 2. EVIDENCE ACTUALLY USED

### Evidence labels

- **DIRECT_DEFHS:** measured competition evidence already in the authorities.
- **STRONG_EXTERNAL:** SER evidence closely bearing on the intervention.
- **TRANSFERABLE_EXTERNAL:** relevant evidence with material corpus/language/regime differences.
- **MECHANISTIC:** representation/layer evidence, not performance superiority.
- **INFERENCE:** this policy's scientific and decision-design choices.
- **UNKNOWN:** not identified by current evidence.

### Existing DEFHS evidence

**DIRECT_DEFHS.** DS records verify 826 training clips, class supports
205/192/217/212 and FULL_RBF_SVM V-B macro-F1 `0.6310269549` at the frozen
seed. Its per-class F1 is approximately `0.6714/0.5823/0.6389/0.6316`.
Existing alternate, non-protected DS allocations yielded V-B `0.6173208585`
and `0.6219651206`. The frozen-seed fold scores range from approximately
`0.5938` to `0.6782`. These demonstrate selection sensitivity; they are not a
universal numerical noise threshold for future encoders.

**DIRECT_DEFHS.** The post-red-team authority establishes moderate,
representation-dependent residual train/test shift without identifying one
alternate hidden grouping mechanism. Prompt repetitions mostly overlap the
duplicate graph; residual prompt dependence still deserves diagnostic checks.
Int16/int32 recording regimes are verified. Speaker/latent clusters do not
establish authoritative new groups. Relevant paths:

- `runs/DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001/POST_REDTEAM_VALIDATION_AUTHORITY.md`
- `runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_STABILITY_RESULTS.json`
- `runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_PER_CLASS_F1.csv`
- the same directory's `FINAL_VALIDATION_AUTHORITY.md`,
  `SOURCE_STRUCTURE_REPORT.md`, `TRANSCRIPT_STRUCTURE_REPORT.md`.

### Acquired sources inspected directly

Page numbers below are physical PDF pages, not necessarily printed page numbers.

| Source | Evidence classification | Material inspected and conclusion | Limitation |
|---|---|---|---|
| DEFHS-KNOW-0006, Ma et al., emotion2vec | STRONG_EXTERNAL for frozen SER; TRANSFERABLE_EXTERNAL for multilingual transfer | pp. 4–8 and 12–13: downstream upstream freezing, small head, multilingual results and evaluation protocols; English emotion pretraining supports useful frozen representations in other languages | No Hindi/DEFHS experiment or controlled target-PEFT comparison. Several transfer evaluations use random row CV; IEMOCAP is present in pretraining. The paper is not evidence for every emotion2vec+ checkpoint |
| DEFHS-KNOW-0051, Chen et al., Vesper | STRONG_EXTERNAL for frozen emotion specialization | pp. 6–8, 11–12: encoder fixed during downstream training, scalar layer weighting, last-versus-weighted comparisons; final-layer sufficiency is architecture/regime-dependent | English-focused pretraining, different metrics/protocols; no target adaptation comparison. Its downstream word “fine-tuning” does not mean encoder updates |
| DEFHS-KNOW-0052, pinned Vesper implementation | MECHANISTIC / implementation verification | `models/vesper.py`, `VesperFinetuneWrapper`: `freeze_upstream`, `torch.no_grad`, softmax scalar weights, masked temporal mean, linear projector/classifier; `modules/multihead_attention.py`: separate Q/K/V/output projections | Code structure and Apache-2.0 repository license do not establish checkpoint-weight permission |
| DEFHS-KNOW-0055, Han et al., acquired arXiv v2 | TRANSFERABLE_EXTERNAL | pp. 1–4, especially Table I: PEFT effects vary by language/setting; plain LoRA helps some transfers and hurts some monolingual/transfer configurations; middle-layer frozen features can outperform final layers | Approximately 1,600 training utterances per corpus in its balanced setup, non-Hindi languages, UA rather than macro-F1. No evidence this exact small-N upper-quarter recipe wins |
| DEFHS-KNOW-0058, Ma et al., acquired arXiv v3 | MECHANISTIC for location; TRANSFERABLE_EXTERNAL for its SER comparison | pp. 2–4: frozen-encoder comparison and concentration of adaptation effects in later Whisper layers; rank 8/32/64 visualization is not a controlled DEFHS rank-selection result | Whisper/IEMOCAP, not the selected DEFHS parent. t-SNE separation and late-layer activity do not prove causation or the best block/rank choice |
| DEFHS-KNOW-0081, Uniyal and Abrol | TRANSFERABLE_EXTERNAL | pp. 2–4, Tables 3–4: full tuning often fails; strongest partial-tuning result changes layer fusion/pooling and loss as well as encoder trainability | Much larger, imbalanced MSP-Podcast regime; extensive dev selection; the strongest result does not isolate encoder tuning. Its ensemble failure concerns its own architecture, not every probability blend |
| DEFHS-KNOW-0054, Leygue et al. | TRANSFERABLE_EXTERNAL; MECHANISTIC pooling observations | pp. 2–4: attentive pooling can help and greater attention complexity can hurt; masking/padding matters | Audio/text model with gradual unfreezing and weighted focal loss, tens of thousands of clips. Neither its absolute gain nor attention localization proves a frozen Hindi pooling effect |

Two exact metadata qualifications were recovered from the PDFs: 0055's acquired
`2409.16920v2` is titled *Cross-Lingual Speech Emotion Recognition: Humans vs.
Self-Supervised Models* (30 April 2025), rather than the older catalog title.
0058's acquired `2509.08454v3` is dated 22 January 2026, despite the catalog's
2025 year. Claims here refer to these inspected bytes; the acquisition authorities
were not edited.

### Independent binary readback

All seven materialized binaries matched the existing manifest, and the ZIP
passed archive integrity inspection. No weights were acquired or executed.

| Source | Drive object ID | SHA256 |
|---|---|---|
| 0006 | `12yW0FlwHxQRLh4Ew3M6fSbOvETKPc0A_` | `5e6f3ad6a10b71b08150ee1ba2a6f6473e23b223263f59afa84794c43aadecac` |
| 0051 | `1pC3Qq4L7U36eGBLIvp-FIKvUBEDZMp49` | `a53f8137120497b617f3b8b7468992c2281b64937d2921a018826eda4952f7b2` |
| 0052 | `115TBwlO9V3QBtDP82RtJ0bgj8r-sgE2g` | `7876dbac7140b821fb2983ceb50f9c6fd00c50a9307ec8e6b09de63e5760eb84` |
| 0054 | `1TYjrJVPVCCdBGBFwgkJYdPpQ2JlWiLnO` | `18b2185d7c113598123d51403ea5f3cf8c7a67fa5ea3769f81b1b3e0e5f067c0` |
| 0055 | `1Sz8vE-mYFbl6H7gKa-IhWwMHqPrdkxp_` | `6d4370422faebb3ae9e0ac40f1aafa64fc1c22633df2fcac8ba44b8b6ef7679d` |
| 0058 | `110IxryHCM6M8d2avsBajxPHV0XuwJXuK` | `63deb0002590e2d414d6d8f819bc0698be4d17a472640b96f70f1073105b0b13` |
| 0081 | `1HnAau97t1dsxn_ekRUJ1113FyFVI75ME` | `383a08db89670ea96967bd53be1398d8632d4bddfd858855c741400ad047bb7f` |

Vesper repository commit: `2b62af3e15fbd526fac6d4f1d6fea279c306244d`.
Canonical URLs remain in the inspected knowledge manifest/provenance.

**UNKNOWN.** There is no inspected DEFHS foundation-model OOF, no identified
PEFT winner, and no established emotion2vec/Vesper/WavLM checkpoint execution
permission beyond the existing Stage-0 records. XLS-R's documented Apache-2.0
checkpoint terms still require an immutable full Hub revision. Scientific
reasoning about a family does not clear any blocked asset.

## 3. EX-ANTE PRIOR

**FROZEN_DIVERSITY_PRIOR — INFERENCE supported by the evidence above.**

The effective independent sample size is at most 826 and smaller for dependent
clips. A V-B training fold has roughly four fifths of those labels. Four nearly
balanced classes do not justify loss/sampling machinery for rare classes. Short
speech limits observation time for affect and makes stable estimates of subtle
class boundaries difficult. The observed allocation/fold sensitivity makes
selective small score improvements particularly vulnerable to selection.

Strong pretrained emotion/SSL features can reduce task bias without estimating
new encoder parameters from these labels. Diverse frozen encoders and the
acoustic anchor offer an inexpensive, directly testable route to complementary
errors. Cached features separate representation comparisons from expensive
encoder training.

Adaptation can nevertheless reduce a target-specific bias: a representation
trained for another language/objective may retain useful cues but organize them
poorly for these four labels. The same moderate shift makes adapting to local
recording or prompt structure dangerous. Parameter efficiency does not imply
statistical safety or preservation of error diversity. The prior therefore
controls the burden of evidence; it does not predict that PEFT loses.

## 4. CAUSAL / MECHANISTIC FAILURE TAXONOMY

The mapping below is **INFERENCE**. An observation updates a hypothesis; it does
not identify a cause on its own.

| Failure hypothesis | Evidence supporting it | Intervention/decision |
|---|---|---|
| Representation-limited relative to the tested family | Stable cross-family class-pair ranking deficit; another frozen neural representation discriminates persistent parent/system mistakes after downstream controls | One bounded encoder experiment may be justified if all entry conditions pass |
| Pooling-limited | One simple attentive-statistics module robustly repairs the target confusion or adds system value with encoder frozen | Prefer/promote that result; reassess only the final frozen state once |
| Layer access or head-limited | Scalar layer mixture or RBF head repairs the failure compared with final layer/logistic | Access existing information; this is evidence against immediate encoder adaptation |
| Decision-limited | Shrunk class-logit offsets improve held-out macro-F1; class-pair rankings remain informative | Keep encoder frozen; complete decision calibration after membership lock |
| Ensemble-diversity-limited | Different encoders rescue mistakes through actual held-out probability blends and ablations | Prefer the small frozen system; oracle union alone is insufficient |
| Dependency/source-limited | Effects disappear on clean rows, after deleting a dominant dependency block/format/Q stratum, or in V-A non-retrieval evidence | Do not adapt to the apparent opportunity |
| Likely overlapping/noisy or unidentified | Persistent common errors, similar class margins, no independent discrimination witness, mixed-label duplicate evidence | No PEFT under this policy. Do not declare Bayes error or relabel data |

High-confidence wrong predictions can reflect geometry, source fitting or label
error. Low-confidence predictions can reflect geometry or affective overlap.
Neither confidence pattern triggers this policy by itself. A visualization of
clusters is not a required diagnostic and cannot override numerical evidence.

## 5. MINIMAL REPRESENTATION-LIMITED DIAGNOSTIC

### 5.1 Input and evaluation contract

Use only the completed Layer-3 frozen screen: aligned V-B/V-A predictions,
registered heads/layer mixtures/pooling, fixed metadata and ordinary ensemble
outputs. Class order is `angry, happy, neutral, sad`; hard predictions use
argmax with ties resolved by that order. Scores are aggregate four-class
macro-F1, not the unweighted mean of fold F1. Per-fold scores are stability
checks. Do not substitute public/private scores or protected folds.

Define `E` as the final frozen 2–3-lane ensemble after the allowed Stage-6
pooling decision, before final class offsets; `E0` is its pre-Stage-6 incumbent.
`E_minus_P` reruns the same permitted blending procedure without parent `P`.
Freeze the blend candidate grid/rule before examining its OOF scores. If no
exact grid/rule was previously committed, use this deterministic default:

- Evaluate the equal-weight blend first. The other candidates are nonnegative
  weights in multiples of 1/4, summing to one, including zero weights. Include
  the exact equal-weight vector even when three members make it off-grid.
- In each held-out V-B meta-fold, find the highest training-meta macro-F1
  candidate on the other four folds; ties prefer fewer nonzero weights, then
  smaller squared distance from equal weights, then lexicographic weights in
  immutable lane-ID order. Use that candidate only if its training-meta gain
  over equal weights exceeds one paired bootstrap SD of that gain; otherwise
  use equal weights. Compute the SD with Section 5.2 draws restricted to those
  four folds. Score the held-out fold only after selecting its weights.
- Apply this identical rule within the existing V-A folds for the secondary
  diagnostic, using their own four other folds' OOF. V-A never selects the grid,
  final membership or final V-B weights. Rerun the same selector for every
  replacement/addition/ablation comparator. No unrestricted stacker.

This meta-validation excludes held-out labels from the *weight/offset choice*.
Ordinary OOF models for other folds can have trained on those labels, so it is
not a fully independent nested estimate of the entire selected system. Reusing
these folds remains a limitation; neither a bootstrap nor this policy removes
prior adaptive selection bias. This policy does not add another primary split
or claim to replace eventual protected confirmation.

### 5.2 Fixed uncertainty and stability operators

Use a paired, dependency-aware multiplier bootstrap, computed from actual OOF:

1. Start with frozen duplicate-family components, with individual clips as
   singleton components. Union components linked by the already frozen 0.90
   prompt-cluster membership. Do not infer new speaker groups or tune a threshold.
2. For each of 2,000 replicates, draw one `Exp(1)` weight per component with
   NumPy `PCG64(20260930)`, in lexicographic component order. Apply the same
   component weight to every member, candidate and view. Keep existing fold IDs.
   Recording/Q groups are sensitivity strata, not bootstrap components.
3. Recompute weighted confusion counts/F1 and paired differences. For class-pair
   AUC, use the same row weights and half-credit for tied ranks. Both classes
   must exist in the evaluation subset; otherwise the claim is UNKNOWN.
4. Before examining the estimates, enumerate the fixed contrast family `J` for
   that decision phase. Let `d_j` be a point contrast and `s_j` the bootstrap SD
   (`ddof=1`). Compute the 0.95 quantile (`method='higher'`) of
   `max_j abs((d_j_star - d_j)/s_j)` and call it `q`. Ignore truly constant
   contrasts in the maximum and give them the interval `[d_j,d_j]`.
   If every contrast is constant, set q=0. Otherwise set
   `L_j=d_j-q*s_j`, `U_j=d_j+q*s_j`.
5. `sigma_E` is the bootstrap SD of aggregate F1(E), with the same draws.

These are **conditional credibility intervals**, not calibrated probabilities
that a selected candidate will win a hidden leaderboard. The simultaneous
contrast family reduces within-phase shopping; it does not solve model-training
or historical selection uncertainty. Alpha 0.05, 2,000 draws and four-of-five
fold consistency are precommitted decision conventions, not asserted biological
constants or DEFHS effect sizes.

At pre-pooling parent selection enumerate `J_SELECT` only over then-completed,
legally screened lanes: standalone acoustic-reference, same-encoder/best-lane
contrasts, E0 parent ablations and the corresponding V-A compatibility contrasts.
Use these simultaneous intervals for that selection; future pooling results
cannot change its identity. Then enumerate `J_ENTRY` over the closed frozen
registry:
their standalone reference and parent-selection contrasts; every within-parent
head/layer/pooling contrast and its system replacement; parent ablations in
E0/E; the two offset-control contrasts;
all six unordered class-pair AUC witness-minus-parent contrasts in full/clean
V-B and non-retrieval V-A; and each corresponding witnessed residual-oracle
headroom contrast. Enumerate `J_POST` over all Section-9 parent/system, four-class,
target-pair and loss contrasts for both seeds and their mean, including both
system configurations and both-member ablations. Include subgroup contrasts
used for a harm veto. No adding a favorable contrast after seeing results.

For F1 comparisons define:

```text
ROBUST_GAIN(X,Y):
    aggregate F1(X)-F1(Y) > 0 AND simultaneous L(X-Y) > 0
    AND at least 4 of the 5 individual fold differences > 0
    AND aggregate difference after removing any one fold > 0

CONTRADICTION(X,Y): simultaneous U(X-Y) < 0
```

For a seed-average ROBUST_GAIN claim also require each seed's aggregate difference
positive, at least four positive fold differences per seed, and no deletion-of-
one-fold reversal per seed. Do not average away a bad seed. Correlated CV folds
are not five independent trials, and no independent-fold significance test is
claimed. If a required value/mask/claim is missing or undefined, return UNKNOWN
and fail the trigger; do not turn UNKNOWN into PASS.

### 5.3 Select one parent before selecting a residual

Eligible parents must be already screened frozen neural lanes in `E`, have a
serialized differentiable four-class classifier, and have complete Stage-0
authority. A logistic/small neural-head realization qualifies only if it is not
credibly inferior to that encoder's selected RBF/head realization (`U(P-best
same-encoder variant) >= 0`). Do not swap an RBF winner for a new differentiable
head merely to make LoRA possible. If no such parent exists, no adaptation.

Parent credibility is `ROBUST_GAIN(P,FULL_RBF_SVM)` OR
`ROBUST_GAIN(E,E_minus_P)`. It must additionally have no V-A non-retrieval
CONTRADICTION against the corresponding acoustic reference or its own system
ablation, respectively. V-A retrieval-covered predictions cannot establish it.

At Stage-6 entry apply this selection with E0 in place of E, before inspecting
residuals or training its pooling control. Of credible eligible parents, form
the set whose aggregate V-B standalone
score is not credibly below the best eligible standalone lane. Prefer an
emotion-specialized parent in that set; otherwise use a general SSL parent.
Within that type, maximize the minimum deletion-of-one-fold marginal system
gain, then minimize the prospective LoRA parameter count, then use
lexicographic immutable checkpoint ID. Freeze this one encoder/checkpoint
identity. Complete its one Stage-6 pooling comparison, decide its final frozen
realization P, and finalize E using the existing frozen promotion rules. Recheck
P's eligibility/credibility against final E and the same-encoder controls. If P
is no longer eligible, credible, or a member of E, close adaptation; do not
select another encoder. A stronger RBF realization cannot be replaced with a
weaker new differentiable head to preserve entry. The final P and E are fixed
before residual selection. This tie policy expresses the ex-ante prior without
assuming a family wins.

For G3, the remaining downstream contrasts are exactly V-minus-P and
E-with-P-replaced-by-V minus E for each completed registered realization V of
this encoder, plus offset(P)-P and offset(E)-E. Comparisons between two obsolete
variants cannot establish unexplored headroom over the selected final state.

### 5.4 Required residual evidence

`CLEAN` means training clips that belong to neither a non-singleton frozen
duplicate family nor a non-singleton frozen 0.90 prompt cluster. Remove known
label-conflict duplicate families from this *diagnostic* mask. This changes no
training labels or validation membership. Non-retrieval V-A additionally removes
rows covered by the existing fold-safe retrieval audit. Preserve all training
rows for ordinary fitting.

For each unordered pair `{a,b}` and already screened frozen **neural** witness
`W` from a different representation family:

Use the predeclared family IDs emotion2vec, Vesper, WavLM and XLS-R; sizes,
heads and layer/pooling variants within one family are not new witnesses.
Different families are not independent pretraining corpora: Vesper's WavLM
distillation, for example, leaves shared lineage. The witness requires different
frozen discriminative information, not statistical independence of two studies.

- Class-pair score is `log p(a) - log p(b)`, using supplied logits where possible
  only when their differences equal the recorded final log-probability
  differences; otherwise use the probabilities, clipped to `1e-12` for numerical
  logs. Let a precede
  b in the fixed class order and encode a as the positive AUC class.
- Compare pair AUC(W) minus AUC(P) on all clean rows with true label in the pair.
  A constant class-logit offset cannot change this ranking. This measures
  relative score geometry; it is not a direct embedding/Bayes-error estimate.
- `S(a,b,W)` consists of CLEAN rows where both P and E predict the wrong member
  of this pair, W predicts the true class, and every registered completed
  head/layer/pooling realization of P also remains wrong on the row.
- Define `E_oracle_S`: E's hard labels with only S corrected using observed
  labels. It is a diagnostic ceiling, never a deployable model or expected
  adaptation gain. Other errors are unchanged.

A pair/witness is actionable only if **all** are true:

1. Pair-AUC witness advantage has simultaneous `L > 0` on full and CLEAN V-B;
   its point difference is positive in at least four folds with both classes
   present and remains positive after every one-fold deletion. Fewer than four
   evaluable folds fails the criterion.
2. S contains independent dependency components in at least four V-B folds.
   Its oracle macro-F1 gain is positive after every one-fold deletion and has
   `L(oracle gain) > sigma_E`. This requires a ceiling above an observed
   uncertainty scale; it does not assume any fraction of it is learnable by PEFT.
3. After deleting the dependency component contributing the most S corrections
   (lexicographic ID for ties), S headroom remains positive. No single block
   supplies the whole opportunity.
4. For each V-D format or Q128/Q960 stratum whose deletion leaves both pair
   classes and four-class F1 evaluable, the pair-AUC witness advantage and S
   headroom remain point-positive. Report unevaluable deletions as UNKNOWN;
   they do not prove robustness. Also require no credible sign reversal in any
   evaluable stratum. A uniformly absent clean opportunity fails.
5. In non-retrieval V-A the same pair-AUC advantage is point-positive, has no
   credible reversal, and the analogous witnessed S headroom is positive.
   Missing coverage or zero witnessed headroom fails; retrieval success cannot
   compensate. V-A is secondary compatibility, not an independent replication.

If several qualify, choose the largest simultaneous lower bound of S oracle
headroom, then largest lower bound of pair-AUC advantage, then class order and
checkpoint ID. Store this pair/witness/S definition before adaptation. No happy
preference, listening-based discretionary relabeling or post-hoc cluster selection.

This is the smallest decisive set: matched downstream controls, relative
class-pair ranking with a discrimination witness, stable unresolved ensemble
errors, and dependency/V-A compatibility. Raw correlations and margins are
reported for interpretation but are not additional triggers.

## 6. PEFT_ENTRY_GATE

The complete frozen package must exist before evaluating this gate. A partial
screen gives `PENDING_FROZEN_OOF`; no adaptation is launched. On the completed
package, every missing required result makes adaptation NOT JUSTIFIED.

| Required condition | Executable test | Scientific reason |
|---|---|---|
| G0. Authority and provenance | P passes Stage 0; exact prediction/fold/preprocessing hashes and implementation mapping exist | Prevents an unauthorized or unrepeatable intervention |
| G1. Credible parent | Section 5.3 selection produces P | Adapt a proven lane, rather than rescue an abandoned family |
| G2. Downstream closure | Registered logistic/RBF, final/scalar mixture where supported, and one simple attentive-pooling comparison for P are completed; selected frozen P/E reflect their decisions | Excludes the obvious cheaper access/aggregation fixes |
| G3. Downstream plateau | None of the exact Section-5.3 remaining contrasts has ROBUST_GAIN; their maximum simultaneous upper bound is `<= sigma_E` | Null results alone are insufficient; unresolved downstream headroom must be bounded relative to actual OOF uncertainty |
| G4. Actionable residual | At least one pair/witness satisfies all five Section-5.4 conditions | Requires evidence beyond common errors or happy weakness |
| G5. Ensemble closure | All already scheduled frozen lanes/ablations are decided; no unpromoted frozen addition has ROBUST_GAIN; S is still wrong in the resulting E | Diversity must have had its cheaper opportunity first |
| G6. Bounded intervention feasible | Differentiable fixed parent head, exact Q/V adapter mapping, zero-adapter parity and within-budget timing feasibility can be established without changing the scientific recipe | Prevents silently testing a different head/model or an unbounded experiment |

For an unsupported scalar mixture, record architectural/API unavailability at
scaffold time, before scores; do not fabricate that comparison or omit a
supported comparison after seeing a disappointing result. An unperformed,
supported comparison is incomplete evidence and fails G2. Stage-6 pooling is
mandatory only for the one selected prospective parent if PEFT is still under
consideration; there is no requirement to upgrade every encoder.

G6's future zero-adapter parity/timing check is engineering preparation inside
the one allowed experiment, not a new scientific diagnostic. Training begins
only after G0–G5 pass. Failure of G6 closes adaptation technically; it does not
imply the representation hypothesis is scientifically disproved.

The conjunction triggers **one testable upper-representation hypothesis**.
It cannot establish that attention Q/V rather than feed-forward/front-end
processing is the true cause. That irreducible uncertainty is precisely what
the bounded experiment tests.

## 7. NO_PEFT_GATE

On a completed screen, lock the frozen architecture with respect to adaptation
if any entry condition fails. Record the first failing reason, plus all other
available failures, using these statuses:

| Status | Condition |
|---|---|
| `INSUFFICIENT_EVIDENCE` | Completed package lacks required aligned predictions, valid probabilities/logits, folds or metadata |
| `FORBIDDEN_EXECUTION` | Selected checkpoint/code/competition permission or immutable revision unresolved |
| `NO_CREDIBLE_PARENT` | No eligible parent under Section 5.3, unstable value, or V-A credibility contradiction |
| `DOWNSTREAM_NOT_CLOSED` | Required supported head/layer/pooling comparison absent |
| `DOWNSTREAM_FIX_OR_UNCERTAINTY` | A simpler robust fix exists, or its upper headroom bound exceeds sigma_E |
| `RESIDUAL_NOT_IDENTIFIED` | No qualifying witness; shared errors/low margins alone; label overlap remains unidentified |
| `DEPENDENCY_OR_VA_CONTRADICTION` | Witnessed opportunity fails clean/deletion/secondary compatibility conditions |
| `FROZEN_DIVERSITY_SUFFICIENT` | Permitted frozen blends resolve S or an unpromoted frozen member still has robust marginal gain |
| `RECIPE_NOT_REPRODUCIBLE_OR_BOUNDED` | Exact fixed-head Q/V recipe cannot be implemented within budget |

“Lock” means do not run encoder adaptation under this mission; the remaining
already-authorized frozen-system calibration/finalist stages can still finish.
It does not prematurely lock an empirical winner before its OOF exists.
Complete scheduled inexpensive frozen decisions without asking for a new
adaptation rationale. Do not reopen PEFT merely because the final frozen score
is disappointing. If Stage 0 blocks an entire intended architecture, follow
Layer 1's return-to-SS rule; no silent model substitution is authorized here.

## 8. EXACT_SINGLE_PEFT_RECIPE_IF_TRIGGERED

Recipe ID: `DEFHS_UPPER_QUARTER_QV_LORA_FIXED_DOWNSTREAM_V1`.
All numerical defaults below are **INFERENCE / precommitted engineering
choices**, informed by the acquired SER/LoRA evidence, not DEFHS optima.

| Item | Exact commitment |
|---|---|
| Parent type | The single P chosen by Section 5.3: emotion-specialized if credible within the selected set, otherwise general SSL; no family assumed to win |
| Method | LoRA only; no selective full-block unfreezing, bottleneck adapters or gates |
| Adapted blocks | If actual encoder depth is D, adapt only the final `max(1, ceil(D/4))` transformer blocks, indexed `D-ceil(D/4)` through `D-1` for D>=1 |
| Adapted matrices | Self-attention query and value linear weights only; additive `(alpha/r) B A`; no key/output/FFN/bias/norm updates. Fused QKV requires an exact Q/V-only row mapping with K untouched; if unavailable, fail technically |
| Rank/scaling | `r=8`, `alpha=8`, scaling 1; no sweep. Rank 8 is studied in 0058 but is not its claimed optimum; here it is a conservative capacity budget |
| Frozen encoder components | Feature frontend, projections, positional/relative-position parameters, all original encoder weights including upper-block weights, every norm and bias, lower blocks |
| Layer mixture | Fixed at the matching frozen parent checkpoint's learned scalar weights, or its already selected final-layer rule |
| Pooling | Same selected masked mean+std or attentive-statistics operation and parameters, frozen; no topology change |
| Classifier | Exact serialized differentiable P classifier, including any fixed standardization/projection/calibration, frozen. Do not replace an RBF head with a new MLP |
| Initialization | Copy the fold-specific P. For each adapted block in ascending order, query then value, A has shape `(r,input_dim)` and uses `kaiming_uniform_(a=sqrt(5), mode='fan_in', nonlinearity='leaky_relu')`; B has shape `(output_dim,r)` and is zero. Initial eval logits must reproduce the recorded P logits with `atol=1e-6, rtol=1e-5` in the same FP32 path; a precision change cannot supply the measured gain |
| Loss | Ordinary unweighted four-class cross-entropy on training labels only. No focal loss, class weights, class-specific oversampling or external labels |
| Augmentation | None. No waveform/spec masks, gain/noise/pitch/time changes or rescue augmentation |
| Optimizer | AdamW on A/B only, LR `1e-4`, betas `(0.9,0.999)`, epsilon `1e-8`, weight decay `0.01`, gradient norm clipping `1.0` |
| Schedule | Linear warmup over the first 5% of planned updates, then cosine decay to zero at epoch 30. Each pilot, refit and final fit uses its own training-set update count for the same 30-epoch horizon, even if stopping earlier; do not compress the schedule to the selected epoch count |
| Regularization | LoRA-input dropout `0.1`; pretrained encoder/head/pooling remain in eval behavior, with base dropout/LayerDrop disabled as in frozen inference. Only LoRA dropout is active in training |
| Batches | Effective batch 16, shuffle with the optimization seed; microbatch may be reduced for memory with gradient accumulation preserving effective batch 16. Record its engineering choice before label-scored training |
| Seeds | Exactly `20260930` and `20260917` as optimization RNG seeds on the SAME frozen fold assignments; these do not create new validation allocations. Never use 20261001 |
| Lane output | Equal average of the two adapted probability outputs; also retain each seed separately. No seed selection or extra seed to rescue a result |
| Compute ceiling | At most 8 accelerator-hours total, summing device time for this adaptation stage, including engineering/cache work, pilot-parent prerequisites, pilots, V-B, V-A and the two final full-training fits if promoted. At most two GPUs concurrently, one fit per GPU; no larger accelerator campaign |

For square attention projections the added capacity is `4*K*d*r` parameters,
where K is adapted block count and d is hidden width. For example D=24,d=1024
gives 196,608 added parameters; D=4,d=1024 gives 32,768. This is a capacity
calculation, not proof of low variance. The upper-quarter restriction is an
ex-ante localization/budget choice; the acquired mechanistic work does not
validate that exact fraction for these parents.

### Fold-safe stopping and matched comparison

Use the existing fold IDs, without generating another partition. For each
outer V-B fold f (IDs normalized to 0–4), designate `g=(f+1) mod 5` as its
training-only stopping fold. Fit the selected frozen parent downstream recipe
on the other three folds, with no access to f or g labels in fitting. It must
use the same inherited training-only fitting rules. Add zero-initialized LoRA
and train on those three folds, monitoring CE on g only. Include epoch 0;
stop after five consecutive epochs without a strictly lower CE, or epoch 30.
Select the earliest epoch attaining the minimum g CE. If it is zero, retain zero.

Then discard the pilot, copy the *exact frozen outer-fold P* trained on the
four outer-training folds, reinitialize LoRA with the same seed, and train
for the pilot's selected number of epochs on those four folds. Only then score
outer f. P is unchanged and is the matched comparator. No outer-fold scores
select the epoch, seed, LR, layer subset or parent. V-A uses its own existing
fold IDs with the identical cyclic stopping construction. V-A does not select
a recipe. The existing duplicate-leakage properties of V-A remain secondary.

This entails at most 40 LoRA fits: pilot+refit for five folds, two seeds, two
views. A pilot parent downstream refit is a matched training-only prerequisite,
not another architecture search. Frozen lower activations may be cached if
preprocessing, masks and layer states remain exactly equivalent. Preserve
gradients through upper blocks and the frozen differentiable head/pooling;
`torch.no_grad()` around those adapted computations would invalidate the test.

Before label-scored training, time an unlabeled shape/gradient engineering
check and require the planned workload plus two reserved final fits to fit
the 8-hour ceiling. Keep the same recipe if a service interruption requires
an identical checkpoint resume. Numerical bugs may be repaired to restore the
specified implementation; scientific failures cannot be relabeled as bugs.

If provisionally promoted, train two all-826 parent realizations by the same
frozen fitting rule and adapt for each seed's median selected V-B pilot epoch
count (rounded down). All-826 fitting is part of subsequent authorized final
implementation, not this policy mission. No protected result sets that duration.

## 9. ADAPTED_MODEL_PROMOTION_RULE

All outcomes here are ordinary development recommendations for SS. Final
protected confirmation and submission remain Stage 9 / SS authority.

Let A be the fixed two-seed average; retain A1 and A2. Keep frozen E and P
unchanged as comparators. Define only these candidate systems:

- `ER`: E with P replaced by A, same permitted blending/meta-validation rule.
- `EB`: E plus A, only if this yields at most three lanes. If E already has
  three lanes, EB is disallowed; do not drop an unrelated member to create space.
- For EB, rerun each of `EB_minus_A` and `EB_minus_P` under the same rule.

Use J_POST simultaneous contrasts, including each seed substituted separately
into each allowed system. Membership and weights are evaluated under the same
five-fold meta-validation, with no unrestricted refitting of a stacker. When
both operands contain A, substitute the same seed in both operands, then rerun
their selectors; do not compare a selected seed against the other seed/mean.

First require `PARENT_PASS`:

1. `ROBUST_GAIN(A,P)` on V-B; A1/A2 each satisfy the seed conditions in 5.2.
2. The selected pair's AUC improves over P on CLEAN V-B with `L > 0`, positive
   point changes in four evaluable folds, and no deletion-of-one-fold reversal.
   The predeclared pair confusion decreases in at least four folds; use the
   total a-to-b plus b-to-a count per pair-support, not cherry-picked direction.
3. No class has a simultaneous `U(F1_A_class-F1_P_class) < 0`; apply identically
   to all four classes, including happy, and to each seed as well as the mean.
   Report all point declines regardless.
4. No V-A non-retrieval macro-F1 or target-pair AUC credible reversal. V-A
   non-retrieval aggregate macro-F1 difference must be nonnegative for A and
   each seed; unchanged retrieval-covered rows cannot hide a decline.
5. No overfit/source contradiction: if training CE drops but outer validation
   CE increases with simultaneous `L(CE_A-CE_P)>0`, reject as a probability/
   overfit contradiction. Compute both training and validation CE in eval mode,
   with LoRA dropout off; check the mean and both seeds. Also reject if positive
   system gain disappears on
   CLEAN rows, after any one-fold deletion, after deletion of the largest
   corrective dependency component, or reverses credibly in a supported
   V-D/Q diagnostic stratum. Tiny strata that cannot support a contrast remain
   uncertain, not proof of either harm or safety.

For each X-minus-Y gain's largest corrective dependency component, count rows
where Y is wrong and X is correct, choose the largest count with lexicographic
component-ID ties, delete that entire component and recompute macro-F1 gain.
Require a positive remaining point gain. Supported V-D/Q harm contrasts are
exactly those with all four true classes present; list all others as unevaluable.

The class harm test is a veto for observed credible harm, not proof that all
classes are non-inferior. The CE veto is a deliberately conservative secondary
check for an overconfident probability-blend component; macro-F1 remains the
primary objective. Both are INFERENCE, not facts dictated by the literature.

For a system S define `SYSTEM_PASS(S)`:

- ROBUST_GAIN(S,E) on V-B, with each seed substitution's aggregate/fold/deletion
  conditions passing as well;
- positive CLEAN V-B aggregate gain and no credible CLEAN reversal;
- V-A non-retrieval aggregate gain nonnegative for the mean and both seeds,
  with no credible macro-F1 or per-class reversal;
- no credible V-B per-class collapse, and the same dependency/source checks
  as above. Report the fixed-retrieval pipeline separately.

Apply CLEAN, class-harm and dependency/source checks to both seed substitutions
as well as the mean. Unevaluable tiny diagnostic strata remain reported
uncertainties; required full/CLEAN/V-A quantities cannot be missing.

Return exactly one outcome:

| Outcome | Rule |
|---|---|
| A. `REPLACE_PARENT` | PARENT_PASS and SYSTEM_PASS(ER), unless the stronger keep-both rule below passes |
| B. `KEEP_BOTH` | PARENT_PASS; EB allowed; SYSTEM_PASS(EB); ROBUST_GAIN(EB,ER), ROBUST_GAIN(EB,EB_minus_A), and ROBUST_GAIN(EB,EB_minus_P); both ablation gains positive on CLEAN rows and in non-retrieval V-A |
| C. `KEEP_FROZEN_ONLY` | PARENT_PASS fails or neither allowed adapted system passes; this closes adaptation scientifically under the one-test policy |
| D. `ABANDON_ADAPTATION_TECHNICAL` | Authority, parity, reproducibility, finite outputs or compute completion fails before a valid comparison; retain E, distinguish this from hypothesis falsification |

Keep-both is deliberately much harder than replacement. Error/probability
correlations and correction/breakage counts must be reported, but no arbitrary
correlation threshold determines membership. Nearly identical errors normally
fail the two-way marginal/ablation conditions. If they nevertheless pass all
held-out conditions, measured system value takes precedence over correlation.

A standalone improvement with zero/negative system marginal value produces
KEEP_FROZEN_ONLY. The adaptation is not promoted merely to display a stronger
single model. Conversely this first, high-risk intervention is held to the
stricter requirement of a robust parent improvement as well as system value;
it is not admitted as a weak speculative diversity lane.

## 10. ADAPTED_MODEL_KILL_RULE

Scientific kill: a completed valid two-seed experiment returns KEEP_FROZEN_ONLY
for any failure of parent, mechanism or system promotion conditions. Examples:

- positive aggregate mean but a seed/fold reversal, or one-fold-driven gain;
- happy gain accompanied by a credible other-class decline;
- V-B improvement with a V-A non-retrieval contradiction;
- no improvement in the registered class-pair geometry/confusion;
- lower training loss but credibly higher held-out CE;
- gains confined to dependent clips, one source stratum or repeated prompts;
- improved standalone F1 but absent/negative ensemble marginal value;
- no meaningful difference from P relative to the paired OOF uncertainty;
- reduced measured finalist robustness.

Technical kill: invalid comparator, unresolved asset permission, failed parity,
NaN/Inf, missing folds/seeds/views, or the compute ceiling. Do not promote a
partial run. Technical failure does not establish that PEFT is ineffective.

After either kill, there is no second parent, rank, layer-count, LR, loss,
augmentation, adapter family or full-tuning attempt under this assignment.
An unfavorable result is recorded and allowed to terminate the hypothesis.

## 11. HAPPY_CLASS_INTERPRETATION_RULE

The baseline happy weakness is **DIRECT_DEFHS**; its cause and persistence in
foundation features are **UNKNOWN**. Happy gets exactly the same six-pair scan,
simultaneous intervals, clean/fold checks, class harm veto and ensemble rule as
other classes. There is no happy weighting, special threshold or preferred
adaptation pair.

Belief shifts toward relative representation geometry if a happy-related pair
has a stable ranking deficit against an independent frozen witness, survives
head/layer/pooling and offset controls, and supplies unresolved clean system
errors under Section 5.4. A higher happy recall alone is insufficient; require
the false-positive/false-negative changes and all other class F1 values.

Belief shifts toward decision/pooling failure when the cheaper controls fix it.
It shifts toward overlap/noise or unidentified cause when high-quality encoders
share the same ambiguous margins without a discrimination witness, or toward
dependence when it disappears on clean/deletion views. Neither human listening
nor model disagreement establishes annotation truth. Do not relabel or delete
training rows. Mechanistic happy observations in 0058 are not a DEFHS rank or
PEFT trigger.

## 12. ENSEMBLE_VALUE_RULE

For any frozen X/Y, rank prospective system membership by actual held-out
marginal F1 and ablation, with fold/clean/V-A consistency, then choose the
smaller system. A weaker standalone Y can beat a stronger X as a system member
if the permitted blend's measured marginal value is stronger. Pairwise
correlation/disagreement/oracle union explains that result; it does not replace it.

For adapted X, rerun replacement and (if capacity allows) addition rather than
assuming its stronger standalone score is better. If adaptation destroys errors
that made frozen X complementary and its system gain fails, retain frozen X.
Do not keep both as insurance without the Section-9 two-way ablation test.

Equal weights remain the first blend. Any nonnegative coarse weighting is
selected on four V-B meta-folds and evaluated on the fifth, with the same
search space for every comparator. Final weights may be fit on all V-B OOF
only after development membership is decided. No offsets are optimized jointly
with membership to rescue adaptation. Final class-offset evaluation stays after
membership lock.

## 13. FAIL_SAFE_AND_STOP_RULE

The default at every ambiguity is the best justified frozen system E. On a
complete frozen package, a failed entry gate terminates adaptation. On a valid
adaptation result, failure of the promotion conjunction terminates adaptation.
No repeated gate reinterpretation or extra model shopping is allowed.

Future workers must store the policy version/input authority, candidate registry,
fold and metadata hashes, selected P/E/pair/witness, every gate value/interval,
first-failure status, and the fixed recipe before launching adaptation. These
are ordinary Layer-3 reporting outputs, not additional RS2 repository files.
If the gate is incomplete because scheduled frozen work is still running,
return PENDING_FROZEN_OOF and complete that work; do not launch adaptation.

Any proposed change to this policy after foundation OOF has been observed must
be reported to SS as a new adaptive decision. It cannot be called precommitted.
The current mission neither authorizes that change nor protected confirmation.

## 14. PRECOMMITTABLE_NOW_VS_EMPIRICAL_LATER

| PRECOMMITTABLE NOW — INFERENCE | MUST WAIT FOR FROZEN OOF / EXECUTION — UNKNOWN |
|---|---|
| Frozen-diversity prior and burden of evidence | Which encoder/head/pooling wins |
| Input schema, conditional uncertainty/stability rules and deterministic tie-breaking | Actual uncertainty widths and fold/seed stability |
| Matched downstream closure, offset-control family and witness criteria | Whether happy remains weakest or any pair qualifies |
| One LoRA family, upper-quarter Q/V subset and rank/budget | Whether the attention intervention addresses the cause |
| Fixed downstream components, loss/optimizer/seeds/stopping | Whether exact assets clear future Stage 0 and fit memory/time |
| Parent/system promotion and terminal kill conditions | Whether E2V/Vesper/generic/acoustic lanes complement each other |
| No repeated PEFT rescue and no protected/public-LB selection | Whether the entry gate triggers or adaptation adds system value |

The policy does not precommit an empirical winner or final hidden-test score.
Passing the gate buys one experiment; passing ordinary development promotion
still leaves transfer and selection uncertainty.

## 15. OPTIONAL_DIAGNOSTIC

**ONE REQUIRED CHEAP CPU DIAGNOSTIC FAMILY:** shrunk class-logit offsets before
the PEFT gate, applied to P and E. This is the only added diagnostic; class-pair,
oracle, clean and sensitivity summaries above are deterministic analyses of the
already scheduled predictions/confusion/dependency outputs, with no new model.

For each held-out V-B meta-fold f:

1. Work only with the four other folds' OOF scores/labels when choosing offsets.
2. Enumerate the 19 zero-sum vectors with each component in
   `{-log(2),0,+log(2)}`. Zero is included. This is a bounded twofold odds-change
   screen, not an unrestricted threshold search.
3. Find the highest aggregate training-meta macro-F1 vector (lexicographic ties).
   Estimate bootstrap SD of its paired gain over zero using only those four
   folds' rows/components and the Section-5.2 draws restricted to them.
4. Among vectors within that one SD of the best training-meta F1, select minimum
   squared norm, then lexicographic vector. This strongly favors zero.
5. Apply that vector to held-out f; concatenate held-out predictions across f.

Use `log p + b` and ordinary argmax; no temperature/affine calibration campaign.
Assess the two resulting diagnostic gains with J_ENTRY. A ROBUST_GAIN for
either P or E blocks PEFT in favor of the cheaper decision route. If no gain
is credible but an upper improvement bound exceeds sigma_E, downstream closure
is inconclusive and PEFT is also blocked. A null bounded offset screen is not
proof that all conceivable decision rules fail; pair-AUC witness evidence is
still required.

These diagnostic offset predictions are not used as training targets, as a
classifier initializer, or to alter the LoRA comparator. Only the decision of
whether to adapt uses them. The ordinary Layer-1 Stage-8 final calibration
remains after final membership lock and uses this same bounded/shrunk rule.
No primary split, protected labels, new pretrained model or GPU diagnostic.

## 16. ADVERSARIAL_SELF_AUDIT

| Attack | Revision / remaining limitation |
|---|---|
| Repeated V-B use manufactures a PEFT story | Commit policy before OOF, use one completed registry/gate, simultaneous contrasts, fold deletions, clean and secondary checks; explicitly retain historical selection bias |
| Any disappointing frozen score can trigger adaptation | No absolute disappointment trigger; require parent credibility, a discrimination witness and unresolved system headroom above actual uncertainty |
| Head or pooling failure is mistaken for encoder failure | Complete matched logistic/RBF, final/mixture and one pooling control; add only the bounded offset diagnostic; uncertain closure blocks entry |
| V-A retrieval rewards source memorization | Use fold-safe non-retrieval/CLEAN V-A compatibility; retrieval stays fixed and separate |
| Happy was noticed early and gets special treatment | All class pairs and class harms treated symmetrically; deterministic pair selection and simultaneous family |
| Complementarity overfits 826 labels | Evaluate actual low-dimensional held-out blends, not correlation or oracle alone; two-way keep-both ablation; conditional limitations disclosed |
| External PEFT evidence is too distant | Classify external/mechanistic evidence explicitly; no translated score gain; exact upper-quarter/rank defaults called inference |
| One experiment hides many recipes | One parent/family/subset/rank/LR/loss, no augmentation, frozen downstream, two fixed seeds, training-only stopping, hard compute ceiling |
| Analyst narrative changes the decision | Machine gates, exact masks/ties/interval conventions and UNKNOWN-fails behavior replace qualitative votes |
| Shared errors prove irreducibility or label error | They prove neither. Without a witness the intervention remains unearned; no relabeling |
| A weak differentiable head is substituted for a strong RBF parent | Eligibility requires an existing credible differentiable realization; otherwise no adaptation |
| Freezing the head makes PEFT less flexible and could cause a false negative | Yes. This is an intentionally narrow attributable test. A failure rejects this bounded intervention; it does not prove every adaptation method would fail |
| Oracle headroom is advertised as achievable gain | It is explicitly only a ceiling. The gate never multiplies it by an assumed learnable fraction |
| Keeping only two seeds understates optimization variance | Yes; neither seed can be averaged away, but two seeds do not characterize every run or hidden domain |
| No detected per-class/source harm means proven safety | No; small strata/interval power remain limited and are reported UNKNOWN, not certified safe |

There is no observational guarantee of causal identification. The policy favors
false-negative adaptation decisions over speculative encoder fitting in this
small-N regime. That tradeoff is explicit and can be reviewed by SS before OOF.

## 17. EXACT_MINIMAL_EDITS_TO_LAYER3_LADDER

These are proposed edits for SS/Layer 3, not modifications to Layer-1 files.

1. **Stage 6:** if PEFT is still a live possibility, select the prospective
   encoder once from E0 by Section 5.3 before its pooling comparison; complete
   that encoder's one simple attentive-pooling comparison, recheck its final P
   without switching encoder, and finalize P/E and
   the registered downstream/ensemble decisions. Generate the already scheduled
   fold/class/margin/complementarity/dependency summaries needed in Section 5.
   Run the single bounded offset-control family in Section 15 before Stage 7.
   Record required unsupported comparisons before scores; incomplete supported
   comparisons cannot count as a plateau.
2. **Stage 7 entry:** replace qualitative “potential gain” language with G0–G6
   and the exact first-failure statuses. Select one P before residual selection.
   A failed complete gate closes encoder adaptation; no default GPU reservation.
3. **Stage 7 experiment:** replace the adaptation alternatives with the single
   Section-8 recipe. Tighten attribution: layer mixture, pooling and classifier
   fixed, only upper-quarter Q/V LoRA trainable. Remove the post-failure
   augmentation escape clause; exactly two fixed seeds and the compute ceiling.
4. **Stage 7 exit:** use the Section-9 replacement/addition/ablation and Section-10
   terminal kill rules. Preserve final 2–3-member system size.
5. **Decision-order dependency only:** the frozen-only offset diagnostic is a
   pre-PEFT control. Final Stage-8 calibration still follows membership lock.
   Existing V-A non-retrieval and source/prompt diagnostics must be available for
   entry/promotion rather than first inspected after PEFT; reuse the already
   scheduled outputs. Full finalist V-D/Q/correlated-allocation and eventual
   SS-authorized protected confirmation remain Stage 9.

Do not rewrite Stages 0–5, redesign retrieval/validation, add text/model lanes,
or update PROJECT_STATE as if SS had accepted this answer.

## 18. MACHINE-LIKE DECISION TREE / PSEUDOCODE

The functions referenced here are defined by Sections 5–15, not analyst votes.
All unknown required booleans evaluate False. Gate evidence is derived once
from the closed fixed registry; a failed parent is never replaced by another.

```python
def entry(package):
    if not package.frozen_screen_complete:
        return "PENDING_FROZEN_OOF", None
    if not package.required_predictions_and_metadata_valid:
        return "NO_PEFT:INSUFFICIENT_EVIDENCE", None

    # At Stage-6 entry: Section 5.3 selection on E0 with J_SELECT, saved once.
    # Here only recheck its post-pooling realization; never rerank encoders.
    if not package.stage0_and_prediction_provenance_complete:
        return "NO_PEFT:FORBIDDEN_EXECUTION", None
    P = recheck_saved_prospective_parent_after_stage6(package)
    if P is None:
        return "NO_PEFT:NO_CREDIBLE_PARENT", None
    if not exact_stage0_authority(P):
        return "NO_PEFT:FORBIDDEN_EXECUTION", None

    E = package.final_frozen_system_after_stage6
    if not required_supported_head_layer_pool_controls_complete(P):
        return "NO_PEFT:DOWNSTREAM_NOT_CLOSED", None
    if not all_scheduled_frozen_marginal_decisions_closed(package):
        return "NO_PEFT:FROZEN_DIVERSITY_SUFFICIENT", None

    # One diagnostic family; never used to change the adaptation classifier.
    OP, OE = bounded_shrunk_offset_meta_predictions(P, E)
    if robust_gain(OP, P) or robust_gain(OE, E):
        return "NO_PEFT:DOWNSTREAM_FIX_OR_UNCERTAINTY", None
    if not downstream_plateau_upper_bound_passes(P, E, OP, OE):
        # Exactly the Section-5.3 contrasts; UNKNOWN returns False.
        return "NO_PEFT:DOWNSTREAM_FIX_OR_UNCERTAINTY", None
    if any_unpromoted_frozen_addition_has_robust_system_gain(package, E):
        return "NO_PEFT:FROZEN_DIVERSITY_SUFFICIENT", None

    target = select_one_qualifying_pair_witness(P, E, package)  # 5.4
    if target is None:
        return "NO_PEFT:RESIDUAL_NOT_IDENTIFIED", None
    if not target.clean_dependency_and_VA_compatible:
        return "NO_PEFT:DEPENDENCY_OR_VA_CONTRADICTION", None
    if not fixed_QV_mapping_parity_and_8hour_budget_feasible(P):
        return "NO_PEFT:RECIPE_NOT_REPRODUCIBLE_OR_BOUNDED", None
    return "RUN_EXACT_SINGLE_PEFT", freeze_packet(P, E, target, recipe_v1)


def post_experiment(packet, results):
    if not results.complete_valid_matched_two_seed_VB_VA_package:
        return "ABANDON_ADAPTATION_TECHNICAL:KEEP_FROZEN_SYSTEM"
    # Includes attribution, target geometry/confusions, class, clean,
    # dependency, CE and V-A requirements and individual-seed checks.
    if not parent_pass(results, packet.P, packet.target):
        return "KEEP_FROZEN_ONLY:ADAPTATION_CLOSED"

    ER = replace_parent_with_seed_average(packet.E, results.A)
    replace_ok = system_pass(ER, packet.E, results)
    EB = add_seed_average_if_at_most_three_members(packet.E, results.A)
    if EB is not None:
        both_ok = (
            system_pass(EB, packet.E, results)
            and robust_gain(EB, ER)
            and robust_gain(EB, ablate(EB, results.A))
            and robust_gain(EB, ablate(EB, packet.P))
            and both_ablation_gains_positive_on_clean_and_VA(EB)
        )
        if both_ok:
            return "KEEP_BOTH:RETURN_TO_SS_FOR_FINALIST_CONFIRMATION"
    if replace_ok:
        return "REPLACE_PARENT:RETURN_TO_SS_FOR_FINALIST_CONFIRMATION"
    return "KEEP_FROZEN_ONLY:ADAPTATION_CLOSED"


# Every terminal NO_PEFT/KEEP_FROZEN_ONLY/TECHNICAL outcome closes the one
# adaptation slot. No second parent, recipe, rank, LR, layer count or rescue.
# No function here opens protected folds, uses public LB, relabels clips,
# changes retrieval, or authorizes unresolved pretrained assets.
```
