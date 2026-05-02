# Format: apple-health (skeleton)

## File granularity
One markdown file per (`metric_type`, `YYYY-MM`). Examples: `weight/2026-04.md`, `resting-heart-rate/2026-04.md`, `sleep/2026-04.md`.

## Path
`workspaces/<ws>/raw/apple-health/<metric-slug>/<YYYY>/<YYYY-MM>.md`

## Frontmatter

```yaml
---
source: apple-health
workspace: <ws-slug>
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: <blake3>
provider_modified_at: <ISO 8601 of last reading>

metric_type: weight                # weight | resting-heart-rate | hrv | sleep | active-energy | ...
metric_slug: weight
units: lb                          # mandatory; per-metric
month: 2026-04
reading_count: 27
date_range: [2026-04-01, 2026-04-29]
---
```

## Body
Daily aggregates as a markdown table, one row per day with min/max/avg.

## Pre-filter
Skip files larger than 250 MB (the full export is ~1 GB; we expect month-slices, not raw export dumps).

## Dedup key
`apple-health:<metric_slug>:<YYYY-MM>` — month granularity.
