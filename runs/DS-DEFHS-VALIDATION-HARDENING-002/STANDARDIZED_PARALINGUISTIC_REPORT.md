# Standardized Paralinguistic Report

## Status

**PENDING REQUIRED EXECUTION — final freeze blocker.**

The existing ~402-column librosa-derived acoustic matrix remains valid, but it is not a substitute for the standardized feature family required by the controlling mission.

## Canonical required implementation

Executor:

`scripts/run_ds002_opensmile_egemaps_audit.py`

Required package:

`opensmile==2.6.0`

Feature set:

`eGeMAPSv02`

Feature level:

`Functionals`

The executor is designed to extract the standard 88-dimensional eGeMAPSv02 functionals for every supplied clip and then evaluate:

- feature completeness;
- train/test standardized-feature shift;
- low-cost V-A performance;
- low-cost V-B performance;
- recording/source associations;
- whether standardized descriptors expose structure missed by the existing acoustic matrix.

It explicitly does not use the protected promotion gate.

## Why this is not marked UNRESOLVABLE

openSMILE/eGeMAPS is public and technically executable in an appropriate environment. The current failure is an execution-environment package-access limitation, not an epistemic limitation of the competition data.

Therefore no conclusion such as "eGeMAPS adds no new structure" has been made.

## Final-closure requirement

A final data-understanding certificate may be issued only after:

- `EGEMAPS_FEATURES.csv`;
- `EGEMAPS_SHIFT_SUMMARY.csv`;
- `EGEMAPS_AUDIT_RESULTS.json`;
- `EGEMAPS_MANIFEST.json`

have actually been produced, checked, preserved, and interpreted.
