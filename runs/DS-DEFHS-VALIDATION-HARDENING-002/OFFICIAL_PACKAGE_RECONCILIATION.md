# Official Package Reconciliation

**Evidence state: VERIFIED package state; UNRESOLVABLE organizer-prose discrepancy.**

The supplied package contains exactly 826 training rows and 209 test rows, for 1,035 examples. The union of train and test IDs is exactly the contiguous set 1..1035, with no overlap and no missing ID. The sample-submission IDs exactly match test IDs.

Competition prose states 1,036 samples. No 1,036th supplied example is present and no missing ID exists inside 1..1035. Therefore the operational competition authority is the supplied 1,035-example package. The origin of the one-sample prose discrepancy is not identifiable from the available package and is not guessed.

All 1,035 WAVs are mono 16 kHz. 933 are int16 PCM and 102 are int32 PCM. Duration ranges from 1.008 s to 11.2 s (median about 2.88 s).

Policy: use the supplied CSV/WAV package as schema authority; register the 1,036 statement as unresolved metadata/prose discrepancy with no fold or inference adjustment.
