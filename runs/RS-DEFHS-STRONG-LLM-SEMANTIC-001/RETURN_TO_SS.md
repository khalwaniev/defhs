# Return to SS — RS-DEFHS-STRONG-LLM-SEMANTIC-001

**Disposition: MODEL_ACCESS_BLOCKED — SCIENTIFIC QUESTION UNRESOLVED.**

The selected stronger LLM has not produced a single prediction. This is not a
negative semantic-model result. A reproducible train-only execution package is
prepared under the user's explicit external-execution fallback. No fusion or
new submission candidate was made. No Kaggle submission was made.

## Urgent competition state (live browser observation, 2026-10-10)

- Deadline: **2026-10-12 18:30 UTC = 2026-10-13 01:30 WIB**. About 50 h 45 min
  remained at the user's 2026-10-10 22:45 WIB request.
- Live public leader score: **0.96544** (three teams).
- Account `khalwaniev`: **0.80549, rank 30, four entries**, displayed last entry
  approximately five days ago. These are public observations, not account receipts.
- Live rules: maximum **five submissions/day**, up to **two final submissions**.
  Remaining submissions today, exact submitted files/models, and final selections
  are **UNKNOWN**, because this browser is signed out and the execution environment
  has no Kaggle CLI or credentials. Four lifetime entries is not today's quota.
- The canonical System C report says no submission was made by that mission.
  Its prepared candidate is byte-verified at SHA-256
  `8ab7c5dc291cd9d1223283245fb62130b03bf728f764c5eeedf9d2915153e2a8`.
  A later user submission is possible and cannot be excluded. **Do not assume C
  has been submitted, and do not infer its public score from the account's best.**

Run the supplied account-status script now. If the receipt remains ambiguous,
retrieve the specific submission using `kaggle competitions submission REF`
and its original uploaded file; compare exact IDs/labels or bytes with the
canonical C candidate. Do not upload another copy merely to resolve identity.
Any actual submission still needs SS/user approval.

## Verified existing comparison

| Evidence | Population | Four-class macro-F1 | Status |
|---|---:|---:|---|
| Qwen3-8B, abstentions counted as errors | 826 | 0.5172141900 | Recomputed from committed semantic-label rows |
| Qwen3-8B, covered rows only | 467 | 0.7280251225 | Recomputed; coverage 56.54%, not a full-population result |
| System C | 826 | 0.8135577912 | Verified canonical aggregate; row-level OOF unavailable |
| Selected Opus 4.6 | 0 evaluated | Not measured | Missing API credential |
| C + stronger semantics | 0 evaluated | Not measured | Conditional stage not entered |

| Class | Qwen all-826 F1, abstentions penalized | Canonical System C F1 |
|---|---:|---:|
| angry | 0.2786885246 | 0.8487804878 |
| happy | 0.5652173913 | 0.8351063830 |
| neutral | 0.6418604651 | 0.7749419954 |
| sad | 0.5830903790 | 0.7954022989 |

Qwen supplies 350 correct predictions and 359 abstentions among 826 clips.
System C's canonical confusion matrix has 671 correct predictions / 155 errors,
including 29 neutral-to-sad and 20 sad-to-neutral. New-LLM corrections/breakages
versus C cannot be calculated before new inference and recovery of C's OOF rows.
Do not subtract PRIMARY_CV from public LB as if these were matched test sets.

## Transcripts

Recovered original ASR_TRANSCRIPTS.csv with exact SHA-256
`a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01`.
Its Id/text content exactly matches the previously committed Qwen runner payload.
ASR: `mobiuslabsgmbh/faster-whisper-large-v3-turbo`, revision
`0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf`, forced Hindi.
All 1,035 rows are present, including 826 train and 209 test; zero empty texts.
The train-only package has 711 distinct exact strings. Median text length is 27
characters; maximum is 182. Three rows have average ASR log probability below -1.
These are mechanical flags, not a transcription-accuracy estimate.

The language was forced, so high Hindi language probability is not evidence of
word-perfect transcription. No human reference or WER exists in the recovered
evidence. A small uncorrected text inspection found apparent ASR errors. No new
transcription or label-guided correction was performed. One exact training-text
group has conflicting labels (three rows); this proves at least a small
text-only ambiguity but does not estimate a generalization ceiling.

## Model choice and targeted research

Selected **Claude Opus 4.6 (`claude-opus-4-6`)**, not a model sweep. The official
MILU table reports **92.4% Hindi accuracy** for Opus 4.6 with adaptive max effort.
This supports Hindi understanding, not Hindi speech-emotion accuracy. The chosen
run uses high effort and a fixed token limit; benchmark configuration differs.
Opus is a substantially stronger general-language candidate than the existing
8B model; superiority on this task remains the experiment's hypothesis.

The provider states that the dateless 4.6 model ID is a pinned snapshot. It is
currently active; standard input/output prices are $5/$25 per million tokens.
The run defaults to a $10 accounting stop and records actual token usage. This
budget is not guaranteed sufficient; stop if access, cost or deadline fails.
The latest model label was not the selection criterion: a stable version and
explicit Hindi evaluation support this bounded test without a broad search.

The live competition rules permit external models subject to reasonable access
and minimal cost, and explicitly contemplate small LLM subscriptions. This
supports a small API experiment; it is not an organizer ruling on this account.
The model is proprietary API access, not an open-weight checkpoint. No API key,
account credit, regional eligibility or provider inference access is verified
for the user. No competition transcript was sent to the API in this execution.

Primary sources inspected:

- https://www.kaggle.com/competitions/dataverse-detecting-emotions-from-hindi-speech
- https://www.kaggle.com/competitions/dataverse-detecting-emotions-from-hindi-speech/rules
- https://www.kaggle.com/competitions/dataverse-detecting-emotions-from-hindi-speech/leaderboard
- https://www-cdn.anthropic.com/78073f739564e986ff3e28522761a7a0b4484f84.pdf (Table 2.19.2.A, PDF page 42)
- https://platform.claude.com/docs/en/models/opus-4-6/overview
- https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions
- https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- https://platform.claude.com/docs/en/build-with-claude/token-counting

Qwen3's official technical report/model card and current Gemini documentation
were inspected only for feasibility. No alternate model was selected or run.

## Exact external execution (configured WSL; no GPU required)

Use an isolated worktree, preserving any active checkout:

```bash
cd /home/fikar/zingle/defhs
git fetch origin rs/strong-llm-semantic-001
git worktree add --detach /home/fikar/zingle/defhs_strong_llm_001 origin/rs/strong-llm-semantic-001
cd /home/fikar/zingle/defhs_strong_llm_001
bash scripts/defhs_strong_llm_status.sh
python3 scripts/defhs_strong_llm.py preflight
```

The inference runner uses only Python's standard library. If this same worktree
already exists from these instructions, enter it instead of creating it again.
For an existing funded Anthropic API account, enter the key privately in the
terminal (never chat, source code or git):

```bash
read -rsp 'Anthropic API key: ' ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY
python3 scripts/defhs_strong_llm.py infer --max-cost-usd 10
unset ANTHROPIC_API_KEY
python3 scripts/defhs_strong_llm.py evaluate
tar -czf /mnt/c/Users/fikar/Downloads/DEFHS_STRONG_LLM_RETURN.tar.gz work/strong_llm_semantic_001 work/strong_llm_status_001
```

Run evaluation only after inference reports completion. If inference stops,
return the failure evidence and completed response journal; do not choose a new
model, change the prompt or infer a scientific failure. The script resumes only
the identical contract and refuses uncertain prior requests. It never submits,
fine-tunes, accesses protected data, or predicts TARGET209.

Return the archive for RS analysis. The first offline evaluation compares Qwen
and the stronger model; paired C analysis/fusion still requires original C OOF
provenance and nested waveform inputs. See PROTOCOL.md for the one conditional
fusion. Do not replace it with a leaky second split of ordinary C OOF features.

## Compute, checks, and SS recommendation

Consumed here: **0 GPU-hours; 0 LLM inference requests; 0 API tokens; $0 API
spend**. Only lightweight CPU provenance/metric replay and package checks ran.
Four offline scientific-contract tests passed (abstention accounting, paired
counts, input isolation, wrong-model/truncation rejection). These are not live
API tests. The actual inference command stopped with
`MODEL_ACCESS_BLOCKED: ANTHROPIC_API_KEY is not set` before network inference.

Recommendation: immediately establish the submitted-model ledger and final
selections; then execute this single test only if the selected API is accessible
within the remaining budget/time. Existing C versus the fixed waveform pair
already demonstrates useful lexical information (+0.036742 PRIMARY_CV). Whether
deeper understanding adds enough further information is **not yet known**.
Do not promise a 0.96 system, interpret an environment block as a negative model
result, or displace System C using unmeasured stronger-model predictions.
