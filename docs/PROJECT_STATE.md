# DEFHS Project State

Status date: 2026-10-01

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
- protected seed 20261001 = untouched, confirmation-only.

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

**COMPLETE — RETURNED TO STRATEGIC SCIENTIST**

Active mission branch:

`ss/evidence-synthesis-001`

The historical `ss/...` branch name is retained intentionally. No replacement
remote branch was created.

Authoritative Layer-1 artifacts:

- `runs/RS-DEFHS-SYSTEM-DESIGN-001/MISSION.md`
- `runs/RS-DEFHS-SYSTEM-DESIGN-001/SYSTEM_DESIGN.md`
- `runs/RS-DEFHS-SYSTEM-DESIGN-001/EXPERIMENT_LADDER.md`
- `runs/RS-DEFHS-SYSTEM-DESIGN-001/ASTRA_BOTTLENECK_PACKET.md`
- `runs/RS-DEFHS-SYSTEM-DESIGN-001/FINAL_RETURN_TO_SS.md`

## Provisional system selected by Layer 1

The implementation program is frozen-first:

1. keep the certified duplicate-retrieval lane separate as a deterministic hard
   override;
2. screen a frozen emotion2vec-family representation as the primary
   emotion-specialized candidate;
3. screen frozen Vesper-4 as a second emotion-specialized candidate;
4. run one bounded WavLM-large versus XLS-R-300m discriminator and keep at most
   one generic/multilingual SSL lane;
5. retain the existing FULL_RBF_SVM acoustic system only while it adds genuine
   ensemble diversity;
6. treat eGeMAPS and transcript semantics as conditional diversity lanes;
7. use a simple regularized probability/logit blend and ordinary argmax first;
8. do not perform full-model fine-tuning.

Every pretrained asset remains subject to execution-time checkpoint revision,
license, and competition-policy verification.

## Astra bottleneck

Primary unresolved decision:

**Should the system remain a fully frozen representation-diversity core, or,
after the frozen screen selects one strongest encoder, should one bounded
upper-layer PEFT experiment become the default next use of GPU compute?**

Astra receives:

`runs/RS-DEFHS-SYSTEM-DESIGN-001/ASTRA_BOTTLENECK_PACKET.md`

Astra must not redo the broad evidence synthesis, validation, EDA, or knowledge
acquisition.

## Next handoff

1. Strategic Scientist reviews and integrates Layer-1 system design.
2. Astra 6 Max answers only the adaptation-versus-diversity bottleneck.
3. Strategic Scientist integrates the Astra answer.
4. Layer-3 GPT-5.6 Sol High Research Scientist implements the ordered experiment
   ladder.

No Layer-3 modeling has been authorized or run by this mission.

## Protected information

Protected seed 20261001 remains:

**UNTOUCHED / CONFIRMATION-ONLY**

No protected candidate performance was queried during Layer 1.

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
