---
platform: discord
last_verified: 2026-04-29
endpoint: POST /v1/posts
---

# Discord

Posting to SERVER channels via Zernio's centralized managed bot. NOT for personal DMs or selfbot reads (that's the `discord` skill — totally separate).

Each connected Zernio Discord account = one guild + one currently-selected channel. The Zernio bot posts AS the bot (or a webhook identity), NOT as Adithya.

## Connect flow

1. `GET /v1/connect/discord?profileId=<profileId>` returns a `botInviteUrl`. Open in browser, authorize bot to join the target guild.
2. After authorization, select a channel via `/connect/discord/select-channel` (Zernio handles the redirect).
3. Confirm with `cli.sh accounts | jq '.accounts[] | select(.platform == "discord")'`.

## Limits

| Item | Value |
|------|-------|
| Content | 2000 chars |
| Embeds | ≤ 10 per message; combined embed text ≤ 6000 chars |
| Attachments | ≤ 10 per message |
| Image formats | JPEG, PNG, GIF, WebP; 25 MB (higher on boosted servers) |
| Video formats | MP4, MOV, WebM; 25 MB (up to 500 MB on boosted servers) |
| Embed: name 256 chars, value 1024, footer 2048; ≤ 25 fields |

## Supported channel types

`0` (text), `5` (announcement), `15` (forum). DMs, voice, stage, category, and thread channels are out of scope. The `discord-channels` endpoint already filters to supported types.

## `platformSpecificData` fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `channelId` | string | YES | Target channel snowflake. Must be one of the channels in `discord-channels` |
| `embeds` | array | no | Up to 10 Discord embed objects |
| `poll` | object | no | Native Discord poll. Mutually exclusive with media |
| `crosspost` | bool | no | Auto-publish to followers of an announcement channel (type 5). No-op on text/forum |
| `forumThreadName` | string | required for type 15 | Thread title |
| `forumAppliedTags` | string[] | no | ≤ 5 forum tag snowflake IDs |
| `threadFromMessage` | object | no | Spawn a thread under the published message: `{name, autoArchiveDuration: 60|1440|4320|10080, rateLimitPerUser: 0–21600}` |
| `tts` | bool | no | Text-to-speech message |
| `webhookUsername` | string | no | Override display name. 1–80 chars. Cannot contain `clyde` or `discord` (case-insensitive). Empty resets to default |
| `webhookAvatarUrl` | string | no | Override avatar URL |

`embeds[N]`: `title`, `description`, `color` (decimal RGB int), `url`, `timestamp` (ISO 8601), `footer.{text, icon_url}`, `image.url`, `thumbnail.url`, `author.{name, url, icon_url}`, `fields[].{name, value, inline}`.

`poll`: `{ question: { text }, answers: [{ poll_media: { text, emoji? } }, ...], duration: 1–768 hours (default 24), allow_multiselect: bool (default false) }`. Max 10 answers.

## Reject locally before submission

- `poll` set AND `mediaItems` non-empty (Discord rejects)
- `forumThreadName` set AND channel type ≠ 15 (returns 400)
- `forumThreadName` missing on type-15 channel (returns 400)
- `forumAppliedTags.length > 5`
- `embeds.length > 10`
- combined embed text > 6000 chars
- content > 2000 chars
- attachments > 10
- `webhookUsername` contains `clyde`/`discord` (case-insensitive) or 0 chars or > 80 chars

## Quick start: text + channel

```json
{
  "content": "Hello from Zernio API!",
  "platforms": [{
    "platform": "discord",
    "accountId": "YOUR_ACCOUNT_ID",
    "platformSpecificData": { "channelId": "1234567890" }
  }],
  "publishNow": true
}
```

## Embed example

```json
{
  "content": "New release shipping today!",
  "platforms": [{
    "platform": "discord",
    "accountId": "YOUR_ACCOUNT_ID",
    "platformSpecificData": {
      "channelId": "1234567890",
      "embeds": [{
        "title": "v2.3.0 Release Notes",
        "description": "Dark mode, new API endpoints, faster uploads.",
        "color": 5814783,
        "url": "https://example.com/changelog",
        "footer": { "text": "Shipped today" },
        "fields": [
          { "name": "New Features", "value": "3", "inline": true },
          { "name": "Bug Fixes", "value": "12", "inline": true }
        ]
      }]
    }
  }],
  "publishNow": true
}
```

## Poll example (no media allowed)

```json
{
  "platforms": [{
    "platform": "discord",
    "accountId": "YOUR_ACCOUNT_ID",
    "platformSpecificData": {
      "channelId": "1234567890",
      "poll": {
        "question": { "text": "Ship it now or wait until Monday?" },
        "answers": [
          { "poll_media": { "text": "Ship now" } },
          { "poll_media": { "text": "Wait for Monday" } }
        ],
        "duration": 24,
        "allow_multiselect": false
      }
    }
  }],
  "publishNow": true
}
```

## Forum starter post (type 15)

```json
{
  "content": "Community call notes for January 15",
  "platforms": [{
    "platform": "discord",
    "accountId": "YOUR_ACCOUNT_ID",
    "platformSpecificData": {
      "channelId": "9999999999",
      "forumThreadName": "Community Call - Jan 15",
      "forumAppliedTags": ["11111111", "22222222"]
    }
  }],
  "publishNow": true
}
```

## Endpoints

- `cli.sh discord-channels <accountId>` — list channels in connected guild (id, name, type, parentId, available_tags[] for forums)
- `cli.sh discord-settings <accountId>` — current webhook identity + selected channel
- `cli.sh discord-settings-update <accountId> <payload.json>` — PATCH `webhookUsername`, `webhookAvatarUrl`, and/or `channelId` (switches connected channel; new webhook gets created automatically)

## Common errors

- `channel_not_found` / `channel_not_supported` — `channelId` not in connected guild, or channel is not type 0/5/15
- `webhook_username_invalid` — contains `clyde`/`discord`, or 0 chars, or > 80 chars
- `forum_thread_name_required` — forgot `forumThreadName` on type-15 channel
- `embed_too_large` — total embed text > 6000 chars
- `poll_with_media` — payload combines `poll` and `mediaItems`. Pick one
- `not_connected` — Zernio bot was kicked from the guild. Run connect flow again

Zernio handles 429 backoff and `X-RateLimit-Reset-After` automatically.
