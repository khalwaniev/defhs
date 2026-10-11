# RS-DEFHS-FINAL-BREAKTHROUGH-001 — READ-ONLY Literature Addendum (2026-10-11)

**Disposition:** `NO_SUPERIOR_PROVEN_ALTERNATIVE_TO_ACTIVE_QWEN3_ASR`; prioritize completed train826 ASR GPU output and frozen new-transcript → unchanged Qwen3-14B semantic inference. **No model changes, Kaggle submission, validation refit, or retrieval-map edits.**

Protected authorities: System D commit `69ebbe3ca3c65f82e546fdf1d42e90fa885c8634`; original interrupted Astra `ab2147c7be342a71e67003e2314c7cf104cf6031`; corrected independent Sol continuation branch. System D PRIMARY_CV macro-F1 0.8396460575, PUBLIC_LB 0.88227 (as supplied by SS). Frozen 826 train, 209 test; 78 certified retrieval assignments unchanged. The rejected acoustic probability-coordinate transform remains rejected.

## Sources inspected
1. Chatzichristodoulou et al. (Interspeech 2025): MEDUSA, https://www.isca-archive.org/interspeech_2025/chatzichristodoulou25_interspeech.pdf. Tables 1–3, Fig. 1 and Algorithms 1–2 inspected.
2. Chen et al. (Odyssey 2024): First-place Task 1, https://www.isca-archive.org/odyssey_2024/chen24_odyssey.pdf. Tables 2, 5, 6 and Sections 3–5 inspected.
3. 2025 challenge organizers' report, https://www.isca-archive.org/interspeech_2025/naini25_interspeech.pdf. Baseline, test split, peer-method comparison, Tables 1–2.
4. 2024 organizer's report, https://www.isca-archive.org/odyssey_2024/goncalves24_odyssey.pdf, and https://www.odyssey2024.org/emotion-recognition-challenge.
5. Verified public MEDUSA code, https://github.com/emopodntua/medusa: `train_metacls.py`, `train_deepser.py`, `configs/metacls.yaml`, `configs/deepser.yaml`. Public source/code is not a proof of exact winning checkpoint reproduction.
6. 2025 comparator ABHINAYA: https://www.isca-archive.org/interspeech_2025/dutta25_interspeech.html.

## Transfer-context warning
MEDUSA ranked first among 2025 categorical challenge submissions with **held-out macro-F1 0.4316** (do NOT mistake internal 0.472 for public score). The 2025 dataset comprised **84,260 train, 31,961 development, 3,200 test** utterances across **8** classes with speaker-independent partition, detailed human annotator decisions and valence/arousal/dominance auxiliary scores. These resources are not DEFHS's **826 hard-label-only Hindi utterances**, 4 classes, grouped folds, duplicate/prompt/dtype shifts. Odyssey 2024 first place was **macro-F1 0.3569** and accuracy 0.3732, also an 8-class MSP-Podcast challenge. Scores cannot be compared numerically to DEFHS.

## What ablations actually support

**MEDUSA**
- DeepSER intermediate acoustic/text feature interaction is genuinely different from a posterior-level logistic combiner. Mean over four measured DeepSER configurations: full **0.421**, late-fusion replacement **0.396** (relative -6.31%).
- Use human vote **soft targets**: full **0.421**, one-hot replacement **0.389** (relative -8.23%). Annotator distributions, not class softmax pseudo-targets, supplied the information. DEFHS has no verified equivalent; synthesizing them would not reproduce the hypothesis.
- Remove Manifold MixUp: average **0.409** vs 0.421; no multitask emotional attributes: **0.412** vs 0.421; no balanced second-stage training: **0.416** vs 0.421. Their training recipe used class-weighted stage1 then class-balanced stage2 and multi-attribute MSE supervision.
- Ensemble 14 expert posteriors: **majority 0.439**, **soft 0.439**, single learned metaclassifier **0.471**, six-seed soup **0.472**. Crucially **soup underperforms single (0.445 vs 0.468) on the top-five ensemble**. No universal soup benefit.
- **Reproducibility discrepancy/limitation:** paper describes a *linear* metaclassifier, while public example `configs/metacls.yaml` specifies `mlp_outs: [64]` and **three** result CSVs; `train_metacls.py` constructs linear layers plus ReLU for each layer, including output. The example is not proof of reproducing the winning 14-expert linear model. Do not copy example defaults into DEFHS.

**Odyssey 2024**
- Each expert combines frame-level pretrained acoustic features (WavLM-large, HuBERT extra large, Whisper large-v3) and RoBERTa-large text features; two-layer Transformer + mean pooling + concatenation MLP. Their ablation reports **early fusion superior to other tested late/tensor/low-rank variants**, even though MEDUSA later found hierarchical deep fusion useful. Results are setting-dependent, **not a universal architecture law**.
- A pretrained **English** seq2seq ASR error correction model was fine-tuned on **paired in-domain human transcriptions**. Dev **WER 17.65% → 14.51%**, BLEU **81.32→83.48**, GLEU **78.02→81.19**. **No direct ablation proves that this correction alone increases downstream emotion F1**; an approximately 1% projected accuracy benefit is conjectural. DEFHS has no verified Hindi gold transcripts; comparing Whisper and Qwen3-ASR does not yield WER or accuracy ranking.
- Focal loss prior weights showed tradeoffs: model1 **34.2%** macro-F1 (focal gamma=2 + prior), model5 **33.8%** (CE + prior), model6 **33.3%** (focal + uniform), model7 **32.8%** (CE + uniform); distinct WavLM/HuBERT/Whisper experts and loss weights yielded **35.6%** development macro-F1 with 7-model majority voting. That does not establish a material macro-F1 gain on nearly balanced DEFHS.

**Challenge organizer triangulation**
- Interspeech 2025 93 teams, 166 categorical submissions: top NTUA/MEDUSA **0.4316**, SAIL **0.4281**, ABHINAYA **0.4181**, Voinosis **0.4101**, UNICAMP **0.4094**. Many use audio+text foundation models, ensembles, balancing and augmentation. These are broad-method trends, not validated interventions on the frozen DEFHS groups. The organizer reports UNICAMP used RandomForest stacking, but does not establish genuinely nested group-safe fitting under DEFHS's regime.

## Mechanism classification specifically for DEFHS

| Proposed change | Classification | Why / what would falsify |
|---|---|---|
| Multimodal acoustic+semantic information | **ALREADY TESTED** | E2V+XLS-R and Qwen8B+Qwen14B make up System D; its +0.02609 over C is proven frozen OOF; no reason to restart. |
| Learned class-dependent posterior-level metaclassifier | **ALREADY TESTED** | D has 18-feature L2 multinomial logistic with distinct class coefficients. MEDUSA's learned reliability principle is already used. |
| Fixed voting, fixed waveform ensemble, extra model heads | **ALREADY TESTED** | System1, waveform fixed pair, and C/D fusion already tested; adding many correlated experts is not guaranteed. |
| Probability-coordinate (CLR) change | **REJECTED ALREADY TESTED** | SS's exact dependent CI crosses zero; -0.02837 int32. No rescue. |
| Novel **ASR language information** (new Qwen3-ASR → frozen Qwen3-14B) | **GENUINELY NEW, ACTIVE** | Exact next decisive experiment. New transcript may recover missing semantic information and repair cases where all four current experts are wrong; must measure actual correction-minus-breakage under frozen nested CV. |
| Unpaired text-only ASR hallucination correction | **UNSUPPORTED**, risky | Without Hindi reference pairs, rewriting text can distort emotion cues. AEC paper's demonstrated WER drop depended on paired text supervision. |
| Direct new transcript vs old transcript inspection | **DIAGNOSTICALLY NEW**, near-free | Measure ID-level changes, new semantic states and conditional correctness; don't label disagreement as accuracy/WER. |
| Early frame/token multimodal feature fusion | **GENUINELY NEW but INFEASIBLE before deadline** | Requires token/frame features, alignment, multiple fresh group-nested supervised deep fits; 826 examples vs 84k and speaker/prompt duplication make variance high. |
| Annotator vote soft labels + VAD multitask supervision | **UNSUPPORTED BY DEFHS DATA** | No real vote distributions/attribute ratings; do not synthesize gold supervision. |
| Class-aware focal-loss / balance variants | **UNCONFIRMED LOCALLY; LOW PRIORITY** | A specific new loss recipe is possible, but this does not introduce new evidence, changes calibration and has class/speaker shift risks; published benefits small and confounded with 8-class imbalance. No adaptive tuning permitted. |
| Learned nonlinear meta / meta soup over D | **GENUINELY DIFFERENT FUNCTION CLASS, LOW PRIORITY/INFEASIBLE** | Only 826 training labels and grouped inner folds; risk of correlated-family fitting and fragile source transfer. Public MEDUSA config isn't final experimental authority; no new independent information. |
| Speaker metadata, human transcript, forced alignment | **UNSUPPORTED** | MEDUSA datasets contain annotation/metadata absent from frozen DEFHS evidence. No gold target transcripts or speaker labels. |

## Specific falsifiable mechanisms and ordering

**H1 (active and most decision-relevant): Missing Hindi lexical/semantic evidence.** System D 133/826 errors; frozen HARD316 contains 94 errors; 43 neutral/sad confusions, 93 errors have at least one correct existing expert, while 40 are wrong under all four considered experts. A replacement ASR may change lexical information that influences Qwen3-14B semantic judgments, potentially correcting some of those 40 expert-oracle misses. However transcript changes alone are not sufficient; changed new labels can break correct D predictions and may expose new biases.

After the repaired Kaggle ASR 826 run, verify all WAV IDs/hashes and output inventories, compare old/new transcripts without claiming WER, run identical 14B prompt and checkpoint on new transcript set. Then execute **exactly one predeclared 23-feature nested System E** (original D 18 features plus 5 new categorical semantic indicators), reproducing D first, testing all original 6 primary and 7 stress gates. Keep retrieval unchanged. The hypothesis is falsified if new semantic states show no net complementarity or System E fails any gate; a GPU execution failure is only a technical blocker.

**H2 (lower priority, defer): Acoustic-text interaction beyond posterior fusion.** This could capture prompt/prosody contradictions absent from D's 18-feature representation; but only credible with group-safe nested training and demonstrate gains in duplicate-singleton/int32 and neutral/sad, with positive dependency-aware CI. DeepSER results on 84k eight-class podcast samples do not authorize such deployment on 826 four-class Hindi samples under an imminent deadline.

**Recommendation to SS:** Continue the Kaggle ASR fix+launch immediately. No literature-derived architecture or loss search should displace it. Evaluate System E only after byte-verified 826 ASR output and frozen 14B semantic inference. If negative, retain System D public 0.88227. No competition submission from RS.
