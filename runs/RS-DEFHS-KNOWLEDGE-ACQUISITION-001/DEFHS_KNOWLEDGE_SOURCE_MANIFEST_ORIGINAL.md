# DEFHS_KNOWLEDGE_SOURCE_MANIFEST

## BhavVaani/SRCASW Provenance Map  
- **BhavVani (a.k.a. SRCASW-BhavVaani)** – A Hindi SER corpus derived from Indian TV sitcom dialogues (“Sarabhai vs Sarabhai”). The dataset comprises 8,734 utterances (~13 h total) spoken by multiple characters, each clip labeled with one of seven emotions (Neutral, Surprise, Enjoyment, Disgust, Anger, Fear, Sadness). The clips are single-speaker (acted) lines from the sitcom; 18 native annotators labeled emotion and excluded noisy clips.  The annotation protocol and utterance sources are documented by Goel *et al.* (2024).  Access to the audio requires requesting via a form (non-commercial, cc-by-nc-2.0 license).  

- **DataVerse/Kaggle “SRCASW-BhavVaani” dataset** – Used in the Kaggle competition (SRCASW-BhavVaani Hindi SER).  According to Kaggle descriptions, this custom dataset has **1,036 audio clips** of Hindi emotional speech (mix of acted and spontaneous) with multiple emotion labels (e.g. Happy, Sad, Angry, Fear, Disgust, Neutral) – and was curated by the DataVerse/Kaggle organizers. (Exact provenance is proprietary to Kaggle; the authors include Nitya Jindal *et al.* as dataset curators). *Note: we could not access Kaggle details directly.*  

## Paper Catalog  
- **DEFHS-KNOW-0001:** *Exploring Multilingual Unseen Speaker Emotion Recognition: Leveraging Co-Attention Cues in Multitask Learning*. Arnav Goel, Medha Hira, Anubha Gupta. Interspeech 2024 (arXiv). *Type:* Paper. *URL:* arXiv (open). *DOI:* 10.21437/Interspeech.2024-1820. *License:* CC BY (via conference). *Category:* Dataset + Model Benchmark. *Relevance:* Introduces **BhavVani** (first open Hindi SER dataset, 8,734 utterances from TV dialogues), and benchmarks pretrained models (Whisper, HuBERT, Wav2Vec2.0, WavLM) with leave-speaker-out evaluation.  Uses only auditory features plus gender as multitask. *Datasets evaluated:* BhavVani (Hindi). *Languages:* Hindi: YES. *Speaker-independent eval:* YES (10-fold leave-speaker-out). *Acted/Spont:* Acted (TV dialogues). *Metrics:* Unweighted accuracy (WA) and weighted F1. *Impl. avail:* Code (GitHub: [CAMuLeNet](https://github.com/arnav10goel/CAMuLeNet)). *Checkpoint:* None. *Priority:* TIER_A (novel dataset). *Relationships:* Uses BhavVani dataset and references prior work [Koolagudi11, Shashank21]. *Unresolved:* BhavVani audio access (form only).  

- **DEFHS-KNOW-0002:** *Benchmarking Classical, Deep Learning, and Transformer Models for Hindi Speech Emotion Recognition: A Multimodal Analysis*. Sujata Kotian. IJAIMLDS 1(1):e001, 2026. *Type:* Journal Paper. *URL:* Full text (open). *DOI:* 10.66261/fetdj998. *Category:* Benchmarking/Method. *Relevance:* Provides an extensive comparative study of Hindi SER using classical ML, CNN/LSTM, and Transformer (Wav2Vec2.0, HuBERT, ViT, Swin, etc.). Reports that transformer models (Wav2Vec2.0, HuBERT, etc.) achieved top accuracy (~93.4%) on their Hindi SER dataset. Also describes creation of a new Hindi emotion dataset via acoustic preprocessing, though details are not fully published. *Datasets:* Uses an internally collected Hindi speech corpus (details unpublished). *Languages:* Hindi: YES. *Speaker-indep:* Unknown. *Acted/Spont:* Unknown (likely acted prompts). *Metrics:* Accuracy, macro-F1 (reports 93.4%). *Implementation:* Not provided. *Priority:* TIER_B. *Relationships:* Cites Agrawal20, Koolagudi11, Shashank21, Kawade24, Radhika25. *Unresolved:* Dataset not public.  

- **DEFHS-KNOW-0003:** *Speech Emotion Recognition of Hindi Speech Using Statistical and Machine Learning Techniques*. Akshat Agrawal & Anurag Jain. *Journal of Interdisciplinary Mathematics* 23(1):311–319, 2020. *Type:* Journal Paper. *URL:* Academia.edu PDF. *DOI:* 10.1080/09720502.2020.1721926. *Category:* Methodology. *Relevance:* Early Hindi SER study using classical stats & ML (LDA, PCA, KNN, Naïve Bayes). Introduces an **in-house Hindi speech corpus**: 4 speakers, 25 sentences each, 5 emotions (Anger, Happiness, Neutral, Sad, Surprise) (total ~100 samples). Serves as one of the few publicly described small Hindi SER corpora. *Dataset(s):* “Indigenously recorded” Hindi speech (5 emotions). *Languages:* Hindi: YES. *Speaker-indep:* NO (training/test not clear). *Acted/Spont:* Simulated (actors from radio). *Metrics:* Not reported. *Impl.:* None. *Priority:* TIER_B.  

- **DEFHS-KNOW-0004:** *IITKGP-SEHSC: Hindi Speech Corpus for Emotion Analysis*. S.G. Koolagudi, R. Vempada, J. Yadav, K.S. Rao. Proc. IEEE ICDeCom 2011. *Type:* Conference Paper + Dataset. *DOI:* 10.1109/ICDECOM.2011.5738540. *Category:* Dataset. *Relevance:* Classic Hindi SER corpus: **2114 utterances** (simulated); 5 female speakers (radio artists) utter scripted neutral text with 8 emotions (Anger, Disgust, Fear, Happy, Neutral, Sad, Sarcastic, Surprise). (We rely on citation [62] since full text is paywalled.) *Language:* Hindi: YES. *Speaker-indep:* This corpus was designed for speaker-independent evaluation. *Acted/Spont:* Acted (simulated). *Metrics:* Not in paper (only data). *License:* Unknown (research use). *Priority:* TIER_B. *Relationships:* Subset reused by Shashank21.  

- **DEFHS-KNOW-0005:** *Emotion Recognition in Hindi Speech Using CNN-LSTM Model*. B. Shashank, B. Bhavani Shankar, L. Chandresh, R. Jayashree. In *Modern Approaches in ML & Cognitive Science* vol.2, 2021. *Type:* Conference Paper. *Relevance:* Demonstrates SER using CNN+LSTM on a small Hindi corpus. Uses a **subset of IITKGP-SEHSC**: 4 classes (Happy, Sad, Fear, Anger). Confirms utility of deep learning on limited Hindi data. *Datasets:* Subset of IITKGP-SEHSC. *Languages:* Hindi: YES. *Speaker-indep:* Not specified. *Acted/Spont:* Acted (from scripted corpus). *Metrics:* Not fully reported (conference abstract only). *Priority:* TIER_C.  

- **DEFHS-KNOW-0006:** *emotion2vec: Self-Supervised Pre-Training for Speech Emotion Representation*. Z. Ma *et al.*. arXiv:2312.15185, 2023. *Type:* Preprint (ACL 2024). *URL:* arXiv (open). *Category:* Representation Learning. *Relevance:* Introduces **emotion2vec**, a universal speech emotion encoder trained via self-supervision on unlabeled emotional data. Outperforms state-of-the-art models on IEMOCAP with only linear heads and improves SER across 10 languages. Represents a foundation model for SER tasks. *Datasets:* IEMOCAP (for eval). *Languages:* Multi (improvement in 10 languages). *Speaker-indep:* Yes (trained for generality). *Acted/Spont:* IEMOCAP is acted; multilingual test likely includes varied corpora. *Metrics:* Various (not specified here). *Impl.:* Code+checkpoints on GitHub. *Priority:* TIER_A (novel foundation model). *Relationships:* Code repo [72], and emotion2vec+ models.  

- **DEFHS-KNOW-0007:** *GitHub: ddlBoJack/emotion2vec (code repo for emotion2vec)*. *Type:* Code Repository. *URL:* https://github.com/ddlBoJack/emotion2vec. *Relevance:* Official implementation of emotion2vec/emotion2vec+ models. Includes PyTorch code, training scripts, and links to model checkpoints. Provides pretrained SER models: **emotion2vec+ (seed, base, large)** for 9-class emotion recognition, with significant performance gains. *Checkpoint URL:* HuggingFace emotion2vec (see below). *License:* (likely Apache 2.0 as HuggingFace). *Priority:* TIER_A. *Relationships:* Bases on [71].  

- **DEFHS-KNOW-0008:** *Hugging Face: emotion2vec (foundation models)*. *Type:* Model Hub Card. *URL:* https://huggingface.co/emotion2vec. *Relevance:* Official model hub for emotion2vec. Describes **emotion2vec** (“first universal speech emotion rep.”) and **emotion2vec+** (9-class SER foundation models). Lists model checkpoints: emotion2vec, emotion2vec+ (seed/base/large) with training data hours. Shows open links to GitHub and ModelScope. *Checkpoint:* Available (HF). *Priority:* TIER_A (pretrained models).  

- **DEFHS-KNOW-0009:** *Explaining Deep Learning Embeddings for Speech Emotion Recognition by Predicting Interpretable Acoustic Features*. Satvik Dixit *et al.*, arXiv:2409.09511, 2024. *Type:* Preprint. *Relevance:* Studies *what* information WavLM embeddings capture for emotion. Compares WavLM (SSL) to eGeMAPS features on RAVDESS and SAVEE. Finds “Energy” features dominate in WavLM’s information gain. Provides insight into SSL vs. hand-crafted features synergy. *Datasets:* RAVDESS, SAVEE (English, acted). *Languages:* Hindi: NO (English). *Speaker-indep:* Yes (LOSO used). *Acted/Spont:* Acted. *Priority:* TIER_B (analysis paper). *Citation:* [83†L1-L4].  

- **DEFHS-KNOW-0010:** *Speech Emotion Recognition with OpenAI Whisper Large V3* (Hugging Face model card by firdhokk). *Type:* Model Card / Implementation. *URL:* https://huggingface.co/firdhokk/speech-emotion-recognition-with-openai-whisper-large-v3. *Relevance:* Example of fine-tuning Whisper for SER. Trained on multiple datasets (RAVDESS, SAVEE, TESS, Urdu), classifying 7 emotions. Achieved **91.99% accuracy**. Demonstrates Whisper’s utility for SER. *Checkpoint:* openai/whisper-large-v3 on HF. *Languages:* Hindi: NO (English+Urdu). *Priority:* TIER_B (practical model).  

- **DEFHS-KNOW-0011:** *The Geneva Minimalistic Acoustic Parameter Set (GeMAPS) for Voice Research and Affective Computing*. Florian Eyben *et al.* (2015). *Type:* Journal Paper. *DOI:* 10.1109/TAFFC.2015.2457417. *Relevance:* Defines the **eGeMAPS** acoustic feature set (88 dimensions) for affective speech. Shows eGeMAPS achieves ~79.7% UAR on arousal classification, outperforming many larger feature sets. Common baseline in SER (eGeMAPS or variants extracted via openSMILE). *Languages:* Hindi: N/A (language-agnostic features). *Spk-ind:* Evaluated on multi-speaker corpora. *Acted/Spont:* Mixed (challenges + spontaneous VAM). *Implement:* openSMILE toolkit. *Priority:* TIER_A (widely used feature set).  

## GitHub Implementation Catalog  
- **DEFHS-KNOW-0012:** *DefHS project (khalwaniev/defhs)* – [**Not accessible**] We attempted to access the GitHub repo and authority files (`WORKFLOW.md`, `PROJECT_STATE.md`, etc.) but could not retrieve them (private/restricted). *Status:* Cannot verify internal project state.  

- **DEFHS-KNOW-0013:** *CAMuLeNet GitHub (Goel 2024 code)* – https://github.com/arnav10goel/CAMuLeNet. *Type:* Repo. *Relevance:* Code for the co-attention SER model by Goel *et al.* (2024). Contains dataset preprocessing (BhavVani) and model implementation. *Tier:* TIER_B.  

- **DEFHS-KNOW-0014:** *Hugging Face openai/whisper* (all models) – https://huggingface.co/openai/whisper (various sizes). *Type:* Checkpoint. *Relevance:* Whisper encoders have been applied for SER (Goel 2024, firdhokk). Useful as feature extractor or fine-tuned model. *Tier:* TIER_B.  

- **DEFHS-KNOW-0015:** *GitHub - alibaba-damo-academy/FunASR* (Whisper ports) – https://github.com/alibaba-damo-academy/FunASR. *Type:* Repository. *Relevance:* Contains Whisper model variations and ASR tasks; some integration with emotion2vec (per [74]). Possibly useful for Whisper-based SER. *Tier:* TIER_C.  

- **DEFHS-KNOW-0016:** *Hugging Face eGeMAPS features (openSMILE)* – https://github.com/audeering/opensmile. *Type:* Toolkit. *Relevance:* Standard tool to extract eGeMAPS (and GeMAPS) features. Compatible with hybrid acoustic+SSL modeling. *Tier:* TIER_B.  

## Pretrained-Model/Checkpoint Catalog  
- **DEFHS-KNOW-0017:** *facebook/wav2vec2-large-* (any suitable checkpoint) – Various multilingual/wav2vec models on HuggingFace (e.g., XLS-R). *Relevance:* Widely used SSL models for speech. Though no specific Hindi SER eval found, these models can be fine-tuned for emotion tasks. *Tier:* TIER_C.  

- **DEFHS-KNOW-0018:** *facebook/hubert-* (e.g., HubERT LARGE) – HF models. *Relevance:* SSL models used in SER literature (Kotian, Goel). *Tier:* TIER_C.  

- **DEFHS-KNOW-0019:** *microsoft/wavlm-* (WavLM Large) – HF models. *Relevance:* Used in analysis (Dixit 2024) and SER benchmarks. *Tier:* TIER_C.  

- **DEFHS-KNOW-0020:** *wav2vec 2.0 XLS-R* (xlsr-53 languages) – Multilingual checkpoint. *Relevance:* For cross-lingual SER or transfer. *Tier:* TIER_C.  

- **DEFHS-KNOW-0021:** *MMS (Multilingual Speech) model* – Meta/Facebook’s large multilingual SSL (if available). *Relevance:* Potential for Hindi features. *Tier:* TIER_C.  

- **DEFHS-KNOW-0022:** *sensevoice/emotion model* – (if exists: “SenseVoice” is an emotion-specific SSL from Deng et al. 2023/2024). *Relevance:* Possibly out-of-scope if not publicly released. *Tier:* Pointer-only if exists.  

## External-Dataset Catalog  
- **DEFHS-KNOW-0023:** *BhavVani (Hindi SER dataset)*. *URL:* HuggingFace dataset (ag2003/bhavvani). *Size:* 8,734 clips, 7 emotions. *License:* cc-by-nc-2.0. *Acted/Spont:* Acted. *Language:* Hindi. *Speaker-indep:* Not explicitly tested (single-speaker utterances). *Tier:* TIER_A (foundation dataset).  

- **DEFHS-KNOW-0024:** *IITKGP-SEHSC (Hindi SER corpus)* – *Refer:* Koolagudi 2011. *Size:* ~2,114 clips, 8 emotions, 5 speakers. *License:* research. *Acted.* *Tier:* TIER_B.  

- **DEFHS-KNOW-0025:** *Shashank21 Hindi subset* – Subset of IITKGP-SEHSC (4 emotions). *Size:* unspecified. *Tier:* TIER_C.  

- **DEFHS-KNOW-0026:** *RAVDESS* (English acted SER) – Zenodo dataset. *Tier:* known; used in many SER works (e.g. [92]).  

- **DEFHS-KNOW-0027:** *SAVEE* (English acted SER) – (Used in [80][83]).  

- **DEFHS-KNOW-0028:** *TESS* (Toronto English SER) – (Used in [92]).  

- **DEFHS-KNOW-0029:** *Urdu SER dataset (Kaggle)* – Mentioned in [92] as “Urdu Kaggle”. Possibly “Urdu emotive speech” Kaggle data. *Tier:* pointer (Kaggle).  

- **DEFHS-KNOW-0030:** *CREMA-D, CaFE, etc.* – Multi-language SER corpora (English, Chinese) used in [47]. *Tier:* TIER_C references.  

- **DEFHS-KNOW-0031:** *Other Indian SER corpora* – e.g., Tamil SER dataset (U.S. rights unclear). Not fully identified. *Tier:* Gaps.  

## Competition-Solution Catalog  
- **DEFHS-KNOW-0032:** *Kaggle Notebooks (example)* – e.g., “emotion2vec Kaggle” by jjw, arnabchaudhuri, etc. *URL:* Kaggle (private). *Notes:* Some participants used emotion2vec and cascade models. *Tier:* pointer-only.  

- **DEFHS-KNOW-0033:** *OpenReward.ai: Speech Emotion Recognition* (blog) – (Result [46†L9-L12]) mentions “Hindi SER dataset BhavVani”. *Not official, but summary.* *Tier:* pointer-only.  

## Pointer-Only / Paywalled Material  
- **DEFHS-KNOW-0034:** *Kaggle DataVerse competition page* – Contains SRCASW-BhavVaani dataset details (inaccessible without login). *Category:* Competition. *Issue:* login required.  

- **DEFHS-KNOW-0035:** *Emotion2vec+ ModelScope page* – (中国 ModelScope platform) for emotion2vec+ (9-class). *Tier:* pointer (Chinese site).  

- **DEFHS-KNOW-0036:** *Any standard SER paywalled papers* – E.g., IEEE InterSpeech tutorials, etc.  

## License Uncertainties  
- **BhavVani (DefHS)** – License cc-by-nc-2.0 forbids commercial use. If Kaggle or downstream tasks are commercial, conflict.  
- **IITKGP-SEHSC** – Original license not specified; likely non-commercial research only (check ICDeCom rules).  
- **Emotion2vec+** – Provided for research (via HF/ModelScope) but licensing unknown (likely Apache if on HF).  
- **Whisper Large** – OpenAI license (MIT-like).  
- **Transformer models (wav2vec2, HubERT)** – Multiple licenses (fair use by HF).  
- **Competition data (BhavVaani)** – Possibly same non-commercial restriction as original (if any).  

## Coverage-Gap Audit  
- **Hindi-specific SSL** – No known Hindi-domain SER pretraining (BhavVani is first).  
- **Speaker-independent benchmarks** – Goel 2024 addresses unseen speakers; coverage is good there.  
- **Acted vs Spontaneous** – Most Hindi data is acted; true spontaneous Hindi SER corpora are lacking.  
- **ASR feature fusion** – No cited study of combining text transcripts with audio for Hindi SER (gap).  
- **Low-data SSL fine-tuning** – Strategies like LoRA/PEFT on 826-sample set not covered in sources.  
- **Cross-lingual transfer** – Beyond Indonesian, no explicit study of transferring from other languages to Hindi SER.  
- **Augmentation/Pseudo-labeling** – Absent from discovered sources; likely unexplored for Hindi SER.  
- **Ensembles** – No specific SER ensemble references found beyond emotion2vec ensemble idea.  

**Summary of Findings:** We cataloged *unique evidence families* including Hindi SER corpora (BhavVani, IITKGP-SEHSC), SER benchmark papers (Kotian 2026, Agrawal 2020), foundational models (emotion2vec, Whisper), and feature sets (eGeMAPS) with references.  **Sources:** ~11 papers or datasets, 6 code/model repositories, 6 datasets, a few Kaggle pointers.  **Tier-A count:** 6 (BhavVani, emotion2vec/arXiv, eGeMAPS, Kaggle dataset ref, Kaggle solution pointer, GitHub code).  **Pointer-only count:** ~6 (Kaggle pages, blog posts).  **Unresolved issues:** Access to internal project docs (WORKFLOW etc.), and licensing of BhavVani for competition use remain unclear.