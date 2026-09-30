# Initial Data Audit

Date: 2026-09-30

This is an initial repository bootstrap report, not yet the frozen DS authority.

## Dataset sizes

- train.csv: 826 rows
- test.csv: 209 rows
- total: 1,035 rows represented by train/test

The Kaggle overview text reports 1,036 samples, so the discrepancy between
overview text and supplied train/test assets should be recorded rather than
silently reconciled.

## Audio format

Direct WAV inspection:

- sample rate: 16,000 Hz for all 1,035 clips
- mono after inspection
- PCM dtypes observed: int16 and int32
- median duration: about 2.88 seconds
- range: about 1.008 to 11.2 seconds

## Exact duplicates

SHA-256 hashes over decoded PCM samples found:

- 8 exact cross-split train→test duplicate groups
- 8 affected test clips
- 13 exact train-only duplicate groups
- 27 train clips inside those train-only exact groups

Exact duplicate matching is only a lower bound because gain changes, encoding
changes, trimming, or other benign transforms can conceal identical source
recordings.

## Required next audit

The frozen audit must add:

- silence-trimmed/gain-normalized waveform fingerprints;
- resampling-invariant comparison if needed;
- near-duplicate clustering;
- conflicting-label detection within duplicate groups;
- source/speaker similarity analysis;
- duration/energy/SNR/source-distribution diagnostics;
- train/test dependency map;
- reproducible CSV/JSON group artifacts.

Do not use random row-level CV as the sole validation authority until this work
is complete.
