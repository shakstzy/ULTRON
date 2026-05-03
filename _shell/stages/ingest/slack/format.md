# Format: slack (AUTHORITATIVE)

> Locked. Every Slack file written by `ingest-slack.py` must conform
> to this spec exactly. The 9 locks below are the contract.

## Lock 1 — Path template

Channels:
```
workspaces/<ws>/raw/slack/<workspace-slug>/channels/<channel-name>/<YYYY>/<MM>/<YYYY-MM-DD>__<channel-name>.md
```

DMs (1:1):
```
workspaces/<ws>/raw/slack/<workspace-slug>/dms/<other-user-slug>/<YYYY>/<MM>/<YYYY-MM-DD>__<other-user-slug>.md
```

Group DMs:
```
workspaces/<ws>/raw/slack/<workspace-slug>/group-dms/<group-id-short>/<YYYY>/<MM>/<YYYY-MM-DD>__<group-id-short>.md
```

`<YYYY>/<MM>/<YYYY-MM-DD>` is the **local-timezone date of the file's
earliest message**. Threads spanning midnight stay in the start-date
file. Re-ingesting today rewrites today's file deterministically.

`<group-id-short>` = first 8 chars of Slack's stable group conversation
ID, lowercased (e.g., `g07abc12`). NOT participant-derived; survives
membership churn.

## Lock 2 — Slug derivation

**Workspace slug**: from `team.info` API at first ingest. Recorded in
the workspace `_profile.md`, stable forever. `Eclipse Labs` →
`eclipse-labs`.

**Channel slug**: strip leading `#`, lowercase, ASCII-fold. Use the
current `channel.name` from `conversations.info`, NOT the channel ID.
Renames change the path prospectively; old files stay at the old name;
rename history lives in the channel `_profile.md`.

**User slug** (priority order, locked at first sight, recorded in the
relevant `_profile.md`):
1. `display_name` → kebab-case ASCII, max 40 chars (`Sydney Hayes` →
   `sydney-hayes`).
2. `real_name` if no display name.
3. `profile.email` local-part + domain stem (`sydney@eclipse.audio` →
   `sydney-eclipse`).
4. Slack user ID lowercased (`U02ABC123` → `u02abc123`).

**`me` / self**: ALWAYS `adithya-shak-kumar` (canonical cross-source
identity). Auto-detected on robot startup via `auth.test`; the
`user_id → canonical_slug` mapping is cached in
`_shell/cursors/slack/<workspace-slug>/me.txt`. The renderer swaps the
detected user_id for the canonical slug at every render.

**Group DM slug**: ALWAYS `group-id-short`. Member churn does NOT
change it. Member snapshots live in the group DM `_profile.md`.

## Lock 3 — Universal frontmatter envelope (REQUIRED)

```yaml
source: slack
workspace: <ws-slug>
ingested_at: <ISO 8601 with TZ>
ingest_version: 1
content_hash: blake3:<64-hex>          # of body markdown only
provider_modified_at: <ISO 8601 with TZ>   # ts of last message in file
```

## Lock 4 — Slack-specific frontmatter

```yaml
slack_workspace_slug: eclipse-labs
slack_workspace_id: T02ABC123
container_type: channel                # channel | dm | group-dm
container_slug: deals                  # channel-name | other-user-slug | group-id-short
container_id: C02XYZ456
date: 2026-04-15
date_range:
  first: 2026-04-15T09:14:00-05:00
  last: 2026-04-15T17:42:00-05:00
message_count: 38                      # excludes thread replies + bots
thread_count: 4
participant_count: 6
participants:
  - { slug: sydney-hayes, slack_user_id: U02ABC, display_name: "Sydney Hayes",
      real_name: "Sydney Hayes", email: "sydney@eclipse.audio" }
attachments:                           # metadata-only; never copied
  - id: F02ABC456                      # Slack file ID
    filename: tier-2-pricing.pdf
    size_bytes: 1234567
    mime: application/pdf
    sender_slug: sydney-hayes
    sent_at: 2026-04-15T14:31:00-05:00
    permalink: https://eclipse-labs.slack.com/files/U02ABC/F02ABC456/tier-2-pricing.pdf
    private_url: https://files.slack.com/files-pri/T02ABC-F02ABC456/tier-2-pricing.pdf
deleted_messages:
  - { ts: "1713196800.000100", deleted_at: "2026-04-15T15:02:11-05:00" }
edited_messages_count: 3
chat_db_message_ids: null              # not applicable to Slack
deleted_upstream: null                 # set only if container deleted
container_archived: false
```

Field rules: only `deleted_messages`, `edited_messages_count`,
`container_archived`, and `deleted_upstream` may be modified post-write.
`participants[].display_name` is a snapshot at the time of the latest
message in the file; durable history lives in `_profile.md`.

## Lock 5 — Body format

```markdown
# #deals — 2026-04-15 (Wednesday)

## 14:23 — Sydney Hayes

Sandeep wants to discuss tier 2 pricing. Anyone got history?

> ### 14:25 — Marcus Lee
>
> Yeah we discussed in March. I'll find the doc.
>
> ### 14:31 — Sydney Hayes
>
> Found it. Sharing now.
>
> [file: tier-2-pricing.pdf — 1.2MB]

## 14:45 — Daniel Park

(separate, non-threaded message)
```

DM heading: `# DM with <Display Name> — YYYY-MM-DD (DayOfWeek)`.
Group DM heading: `# Group DM (<n>): <name1>, <name2>, ... — YYYY-MM-DD (DayOfWeek)`.

Conventions:
- One day per file → no internal `## YYYY-MM-DD` headers needed.
- Sender is `display_name` at the time of the message, OR
  `Adithya Kumar (me)` for self (slug `adithya-shak-kumar` lives in
  frontmatter only).
- Thread replies render inline at the parent message's location,
  chronologically, inside a `> ` quoted block, with `### HH:MM —` (one
  heading level deeper than the parent).
- Attachments inline at the moment sent: `[file: <filename> — <size>]`.
  No content extraction. No binary copy. Image-only messages are a
  bare `[file: ...]` line — no "Sender said:" filler.
- Edits: render the CURRENT text only. No `(edited)` flag in body.
  The count of edits is recorded in frontmatter
  (`edited_messages_count`). Edit history is NOT captured.
- Deletions: `**HH:MM — <Sender>:** [deleted at HH:MM]` where the
  deleted-at timestamp is when the robot first observed the deletion.
  Reference appended to `deleted_messages[]` in frontmatter.
- Mentions: `<@U02ABC>` → `@<display-name>`;
  `<#C02XYZ|channel-name>` → `#<channel-name>`.
- Slack mrkdwn → standard markdown:
  `*bold*` → `**bold**`, `_italic_` → `*italic*`,
  `~strike~` → `~~strike~~`, `<url|label>` → `[label](url)`,
  bare `<url>` → `url`. Code fences and `> quote` pass through.

## Lock 6 — Pre-filter (deterministic, NO LLM)

Skip messages where any of:
- `bot_id` is non-null (every bot — GitHub, Linear, Calendly, Zapier,
  custom — ALL).
- `subtype` ∈ `{channel_join, channel_leave, channel_topic,
  channel_purpose, channel_name, channel_archive, channel_unarchive,
  group_join, group_leave, bot_message, bot_add, bot_remove}`.
- `text` empty AND `files` empty AND no thread replies (pure pings /
  metadata events not caught above).
- Slack user ID is in the universal blocklist (none currently;
  reserved).

Reactions: filter at render time — don't render the `reactions[]`
field, but never drop the underlying message because it has reactions.

Edits and deletions are state changes, NOT skip conditions:
- `subtype: message_changed` → re-render the in-place message text;
  bump `edited_messages_count`.
- `subtype: message_deleted` → replace the body line with
  `[deleted at HH:MM]`; append to `deleted_messages[]`.

Channel allowlists are a routing concern (`sources.yaml`), NOT a
format concern. The robot fetches everything the user token can see.

## Lock 7 — `_profile.md` (channel / DM / group DM / workspace)

All four profile types live alongside the data they describe and have
the same shape: the robot owns the YAML frontmatter; the body is
human-editable and is preserved across re-renders.

**Channel** (`channels/<channel-name>/_profile.md`):
```yaml
slack_channel_id: C02XYZ456
channel_name_current: deals
channel_name_history:
  - { name: deals, changed_at: 2024-08-12T00:00:00Z }
purpose: "Deal flow for the audio data marketplace."
topic: "Active negotiations"
created: 2024-08-12T00:00:00Z
is_archived: false
archived_at: null
member_count: 6
members:
  - { slug: sydney-hayes, slack_user_id: U02ABC,
      display_name: "Sydney Hayes", joined_at: 2024-08-12T00:00:00Z }
first_seen: 2026-04-15T00:00:00Z       # robot's first ingest
last_updated: 2026-04-15T18:02:00Z
```

**DM** (`dms/<other-user-slug>/_profile.md`):
```yaml
slack_dm_id: D02XYZ
counterparty:
  slug: sydney-hayes
  slack_user_id: U02ABC
  display_name: "Sydney Hayes"
  real_name: "Sydney Hayes"
  email: "sydney@eclipse.audio"
  display_name_history:
    - { name: "Sydney Hayes", observed_at: 2024-08-12T00:00:00Z }
first_message: 2024-08-12T00:00:00Z
last_message: 2026-04-15T18:02:00Z
message_count_total: 1284
```

**Group DM** (`group-dms/<group-id-short>/_profile.md`):
```yaml
slack_group_id: G07ABC123
group_id_short: g07abc12
display_label: "Kayla, sydney"         # Slack's auto-rendered label
member_count: 3
members:
  - { slug, slack_user_id, display_name }
member_history:
  - { event: joined, slug: kayla-...., at: 2025-11-02T00:00:00Z }
first_message: 2025-11-02T00:00:00Z
last_message: 2026-04-15T18:02:00Z
```

**Workspace** (`<workspace-slug>/_profile.md`):
```yaml
slack_team_id: T02ABC123
slack_workspace_slug: eclipse-labs
slack_workspace_name_current: "Eclipse Labs"
slack_workspace_name_history:
  - { name: "Eclipse Labs", observed_at: 2024-08-12T00:00:00Z }
slack_workspace_url: https://eclipse-labs.slack.com/
me_user_id: U02XYZ789
me_canonical_slug: adithya-shak-kumar
auth_token_path: _credentials/slack-eclipse-labs.json
auth_scopes: [channels:history, channels:read, groups:history, ...]
first_seen: 2026-04-15T00:00:00Z
```

## Lock 8 — Cursor + dedup

**Cursor**: `_shell/cursors/slack/<workspace-slug>/<container-slug>.txt`
where `<container-slug>` is the channel slug, the other-user-slug for
1:1 DMs, or `group-id-short` for group DMs. Stores the latest seen
Slack microsecond `ts` for that container. Atomic write via
`tmp → rename`.

Sanity check on every run, in order:
1. Read cursor `ts`.
2. Call `conversations.history(oldest=cursor)`.
3. If the API returns `not_found` / `channel_not_found`: the container
   was archived or deleted upstream. Set `container_archived: true` on
   `_profile.md`, skip the container for this run, do NOT crash.
4. Process messages newer than the cursor.
5. Atomically advance the cursor to the latest seen `ts` only AFTER
   the write phase succeeds. Mid-run failure leaves the cursor at the
   prior value; the next run replays.

For threads, the cursor advances based on the **parent message ts**,
not the latest reply. Replies arriving days later trigger a re-render
of the parent's day-file in place.

**Dedup ledger**: `workspaces/<ws>/_meta/ingested.jsonl`. Key:
`slack:<workspace_id>:<container_id>:<YYYY-MM-DD>` (file-level, like
iMessage).

| Existing ledger row | content_hash | Action |
|---|---|---|
| absent | — | write file, append ledger row |
| present | matches | no-op (silent skip) |
| present | mismatches | overwrite file, append NEW ledger row |

## Lock 9 — Robot CLI

```
ingest-slack.py
  --workspace <slug>             required; e.g., eclipse-labs
  [--containers <list>]          subset of {channels,dms,group-dms}; default: all
  [--channel <slug>]             single channel/DM/group-dm (debugging)
  [--dry-run]                    parse + render, no writes; cursor untouched
  [--show]                       in dry-run, print full content to stdout
  [--max-days <int>]             cap days back from cursor
  [--reset-cursor]               wipe all cursors for the workspace
  [--reset-cursor-channel <slug>] wipe cursor for one container only
  [--no-attachments]             skip attachment metadata extraction (fast schema-only re-render)
  [--run-id <id>]                tag for ledger / log lines
```

**flock**: `/tmp/com.adithya.ultron.ingest-slack-<workspace-slug>.lock`.
Concurrent invocation for the same workspace exits 0 silently.

## Forbidden behaviors (immutable contract)

The robot **NEVER**:
1. Deletes a raw file based on a Slack-side deletion. Vanished
   messages set `deleted_upstream` (container) or append to
   `deleted_messages[]` (single message). The file persists.
2. Copies attachment binaries. Metadata + permalinks only.
3. Runs LLM / vision calls during ingest. Pure Python only.
4. Edits frontmatter post-write except `deleted_messages`,
   `edited_messages_count`, `container_archived`, `deleted_upstream`.
5. Writes outside `workspaces/<ws>/raw/slack/<workspace-slug>/...`.
6. Fetches full edit history. Current text only.
7. Renders reactions.
8. Renders bot messages.
9. Skips the universal pre-filter (Lock 6), even if a workspace
   allowlists the channel.

## Cross-references

Workflow: `CONTEXT.md`. Setup, scopes, rate limits: `SETUP.md`.
Routing: `route.py` (workspace + channel/DM allowlist). Universal
envelope check: `_shell/bin/check-frontmatter.py`.
