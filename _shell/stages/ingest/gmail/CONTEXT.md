# Stage: ingest-gmail

> **Authoritative data spec**: `format.md` (paths, frontmatter, body, pre-filter, dedup).
> **sources.yaml schema**: `sources-schema.md` (locked in §3).
> **Operator runbook**: `_shell/docs/runbook-gmail.md` (written in §9).
> **Credential layout**: `_shell/docs/credentials-gmail.md` (written in §9).

## Inputs
| Source | Location | Why |
|---|---|---|
| Subscriptions | `workspaces/*/config/sources.yaml` (gmail block) | Per-mailbox union query + per-workspace routing |
| Cursor | `_shell/cursors/gmail/<mailbox-slug>.txt` | Last `historyId` per upstream mailbox |
| Credentials | `_credentials/gmail-<mailbox-slug>.json` | Authorized-user JSON, 1:1 with mailbox |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` | Per-workspace dedup by `gmail:<thread_id>` |

## Process
One robot run = one upstream mailbox. The dispatcher loops mailboxes via `--account-list`.

1. **flock** `/tmp/com.adithya.ultron.ingest-gmail-<mailbox-slug>.lock`. Concurrent run → exit 0 silently.
2. **Auth** from `_credentials/gmail-<mailbox-slug>.json`; build Gmail API client.
3. **Read cursor**.
   - First run (no cursor): `messages.list(q=<union>)` over `lookback_days_initial`. After: persist `historyId` from `users.getProfile`.
   - Subsequent: `users.history.list(startHistoryId=<cursor>, historyTypes=[messageAdded, messageDeleted, labelAdded, labelRemoved])`.
4. **Build union query** in Gmail q= syntax — OR of every subscribing workspace's `api_query.include`, AND with the union of `api_query.exclude`, AND with the universal blocklist (`format.md` § F).
5. **For each thread** (returned by list, or implicated by a history event):
   - Apply pre-filter (`format.md` § F).
   - Render thread → markdown (`format.md` § E).
   - Compute `content_hash` (blake3 of body).
   - `route(thread, workspaces_config) -> (destinations, matched_rules)` from `route.py`.
   - Per destination: skip if `(key, content_hash)` already in ledger; else write file at deterministic path (`format.md` § B) and append ledger row (`format.md` § G).
6. **History-event side-effects**:
   | Event | Action |
   |---|---|
   | `messageAdded` | Normal pipeline. |
   | `messageDeleted` | If file exists, set `deleted_upstream` in frontmatter and rewrite. Don't delete. |
   | `labelAdded` / `labelRemoved` | Re-evaluate routing. New matches → write to new workspaces. Existing copies stay. |
7. **Advance cursor** only after successful write phase. Mid-batch failure → cursor stays; next run replays.
8. **Per-workspace summary** appended to `workspaces/<ws>/_meta/log.md`.
9. **Deterministic post-run validation** via `_shell/bin/validate-gmail-run.py`: confirms every new file passes `check-frontmatter.py`, matches the deterministic path template, has a re-computable `content_hash`, has a ledger row, and that the cursor moved forward (or stayed). No LLM. Failures → `_logs/gmail-<mailbox-slug>-<run-id>.validation.log`, non-zero exit.

## Outputs
| Artifact | Location |
|---|---|
| Thread files | `workspaces/<ws>/raw/gmail/<mailbox-slug>/<YYYY>/<MM>/<file>.md` |
| Cursor | `_shell/cursors/gmail/<mailbox-slug>.txt` |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` |
| Workspace log | `workspaces/<ws>/_meta/log.md` |
| Per-run log | `_logs/gmail-<mailbox-slug>-<run-id>.log` |
| Validation log | `_logs/gmail-<mailbox-slug>-<run-id>.validation.log` (only on findings) |

## Out of scope (this phase)
LLM/vision attachment extraction; backfill beyond `lookback_days_initial`; cross-source dedup; multi-mailbox batching in one robot invocation.
