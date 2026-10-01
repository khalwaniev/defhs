# BhavVani / SRCASW-BhavVaani Provenance Reconciliation

Mission: `RS-DEFHS-KNOWLEDGE-ACQUISITION-001`  
Audit date: 2026-10-01

## Conclusion

**Relationship classification: UNRESOLVED.**

The evidence does **not** justify treating Goel et al.'s `BhavVani` corpus and the Kaggle/DataVerse `SRCASW-BhavVaani` competition corpus as the same source or as a verified derivative. For all DEFHS scientific decisions, treat them as **operationally distinct corpora unless later documentary or clip-level evidence establishes a lineage**.

## Evidence that is verified

| Property | Goel et al. BhavVani | Kaggle/DataVerse SRCASW-BhavVaani |
|---|---|---|
| Primary/public anchor | Goel, Hira & Gupta, Interspeech 2024, DOI 10.21437/Interspeech.2024-1820 | Kaggle competition page + supplied DEFHS package |
| Described size | 8,734 utterances, about 13 h | organizer prose 1,036; supplied package 826 train + 209 test = 1,035 |
| Emotional label inventory | 7: Neutral, Surprise, Enjoyment, Disgust, Anger, Fear, Sadness | operational package: angry, happy, neutral, sad |
| Source description | Hindi TV sitcom dialogues, `Sarabhai vs Sarabhai` | organizer calls corpus self-curated and describes acted + spontaneous speech |
| Annotation/source metadata | 18 native Hindi annotators described by Goel et al. | exact source/annotator lineage unavailable in current competition materials |
| Access | author access form / current HF mirror has restrictive terms | supplied through Kaggle competition |

## Why “BhavVani (a.k.a. SRCASW-BhavVaani)” is rejected

The shared/similar naming is insufficient provenance. The published sizes, class inventories and source descriptions materially differ. Those differences prove that the *published descriptions are not identical*, but they do not by themselves prove that the Kaggle corpus could not contain a subset, derivative, reannotation, or independently named collection. No source inspected in this mission documents such a relationship.

Therefore the defensible state is `UNRESOLVED`, not `VERIFIED SAME SOURCE`, `VERIFIED DERIVATIVE`, or an invented provenance story.

## Operational consequence

1. Do not use Goel/BhavVani licensing terms as the license for the Kaggle competition data.
2. Do not assume that external BhavVani clips are permitted competition training data.
3. Do not use BhavVani speaker/label/source metadata as ground truth for the Kaggle clips.
4. If future external-data use is contemplated, SS must separately confirm Kaggle competition compatibility and dataset terms.
5. A future provenance test may compare audio fingerprints only if authorized and scientifically necessary; it is not required for this acquisition closure.
