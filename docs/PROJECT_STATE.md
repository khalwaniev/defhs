# Project State

Status date: 2026-09-30

## Repository phase

RB / repository bootstrap.

Local canonical path intended by user:

`/home/fikar/zingle/defhs`

GitHub canonical repository intended:

`khalwaniev/defhs`

## Verified competition-data state

From direct inspection of the supplied competition ZIP:

- train: 826 rows
- test: 209 rows
- all audio sample rates: 16 kHz
- median clip duration: approximately 2.88 s
- minimum duration: approximately 1.008 s
- maximum duration: 11.2 s
- audio storage includes both int16 and int32 PCM

Exact PCM hashing found:

- 8 train→test exact duplicate groups affecting 8 test clips
- 13 exact train-only duplicate groups involving 27 train clips

Earlier exploratory work also indicated a substantially larger set of
near-identical recordings after gain/encoding-invariant matching. That result
must be reproduced by repository code before it is treated as frozen authority.

## Current bottleneck

Validation/data authority is not yet frozen.

The key immediate question is not "which large model is best?" but:

> What validation construction most faithfully estimates the hidden test while
> preventing duplicate/source/speaker structure from creating misleading model
> selection?

## Next worker

DS should own the first frozen data/validation mission, with RS involvement for
duplicate-retrieval methodology and later foundation-model baselines.
