# Data Access Authority

## Canonical raw archive

- Google Drive folder: `/DEFHS/raw`
- Google Drive folder ID: `1g5ikVyvAQhnBxBHj7MEfoguGFHRL_3F8`
- Google Drive file: `dataverse-detecting-emotions-from-hindi-speech.zip`
- Google Drive file ID: `1D0DcnbK0vrJGTsvtb7-l7vnpdfNxc-nH`
- Size: `99,298,085 bytes`
- SHA-256: `100b38e6ed69542df88c1d295932a7a4c1914cd931ee64f7c6c848f6053bf214`

The ZIP remains the immutable provenance authority. DS must verify the SHA-256
of any downloaded/local ZIP before treating it as canonical.

## Verified extracted mirror

For direct EDA access, a byte-derived extracted mirror is available in Drive:

- Google Drive path: `/DEFHS/competition_extracted`
- Google Drive folder ID: `1d4A0b7_t_kUSwkyZkJ6al3R-vzwmHmvq`
- expected files: `1,038`
- expected WAV files: `1,035`
- verification: `rclone check` returned `0 differences` and `1,038 matching files`
- terminal verdict: `DEFHS_EXTRACTED_DRIVE_MIRROR=PASS`

Canonical local WSL working copy:

`/home/fikar/zingle/defhs/data/raw/competition/SRCASW-BhavVaani`

The extracted mirror is a convenience/work-recovery artifact; the ZIP checksum
remains the provenance authority.

Canonical manifest:

`manifests/DEFHS_COMPETITION_DATA_20260930.json`

Heavy derived artifacts (speaker embeddings, ASR transcripts, acoustic feature
matrices, SSL embeddings, etc.) should live in Google Drive or another approved
external store and be referenced by lightweight GitHub manifests/checksums.
