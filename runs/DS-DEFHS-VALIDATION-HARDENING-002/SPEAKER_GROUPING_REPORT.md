# Speaker Grouping Report — Final Interpretation

## Status

**COMPLETE.**

The required pretrained speaker audit executed successfully on all 1,035 clips.

Model:

`speechbrain/spkrec-ecapa-voxceleb`

Immutable revision:

`0f99f2d0ebe89ac095bcc5903c4dd8f72b367286`

Embedding matrix:

`1035 x 192`

The canonical embedding artifact is preserved in Drive under
`/DEFHS/ds_validation_002/speaker_embeddings/`.

## Direct evidence

ECAPA strongly confirms the already-frozen duplicate structure:

- duplicate-pair cosine similarity median: `0.9999968409538269`;
- minimum duplicate-pair similarity: `0.7258741855621338`;
- sampled nonduplicate p95: `0.38857135772705076`;
- sampled nonduplicate p99: `0.5092418485879889`.

The crucial question is whether ECAPA creates a reliable speaker-like grouping
that is materially independent of the duplicate graph.

| Agglomerative distance | non-singleton clusters beyond duplicate graph | clips in those clusters |
|---|---:|---:|
| 0.10 | 0 | 0 |
| 0.15 | 0 | 0 |
| 0.20 | 2 | 6 |
| 0.25 | 11 | 33 |
| 0.30 | 42 | 129 |
| 0.35 | 88 | 290 |

At the strict, highly stable end of the sweep, essentially all non-singleton
ECAPA clusters are already contained inside frozen duplicate families.

As the threshold is relaxed enough to create substantial additional grouping,
threshold-to-threshold stability deteriorates:

- ARI 0.10 -> 0.15: `0.9688`;
- 0.15 -> 0.20: `0.9802`;
- 0.20 -> 0.25: `0.9485`;
- 0.25 -> 0.30: `0.8411`;
- 0.30 -> 0.35: `0.7942`;
- 0.35 -> 0.40: `0.6806`.

There is therefore no scientifically identified cutoff at which the grouping
both adds substantial non-duplicate information and remains sufficiently
stable to be treated as a speaker-disjoint authority.

Chance-adjusted association with train/test membership is effectively null
across the strict-to-central thresholds (AMI approximately -0.001 to 0.001),
and dtype AMI remains very small (approximately 0.004-0.014 over 0.10-0.35).

## Interpretation

The embeddings contain real speaker-sensitive information, but the reliable
strict clustering region mostly reproduces duplicate-family identity. More
permissive clustering produces additional speaker-like hypotheses, but those
hypotheses depend materially on the chosen threshold.

These groups are **not organizer speaker IDs**.

Train/test speaker-like overlap is therefore **INFERRED but
threshold-sensitive**: mixed clusters exist, including clusters beyond the
duplicate graph at permissive thresholds, but the evidence does not support an
exact speaker-overlap count or authoritative speaker-disjoint partition.

## V-C decision

**REJECT AUTHORITATIVE V-C.**

Do not freeze an ECAPA-derived speaker-disjoint validation split.

Retain ECAPA assignments as a diagnostic/stress resource for later model
analysis. V-B already supplies the robust dependency guardrail that is
scientifically identified by the data.

This decision is positive evidence from an executed pretrained speaker audit,
not a consequence of unavailable model weights.
