---
name: zernio
description: Publish to Instagram, YouTube, TikTok, Twitter/X, or Discord (server channels via the Zernio managed bot), and run paid ads on Meta / Google / LinkedIn / TikTok / Pinterest / X via the Zernio REST API. Direct curl wrapper, no MCP. Trigger phrases include "post to IG", "publish this reel", "tweet this", "drop in #channel on discord", "boost this post", "create a Meta ad", "sync customer list to a Meta audience", "send conversion to Meta CAPI". Do NOT use for Discord DMs / selfbot reads (that's the `discord` skill), reading inbox / DMs / comment moderation, or platforms outside that list.
---

# zernio

Single skill for all Zernio API surface — organic publishing AND paid ads. Same API key, same base URL, two write tokens.

Direct REST via `cli.sh` (curl + jq). NOT an MCP wrapper. The hosted Zernio MCP exposes 280+ tools that ambient-load into every session; this skill is opt-in.

## When this fires

**Organic posting (PUBLISH gate):** "post to IG / YT / TT / X", "publish this reel", "drop this on TikTok", "tweet this", "cross-post this", "post in #channel on discord", "post to my discord server".

**Paid ads (LAUNCH-AD gate):** "boost this post", "promote this post", "launch a Meta / LinkedIn / TikTok / Pinterest / X / Google ad", "pause this campaign", "duplicate this campaign", "sync customer list to a Meta audience", "send conversion to Meta CAPI", "log this purchase to Google Ads".

**Reads (no gate):** "list my accounts / ad accounts", "list my campaigns / ads / audiences", "show my ad spend", "tree", "search interests for X".

## Do NOT use for

- Discord DMs, reading personal Discord, or self-account posts → that's the `discord` skill (patchright selfbot).
- Reading inbox, replying to comments, analytics dashboards → use the Zernio dashboard.
- Snapchat / Reddit / Threads ads, or any platform outside the six → surface the gap, don't improvise.
- Drafting content. This skill publishes pre-approved artifacts.

## Auth + setup

`ZERNIO_API_KEY` lives in `.claude/settings.local.json` under `env` and is injected into every Bash session. `cli.sh` reads it from env. If it's missing, every command exits 1 with a clear message.

Account-alias registry lives at `~/.zernio/accounts.yaml` (outside repo, gitignored by location). Resolve aliases there; if missing, run `cli.sh accounts` and surface the list. Common aliases: `my-ig`, `my-tiktok`, `my-youtube`, `my-twitter`, `my-discord`. Natural-language variants ("my ig" / "my instagram" / "my personal ig") all normalize to `my-ig`.

Output directory: `~/.zernio/output/` (outside repo). PII payloads (custom-audience users) NEVER land in `raw/` or any workspace.

## CLI surface

```
# Reads (safe, no gate)
cli.sh accounts                                            list connected social accounts
cli.sh creator-info <accountId> [video|photo]              TikTok creator-info precheck
cli.sh discord-channels <accountId>                        Discord: list channels in connected guild
cli.sh discord-settings <accountId>                        Discord: current channel + webhook identity
cli.sh status <postId>                                     poll a post to terminal state
cli.sh ad-accounts [accountId]                             list platform ad accounts
cli.sh list-ads [adAccountId] [platform]                   list ads
cli.sh get-ad <adId>                                       one ad incl. metrics
cli.sh ad-analytics <adId> [from] [to]                     daily ad analytics
cli.sh ad-comments <adId>                                  comments on an ad's underlying post
cli.sh tree [adAccountId]                                  Campaign > AdSet > Ad with metrics
cli.sh list-campaigns [adAccountId]                        list campaigns
cli.sh list-audiences [adAccountId]                        list custom audiences
cli.sh get-audience <audienceId>                           one audience
cli.sh search-interests <q> <accountId> [platform]         lookup interest IDs
cli.sh conversion-destinations <accountId>                 list pixels / conversion actions

# Local file ops
cli.sh preflight <file> <platform> [surface]               offline media validation
cli.sh presign <file>                                      get upload URL
cli.sh upload <file>                                       presign + PUT, returns publicUrl

# Writes (PUBLISH gate)
cli.sh post <payload.json>                                 organic publish
cli.sh discord-settings-update <accountId> <payload.json>  PATCH webhook identity / switch channel

# Writes (LAUNCH-AD gate)
cli.sh boost-post <payload.json>
cli.sh create-ad <payload.json>
cli.sh create-ctwa <payload.json>
cli.sh update-ad <adId> <payload.json>
cli.sh cancel-ad <adId>
cli.sh update-campaign <campaignId> <payload.json>
cli.sh campaign-status <campaignId> <ACTIVE|PAUSED>
cli.sh delete-campaign <campaignId>
cli.sh duplicate-campaign <campaignId> [payload.json]
cli.sh bulk-status <payload.json>
cli.sh update-ad-set <adSetId> <payload.json>
cli.sh ad-set-status <adSetId> <ACTIVE|PAUSED>
cli.sh create-audience <payload.json>
cli.sh add-audience-users <audienceId> <payload.json>
cli.sh delete-audience <audienceId>
cli.sh send-conversions <payload.json>
cli.sh connect-ads <facebook|instagram|linkedin|pinterest|tiktok|twitter|googleads> [accountId]
```

`cli.sh help` prints the same surface.

## Procedure: organic publish

1. **Resolve accounts.** Map each `account_alias` via `~/.zernio/accounts.yaml`. If missing, run `cli.sh accounts` and surface the list.
2. **TikTok precheck (mandatory for TikTok targets).** `cli.sh creator-info <accountId>`. The caller's `privacy_level` MUST be in the returned `privacyLevels` array. If `PUBLIC_TO_EVERYONE` is missing for an unaudited client, surface that — `SELF_ONLY` lands the post privately. Surface `postingLimits.used / cap`.
3. **Discord precheck (mandatory for Discord targets).** If `platformSpecificData.channelId` is missing, run `cli.sh discord-channels <accountId>`. **Caveat:** Zernio's live `/discord-channels` endpoint isn't shipped yet (returns 404 HTML), so the CLI falls back to reading the currently-connected channel from `accounts[].metadata` — that fallback enumerates exactly ONE channel (the connected one). When the fallback's `note` field is present, you cannot validate against an arbitrary channelId; either post to the connected channel OR call `discord-settings-update` first to switch the connected channel. Validate channel type 0 (text), 5 (announcement), or 15 (forum). If type 15, payload MUST include `forumThreadName`. If `forumAppliedTags` is supplied, cap at 5. Reject locally if `poll` is set AND `mediaItems` is non-empty (Discord rejects). Enforce: content ≤ 2000 chars, ≤ 10 embeds, total embed text ≤ 6000 chars, ≤ 10 attachments, `webhookUsername` 1–80 chars and no `clyde`/`discord` substrings (case-insensitive).
4. **Preflight every file × every platform.** `cli.sh preflight <file> <platform> [surface]`. Surface for Instagram is `feed | story | reels | carousel`. For Discord, pass `boosted` only if the target server is Nitro-boosted (lifts video cap to 500MB); default `standard` keeps the conservative 25MB cap.
5. **Upload media.** `cli.sh upload <file>` → `{publicUrl}`. Treat the URL TTL as short and retry on expiry (the script does one retry automatically).
6. **Assemble payload.** Build per `references/<platform>.md`. AI-disclosure flags: caller sets, skill never defaults — see "AI disclosure" below. For TikTok: explicitly verify `content_preview_confirmed=true` and `express_consent_given=true`; if `draft=true`, force `publishNow=false`. For Discord: enforce all rules from step 3. Save the payload to `~/.zernio/output/zernio-payload-<ts>.json` BEFORE the gate — the saved file is the audit trail.
7. **PUBLISH gate (Pattern 11).** Print the full assembled payload AND, for TikTok, the `privacyLevels` array from creator-info AND, for YouTube, the `madeForKids` value with a permanent-flag warning if true. Wait for the literal token `PUBLISH` (case-sensitive). Anything else aborts. If `ZERNIO_NO_CONFIRM=1` is set, skip the gate and log `confirmation_skipped: true` in the result file — but NEVER skip when YouTube `madeForKids=true` or for scheduled posts more than 24h out.
8. **Post.** `cli.sh post zernio-payload-<ts>.json`. Capture the response. Write request + response to `~/.zernio/output/zernio-result-<ts>.json`.
9. **Poll status.** `cli.sh status <post._id>` until terminal (`published | scheduled | failed`). Cap at 60 iterations × 5s (5 min). 200 from `post` does not mean live — TikTok and IG report transcoding failures asynchronously. For multi-platform posts, the response carries `platforms[]` — inspect every platform's status, not just the top-level. A success at the top with one failed `platforms[].status` is `partial_failure`, not success.
10. **Audit.** Run every check in the audit table below. Don't claim success on a silent failure.

## Procedure: paid ads

1. **Add-on precheck.** Every `/v1/ads/*` call needs the Zernio Ads add-on enabled. The first ads call returns a clean 403 if it's off — don't retry; tell the user to enable at zernio.com/settings/billing (Build $10/mo, Accelerate $50/unit, Unlimited $1k/mo).
2. **Resolve the social account.** Same alias resolution as organic.
3. **Resolve the ad account.** `cli.sh ad-accounts <accountId>`. Pick the right `adAccountId`:
   - Meta `act_<digits>` · LinkedIn `urn:li:sponsoredAccount:<digits>` · TikTok numeric advertiser ID · Pinterest bizId · X alphanumeric (e.g. `18ce54d4x5t`) · Google `customers/<digits>` or `<digits>-<digits>-<digits>`.
   - If empty for the target platform, run `connect-ads <platform> [accountId]` first. Google is standalone (no `accountId`); TikTok and X are separate-token (require `accountId`); the rest are same-token reuse.
4. **Boost-post only.** Confirm the source post is `published` on the same `accountId` via `cli.sh status <postId>`.
5. **Media-bearing ads.** Run organic preflight (`cli.sh preflight ...`), upload to get `publicUrl`, reference the URL in the creative. The Ads API does NOT auto-upload local files.
6. **Meta multi-creative.** Use `creatives: [{...}, {...}]`. See `references/ads.md` for the shape.
7. **Assemble payload.** Save to `~/.zernio/output/zernio-ads-payload-<ts>.json` BEFORE the gate. For `add-audience-users`, enforce ≤ 10,000 users / request locally; chunk if larger.
8. **Compute dollar exposure.**
   - `daily` budget with `endDate`: `amount × (endDate − startDate in calendar days)`. If `startDate` is missing, default to today.
   - `lifetime` budget: `amount` as-is.
   - `daily` with no end date: surface "OPEN-ENDED daily spend at $X/day, no auto-stop". Treat as a flag — usually wrong.
9. **LAUNCH-AD gate.** Print the full payload + dollar exposure + (audience-sync) PII row count + (Meta) any `specialAdCategories` value. Require the literal token `LAUNCH-AD`. `PUBLISH` is NOT accepted here; reusing tokens blurs the gate. `ZERNIO_NO_CONFIRM=1` skips the gate and logs `confirmation_skipped: true` — **with three exceptions**: `add-audience-users`, `create-audience` with non-empty `users[]`, and `send-conversions` ALWAYS require LAUNCH-AD regardless of env. PII-movement paths and conversion-event paths can leak user data to Meta/Google in bulk; the bypass is too sharp an instrument for them.
10. **Call the write endpoint.** Capture the full response to `~/.zernio/output/zernio-ads-result-<ts>.json`.
11. **Poll where applicable.** For `boost-post` and `create-ad`, poll `cli.sh get-ad <adId>` every 30s up to 20 iterations until terminal (`active | pending_review | paused | rejected | cancelled`). `rejected` is terminal; quote `rejectionReason` verbatim. **`pending_review` is the terminal-from-Zernio state but NOT a launch confirmation** — the platform has not approved the ad yet, no spend has begun. Surface it as "submitted, awaiting platform review (12–24h typical)", never as "launched" or "active".
12. **Audit.** Run every check below.

## PUBLISH gate — what to print

- Every target: `{platform, account_alias, accountId, username}`.
- Every media file: local path, size, MIME, resulting publicUrl.
- Full caption / `content` text.
- Every field in `platformSpecificData` for IG / YT / Twitter / Discord, every field in `tiktokSettings` (top-level, not nested) for TikTok.
- Explicit AI-disclosure values per platform, even if false.
- `publishNow`, `scheduledAt`.
- TikTok: chosen `privacy_level` AND the `privacyLevels` array from creator-info.
- YouTube: `madeForKids`. If true, print the permanent-flag warning.
- Discord: `channelId`, channel type, `webhookUsername` if set, `poll`/`mediaItems` exclusivity confirmed.

`PUBLISH` (literal, case-sensitive) → proceed. `publish` / `yes` / `ok` / "yeah do it" / empty → abort.

## LAUNCH-AD gate — what to print

- Subcommand + platform: "boost-post on linkedinads", "create-audience on metaads".
- Full assembled payload, pretty-printed JSON, no summarization.
- Dollar exposure (computed per step 8).
- For audience-sync: PII row count + ("plaintext, hashed server-side by Zernio").
- For Meta: `specialAdCategories` if set; if missing on a clearly housing/employment/credit/political ad, ASK before launching.

`LAUNCH-AD` (literal, case-sensitive) → proceed. `PUBLISH` / `yes` / `confirm` / "looks good" → abort.

## AI disclosure

Caller sets per-post; skill never defaults. Treating unsure as true is the safe direction — disclosing human content as AI is not a TOS violation; the reverse is.

| Platform | Field | What "true" means |
|----------|-------|-------------------|
| YouTube | `containsSyntheticMedia` (in `platformSpecificData`) | realistic AI-generated content |
| TikTok | `video_made_with_ai` (in `tiktokSettings`) | AIGC label displayed |
| Instagram | none exposed via Zernio | manual label in IG app only |
| Twitter | none | no API field |

Set true if any of: media generated by Sora/Runway/Kling/Veo, audio TTS or voice-cloned, realistic human likeness altered, photorealistic AI stills. The platforms detect C2PA metadata; non-disclosure plus auto-detection equals an immediate strike on YT and TT.

## Audience sync (PII)

`create-audience` and `add-audience-users` send PII to Meta (and TikTok/Pinterest where supported). Rules:

- Send PII PLAINTEXT — Zernio SHA-256-hashes server-side per platform's normalization rules. Do NOT pre-hash, lowercase, trim, or strip dial codes.
- 10,000 row cap per request, enforced locally. Chunk larger lists into sequential calls.
- Lookalike requires `seedAudienceId` + `country` codes + `ratio` (1–10 percentage of country pop). Meta needs ≥ 100 matched users in the seed.
- Special-category compliance: set `specialAdCategories` on every ad that uses an audience for housing / employment / credit / political. Don't strip restricted fields silently — return Meta's 422 verbatim.
- Payload files contain plaintext PII. They live in `~/.zernio/output/` (outside repo, gitignored), NEVER in `raw/`. After a successful sync, ask if the user wants the payload deleted.

## Errors

| Class | Trigger | Action |
|-------|---------|--------|
| `retryable_now` | HTTP 5xx from Zernio, TLS / connection reset, presigned URL expired mid-PUT | retry up to 2× with 1s then 5s backoff |
| `retryable_later` | IG `100 posts / 24h`, TT `daily posting limit`, YT `quotaExceeded`, 429 | surface reset window; do NOT auto-retry |
| `fatal_content` | IG `Duplicate content`, IG `blocked your request`, IG `Cannot process video from this URL`, TT 30001 / 30005, YT `videoRejected`, X `does not allow duplicate tweets`, X `Tweet text is too long` | stop; return error; keep output files |
| `fatal_auth` | HTTP 401 from Zernio, "access token expired", account disconnected, X `Missing tweet.write scope` | tell user to reconnect at zernio.com/dashboard/accounts; do NOT rotate `ZERNIO_API_KEY` |
| `add_on_required` | 403 + body mentions Ads add-on | route to billing; do NOT retry |
| `partial_failure` | multi-platform post with mixed `status` in `platforms[]` | write full result file; caller decides whether to retry failed platforms individually; never auto-retry (successful posts are already live) |
| `async_pending` | post status `processing` after 200 | poll up to 5 min then reclassify `async_timeout` |
| `validation` | 422 with field-level message | quote field + message verbatim; never silently rewrite the payload |
| `platform_error` | 4xx with platform-side reason (Meta `(#100)`, LinkedIn `r_organization_admin`, TT `40002`) | quote verbatim; never retry; common fix is re-run `connect-ads` |

Specific platform recipes:
- IG `Duplicate content detected` ALSO fires on low-entropy test videos (solid colors, sine gradients) even on a fresh account. For tests, use visually-variable media + nonce in the caption.
- Meta `BUDGET_LEVEL_MISMATCH` (409) when updating a campaign budget on an ABO campaign → retry against `update-ad-set <adSetId>` instead. Read `budgetLevel` from `tree` first.
- LinkedIn 422 `INVALID_PARAMETER_VALUE r_organization_admin` → re-run `connect-ads linkedin <accountId>` to refresh scopes.
- LinkedIn `duplicate content` (422) on boost → post a fresh organic version first.
- TikTok `creative under review` is normal first-launch state (resolves 12–24h). Don't claim "rejected".
- Meta `special_ad_category_required` → prompt user for the category, set it, re-prompt LAUNCH-AD.

Never auto-retry write calls that returned 4xx — the first attempt may have created the campaign even if the response said error; retrying duplicates. Never strip targeting fields silently after 422. Never claim success when status is `pending_review` / `processing`.

## Audit (Pattern 12)

Run before declaring done. Surface any failure rather than silently claiming success.

| Check | Pass condition |
|-------|----------------|
| Payload saved BEFORE write | `zernio-payload-<ts>.json` (or `zernio-ads-payload-<ts>.json`) exists |
| Response captured | `zernio-result-<ts>.json` (or `zernio-ads-result-<ts>.json`) exists with request + response |
| Terminal status reached | organic: `published | scheduled` (not `processing | failed`); ads: `active | pending_review | paused | rejected | cancelled` (not `processing` or unset). For ads, `pending_review` is reported as "submitted, awaiting platform review" — never as "launched"/"active" |
| Multi-platform organic post: every `platforms[].status` is terminal | inspect `platforms[]` not just top-level `status` (top-level can mask one failed platform). Mixed terminal states classify as `partial_failure` |
| TikTok: `privacy_level` matched creator-info | value was in `privacyLevels` |
| YouTube: `madeForKids` matches caller input | explicitly set, not defaulted |
| Discord: `channelId` validated | in `discord-channels` for the connected guild |
| Discord: forum channel has `forumThreadName` | required for type 15 |
| Discord: poll xor media | never both in same payload |
| Discord: `webhookUsername` hygiene | 1–80 chars, no `clyde`/`discord` |
| AI-disclosure values match caller input | not skill defaults |
| Boost-post only: source post `published` on same `accountId` | verified before LAUNCH-AD |
| Audience-sync only: each chunk ≤ 10,000 rows | all chunks returned 2xx |
| Audience-sync only: PII sent PLAINTEXT | no client-side hashing |
| Conversion-only: stable `eventId` per event | for Meta dedup / Google `transactionId` mapping |
| Meta special-category | `specialAdCategories` set if housing/employment/credit/political |
| Dollar exposure matched gate | same number quoted to user |

## Budget

- Live posts / writes per run: no hard cap; platform rate limits apply.
- Audience-sync rows / request: 10,000 (enforced locally).
- Organic status polling: ≤ 60 iterations × 5s = 5 min.
- Ads status polling: ≤ 20 iterations × 30s = 10 min.

## Files

- `cli.sh` — single curl wrapper covering organic + ads
- `references/instagram.md` — `platformSpecificData` shape for feed / carousel / story / reels
- `references/youtube.md` — title / category / visibility / madeForKids / Shorts auto-detection
- `references/tiktok.md` — creator-info, `tiktokSettings` (top-level), privacy_level enum, consent flags, draft + publishNow precedence
- `references/twitter.md` — threads, replies, polls, longVideo (Premium), geo restriction
- `references/discord.md` — channelId, embeds, polls, forum starter posts, threads, crosspost, webhook identity
- `references/ads.md` — six ad platforms in one file: meta, google, linkedin, tiktok, pinterest, x (statuses, formats, payload shapes, common errors)
