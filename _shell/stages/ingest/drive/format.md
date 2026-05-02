# Format: drive

## File granularity
One file per Drive file (Google Doc, PDF, etc.).

## Path
`workspaces/<ws>/raw/drive/<account-slug>/<YYYY>/<MM>/<slug>__<file_id8>.<ext>`

- `<YYYY>/<MM>` from `createdTime` (stable). `<slug>` from filename, kebab-case ASCII, max 60 chars.
- `<ext>`: `md` for Google Docs (exported), `pdf` for PDFs, original ext for others.

## Frontmatter

```yaml
---
source: drive
workspace: <ws-slug>
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: <blake3>
provider_modified_at: <ISO 8601>

account: <gmail-equivalent>
file_id: <Drive file id>
mime: application/vnd.google-apps.document
title: Original Drive title
parents: [<folder ids>]
parent_paths: ["Eclipse Labs / Sales", "Eclipse Labs / Vendors"]
owners: [{name: ..., email: ...}]
created: <ISO 8601>
size_bytes: 12345
---
```

## Body
For Google Docs: exported markdown. For PDFs: empty body (extraction deferred — body says `<binary, see file alongside>`). For images: empty body.

## Pre-filter
- Skip if `size_bytes > 50 MB`.
- Skip if mime outside allowlist: `application/vnd.google-apps.document`, `application/pdf`, `image/*`, `text/*`.
- Skip if `trashed: true`.

## Dedup key
`drive:<file_id>`. Same key + same content_hash → skip. Different hash → overwrite.
