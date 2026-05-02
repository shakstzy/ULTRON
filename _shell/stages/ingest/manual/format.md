# Format: manual

## File granularity
One file per dropped artifact.

## Path
`workspaces/<ws>/raw/<source-id>/<YYYY-MM>/<slug>.<ext>`

`<source-id>` is set in the workspace's `sources.yaml` (`id: manual-notes`, `id: plaid-export`, `id: apple-health`, etc.). `<slug>` is derived from the original filename — kebab-case ASCII, max 60 chars.

## Frontmatter
Manual sources do NOT enforce the universal frontmatter envelope on the file body itself (the user might drop arbitrary files: PDFs, screenshots, CSVs). Instead, the universal envelope lives in the `ingested.jsonl` row.

## Pre-filter
None at ingest time (the user owns what they drop). Lint flags suspect files later.

## Dedup key
`manual:<source_id>:<basename>` — once a filename moves out of `_inbox/`, dropping the same name again creates a `<basename>-2.<ext>` to avoid clobbering.
