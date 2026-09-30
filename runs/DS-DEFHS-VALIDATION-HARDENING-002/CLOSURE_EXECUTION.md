# DS-002 Closure Execution

This file defines the remaining bounded execution. It is not permission to restart EDA or begin SER modeling.

Install the pinned closure environment:

```bash
python -m pip install -r requirements/ds002_closure.txt
```

Use the canonical extracted SRCASW-BhavVaani directory as `DATA_ROOT` and the canonical DS-002 run directory as `OUT`.

Execute in order:

```bash
python scripts/run_ds002_speaker_ecapa_audit.py \
  --data-root "$DATA_ROOT" \
  --out "$OUT"

python scripts/run_ds002_asr_prompt_audit.py \
  --data-root "$DATA_ROOT" \
  --out "$OUT" \
  --device cuda \
  --compute-type float16

python scripts/run_ds002_opensmile_egemaps_audit.py \
  --data-root "$DATA_ROOT" \
  --out "$OUT"

python scripts/run_ds002_latent_regime_joint_audit.py \
  --out "$OUT"
```

The speaker and ASR scripts resolve an immutable Hugging Face revision before downloading the model and record that resolved revision in their manifests.

Do not run candidate SER models on `VALIDATION_VP_PROTECTED_FOLDS.csv` during this closure.

After execution:

1. verify every output row count / checksum;
2. upload heavy embeddings/transcripts/features to `/DEFHS/ds_validation_002/`;
3. record Drive file IDs, size, SHA-256, producer commit, model revision;
4. update the speaker/transcript/acted-spontaneous/source/shift reports;
5. decide whether V-C is reliable enough to freeze;
6. only then reissue the unknown register, certificate, final validation authority, and return to SS.

No main RS modeling is authorized by this file.
