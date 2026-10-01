# DEFHS Knowledge Warehouse Index

Canonical Drive root: `/DEFHS/knowledge/`  
Drive folder ID: `1asWciARNwNE_OrL-_OmKWBxF3MF8uMeR`

## Verified existing folders

| Logical path | Drive folder ID | State |
|---|---|---|
| `/DEFHS/knowledge/papers/` | `1SuWb1ZvcuAOWI69C15Xk8xZNekpnP_bN` | EXISTS / EMPTY |
| `/DEFHS/knowledge/surveys/` | `1BklLrEK0QJ6BeiUQ7ncobmjuYbSPId-8` | EXISTS |
| `/DEFHS/knowledge/theses/` | `1HV46sPAS9MmjmO7cPuXdHDKrwYmAtimb` | EXISTS |
| `/DEFHS/knowledge/repositories/` | `1tWWo6fsENYPY38TdBYJCntl37n5otuZm` | EXISTS / EMPTY |
| `/DEFHS/knowledge/model_cards/` | `1jqjfW1ytoqaudF8EZ6hT-M_s3r-1aExd` | EXISTS |
| `/DEFHS/knowledge/checkpoint_metadata/` | `1u8yt5id6rerFFKfsJNLWkbbkLiSIHNeX` | EXISTS |
| `/DEFHS/knowledge/datasets/` | `16FuCNx7VJepDnwaLCNMTLYBPesJ7otbu` | EXISTS |
| `/DEFHS/knowledge/supplements/` | `13fYlYvDzgkL5KMuwWRy4RLGeCpey3xXW` | EXISTS |
| `/DEFHS/knowledge/competition_solutions/` | `1iaKcby7Yq3HXT67LLsbjoifw9cb9R29q` | EXISTS |
| `/DEFHS/knowledge/pointer_only/` | `1iTlkYbho5Vkegm_NhVvTZLRAwUNiIfBn` | EXISTS |
| `/DEFHS/knowledge/manifests/` | `1Q8pVKD_YUGAgM2CyAmqZdJFn9Sk6uygU` | EXISTS |

## Verified manifest/control files in Drive

| File | Drive ID | Bytes |
|---|---|---:|
| `RS-DEFHS-KNOWLEDGE-ACQUISITION-001_packet.zip` | `1a3QzpBCtdZv5G1tz8CBh91fq1rMZPfsf` | 64,089 |
| `KNOWLEDGE_MANIFEST.csv` | `13bwInAcQ9dZsSV8ZowcnYO5pFuyrKMF1` | 53,614 |
| `DEFHS_KNOWLEDGE_SOURCE_MANIFEST_ORIGINAL.md` | `1ReIfX840vUH7ncB4S1ylm55K4fvPtsZ0` | 17,022 |
| `LICENSE_REGISTER.csv` | `1RqkDQcpzNn-dZyoorAlXBkJgsC6RFZ4F` | 21,240 |
| `DUPLICATE_SOURCE_MAP.csv` | `1PpTExRkJxEJGfK2u-vDhAggCIhuHVMT6` | 2,141 |
| `BHAVVAANI_PROVENANCE_RECONCILIATION.md` | `1E_2cYqECOu6vBdLq-ubKKoHr517DJCxk` | 2,702 |
| `SOURCE_COVERAGE_REPORT.md` | `1ydF6eE6_l9xpob7nf1BE88uZdDkpkhr0` | 3,171 |
| `MISSING_EVIDENCE_REGISTER.md` | `12TtKfwbMqogAK38oI3Xwd3Kvf9RAhG7a` | 2,284 |
| `POINTER_ONLY_REGISTER.md` | `1_YpYsFrn0PDCuFCg8og0YKZevUq7PS1x` | 13,193 |

The packet ZIP was rebuilt during recovery and contains no `.pyc` or `__pycache__` entry. Its SHA256 is `53956d73ee230e3619234c0f63dcf09c1e0f48affad79524ec3175cc193f382f`.

## External binary state

`papers/` and `repositories/` are still empty. The 17 records marked `PENDING_BINARY_HANDOFF` are the selected legally/reproducibly acquirable binary set. The current ChatGPT runtime cannot fetch those public binary URLs into a Drive-compatible file reference; local container DNS/rclone are unavailable.

The committed handoff script downloads only that pre-approved set, computes SHA256, uploads it with rclone, uploads the remaining lightweight manifests, and verifies the paper/repository copies.

Do not interpret a target path in `KNOWLEDGE_MANIFEST.csv` as proof that the corresponding external binary exists until post-handoff Drive readback succeeds.
