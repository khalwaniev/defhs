# Wave1 decision

Status: SCIENCE_COMPLETE_ARTIFACT_CLOSURE_PENDING. The 0.90 architecture target is not reached.

Prefer the fixed 50/50 original emotion2vec/XLS-R probability pair for SS review. Its legal outer refits reproduce historical metrics; this is reused development evidence, not independent replication. V-B gain +0.0384411 is positive in all five folds and all leave-one-fold deletions, with positive CLEAN, V-A and V-A nonretrieval directions. A conservative simultaneous uncertainty bound still crosses zero.

Do not promote nested fitting: V-A nonretrieval direction is negative relative to the fixed pair. Do not add progressive emotion2vec: all pilots selected epoch zero, and strict shared-initializer recovery yields A0=A1 with no retained adaptation. Original erroneous four-block refit outputs are preserved; corrected results supersede them.

AST's supervised adaptation gain against its weaker frozen control is repeatable, and seed averaging supports that finding conditionally. Its absolute scores remain weak, and none of its registered fixed marginal blends meets promotion conventions. Keep this positive scientific finding separate from deployment membership.

The fixed pair still makes 184 V-B errors; 56 are neutral↔sad confusions. This does not prove label ambiguity, representation failure or an achievable oracle ceiling. Return these target gaps and errors to SS for the accepted Wave2 decision. No Wave2 execution, protected access or competition submission.

Artifact closure recovery: scientific conclusions above are unchanged. Drive remains short of B1_fold4_pilot_STATE.pt for V-A seed20260917. Complete preservation is not claimed; exact transport failures and the unchanged artifact hash are recorded in CHECKPOINT_PROVENANCE.json.
