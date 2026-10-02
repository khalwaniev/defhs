# Execution ledger

- Read WORKFLOW first; verified parent/main remote and tracked-clean checkout, preserving .tmp.
- Created exactly one execution branch from authorized parent.
- Located all permitted inputs; explicit required hashes match. Final preflight and launch pending runner checks.
- Local runtime CPU-only; Kaggle reported 23.49 GPU hours remaining. One private dual-T4 job runs independent A and B lanes concurrently, with CPU fitting local.
