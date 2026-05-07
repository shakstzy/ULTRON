---
platform: twitter
last_verified: 2026-04-21
endpoint: POST /v1/posts
---

# Twitter / X

`POST /v1/posts`. Twitter fields live in `platformSpecificData` (same shape as IG/YT).

## Account prerequisites

OAuth scopes: `tweet.write`, `media.write`, `offline.access`. Token TTL is short (2 hours); Zernio auto-refreshes via `offline.access`. Adithya is Premium (verified live 2026-04-21).

## Request shape

```json
{
  "content": "Tweet text. URLs always count as 23 chars. Emojis count as 2.",
  "mediaItems": [{ "type": "video", "url": "https://..." }],
  "platforms": [{
    "platform": "twitter",
    "accountId": "<accountId>",
    "platformSpecificData": {
      "threadItems": [],
      "replyToTweetId": null,
      "replySettings": "following",
      "longVideo": false,
      "geoRestriction": { "countries": [] }
    }
  }],
  "publishNow": true
}
```

## `platformSpecificData` fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `threadItems` | array | unset | Each item is `{content, mediaItems?}`. Top-level `content` is then display/search-only |
| `replyToTweetId` | string | unset | Creates a reply thread |
| `replySettings` | enum | `following` | `following | mentionedUsers | subscribers | verified` |
| `poll` | object | unset | `{options: string[], duration_minutes: number}`. Mutually exclusive with media + threadItems |
| `longVideo` | bool | `false` | Premium-only flag for videos over standard limit |
| `geoRestriction` | object | unset | `{countries: ["US", ...]}` ISO codes |

## Limits

| Item | Value |
|------|-------|
| Char count | 280 (free) / 25,000 (Premium). URLs count as 23, emojis as 2 |
| Image | JPEG/PNG/WebP; 5 MB; 1200x675 (16:9); ≤ 4 per tweet |
| GIF | 15 MB; 1 per tweet (consumes all 4 image slots) |
| Video | MP4/MOV; 512 MB; 140 s (or `longVideo` for Premium); 1280x720 |
| Polls | mutually exclusive with media and thread items |

## Errors

| Error | Class |
|-------|-------|
| `Tweet text is too long` | fatal_content |
| `does not allow duplicate tweets` | fatal_content |
| `Rate limit hit. Please wait 10 minutes` | retryable_later |
| `Missing tweet.write scope` | fatal_auth |

## Unsupported

Quote tweets, pinning, Spaces, Community posts, DM broadcasts.

## AI disclosure

No per-post field via API. Twitter has weaker enforcement than YT/TT.
