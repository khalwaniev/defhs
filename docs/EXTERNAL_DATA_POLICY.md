# External Data Policy

## Current position

External models/data may be used only when they satisfy the competition rules
and are sufficiently accessible/reproducible for participants.

Before any external corpus is promoted, record:

- dataset/model name;
- source URL;
- license/access terms;
- acquisition date;
- exact subset used;
- label mapping;
- checksum/version when practical;
- experiment demonstrating target-domain value.

## Scientific priority

Priority order for external knowledge:

1. emotion-specialized pretrained representations, especially emotion2vec+;
2. Hindi speech-emotion corpora with clean overlap to angry/happy/neutral/sad;
3. large, accessible SER corpora such as CREMA-D when used as a controlled
   pre-adaptation experiment;
4. other multilingual SER corpora only when OOF evidence supports them.

Do not concatenate every available SER dataset by default.

## Required experiment

For each promoted encoder, compare under identical frozen folds:

- competition-only;
- external pre-adaptation → competition fine-tuning;
- Hindi external pre-adaptation → competition fine-tuning;
- multi-corpus pre-adaptation → competition fine-tuning.

External data are useful only if they improve target-domain evidence or add
valuable ensemble diversity.
