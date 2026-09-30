# Acted / Spontaneous Report

The organizers state that the corpus contains both acted and spontaneous speech, but the supplied package provides no regime labels.

Observable recording-format, low-level acoustic, duration, pause and clustering structure shows latent heterogeneity, but no defensible mapping from those latent clusters to acted versus spontaneous status can be established. The int16/int32 split must not be relabeled as acted/spontaneous without evidence.

**Evidence state: UNRESOLVABLE for per-clip hard labels.**

Policy:
- no hard acted/spontaneous labels are created;
- latent source/format heterogeneity is stress-tested through V-D;
- later representation models may be checked for robustness across verified format regimes and discovered stable latent clusters, without naming them acted/spontaneous.
