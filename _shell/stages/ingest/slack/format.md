# Format: slack

## File granularity
One file per (channel, day) for channels. One file per (DM thread, day) for DMs.

## Path
- Channel: `workspaces/<ws>/raw/slack/<workspace-slug>/<channel-slug>/<YYYY>/<MM>/<YYYY-MM-DD>.md`
- DM: `workspaces/<ws>/raw/slack/<workspace-slug>/dm/<participants-slug>/<YYYY>/<MM>/<YYYY-MM-DD>.md`

`<workspace-slug>`: from team name, kebab-case. `<channel-slug>`: from channel name, kebab-case (drop leading `#`). `<participants-slug>`: sorted user slugs joined with `__`.

## Frontmatter

```yaml
---
source: slack
workspace: <ws-slug>
ingested_at: <ISO 8601>
ingest_version: 1
content_hash: <blake3>
provider_modified_at: <ISO 8601>

slack_workspace_id: T0XXXXXX
slack_workspace_name: Eclipse
channel_id: C0XXXXX
channel_name: deals
channel_type: public | private | im | mpim
date: 2026-04-15
participants:
  - { user_id: U0XXX, name: Sydney Hayes, slug: sydney }
message_count: 42
thread_count: 6
---
```

## Body

```markdown
# #deals — 2026-04-15

## 09:14 UTC — Sydney
Body text. Slack mrkdwn rendered to markdown (`*bold*` → `**bold**`, `_italic_` → `*italic*`, `<https://x|label>` → `[label](https://x)`).

> Thread (3 replies):
> - **09:18 UTC — Adithya:** Reply.
> - **09:21 UTC — Sydney:** Reply.
> - **09:30 UTC — Julian:** Reply.

## 10:02 UTC — Julian
Standalone message.
```

## Pre-filter
- Skip messages where `subtype` ∈ `{channel_join, channel_leave, channel_topic, channel_purpose, bot_message}` UNLESS bot is on allowlist (e.g., GitHub, Linear).
- Skip files / attachments larger than 25 MB; reference by metadata only.
- Skip channels matching `*-bot`, `notifications`, `alerts`.

## Dedup key
`slack:<workspace_id>:<channel_id>:<YYYY-MM-DD>` — channel-day granularity.
Same key + same content_hash → skip. Different hash → overwrite (new messages arrived for that day).
