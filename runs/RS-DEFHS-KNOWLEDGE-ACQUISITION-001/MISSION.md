ROLE: RESEARCH SCIENTIST — KNOWLEDGE ACQUISITION

MISSION:
RS-DEFHS-KNOWLEDGE-ACQUISITION-001

This is an EXECUTION / KNOWLEDGE-ACQUISITION mission for the Kaggle competition:

dataverse-detecting-emotions-from-hindi-speech

Project:
DEFHS — Hindi Speech Emotion Recognition

Your mission is NOT to start serious model experimentation yet.

Your mission is to construct a rigorous, decision-useful, provenance-verified
knowledge warehouse for the later modeling RS.

You must:

1. reread and re-inspect the true current DEFHS project state;
2. audit the attached Deep Research discovery manifest;
3. verify/correct every useful source;
4. independently search for important missing evidence;
5. legally acquire the useful papers, repositories, model documentation,
   supplementary material, and other decision-relevant artifacts;
6. preserve heavy artifacts in Google Drive;
7. preserve manifests, provenance, licenses, checksums, scripts, and scientific
   interpretation in GitHub;
8. return a complete acquisition closure packet to SS.

Do not treat the attached Deep Research report as unquestionable truth.
It is a candidate discovery inventory.

======================================================================
GOVERNING AUTHORITIES
======================================================================

Canonical repository:

khalwaniev/defhs

Canonical branch:

main

Current canonical Git authority:

78a61ade6a86de023af1862485096cffb0109ef0

Current active working branch:

rs/knowledge-discovery-001

At mission start, main and rs/knowledge-discovery-001 are expected to be
identical at the SHA above.

IMPORTANT BRANCH POLICY:

The user wants exactly TWO live remote branches:

- main
- one active mission branch

Do NOT create a third remote branch.

For this acquisition mission, continue using the existing
rs/knowledge-discovery-001 branch unless the user explicitly authorizes a
branch rename/consolidation.

Governing workflow:

WORKFLOW.md

Read it in full before execution.

At minimum, also reread completely:

- docs/PROJECT_STATE.md
- runs/DS-DEFHS-VALIDATION-HARDENING-002/FINAL_VALIDATION_AUTHORITY.md
- runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_UNDERSTANDING_CERTIFICATE.md
- runs/DS-DEFHS-VALIDATION-HARDENING-002/OFFICIAL_COMPETITION_CONTEXT.md
- runs/DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001/
  POST_REDTEAM_VALIDATION_AUTHORITY.md
- runs/DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001/
  POST_REDTEAM_DATA_UNKNOWN_REGISTER.md
- runs/DS-DEFHS-CORRELATED-ALLOCATION-SOURCE-STRESS-PATCH-001/
  FINAL_PATCH_RETURN_TO_SS.md
- relevant DS-001 / DS-002 / adversarial artifacts needed to understand
  the data and validation regime.

Do not infer the project state from this prompt when GitHub can verify it.

======================================================================
CURRENT SCIENTIFIC STATE THAT MUST BE VERIFIED
======================================================================

Do not proceed until the repository confirms approximately the following:

- supplied package authority:
  826 train + 209 test = 1,035 clips;
- organizer prose says 1,036, but the supplied package has 1,035;
- competition labels are:
  angry / happy / neutral / sad;
- official metric is macro-F1;
- final leaderboard score combines:
  0.40 * public + 0.60 * private;
- those weights do NOT establish hidden row fractions;
- V-B is the PRIMARY model/representation-selection authority;
- V-A is SECONDARY competition-mimic / retrieval-aware;
- V-D is diagnostic recording/source-format stress;
- authoritative V-C remains rejected;
- Q128/Q960 are diagnostic stress views only;
- correlated-allocation analysis is a secondary leaderboard-risk envelope;
- deterministic duplicate retrieval covers 77 groups / 78 test clips;
- protected seed 20261001 remains untouched and confirmation-only;
- final validation verdict is PATCH_AND_FREEZE.

Do not redesign validation during this mission.

Do not query protected candidate performance.

Do not make leaderboard submissions.

======================================================================
GOOGLE DRIVE AUTHORITY
======================================================================

Canonical DEFHS Drive root:

/DEFHS/

Current verified Drive folder ID:

1Spi0YOSIbOth6Av801b0w9zKbNAqle94

At mission start, re-inspect this folder yourself.

Current known top-level contents include:

- /DEFHS/raw/
- /DEFHS/competition_extracted/
- /DEFHS/ds_validation_002/

Do NOT assume this remains complete; inspect it live.

Create the knowledge warehouse only after checking for an existing equivalent
folder to avoid duplication.

Preferred structure:

/DEFHS/knowledge/
    papers/
    surveys/
    theses/
    repositories/
    model_cards/
    checkpoint_metadata/
    datasets/
    supplements/
    competition_solutions/
    pointer_only/
    manifests/

Heavy/binary artifacts belong in Drive.

GitHub should remain the canonical scientific/provenance control layer.

======================================================================
ATTACHED DEEP RESEARCH MANIFEST
======================================================================

I am attaching:

DEFHS_KNOWLEDGE_SOURCE_MANIFEST.md

generated by Deep Research.

Read it completely before acquisition.

It contains candidate records DEFHS-KNOW-0001 ... DEFHS-KNOW-0036.

It is useful discovery evidence, NOT final authority.

Known issues you must independently resolve include:

A. BHAVVANI / SRCASW-BHAVVAANI PROVENANCE

The manifest describes:

1. BhavVani from Goel et al. / CAMuLeNet:
   approximately 8,734 Hindi TV-dialogue utterances, seven emotions;

and separately:

2. the Kaggle/DataVerse SRCASW-BhavVaani competition corpus:
   organizer prose ~1,036 clips, acted + spontaneous.

Do NOT assume these are the same corpus, a direct subset, or derived from one
another without documentary or empirical evidence.

Our supplied competition package is 1,035 clips and operationally has only:

angry / happy / neutral / sad.

Produce an explicit provenance reconciliation.

Classify the relationship using evidence, e.g.:

- VERIFIED SAME SOURCE
- VERIFIED DERIVATIVE
- PLAUSIBLE BUT UNVERIFIED
- DISTINCT
- UNRESOLVED

Do not invent provenance.

B. MANIFEST SOURCE QUALITY

Several entries are placeholders or families rather than immutable sources,
for example:

- facebook/wav2vec2-large-*
- facebook/hubert-*
- microsoft/wavlm-*
- XLS-R
- MMS
- SenseVoice
- generic Kaggle-notebook references
- “Any standard SER paywalled papers”

Replace vague entries with exact sources where possible:

- exact paper;
- exact repository;
- exact model/checkpoint ID;
- exact revision/tag/commit;
- exact URL;
- exact license;
- exact publication metadata.

Delete or mark non-sources/duplicates appropriately.

C. LICENSE CLAIMS

Do not accept phrases such as:

- “likely Apache”
- “MIT-like”
- “fair use by HuggingFace”
- “research use likely”

as final license determinations.

Verify licenses from authoritative sources.

If a license remains unclear:

LICENSE_STATUS = UNRESOLVED

and do not mirror/distribute the asset merely because it is downloadable.

D. GITHUB ACCESS

The Deep Research report states that khalwaniev/defhs was inaccessible.

That statement is stale/incorrect for this mission.

You have connected GitHub access.

Use the live repository and current SHA as project authority.

E. COVERAGE IS TOO THIN

The discovery report is only a seed.

Search aggressively for missing, decision-relevant evidence through
2026-10-01.

======================================================================
MANDATORY RESEARCH EXPANSION
======================================================================

Independently search the literature and implementation ecosystem for
decision-relevant SER evidence, especially:

- Hindi speech emotion recognition;
- Indian-language SER;
- multilingual SER;
- low-resource SER;
- small-n SER;
- unseen-speaker generalization;
- acted vs spontaneous domain shift;
- noisy / source heterogeneous SER;
- foundation models specialized for emotion;
- emotion2vec;
- emotion2vec+;
- SenseVoice and relevant emotion heads;
- WavLM;
- wav2vec 2.0;
- XLS-R;
- HuBERT;
- MMS;
- UniSpeech / UniSpeech-SAT;
- data2vec;
- Whisper / Whisper encoders;
- multilingual speech foundation models released in 2025–2026;
- layer weighting / layer selection;
- temporal pooling;
- attentive statistics pooling;
- mean/max/statistics pooling;
- frozen encoder + shallow head;
- partial unfreezing;
- discriminative learning rates;
- gradual unfreezing;
- LoRA;
- adapters;
- PEFT;
- low-data fine-tuning;
- parameter-efficient SER;
- eGeMAPS + SSL fusion;
- acoustic + SSL fusion;
- audio + transcript/text fusion;
- ASR transcript fusion;
- lexical-emotional cues;
- data augmentation for SER;
- SpecAugment;
- noise/reverb augmentation;
- speed/pitch perturbation;
- mixup/manifold mixup where appropriate;
- class imbalance;
- focal/class-balanced losses where supported;
- pseudo-labeling;
- semi-supervised SER;
- self-training;
- test-time augmentation where scientifically valid;
- ensembling;
- stacking;
- calibration;
- cross-lingual transfer;
- external SER datasets;
- domain adaptation;
- retrieval / near-duplicate handling where relevant;
- macro-F1 optimization and model-selection stability.

Search important 2025–2026 work explicitly rather than relying on older
surveys.

Prioritize:

1. directly applicable evidence;
2. strong experimental papers;
3. official implementations;
4. released checkpoints;
5. reproducible competition solutions;
6. authoritative surveys/meta-analyses.

Do not inflate the warehouse with low-value SEO/blog repetition.

======================================================================
SOURCE VERIFICATION CONTRACT
======================================================================

Every canonical source record should, where applicable, include:

- stable source ID;
- title;
- authors/organization;
- year;
- venue;
- source type;
- DOI;
- canonical publication URL;
- arXiv/OpenReview/ACL/ISCA URL if applicable;
- official GitHub URL;
- exact Git commit/tag/release when relevant;
- Hugging Face / ModelScope model or dataset ID;
- exact model revision if available;
- dataset name;
- language(s);
- Hindi relevance;
- emotion classes;
- speaker protocol;
- acted/spontaneous status;
- evaluation protocol;
- metrics;
- macro-F1/UAR/WA distinction;
- implementation availability;
- checkpoint availability;
- training data;
- model size if useful;
- license;
- access restrictions;
- commercial-use restriction if any;
- redistribution permission;
- acquisition status;
- local/Drive artifact path;
- SHA256 for downloaded artifacts;
- source relationship / duplicate family;
- DEFHS relevance;
- evidence tier;
- unresolved uncertainties.

Never convert uncertainty into fact.

======================================================================
ACQUISITION POLICY
======================================================================

Acquire all decision-useful material that can be obtained legally and
reproducibly.

For PAPERS:

Prefer, in order:

- publisher-authorized open PDF;
- arXiv / ACL Anthology / ISCA / institutional repository;
- author manuscript;
- other legitimate open-access copy.

Do NOT bypass:

- paywalls;
- authentication;
- access controls;
- robots protections;
- license restrictions.

If only paywalled:

record metadata + canonical pointer + DOI + access status.

Do not fabricate a PDF.

For CODE:

Prefer official repositories.

Record:

- repository URL;
- exact commit SHA;
- license;
- relevant release/tag.

For important repositories, preserve a reproducible snapshot or archive in
Drive if legally permissible and reasonably sized.

Do not mirror enormous irrelevant repository histories blindly.

For MODEL CHECKPOINTS:

Do NOT automatically copy multi-gigabyte weights into Drive simply because
they exist.

For each checkpoint record:

- exact ID;
- revision;
- model card;
- license;
- size;
- source;
- checksum if acquired;
- whether the actual weights are necessary for the subsequent experiment.

Acquire weights only when:

- licensing permits;
- size is reasonable relative to expected use;
- the checkpoint is sufficiently high priority;
- mirroring adds real reproducibility value.

Otherwise preserve authoritative metadata and immutable pointers.

For DATASETS:

Do not download external datasets blindly.

First verify:

- license;
- terms;
- redistribution;
- competition compatibility;
- actual relevance.

Store metadata/pointers when redistribution is restricted.

Do not assume that an external dataset is permitted for the Kaggle
competition merely because it is public.

======================================================================
GOOGLE DRIVE WAREHOUSE
======================================================================

Create a clean, deterministic warehouse.

Suggested naming:

papers/
  DEFHS-KNOW-XXXX__firstauthor_year__short-title.pdf

repositories/
  DEFHS-KNOW-XXXX__owner_repo__<commit>.zip

model_cards/
  DEFHS-KNOW-XXXX__provider_model__MODEL_CARD.md

checkpoint_metadata/
  DEFHS-KNOW-XXXX__provider_model__metadata.json

pointer_only/
  DEFHS-KNOW-XXXX__POINTER.md

manifests/
  KNOWLEDGE_MANIFEST.csv
  SOURCE_PROVENANCE.jsonl
  LICENSE_REGISTER.csv
  CHECKSUMS_SHA256.txt

Avoid duplicate bytes when several manifest records refer to the same
underlying artifact.

======================================================================
GITHUB DELIVERABLES
======================================================================

Use the existing active branch:

rs/knowledge-discovery-001

Do NOT touch main directly during acquisition.

Create:

runs/RS-DEFHS-KNOWLEDGE-ACQUISITION-001/

with at minimum:

MISSION.md

DEFHS_KNOWLEDGE_SOURCE_MANIFEST_ORIGINAL.md
    exact preserved copy of the attached discovery manifest

KNOWLEDGE_MANIFEST.csv
    normalized final source inventory

SOURCE_PROVENANCE.jsonl
    machine-readable provenance chain

ACQUISITION_LOG.jsonl
    every acquisition attempt and disposition

LICENSE_REGISTER.csv
    verified license/access/redistribution state

CHECKSUMS_SHA256.txt
    every downloaded artifact

POINTER_ONLY_REGISTER.md
    paywalled / inaccessible / restricted / intentionally-not-mirrored items

SOURCE_COVERAGE_REPORT.md
    what evidence families are covered

BHAVVAANI_PROVENANCE_RECONCILIATION.md
    explicit competition-vs-Goel/BhavVani provenance analysis

DUPLICATE_SOURCE_MAP.csv
    paper / repo / checkpoint / dataset relationships and duplicated records

MISSING_EVIDENCE_REGISTER.md
    remaining important holes after independent expansion

WAREHOUSE_INDEX.md
    map of GitHub records to Google Drive artifact locations

FINAL_RETURN_TO_SS.md

Also add a reproducible acquisition script where practical, e.g.:

scripts/run_rs_defhs_knowledge_acquisition_001.py

or an equivalent small set of scripts.

Do not commit large PDFs, model weights, datasets, or repository archives to
GitHub.

Heavy artifacts belong in Drive.

======================================================================
QUALITY GATES
======================================================================

Before declaring COMPLETE, verify all of the following:

- current GitHub scientific authority was reread;
- Drive warehouse contents were inspected, not assumed;
- the original Deep Research manifest was preserved exactly;
- every original DEFHS-KNOW entry has a disposition;
- vague source-family entries were resolved or explicitly left unresolved;
- obvious duplicate records were linked;
- licenses were checked from authoritative sources;
- no paywall/access bypass occurred;
- SHA256 exists for every acquired file;
- Drive paths actually exist;
- GitHub warehouse index points to real Drive artifacts;
- major missing 2025–2026 SER evidence was independently searched;
- Hindi / Indian-language SER coverage was expanded;
- low-data/PEFT coverage was expanded;
- audio-text fusion was searched;
- augmentation/pseudo-labeling was searched;
- cross-lingual transfer was searched;
- ensembles were searched;
- no protected validation performance was queried;
- no validation redesign occurred;
- no model winner was selected;
- no Kaggle submission was made.

======================================================================
EXECUTION BEHAVIOR
======================================================================

Execute, do not merely propose.

Use connected GitHub, Google Drive, and the public web directly when possible.

If a tool limitation prevents an important binary acquisition/upload:

- do not pretend it succeeded;
- identify the exact blocker;
- produce the smallest deterministic WSL command needed;
- use the user's canonical local repository:
  /home/fikar/zingle/defhs
- use the user's existing Drive/rclone workflow where appropriate;
- request only the resulting terminal output needed to resume.

Do not ask the user to manually perform research that you can perform.

Do not stop merely because the Deep Research manifest has gaps.
Closing those gaps is part of this mission.

Do not start serious SER model experimentation during this mission.

======================================================================
FINAL RETURN
======================================================================

Return to SS only when the acquisition is substantially exhausted or a real
access/legal blocker prevents completion.

FINAL_RETURN_TO_SS.md must state:

- verified source count;
- acquired paper count;
- acquired repository count;
- model/checkpoint records;
- external-dataset records;
- pointer-only count;
- unresolved license count;
- Drive warehouse location;
- total acquired bytes;
- all artifact SHA256 status;
- most important newly discovered sources beyond Deep Research;
- corrections made to the original manifest;
- BhavVaani/SRCASW provenance conclusion;
- remaining knowledge gaps;
- whether the warehouse is sufficient to proceed to
  SS-DEFHS-EVIDENCE-SYNTHESIS-001.

The mission should end with one of:

PASS_ACQUISITION_COMPLETE

or

BLOCKED_ACQUISITION_INCOMPLETE

Do not use PASS if major acquisition/provenance/coverage work remains.