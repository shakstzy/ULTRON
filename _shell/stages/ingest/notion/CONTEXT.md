# Stage: ingest-notion

## Status
Implemented. Single integration token in macOS Keychain (`service=quantum-notion, account=default`). The integration must be invited to each target page or database.

## Inputs
| Source | File / Location | Why |
|---|---|---|
| Workspace targets | `workspaces/<ws>/config/sources.yaml` → `sources.notion.targets` | List of root pages / databases per workspace |
| Integration token | macOS Keychain (`quantum-notion`) | Notion API auth |
| Existing raw files | `workspaces/<ws>/raw/notion/<label>/...md` | Per-file frontmatter `provider_modified_at` is the cursor |
| cloud-llm skill | `~/.claude/skills/cloud-llm/client.py` | VLM for image blocks |

## Process
1. Load token from Keychain. Verify with `GET /users/me`.
2. Load each subscribed workspace's `sources.yaml` notion block.
3. For each `target` (page or database):
   - Auto-detect kind if hint missing (`get_page` → fall back to `get_database`).
   - Pages: list block children (paginated), recurse into `child_page` and `child_database` blocks.
   - Databases: query rows (paginated), each row treated as a page.
4. For each page:
   - Compare `last_edited_time` to existing file's `provider_modified_at`. Skip if matched.
   - Render blocks → markdown per `format.md`.
   - Image blocks → download to `<page-dir>/_assets/<block-id8>.<ext>`, describe via cloud-llm Gemini Pro/Flash, embed as alt-text.
   - File / PDF / video / audio blocks → metadata-only line, no download, no VLM.
5. Atomic write `.md` (tmp + rename).

## Outputs
| Artifact | Location | Format |
|---|---|---|
| Per-page markdown | `workspaces/<ws>/raw/notion/<label>/...md` | Universal envelope + notion fields per `format.md` |
| Image assets | `workspaces/<ws>/raw/notion/<label>/.../_assets/<block-id8>.<ext>` | original bytes |
| Run log | `_logs/ingest-notion-<run-id>.log` | JSONL |

## Invocation
```bash
# Per-workspace config-driven (cron form):
_shell/bin/ingest-notion.py --workspace synapse

# Ad-hoc against one URL/ID:
_shell/bin/ingest-notion.py --workspace synapse --url <notion-url-or-id>

# Skip the VLM pass:
_shell/bin/ingest-notion.py --workspace synapse --no-vlm

# Re-render every page even if unchanged:
_shell/bin/ingest-notion.py --workspace synapse --force
```

## Self-review
- Verify universal frontmatter envelope on every new file.
- Verify `provider_modified_at` matches `last_edited_time` from API.
- Verify image alt-text under 120 chars; assets present at expected paths.
- Verify wikilinks for `child_page` / `child_database` resolve to actual files.
