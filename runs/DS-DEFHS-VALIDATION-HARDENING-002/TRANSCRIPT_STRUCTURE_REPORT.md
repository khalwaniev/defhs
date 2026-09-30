# Transcript / Prompt Structure Report — Final Interpretation

## Status

**COMPLETE.**

Hindi ASR executed for all 1,035 clips using:

`mobiuslabsgmbh/faster-whisper-large-v3-turbo`

Immutable revision:

`0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf`

Language was forced to Hindi (`hi`).

The transcripts are machine-generated audit evidence, not organizer ground
truth.

## ASR quality evidence

- rows: `1,035`;
- empty normalized transcripts: `0`;
- detected language: Hindi for all rows;
- language-probability median: `1.0`;
- exact repeated-transcript rows: `338`;
- exact repeated normalized-transcript groups: `159`;
- duplicate-family transcript similarity median: `1.0`;
- duplicate-family transcript similarity p10: approximately `0.6126`.

These checks are sufficient for structural prompt auditing, while not implying
word-perfect transcription.

## Repeated-prompt structure

At character n-gram prompt similarity `0.90`:

- non-singleton prompt clusters: `170`;
- clips in those clusters: `367`;
- duplicate-family-contained clusters: `155`;
- duplicate-family-contained clips: `321`;
- clusters adding structure beyond the duplicate graph: `15`;
- clips in those beyond-duplicate clusters: `46`.

The same qualitative conclusion holds across the 0.80-0.98 sweep: most
repeated-prompt structure is already explained by duplicate families, while a
small residual repeated-prompt signal remains.

## Emotion association: chance-adjusted interpretation

For training rows at prompt similarity 0.90:

- raw NMI: `0.3509305706884669`;
- adjusted mutual information (AMI): `0.060114333811182155`.

A 2,000-permutation class-label null (seed `20261001`) gives:

- null NMI mean: `0.30931240776962304`;
- null NMI SD: `0.002074073309729764`;
- null p95: `0.31289458566085976`.

The high raw NMI is therefore substantially driven by the very high-cardinality
cluster variable.

After removing every known duplicate-family clip from training
(`n=453`):

- raw NMI: `0.36930343598857607`;
- AMI: `0.007476930842328752`.

Thus the chance-adjusted prompt/emotion association beyond the duplicate graph
is negligible.

## Validation decision

Prompt/script structure is **INFERRED** and scientifically real enough to keep
as a diagnostic, but it does **not** justify a new prompt-grouped validation
authority.

Do not authorize a text model merely from this audit.

V-A/V-B remain unchanged.
