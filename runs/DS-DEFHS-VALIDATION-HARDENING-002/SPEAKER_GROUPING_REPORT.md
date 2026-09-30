# Speaker Grouping Report

**Evidence state: UNRESOLVABLE as authoritative speaker identity from the current observable package.**

The competition supplies no speaker IDs. Low-level acoustic and pitch features can expose voice/source structure but cannot establish identity reliably enough for a speaker-disjoint authority.

A strong pretrained ECAPA-TDNN speaker-embedding audit was attempted, but pretrained weights are not locally cached and the current execution environment cannot fetch the model weights directly. No demographic attributes are inferred from voice.

Policy:
- V-C speaker-disjoint validation is **not frozen**;
- do not invent speaker IDs from pitch or low-level clusters;
- future execution with accessible ECAPA/x-vector weights may add a speaker stress view, but it must pass threshold and clustering-stability checks before becoming authoritative;
- current model promotion must remain robust under duplicate-safe V-B and verified format/source stress V-D.
