---
platform: instagram
last_verified: 2026-04-20
endpoint: POST /v1/posts
---

# Instagram

Single endpoint, `POST /v1/posts`. `platformSpecificData.contentType` selects the surface.

## Account prerequisites

Business or Creator account (personal accounts rejected). OAuth via Facebook Business in the Zernio dashboard. Required permissions: `instagram_business_basic`, `instagram_business_content_publish`.

## Surfaces

| Surface | `contentType` | Media |
|---------|---------------|-------|
| Feed post | omit (default) | 1 image or 1 video |
| Carousel | omit | 2–10 mixed items in `mediaItems` |
| Story | `"story"` | 1 image or short video; no caption displayed |
| Reel | `"reels"` | 1 video, 9:16, max 90s |

## Request shape

```json
{
  "content": "Caption text. Max 2200 chars.",
  "mediaItems": [
    { "type": "image", "url": "https://..." },
    { "type": "video", "url": "https://..." }
  ],
  "platforms": [{
    "platform": "instagram",
    "accountId": "<accountId>",
    "platformSpecificData": {
      "contentType": "reels",
      "shareToFeed": true,
      "collaborators": ["username1"],
      "userTags": [{"username": "user1", "x": 0.5, "y": 0.5, "mediaIndex": 0}],
      "thumbOffset": 0,
      "instagramThumbnail": "https://...",
      "audioName": "Custom Audio",
      "firstComment": "Auto-pinned comment"
    }
  }],
  "publishNow": true
}
```

## Limits

| Item | Value |
|------|-------|
| Caption | 2,200 chars |
| Feed image | 8 MB; aspect 0.8 to 1.91:1 |
| Feed video | 300 MB; max 60 min; 4:5 to 1.91:1 |
| Reels video | 300 MB; max 90 s; 9:16 (1080x1920) |
| Story | image 8 MB / video 100 MB; max 60 s; 9:16 |
| Carousel | up to 10 items, 8 MB image each |
| Posts | 100 per 24h rolling, all content types combined |

## Errors

| Error | Class | Note |
|-------|-------|------|
| `Cannot process video from this URL` | fatal_content | Cloud-storage URL (Drive/Dropbox/iCloud) returns HTML, not bytes |
| `100 posts per day` | retryable_later | Rate limit |
| `Instagram blocked your request` | fatal_content / retryable_later | Automation detected — reduce cadence |
| `Duplicate content detected` | fatal_content | Also fires on low-entropy test videos (solid colors, sine gradients) on fresh accounts. Use visually-variable media + nonce in caption for tests |
| `Media fetch failed (3 attempts)` | fatal_content | URL inaccessible |
| `Instagram access token expired` | fatal_auth | Reconnect in dashboard |

## Unsupported

Music on Reels, story stickers, location tags, Live, Guides, product tags, filters, boosting from organic skill (use ads), personal accounts, top-level comments.

## AI disclosure

No field exposed via Zernio. Manual label in IG app only. Meta auto-detects via C2PA.
