# Source / Recording Structure Report — Closure Reissue

## Verified structure retained

Two verified encoding regimes exist:

- int16: 933 clips (746 train, 187 test);
- int32: 102 clips (80 train, 22 test).

The test fraction is similar in both regimes (about 20.0% versus 21.6%), so recording dtype does not explain the train/test split.

The int32 regime differs materially from int16 in duration, silence/pause, and spectral structure. Existing leave-one-format-out cheap-model stress remains difficult:

- train int32 -> validate int16: macro-F1 roughly 0.24–0.32;
- train int16 -> validate int32: macro-F1 roughly 0.36–0.55, depending on cheap model.

Low-level unsupervised clustering remains only weak-to-moderately concordant across representations (cross-representation ARI about 0.42 for k=2 and lower thereafter), with negligible relation to train/test membership.

## Canonical V-D definition

`VALIDATION_VD_REGIMES.csv`

SHA-256:
`f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839`

V-D remains a verified **recording-format/source stress**, not a claim of true source-corpus identity or acted/spontaneous identity.

## Closure limitation

The controlling mission additionally requires standardized openSMILE eGeMAPSv02 evidence and actual pretrained speaker embeddings. Those may reveal source/speaker structure missed by the existing librosa matrix.

Therefore:

- the existence of recording heterogeneity is VERIFIED;
- int16/int32 V-D membership is VERIFIED;
- the conclusion that no additional reliable source/speaker grouping exists is **not final** until eGeMAPS and ECAPA execute.

Canonical pending executor:

`scripts/run_ds002_opensmile_egemaps_audit.py`
