# Active validation

**PRIMARY_CV = historical V-B**, active under this alias. No new split is being
invented. No assignment, grouping rule, seed, hash, score or evaluation protocol
changes for naming convenience.

| Property | Existing authority |
| --- | --- |
| Labeled population | 826 supplied training clips |
| Split | Five-fold duplicate-family-safe StratifiedGroupKFold |
| Seed | `20260930` |
| Groups | Existing frozen duplicate graph; not inferred speaker identities |
| Metric | Macro-F1 over `angry / happy / neutral / sad` |
| Membership | [VALIDATION_VB_FOLDS.csv](../runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VB_FOLDS.csv) |
| Membership SHA-256 | `87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b` |

Definitions and provenance remain in the original
[FINAL_VALIDATION_AUTHORITY](../runs/DS-DEFHS-VALIDATION-HARDENING-002/FINAL_VALIDATION_AUTHORITY.md)
and subsequent
[POST_REDTEAM_VALIDATION_AUTHORITY](../runs/DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001/POST_REDTEAM_VALIDATION_AUTHORITY.md),
whose V-B is explicitly unchanged. The
[canonical artifact inventory](../runs/DS-DEFHS-VALIDATION-HARDENING-002/CANONICAL_ARTIFACT_INVENTORY.json)
and [closure manifest](../runs/DS-DEFHS-VALIDATION-HARDENING-002/CLOSURE_COMPLETED_ARTIFACT_MANIFEST.tsv)
retain hashes and external provenance. Use that exact existing fold file;
do not generate, copy or rename folds. Existing code/artifacts may keep `VB`
or `V-B`; future reports should say `PRIMARY_CV (historical V-B)`.

PRIMARY_CV determines whether a candidate credibly improves four-class emotion
recognition on unseen labeled speech while controlling duplicate memorization.
It is a **guardrail, not the competition objective**, and does not guarantee
speaker-disjoint evaluation or hidden-test transfer. Preserve existing OOF
alignment, train-side fitting and recorded scoring conventions.

The active evidence order is **PRIMARY_CV → TARGET209_ANALYSIS → PUBLIC_LB**.
Target-domain understanding comes from the **unlabeled TARGET209** recordings.
Public LB is partial real-test evidence, not a source of row labels or a
private-performance guarantee. No test macro-F1 can be computed without labels.

V-A, V-D, CLEAN, non-retrieval, quantization and correlated-allocation views are
historical diagnostics, consulted for a specific risk question rather than
simultaneous optimization objectives. Their original definitions, results and
promotion verdicts are preserved in the
[historical index](HISTORICAL_VALIDATION_INDEX.md). Old mandatory multi-view
gates describe their original missions; this alias does not retrospectively
rejudge those missions or authorize a new execution.

Protected validation remains closed to ordinary research. This mission does
not access it, refresh it or authorize another confirmation. Historical
protected artifacts remain preserved under their existing access restrictions.
