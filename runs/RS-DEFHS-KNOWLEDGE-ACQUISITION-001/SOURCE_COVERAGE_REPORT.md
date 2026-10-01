# Source Coverage Report

Mission: `RS-DEFHS-KNOWLEDGE-ACQUISITION-001`  
As of: 2026-10-01

The normalized inventory contains **84 canonical records** (including all 36 original discovery records, exact replacements/children, and independently discovered sources). Every original record has a disposition.

## Coverage achieved

- **Hindi-specific SER:** Goel/BhavVani/CAMuLeNet; IITKGP-SEHSC; Agrawal/Jain; Kotian 2026; Shashank derivative.
- **Indian/South-Asian transfer:** SUBESCO (Bangla), EmoTa (Tamil), Urdu dataset, current Bangla Interspeech 2026 work, regional review and 2025 cross-lingual Indo-Aryan/Dravidian study.
- **Emotion-specialized foundation models:** emotion2vec / emotion2vec+; SenseVoice; Vesper; MERaLiON-SER-v1.
- **General speech foundation models:** Whisper large-v3; XLS-R/XLSR-53; HuBERT; WavLM; UniSpeech-SAT; data2vec; MMS; Qwen2.5-Omni as lower-priority audio-native context.
- **Unseen-speaker / cross-lingual:** CAMuLeNet; ICASSP 2025 PEFT/cross-lingual work; Interspeech 2026 zero-shot cross-lingual, KuralHub, TIMBRE.
- **Acted vs naturalistic / domain shift:** Interspeech 2025 SERNC challenge and systems; Goel multilingual datasets; naturalistic 2025/2026 methods.
- **Pooling / layer selection:** attentive statistics pooling 2025; layer-wise cross-lingual 2025/2026; Whisper/SSL freezing evidence.
- **Frozen encoder / partial fine-tuning / PEFT:** Interspeech 2025 SSL benchmark; ICASSP 2025 cross-lingual PEFT; 2025 ESWA PEFT; LoRA Whisper; EmoSLLM.
- **Acoustic + SSL:** eGeMAPS/openSMILE; WavLM interpretability; CAMuLeNet acoustic/embedding combinations.
- **Audio + transcript/text fusion:** MATER, ABHINAYA, SERNC overview, EmoSLLM, high-performance 2025 naturalistic framework.
- **Augmentation / imbalance:** 2026 energy-adaptive mixup/multi-loss; 2024 focal-loss ensemble; 2025 challenge imbalance losses.
- **Pseudo-labeling / weak supervision:** Interspeech 2026 conflict-aware pseudo-labeling and progressive weak supervision.
- **Ensembling:** ABHINAYA majority voting; MATER uncertainty-aware ensemble; Odyssey class-imbalance system; 2025 SERNC top framework.
- **Calibration / macro-F1 selection stability:** metric distinctions are captured, but dedicated probability-calibration evidence remains a secondary gap because macro-F1 decision policy is more immediately relevant than probabilistic calibration.
- **Retrieval / near-duplicate handling:** internal DEFHS retrieval authority remains the relevant source; no external paper was allowed to redesign that frozen lane.

## Evidence tiers

{'TIER_A': 51, 'TIER_B': 22, 'TIER_C': 8, 'INTERNAL': 1, 'REJECT': 2}

## Acquisition dispositions

{'ACQUIRED_VERIFIED': 17, 'POINTER_ONLY': 33, 'SPLIT_TO_EXACT_RECORDS': 6, 'INTERNAL_AUTHORITY': 1, 'METADATA_ONLY': 21, 'DUPLICATE_FAMILY': 1, 'DUPLICATE_DERIVATIVE': 1, 'REJECTED_NON_SOURCE': 2, 'INTERNAL_COMPETITION_DATA_ALREADY_PRESENT': 1, 'DUPLICATE_HOST': 1}

## Scientific boundary

This warehouse is evidence acquisition only. It does not select a winning model family and contains no protected-validation candidate performance. V-B/V-A/V-D/Q/retrieval roles remain exactly as frozen by DS authority.