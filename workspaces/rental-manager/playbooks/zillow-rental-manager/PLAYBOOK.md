---
name: zillow-rental-manager
description: Drive Zillow Rental Manager from the rental-manager workspace to pull leads, reply to inquiries, and run follow-up cadence. Real-Chrome + CDP + rebrowser-playwright.
---

# Zillow Rental Manager Playbook

Owner-side automation for `zillow.com/rental-manager`. Real Chrome daemon on port 9222 + rebrowser-playwright CDP attach. Lead markdown is committed under `raw/leads/`; operational state is local-only under `state/`.

## What's where

| Item | Path |
|------|------|
| Code | `scripts/` (everything imports from `paths.mjs`) |
| Lead markdown (committed) | `../../raw/leads/<slug>.md` |
| Application packets | `../../raw/applications/<slug>/{source.pdf,parsed.md}` (PDF gitignored) |
| Chrome profile | `../../state/chrome-profile/` (gitignored) |
| Pacing log | `../../state/pacing.json` |
| Breaker file | `../../state/breaker.json` |
| Daemon pidfile | `../../state/chrome-profile/.daemon.pid` |
| Audit bundles (per send) | `../../state/audit/<yyyy-mm-dd>/<id>/` |
| GraphQL captures | `../../state/network/<yyyy-mm-dd>/` |
| Batch run logs | `../../state/batch-followup/<runId>.{ndjson,start,done,aborted,crashed}` |

All paths derive from `paths.mjs`; nothing hard-codes a SHAKOS / QUANTUM / shakos prefix.

## Browser stack — why this exact combo

- **Real system Chrome daemon** (`/Applications/Google Chrome.app`, `--remote-debugging-port=9222`). Bundled Chromium leaks the absence of Widevine + H.264 codecs, which PerimeterX scores. Real Chrome has both.
- **rebrowser-playwright** for the CDP attach. Stock Playwright's `Runtime.enable` instrumentation is a known PX flag (Gemini diagnostic 2026-05-05); rebrowser-patches plugs it at the source-code level.
- **patchright** still in `package.json` only for the legacy `launchContext` fallback path used by `explore` / `snapshot`. Production (batch / send) goes through the daemon.

## Commands

Run from this directory.

```bash
# Lifecycle
node scripts/run.mjs login                       # one-time visible-Chrome sign-in
node scripts/run.mjs status                      # profile + breaker + daemon + pacing
node scripts/run.mjs daemon-start                # spawn long-lived Chrome
node scripts/run.mjs daemon-stop
node scripts/run.mjs reset-breaker               # clear 24h halt after manual captcha
node scripts/run.mjs reset-pacing                # wipe paced-call log

# Read
node scripts/run.mjs pull-inbox [--max=N]        # delta-only via lead checkpoint
node scripts/run.mjs pull-thread <cid>           # single thread

# Write
node scripts/run.mjs send-reply <cid> "<body>" [--live]   # default dry-run

# One-shot blast
node scripts/batch-followup.mjs --dry --limit 3            # smoke
node scripts/batch-followup.mjs --live [--resume <runId>]
```

## Pacing

Defined in `scripts/pacing.mjs`. Hard ceilings: 150/hr, 600/24h, 4s gap floor. Defaults: 120/hr, 400/24h, 5-10s gap. Env vars (`ZRM_HOURLY_CAP`, `ZRM_DAILY_CAP`, `ZRM_MIN_GAP_MS`, `ZRM_MAX_GAP_MS`) can lower throughput; never raise. A 403 nav response trips the breaker; one strike enters a 4h post-flag cooldown, two strikes within 24h halt for 24h.

## Auth lifecycle

`login.mjs` opens visible Chrome, polls until `/rental-manager/properties/` loads with no login form. Auth lives in the persistent profile under `state/chrome-profile/`. `persistZillowSessionCookies` upgrades session cookies to 30d TTL on context close so they survive Chrome restarts. If `zjs_user_id` goes null mid-batch, the run aborts with `err.code === 'AUTH_LAPSED'` and writes a `<runId>.aborted` marker; resume after `node scripts/run.mjs login` with `--resume <runId>`.

## Architecture flow per send

1. Daemon already running and warmed up (homepage GET established a healthy `_px3` token).
2. CDP attach via rebrowser-playwright `connectOverCDP`.
3. `enforceMinPacing` sleeps 5-10s since last paced call.
4. `goto(threadUrl)` — direct nav, NOT click (the SPA skips `MessageList_GetConversation` on click-on-already-selected).
5. Auth check via `context.cookies(['https://www.zillow.com'])` reading `zjs_user_id`. If null, throw `AUTH_LAPSED`.
6. Wait for `[data-testid="textarea-autosize"]` (compose textarea).
7. Paste-fill body via native value-setter + `input` + `change` events (default; `ZRM_HUMAN_TYPING=1` reverts to per-char keyboard.type).
8. Click Send. Observe mutation response.
9. Append outbound to thread state, regenerate lead markdown, write audit bundle.

## Recovery

| Problem | Fix |
|---------|------|
| `AUTH_LAPSED` mid-batch | `node scripts/run.mjs login`, then `--resume <runId>` |
| Press-and-hold on every nav | Profile poisoned. `rm -rf state/chrome-profile/`, hotspot, re-login. |
| `WARMUP_403` | Daemon auto-stopped to prevent attach loop. Same fix as above. |
| Daemon hung | `daemon-stop && daemon-start` |
| Breaker halted | Solve captcha in normal Chrome on zillow.com → `run.mjs reset-breaker` |

## Notes on ToS

Automated access likely violates Zillow's Terms of Service. Adithya is operating on his own listing with his owner account; enforcement risk on a single-property owner account is low, not zero. Avoid aggressive cadence or parallel profiles that look like a rental-agent farm.
