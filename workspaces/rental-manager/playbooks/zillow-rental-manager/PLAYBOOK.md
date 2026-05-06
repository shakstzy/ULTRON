---
name: zillow-rental-manager
description: Drive Zillow Rental Manager from Claude Code to list a rental, triage inbound leads, reply to inquiries, and run persistent follow-up cadence. Browser automation via patchright over a dedicated Chrome profile. Designed for Adithya's owner account managing his rental property.
---

# Zillow Rental Manager Playbook

Patchright-driven automation for zillow.com/rental-manager. Persistent Chrome profile. Visible-login bootstrap. Pidfile + 24h circuit breaker on 403 / captcha.

## SHAKOS integration

- **Home:** `workspaces/rental-property/playbooks/zillow-rental-manager/` (Pattern 9 placement). Registered in `workspaces/rental-property/CLAUDE.md` Routing + What to Load tables.
- **Chrome profile:** `~/.shakos/chrome-profiles/zillow-rental-manager/` (persistent, per the global Browser Automation rule). First login is manual; session survives restarts.
- **MCP entry:** `chrome-devtools-zillow-rental-manager` registered in root `.mcp.json`. Dev-time DOM inspection only. Production goes through the playbook's own patchright runtime.
- **Workspace build:** stub registered; full `stages/` scaffold + workspace-local wiki are deferred until workspace-builder is invoked on this vertical (see `workspaces/rental-property/CLAUDE.md` Pending Work section).

## Browser Runtime Contract (Pattern 18)

| Item | Path / Value |
|------|--------------|
| Profile directory | `~/.shakos/chrome-profiles/zillow-rental-manager/` (override with `ZRM_PROFILE_DIR`) |
| Login command | `node scripts/run.mjs login` (from this playbook's folder) |
| Status check | `node scripts/run.mjs status` |
| Pidfile | `~/.shakos/chrome-profiles/zillow-rental-manager/.skill.pid` (atomic `openSync(..., 'wx')`) |
| Breaker file | `~/.shakos/chrome-profiles/zillow-rental-manager/.breaker.json` |
| Breaker trip condition | Two top-level-navigation 403s from zillow.com within 24h (60s strike-debounce) OR captcha DOM detection |
| Breaker cooldown | 24h halt; reset with `node scripts/run.mjs reset-breaker` |
| Proxy (optional) | `ZRM_PROXY` residential only; consumer VPNs refused |

## When this fires

Triggers (once wired into workspace CLAUDE.md): "manage my Zillow listing", "reply to Zillow lead", "follow up with Zillow inquiries", "Zillow rental inbox", "relist my property on Zillow".

Out of scope for v1: Apartments.com, Facebook Marketplace, Craigslist, off-platform SMS. (iMessage / contacts integration is a separate future playbook.)

## First-time setup (once)

```bash
cd workspaces/rental-property/playbooks/zillow-rental-manager
node scripts/run.mjs login
```

Opens a visible Chrome window on `https://www.zillow.com/rental-manager/`. Sign in with Adithya's owner account (Zillow may send an email verification code). Skill polls for a signed-in signal (rental-manager URL + owner-nav DOM, no login form). On success, cookies persist to `~/.shakos/chrome-profiles/zillow-rental-manager/`. Future runs reuse silently. If session expires, re-run `login`.

## Commands (v2 — inbox + send)

```bash
# Setup / lifecycle
node scripts/run.mjs login                           One-time Zillow sign-in (visible Chrome)
node scripts/run.mjs status                          Profile + breaker + daemon + pacing state
node scripts/run.mjs reset-breaker                   Clear 24h halt
node scripts/run.mjs reset-pacing                    Clear paced-call log (after long downtime)
node scripts/run.mjs pacing-status                   Show last call, hourly + daily counts, caps

# Daemon (currently optional; CDP attach is broken on Chrome 147)
node scripts/run.mjs daemon-start                    Spawn long-lived Chrome (port 9222)
node scripts/run.mjs daemon-stop                     Stop the daemon Chrome
node scripts/run.mjs daemon-status                   pid, CDP reachability, Chrome version

# Inbox + lead operations (UI-driven; observe GraphQL responses)
node scripts/run.mjs pull-inbox [--max=N]            Fetch inbox list, then for each unread lead:
                                                     navigate /inbox/<alias>/<cid>, capture
                                                     MessageList_GetConversation, persist a
                                                     graph-linkable lead markdown to
                                                     ~/QUANTUM/raw/rental-property/leads/<slug>.md
                                                     Paced 45-90s between fetches.
node scripts/run.mjs pull-thread <conversation_id>   Pull one thread by ID (re-fetches inbox first
                                                     to resolve listingAlias). Persists markdown.
node scripts/run.mjs send-reply <cid> "<body>" [--live]
                                                     Type body into the conversation. DEFAULT IS
                                                     DRY-RUN: types the body and clears it without
                                                     clicking Send. Pass --live to actually send.
                                                     Saves an immutable audit bundle either way at
                                                     ~/.shakos/playbook-output/zillow-rental-manager/
                                                     audit/<yyyy-mm-dd>/<id>/

# Diagnostic
node scripts/run.mjs explore [url]                   Open visible Chrome on URL; leave it open
node scripts/run.mjs snapshot <url> <out-dir>        Dump HTML + PNG (forensics)
```

Follow-up cadence handler (`follow-up`) is the next build. State already exists per-thread.

## Global flags + env

```
--headless               Run without visible browser (login must be visible; reads/sends ok)
--force                  Bypass breaker halt (discouraged)
--max=N                  pull-inbox: cap target threads per run (default: all unread)
--live                   send-reply: actually click Send (default is dry-run)
ZRM_PROFILE_DIR          Override profile dir
ZRM_DEBUG_PORT           CDP debug port (default 9222)
ZRM_PROXY                Residential proxy only; consumer VPNs refused
ZRM_MIN_GAP_MS           Min gap between paced ops (default 45000)
ZRM_MAX_GAP_MS           Max gap (jitter ceiling, default 90000)
ZRM_HOURLY_CAP           Max paced ops per hour (default 20)
ZRM_DAILY_CAP            Max paced ops per 24h (default 100)
ZRM_DEBUG=1              Print stack on error
```

## Architecture (v2)

PerimeterX bypass is purely behavioral — we look exactly like a human user clicking through the inbox. No request replay, no JA3 spoofing, no proxy rotation, no captcha-solver. Three layers do all the work:

### 1. Browser layer (`scripts/browser.mjs`)
- **Patchright + bundled Chromium** (NOT system Chrome). System Chrome 147 disabled CDP browser-context-management (`Browser.setDownloadBehavior` errors), which broke both `launchPersistentContext({channel:'chrome'})` and `connectOverCDP`. The bundled Chromium at `~/Library/Caches/ms-playwright/chromium-1217` doesn't have that restriction. Patchright's stealth patches were tested against this bundled build, so fingerprint surface is also more predictable.
- **`killOrphanProfileProcesses()` runs on every launch** — scans `ps` for any process holding `--user-data-dir=$PROFILE_DIR` (e.g. orphan `chrome-devtools-mcp` from prior Claude Code sessions) and SIGKILLs them. Without this, SingletonLock causes Chrome to silently die on launch ("context closed" error).
- **`persistZillowSessionCookies()` on context close** — Chrome drops session cookies on teardown by default. Before close, this scans for Zillow cookies with `expires=-1` or `0` and re-adds them with a 30d TTL. Required to keep the CIAM session alive between commands.
- **Circuit breaker** trips on (a) two top-level-nav 403s from zillow.com within 24h (60s strike-debounce) or (b) captcha DOM. 24h cooldown.

### 2. Pacing layer (`scripts/pacing.mjs`)
- File-backed call log at `~/.shakos/playbook-output/zillow-rental-manager/state/pacing.json` (atomic tmp+rename). Survives process restarts.
- **`enforceMinPacing(label)`** sleeps until 45-90s (jittered) since the last paced call.
- **Hard caps**: 20 paced calls per rolling hour, 100 per rolling 24h. Throws typed errors (`PACING_HOURLY_CAP`, `PACING_DAILY_CAP`) when hit so callers can abort the run cleanly.
- Pacing happens BEFORE Chrome launches — patchright's idle about:blank tab can auto-quit during long sleeps, so we sleep with no Chrome open.
- **`humanBeat(page)`** does small mouse jitter + scroll between paced actions. Cheap, non-blocking.

### 3. Inbox driver (`scripts/inbox.mjs`)
- **`pullInboxList(page)`**: navigate `/rental-manager/inbox`, observe `ConversationList_GetConversations` GraphQL response via `page.on('response')`, extract conversations.
- **`pullThread(page, cid, alias)`**: navigate directly to `/rental-manager/inbox/<alias>/<cid>` (NOT click — Zillow's SPA detects "click on already-selected thread" and skips the GraphQL refire). Observe `MessageList_GetConversation`, parse out messages + renter profile + inquiry (name, phone, credit, income, lease, pets).
- **`sendReply(page, cid, body, {dryRun})`**: fill compose textarea with human-cadence typing (35-105ms/char), `humanBeat`, click Send (or skip on dry-run), observe the mutation response, capture pre/post screenshots into an immutable audit bundle.

### 4. Storage layer (`scripts/storage.mjs`)
- **Tier 1 (graph-linkable)**: `~/QUANTUM/raw/rental-property/leads/<slug>.md` per lead. Frontmatter has E.164 phone, lowercase email, kebab-case slug, listing_alias, conversation_id, status_label. Body has messages timeline + renter profile attributes. Idempotent: same slug rewrites the same file. QUANTUM Graphify auto-picks this up on next lint pass and cross-edges by phone/email.
- **Tier 2 (operational)**: `~/.shakos/playbook-output/zillow-rental-manager/state/threads/<cid>.json` per-thread state, `audit/<yyyy-mm-dd>/<id>/` immutable send bundles, `network/<yyyy-mm-dd>/` redacted GraphQL captures (forensics).

### Flow per command
1. Caller calls `enforceMinPacing(label)` BEFORE launching Chrome.
2. `connectOrLaunch` → tries CDP attach to a running daemon, falls back to fresh patchright `launchPersistentContext` (which is what currently works).
3. Navigate to the target URL. `page.on('response')` captures the relevant GraphQL response.
4. Parse, persist to Tier 1 + Tier 2.
5. `humanBeat` (mouse jitter + scroll), then close.

### Why no programmatic captcha bypass
PerimeterX's press-and-hold uses micro-movement timing + hardware telemetry analyzed across multiple seconds. The model also updates frequently, so any solver written today rots fast. Empirically the press-and-hold only fires when we burst >10 calls in 30s. Pacing 45-90s + 20/hr cap mathematically prevents burst, so the challenge never spawns. Both Codex and Gemini agreed on this approach (Gemini wrote the original brief; Codex refused on ToS grounds and recommended email-channel only — rejected because Zillow strips phone/credit/application data from forwarded emails).

## Follow-up cadence (design intent, not yet coded)

Per Adithya's spec:
- Week 1: daily follow-up
- Weeks 2-3: every 2 days
- Week 4+: every 3 days (exponential decay ceiling TBD)
- **Never disqualify** a lead. Pings persist until tenant is locked or Adithya manually freezes the lead.
- Auto-send enabled after the first manual approval per lead. First message on each new thread always gets draft-and-review.

## Files

- `scripts/browser.mjs` -- patchright launchPersistentContext wrapper. Atomic pidfile (openSync 'wx'). Breaker trips only on top-level-navigation 403s with 60s strike-debounce. `escalateOnCaptcha()` for production paths. `installGracefulShutdown()` for callers to close context cleanly on SIGINT/SIGTERM. No custom fingerprint layer (stock patchright defaults are more reliable than ad-hoc noise).
- `scripts/login.mjs` -- single-target auth probe: navigate directly to /rental-manager/properties/ (an owner-only path) and poll until the URL stays there with no login form. Periodically re-navigates if Zillow drops the user on a non-probe URL after sign-in. Skips renavigation while user is mid-signin on identity.zillow.com. Respects breaker (no implicit --force). Earlier two-phase design was abandoned: /rental-manager/ alone is a public marketing page when unauthenticated, so phase-1 false-positived without ever prompting sign-in.
- `scripts/run.mjs` -- CLI dispatcher. Commands wire their own graceful-shutdown so Ctrl-C closes Chrome before exit.
- `package.json` -- patchright 1.59.4, `postinstall: "patchright install chrome"`
- `rules/` -- reserved for per-surface selector maps (filled after surface mapping pass)

## Known limits (v1)

- No inbox scrape, reply send, or follow-up scheduler yet. `explore` / `snapshot` only.
- No relist flow yet.
- No property-level config (rent, beds, etc.) until workspace scaffolds and `shared/property.md` exists.
- Headless login is unreliable (Zillow sends email verification on unfamiliar device); use visible Chrome.
- No iMessage / contacts integration (deferred to separate shared playbook).

## Troubleshooting

| Problem | Action |
|---------|--------|
| "Profile locked by pid N" | Another invocation is running. Wait, or kill pid if stale. |
| "Circuit breaker HALT active" | Solve captcha manually at zillow.com in your normal browser, then `run.mjs reset-breaker`. |
| Login timeout | Session did not complete in 10 min. Re-run; check your email for Zillow's verification code. |
| 403 on first page load | Zillow flagged the profile. Wait, switch IP (tether or residential proxy), retry. |
| `npm install` fails on `patchright install chrome` | Run it manually in the playbook dir; network-restricted environments may block the Chrome download. |

## Notes on ToS

Automated access to Zillow likely violates their Terms of Service. Adithya is operating on his own listing with his owner account; enforcement risk on a single-property owner account is low, but not zero. Use is at his discretion. Avoid aggressive cadence or parallel profiles that would look like a rental-agent farm.
