# Heavy Artifact Manifests

Do not commit large datasets, checkpoints, embeddings, or prediction matrices.

For every important external artifact, create a lightweight JSON/YAML/Markdown
manifest containing at least:

- artifact ID/name
- storage URI/path
- size
- SHA-256 when practical
- producer experiment
- producing Git commit
- short description
