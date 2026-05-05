# Stage: ingest-granola

> **Authoritative data spec**: `format.md` (paths, frontmatter, body,
> pre-filter, dedup, cursor, auth, endpoints). This file is the
> workflow contract.

## Inputs

| Source | Location | Why |
|---|---|---|
| Subscriptions | `workspaces/*/config/sources.yaml` (granola block) | Per-workspace folder allowlist |
| Cursor | `_shell/cursors/granola/<account-slug>.txt` | Latest `updated_at` ingested per upstream account |
| Credentials | `~/Library/Application Support/Granola/supabase.json` | Granola desktop app's WorkOS access_token + refresh_token |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` | Per-workspace dedup by `granola:<document_id>` |

The credentials file is owned by the Granola desktop app. We read it cold each run; we only write it back when forced to refresh ourselves (401 path, atomic replace).

## Process

One robot run = one upstream Granola account. Multi-account scheduling is the launchd / cron layer's job: one plist per account-slug. (Granola accounts are 1:1 with desktop installs in current scope, so v1 only supports the single local account.)

1. **flock** `/tmp/com.adithya.ultron.ingest-granola-<account-slug>.lock`. Concurrent run → exit 0 silently.
2. **Auth** — read `workos_tokens.access_token` from `supabase.json`. On 401 from any API call, re-read the file (the desktop app may have refreshed it since we started). If still 401, do a WorkOS refresh ourselves (`format.md` Lock 7), atomic-write the new tokens back, retry once. Two consecutive 401s → fail loudly.
3. **Read cursor**.
   - Missing/empty → first-run: ingest every doc that matches a subscribed folder.
   - Present → incremental: ingest only docs where `updated_at > cursor`.
4. **List folders** — `POST /v1/get-document-lists-metadata` with `{include_document_ids: true, include_only_joined_lists: false}`. Build the maps `folder_id → folder_title` and `document_id → [folder_titles]`.
5. **Build subscribed-doc-id set** — for each workspace `ws` in the global config, for each folder title in `ws.granola.folders`, union the folder's `document_ids`. The robot only fetches docs in this union.
6. **Fetch docs in batches of 20** — `POST /v1/get-documents-batch` with `{document_ids: [...]}`.
7. **For each doc**:
   - Apply pre-filter (`format.md` Lock 5).
   - Fetch transcript: `POST /v1/get-document-transcript` with `{document_id}`. Skip doc if 0 final segments (Lock 5).
   - Render doc → markdown (`format.md` Lock 4).
   - Compute `content_hash` (blake3 of body).
   - `route(doc, workspaces_config) → list[{workspace, rule}]` from `route.py`.
   - Per destination: skip if `(key, content_hash)` already in ledger; else write at deterministic path (`format.md` Lock 1) and append ledger row (`format.md` Lock 6).
8. **Advance cursor** to the max `updated_at` across all successfully written docs. Only after the write phase finishes. Mid-batch failure → cursor stays; next run replays.
9. **Per-workspace summary** appended to `workspaces/<ws>/_meta/log.md`.

## Outputs

| Artifact | Location |
|---|---|
| Doc files | `workspaces/<ws>/raw/granola/<account-slug>/<YYYY>/<MM>/<file>.md` |
| Cursor | `_shell/cursors/granola/<account-slug>.txt` |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` |
| Workspace log | `workspaces/<ws>/_meta/log.md` |
| Per-run log | `_logs/granola-<account-slug>-<run-id>.log` |
| Error log | `_logs/granola-errors-<date>.log` |

## Self-review

- [ ] Path is deterministic: same `(account_slug, document_id, created_at, title)` → same file.
- [ ] Re-running is idempotent. Same key + same `content_hash` does not rewrite.
- [ ] Cursor only advances on successful writes; next run replays on mid-batch failure.
- [ ] No doc is fetched twice in one run (folder→docs union dedups).
- [ ] No transcript-less doc is written (Lock 5 enforces).
- [ ] Refresh-token write is atomic (`os.replace` from sibling tmp file).

## Out of scope (this stage)

Recipes / templates content; chat-with-document threads; YDoc CRDT state; multi-account batching in one robot invocation; backfill of trashed/deleted docs; LLM enrichment of body markdown.
