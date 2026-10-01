# Standardized Paralinguistic Report — Final Interpretation

## Status

**COMPLETE — incorporated into the final DS-002 freeze.**

This file supersedes the earlier in-mission placeholder that marked the
openSMILE/eGeMAPS audit as a pending execution blocker. The required audit was
subsequently executed and interpreted before
`FINAL_VALIDATION_AUTHORITY.md` and the final data-understanding certificate
were issued.

## Canonical implementation

Executor:

`scripts/run_ds002_opensmile_egemaps_audit.py`

Package:

`opensmile==2.6.0`

Feature set:

`eGeMAPSv02`

Feature level:

`Functionals`

The standardized audit used 88 eGeMAPSv02 descriptors over all 1,035 supplied
clips and did not query the protected promotion gate.

## Final evidence

The completed audit reported:

- rows: `1,035`;
- descriptors: `88`;
- train/test adversarial logistic AUC mean:
  `0.476416387656352`;
- V-A OOF macro-F1:
  `0.5753536951338543`;
- V-B OOF macro-F1:
  `0.5601482021030706`;
- maximum absolute univariate train/test standardized mean difference:
  approximately `0.150`.

## Scientific disposition

The standardized paralinguistic feature family did **not** expose a material
new train/test shift requiring validation redesign.

It therefore supports the frozen architecture rather than replacing it:

- V-B remains the primary duplicate-family-safe representation/model-family
  selection authority;
- V-A remains the secondary competition-mimic / retrieval-aware view;
- V-D remains the recording-format/source diagnostic;
- the protected promotion gate remains confirmation-only.

The existing approximately 402-column librosa-derived acoustic matrix remains
valid complementary diagnostic evidence; eGeMAPSv02 is the standardized
paralinguistic evidence family required by the DS-002 closure contract.

## Final authority

Authoritative interpretation:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/FINAL_VALIDATION_AUTHORITY.md`

Final DS-002 certificate:

`runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_UNDERSTANDING_CERTIFICATE.md`

Post-red-team governing authority:

`runs/DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001/POST_REDTEAM_VALIDATION_AUTHORITY.md`

This audit is complete and is **not** a remaining freeze blocker.
