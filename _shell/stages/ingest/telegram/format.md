# Format: telegram (skeleton)

## File granularity
One file per (chat, year-month).

## Path
`workspaces/<ws>/raw/telegram/{individuals|groups|channels}/<slug>/<YYYY>/<YYYY-MM>__<slug>.md`

## Frontmatter

```yaml
---
source: telegram
workspace: <ws-slug>
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: <blake3>
provider_modified_at: <ISO 8601 of last message>

chat_slug: <kebab>
chat_type: individual | group | channel
participants: [...]
month: 2026-04
message_count: 142
attachments: [...]
---
```

## Body
Day-grouped messages, same shape as iMessage.

## Pre-filter
Skip months > 5 MB; skip channels matching `*-bot` or `*notifications`.

## Dedup key
`telegram:<chat_slug>:<YYYY-MM>` — month granularity.
