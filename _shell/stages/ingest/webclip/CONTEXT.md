# Stage: ingest-webclip

## Status
Skeleton. Future: Obsidian Web Clipper or manual web saves.

## Planned shape
- Watch a global `_inbox/` (e.g., `~/ULTRON/_inbox/webclip/`) OR per-workspace `raw/webclip/_inbox/`.
- For each new clip (markdown with frontmatter `url`, `title`, `clipped_at`):
  - Apply pre-filter (size cap, domain blocklist).
  - Compute content_hash.
  - Call `route.py` to determine destination workspaces (route by URL pattern + tag).
  - Write to `workspaces/<ws>/raw/webclip/<YYYY>/<MM>/<title-slug>__<urlhash8>.md`.

## Out of scope for v1
Wiring to Obsidian Web Clipper, browser extensions, RSS feeds.
