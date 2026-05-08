# Stage: ingest-discord

> Cron-driven refresh of Discord DMs and group DMs already known to ULTRON.
> The skill's `ingest` verb (at `~/.claude/skills/discord/scripts/run.mjs`)
> does the heavy lifting; this substage's robot only iterates the watermark
> files and re-invokes the skill.

## Inputs
| Source | Location | Why |
|---|---|---|
| Watermarks | `workspaces/*/raw/.ingest-log/discord/*.json` | Per-channel watch list. Each watermark → one re-pull. |
| Skill | `~/.claude/skills/discord/scripts/run.mjs ingest <channel_id> --workspace <ws>` | Authoritative ingest path. Handles delta/skip-write internally via month-level `content_hash`. |
| Auth | `~/ULTRON/_credentials/browser-profiles/discord/` | Persistent Chrome profile cookies. No bot token. Refresh via `node run.mjs login` if breaker trips. |

## Process
1. **flock** `/tmp/com.adithya.ultron.ingest-discord-default.lock`. Concurrent run exits 0 silently.
2. **Discover watch list**. Glob `workspaces/*/raw/.ingest-log/discord/*.json`. Each file = one channel (1:1 DM or group DM) on Adithya's auto-refresh roster. To stop tracking a channel, delete its watermark + folder. To start tracking, run `node run.mjs ingest <name> --workspace <ws>` once manually.
3. **Per-channel re-pull**. Sequential (Discord rate limits + ban-aversion). Spawn `node run.mjs ingest <channel_id> --workspace <ws>`. Skill's `content_hash` skip-write keeps writes idempotent — touched-but-unchanged months are no-ops.
4. **Failure isolation**. A single channel failing (401, 403, network, etc.) does NOT abort siblings. Errors logged; robot exit is non-zero only if any sub-run failed.
5. **Breaker**. Skill itself trips a 24h breaker on 401/403. Cron sees a non-zero exit and surfaces in cron-ledger; next run reads breaker and short-circuits until manual `node run.mjs login`.

## Outputs
| Artifact | Location |
|---|---|
| Month files | `workspaces/<ws>/raw/discord/{individuals,groups}/<slug>/<YYYY>/<YYYY-MM>__<slug>.md` |
| Watermark | `workspaces/<ws>/raw/.ingest-log/discord/<slug>.json` (overwritten each successful run) |
| Cron log | `_logs/com.adithya.ultron.ingest-discord-default.{out,err}.log` |

## Forbidden behaviors
1. Never run unattended on a channel without an existing watermark — manual seed required (prevents accidental ingest of every Discord conversation in history).
2. Never delete a watermark or month file based on Discord-side deletion — same archival contract as iMessage.
3. Never call the skill's `dm` or `group` (send) verbs from this robot — read-only path.
4. Never bypass the skill's flock or breaker by hitting Discord REST directly.

## Self-review
- Every watermark on disk produced exactly one sub-run (or one logged skip with reason).
- Sub-runs that wrote new months show up in the month-files list with current ISO timestamps.
- No 401/403 in logs. If present, breaker tripped → halt advice surfaced to Adithya.
