# RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001 — one-shot execution handoff

**Status:** `EXPLORATORY_IMPLEMENTATION_PUSHED__AUTHENTIC_DATA_UNAVAILABLE_IN_THIS_SESSION`. No 28F model has been fitted here. Scientific hypothesis UNTESTED; neither rejection nor promotion is justified. No Kaggle submission or protected evaluation.

## Authority and external input integrity

- Starting parent: `e82f6fe63f12ca99af2e128f72415e0dac0a31a9`.
- Original D archive SHA256: `fb76b00dcc145c3ea7df6046ed7da594ff3b1ebd4cb52848184902876af61839`.
- Original E evidence ZIP SHA256: `dc0393a55644448fa85ddc142d7cf5a3c8877d90125d0a0ad9e5dff0734574bf`.
- New 826-row Qwen14 semantic ZIP SHA256: `cd1481baea48c73fff0fe99c1da027f6b65d84e271b401d02dfec285fd4f8789`.
- Authenticated 826-row five-likelihood CSV SHA256: `66d01f825c9be4142452e6f04fb921dd8ece6c8f82aac5e0768a9941c0e4e788`.
- Frozen V-B fold SHA256: `87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b`.
- Optional authentic prompt assignments SHA256: `458712cfee51e0cf65ef57d1a0deb8f81dcb70e4ecfe6ebfc73220f3aefac005`.
- Original E PRIMARY_CV = `0.8774091527555827`. Original Q960-606 failure versus D = `-0.03367392841077055`; the failure is NOT overturned.

## Exact WSL launch

```bash
cd /home/fikar/zingle/defhs-semantic-information
git switch rs/final-semantic-information-001
git pull --ff-only
PY="$PWD/work/ss_d_replay_exact_py3135/bin/python"
test -x "$PY" || { echo "Original CPU environment missing"; exit 2; }
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONNOUSERSITE=1 \
"$PY" scripts/auto_run_semantic_info_oneshot.py \
  --scan-root /home/fikar/zingle \
  --scan-root /mnt/c/Users/fikar/Downloads \
  --out work/rs_final_semantic_information_one_shot
```

If the original authenticated files exist elsewhere, add their directory with another `--scan-root /path`. The launch helper matches the **exact four original SHA256 hashes** and will stop rather than substitute any archive. It does not alter or upload the original data. If the probability column names are not unambiguous, the evaluator will stop BEFORE model fitting and print the actual CSV columns; re-invoke with `--prob-columns COL_ANGRY COL_HAPPY COL_NEUTRAL COL_SAD COL_UNCLEAR`, using the observed names and class order.

## Outputs and interpretation

- `work/rs_final_semantic_information_one_shot/ARTIFACT_DISCOVERY.json`: authenticated file locations or exact missing inputs.
- `work/rs_final_semantic_information_one_shot/RESULT.json`: all 3 requested contrasts, pooled and fold F1, per-class metrics, confusion matrices, corrections/breakages, HARD316, Q960-606, candidate margins, numerical drift, environment, and uncertainty status.
- `work/rs_final_semantic_information_one_shot/PAIRED_PRIMARY_OOF.csv`: all 826 authoritative IDs, original 23F reference, local 23F and 28F probabilities/predictions, cohort masks, margins.
- `RESULT.json` is creation-guarded: a second 23F/28F experiment cannot silently overwrite it.
- If the 656 authentic dependency components are available through the genuine prompt-assignment CSV, the evaluator uses the original Evidence implementation for 2,000 paired draws. Otherwise explicitly reports uncertainty INCOMPLETE. Do not reconstruct components from a newly chosen rule.
- Local positive results are **EXPLORATORY**, not a historical frozen certification. Independently examine E reference/local drift and Q960 stress, and request SS approval before target209 inference or Kaggle submission.

## Publish executed evidence after successful result

```bash
cd /home/fikar/zingle/defhs-semantic-information
test -f work/rs_final_semantic_information_one_shot/RESULT.json || exit 2
cp work/rs_final_semantic_information_one_shot/RESULT.json \
  runs/RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001/ONE_SHOT_RESULT.json
cp work/rs_final_semantic_information_one_shot/PAIRED_PRIMARY_OOF.csv \
  runs/RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001/ONE_SHOT_PRIMARY_OOF.csv
git add runs/RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001/ONE_SHOT_RESULT.json \
  runs/RS-DEFHS-FINAL-SEMANTIC-INFORMATION-001/ONE_SHOT_PRIMARY_OOF.csv
git commit -m "Record one-shot semantic information paired nested evaluation"
git push origin rs/final-semantic-information-001
```

Do not publish outputs after a failed hash, data, or model fit check. SS review is required for every promotion or submission decision.
