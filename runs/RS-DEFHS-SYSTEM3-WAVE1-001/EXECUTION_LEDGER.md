# Execution ledger

- Read WORKFLOW first; verified parent/main remote and tracked-clean checkout, preserving .tmp.
- Created exactly one execution branch from authorized parent.
- Located all permitted inputs; explicit required hashes match. Final preflight and launch pending runner checks.
- Local runtime CPU-only; Kaggle reported 23.49 GPU hours remaining. One private dual-T4 job runs independent A and B lanes concurrently, with CPU fitting local.

- W1.0 PASS: all explicit hash, ID/support/retrieval and historical pair replay checks pass. No protected file read.
- Launched Kaggle version1: khalwaniev/defhs-system3-wave1-matched-adaptation; source 824ef6b4b93a42a92747e134b4d8b85c342f86ef, generated runner SHA256 7a78ff0434cd4f57f286f76753b36b445a9d7b42708cbec3be98fe4f7e5dee0a. Independent GPU A0/A1 and B0/B1 workers launched together. CPU W1.1/W1.2 started immediately concurrently.

- CPU fixed pair: VB .7768156647359765; VA .8266398472107417; VA non-retrieval .767215174621592. Historical replay/outer refit hard labels agree.
- Legal nested fusion: VB .7833622524562892, all5 folds positive; VA .8264383258101213, non-retrieval .7639258492378965. Keep fixed pair under registered concordance. Independent sklearn metrics and all inner ID-hash exclusions pass.
- CPU heavy outputs: 28/28 files byte-verified on Drive, zero differences; manifest recorded. GPU A stopping observations select epoch0 in all5 folds; final OOF analysis awaits notebook outputs and complete VB Wave1.
- Reused frozen ordinary V-A retrieval audit (232 held-out rows covered), without refitting models or changing retrieval: control .8052768510049559; fixed pair .8314384804867729; nested .8289228474552494. Control parity passes; audit hash recorded. This is a correlated diagnostic, not independent confirmation.
- Adopted SS execution-efficiency addendum: status/log inspection approximately every five minutes, surfacing only meaningful transitions. Local Kaggle log capture uses passive server-sent events (installed CLI source verified), not active status polling. No running recipe or completed fit changed.
- Complete VB GPU package: all20 outer predictions saved, 172 files / 4,427,893,601 bytes SHA256-verified; manifest 2ca3906fcb379ceb24c912719bf24c2cb02287cf2d846da92978a8b7519da6dc. Checkpoint, ID exclusion, head-phase parity and independent sklearn audits pass. Transport reused144 valid files and downloaded28; no completed fit repeated.
- A0=A1 VB .7383745765682462; all selected epochs0, no retained adaptation; fixed Candidate_A .7678538080170124. A is closed for this recipe, no VA/seed2 entry.
- B0 VB .5468363348281033; B1 .5928778934468633 (+.046041558618759915), 4/5 fold gains, all classes positive, CLEAN .5556312749295205→.5829384792860433. B1 selects[4,6,6,5,5]. Fixed Candidate_B .7761482572759908 (−.0006674074599857 vsP), not promoted. B qualifies for separately trained matched VA confirmation through standalone adaptation evidence.
- VA packaging upload failed before execution: server HTTP400 INVALID_ARGUMENT, "The title cannot exceed 50 characters." Inspected the exact response, then shortened only conditional notebook title/slug generation and added a length guard. No fold ran, no recipe changed, no scientific rescue.
- Launched matched AST VA version1 after metadata fix: khalwaniev/defhs-system3-wave1-b-va-20260930; source0959ca82e53f932d85c274ced0f0407d1f1b4a77; runner7e3fdd08cb4b108bc6f6570e662e770e118f6d32e39a4a2dd8f05a789d6066f1. GPU0 folds0/2/4, GPU1 folds1/3; exact deterministic frozen-feature cache, clean validation, identical per-ID/epoch augmentation. No A VA or seed2.

- V-B immutable server source and AST full-window/clip-family segmentation audits passed. Pilot/refit initialization, schedule, and checkpoint-selection details are recorded in CHECKPOINT_PROVENANCE.json. All 173 V-B package objects were copied to Drive; rclone download-based byte verification is running. V-A remains in flight without recipe changes or completed-fold restarts.
