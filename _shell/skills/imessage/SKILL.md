---
name: imessage
description: Send an iMessage (or SMS/RCS via existing chat) from inside ULTRON. Uses Messages.app via AppleScript — no ObjC, no IDS lookup, no SQLite. Use for bot halt notifications, low-volume operator pings, any script that needs to text Adithya, AND any time Adithya asks Claude to text someone ("text mom", "send X to Y") — see Recipient resolution. For contact CRUD use `contacts-add` / `contacts-sync`.
---

# imessage

Slim ULTRON-native iMessage send. Lives at `~/ULTRON/_shell/skills/imessage/`. Consumed via the global symlink `~/.claude/skills/imessage/`.

## Why this exists

ULTRON's bots need to ping Adithya from cron when something halts (Bumble Turnstile, selector drift, cap exhausted). MCP tools can't run from cron — they need Claude in the loop. This skill is a 60-line bash + AppleScript send that any Python or Node consumer can shell out to.

This is also the entry point when Adithya asks Claude to text a third party ("text mom this", "send this to Sydney"). Recipient resolution is mandatory — see next section.

For contact add/lookup use `contacts-add` (write) and `contacts-sync` (read) — they cover the contact side cleanly.

## Recipient resolution (REQUIRED when sending on Adithya's behalf to a named person)

NEVER ask Adithya for a phone number or email. Resolve mechanically. ONLY surface a question when resolution is genuinely ambiguous — clean single-match resolution sends without asking.

**Resolution order:**

1. **Apple Contacts is ground truth.** Query Contacts.app via `osascript`:
   ```bash
   osascript -e 'tell application "Contacts" to get the name of every person whose name contains "<term>"'
   ```
   Then for the matching name, pull phones:
   ```bash
   osascript <<'EOF'
   tell application "Contacts"
     repeat with p in (every person whose name is "<exact name>")
       repeat with ph in phones of p
         log (value of ph as string)
       end repeat
     end repeat
   end tell
   EOF
   ```
2. **Cross-check the entity stub** at `_global/entities/people/<slug>.md`. Stubs can be mislabeled — e.g. `aartis-mom.md` is "Aarti's mom" (a third party), NOT Adithya's mom (whose contact is named just "Mom"). If the stub disagrees with Apple Contacts, trust Contacts and surface the mismatch so Adithya can fix the stub.
3. **Disambiguate relationships by exact contact name.** "My mom" = the contact literally named `Mom`. "My dad" = `Dad`. Names like `<X> Mom` / `<X> Dad` almost always mean "X's parent" (a third party), not Adithya's parent.

**When to ask Adithya** (and only these cases):

- **Multiple candidates with the same name** — list them (name + number + emails) and ask which.
- **Fuzzy / partial match with several hits** — e.g. "send to alex" matches three Alexes, ask which.
- **Apple Contacts and the entity stub disagree** on the canonical handle — surface both, ask which to trust.
- **No matches anywhere** — say so, ask for the right name or handle.

**When NOT to ask:**

- Single confident match across sources → just send. Do not echo "→ resolved to X, confirm?" for unambiguous lookups.
- Adithya already specified the recipient unambiguously (e.g. "text Mom" → contact literally named "Mom").
- Adithya already specified the message body → NEVER re-confirm the body. Auto-send.

**One-time disambiguation = stable resolution.** When Adithya tells you how to resolve ("the alex from austin"), confirm once if needed, then fire and don't re-ask in the session. Save the disambiguation as a memory if it'll recur.

**Stub bug?** Note it in the reply so Adithya can fix `_global/entities/people/<slug>.md` or the `contacts-sync` skill — don't silently route around it.

## Voice fidelity — three-source context before drafting

Before composing ANY iMessage body to a third party, assemble these into your scratch context:

1. **Voice profile** — read `_global/entities/people/<entity-slug>.md` frontmatter. If `voice_profile:` is present, that's the canonical "how Adithya talks to this person" digest (tone register, vocabulary, abbreviations, emoji habits, message length). Use it as the dominant style anchor.
2. **Conversation summary** — same stub, `conversation_summary:` field. Recent topics, ongoing threads, inside references. Pull this so the message lands in current context, not in a vacuum.
3. **Recent message tail** — read the last shard at `workspaces/personal/raw/imessage/individuals/<imsg-slug>/<latest-year>/<latest-month>__<imsg-slug>.md` (or `groups/...` for group chats) to anchor on the most recent ~50 messages. The imessage profile slug is in `_profiles/<imsg-slug>.md` matched by phone/email — usually `<entity-slug>` or `<entity-slug>-2`.

If `voice_profile:` is missing on the stub, run `python3 ~/ULTRON/_shell/bin/synthesize-voice-profiles.py --slug <entity-slug> --force` once to populate it, then proceed. The weekly cron (Sun 04:00) refreshes stale stubs automatically; the on-demand call covers cold contacts.

Compose the draft IN that voice. If the voice profile says "no punctuation, abbreviations, sub-5-word messages," obey that — do not write paragraphs.

## ALWAYS humanize the body before sending

After composing the in-voice draft, run it through the **humanizer** skill (`~/ULTRON/_shell/skills/humanizer/`, symlink to the global). Adithya does not want AI tells going out under his name — em-dashes, rule-of-three, inflated symbolism, "I came across some questions that meant a lot to me," etc.

Flow:
1. Compose draft using the three-source context above (voice profile + summary + recent tail).
2. Invoke the humanizer skill on the draft.
3. Write the humanized result to a temp file, then `send.sh --text-file /tmp/draft.txt`. Use `--text-file` (not `--text "..."`) for any draft you didn't write byte-for-byte yourself — avoids shell-quoting bugs with backticks, `$`, and newlines.

For halt-notification sends from cron bots to Adithya himself, skip both voice-context and humanizer (those are explicitly machine-flavored).

## ALWAYS use `send.sh` — NEVER the MCP iMessage tool

The MCP tool `mcp__Read_and_Send_iMessages__send_imessage` forces the iMessage service even when the recipient is SMS-only. It returns "sent successfully" but the message lands as red "Not Delivered" in Messages.app. **Do not use it.**

Use `~/ULTRON/_shell/skills/imessage/send.sh` instead. It tries the existing 1:1 chat first (preserves whatever service Messages.app already chose — iMessage / SMS / RCS), falling back to iMessage buddy only if no chat exists. This is the only path that handles SMS-only recipients correctly.

```bash
~/ULTRON/_shell/skills/imessage/send.sh --to +15104499964 --text "..."
```

If `send.sh` returns `{"handoff":"error",...}`, surface the error to Adithya — don't silently retry through the MCP tool.

## Send strategy

1. **Existing 1:1 chat first.** If Messages.app already has a 1:1 chat with the recipient, send through it. This preserves whatever service binding Messages already chose (iMessage / SMS / RCS).
2. **iMessage buddy fallback.** If no chat exists, send via `1st service whose service type = iMessage`. First-time SMS / RCS recipients are NOT supported via this path — Messages.app must already have routed at least once.

This is intentionally simpler than QUANTUM's `macos-contacts-imessage` skill (which compiles an ObjC IDS-query helper and consults Apple's private framework). For ULTRON's halt-notification use case, the chat-history fallback is sufficient and avoids the build step.

## CLI

```bash
# 1:1
~/ULTRON/_shell/skills/imessage/send.sh --to +15125551234 --text "halt: turnstile detected"
~/ULTRON/_shell/skills/imessage/send.sh --to friend@icloud.com --text "ping"
~/ULTRON/_shell/skills/imessage/send.sh --to +15125551234 --file /abs/path/to/screenshot.png

# Group, by exact name (existing only — named groups in Messages.app)
~/ULTRON/_shell/skills/imessage/send.sh --group "ATX BABY🤙" --text "what's the move tonight"

# Group, by participant set — FIND-OR-CREATE. Same flag for both. Idempotent.
~/ULTRON/_shell/skills/imessage/send.sh --new-group "+15125551234,+15129998877" --text "..."
~/ULTRON/_shell/skills/imessage/send.sh --to "+15125551234,+15129998877" --text "..."   # alias for --new-group
```

Emits JSON on stdout: `{"handoff":"ok","path":"chat"|"buddy"|"group-by-name"|"group-existing"|"group-created"}`. Exit 0 = handoff accepted. Delivery is verifiable only in Messages.app UI; this script does not claim delivery.

## Group chat support — find-or-create semantics

**One canonical chat per participant set.** `--new-group` (and the `--to "h1,h2,..."` alias) first scans for an existing chat with EXACTLY this participant set across any service binding (iMessage / RCS / SMS). If one exists, the message routes through it. Only if no match exists does the script create a new chat via the `imessage:?addresses=...&body=...` URL scheme. This prevents Messages.app from spawning duplicate iMessage / RCS / SMS variants when the participant set is already known.

**Service binding for groups:** AppleScript `send X to chat` preserves the chat's existing service binding, so mixed iMessage+Android groups (RCS or SMS) route correctly without the caller knowing which.

**New-group creation caveats** (only fires when no existing match):
- Requires **Accessibility** permission for the parent process (System Settings → Privacy & Security → Accessibility).
- The single Return keystroke goes to the frontmost app — script `activate`s Messages, but a focus-stealing app racing for foreground would eat it.
- Verify the first send in Messages.app UI — handoff is not delivery.
- Mixed-service participants (one Android in an otherwise-iMessage group) can cause Messages to materialize TWO parallel chats (iMessage + SMS/RCS variants) on initial send. Once both exist, future `--new-group` calls reuse whichever the chat-iterator finds first; the duplicate must be deleted manually in Messages.app.

## Python consumer surface

```python
import sys
sys.path.insert(0, "/Users/shakstzy/ULTRON/_shell/skills/imessage")
from client import send_imessage, IMessageError

result = send_imessage("+15125551234", text="halt: turnstile detected")
# → {"handoff": "ok", "path": "chat"}
```

`send_imessage(to, text=None, file=None)` returns the parsed JSON. Raises `IMessageError` on non-zero exit.

## Permissions

Messages Automation must be allowed (System Settings → Privacy & Security → Automation → grant Terminal/iTerm/Ghostty access to Messages). On first run, AppleScript will prompt; subsequent runs are silent.

No Full Disk Access required (this skill never reads `~/Library/Messages/chat.db`).

## When NOT to use

- Tapbacks, message edits, reactions — AppleScript can't.
- WhatsApp / Telegram / Signal / Slack — different skills.
- High-volume bulk sends — macOS will throttle.
- Anything where you need delivery confirmation — handoff ≠ delivery.

## Throttling

No internal cap. Callers in batch contexts should space sends by ≥2s.
