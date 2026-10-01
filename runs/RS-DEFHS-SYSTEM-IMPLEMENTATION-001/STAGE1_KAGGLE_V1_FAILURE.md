# Stage 1 Kaggle v1 failure report

Mission: `RS-DEFHS-SYSTEM-IMPLEMENTATION-001`

Kernel: `khalwaniev/defhs-rs-system-implementation-frozen-screen`

Version: 1

Status: **ERROR — PRE-EXTRACTION INPUT-ALIAS CARDINALITY DEFECT**

## Exact traceback evidence

The traceback terminates in:

```text
RuntimeError: Expected one canonical DATA_MANIFEST.csv; got [
  /kaggle/input/notebooks/khalwaniev/defhs-ds002-closure/ds002_closure/DATA_MANIFEST.csv,
  /kaggle/input/notebooks/khalwaniev/defhs-ds002-closure/ds002_authority/runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv
]
```

Traceback timestamp: approximately 80.0814 seconds.

## Scientific interpretation

The runner first filters `DATA_MANIFEST.csv` candidates by the frozen canonical SHA256:

`1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469`

Both listed paths survived that filter. Therefore both are byte-identical canonical-authority aliases from the same upstream Kaggle kernel source.

This is not:
- a model failure;
- a GPU failure;
- a dependency failure;
- a validation-authority disagreement;
- a reason to redesign Stage 1.

No pretrained model was constructed before the exception.

## Bounded patch

Replace the incorrect invariant:

> exactly one filesystem path must match

with:

> at least one path must match the exact canonical SHA256.

When multiple matching aliases exist:
1. retain all paths in provenance;
2. deterministically prefer the `/ds002_closure/` copy when present;
3. otherwise choose the lexicographically first matching path;
4. continue only because all accepted aliases already match the same frozen SHA256.

No other Stage-1/2/3 logic is changed.

## Safety

- protected validation queried: **NO**
- Kaggle competition submission made: **NO**
- emotion2vec execution reached: **NO**
- XLS-R execution reached: **NO**
