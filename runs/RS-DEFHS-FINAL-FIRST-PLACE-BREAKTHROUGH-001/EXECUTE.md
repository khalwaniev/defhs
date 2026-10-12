# Immediate CPU handoff

No GPU or competition submission is required. Run from your DEFHS WSL checkout.
Use a separate worktree so Sol's branch and working files remain unchanged:

```bash
git fetch origin rs/final-first-place-breakthrough-001-astra
git worktree add ../defhs-astra-temporal origin/rs/final-first-place-breakthrough-001-astra
cd ../defhs-astra-temporal
python3 -m venv .venv-temporal
.venv-temporal/bin/python -m pip install numpy==2.3.5 pandas==2.2.3 h5py==3.15.1 scipy==1.17.0 scikit-learn==1.8.0 joblib==1.5.3 threadpoolctl==3.6.0
mkdir -p work/temporal_input
rclone copyto 'gdrive:DEFHS/rs_system_implementation_001/kaggle_v3_frozen_screen/rs_defhs_system_implementation_001/emotion2vec_base_frames.h5' work/temporal_input/emotion2vec_base_frames.h5
rclone copyto 'gdrive:DEFHS/rs_system_implementation_001/kaggle_v3_frozen_screen/rs_defhs_system_implementation_001/emotion2vec_base_meanstd.npz' work/temporal_input/emotion2vec_base_meanstd.npz
.venv-temporal/bin/python scripts/final_temporal_reduce.py --frames work/temporal_input/emotion2vec_base_frames.h5 --meanstd work/temporal_input/emotion2vec_base_meanstd.npz --out work/TEMPORAL_TRAIN826.npz
```

If the authenticated files already exist locally, use their actual paths and
skip the two rclone transfers. `gdrive:` is the historical project rclone remote;
if your configured remote has a different name, change only that remote prefix.
Do not set up a new public share.

Return `work/TEMPORAL_TRAIN826.npz` and `work/TEMPORAL_TRAIN826.json`. They contain
only compact, label-blind training windows. RS can execute the nested CPU test
with the already authenticated original D and E inputs. The original 459.6 MB
cache exceeds RS's connected-download limit; exporting this small derivative
resolves that technical limit without repeating encoder inference.

The evaluator, full CPU notebook, and integrity tests are added in the next
checkpoint. This early handoff deliberately lets reduction run immediately;
it is not a scientific GO or a result claim.

For SS's account check, use the existing authenticated Kaggle CLI:
`kaggle quota`, then `kaggle competitions submissions COMP` and
`kaggle competitions submission-limits COMP`, replacing COMP with the official
slug in `configs/competition.yaml`. These read-only checks are separate from
this experiment. No submission command belongs in this package.
