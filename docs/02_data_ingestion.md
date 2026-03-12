# 02 Data Ingestion

## Supported sources

- NFS-mounted shares
- Google Drive
- Local Markdown, PDFs, DOCX, HTML, TXT
- Email via `mbox`, `.eml`, Gmail export, or IMAP
- Linkwarden exports
- Spreadsheets
- Code repositories
- Architecture notes and operational documentation

## Pipeline stages

1. Source discovery and raw acquisition
2. Snapshot to `data/raw/` for reproducibility
3. Text extraction
4. Deduplication
5. Metadata enrichment
6. Domain classification
7. Chunking
8. Manifest and Parquet export
9. Embedding for retrieval

## Default commands

```bash
uv run personal-llm ingest --config config/sources.yaml
uv run personal-llm extract
uv run personal-llm classify-domains
uv run personal-llm embed
```

## Source-specific notes

- NFS works through the `local_files` connector. Mount the share on your Mac and point the configured path at the mount point, for example `/Volumes/KnowledgeShare`.
- Local and NFS files are snapshotted into `data/raw/` before extraction. This is the recommended best practice because it preserves a stable training and indexing input even if the source share changes later.
- Google Drive supports incremental changes through stored page/change tokens.
- Email ingestion preserves thread, sender, recipients, timestamps, and attachment metadata.
- The simplest email path is file-based ingestion:
  - `mbox` if you have mailbox exports
  - `.eml` directories if you have one-message-per-file exports
  - Gmail Takeout if you exported from Gmail
- IMAP is optional and only needed when you want direct mailbox sync.
- Linkwarden ingestion keeps URL, tags, archive references, and collection metadata.
- Code repositories prioritize README files, ADRs, infra code, CI files, and key modules rather than embedding every binary or vendored file.

## Recommended first ingestion setup

For the first version of the system, prefer:

1. `local_files` pointing at a local folder or NFS mount
2. `email.mbox_paths` pointing at mailbox exports, or `.eml` files inside `local_files`
3. Linkwarden export JSON if you use Linkwarden

Use Google Drive and IMAP only if you specifically need live API-based sync.

## Privacy

- `data/raw/` should be treated as highly sensitive.
- Use `config/security.yaml` to define retention, encryption, and export policies.

## Quality control

Ingestion is only the mechanical part of the system. Before you promote extracted content into training data, review:

- [docs/13_data_quality.md](13_data_quality.md) for duplicate, contradiction, freshness, and source-trust rules
- [docs/11_personal_knowledge.md](11_personal_knowledge.md) for what belongs in curated knowledge versus raw RAG-only content
