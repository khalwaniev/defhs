# Source / Recording Structure Report

Two verified encoding regimes exist:
- int16: 933 clips (746 train, 187 test)
- int32: 102 clips (80 train, 22 test)

The test fraction is similar in both regimes (~20.0% vs ~21.6%), arguing against a simple format-defined train/test split. int32 clips nevertheless differ materially in duration, silence/pause structure and spectral characteristics.

Leave-one-format-out stress tests are hard:
- train int32 -> validate int16: macro-F1 about 0.24–0.32
- train int16 -> validate int32: macro-F1 about 0.36–0.55, depending on cheap model

Unsupervised clustering is internally stable within a representation but only weak-to-moderately concordant across basic versus spectral representations (cross-representation ARI about 0.42 for k=2 and lower thereafter). Cluster membership has negligible NMI with train/test split.

Conclusion: recording/source heterogeneity is real, but inferred clusters are not reliable enough to become authoritative source groups. The verified dtype regime is retained as V-D format/source stress only.
