# Data Understanding Certificate — Final

Mission: `DS-DEFHS-VALIDATION-HARDENING-002`

## Certificate status

**CERTIFIED — REVISE_AND_FREEZE**

The evidence-completion contract is satisfied.

## Completed evidence

The following are now executed, interpreted and preserved:

- package/schema and WAV integrity;
- label/class audit;
- duplicate and retrieval graph;
- low-level acoustic EDA;
- ID/order and train/test assignment diagnostics;
- recording/source heterogeneity;
- V-A/V-B/V-D validation evidence;
- private-LB emulator and public-fraction sensitivity;
- exact byte-preserved V-A/V-B/V-D/protected memberships;
- ECAPA speaker-verification embeddings over all 1,035 clips;
- Hindi ASR/prompt audit over all 1,035 clips;
- openSMILE eGeMAPSv02 standardized paralinguistics;
- joint speaker/prompt/eGeMAPS/source latent-regime audit;
- chance-adjusted prompt/class association analysis.

Primary closure interpretation diagnostics are preserved in:

`FINAL_INTERPRETATION_DIAGNOSTICS.json`

Heavy artifact provenance is preserved in:

`CLOSURE_COMPLETED_ARTIFACT_MANIFEST.tsv`

and under:

`/DEFHS/ds_validation_002/`

## Final evidence states

### VERIFIED

Directly observed/frozen facts include:

- 826 train + 209 test = 1,035 supplied clips;
- IDs 1..1035;
- mono 16 kHz WAV structure;
- 933 int16 / 102 int32;
- 227 duplicate groups / 467 clips;
- 77 train-test duplicate groups / 78 affected test clips;
- frozen duplicate threshold and retrieval map;
- the 75/636/878 label-conflict family;
- exact V-A, V-B, V-D and protected memberships;
- completed ECAPA, ASR, eGeMAPS and latent executors and their artifact hashes;
- the protected gate was not queried.

### INFERRED

Evidence supports, without elevating to unavailable ground truth:

- train/test are broadly a common mixture with modest nonlinear residual shift;
- ECAPA contains speaker-sensitive structure, but no stable independent
  speaker-disjoint cutoff is identified beyond the duplicate graph;
- repeated prompt structure exists, but most is duplicate-contained and
  chance-adjusted class association beyond duplicates is negligible;
- joint latent regimes are weak and not sufficiently stable for a new
  validation authority.

### UNRESOLVABLE FROM AVAILABLE EVIDENCE

The following remain genuinely unknowable from the competition evidence:

- why organizer prose says 1,036 while the supplied package contains 1,035;
- exact organizer speaker IDs;
- exact organizer prompt/script IDs;
- exact per-clip acted/spontaneous labels;
- broader ground-truth annotation correctness beyond directly observed
  conflicts;
- exact hidden public/private row fraction;
- exact hidden public/private assignment.

These unknowns are explicitly bounded and do not prevent freeze.

## Validation consequence

The completed closure does not justify redesigning the preserved backbone.

Final roles:

- V-B: primary duplicate-safe representation/model-family selection authority;
- V-A: secondary competition-mimic/retrieval-aware view;
- V-D: verified recording-format/source robustness stress;
- V-C: rejected as an authoritative split; ECAPA retained diagnostically;
- prompt/script grouping: diagnostic only;
- latent acted/spontaneous-like grouping: diagnostic only;
- protected seed 20261001: confirmation only.

## Certification statement

No material decision-relevant question remains unexplored because of an
execution limitation.

The DS foundation is scientifically complete enough for serious SER modeling
under the reissued validation authority.

The DS worker does not start modeling in this mission; the authority returns to
SS for independent acceptance and RS allocation.
