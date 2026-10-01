# Stage 1–3 Kaggle v3 frozen-screen result

Mission: `RS-DEFHS-SYSTEM-IMPLEMENTATION-001`

Source commit: `2bf65c7c978193f8baf8930fc46124190718bc86`

Status: **SUCCESS**

## Execution

- emotion2vec_base → `cuda:0`
- XLS-R-300m → `cuda:1`
- dual-GPU execution: PASS
- protected validation queried: NO
- Kaggle competition submission made: NO

## Frozen OOF results

| Family | Head | V-B macro-F1 | V-A macro-F1 |
|---|---|---:|---:|
| emotion2vec_base | L2 logistic | 0.7383745765682462 | 0.8016519493535111 |
| emotion2vec_base | calibrated RBF | 0.7026587840956953 | 0.7582039534692412 |
| XLS-R-300m | L2 logistic | 0.7107962132114378 | 0.7676504052799028 |
| XLS-R-300m | calibrated RBF | 0.6514871413848837 | 0.7054228952640451 |

emotion2vec + L2 logistic is the strongest standalone realization in this bounded frozen screen. XLS-R is not killed by standalone ordering alone; Stage 4 must test actual OOF complementarity and held-out marginal blend value.

PEFT remains pending frozen-system closure under `RS-DEFHS-ADAPTATION-POLICY-001`.

Heavy Kaggle output files are not represented by this GitHub report and still require import/preservation.
