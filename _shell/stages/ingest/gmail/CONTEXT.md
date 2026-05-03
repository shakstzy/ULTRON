# Stage: ingest-gmail

> **Authoritative data spec**: `format.md` (paths, frontmatter, body,
> pre-filter, dedup, cursor, CLI). This file is the workflow contract.

## Inputs

| Source | Location | Why |
|---|---|---|
| Subscriptions | `workspaces/*/config/sources.yaml` (gmail block) | Per-account union query + per-workspace routing |
| Cursor | `_shell/cursors/gmail/<account-slug>.txt` | Last `historyId` per upstream account |
| Credentials | `_credentials/gmail-<account-slug>.json` | Authorized-user JSON, 1:1 with mailbox |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` | Per-workspace dedup by `gmail:<thread_id>` |
| Lookback window | `GMAIL_INITIAL_LOOKBACK_DAYS` env var | First-run window when cursor absent (default 365) |

## Process

One robot run = one upstream account. Multi-account scheduling is the
launchd / cron layer's job: one plist per account-slug.

1. **flock** `/tmp/com.adithya.ultron.ingest-gmail-<account-slug>.lock`.
   Concurrent run → exit 0 silently.
2. **Auth** from `_credentials/gmail-<account-slug>.json`; build Gmail
   API client. On `invalid_grant`: fast-fail with recovery message.
3. **Read cursor**.
   - Missing/empty → first-run path: `users.messages.list(q=<union>)`
     with `after:` derived from `GMAIL_INITIAL_LOOKBACK_DAYS`.
   - Present → incremental path:
     `users.history.list(startHistoryId=<cursor>, historyTypes=[
     messageAdded, messageDeleted, labelAdded, labelRemoved])`.
4. **Build union query** (first-run only) in Gmail q= syntax: OR of
   every subscribing workspace's `api_query.include`, AND with the
   union of `api_query.exclude`, AND with `-in:trash -in:spam` plus
   the universal blocklist (`format.md` Lock 5).
5. **For each thread** (returned by list, or implicated by a history
   event):
   - Apply pre-filter (`format.md` Lock 5).
   - Render thread → markdown (`format.md` Lock 4).
   - Compute `content_hash` (blake3 of body).
   - `route(thread, workspaces_config) → list[{workspace, rule}]` from
     `route.py`.
   - Per destination: skip if `(key, content_hash)` already in ledger;
     else write file at deterministic path (`format.md` Lock 1) and
     append ledger row (`format.md` Lock 6).
6. **History-event side-effects**:

   | Event | Action |
   |---|---|
   | `messageAdded` | Normal pipeline. |
   | `messageDeleted` | If file exists, set `deleted_upstream` in frontmatter; rewrite. Don't delete the file. |
   | `labelAdded` / `labelRemoved` | Update `labels` in existing files; re-evaluate routing. New matches → write to new workspaces. Existing copies stay. |

7. **Advance cursor** to `users.getProfile().historyId` only after the
   write phase succeeds. Mid-batch failure → cursor stays; next run
   replays.
8. **Per-workspace summary** appended to
   `workspaces/<ws>/_meta/log.md`.

## Outputs

| Artifact | Location |
|---|---|
| Thread files | `workspaces/<ws>/raw/gmail/<account-slug>/<YYYY>/<MM>/<file>.md` |
| Cursor | `_shell/cursors/gmail/<account-slug>.txt` |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` |
| Workspace log | `workspaces/<ws>/_meta/log.md` |
| Per-run log | `_logs/gmail-<account-slug>-<run-id>.log` |
| Error log | `_logs/gmail-errors-<date>.log` |

## Out of scope (this stage)

LLM / vision attachment extraction; backfill beyond
`GMAIL_INITIAL_LOOKBACK_DAYS`; cross-source dedup; multi-account
batching in one robot invocation.
