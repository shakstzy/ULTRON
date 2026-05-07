---
name: discord
description: Read, ingest, and send messages on Adithya's Discord account — patchright-driven Chrome session against discord.com/api/v9, authenticated by session cookies in a persistent profile dir, never bot tokens. Personal DMs work here where bot tokens cannot. Three primary capabilities — (1) ingest a friend's full DM history into ULTRON workspace folders as monthly markdown shards mirroring the imessage individual format with Gemini Flash image descriptions via cloud-llm; (2) send a DM by friend name or user ID; (3) read session state (whoami, friends list, breaker status). Trigger on phrases like "ingest <name> from discord", "pull <name>'s discord into <workspace>", "dm <name> on discord", "send <name> a discord message", "message <name> on discord", "log in to discord", "is the discord session alive", "who's on my discord friends list". Burner account recommended; main-account use is at your own risk.
---

# Discord (ULTRON)

Discord REST primitives + workspace ingest pipeline for Adithya's PERSONAL account. Thin wrapper over `https://discord.com/api/v9/*` where every call runs inside a real Chrome session opened by patchright. Authentication is session cookies in a persistent profile dir; the Authorization header is captured live from Discord's own client (CDP `Network.requestWillBeSent`) and replayed inside the same page context.

Deliberately NOT using a Discord MCP. Every public DM-reading Discord MCP is user-token or browser-session based (same ToS surface) AND adds a persistent tool surface loaded into every session for a skill that is rarely invoked. A single-folder Node script driving one Chrome profile is strictly less bloat.

Deliberately NOT using a bot token. Bots cannot read your own DMs, cannot search your history, and post AS the bot instead of AS you. Bot tokens solve a different problem.

Deliberately NOT using raw `node fetch` against discord.com. REST traffic with Node's TLS fingerprint and no matching browser Client Hints is the strongest possible selfbot signature. Running every call through a real Chrome page on discord.com gives real TLS/JA3, real Client Hints, real origin, and reuses Discord's own captured Authorization header.

## ToS note, read first

Using your real account against the REST API programmatically is self-botting. Discord's policy at https://support.discord.com/hc/en-us/articles/115002192352 explicitly forbids automating a normal user account. Detection is low but nonzero. Mitigation: keep Discord open in your normal client while the CLI runs (real gateway WebSocket presence is the cheapest camouflage). Burner account recommended; main-account use is at your own risk.

## When this fires

Trigger phrases:
- **Ingest**: "ingest <name> from discord", "pull <name>'s discord into <workspace>", "import <name>'s discord messages".
- **Send**: "dm <name> on discord", "send <name> a discord message", "message <name> on discord", "discord <name>: <text>".
- **Read state**: "log in to discord", "is the discord session alive", "who's on my discord friends list", "discord whoami".

Do NOT fire for:
- Running a Discord bot or app (events, slash commands, modals, activities). Different auth, different semantics.
- Server moderation (kick, ban, role management).
- Posting to a Discord SERVER channel as a centralized bot. That goes through whatever Zernio/Eclipse server-bot skill handles authorized server channels. This skill is explicitly Adithya's PERSONAL account (DMs, group DMs, channels Adithya is a member of, posting as Adithya). If the user phrasing is ambiguous (just "post on discord" with no other signal), ASK whether they want a server bot or their personal account.
- Non-Discord services (Slack, iMessage, Telegram).

## Skill layout

```
_shell/skills/discord/
├── SKILL.md                  this file
├── package.json              patchright dep + chrome postinstall
├── scripts/
│   ├── run.mjs               dispatcher (login / whoami / friends / status / reset-breaker / ingest / dm)
│   ├── session.mjs           DiscordSession class + openSession/listFriends/listDmRecipients/resolveUser/openDmChannel
│   ├── ingest.mjs            per-friend full-history pull + per-month .md writer (skip-write when content_hash unchanged)
│   ├── browser.mjs           patchright launcher, CDP token capture, breaker
│   ├── login.mjs             one-time visible browser login flow
│   └── describe-image.py     cloud-llm wrapper, called per image by ingest.mjs
```

## QUANTUM integration

| Item | Path / Value |
|------|--------------|
| Skill home | `_shell/skills/discord/` |
| Profile dir | `~/ULTRON/_credentials/browser-profiles/discord/` (gitignored under `_credentials`) |
| Pidfile | `<profile>/.skill.pid` |
| Breaker file | `<profile>/.breaker.json` |
| Breaker trip | Two consecutive 401/403s at runtime, or any captcha DOM during login |
| Breaker cooldown | 24h; `--force` to override, `reset-breaker` to clear manually |
| Auth probe | Successful GET `/users/@me` with captured token |

## First-time setup (once)

```bash
cd ~/ULTRON/_shell/skills/discord
node scripts/run.mjs login
```

The first invocation runs `npm install` to fetch patchright + Chrome (~300MB, 2-3 minutes). After that, opens a visible Chrome window pointed at discord.com. Log in (email + password + 2FA or QR code). The script waits for a successful authenticated API call from Discord's own client, captures the Authorization header into the page, confirms the session via `/users/@me`, and closes.

Future runs are silent; cookies in the profile dir authenticate every navigation and the page-side hook re-captures the header from the first real Discord client request.

Re-run `login` when a runtime verb reports a 401.

## Verbs

| Verb | Usage | What it does |
|------|-------|--------------|
| `login` | `node scripts/run.mjs login [--force]` | One-time visible browser login. Cookies persist to profile dir. |
| `whoami` | `node scripts/run.mjs whoami` | GET `/users/@me`, confirm session |
| `friends` | `node scripts/run.mjs friends [query]` | List friends, optional name filter |
| `status` | `node scripts/run.mjs status` | Profile + cookies + breaker + pidfile state |
| `reset-breaker` | `node scripts/run.mjs reset-breaker` | Reset 24h halt after manual intervention |
| `ingest` | `node scripts/run.mjs ingest <name\|id> --workspace <ws> [options]` | Pull entire DM history with a friend; write per-month `.md` |
| `dm` | `node scripts/run.mjs dm <name\|id> <text...>` | Send a DM (resolves through friends list, then open DMs) |

Discord REST is the authoritative surface for edge cases. Do not re-document endpoints here: `https://discord.com/developers/docs/reference` is the source of truth.

## Ingest pipeline (`ingest.mjs`)

For a given friend (resolved by name from your friends list, or numeric snowflake ID), pulls every message in the 1:1 DM channel with them, oldest to newest, paginating via `before=<id>` until empty.

**Filter rules** (cheap, deterministic — no LLM):
- Drop `author.bot`.
- Drop `type !== 0 && type !== 19` (system messages: calls, joins, pins, etc).
- Drop messages with no content AND no attachment.

**No emoji or reaction surface.** Reactions live on a separate field (`reactions`); they are not rendered. Emojis embedded in message text are kept verbatim — the only "filter" is the deterministic rules above.

**Output path:**
`workspaces/<ws>/raw/discord/individuals/<friend-slug>/<year>/<YYYY-MM>__<friend-slug>.md`

The slug is filesystem-safe (lowercase alphanum + `._-`, ≤ 60 chars), derived from `global_name || username`.

**Frontmatter (mirrors imessage individual files):**
```yaml
source: discord
workspace: <ws>
ingested_at: <ISO 8601 UTC>
ingest_version: 1
content_hash: sha256:<hex>
provider_modified_at: <ISO of newest message in this month>
contact_slug: <friend-slug>
contact_type: individual
month: <YYYY-MM>
date_range: [<first-date>, <last-date>]   # America/Chicago
message_count: <int>
my_message_count: <int>
their_message_count: <int>
attachments:
  - message_id: <snowflake>
    kind: image|video|audio|file
    filename: <str>
    url: <discord cdn url>
    size: <bytes or null>
    description: <gemini-flash one-liner, only for images; null otherwise>
discord_channel_id: <snowflake>
discord_channel_kind: dm
discord_recipient_id: <snowflake>
discord_recipient_username: <str>
discord_recipient_global_name: <str>
deleted_upstream: null
superseded_by: null
```

**Body shape (deterministic, recreate-able from data):**
```markdown
# <Recipient> — <Month YYYY>

## YYYY-MM-DD (Weekday)

**HH:MM — me:** message text
**HH:MM — Recipient (edited):** ↳ replying to me ("snippet of original ≤80 chars"): reply text
**HH:MM — me:** message with image
↳ image: photo.jpg (123 KB) — "<gemini-flash description>" — https://cdn.discordapp.com/...
↳ video: clip.mp4 (4.2 MB) — https://cdn.discordapp.com/...
```

- Times are `America/Chicago` (CST/CDT), 24h.
- Day boundaries are `America/Chicago`.
- `(edited)` suffix appears when `edited_timestamp` is set.
- Reply prefix uses `referenced_message` from the API; if the parent was deleted, renders `↳ replying to (deleted): `.
- Images get a one-sentence factual description via cloud-llm (Gemini Flash for vision). If cloud-llm is unreachable the image still renders, just without `— "<description>"`.
- Non-image attachments (videos, voice memos, gifs, files): URL + filename + size only. We never download the actual file.

**Watermark / diagnostic:** `workspaces/<ws>/raw/.ingest-log/discord/<friend-slug>.json` records the last full pull (newest_message_id, oldest_message_id, counts). v1 is full re-pull on every run; idempotent file writes make this safe.

## Ingest options

| Flag | Effect |
|------|--------|
| `--workspace <ws>` | required; target workspace under `workspaces/` |
| `--dry-run` | render to stdout (preview only), write nothing |
| `--no-describe` | skip cloud-llm image descriptions (faster) |
| `--max-pages N` | cap pagination pages (debug; default unlimited) |

## Pacing (detection-conscious)

- One Chrome session for the whole pull (NOT one launch per channel).
- Within a channel, paginated requests jitter 1.5–4s apart.
- Honors `Retry-After` on 429. Two consecutive 401s halt and trip the breaker.

## Audit (Pattern 12)

| Check | Pass condition |
|-------|----------------|
| Session valid | `whoami` returns 200 and your user id |
| Target unambiguous | Friend name resolved to exactly one user id |
| Filtered correctly | No bot/system/empty messages in output |
| Body preserved | Code fences and newlines survive round-trip |
| Image descriptions | All `kind: image` entries either have a `description:` or null with cloud-llm error |
| No token leak | Authorization header never printed to stdout, stderr, or logs |
| Rate-limit respected | On 429, script slept per `Retry-After` then retried |

## Detection risk and mitigation

- Keep Discord open in your normal desktop client while the CLI runs. Real gateway WebSocket presence is the cheapest camouflage; a REST-only account is the obvious selfbot signature.
- All API calls execute inside a real Chrome session, so TLS fingerprint, Client Hints, and Origin are real.
- Requests go serial, not parallel.
- Circuit breaker halts 24h on two consecutive 401/403s.

## Security notes

- Session cookies are equivalent to the password. Profile dir is `chmod 700` and lives under `_credentials/` (gitignored).
- Authorization header captured at runtime is held in memory only; never written to disk or env.
- Rotation: log out of all devices in Discord settings, then re-run `login`.
- If an Authorization value ever appears in chat, logs, or a commit, log out everywhere from Discord settings immediately.

## Known limitations (v1)

- DMs only. No guild/server channel ingest. No group DMs.
- Read + ingest only. No `dm`, `send`, `read`, or `search` verbs in v1 (port from QUANTUM if needed).
- v1 is full re-pull each ingest run; no incremental `--resume`. Idempotent file writes make this safe but slower than incremental.
- No edit-tracking on past messages. We pull current state; if a message was edited after a prior pull, the next pull picks up the new content.
- No deletion tracking. If a message was deleted upstream after our last pull, our shard still has it.
- Single profile. Burner: pass `DISCORD_PROFILE_DIR=~/ULTRON/_credentials/browser-profiles/discord-burner` and run `login` again.
- Cron: out of scope for v1. To schedule, use the `schedule` skill once the manual ingest is dialed in.

## Troubleshooting

| Problem | Action |
|---------|--------|
| `Session expired or never logged in` | Run `node scripts/run.mjs login` |
| 401 at runtime | Token invalidated; re-run `login` |
| 429 on every call | You're hammering. Serial only. Wait one minute. |
| `Profile locked by pid N` | Another login is in flight. Wait or kill pid. |
| Captcha in DOM during login | Complete captcha in the visible browser. If persistent, breaker halts 24h. |
| Friend not found | User isn't in your friends list. Pass a user ID directly. |
| `BREAKER_HALTED` | Run `reset-breaker` only after you understand why it tripped. |
| All image descriptions null | Gemini accounts exhausted or `gemini` CLI not on PATH. Re-run with `--no-describe` and backfill descriptions later. |
