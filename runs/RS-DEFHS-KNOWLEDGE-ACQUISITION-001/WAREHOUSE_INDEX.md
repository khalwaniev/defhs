# DEFHS Knowledge Warehouse Index

Canonical Drive root: `/DEFHS/knowledge/`  
Drive folder ID: `1asWciARNwNE_OrL-_OmKWBxF3MF8uMeR`

## Verified existing folders

| Logical path | Drive folder ID | State |
|---|---|---|
| `/DEFHS/knowledge/papers/` | `1SuWb1ZvcuAOWI69C15Xk8xZNekpnP_bN` | EXISTS |
| `/DEFHS/knowledge/surveys/` | `1BklLrEK0QJ6BeiUQ7ncobmjuYbSPId-8` | EXISTS |
| `/DEFHS/knowledge/theses/` | `1HV46sPAS9MmjmO7cPuXdHDKrwYmAtimb` | EXISTS |
| `/DEFHS/knowledge/repositories/` | `1tWWo6fsENYPY38TdBYJCntl37n5otuZm` | EXISTS |
| `/DEFHS/knowledge/model_cards/` | `1jqjfW1ytoqaudF8EZ6hT-M_s3r-1aExd` | EXISTS |
| `/DEFHS/knowledge/checkpoint_metadata/` | `1u8yt5id6rerFFKfsJNLWkbbkLiSIHNeX` | EXISTS |
| `/DEFHS/knowledge/datasets/` | `16FuCNx7VJepDnwaLCNMTLYBPesJ7otbu` | EXISTS |
| `/DEFHS/knowledge/supplements/` | `13fYlYvDzgkL5KMuwWRy4RLGeCpey3xXW` | EXISTS |
| `/DEFHS/knowledge/competition_solutions/` | `1iaKcby7Yq3HXT67LLsbjoifw9cb9R29q` | EXISTS |
| `/DEFHS/knowledge/pointer_only/` | `1iTlkYbho5Vkegm_NhVvTZLRAwUNiIfBn` | EXISTS |
| `/DEFHS/knowledge/manifests/` | `1Q8pVKD_YUGAgM2CyAmqZdJFn9Sk6uygU` | EXISTS |

## Binary state

No paper PDF, repository archive, model weight, or external dataset byte is claimed to exist in these folders yet. The connected Drive upload action cannot ingest a local path or arbitrary public URL, and this runtime cannot materialize those web binaries into a connector `file_uri`.

Records marked `PENDING_BINARY_HANDOFF` in `KNOWLEDGE_MANIFEST.csv` are the legally/reproducibly selected binary acquisition set. The companion script performs the download, SHA256 calculation, and `rclone` upload from the user's canonical WSL environment.

This file must not be interpreted as proof that a listed target file exists until the post-handoff readback confirms it.

## Verified control-layer archive

- `/DEFHS/knowledge/manifests/RS-DEFHS-KNOWLEDGE-ACQUISITION-001_packet.zip`
- Drive file ID: `1a3QzpBCtdZv5G1tz8CBh91fq1rMZPfsf`
- Size: 69,185 bytes
- SHA256: `eec4948c4653916132a26fb66d7fead4a11f64e332ee88af4d581fdf89f38955`
- State: **EXISTS** (uploaded through connected Drive).

This ZIP is a control-layer snapshot of the generated acquisition packet; it is not a substitute for the selected external paper/repository binaries that remain pending WSL handoff.
