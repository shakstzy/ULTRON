# Stage: ingest-slack

> **Authoritative data spec**: `format.md` (paths, frontmatter, body,
> pre-filter, profiles, cursor, dedup, CLI, forbidden behaviors).
> **Operator runbook**: `SETUP.md` (Slack app provisioning, scopes,
> token install, rate limits, activation procedure).
> **Routing**: `route.py` (per-workspace channel + DM allowlist).

## Inputs

| Source | Location | Why |
|---|---|---|
| Subscriptions | `workspaces/*/config/sources.yaml` (slack block) | Per-channel + per-DM allowlist + per-workspace routing |
| Cursor | `_shell/cursors/slack/<workspace-slug>/<container-slug>.txt` | Last seen Slack `ts` per (workspace, container) |
| Self-id cache | `_shell/cursors/slack/<workspace-slug>/me.txt` | `auth.test` user_id → `adithya-shak-kumar` mapping |
| Credentials | `_credentials/slack-<workspace-slug>.json` | xoxp user token + team_id + scopes |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` | Per-workspace dedup keyed by `slack:<team>:<container>:<YYYY-MM-DD>` |
| Lookback | `ULTRON_SLACK_LOOKBACK_DAYS` env var | First-run window when cursor absent (default 365) |

## Process

One robot run = one Slack workspace. Multi-workspace scheduling is the
launchd / cron layer's job: one plist per workspace-slug.

1. **flock** `/tmp/com.adithya.ultron.ingest-slack-<workspace-slug>.lock`.
   Concurrent run → exit 0 silently.
2. **Auth** from `_credentials/slack-<workspace-slug>.json`. Call
   `auth.test`; cache `user_id → adithya-shak-kumar` in `me.txt`.
   Warn if `me.txt` already records a different user_id.
3. **Workspace profile**: read or create
   `<workspace-slug>/_profile.md`; refresh `team.info` snapshot.
4. **Discover containers**: `conversations.list(types="public_channel,
   private_channel,im,mpim")` — all channels the user token can see.
   Channel allowlist filtering happens in routing (`route.py`), not
   here.
5. **For each container**:
   - Read cursor; on missing, bound by `ULTRON_SLACK_LOOKBACK_DAYS`.
   - `conversations.history(oldest=cursor)`, paginate.
   - For every message with `thread_ts`: call
     `conversations.replies` once per parent (cache within the run to
     avoid N+1 explosion).
   - Apply universal pre-filter (`format.md` Lock 6).
   - Resolve user display names via `users.info` (cache per run).
   - On `not_found` / `channel_not_found`: mark
     `container_archived: true` on `_profile.md`, continue.
   - On `429`: exponential backoff + jitter, max 5 retries, then
     defer the container to a per-run deferred queue and continue.
6. **Bucket** every message by `(container, local-date)`. Threads
   bucket with their parent message's date.
7. **For each (container, date) bucket**:
   - Apply edit (`message_changed`) and deletion (`message_deleted`)
     state transitions per `format.md` Lock 6.
   - Render markdown per `format.md` Lock 5.
   - Compute `content_hash` (blake3 of body markdown only).
   - `route(item, workspaces_config) → list[ws]` from `route.py`.
   - Per destination: skip if `(key, content_hash)` matches existing
     ledger row; else write file at deterministic path
     (`format.md` Lock 1) and append ledger row (`format.md` Lock 8).
8. **Profile updates**: append new members / display-name aliases to
   the relevant `_profile.md`. Never delete prior entries.
9. **Advance cursors** atomically per container, only AFTER the write
   phase for that container succeeds.
10. **Per-workspace summary** appended to
    `workspaces/<ws>/_meta/log.md`.
11. **Self-review** writes anomalies to
    `_shell/runs/<RUN_ID>/self-review.md`: 429 deferrals, archived
    containers, route misses, scope-denied API calls.

## Outputs

| Artifact | Location |
|---|---|
| Day files | `workspaces/<ws>/raw/slack/<workspace-slug>/{channels\|dms\|group-dms}/<slug>/<YYYY>/<MM>/<YYYY-MM-DD>__<slug>.md` |
| Workspace profile | `workspaces/<ws>/raw/slack/<workspace-slug>/_profile.md` |
| Container profiles | `<...>/{channels\|dms\|group-dms}/<slug>/_profile.md` |
| Cursors | `_shell/cursors/slack/<workspace-slug>/<container-slug>.txt` + `me.txt` |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` |
| Workspace log | `workspaces/<ws>/_meta/log.md` |
| Self-review | `_shell/runs/<RUN_ID>/self-review.md` |

## Out of scope (this stage)

LLM / vision attachment extraction; attachment binary copies;
reaction rendering; full edit-history reconstruction; cross-source
dedup (Slack ↔ iMessage ↔ WhatsApp); voice-clip transcription;
fetch-time channel allowlist (routing-time filter only in v1).

## Status

Skeleton. `_shell/bin/ingest-slack.py` has `IMPLEMENTATION_READY = False`.
Activation is a later session. See `SETUP.md` for the flip-on procedure.
