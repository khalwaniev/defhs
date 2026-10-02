# DEFHS Project State

Status date: 2026-10-02

## Objective

Competition:

`dataverse-detecting-emotions-from-hindi-speech`

Target:

maximize robust final/private-leaderboard macro-F1 over:

`angry / happy / neutral / sad`

## Canonical authority

Repository:

`khalwaniev/defhs`

Canonical branch:

`main`

Canonical local repository:

`/home/fikar/zingle/defhs`

Heavy-artifact root:

`/DEFHS/`

Governing workflow:

`WORKFLOW.md`

## Validation

Status:

**FROZEN — PATCH_AND_FREEZE**

Frozen policy:

- V-B = primary duplicate-family-safe model/representation selection authority;
- V-A = secondary competition-mimic / retrieval-aware view;
- V-D = diagnostic recording/source-format stress;
- V-C = rejected as authoritative;
- Q128/Q960 = diagnostic quantization stresses only;
- correlated-allocation envelope = secondary leaderboard-risk sensitivity;
- retrieval = fixed 77 duplicate groups / 78 test clips;
- protected seed 20261001 = one SS-authorized A/B confirmation completed; no retuning.

Detailed authority:

`runs/DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001/POST_REDTEAM_VALIDATION_AUTHORITY.md`

Do not redesign validation without new material evidence.

## Completed foundations

Data/validation work:

**COMPLETE**

Knowledge acquisition:

`RS-DEFHS-KNOWLEDGE-ACQUISITION-001`

Verdict:

**PASS_ACQUISITION_COMPLETE**

Final acquisition authority:

`runs/RS-DEFHS-KNOWLEDGE-ACQUISITION-001/FINAL_RETURN_TO_SS.md`

Knowledge inventory:

- 84 canonical records;
- 15 acquired paper PDFs;
- 2 exact-commit repository snapshots;
- all selected binaries independently verified after Drive readback.

BhavVani versus competition SRCASW-BhavVaani provenance remains:

**UNRESOLVED**

Do not transfer licensing, speaker metadata, or source lineage between them.

## Layer-1 system design

Mission:

`RS-DEFHS-SYSTEM-DESIGN-001`

Worker role:

**Research Scientist**

Status:

**COMPLETE — SS ACCEPTED**

Authoritative artifacts:

- `runs/RS-DEFHS-SYSTEM-DESIGN-001/MISSION.md`
- `runs/RS-DEFHS-SYSTEM-DESIGN-001/SYSTEM_DESIGN.md`
- `runs/RS-DEFHS-SYSTEM-DESIGN-001/EXPERIMENT_LADDER.md`
- `runs/RS-DEFHS-SYSTEM-DESIGN-001/ASTRA_BOTTLENECK_PACKET.md`
- `runs/RS-DEFHS-SYSTEM-DESIGN-001/FINAL_RETURN_TO_SS.md`

Final Layer-1 authority commit:

`5d81af578cd67c4e9826d270c11abbe1812652c1`

## Layer-2 adaptation policy

Mission:

`RS-DEFHS-ADAPTATION-POLICY-001`

Worker role:

**Research Scientist — Astra 6 Max**

Status:

**COMPLETE — SS ACCEPTED**

Authoritative artifacts:

- `runs/RS-DEFHS-ADAPTATION-POLICY-001/MISSION.md`
- `runs/RS-DEFHS-ADAPTATION-POLICY-001/ADAPTATION_POLICY.md`
- `runs/RS-DEFHS-ADAPTATION-POLICY-001/FINAL_RETURN_TO_SS.md`

Final Layer-2 authority commit:

`7a92164b3a5f664f394ac67013287e6a8417a5dc`

Integrated prior:

**FROZEN_DIVERSITY_PRIOR**

Current PEFT status:

**NO_PEFT:DOWNSTREAM_NOT_CLOSED — RS IMPLEMENTATION RETURN PENDING SS REVIEW**

PEFT is not an automatic implementation stage. It is permitted only if the
precommitted RS2 entry gate passes after the frozen OOF program is complete.

If triggered, the sole permitted first adaptation recipe is:

`DEFHS_UPPER_QUARTER_QV_LORA_FIXED_DOWNSTREAM_V1`

A failed gate or failed bounded adaptation closes adaptation under the current
authority; no rescue search is authorized.

## Frozen implementation architecture

The implementation program is:

1. keep certified duplicate retrieval as a separate deterministic hard override;
2. verify checkpoint revision, license, reproducibility and competition-policy
   authority before execution;
3. build the common frozen representation scaffold;
4. screen the bounded emotion2vec-family candidate and Vesper-4;
5. run the bounded WavLM-large versus XLS-R-300m discriminator and retain at
   most one generic/multilingual SSL lane;
6. retain FULL_RBF_SVM only while it provides genuine ensemble value;
7. treat eGeMAPS and transcript semantics only under their existing conditional
   diversity gates;
8. select a small 2-3-lane frozen ensemble using held-out marginal value;
9. complete the authorized pooling and bounded offset controls;
10. apply the RS2 G0-G6 PEFT entry policy;
11. run exactly one bounded Q/V LoRA experiment only if that policy triggers;
12. complete finalist stresses before any later SS-authorized protected
    confirmation.

No broad foundation-model zoo, full-model fine-tuning or adaptive PEFT search is
authorized.

## SS integration

Mission:

`SS-DEFHS-DESIGN-INTEGRATION-001`

Verdict:

**PASS — SCIENTIFIC DESIGN FROZEN FOR LAYER-3 IMPLEMENTATION**

Authority:

`runs/SS-DEFHS-DESIGN-INTEGRATION-001/FINAL_INTEGRATION.md`

## Implementation mission

`RS-DEFHS-SYSTEM-IMPLEMENTATION-001`

Worker role:

**Research Scientist — GPT-5.6 Sol High**

Execution continuation began from local/remote
`16f271b50b1f6d4d3605b3ccb580d5667972dd45` on
`rs/system-implementation-001`. Stage 0 and the successful dual-T4 Kaggle V3
extraction were reused; no encoder extraction was repeated.

The CPU continuation completed Stage 4 frozen complementarity/membership,
Stage 5 transcript controls, Stage 6 one-parent pooling, the pre-PEFT controls
and terminal gate, Stage 8 offsets, and Stage 9 pre-protected diagnostics.

Accepted locked finalist: `emotion2vec_base_L2_LOGREG`, frozen final-frame mean+std,
ordinary argmax, with the existing certified retrieval hard override separate.
V-B macro-F1 is `0.7383745765682462`; V-A SER is
`0.8016519493535111`; retrieval-aware V-A is `0.8052768510049559`.
The neural pair's positive point gain fails the simultaneous marginal criterion;
the acoustic/eGeMAPS/text additions and pooling/offset changes are not retained.

G2 remains UNKNOWN because scalar-mixture evidence and an ex-ante API
unavailability record are absent. G3 and G4 also fail. Per the accepted policy,
adaptation is closed and no PEFT experiment ran. This does not declare the
representation irreducible or the scalar-mixture architecture unsupported.

V-D cross-format stress remains difficult. Correlated-allocation diagnostics
preserve the mean advantage over the accepted cheap references across the
tested scenarios; they do not prove hidden-domain transfer.

The finalist is fitted on all 826 cached training embeddings and its 209 test
inference rows are archived with the unchanged 78-clip certified map. The next
user instruction accepted this lock and authorized one protected comparison
against the exact historical FULL_RBF_SVM, plus submission preparation.
The aggregate decision rule was committed before protected assignment access.
Protected macro-F1 is `0.7376693938891288` for the finalist and
`0.6109463795639095` for FULL_RBF_SVM: **CONFIRM_FINALIST**.
The prepared `submission.csv` passes exact original sample order/schema/209-ID
parity, with the unchanged 78-row retrieval override. Status is
**READY_FOR_SUBMISSION**. No retuning or Kaggle submission occurred.

Implementation results and the SS return are under
`runs/RS-DEFHS-SYSTEM-IMPLEMENTATION-001/`. GitHub remains canonical for decisions;
heavy V3 and CPU artifacts are preserved in the existing Drive mission root.
The pre-protected finalist was accepted for this confirmation; no main branch
merge occurred. Confirmation and preparation details are in the existing mission
folder's `PROTECTED_CONFIRMATION.md` and `PROTECTED_CONFIRMATION.json`.

The implementation worker must preserve the frozen validation hierarchy, OOF
alignment, experiment provenance, promote/kill rules, and the precommitted RS2
adaptation policy.

At the historical integration point no Layer-3 experiment had been run.
The current implementation results are recorded above and in its mission ledger.
## Protected information

Protected seed 20261001 status:

**CONFIRMATION-ONLY — USED ONCE, FINALIST CONFIRMED**

No protected candidate performance was queried during Layer 1 or Layer 2.
The later explicitly authorized execution compared only the locked finalist and
historical FULL_RBF_SVM. No result initiated another tuning loop; Kaggle upload
still requires a separate instruction.

## Do not redo

Unless concrete new evidence reveals a defect:

- do not restart EDA;
- do not redesign V-A/V-B/V-D;
- do not revive V-C as authority;
- do not redo knowledge discovery/acquisition;
- do not query protected validation during ordinary model research;
- do not infer hidden public/private row fractions from 40/60 score weights;
- do not assume BhavVani and SRCASW-BhavVaani are the same dataset;
- do not launch a broad pretrained-model zoo;
- do not use unresolved external-data/model licensing as if it were permission.

Historical details remain preserved under `runs/`.

## Score-push mission closure

RS-DEFHS-SCORE-PUSH-001 on `rs/score-push-001` completed the two authorized mechanisms. Both emotion2vec+ checkpoints ran once; their best V-B scores were 0.54036535 (base) and 0.52066002 (large). The single cached XLS-R pair reached 0.72276314 and was rejected. The locked control was retained before the one fixed Qwen3-8B semantic pass. Its fusion scored V-B 0.75239046 (+0.01401588), V-A 0.77967784 (-0.02197411), non-retrieval 0.74578477 (+0.01466807), and retrieval-aware V-A 0.81370347. Both scientific robustness and competition deployment were evaluated separately. Fusion was rejected for modest, inconsistent primary gain, V-A/source/class regressions, despite positive CLEAN/non-retrieval/Astra-excluded diagnostics; confidence-bound failure was not an automatic deployment veto.

The accepted emotion2vec_base meanstd/logistic C1 system and 78-row certified test retrieval override remain unchanged. No protected access or competition submission occurred in this mission. No new submission was prepared. Heavy audio caches and semantic outputs are byte-verified in `gdrive:DEFHS/rs_score_push_001`. All measurements, decisions, code and pointers are under `runs/RS-DEFHS-SCORE-PUSH-001/`; `FINAL_RETURN_TO_SS.md` and `FINAL_DECISION.json` are its closure record. SS may accept closure with the current control retained; any major new semantic gating mechanism needs new authority.
