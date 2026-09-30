# Workflow for Kaggle Competitions and Research

## Very Important

- Do not hallucinate, drift, wander, or optimize the wrong objective or metric.
- If important information is missing or uncertain, do not guess. Ask for the information, inspect the repository/data, or provide a command to obtain it.
- Avoid unnecessary constraints, complexity, handoffs, and bureaucracy.
- Document every meaningful experiment and run so we do not repeat failures or lose useful discoveries.
- analyzing and inspect kaggle notebook's output should be inside the kaggle , unless local inspection and analysis will more powerfull

## Workers

### rb - repo builder

build repo aat first

### SS — Strategic Scientist

SS is the main scientific decision-maker.

Responsibilities:

- Think deeply about the project and its current state.
- Identify the most important bottleneck.
- Decide the best next action based on scientific evidence, experiments, literature, and first-principles reasoning.
- Allocate time and compute efficiently.
- Decide whether to continue, kill, promote, or redirect a research direction.
- If uncertain, request more evidence rather than guessing.

SS is not only a manager. SS must perform strong scientific reasoning.

Core skills:

- First-principles reasoning
- Analytical reasoning
- Scientific judgment
- Strategic decision-making

### RS — Research Scientist

RS focuses deeply on one specific scientific bottleneck.

Responsibilities:

- Inspect relevant data, code, previous experiments, and literature.
- Generate hypotheses, new methods, and possible breakthroughs.
- Design the cheapest decisive experiment.
- Implement its own ideas whenever practical to avoid communication loss.
- Run, debug, analyze, and document experiments.
- Report important findings and decision points to SS.

RS should have broad capabilities but a narrow mission.

Core skills:

- Fluid reasoning
- First-principles reasoning
- Scientific reasoning
- Modeling
- Experimental design
- Research engineering

For very large literature-acquisition missions, use a separate RS to gather and organize evidence so the bottleneck-focused RS is not overloaded.

If equations are important, use a format that supports them properly, such as LaTeX.

### DS — Data Scientist

DS owns the empirical and validation foundation.

Responsibilities:

- EDA
- Data integrity checks
- Preprocessing
- Leakage and dependency analysis
- Grouping and distribution-shift analysis
- Evaluation metric verification
- Validation design and stress testing

RS may also inspect and analyze data directly. DS exists mainly to maintain an independent and trustworthy understanding of the data and validation system.

Core skills:

- Statistical reasoning
- Logical reasoning
- Causal reasoning when appropriate
- Data analysis
- Validation design

## Scientific Workflow

Default loop:

SS -> identify bottleneck -> RS -> research + hypothesis -> implementation ->
experiment -> analysis -> SS decision

DS becomes involved when the problem concerns data, validation, leakage, grouping, preprocessing, or distribution shift.

RS does not need SS approval for every small experiment within an authorized mission and compute budget.

Return to SS when:

- decisive evidence is obtained;
- the hypothesis fails;
- the main bottleneck appears to be wrong;
- substantially more compute is required;
- validation or data authority needs to change;
- a major model promotion or leaderboard submission is proposed.

## Validation

Validation should approximate the hidden evaluation (private LB) distribution, data-generating process, and official competition metric as closely and defensibly as possible.

Do not optimize validation merely to match the public leaderboard.

Important validation versions should be frozen and documented.

Material changes to validation should be independently checked before becoming the new authority.

## Experiment Discipline

For every meaningful experiment, record at least:

- experiment ID;
- hypothesis;
- baseline;
- change;
- validation;
- configuration;
- Git commit;
- compute used;
- result;
- verdict;
- important artifact locations.

Record failed and neutral experiments as well as successful ones.

Prefer cheap decisive tests before expensive full runs.

## GitHub and Google Drive

### GitHub — Canonical Live Repository

GitHub is the primary source of truth for the live project.

Keep in GitHub:

- source code;
- configs;
- validation definitions;
- tests;
- workflow and project documentation;
- lightweight experiment reports;
- small CSV/JSON/Markdown outputs;
- manifests and pointers to external artifacts.

Important project states should be identified by Git commit SHA.

After meaningful repository changes:

git status
git add <intentional files>
git commit -m "describe the change"
git push

Do not blindly use `git add -A` when large or generated files may be present.

### Google Drive / External Storage

Use Google Drive or other appropriate external storage for large files such as:

- literature PDFs and research materials;
- large datasets;
- model checkpoints;
- large predictions;
- embeddings and tensors;
- large experiment outputs;
- bulky binary artifacts.

Do not duplicate large files inside GitHub unnecessarily.

For important external artifacts, keep a small manifest or pointer inside GitHub containing:

- artifact name or ID;
- storage location;
- size;
- checksum/hash when important;
- producing experiment;
- short description.

GitHub contains the project logic and scientific state.
External storage contains the heavy artifacts.

## Information Management

Keep the repository simple and easy to understand.

Important information should be easy for humans and different LLMs to locate.

Prefer a small number of authoritative files over duplicated or conflicting documentation.

## Kaggle Environment

- Kaggle CLI is available.
- Up to 2 GPU notebooks can run simultaneously.
- Available accelerators may include:
  - 2x T4
  - 1x P100
- CPU notebooks can be used for CPU-heavy work.

Use the cheapest suitable resource.

If a GPU notebook spends most of its time on CPU work, separate the CPU-heavy stage when practical so GPU quota is not wasted.

When using 2x T4, use both GPUs when the workload genuinely benefits from multi-GPU execution. Do not add unnecessary multi-GPU complexity.

## Kaggle CLI Reference

### GPU / TPU quota

kaggle quota

### Search

kaggle search "..."

### Competition

kaggle competitions files COMP
kaggle competitions download COMP
kaggle competitions leaderboard COMP --show
kaggle competitions submissions COMP
kaggle competitions submission REF
kaggle competitions submission-limits COMP
kaggle competitions submit COMP ...
kaggle competitions submission-download ID

### Notebook execution

kaggle kernels push
kaggle kernels status OWNER/NOTEBOOK
kaggle kernels logs OWNER/NOTEBOOK
kaggle kernels logs OWNER/NOTEBOOK --follow
kaggle kernels output OWNER/NOTEBOOK
kaggle kernels pull OWNER/NOTEBOOK

### Dataset

kaggle datasets create
kaggle datasets version
kaggle datasets files OWNER/DATASET
kaggle datasets download OWNER/DATASET

### Inspect personal Kaggle resources

kaggle kernels list --mine
kaggle datasets list --mine

## Local Environment

Repositories are primarily stored in WSL.

Most downloaded files from the browser usually appear in:

C:\Users\fikar\Downloads

Equivalent WSL path:

/mnt/c/Users/fikar/Downloads

## Scientific Decision Discipline

### Objective Lock

Before consequential work, establish:

- the true objective and metric;
- current validation authority;
- current best accepted result;
- current bottleneck;
- protected components;
- evidence required for promotion.

If the work stops serving the true objective, stop the tangent and return to
the bottleneck.

### Experiment Discipline

When practical, compare each experiment against a clearly identified parent
baseline and isolate the meaningful change.

Prefer the cheapest experiment that can produce decisive evidence.

If an apparent improvement may be within experimental noise, confirm it with
appropriate folds, seeds, groups, or stress tests before promotion.

A successful command or completed run is not sufficient evidence by itself.
Verify the scientific or engineering outcome that actually matters.

### Validation Reuse

Frozen validation is protected, but it is not an unlimited optimization oracle.

After many adaptive modelling decisions, treat very small gains cautiously.
Prefer improvements that remain credible across relevant folds, seeds, groups,
or stress tests.

Use stronger confirmation when validation-selection bias becomes a credible
risk.

### Hypothesis Discipline

When several explanations are plausible, use:

OBSERVATION -> COMPETING HYPOTHESES -> DISCRIMINATING TEST ->
EVIDENCE -> BELIEF UPDATE -> NEXT TEST

Prefer experiments that distinguish important hypotheses and have high
decision value.

Seek evidence that could falsify the leading idea, not only evidence that
supports it.

Negative and null results are useful evidence and must influence future
decisions. Do not repeatedly revive a rejected idea without genuinely new
evidence or a materially different mechanism.
