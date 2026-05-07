---
name: telegram
description: Read and send messages on Adithya's Telegram account — DMs, group DMs, and channels. Telethon (MTProto) user-level client, NOT a bot. Auth is api_id + api_hash + one-time phone+code; session persists at ~/ULTRON/_credentials/telegram.session. Verbs - login (interactive, one-time), whoami, chats (list/search), read (last N messages from a chat), send (DM by name or chat id), status (session + breaker state), reset-breaker. Ingest verb is intentionally not in v1 - workspace ingest will be added when Adithya scopes it. Trigger phrases - "send <name> a telegram", "telegram <name>: <text>", "what's on my telegram", "read my telegram dm with <name>", "list my telegram chats", "telegram whoami", "log in to telegram".
---

# Telegram (ULTRON)

Telethon-based MTProto user client for Adithya's PERSONAL Telegram account. NOT a bot — bots cannot read your DMs or post AS you. This skill talks directly to Telegram's official MTProto API, which is the same surface telegram-desktop uses.

Lives at `~/ULTRON/_shell/skills/telegram/`. Consumed via the global symlink `~/.claude/skills/telegram/`.

## Why Telethon (not Discord-style browser automation)

Telegram publishes the MTProto user API officially — see https://core.telegram.org/api. Programmatic user-account access is sanctioned and rate-limited identically to the official desktop client. No selfbot ToS gray zone (unlike Discord), no need for patchright/Chrome, no token capture games. Telethon 1.x is the most active Python MTProto client (already installed at v1.43.2 on this machine).

`tdl` (the Go CLI, already at `~/.local/bin/tdl`) is kept as an option for bulk media downloads later. Not used in v1.

## When this fires

Trigger phrases:
- **Send**: "send <name> a telegram", "telegram <name>: <text>", "dm <name> on telegram", "message <name> on telegram".
- **Read**: "read my telegram dm with <name>", "what did <name> send me on telegram", "show last N messages from <name> on telegram".
- **List**: "list my telegram chats", "what telegram groups am I in".
- **State**: "telegram whoami", "is telegram logged in", "log in to telegram".

Do NOT fire for:
- Running a Telegram BOT (bot tokens, slash commands, `/setcommands`). Different auth, different semantics. Use `python-telegram-bot` for that, separate skill.
- Telegram CHANNELS where Adithya is not a member.
- Posting to a Telegram channel as a centralized brand bot — that goes through Zernio if/when wired up.
- Other comms services (Slack, iMessage, Discord) — separate skills.

## Skill layout

```
_shell/skills/telegram/
├── SKILL.md                  this file
├── scripts/
│   ├── run.py                dispatcher (login / whoami / chats / read / send / status / reset-breaker)
│   ├── session.py            TelegramSession context manager + breaker
│   └── login.py              one-time interactive phone+code auth
```

## Layout

| Item | Path / Value |
|------|--------------|
| Skill home | `~/ULTRON/_shell/skills/telegram/` |
| Global symlink | `~/.claude/skills/telegram` -> skill home |
| Credentials | `~/ULTRON/_credentials/telegram.json` (api_id, api_hash, phone — chmod 600, gitignored) |
| Session file | `~/ULTRON/_credentials/telegram.session` (Telethon SQLite — chmod 600, gitignored) |
| Breaker file | `~/ULTRON/_credentials/.telegram-breaker.json` |
| Breaker trip | Two consecutive `AuthKeyError` / 401-equivalent failures, or `FloodWaitError` > 600s |
| Breaker cooldown | 24h; `reset-breaker` to clear manually |
| Auth probe | `client.get_me()` returns a User object |

## First-time setup (once)

1. Get API credentials:
   - Visit https://my.telegram.org, log in with your phone.
   - Click **API development tools** → create a new application (any name + short name; platform "Other").
   - Copy `api_id` (a number) and `api_hash` (32-char hex).
2. Adithya provides those values to Claude in chat.
3. Claude writes them to `~/ULTRON/_credentials/telegram.json` (chmod 600).
4. Claude runs `python3 scripts/run.py login`. Telethon prompts for phone, you confirm. Telegram pushes a 5-digit code (in your Telegram app — NOT SMS — if your account already exists). You paste the code back. Done.

After that, every verb reuses `telegram.session`. Re-run `login` only if a verb returns `AuthKeyError`.

## Verbs

| Verb | Usage | What it does |
|------|-------|--------------|
| `login` | `python3 scripts/run.py login` | Interactive phone+code auth. Writes session. |
| `whoami` | `python3 scripts/run.py whoami` | `get_me()`, prints id + name + phone + username. |
| `chats` | `python3 scripts/run.py chats [--query <substr>] [--limit N] [--kind dm\|group\|channel\|all]` | List dialogs (most-recent first). |
| `read` | `python3 scripts/run.py read <chat> [--limit N]` | Last N messages from a chat (default 20). `<chat>` = name substring, @username, or numeric chat id. |
| `send` | `python3 scripts/run.py send <chat> <text...>` | Send a text message. `<chat>` resolved like `read`. Single-match required; otherwise lists candidates and exits non-zero. |
| `status` | `python3 scripts/run.py status` | Credentials + session + breaker state. |
| `reset-breaker` | `python3 scripts/run.py reset-breaker` | Clear 24h halt after manual investigation. |

## Output shape (for Claude consumers)

All verbs print human-readable text by default. Add `--json` for structured output (Claude consumers should prefer this).

`read` JSON shape:
```json
{
  "chat": {"id": 123, "kind": "dm|group|channel", "title": "..."},
  "messages": [
    {"id": 456, "ts": "2026-05-07T18:30:00Z", "from": {"id": 789, "name": "...", "is_me": false}, "text": "...", "reply_to_id": null, "media_kind": null}
  ]
}
```

## Pacing

- One client per verb invocation; connect → call → disconnect cleanly.
- Telethon handles `FloodWaitError` automatically with sleep ≤ 60s; longer flood waits raise and trip the breaker.
- No parallel chat reads inside a single verb. Serial only.

## Security notes

- `api_id` and `api_hash` are app-level credentials. Leaking them lets someone impersonate the *application*, not your account — but combined with a stolen session file it's full account takeover. Both files chmod 600 and gitignored.
- Session file is account-equivalent. Treat like a password.
- Rotation: Telegram → Settings → Devices → terminate all other sessions, then re-run `login`.
- Never log api_hash, session bytes, or 2FA password to stdout/stderr.

## Known limitations (v1)

- Text send only. Media send (`--file <path>`) not implemented; add when needed.
- No ingest/history pull verb. Workspace ingest will land in a follow-up scoped by Adithya.
- No live event listener. Polling/event consumers are out of scope for v1.
- No 2FA password support beyond Telethon's interactive prompt (if you have a cloud password set, the login flow will ask for it once).

## Troubleshooting

| Problem | Action |
|---------|--------|
| `AuthKeyError` / `SessionPasswordNeededError` | Run `login` again. |
| `PhoneCodeInvalidError` | Code typo or expired (5-min TTL). Re-run `login`, request a fresh code. |
| `FloodWaitError: wait N seconds` | Telethon auto-handles ≤ 60s. Longer = back off, breaker trips. |
| `Chat not found` | `<chat>` matched zero or multiple dialogs. Use `chats --query <substr>` to find the right id, then pass numeric id. |
| `BREAKER_HALTED` | Run `status`, investigate why, then `reset-breaker`. |
