# Format: <source> (template)

## File granularity
<one file per WHAT — message? thread? day? contact?>

## Path
`workspaces/<ws>/raw/<source>/<account-slug-if-any>/<YYYY>/<MM>/<slug>.md`

Re-runs OVERWRITE the same file. Stable filename = idempotent ingest.

## Frontmatter (universal envelope + source-specific)

```yaml
---
# Universal envelope (REQUIRED)
source: <source>
workspace: <ws-slug>
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: <blake3>
provider_modified_at: <ISO 8601>

# Source-specific keys
# ... add what this source needs ...

# Lifecycle (when applicable)
deleted_upstream: null
superseded_by: null
---
```

## Body
Plain markdown. Source-specific structure documented here.

## Pre-filter (deterministic, NO LLM)
Skip if:
- (size cap)
- (sender / source / type blocklist)
- (irrelevant labels / categories)

## Dedup key
`<source>:<provider-stable-id>` — recorded in workspace `_meta/ingested.jsonl`.

Re-ingest behavior:
- Same key + same content_hash → skip (no-op).
- Same key + different content_hash → overwrite (item changed upstream).
