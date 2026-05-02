# Stage: ingest-slack

## Inputs
| Source | File / Location | Why |
|---|---|---|
| Workspace slack subscriptions | `workspaces/*/config/sources.yaml` (slack block) | Channels + DM allowlist + routing |
| Format spec | `_shell/stages/ingest/slack/format.md` | Output shape |
| Cursor | `_shell/cursors/slack/<workspace_id>.txt` | Last `oldest` ts per channel/DM (JSON map) |
| Credentials | `_credentials/slack-<workspace_id>.json` | `{token, team_id}` (bot or user) |
| Dedup ledger | `workspaces/<ws>/_meta/ingested.jsonl` | Per-workspace dedup |

## Process
1. Discover slack subscriptions; group by `workspace_id` (Slack team).
2. For each team: load creds; build the WebClient.
3. For each subscribed channel / DM:
   a. Page through `conversations.history` since cursor.
   b. For each message thread: fetch `conversations.replies` if it has thread replies.
   c. Group messages by day per `format.md` (one file per channel-day).
   d. Apply pre-filter; render markdown; compute content_hash; route; write.
4. Advance cursor (latest ts seen per channel) to `_shell/cursors/slack/<workspace_id>.txt` as JSON `{channel_id: ts}`.

## Outputs
Slack channel-day files; cursor JSON; ledgers; log.

## Self-review
Envelope, cursor, ledger, route outputs.

## Status
Skeleton. Robot exits cleanly without credentials.
