# Source / Recording Structure Report — Final Interpretation

## Verified recording structure

Two encoding regimes remain directly observed:

- int16: 933 clips (746 train, 187 test);
- int32: 102 clips (80 train, 22 test).

The test fraction is similar across these regimes, so dtype does not explain
the train/test split.

The int32 regime differs materially from int16 in duration, silence/pause and
spectral structure. Existing leave-one-format-out cheap-model stress remains
difficult:

- train int32 -> validate int16: macro-F1 roughly 0.24-0.32;
- train int16 -> validate int32: macro-F1 roughly 0.36-0.55.

## New closure evidence

### eGeMAPSv02

openSMILE 2.6.0 produced 88 standardized functionals for all 1,035 clips.

Train/test adversarial logistic AUC mean:

`0.476416387656352`

Largest absolute univariate train/test standardized mean difference among the
88 descriptors:

approximately `0.150`.

This does not expose a new strong standardized paralinguistic split signal.

### ECAPA

Strict ECAPA clustering mostly reproduces frozen duplicate families. Relaxing
the threshold adds non-duplicate clusters but reduces clustering stability.
Chance-adjusted association of ECAPA cluster identity with split or dtype is
very small in the strict-to-central region.

Therefore ECAPA does not identify a sufficiently stable independent
speaker/source partition for authoritative grouping.

### Joint latent regimes

Joint clustering has low silhouette, negligible split NMI, low dtype NMI and
only moderate adjacent-k stability. It does not identify a new stable source
regime.

## Final source conclusion

Recording/source heterogeneity is **VERIFIED**, with int16/int32 the only
directly observed, reproducible regime suitable for a frozen source stress.

Other latent source/speaker regimes are **INFERRED but insufficiently
identified** for authoritative validation.

## V-D

Canonical membership:

`VALIDATION_VD_REGIMES.csv`

SHA-256:

`f310cc024d122f19321e34a826e2793b5a661b1dd01ee4d1d72709a4472f0839`

V-D remains a diagnostic recording-format/source stress, not the primary
leaderboard estimator and not an acted/spontaneous label.
