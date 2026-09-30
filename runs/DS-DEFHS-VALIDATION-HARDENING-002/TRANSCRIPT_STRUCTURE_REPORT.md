# Transcript / Prompt Structure Report

## Closure status

**PENDING REQUIRED HINDI ASR AUDIT.**

The package supplies no transcript, prompt, or script identifiers. The earlier `UNRESOLVABLE` classification reflected unavailable ASR weights in one runtime, not completed prompt-structure evidence.

## Required executed analysis

Canonical executor:

`scripts/run_ds002_asr_prompt_audit.py`

Planned ASR:

`mobiuslabsgmbh/faster-whisper-large-v3-turbo`, with language forced to Hindi (`hi`). The executor resolves and records an immutable model revision at runtime.

For all 1,035 clips it records:

- transcript and normalized transcript;
- decoding segment count;
- average log probability;
- no-speech probability;
- compression ratio;
- detected-language metadata where returned.

Quality is audited objectively using:

- transcript agreement inside the known acoustic duplicate families;
- language/decode probability;
- empty transcript rate;
- confidence distributions.

Prompt structure is then assessed through:

- exact repeated normalized transcripts;
- character n-gram fuzzy similarity;
- prompt-cluster threshold sweep;
- train/test prompt overlap;
- class association.

## Current policy

- No prompt/script grouping is authoritative yet.
- No text-semantic SER branch is authorized by this data-understanding mission.
- Existing duplicate handling remains valid independently of ASR.
- Final closure requires the actual transcript artifact and prompt audit.

Current evidence state for prompt/script families: **not yet classifiable; required ASR audit pending**.
