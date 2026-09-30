# DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001

## Purpose

Targeted post-freeze correction triggered by:

`AR-DEFHS-FINAL-VALIDATION-DATA-REDTEAM-001`

Canonical frozen parent:

`ds/validation-hardening-002@c7da27a0f7d0927a5070da8cf825d1415546345c`

Adversarial authority:

`audit/final-validation-data-redteam-001@5973f06e1a710017776c2f4ced60f892eaf2c76b`

## Scope

Only two bounded defects are in scope:

1. determine the true materiality of sample-count quantization, including whether
   `samples % 128` survives multiplicity and duration/source conditioning;
2. replace single forced hidden-allocation attacks with a correlated-allocation
   sensitivity envelope that separates baseline, plausible correlation, strong
   stress, and extreme forced tails.

## Preserved authority

Unless contradicted by new evidence:

- V-B remains primary;
- V-A remains secondary;
- V-D remains diagnostic;
- authoritative V-C remains rejected;
- retrieval remains unchanged;
- the protected seed `20261001` remains confirmation-only.

## Prohibitions

- no protected-gate performance is read or queried;
- no serious SER/foundation-model training;
- no main DS-002 restart;
- no hidden private membership is invented.

## Stop condition

Return exactly one final patch verdict:

- `PATCH_AND_FREEZE`;
- `MATERIAL_REDESIGN_REQUIRED`;
- `PATCH_INCONCLUSIVE`.
