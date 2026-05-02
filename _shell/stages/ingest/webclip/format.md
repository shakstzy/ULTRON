# Format: webclip (skeleton)

## File granularity
One markdown file per clipped page.

## Path
`workspaces/<ws>/raw/webclip/<YYYY>/<MM>/<title-slug>__<urlhash8>.md`

## Frontmatter

```yaml
---
source: webclip
workspace: <ws-slug>
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: <blake3>
provider_modified_at: <ISO 8601 of clipping>

url: https://example.com/article
title: ...
domain: example.com
author: ...
published_at: <ISO 8601>
tags: []
---
```

## Body
Markdown content extracted from the page (Defuddle, Reader-mode, or manual paste).

## Pre-filter
- Skip if domain on a denylist.
- Skip if page length > 200 KB rendered markdown.

## Dedup key
`webclip:<sha256-of-url>` — URL is provider-stable.
