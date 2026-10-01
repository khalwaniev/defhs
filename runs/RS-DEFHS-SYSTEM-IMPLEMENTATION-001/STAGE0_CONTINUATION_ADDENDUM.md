# Stage-0 continuation addendum — policy unblock and asset clearance

Mission: `RS-DEFHS-SYSTEM-IMPLEMENTATION-001`

Date: 2026-10-01

Parent Stage-0 STOP commit: `efd312c3515acddee143a5398c003471ecd4b885`

## Audit-trail rule

This addendum does **not** replace or reinterpret the original Stage-0 STOP report. The STOP was mechanically correct under the authority available at that time:

`UNKNOWN → STOP / RETURN TO SS`

The continuation path is:

`UNKNOWN → official Rules captured by SS → policy resolution → asset-specific re-audit → execution resumed`

The original files `STAGE0_EXECUTION_AUTHORITY.md` and `STAGE0_RETURN_TO_SS.md` remain unchanged.

## 1. Official competition Rules authority

SS supplied the official Kaggle Competition-Specific Rules capture obtained with:

```bash
kaggle competitions pages \
  dataverse-detecting-emotions-from-hindi-speech \
  --page-name rules \
  --content
```

Relevant section: **5. EXTERNAL DATA AND TOOLS**.

The captured authority states that external data may be used when publicly/equally accessible at no cost or otherwise reasonable under the competition criteria, and specifically states:

> The use of external data and models is acceptable unless specifically prohibited by the Host.

No captured competition-specific rule prohibits pretrained models.

SS resolution:

`COMPETITION_POLICY_COMPATIBILITY = ALLOWED_CONDITIONAL_ON_ASSET_LICENSE_AND_REASONABLE_PUBLIC_ACCESS`

This is not permission for proprietary, inaccessible, unlicensed, or otherwise noncompliant assets.

## 2. emotion2vec base — STAGE0_CLEARED

Execution asset:

- ModelScope identity: `iic/emotion2vec_base`
- ModelScope revision: `v2.0.4`
- access: public / no-cost
- model authority: current ModelScope listing identifies Apache License 2.0
- execution source: **ModelScope**, not the Hugging Face mirror

Revision provenance:

- official project repository: `ddlBoJack/emotion2vec`
- exact official repository commit used for revision provenance:
  `a00c9fef630f88c579ed768a6f9409ceaf45c96f`
- that official README explicitly invokes:
  `model="iic/emotion2vec_base", model_revision="v2.0.4"`
  for both ModelScope and FunASR extraction.

Pinned extraction implementation:

- repository: `modelscope/FunASR`
- revision: `4a84879ae8ca4d2430953b11c49d609217d93988`
- code license at that revision: MIT
- the pinned `Emotion2vec.inference` path loads audio at 16 kHz, applies checkpoint-configured waveform normalization, calls frozen `extract_features`, and exposes frame or utterance granularity.

Deterministic execution contract:

1. resolve `iic/emotion2vec_base` from ModelScope at `v2.0.4`;
2. before extracting any competition representation, record the resolved model cache file inventory and SHA256 of every checkpoint/config file used;
3. abort if the requested revision does not resolve, the model license authority no longer reports Apache-2.0, or the resolved asset differs from the recorded revision;
4. canonicalize audio to mono float32 at exactly 16,000 Hz before the model call;
5. use evaluation mode, inference/no-grad mode, fixed deterministic seeds and no stochastic augmentation;
6. cache **frame-level** frozen representations once; apply the common Stage-1 mean+std pooling downstream so the same pooling implementation is used across encoders;
7. do not substitute the Hugging Face mirror if ModelScope acquisition fails.

The post-download SHA256 capture is a provenance assertion on the actually used ModelScope object, not authorization to switch sources.

Status: **STAGE0_CLEARED**.

## 3. Vesper-4 — DEFERRED_UNAVAILABLE

The competition-policy block is removed.

The pinned official code repository remains:

`HappyColor/Vesper@2b62af3e15fbd526fac6d4f1d6fea279c306244d`

Code is Apache-2.0, but no authoritative immutable released Vesper-4 pretrained checkpoint was established.

Status: **DEFERRED_BLOCKED_NO_RELEASED_CHECKPOINT**.

Not authorized:
- WavLM initialization labeled as pretrained Vesper-4;
- training Vesper from scratch;
- Vesper-12 substitution;
- replacement emotion model.

This is an availability defer, not a performance kill.

## 4. XLS-R-300m — STAGE0_CLEARED

Execution asset:

- checkpoint: `facebook/wav2vec2-xls-r-300m`
- immutable revision:
  `1a640f32ac3e39899438a2931f9924c02f080a54`
- checkpoint/model-card license: Apache-2.0
- access: public / no-cost
- canonical sample rate: 16 kHz
- feature-extractor normalization: enabled
- attention-mask return: enabled

The prior asset evidence was re-read after the global policy unblock and no inconsistency was found.

Status: **STAGE0_CLEARED**.

## 5. WavLM-large — DEFERRED_TERMS_UNRESOLVED

Candidate identity remains:

`microsoft/wavlm-large@c1423ed94bb01d80a3f5ce5bc39f6026a0f4828c`

The global competition-policy block is removed. The pre-existing checkpoint-weight-term ambiguity is not resolved to the required authority standard.

Status: **DEFERRED_BLOCKED_WEIGHT_TERMS_UNRESOLVED**.

This defer does not block XLS-R and does not authorize another generic model.

## 6. Reduced bounded architecture

SS explicitly authorizes continuation with:

- emotion2vec base frozen lane;
- Vesper-4 deferred/unavailable;
- XLS-R-300m frozen generic/multilingual lane;
- WavLM-large deferred on weight terms;
- existing FULL_RBF_SVM retained only under the original complementarity rule;
- eGeMAPS/text conditional exactly as previously authorized.

No replacement for Vesper or WavLM is permitted.

## 7. Frozen Stage-1 data authority readback

Without opening the protected fold file, the following canonical Drive artifacts were read back:

| Artifact | Drive file ID | SHA256 |
|---|---|---|
| `VALIDATION_VB_FOLDS.csv` | `1AQxmJTSA5SaawTiw0AVJAUk1su7ICoRK` | `87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b` |
| `VALIDATION_VA_FOLDS.csv` | `1DnSBTewpadR1hzof9Hb_Es9gt16_9N-4` | `dcee356b0a66cb73c506bb71a6c57962227d6d0474efd3e4d6c404168308f3d1` |
| `DATA_MANIFEST.csv` | `1K72qAYnm3k1vHLyTQK6hZ-A30sJGFs3A` | `1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469` |
| `RETRIEVAL_MAP_FINAL.csv` | `1JsnJCryDsbOV7GWUAkzi4cCS7uZ3WGcx` | `e08f7d06c13d64a1d365d7ae6fa741d6e831dea8816de6663d4a9c0eb113d2a7` |

These hashes are taken from the existing canonical artifact inventory. V-B remains primary; V-A secondary; retrieval remains separate.

## 8. Continuation decision

Stage 0 is now **CLEARED FOR THE AVAILABLE BOUNDED ARCHITECTURE**.

Proceed to Stage 1. Do not return to SS merely because Vesper and WavLM remain deferred.

Safety state:
- **PROTECTED VALIDATION NOT QUERIED**
- **KAGGLE SUBMISSION NOT MADE**
- GPU model compute used through this addendum: **0 accelerator-hours**
