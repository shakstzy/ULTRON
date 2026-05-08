---
name: linkedin
description: Read and write on Adithya's PERSONAL LinkedIn account — patchright-driven persistent Chrome profile + URL navigation + innerText extraction + structural href signals. Single user, single account, no paid APIs, no Voyager API. 13 verbs through one dispatcher (`scripts/run.mjs`) — login, status, diag, pull, get-profile, send-dm, send-connect, list-threads, list-invites, get-conversation, accept-invite, withdraw-invite, search-people. All write verbs default to dry-run; `--send` to execute. Ban-aversion is priority #1 (halt-file kill switch, daily/weekly caps, active-hours guard, pending-invite ceiling, rate-limit detection, modal close, auto-quarantine on hard signal, manual-only login, messy-human pacing). Trigger on phrases like "look up <name> on linkedin", "linkedin profile of <person>", "send <name> a connection request", "dm <name> on linkedin", "search linkedin for <query>", "what's in my linkedin inbox", "show pending linkedin invites", "withdraw the invite to <name>", "log in to linkedin". Burner-account use is safer; main-account use is at your own risk.
---

# linkedin (ULTRON)

Personal LinkedIn capability layer. One Node project under `_shell/skills/linkedin/`, one dispatcher (`scripts/run.mjs`), one persistent Chrome profile at `_credentials/browser-profiles/linkedin/`. Every verb does exactly one navigation; the page's `<main>` innerText is returned to Claude, which parses if it needs structure.

**Why not the LinkedIn MCP?** It injects 13 tool definitions into every Claude conversation context. We mine the proven patterns from [stickerdaniel/linkedin-mcp-server](https://github.com/stickerdaniel/linkedin-mcp-server); we do not run it in-process.

**Why not Voyager API?** LinkedIn drift-resists URL navigation + innerText, but rotates Voyager schemas. Structural href anchors (`/preload/custom-invite/`, `/messaging/compose/`, `/edit/intro/`) survive language changes and layout reshuffles.

## ToS note, read first

Programmatic use of a real account is against LinkedIn's ToS. Detection is low but nonzero. Mitigation: keep LinkedIn open in the normal client while the CLI runs, stay inside daily/weekly caps, and let the messy-human pacing do its job. Burner account recommended; main-account use is at your own risk.

## When this fires

Trigger phrases:
- **Read**: "look up <name> on linkedin", "fetch <person>'s linkedin", "linkedin profile of <X>", "search linkedin for <query>", "what's in my linkedin inbox", "show pending linkedin invites", "show my linkedin connection requests", "read <name>'s thread on linkedin".
- **Write**: "send <name> a linkedin connection request", "connect with <X> on linkedin", "dm <name> on linkedin", "message <X> on linkedin", "withdraw the invite to <name>", "accept <name>'s linkedin request".
- **Session/maintenance**: "log in to linkedin", "is the linkedin session alive", "linkedin status", "run linkedin diag".

Do NOT fire for:
- Sales Navigator / Recruiter surfaces. Out of scope.
- Posts, reactions, comments, newsletter, recommendations, endorsements. Out of scope.
- Cold-outreach campaigns, drip sequences, AI-drafted batch messages. v0 is primitives only.
- Any other social network (X, Instagram, Discord, etc.).

## Skill layout

```
_shell/skills/linkedin/
├── SKILL.md                    this file
├── package.json                patchright dep + chrome postinstall
├── config/caps.json            daily/weekly caps + pacing knobs
├── scripts/
│   └── run.mjs                 single dispatcher — every verb
├── src/
│   ├── linkedin/
│   │   ├── extractor.mjs       LinkedInExtractor class — every verb's navigation + parsing
│   │   ├── session.mjs         ensureLoggedIn (li_at fast-path, manual-login-only)
│   │   ├── page-actions.mjs    rate-limit detection, modal close, login state, scroll
│   │   ├── connection-state.mjs  structural-href state detection
│   │   └── ban-signals.mjs     wraps page-actions + quarantine handler
│   ├── runtime/
│   │   ├── paths.mjs           every state path
│   │   ├── profile.mjs         patchright launcher (paced, tab-hygiene)
│   │   ├── caps.mjs, halt.mjs, logger.mjs, ban-quarantine.mjs, notifier.mjs
│   │   ├── humanize.mjs, messy-human.mjs   anti-detection pacing
│   │   ├── entity-store.mjs    raw markdown writer (per-person, frontmatter-merge)
│   │   ├── identity.mjs, slug.mjs, exceptions.mjs
│   └── policy/
│       ├── rate-limits.mjs     gate(action) / record(action)
│       └── pending-budget.mjs  pending-invite ceiling enforcement
└── tests/                      identity + entity-store smoke tests (no live calls)
```

## ULTRON paths

| Item | Path |
|------|------|
| Skill home | `~/ULTRON/_shell/skills/linkedin/` |
| Persistent Chrome profile | `~/ULTRON/_credentials/browser-profiles/linkedin/` |
| State home | `~/.ultron/linkedin/` |
| Halt file (kill switch) | `~/.ultron/linkedin/.halt` |
| Daily counters | `~/.ultron/linkedin/state/rate-state.json` |
| Action audit log | `~/.ultron/linkedin/state/actions.ndjson` |
| Quarantined profiles | `~/.ultron/linkedin/quarantine/` |
| Ban-signal alerts | `~/.ultron/linkedin/alerts/` |
| Diag artifacts | `~/.ultron/linkedin/diag/<ts>/` |
| Raw markdown deposits | `~/ULTRON/workspaces/<ws>/raw/linkedin/<slug>-linkedin.md` (default ws: `network`) |
| Auto-promoted global stubs | `~/ULTRON/_global/entities/people/<slug>.md` (`entity_status: provisional` until promoted) |

## First-time setup (once)

```bash
cd ~/ULTRON/_shell/skills/linkedin
npm install                                # postinstall fetches chromium (~300MB)
node scripts/run.mjs login                 # headful Chrome, log in by hand
```

The login window handles 2FA, OTP, device verification, and comply gate manually. We never auto-fill credentials. After `/feed/` is reached, the persistent profile (cookies + fingerprint + history) survives across runs. Do NOT copy the profile dir to another machine — LinkedIn 2026 fingerprints hardware.

Re-run `login` only when a runtime verb reports `AUTH` / `CHECKPOINT`. Auto-relogin loops are the canonical ban trigger.

## Verbs

All verbs go through `node scripts/run.mjs <verb> [flags]`. Common flag `--workspace <ws>` (default `network`) controls where raw markdown writes land. Write verbs default to dry-run; pass `--send` to execute.

**Raw deposit format** follows the ULTRON workspace ingest standard (source / workspace / ingested_at / ingest_version / content_hash / provider_modified_at) plus LinkedIn-specific fields (linkedin_public_id, linkedin_url, linkedin_urn, connection_status) plus an `entity:` wikilink up to `_global/entities/people/<slug>.md` for graphify route-resolution. Body has `## Profile snapshot` (overwritten on re-pull) and append-only `## Threads` (dedup'd on day+direction+text).

**Auto-promote.** `get-profile` creates a thin `_global/entities/people/<slug>.md` stub on first fetch, tagged `entity_status: provisional`. Idempotent — if contacts-sync already wrote a stub at that slug we leave it alone. Pass `--no-promote` to skip auto-creation when researching one-offs you don't want polluting the network graph. Promote provisional stubs to first-class with `/promote-entity`.

**Redirect-honor.** Before writing a raw deposit, the upsert reads the target's frontmatter; if `redirect_to:` is set (left by `/alias` after a slug merge), the write resolves to canonical. This is what makes alias durable — future LinkedIn pulls don't re-create the duplicate.

| Verb | Usage | Gate | Output |
|------|-------|------|--------|
| `login` | `run.mjs login` | none | interactive — establishes / refreshes profile |
| `status` | `run.mjs status [--json]` | none | halt + budgets + recent actions, local files only |
| `diag` | `run.mjs diag [--url <u>]` | none | screenshot + page-text + selector survey under `~/.ultron/linkedin/diag/<ts>/` |
| `pull` | `run.mjs pull [--thread-limit N]` | per-action | inbox + each thread + invites; upserts thread snapshots |
| `get-profile` | `run.mjs get-profile --profile <id_or_url> [--no-write] [--json]` | `get_profile` | upserts `<slug>-linkedin.md`; `--no-write` for stdout-only |
| `send-dm` | `run.mjs send-dm --profile <id> --text "..." [--send] [--to-connection] [--profile-urn <urn>]` | `send_dm_to_connection` or `send_dm_to_non_connection` | composes via `/messaging/compose/?profileUrn=...&recipient=...&screenContext=NON_SELF_PROFILE_VIEW` |
| `send-connect` | `run.mjs send-connect --profile <id> [--note "..."] [--send] [--skip-ceiling]` | `send_connect` + pending-ceiling | uses `/preload/custom-invite/?vanityName=` deeplink; pending-ceiling check fails closed |
| `list-threads` | `run.mjs list-threads [--limit N=20] [--json]` | none | inbox listing + thread IDs |
| `list-invites` | `run.mjs list-invites [--direction sent\|received] [--json]` | none | invitation manager listing |
| `get-conversation` | `run.mjs get-conversation (--thread <id> \| --profile <username>) [--json]` | none | one conversation thread |
| `accept-invite` | `run.mjs accept-invite --profile <id> [--send]` | `accept_invite` | detects `incoming_request` state, clicks inline Accept |
| `withdraw-invite` | `run.mjs withdraw-invite --profile <id> [--send]` | `withdraw_invite` | navigates `/mynetwork/invitation-manager/sent/`, matches row, withdraws |
| `search-people` | `run.mjs search-people --query "..." [--location "..."] [--json]` | `search_people` | people search; returns profiles + raw text |

## Ban-aversion stack (priority #1)

Layered. Any single one can short-circuit a run.

1. **Halt file.** `~/.ultron/linkedin/.halt` exists → every entrypoint exits early. Cleared only after manual investigation.
2. **Volume caps** in `config/caps.json` (Premium tier defaults). Daily: 30 connects, 50 DM-to-connection, 200 DM-non-connection, 200 profile fetches, 30 searches, 40 invite-accepts, 50 invite-withdraws. Weekly: 100 connects. Counters persist in `~/.ultron/linkedin/state/rate-state.json`. Bypass active-hours for one-shot CLI: `ULTRON_LINKEDIN_SKIP_ACTIVE_HOURS=1`.
3. **Active-hours guard.** 09:00–19:00 CST, weekdays only by default. Edit `config/caps.json` to change.
4. **Pending-invite ceiling.** Before any `send_connect`, count outstanding sent invites at `/mynetwork/invitation-manager/sent/`. If above 400 (Premium hard ceiling at 700), force-withdraw oldest 25 first. Fails closed if the count can't be read.
5. **Rate-limit detection** before AND after every navigation. Trips on `/checkpoint/`, `/authwall/`, or rate-limit phrases on error-shaped pages.
6. **Modal close** after every navigation.
7. **Auto-quarantine on hard ban signal.** `BanSignalError` → `_credentials/browser-profiles/linkedin/` is renamed into `~/.ultron/linkedin/quarantine/profile-<ts>-<signal>/`, halt is tripped, alert markdown is dropped under `~/.ultron/linkedin/alerts/`. Recovery: log in manually via real Chrome, confirm the account is healthy, then `run.mjs login` for a fresh profile.
8. **No programmatic re-login.** Only manual via `run.mjs login`. Auto-relogin loops are the textbook ban trigger.
9. **Messy-human pacing.** Sprinkles micro-fidget / scroll / dwell between actions. 5% chance of an 8–18 minute distraction per inter-action gap. Every 8 actions, a 45–65 minute cooldown with feed-browse.

## Self-heal protocol (selector drift)

When a verb breaks: do NOT ask the operator. Run `run.mjs diag --url <relevant-page>`, read `~/.ultron/linkedin/diag/<ts>/selector-survey.json` (every key is a selector we depend on with a sample of the matched outerHTML), patch `src/linkedin/extractor.mjs` (structural anchors) or `src/linkedin/connection-state.mjs` (action-area heuristics) — those are the only selector-bearing files. Re-run the failing verb, confirm a real artifact (e.g. for `get-profile`, the markdown file has a non-empty `name:` and `## Profile snapshot` > 200 chars). Send the patch to `codex exec` for one-round review, apply P0/P1.

## Tests

```bash
npm test    # identity + entity-store smoke (no live LinkedIn calls)
```

## Scheduling

To run `pull` daily, declare it in `workspaces/<ws>/config/schedule.yaml` and use the `schedule` skill (`compile` → `load`). Never write launchd plists by hand. Suggested cadence: 10:30 CST, weekdays only, `--thread-limit 10`.

## Out of scope (v0)

Sales Navigator / Recruiter, posts/reactions/comments/recommendations/endorsements, AI-drafted batch outreach, scheduled drip sequences, multi-account, company employee scrapes, job search. Port from the MCP if needed in a later version.

## Known risks (v1 work)

- TLS/JA4 fingerprint hardening — flagged CRITICAL in 2026-04-30 review, not yet landed. Mitigate via persistent-profile age + low volume until verified.
- BrowserGate extension probing — flagged IMPORTANT. v1: install 2–3 noise extensions in the persistent profile.

## Troubleshooting

| Problem | Action |
|---------|--------|
| `AUTH` or `CHECKPOINT` at runtime | Run `run.mjs login`; complete 2FA / device check by hand |
| `HALTED` | Read `~/.ultron/linkedin/.halt`; review the alert under `~/.ultron/linkedin/alerts/`; only clear after the underlying cause is understood |
| `RATE_LIMIT scope=daily/weekly` | Counter cap reached; wait for next day/week or edit `config/caps.json` |
| `RATE_LIMIT scope=active_hours` | Outside the configured window; pass `ULTRON_LINKEDIN_SKIP_ACTIVE_HOURS=1` for one-off dev |
| `RATE_LIMIT scope=pending_ceiling` | >400 outstanding invites; let the auto-withdraw batch run, or `--skip-ceiling` for dev only |
| `BAN_SIGNAL` | Profile auto-quarantined, halt tripped, alert dropped. Investigate before clearing. |
| Selector survey shows count: 0 for a depended-on selector | Patch `extractor.mjs` / `connection-state.mjs` per the self-heal protocol |
| `BROWSER_UNRESPONSIVE` | Patchright/Chromium hung; kill and retry. If it persists, `npm install` to refetch chromium. |
