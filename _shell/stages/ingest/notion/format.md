# Format: notion

## File granularity
One markdown file per Notion page. Every database row IS a page in Notion's API and becomes its own file.

A page with zero `child_page` / `child_database` blocks → single file at the parent dir.
A page with subpages or subdatabases → folder named after the page; the page itself lives at `index.md` in that folder; children land alongside.

A database → folder; `index.md` is a wikilink listing of its rows; each row → its own file in the folder.

## Path
```
workspaces/<ws>/raw/notion/<target-label>/<slug>__<id8>.md            # leaf page
workspaces/<ws>/raw/notion/<target-label>/<slug>__<id8>/index.md      # page-with-subpages or DB
workspaces/<ws>/raw/notion/<target-label>/<slug>__<id8>/_assets/<block-id8>.<ext>  # downloaded images
```

`<target-label>` is the workspace's chosen folder name (from `sources.yaml`) or a slug of the root page title. `<id8>` is the first 8 hex chars of the dash-stripped Notion UUID.

Re-runs OVERWRITE the same file. Stable filename = idempotent ingest.

## Frontmatter (universal envelope + notion-specific)

```yaml
---
# Universal envelope
source: notion
workspace: <ws-slug>
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: blake3:<hex>
provider_modified_at: <ISO 8601 page.last_edited_time>

# Notion identity
notion_page_id: <32-char hex, no dashes>
notion_page_id_dashed: <UUID with dashes>
notion_kind: page | db_index | db_row
notion_target_label: <root target label>
notion_url: <notion.so URL>
notion_title: <page title>
notion_parent_path: ["target-label", ..., "parent-page-title"]
notion_created_at: <ISO 8601>
notion_last_edited_at: <ISO 8601>
notion_archived: bool

# Database rows only
notion_properties:
  <prop name>: <rendered value>
  ...
---
```

## Body
Notion blocks rendered to markdown. Coverage:

| Notion block | Markdown |
|---|---|
| `paragraph` | plain text (with inline annotations: bold, italic, code, strike, link) |
| `heading_1/2/3` | `#`, `##`, `###` |
| `bulleted_list_item` | `- ` |
| `numbered_list_item` | `1. ` |
| `to_do` | `- [ ] ` / `- [x] ` |
| `toggle` | `<details><summary>...</summary>...</details>` |
| `quote` | `> ` |
| `callout` | `> <emoji> ` (preserves icon) |
| `code` | fenced code block with language |
| `divider` | `---` |
| `equation` | `$$ ... $$` |
| `bookmark` / `embed` / `link_preview` | markdown link |
| `image` | `![<vlm-description-or-caption>](_assets/<id8>.<ext>)` |
| `video` / `audio` | `[<caption>](url)` — no VLM, no download |
| `file` / `pdf` | `📎 **<name>** _(notion file)_` — metadata-only, NO download |
| `child_page` | `[[<slug>__<id8>\|<title>]]` wikilink |
| `child_database` | `[[<slug>__<id8>/index\|<title>]]` wikilink |
| `synced_block` | rendered once (deduplicated by source block id) |
| `column_list` | columns concatenated vertically |
| `table` | github-flavored markdown table |

Database rows additionally render a leading `| Property | Value |` table from their `notion_properties`.

Anything unsupported renders as `[unrendered:<type>]` so it's not silently dropped.

## Pre-filter
- Skip `archived: true` pages (use `--force` to override).
- Skip pages whose `last_edited_time` matches the existing file's `provider_modified_at`.

## Dedup key
`notion:<page_id>` — UUID is provider-stable. `<id8>` collisions extremely unlikely; if one occurs the runner overwrites whichever page wrote last (collision-laddering not implemented in v1).

## Image / file policy
- **Image blocks** → downloaded, fed to Gemini Flash via cloud-llm, alt-text capped at 120 chars.
- **File / PDF / video / audio blocks** → metadata-only line. No bytes pulled. Notion's signed URLs expire in ~1h so embedding them is not durable.
