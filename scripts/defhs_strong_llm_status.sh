#!/usr/bin/env bash
# Read-only account check. Never submits or changes final selections.
set -uo pipefail
cd "$(dirname "$0")/.."
out="work/strong_llm_status_001"
comp="dataverse-detecting-emotions-from-hindi-speech"
mkdir -p "$out"
date -u +%FT%TZ > "$out/checked_at_utc.txt"
if ! command -v kaggle >/dev/null 2>&1; then
  echo 'Kaggle CLI is unavailable; use the already-configured WSL environment.' >&2
  exit 1
fi
kaggle competitions submissions "$comp" > "$out/submissions.txt" 2>&1
a=$?
kaggle competitions submission-limits "$comp" > "$out/submission_limits.txt" 2>&1
b=$?
kaggle competitions list -s "$comp" > "$out/competition.txt" 2>&1
c=$?
kaggle quota > "$out/quota.txt" 2>&1
d=$?
python3 - "$out" "$a" "$b" "$c" "$d" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]); keys=['submissions','submission_limits','competition','quota']
status={k:int(v) for k,v in zip(keys,sys.argv[2:])}
(p/'exit_codes.json').write_text(json.dumps(status,indent=2)+'\n')
for k in keys:
    print(k + ': exit=' + str(status[k]))
print('Evidence directory:',p.resolve())
PY
test "$a" -eq 0 && test "$b" -eq 0
