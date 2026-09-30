# Acted / Spontaneous Report — Final Interpretation

The organizers state that both acted and spontaneous speech are present, but
the supplied package provides no per-clip acted/spontaneous labels.

## Completed joint evidence

The required joint audit has now executed using:

- ECAPA speaker-like clusters;
- ASR-derived prompt clusters;
- openSMILE eGeMAPSv02 structure;
- recording dtype/source information;
- duration and observable acoustic structure.

Over joint clustering `k=2..6`:

- silhouette: approximately `0.1061-0.1626`;
- split NMI: approximately `0.00034-0.00138`;
- dtype NMI: approximately `0.00131-0.05579`;
- adjacent-k ARI: approximately `0.35-0.66`.

The joint representation therefore does not reveal a strong, uniquely
identified latent partition. Cluster membership changes materially with k, and
the clusters have essentially no relationship to train/test membership.

## Scientific conclusion

Exact organizer acted/spontaneous labels are:

**UNRESOLVABLE FROM AVAILABLE EVIDENCE.**

Latent acted/spontaneous-like structure is:

**INFERRED WEAK / INSUFFICIENT FOR VALIDATION AUTHORITY.**

No cluster is to be named "acted" or "spontaneous" without ground truth.

The new evidence does not justify:

- per-clip acted/spontaneous pseudo-labels;
- an acted/spontaneous training target;
- a new latent-regime validation split;
- replacing V-D with a semantically named regime.

## Validation policy

- V-A remains the row-level competition-mimic view.
- V-B remains the primary duplicate-safe selection authority.
- V-D remains the verified int16/int32 recording-format/source stress.
- No new acted/spontaneous validation component is frozen.
