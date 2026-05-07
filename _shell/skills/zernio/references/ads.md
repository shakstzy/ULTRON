---
endpoint_root: /v1/ads
last_verified: 2026-04-28
covers: metaads, googleads, linkedinads, tiktokads, pinterestads, xads
---

# Zernio Ads — six platforms

Same `ZERNIO_API_KEY`. Every `/v1/ads/*` call requires the Ads add-on enabled in Zernio billing — first 403 means the add-on is off, route to billing, do not retry.

`adAccountId` formats per platform:

| Platform | `adAccountId` format | Connect mode |
|----------|----------------------|--------------|
| `metaads` | `act_<digits>` | same-token (reuse facebook/instagram OAuth) |
| `googleads` | `customers/<digits>` or `<digits>-<digits>-<digits>` | standalone (no parent posting account) |
| `linkedinads` | `urn:li:sponsoredAccount:<digits>` | same-token (reuse linkedin OAuth) |
| `tiktokads` | numeric advertiser ID (long) | separate-token (requires existing TikTok posting `accountId`) |
| `pinterestads` | numeric business ID (`bizId`) | same-token (reuse pinterest OAuth) |
| `xads` | alphanumeric (e.g. `18ce54d4x5t`) | separate-token (requires existing X posting `accountId`) |

`accountId` resolves to the Zernio social account; pass either the posting account or the ads-credential account; Zernio handles the sibling internally. For Instagram ads, Zernio auto-resolves the linked Facebook Page + IG Business Account; if that link is missing, returns `linked_account_required`.

## Goals — what each platform supports

| Platform | engagement | traffic | awareness | video_views | lead_generation | conversions | app_promotion |
|----------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| metaads | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| googleads (`/create` only) | ✓ | ✓ | ✓ | ✓ | — | — | — |
| linkedinads | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| tiktokads | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| pinterestads | ✓ | ✓ | ✓ | ✓ | — | — | — |
| xads | ✓ | ✓ | ✓ | ✓ | — | — | ✓ |

## Boost a post (`POST /v1/ads/boost`)

Common shape — nested `budget`, nested `schedule`, nested `targeting`:

```json
{
  "postId": "POST_ID",
  "accountId": "ACCOUNT_ID",
  "adAccountId": "<platform-specific>",
  "name": "Spring launch boost",
  "goal": "traffic",
  "budget": { "amount": 40, "type": "daily" },
  "schedule": { "startDate": "2026-04-20", "endDate": "2026-04-27" },
  "targeting": {
    "ageMin": 25, "ageMax": 45,
    "countries": ["US", "CA"],
    "interests": [{ "id": "6003139266461", "name": "DevOps" }]
  }
}
```

Boost-only specifics:

- **Google Ads**: NOT SUPPORTED. No organic-post equivalent. Use `create-ad`.
- **LinkedIn**: source post must be on a connected Company Page (personal profile posts can't be boosted via API). 422 `duplicate content` on recently-posted text — post a fresh organic version first.
- **TikTok (Spark Ads)**: source post must be public on a TikTok Business Account.
- **Pinterest**: source pin must be on an open board with image + valid URL. Otherwise `pin not eligible for promotion`.
- **X**: `not_eligible_for_promotion` if the source tweet is a reply, sensitive-flagged, or from a suspended account.
- **Meta**: targeting is NESTED here. Same field names but a different shape than `/create`.

## Standalone ad (`POST /v1/ads/create`)

Three mutually-exclusive bodies, selected by which fields are present:

### 1. Single-creative (default; all platforms that support `/create`)

FLAT body. `budget` is split into `budgetAmount` + `budgetType` (NOT nested), targeting fields are FLAT (`ageMin`/`countries`/`interests`):

```json
{
  "accountId": "acc_metaads_123",
  "adAccountId": "act_1234567890",
  "name": "Spring sale - US Feed",
  "goal": "conversions",
  "budgetAmount": 75,
  "budgetType": "daily",
  "headline": "Spring Sale - 30% off",
  "body": "Limited time. Upgrade today.",
  "imageUrl": "https://cdn.example.com/spring.jpg",
  "callToAction": "SHOP_NOW",
  "linkUrl": "https://example.com/spring",
  "countries": ["US"],
  "ageMin": 25,
  "ageMax": 55
}
```

**Critical: do not mix `/boost` and `/create` shapes.** `/boost` is nested, `/create` is flat.

### 2. Meta multi-creative (Meta only — A/B testing)

Replace the single creative with `creatives: [{...}, {...}]`. One campaign, one ad set, N ads sharing budget+targeting+schedule. Returns `{ ads: [...], platformCampaignId, platformAdSetId, message }`. Each ad named `"<name> #N"`.

### 3. Meta attach (Meta only)

Pass `adSetId` plus a single creative. Budget+targeting+schedule inherit from the existing ad set.

### Per-platform `/create` notes

- **Meta video creatives**: replace `imageUrl` with `video: { url, thumbnailUrl }`. Thumbnail is REQUIRED. Synchronous chunked upload — set HTTP timeout ≥ 15 min. Max transcoding wait 10 min before `platform_error`.
- **Google Search**: pass `campaignType: "search"` plus `keywords[]` (string array; broad match by default). RSA assets: at least one `headline` + `body`; `additionalHeadlines[]` (≤ 14 more) and `additionalDescriptions[]` (≤ 3 more).
- **Google Display**: pass `campaignType: "display"` AND BOTH `images.landscape` (1.91:1, e.g. 1200×628) AND `images.square` (1:1, e.g. 1080×1080). Missing one returns `NOT_ENOUGH_*_MARKETING_IMAGE_ASSET`. `businessName` REQUIRED, max 25 chars.
- **LinkedIn**: `/create` returns 400 today — boost only.
- **Pinterest**: requires `pinterestImageUrl` (2:3 portrait, 1000x1500 ideal) + `pinterestTitle` (≤100) + `pinterestDescription` (≤500) + `linkUrl`.
- **TikTok**: flat shape; `ageGroups` uses TikTok buckets (`AGE_18_24`, `AGE_25_34`, etc.) — NOT Meta's numeric range. `genders: ["MALE","FEMALE"]` or omit for all.
- **X**: standalone supported. `locations` (ISO codes) + `languages` (BCP-47).

## Click-to-WhatsApp (Meta only — `POST /v1/ads/ctwa`)

Required: `accountId`, `adAccountId`, `pageId` (FB Page paired with the verified WhatsApp Business number), `name`, `budget`, `goal`, `creative.{...}`. CTA locked to `WHATSAPP_MESSAGE`; URL hard-coded to `api.whatsapp.com/send`. Subcode `2446886` = page not paired.

Prereqs Meta enforces: Page paired with verified WABA, WABA business-verified, token has `ads_management`. Missing any returns `platform_error`.

## update-ad / campaign-status / ad-set-status

`update-ad` body fields are all optional — send only what you're changing: `name`, `status` (`ACTIVE | PAUSED`), `budget.amount`, `budget.type`, `targeting` (Meta only), `schedule.endDate`. Multi-field updates land atomically per Meta. LinkedIn / TikTok require status changes via separate calls; Zernio normalizes this.

## CBO vs ABO budget updates (Meta)

- `budgetLevel === 'campaign'` (CBO): use `update-campaign <campaignId>` with `{ "budget": { "amount": 250, "type": "daily" } }`.
- `budgetLevel === 'adset'` (ABO): use `update-ad-set <adSetId>` with `{ "budget": ..., "status": "active" }`.

Wrong endpoint returns 409 `BUDGET_LEVEL_MISMATCH`. Read `budgetLevel` from `tree` first.

## Custom audiences

Three types (Meta full-CRUD; TikTok customer_list + lookalike; Pinterest basic; LinkedIn read-only; X / Google not yet supported):

- `customer_list`: PII via `add-audience-users`. 10k cap / request, enforced locally. PLAINTEXT — Zernio SHA-256-hashes server-side per platform's normalization. Do NOT pre-hash, lowercase, trim, or strip dial codes.
- `website_retargeting`: `pixelId`, `retentionDays`, `eventName`.
- `lookalike`: `seedAudienceId` + `country` codes + `ratio` (Meta uses 0.01–0.10 for 1%–10%; the unified API accepts integer 1–10 too). Meta requires ≥ 100 matched users in seed.

Lookalike example:
```json
{
  "accountId": "acc_metaads_123",
  "adAccountId": "act_1234567890",
  "type": "lookalike",
  "name": "LAL 1% of US customers",
  "sourceAudienceId": "6123456789",
  "country": "US",
  "ratio": 0.01
}
```

`delete-audience` is visible on the platform — any active campaign referencing it loses its target. Run `list-campaigns` first; pause referenced campaigns before deleting.

## Conversions API

`destinationId`:

- **Meta** = pixel (dataset) ID, e.g. `"123456789012345"`. Per-event `eventName` is free-form (or use Meta's standard names: `Purchase`, `Lead`, `CompleteRegistration`, `AddToCart`, `InitiateCheckout`, `AddPaymentInfo`, `Subscribe`, `StartTrial`, `ViewContent`, `Search`, `Contact`, `SubmitApplication`, `Schedule`). Test mode: `testCode: "TEST12345"` at root → Test Events tab. Batch cap 1000 events / request (Zernio auto-chunks). Whole batch fails on any malformed event.
- **Google** = `customers/<id>/conversionActions/<id>`. Google locks the event type to the conversion action — NOT the per-event `eventName`. Two attribution paths: `user.clickIds.{gclid|gbraid|wbraid}` (click-attribution) OR hashed PII via Enhanced Conversions for Leads (`user.email`/`user.phone` PLAINTEXT — Zernio handles SHA-256 + Gmail dot/plus stripping). EEA/UK callers MUST include `consent: { adUserData: "GRANTED", adPersonalization: "GRANTED" }` at root.

Per event (both): `eventId` (REQUIRED, stable, dedup key), `eventName`, `eventTime` (ISO 8601 or unix seconds), `userData / user.{...}` PLAINTEXT, optional `customData` (`{ value, currency, contentIds, contents }`).

LinkedIn / TikTok / Pinterest / X conversions API: roadmap. `send-conversions` against those returns 400.

## Special-category ads (Meta)

Set `specialAdCategories: ["HOUSING"]` (or `EMPLOYMENT`, `CREDIT`, `ISSUES_ELECTIONS_POLITICS`, or any combination). Meta auto-clamps targeting (no narrow age, no narrow geo, no specific zips). Missing on a clearly-restricted ad → 422 `special_ad_category_required`.

## Connect-ads — what each platform needs

| Platform arg | Mode | `accountId` arg | Post-flow |
|--------------|------|-----------------|-----------|
| `facebook` | same-token | optional | usually `alreadyConnected: true` |
| `instagram` | same-token | optional | usually `alreadyConnected: true` |
| `linkedin` | same-token | optional | needs `r_organization_admin` scope |
| `pinterest` | same-token | optional | reuses pinterest OAuth |
| `tiktok` | separate-token | REQUIRED (existing TikTok posting `accountId`) | returns `authUrl`; user OAuths into TikTok Marketing API |
| `twitter` | separate-token | REQUIRED (existing X posting `accountId`) | OAuth 1.0a + marketing-API approval; one OAuth screen |
| `googleads` | standalone | NOT required | returns `authUrl` for Google OAuth |

If LinkedIn returns 422 `INVALID_PARAMETER_VALUE r_organization_admin`, the parent LinkedIn token was issued before that scope existed — re-OAuth from scratch.

## Budget minimums (platform-enforced)

| Platform | Daily floor | Lifetime floor |
|----------|-------------|----------------|
| LinkedIn | $10/day | $100 |
| Meta, TikTok | varies by goal | varies |

422 mentioning a minimum: surface it directly. Don't auto-bump.

## Media specs by platform

| Platform | Type | Format | Max size | Notes |
|----------|------|--------|----------|-------|
| Meta feed | image | JPEG, PNG | 30 MB | 1080x1080 or 1200x628 |
| Meta reels | video | MP4, MOV | 4 GB | 9:16 vertical, max 90 s |
| Meta story | image / video | JPEG, PNG / MP4 | 30 MB / 4 GB | 9:16 vertical |
| Meta carousel | image / video | JPEG, PNG, MP4 | 30 MB / card | 2–10 cards |
| LinkedIn | image | JPEG, PNG, GIF | 5 MB | 1200x627 |
| LinkedIn | video | MP4 | 200 MB | 3s–30min, 75 MB recommended |
| LinkedIn | carousel | JPEG, PNG | 10 MB / card | 2–10 cards, 1080x1080 |
| Pinterest | image | JPEG, PNG | 32 MB | 2:3 portrait, 1000x1500 ideal |
| Pinterest | video | MP4, MOV | — | 4s–15min; 9:16 / 1:1 / 4:5 |
| TikTok ads | video | MP4, MOV, WebM | 4 GB | 9:16, 3s–10min (organic preflight applies) |
| Google Display | image | JPEG, PNG | — | landscape 1.91:1 + square 1:1 BOTH required |
| X / xads | image | JPEG, PNG, WebP | 5 MB | up to 4 per ad |
| X / xads | video | MP4, MOV | 512 MB | up to 140s (or `longVideo` for Premium) |

## Common platform errors

- **Meta `(#100) Invalid parameter`** — usually wrong `adAccountId` format, missing pixel for conversion goal, or invalid targeting interest ID.
- **Meta `(#200) Permissions error`** — token lacks `ads_management`. Re-run `connect-ads facebook` to refresh scopes.
- **Meta `BUDGET_LEVEL_MISMATCH` (409)** — see CBO vs ABO above.
- **Meta `special_ad_category_required` (422)** — set `specialAdCategories` and re-prompt LAUNCH-AD.
- **LinkedIn `INVALID_PARAMETER_VALUE r_organization_admin`** — re-run `connect-ads linkedin <accountId>`.
- **LinkedIn `duplicate content` (422)** — boost target text already on LinkedIn; post fresh organic version first.
- **TikTok `40002 - account not approved`** — TikTok ad account in pending review. No retry; user waits or contacts TikTok.
- **TikTok `creative under review`** — normal first-launch (12–24h). Don't claim "rejected".
- **TikTok `personal account not eligible`** — connected account is not a Business Account.
- **Pinterest `domain not claimed`** — link destination domain not verified. Claim at pinterest.com/business/settings.
- **Pinterest `pin not eligible for promotion`** — closed/secret board, missing image, flagged URL.
- **Google `NOT_ENOUGH_SQUARE_MARKETING_IMAGE_ASSET` / `NOT_ENOUGH_MARKETING_IMAGE_ASSET`** — Display ad missing one of the required image sizes.
- **Google `INVALID_HEADLINE_LENGTH`** — > 30 chars (RSA).
- **Google `INVALID_DESCRIPTION_LENGTH`** — > 90 chars (RSA).
- **Google `customer not approved`** — billing/policy notice on the Ads account; user resolves at ads.google.com.
- **X `marketing_api_approval_pending`** — manual review. Zernio handles most, some get flagged.

## ROAS metrics (Meta)

`metrics.roas = purchaseValue / spend`. `metrics.actionValues` carries per-action revenue. `metrics.purchaseValue` summed via priority list (`offsite_conversion.fb_pixel_purchase` → `omni_purchase` → `purchase`).

## What's NOT yet supported (don't attempt)

- LinkedIn: standalone `/create`, audience writes, Lead Gen Forms, Conversions API.
- Google: boost (no organic equivalent), Performance Max, Shopping/Video/Demand Gen, Customer Match writes.
- Pinterest: Conversions API, catalog/shopping ads.
- TikTok: Conversions API (Events v2 roadmap).
- X: Tailored Audiences (audience writes), Conversions API.
