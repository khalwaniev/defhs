#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
KDIR="$ROOT/kaggle/rs_defhs_target209_ast_recovery_001"
EXECUTOR="$ROOT/scripts/run_rs_defhs_target209_ast_recovery_001.py"
COPIED="$KDIR/run_rs_defhs_target209_ast_recovery_001.py"

test -f "$EXECUTOR"
test -f "$KDIR/run.py"
test -f "$KDIR/kernel-metadata.json"

cleanup() {
  rm -f "$COPIED"
}
trap cleanup EXIT

cp "$EXECUTOR" "$COPIED"
python -m py_compile "$COPIED" "$KDIR/run.py"

echo "KAGGLE_PUSH_DIR=$KDIR"
kaggle kernels push -p "$KDIR"
echo "KAGGLE_KERNEL=khalwaniev/defhs-target209-ast-recovery-001"
echo "NEXT: kaggle kernels status khalwaniev/defhs-target209-ast-recovery-001"
