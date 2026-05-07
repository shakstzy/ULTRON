---
platform: youtube
last_verified: 2026-04-20
endpoint: POST /v1/posts
---

# YouTube

`POST /v1/posts`. Shorts is auto-detected — no flag forces it.

## Account prerequisites

YouTube channel, verified for videos > 15 min. OAuth scopes: `youtube.upload`, `youtube.force-ssl`. Suspended channels reject all uploads with HTTP 403.

## Shorts detection

Auto-detected when BOTH:
- Duration ≤ 3 minutes
- Aspect ratio is 9:16 vertical

Custom thumbnails not supported via API for Shorts.

## Request shape

```json
{
  "content": "Video description",
  "mediaItems": [{ "type": "video", "url": "https://...", "thumbnail": "https://..." }],
  "platforms": [{
    "platform": "youtube",
    "accountId": "<accountId>",
    "platformSpecificData": {
      "title": "My Video Title (max 100 chars, required)",
      "visibility": "public",
      "categoryId": "22",
      "madeForKids": false,
      "containsSyntheticMedia": false,
      "playlistId": "PLxxxxx",
      "firstComment": "Auto-pinned comment (max 10k chars)"
    }
  }],
  "publishNow": true
}
```

## `platformSpecificData` fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `title` | string | (REQUIRED) | Max 100 chars. No derivation from `content` |
| `visibility` | enum | `public` | `public | unlisted | private` |
| `madeForKids` | bool | `false` | **PERMANENT once true.** Disables comments, ads, notifications. Caller must pass explicitly |
| `containsSyntheticMedia` | bool | `false` | AI disclosure |
| `categoryId` | string | `22` | Common: `1` Film, `10` Music, `20` Gaming, `22` People and Blogs, `27` Education |
| `playlistId` | string | unset | Adds video to playlist after upload |
| `firstComment` | string | unset | Posts pinned comment when video goes live |

## Limits

| Item | Value |
|------|-------|
| Title | 100 chars |
| Description | 5,000 chars |
| Regular video | 256 GB / 12 hr (verified) or 15 min (unverified) / 16:9 |
| Shorts | 256 GB / 3 min / 9:16 (1080x1920) |
| Custom thumbnail (regular only) | JPEG/PNG/GIF, 2 MB, 1280x720 |
| Daily quota | ~10,000 units (≈ 6 uploads/day) |

## Scheduling

When `publishNow=false` + `scheduledAt` (ISO-8601 UTC) set, Zernio uploads as private then flips visibility at the scheduled time. `firstComment` posts only when visibility goes live.

## Errors

| Error | Class | Note |
|-------|-------|------|
| HTTP 403 | fatal_auth / fatal_content | Channel suspended or `madeForKids` change blocked |
| `quotaExceeded` | retryable_later | Daily quota hit |
| `videoRejected` | fatal_content | Policy violation |
| `invalidCategoryId` | fatal_content | Bad `categoryId` |

## Unsupported

Community posts, Premieres, live streams, captions/subtitles, end screens, cards, chapters, monetization, playlist creation/deletion (existing only).

## AI disclosure

`containsSyntheticMedia: true` for realistic AI-generated content. Non-disclosure plus auto-detection equals an immediate Community Guidelines strike, not a warning. The 2025 Q3 enforcement wave removed channels with billions of cumulative views.
