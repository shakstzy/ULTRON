# Format: whatsapp (skeleton)

## File granularity
One file per (contact-or-group, year-month).

## Path
`workspaces/<ws>/raw/whatsapp/{individuals|groups}/<slug>/<YYYY>/<YYYY-MM>__<slug>.md`

## Frontmatter

```yaml
---
source: whatsapp
workspace: <ws-slug>
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: <blake3>
provider_modified_at: <ISO 8601 of last message in this month>

contact_slug: <kebab>
contact_type: individual | group
participants: [...]
month: 2026-04
message_count: 142
attachments: [...]
---
```

## Body
Day-grouped messages, same shape as iMessage format.md.

## Pre-filter
Same shape as iMessage — skip if month-batch > 5 MB.

## Dedup key
`whatsapp:<contact_slug>:<YYYY-MM>` — month granularity.
