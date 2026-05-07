# bumble (ULTRON dating)

Bumble automation for Adithya. Patchright-driven (no API-direct), human-paced, ban-aversion is priority #1.

Sibling of `bot/` (Tinder). Mirrors that doctrine, with Bumble-specific adjustments below. If a rule applies to Tinder and is not contradicted here, it applies here too.

## Hard Rules (non-negotiable)

1. **No `bumble.com/api/*`, `mobile.bumble.com/api/*`, or GraphQL replays. Ever.** All actions go through patchright driving the real web UI. API-direct fingerprints are a known shadowban vector and Bumble's anti-bot stack is at least as aggressive as Tinder's.
2. **Hard cap: 50 swipes/day** (half of Tinder, since Bumble's swipe surface is more closely watched). Distributed across 2-3 short sessions. Right-swipe ratio capped at 50% (sample down within filter if too many qualify).
3. **Daily message cap: 10/hour rolling window** with per-message gaps 60-300s. Effective throughput much lower than the cap; on hetero-mode matches the woman starts the conversation, so most outbound is replies, not openers.
4. **Skip 1-2 days/week randomly.** Probability 0.20.
5. **Sessions are short** (5-15 min). No marathon batches.
6. **Halt hard on detection signals**: Cloudflare Turnstile, photo-verification prompt, account-restriction banner, login wall, mode-not-Date. See `../setup/bumble/detection-ladder.md`.
7. **Auth is manual only.** Phone number flow. No Google/Facebook/Apple OAuth (extra fingerprint surfaces). Adithya logs into the dedicated chrome profile once.
8. **Selectors drift.** Re-verify before any production run after 7+ day gap. The bot self-checks on startup and halts loudly if selectors break.
9. **Always Date mode.** Halt if active mode is not Date. BFF/Bizz are off-scope.
10. **Bumble does not initiate openers on hetero matches.** Adithya cannot send the first message; the bot's send role is reply + nudge + extend.

## Why this is its own bot (not a Tinder clone)

- Bumble's 24-hour match expiration changes the cadence: matches die at 24h if she hasn't messaged; her message starts a new 24h timer for the man to reply. `decide.mjs` triages by expiry-imminence, not just recency.
- Bumble's Cloudflare + bot-mitigation stack is reportedly more aggressive than Tinder's. Tighter caps, longer pauses, single-strike breaker on Turnstile.
- Photo verification is pushed harder; verify in the real Bumble iOS/Android app, not in the bot.

## How it runs

There is no human-facing CLI. Cron fires `node scripts/<X>.mjs` directly (see `../setup/bumble/cron.md`). When Adithya wants to drive interactively, Claude (me) runs the scripts via Bash; Adithya never types `./bin/...`.

| Script | Purpose |
|--------|---------|
| `scripts/login.mjs` | Open patchright Chromium to bumble.com for one-time manual login |
| `scripts/swipe.mjs` | One swipe session (subject to caps) |
| `scripts/pull.mjs` | Scrape match list + thread snapshots into `../raw/bumble/<slug>.md` |
| `scripts/decide.mjs` | Walk every entity, cross-ref iMessage, draft replies via `claude -p`, queue to `../04-outbound/bumble/` |
| `scripts/send.mjs` | Drain `../04-outbound/bumble/approved/` via patchright (one msg per fire) |
| `scripts/visualize.mjs` | Per-entity visual ingest: open thread, capture photos, send to cloud-llm, append `## Visual` section. NO-FACIAL-FEATURES guardrail. Skips entities that already have a `## Visual` section unless `BUMBLE_VISUALIZE_FORCE=<slug,slug>` is set. `BUMBLE_VISUALIZE_SLUG=<one>`, `BUMBLE_VISUALIZE_LIMIT=<n>`. |
| `scripts/rematch.mjs` | Automate Bumble's in-app extend flow on expiring matches. `BUMBLE_REMATCH_LIMIT/SLUG/DRY` env knobs. |
| `scripts/status.mjs` | Counters, queue sizes, halt state, entity counts by city/status |
| `scripts/self-check.mjs` | Pre-flight env / deps / config / halt |
| `scripts/selector-check.mjs` | Interactive DOM selector verification |
| `scripts/diag.mjs` | Self-heal entry point: launches Chromium + dumps DOM survey + screenshots when something breaks |
| `scripts/discover-dom.mjs` | One-shot DOM probe: visit each surface, dump candidate selectors. Used when selectors drift. |
| `scripts/discover-network.mjs` | One-shot XHR/fetch probe (read-only, never replayed). Used during diag for drift detection. |

### Drafting via `claude -p`

Drafts come from `claude -p`, which uses Adithya's Claude Code subscription; no separate API key. The voice profile (`../config/bumble/voice/`) is composed into each prompt. Override model with `BUMBLE_MODEL` (default: `sonnet`).

## Layout

```
ULTRON/workspaces/dating/
  bot-bumble/                            # this bot
    package.json                         # name: dating-bumble-bot
    src/
      runtime/
        profile.mjs                      # patchright launch + persistent context + lock
        humanize.mjs                     # ghost-cursor + per-char typing + idle pauses
        caps.mjs                         # daily/hourly counters, persisted state
        detection.mjs                    # Turnstile / photo-verify / restriction-banner / login-wall watchers
        logger.mjs                       # session events (NDJSON)
        entity-store.mjs                 # per-person markdown CRUD
        city.mjs                         # city resolver
        slug.mjs                         # slug generator <first>-<source>-<city>[-<n>]
        imessage-xref.mjs                # Contacts lookup + iMessage activity scan
        queue.mjs                        # 04-outbound/bumble/* file-based queue
        halt.mjs                         # ~/.ultron/dating/bumble/.halt state
        notifier.mjs                     # AppleScript -> self-iMessage on halts (DATING_SELF_PHONE)
        paths.mjs                        # absolute path constants for this bot
        mode-guard.mjs                   # asserts Date mode active; halts on BFF/Bizz
        expiry.mjs                       # 24h match-expiry tracking
        location.mjs                     # location/distance utilities
      bumble/
        page.mjs                         # navigation primitives
        swipe.mjs                        # swipe-loop primitives
        matches.mjs                      # match-list scrape + per-thread upsert
        send.mjs                         # outbound message via patchright
      drafting/
        voice-loader.mjs                 # loads ../config/bumble/voice/ into a single prompt block
        draft.mjs                        # `claude -p` invocation, returns draft + lint
        voice-lint.mjs                   # rule checker (length, em-dashes, banned words, AI tells)
    scripts/                             # entry points (see table above)
    .profile/                            # gitignored; patchright persistent context lives here
  config/bumble/                         # caps.json, schedule.json, filter.json, selectors.json, cities.json, voice/
  raw/bumble/                            # per-match entity .md files (slug = <first>-bumble-<city>)
  04-outbound/bumble/                    # drafts/ pending/ approved/ sent/ expired/ auto-sent/
  setup/bumble/                          # chrome-profile.md, login.md, selector-verify.md, detection-ladder.md, cron.md

ULTRON/_shell/plists/
  com.adithya.ultron.dating-bumble-{swipe,pull,send}.plist

~/.ultron/dating/bumble/                 # state home
  .halt                                  # presence blocks all sessions
  .rate-state.json                       # per-day / per-hour counters
  sessions.ndjson                        # event log
  deleted/                               # tracked "Deleted account" matchIds (don't pollute graph)
```

## Where data lives

Per-person entity files at `raw/bumble/<first>-bumble-<city>.md`:

```markdown
---
slug: caroline-bumble-austin
first_name: caroline
source: bumble
city: austin
match_id: <hex>
person_id: <hex>
phone: null
status: new            # new | active | nudge_pending | gone_dark | unmatched | expired
expires_at: 2026-05-03T14:32:11Z   # 24h after last activity
first_seen: 2026-05-02T14:32:11Z
last_activity: 2026-05-02T14:32:11Z
last_scrape: 2026-05-02T14:32:11Z
previous_slugs: []
---

## Profile
(overwritten on every rescrape)

## Conversation
(append-only timeline)
**her** 2026-05-02 14:32 hey
**you** 2026-05-02 14:35 hey, what's up

## Outbound log
(append-only event list)
- 2026-05-02 14:35 sent (auto, reply) [draft:abc12345] lint=true "hey, what's up"
```

Slug rule: `<first>-bumble-<city>`. Collisions get `-2`, `-3`, etc.

City buckets: **austin**, **sf**, **la**, **nyc**. Resolution is phone area code first, then Bumble distance from Austin (<=100mi -> austin), else default home (austin).

Session-level events go to `~/.ultron/dating/bumble/sessions.ndjson`; entity files stay clean for graphify.

## Cross-workspace dependencies

- **Reads legacy `/Users/shakstzy/QUANTUM/raw/imessage/YYYY-MM.ndjson`** until ULTRON ingests iMessage. See `paths.mjs` IMESSAGE_DIR TODO.
- **Writes nothing outside `raw/bumble/`, `04-outbound/bumble/`, `~/.ultron/dating/bumble/`, and `bot-bumble/.profile/`.**

## Auto-send doctrine (2026-05-04 flip)

All lint-pass drafts auto-approve. No HITL gate. Lint is the only guardrail; lint-fail drafts are discarded (not sent) and the next decide cycle re-drafts.

| Type | Mode | Why |
|------|------|-----|
| Reply where she sent something substantive | auto | Adithya 2026-05-04: "auto approve and auto send and never wait for my input again" |
| 24h-expiry nudge to her | n/a | Bumble shows extend buttons in-app; `scripts/rematch.mjs` automates that |
| Re-engagement after iMessage silence (5+ days) | auto | Short, one-shot, low-stakes |
| Anything matching `voice-lint.mjs` failure | DISCARD | em-dash / AI-tells / banned phrases / >320 chars / >3 sentences silently dropped; re-draft on next decide |
| Anything past message #6 in the thread | auto | Same flip; lint guardrail still applies |

`drafts/` and `pending/` stages are no longer used by `decide.mjs`. Lint-pass drafts go straight to `approved/` with `mode: auto, auto_approved: true`. `send.mjs` drains `approved/` -> `auto-sent/`.

Volume is rate-limited by the cap layer (10 messages/hour rolling, 60-300s between sends, 50 swipes/day) and the launchd schedule (15 send fires/day spread 9:08-22:51, each fire sends one message, 0-30min jitter). At max throughput that's ~10 sent/day = natural human pace.

## Detection ladder (halt and log on any)

1. Cloudflare Turnstile iframe -> halt; alert user; manual solve required
2. Photo verification request modal -> halt; in-person resolution via real Bumble iOS app
3. Account restriction / "We've noticed unusual activity" banner -> halt; investigation needed
4. Login wall / "Your session has expired" -> halt; alert user; manual login
5. Mode is not Date (BFF or Bizz active) -> halt; user check
6. Zero matches in 7 days while swiping -> assume soft shadowban; halt; alert user
7. Selector self-check fails on startup -> halt; run `selector-check.mjs` interactively

State file: `~/.ultron/dating/bumble/.halt`; presence blocks all sessions until removed.

## Discovery / self-heal

`scripts/discover-dom.mjs` and `scripts/discover-network.mjs` are durable diagnostic probes (run when selectors drift, not throwaway). `scripts/diag.mjs` is the self-heal entry point that orchestrates them when something breaks. Output lands in `.dev-fixtures/<ts>/`.

## Learnings (agent-drafted, user-approved)

<!-- decide.mjs may propose additions to this section based on:
     - Which message patterns led to number-close
     - Which times of day yielded highest reply rate
     - Selector drift events
     - Detection ladder firings -->

### Time-of-day reply patterns

_(empty)_

### Selector drift log

_(empty)_

### Detection events

_(empty)_
