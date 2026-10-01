# Missing Evidence Register

As of 2026-10-01, the following gaps remain explicit rather than guessed:

1. **BhavVani -> Kaggle SRCASW lineage:** unresolved; no documentary evidence of same-source or derivative relationship.
2. **IITKGP-SEHSC access/license:** corpus scale and speaker design are well corroborated; redistribution/use license is not.
3. **TESS current repository license:** canonical DOI identified; current license terms were not captured to authority standard.
4. **emotion2vec repository and emotion2vec+ checkpoint licenses:** public availability is not treated as a license. Repo has no LICENSE file at audited HEAD; checkpoint cards use `model-license` without captured governing terms.
5. **SenseVoiceSmall checkpoint license:** repository code is MIT, but checkpoint weight terms are separate and remain unresolved.
6. **MERaLiON-SER-v1 custom license:** exact public-model-license terms need a complete license capture before any weight mirroring/use decision.
7. **Some Hugging Face current full revisions:** exact full SHA was captured for Whisper and an immutable MMS revision, but several model hub records were only observable by prefix in the available web surface. They must be pinned by API at execution time.
8. **Interspeech 2026 individual paper metadata:** the official 2026 index is live on the conference end date (2026-10-01); several individual paper DOI/pages were not yet reliably indexed by the available search surface. Titles/authors are preserved from the official index, not invented.
9. **Competition external-data compatibility:** public availability or a permissive dataset license does not by itself authorize use in this Kaggle competition. SS must verify competition rules before any external training-data ingestion.
10. **Probability calibration specific to macro-F1:** evidence coverage is thinner than for representation, pooling, PEFT, augmentation, fusion and ensemble design. This is a later synthesis gap, not a reason to redesign validation.
11. **Binary warehouse preservation:** the current ChatGPT runtime cannot transfer newly downloaded public PDF/archive bytes into the connected Drive uploader. The exact deterministic WSL acquisition script is provided and is the only remaining operational acquisition blocker.
