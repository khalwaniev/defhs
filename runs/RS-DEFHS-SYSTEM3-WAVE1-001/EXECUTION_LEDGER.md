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
