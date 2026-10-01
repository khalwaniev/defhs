# Stage 1 dual-GPU execution plan

Mission: `RS-DEFHS-SYSTEM-IMPLEMENTATION-001`

## Reason

The v2 runner was verified to bind all neural work to `cuda:0` and to execute the two independent frozen representation families sequentially. When Kaggle's T4 ×2 accelerator is available, this leaves one accelerator idle.

## v3 execution design

Explicit accelerator request: `NvidiaTeslaT4`.

Runtime invariant: `torch.cuda.device_count() >= 2`. The run aborts before model construction if this is false.

Assignments:

- `emotion2vec_base@v2.0.4` → `cuda:0`
- `facebook/wav2vec2-xls-r-300m@1a640f...080a54` → `cuda:1`

Each family runs in its own spawned process and writes independent frame/pooled/result artifacts. The parent waits for both workers, rejects any non-zero exit code, then performs the unchanged V-B/V-A downstream evaluation.

## Unchanged scientific authority

- V-B primary / V-A secondary;
- exact frozen model identities;
- exact mean+std pooling;
- exact L2 logistic and calibrated RBF heads;
- no Vesper substitute;
- WavLM remains deferred;
- no PEFT before frozen-OOF gate;
- protected validation not queried;
- no Kaggle competition submission.

## Expected effect

This is a compute scheduling change only. It is intended to overlap the two independent encoder extraction workloads; it does not change their outputs by design. Actual speedup is empirical and must be measured from the run logs.
