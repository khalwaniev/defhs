# Validation Plan — Draft

This file is a proposal until DS freezes a validated version.

## Why multiple views are needed

The supplied data contain exact train/test duplicates and train duplicates.
Ordinary stratified row-level CV can therefore reward memorization or corpus
dependency and overstate generalization.

At the same time, the hidden competition test appears to be sampled from the
same global corpus, so an aggressively speaker/source-disjoint split could
underestimate the competition's exploitable distribution.

## Proposed validation views

### V-A — competition-mimic

Repeated stratified K-fold at row level.

Purpose:
- estimate performance under the apparent competition sampling mechanism;
- permit explicit duplicate-retrieval logic when the corresponding reference
  is available inside the training fold.

This is not sufficient by itself.

### V-B — duplicate-safe grouped CV

All exact and validated near-duplicate recordings must remain in one fold.

Purpose:
- remove duplicate leakage;
- compare model families on genuine acoustic/emotional generalization.

### V-C — speaker/source stress test

If reliable speaker/source groups can be inferred, keep groups disjoint.

Purpose:
- detect models that exploit voice/source identity rather than emotion.

Do not automatically make V-C the competition-selection metric. Treat it as a
stress test unless evidence shows the hidden test is speaker-disjoint.

## Model promotion

A candidate should be promoted only when it:

1. improves the selected primary validation metric by a credible margin; or
2. adds demonstrable ensemble diversity that increases OOF macro F1;
3. does not rely on an unresolved leakage artifact;
4. remains scientifically plausible under stress validation.

OOF predictions must be saved for every promoted model.
