# Paired dependency-bootstrap calibration (conservative CI)

This addendum refines reporting **without changing the frozen scientific protocol, gate, split, candidate predictions, or result**. The previous continuation report gave the 95% percentile interval for the 18-feature fusion's pooled macro-F1 gain over C. We also replayed the exact max-t-style calibration implemented by `scripts/defhs_frozen_closure_utils.py` for the single prespecified paired contrast.

- 826 exact V-B OOF predictions, no protected labels, original C row-level parity.
- Duplicate-group and prompt-similarity components: **656**; ordered by root component ID.
- `np.random.Generator(np.random.PCG64(20260930)).exponential(1,(2000,656))`; same 2000 component multipliers aligned to both candidate and C.
- Observed pooled macro-F1 difference: **+0.026088266262358828**.
- Bootstrap SD: **0.009983215555854822**.
- Percentile 95% CI: **[+0.006757147181617196,+0.04622019753606841]**.
- Absolute standardized deviation 95th percentile (method='higher', same max-t helper): **1.9756596737973868**.
- Conservative 95% max-t-calibrated CI: **[+0.006364829873829692,+0.045811702650887964]**.

**Both methods have strictly positive lower bounds.** The frozen primary dependency-bootstrap gate remains **PASS**, even with the more conservative max-t adjustment. The final scientific disposition remains `ELIGIBLE_FOR_SS_REVIEW`; no target inference or submission was performed as part of this calibration.
