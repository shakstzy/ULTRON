---
name: podcast-outreach
description: Eclipse podcast licensing outreach pipeline. Discovers conversational podcasts via Listennotes (patchright + CDP network capture, RSS owner-email fallback), sends Sydney's Human-API licensing pitch from adithya@eclipse.builders via gog, labels every send as `podcast - archived`, scans daily for inbound replies and promotes those threads to `podcast - priority`. Runs daily as a launchd cron. All write verbs default to dry-run; `--send` to execute. Pricing replies escalate to Adithya — skill never quotes a rate. Trigger phrases like "run podcast outreach", "scrape more podcasts for outreach", "scan podcast replies", "promote replies to priority", "fill the podcast outreach queue", "podcast outreach status".
---

# podcast-outreach (ULTRON / eclipse)

Eclipse Labs' inbound funnel for the Human API podcast licensing program. One Node project under `_shell/skills/podcast-outreach/`, one dispatcher (`scripts/run.mjs`), one persistent Chrome profile at `_credentials/browser-profiles/podcast-outreach/`. Daily cron fans out across varied Listennotes seeds, captures podcast metadata + RSS-owner emails, dedups against past sends, sends Sydney-approved templated pitch from `adithya@eclipse.builders`, and watches for replies to promote.

## Why this skill exists

Adithya's signed Lisa/Jaeden deals (`$25/hr flat`, exclusive licensing) prove the funnel works one-on-one. We need volume — fill the 2000/day Workspace send cap with on-brand outreach to **conversational** podcasts (the agreement requires dialogue between 2+ speakers in English at 44.1kHz / 16-bit). The skill mechanizes discovery, dedup, and labeling so Adithya only handles negotiations.

## Hard rules

1. **Never quote a rate.** When a podcast replies asking pricing, the scan-replies stage promotes the thread to `podcast - priority` and notifies Adithya. The skill never auto-replies. The old $25/hr was a flat one-off; the new model is 5%-upfront-of-reserves at a per-deal negotiated rate, and only Adithya negotiates.
2. **Dry-run by default.** Every write verb (`send`, `daily-cycle`) requires explicit `--send` to actually mail. Default behavior renders + logs + dedups but does not POST to gmail. Mirrors the WhatsApp / LinkedIn agent-learning rule.
3. **Single account.** All sends from `adithya@eclipse.builders` only. The skill rejects any other `--from` value.
4. **Single workspace.** Outputs land under `workspaces/eclipse/raw/listennotes/` — skill is hard-coded to eclipse.
5. **2000/day hard cap.** Google Workspace's send ceiling. The skill aborts the send loop if cap hit. Hourly throttle = 200/hr with ±30s jitter to avoid spam triggers.
6. **No upfront flat-rate buyouts.** The skill never offers the $25/hr Jaeden terms. The template asks for hours-of-audio estimate and proposes a follow-up call — pricing happens off-skill, in Adithya's reply.
7. **Never email an address twice.** Dedup is a three-layer check: local sent-log, gmail thread search by `to:<email>`, and label-existence check on `podcast - archived` / `podcast - priority`.

## Skill layout

```
_shell/skills/podcast-outreach/
├── SKILL.md                    this file
├── package.json                patchright + fast-xml-parser deps
├── config/
│   ├── caps.json               daily/hourly caps + pacing knobs
│   └── seeds.yaml              genre + topic + popularity seeds for variety
├── templates/
│   └── initial-outreach.md     pitch body + subject
├── scripts/
│   ├── run.mjs                 single dispatcher — every verb
│   └── cron-cycle.mjs          launchd entrypoint (daily-cycle wrapper)
├── src/
│   ├── discover/
│   │   ├── listennotes.mjs     patchright + CDP listener (Network.responseReceived)
│   │   ├── rss-extractor.mjs   fetch RSS, parse <itunes:owner><itunes:email>
│   │   └── seed-cursor.mjs     advance through seeds.yaml across runs
│   ├── pipeline/
│   │   ├── queue.mjs           queue.jsonl read/append/peek
│   │   ├── sent-log.mjs        sent.jsonl dedup index
│   │   └── labels.mjs          ensure `podcast - archived` / `podcast - priority` exist; apply via gog
│   ├── sender/
│   │   ├── template.mjs        render template w/ {podcast_name}, {host_first}, {recent_episode}
│   │   └── gmail-send.mjs      gog gmail send wrapper, returns thread id
│   ├── replies/
│   │   └── scanner.mjs         find archived threads w/ inbound replies, promote to priority
│   └── runtime/
│       ├── paths.mjs           every path lives here
│       ├── logger.mjs          ndjson + colored stdout
│       ├── caps.mjs            daily/hourly cap enforcement
│       ├── humanize.mjs        jittered sleep
│       └── halt.mjs            .halt kill switch
└── tests/
    └── template.test.mjs       smoke test for template rendering
```

## ULTRON paths

| Item | Path |
|------|------|
| Skill home | `~/ULTRON/_shell/skills/podcast-outreach/` |
| Persistent Chrome profile | `~/ULTRON/_credentials/browser-profiles/podcast-outreach/` |
| State home | `~/.ultron/podcast-outreach/` |
| Halt file (kill switch) | `~/.ultron/podcast-outreach/.halt` |
| Queue (pending outreach) | `~/.ultron/podcast-outreach/queue.jsonl` |
| Sent log (dedup canonical) | `~/.ultron/podcast-outreach/sent.jsonl` |
| Reply log (priority promotions) | `~/.ultron/podcast-outreach/replies.jsonl` |
| Daily counters | `~/.ultron/podcast-outreach/state/rate-state.json` |
| Seed cursor | `~/.ultron/podcast-outreach/state/seed-cursor.json` |
| Action audit log | `~/.ultron/podcast-outreach/state/actions.ndjson` |
| Discover artifacts | `~/.ultron/podcast-outreach/discover/<ts>/` |
| Listennotes raw deposits | `~/ULTRON/workspaces/eclipse/raw/listennotes/<yyyy-mm>/<podcast-slug>.md` |

## First-time setup (once)

```bash
cd ~/ULTRON/_shell/skills/podcast-outreach
npm install                                   # postinstall fetches chromium (~300MB)
gog auth login adithya@eclipse.builders       # Adithya: re-auth in browser if token expired
node scripts/run.mjs ensure-labels --send     # creates `podcast - archived` + `podcast - priority`
```

`ensure-labels` is idempotent — safe to re-run. The persistent Chrome profile for Listennotes is anonymous (no login required) but reused across runs to keep cookie/cache state warm and reduce bot-flag heuristics.

## Verbs

All verbs go through `node scripts/run.mjs <verb> [flags]`. Write verbs (`send`, `daily-cycle`, `ensure-labels`) default to dry-run; pass `--send` to execute. Read verbs (`status`, `discover`, `scan-replies --dry-run`) are safe by default.

| Verb | Usage | Output |
|------|-------|--------|
| `status` | `run.mjs status [--json]` | halt + queue size + sent-today + cap remaining |
| `ensure-labels` | `run.mjs ensure-labels [--send]` | creates `podcast - archived` + `podcast - priority` if missing |
| `discover` | `run.mjs discover [--seeds N=10] [--target-queue N=2500] [--headful]` | scrapes Listennotes via N parallel CDP-instrumented tabs, fetches RSS for emails, dedups, appends to queue |
| `enqueue` | `run.mjs enqueue <jsonl-file>` | bulk-append a hand-curated batch (skips dedup-collisions) |
| `send` | `run.mjs send [--limit N=200] [--send]` | pop N from queue, render, gmail-send, label `podcast - archived`, log |
| `scan-replies` | `run.mjs scan-replies [--lookback Nd=14d] [--send]` | find archived threads w/ inbound replies → relabel `podcast - priority`, ping Adithya |
| `daily-cycle` | `run.mjs daily-cycle [--send]` | full cron pass: scan-replies → top-up queue if <2000 → send up to daily cap |
| `dump-queue` | `run.mjs dump-queue [--limit N]` | emit queue contents for inspection (no mutation) |
| `halt` | `run.mjs halt` / `run.mjs halt --clear` | toggle kill switch |

### `daily-cycle` (the cron entrypoint)

1. Abort if `.halt` exists.
2. **scan-replies** (always live; promoting labels is non-destructive).
3. Read `sent-log` count for today; compute remaining headroom against 2000/day cap.
4. If `queue` size < `target_queue` (default 2500), run **discover** with seeds advanced from cursor.
5. Pop up to `min(headroom, hourly_cap × hours_remaining_today)` from queue.
6. **send** loop with 200/hr throttle, ±30s jitter.
7. Audit-log every action; emit a status line to `_logs/<label>.out.log`.

## Listennotes scrape (CDP)

We don't use the Listennotes paid API. We drive their public web pages with patchright + a CDP `Network.responseReceived` listener.

1. Open `https://www.listennotes.com/best-podcasts/<genre>/` or `/search/?q=<topic>` for each seed.
2. Attach a CDP session: `await page.context().newCDPSession(page)`.
3. Listen to `Network.responseReceived` events. Filter for `application/json` mimeType + URLs matching their internal API patterns (`/api/v1/podcasts/`, `/api/v2/`, embedded hydration JSON in script tags).
4. For each podcast surfaced, extract `{listennotes_id, title, rss_url, website, genre_ids, latest_episode_title, host_name?}`.
5. **Email source.** Listennotes' internal API doesn't always expose owner email. The robust path is: take the `rss_url` from each podcast, fetch it directly with `fetch()`, parse the XML, extract `<itunes:owner><itunes:email>`. This is the canonical podcast-contact field that all major directories index.
6. Optional secondary: Listennotes does sometimes embed an obfuscated email in the page DOM under a `data-email` attribute or a base64 blob — `discover/listennotes.mjs` tries this *first* (cheaper than RSS fetch), falls back to RSS.

### Seed variety

`config/seeds.yaml` has 100+ seeds across:
- Genres (Listennotes' top-level taxonomy: Business, Technology, Society, Health, Education, Comedy, etc.)
- Conversational-format keywords ("interview", "podcast roundtable", "longform conversation", "deep dive interview", "Q&A podcast")
- Popularity tiers (best-podcasts vs. mid-tail search results)
- Locale slices (en-US, en-GB, en-AU, en-CA, en-IN — all English to satisfy contract clause 3)

`seed-cursor.mjs` advances through them deterministically across runs so we don't keep hitting the same 10 seeds. Each cron run picks `--seeds N` (default 10) starting from the cursor, marks them visited, wraps around when exhausted, and re-shuffles every full cycle.

### Solo-podcast filter

The licensing agreement requires conversational dialogue. We score each candidate against keyword heuristics in title/description (`interview`, `with`, `host & guest`, `conversation`, `Q&A`, `roundtable`, `discussion`) and reject solo-monologue formats. Borderline cases pass — better to outreach + let the host self-disqualify than to filter too aggressively.

## Email template (subject + body)

Lives at `templates/initial-outreach.md`. Frontmatter declares the subject; body is plain text with three placeholders. Required: `{podcast_name}`. Optional with graceful fallback: `{host_first}` (defaults to "there") and `{recent_episode}` (omits the recent-episode hook line if absent).

The body mirrors Adithya's Lisa email word-for-word, with the `Pushing The Limits` reference parameterized as `{podcast_name}`. No deviation without Adithya's review — the template is the brand voice.

## Gmail labels

Two labels managed by this skill, both nested under `Podcast`:
- `Podcast - Archived` (every send lands here)
- `Podcast - Priority` (replies get promoted here)

Adithya's outbox conventions (per his global `archive-not-trash` agent-learning) — outreach mail is archived from inbox immediately on send, kept marked read, label-only navigation thereafter. Reply-promoted threads stay archived but are also marked unread per his `archive-unread-not-unarchive` rule.

The `labels.mjs` module ensures both labels exist on first run. If gog auth is broken, `ensure-labels` halts loudly with reauth instructions.

## Reply scan logic

Daily, `scan-replies`:
1. `gog gmail threads list -a adithya@eclipse.builders --query 'label:"Podcast - Archived" newer_than:14d'` → set of recent thread ids.
2. For each thread, `gog gmail threads get <tid> -j` → check if any message has `from != adithya@eclipse.builders` (i.e. an inbound reply).
3. If inbound reply found:
   - Remove `Podcast - Archived` label.
   - Add `Podcast - Priority` label.
   - Mark thread unread (per archive-unread agent-learning).
   - Append to `replies.jsonl`.
   - Send Adithya an `imessage` ping: `[podcast-outreach] reply from <podcast_name> (<email>): "<first 80 chars of reply>"`.
4. Idempotent — already-promoted threads are skipped via `replies.jsonl` cross-check.

## Caps + safety

- **Daily cap**: 2000 sends. Hard. Tracked in `~/.ultron/podcast-outreach/state/rate-state.json` (rolls over at local midnight).
- **Hourly throttle**: 200/hr with ±30s jitter between sends. The send loop sleeps `humanize.mjs jittered(18s)` per send (≈200/hr).
- **Halt file**: `~/.ultron/podcast-outreach/.halt`. Cron checks first; if present, exits 0 with a log line.
- **Bounce policy** (future): bounce notifications hitting the inbox should auto-mark the recipient address as bad and remove from queue. v1 stub-out — Adithya manually flags.
- **Address sanity**: regex-validate email format pre-send. Strip role-account aliases that almost never reply (`noreply@`, `do-not-reply@`, `info@`, `support@`) to reduce spam-flag risk; route them to a `low-quality.jsonl` for Adithya's review.

## Scheduling

Wired into the existing `schedule` skill via `workspaces/eclipse/config/schedule.yaml`:

```yaml
workspace_jobs:
  podcast-outreach:
    cron: "0 10 * * *"   # Daily at 10:00 local
```

`run-stage.sh` adds `podcast-outreach` to the helper-stage list (no `_shell/stages/podcast-outreach/CONTEXT.md` required) and dispatches to `node _shell/skills/podcast-outreach/scripts/cron-cycle.mjs`. The cron passes `--send` so the daily run is live; manual invocations stay dry-run.

```bash
# Compile + load:
gog auth login adithya@eclipse.builders   # if expired
~/.claude/skills/schedule/scripts/run.sh compile
~/.claude/skills/schedule/scripts/run.sh load com.adithya.ultron.podcast-outreach-eclipse
```

## Self-review (~150 tokens)

- Every send is preceded by a three-layer dedup check: sent.jsonl, gmail thread search `to:<email>`, label-existence on archived/priority.
- The hard 2000/day cap is enforced before the loop AND inside the loop (defense in depth) — a panicked daily-cycle that re-reads queue mid-loop can't double-fire.
- `--dry-run` is the default and skipping `--send` produces a render-only artifact at `~/.ultron/podcast-outreach/dry-run/<ts>/` for inspection.
- Pricing replies are NEVER auto-handled. The reply scanner promotes label + pings Adithya; that's it.
- Listennotes scrape uses an anonymous persistent profile + jittered scrolling — no auth, no fingerprint leaks.
- The skill is single-account, single-workspace by design. Adding more is a v2 conversation.

## Known limits / v2 roadmap

- No bounce-handler. Hard bounces accumulate on the wrong dedup line.
- No A/B template. Only the Lisa-template ships in v1.
- No automated rate-quote. Pricing replies always escalate to Adithya. (Sydney + Adithya may eventually authorize a "starting at $X/hr" auto-reply once they pick a public floor.)
- No Listennotes API fallback. Pure scrape. If Listennotes ships aggressive bot detection, we'll add the $180/mo API as fallback.
- No auto-followup. If a podcast doesn't reply in N days, no second outreach. (Considered, deferred — Adithya's reply rate metric is week-1.)
