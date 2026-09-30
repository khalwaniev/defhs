# Private-LB Emulator Specification

The emulator does **not** claim to know the hidden public/private assignment.

For each pseudo-test evaluation:
1. pseudo-train labels only are exposed;
2. duplicate retrieval is applied only when a qualifying pseudo-train family member exists;
3. otherwise the SER model prediction is used;
4. retrieval-covered and non-retrieval performance are reported separately;
5. macro-F1 is computed exactly as the competition metric.

Public-fraction sensitivity is evaluated at 0.20 / 0.30 / 0.40 / 0.50; these are sensitivity scenarios, not estimates derived from the 0.40/0.60 score weights.

A 250-replicate class-stratified Monte Carlo sensitivity analysis over the fixed OOF predictions preserves the cheap-model ordering at every tested public fraction. FULL_RBF_SVM remains the top cheap reference on both V-A production-like pipeline predictions and V-B SER predictions.

Use:
- V-A + retrieval simulation for competition-behavior estimation;
- V-B for representation/model-family selection;
- V-D as source/format stress;
- the protected duplicate-safe gate only at promotion checkpoints.
