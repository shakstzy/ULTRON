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

NEVER ask Adithya for a phone number or email. Resolve, then confirm. Order:

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
2. **Cross-check the entity stub** at `_global/entities/people/<slug>.md`. Stubs can be mislabeled — e.g. `aarti-mom.md` is "Aarti's mom" (a third party), NOT Adithya's mom (whose contact is named just "Mom"). If the stub disagrees with Apple Contacts, trust Contacts and surface the mismatch so Adithya can fix the stub.
3. **Disambiguate relationships by exact contact name.** "My mom" = the contact literally named `Mom`. "My dad" = `Dad`. Names like `<X> Mom` / `<X> Dad` almost always mean "X's parent" (a third party), not Adithya's parent.
4. **Multiple candidate matches?** List them (name + number + emails) and ask which. Don't guess.
5. **Single confident match?** Show the draft, recipient, and resolved number on one line, then wait for an explicit "yes/send/go" before calling the send tool. Sends are gated per Adithya's standing rules.
6. **Stub bug?** Note it in the reply so Adithya can fix `_global/entities/people/<slug>.md` or the `contacts-sync` skill — don't silently route around it.

Skip the confirm step ONLY for halt-notification sends from bots to Adithya himself (the original cron use case), where the recipient is hardcoded and there's no third party.

## Send strategy

1. **Existing 1:1 chat first.** If Messages.app already has a 1:1 chat with the recipient, send through it. This preserves whatever service binding Messages already chose (iMessage / SMS / RCS).
2. **iMessage buddy fallback.** If no chat exists, send via `1st service whose service type = iMessage`. First-time SMS / RCS recipients are NOT supported via this path — Messages.app must already have routed at least once.

This is intentionally simpler than QUANTUM's `macos-contacts-imessage` skill (which compiles an ObjC IDS-query helper and consults Apple's private framework). For ULTRON's halt-notification use case, the chat-history fallback is sufficient and avoids the build step.

## CLI

```bash
~/ULTRON/_shell/skills/imessage/send.sh --to +15125551234 --text "halt: turnstile detected"
~/ULTRON/_shell/skills/imessage/send.sh --to friend@icloud.com --text "ping"
~/ULTRON/_shell/skills/imessage/send.sh --to +15125551234 --file /abs/path/to/screenshot.png
```

Emits JSON on stdout: `{"handoff":"ok","path":"chat"|"buddy"}`. Exit 0 = handoff accepted. Delivery is verifiable only in Messages.app UI; this script does not claim delivery.

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

- Group chats, tapbacks, message edits — AppleScript can't.
- WhatsApp / Telegram / Signal / Slack — different skills.
- High-volume bulk sends — macOS will throttle.
- Anything where you need delivery confirmation — handoff ≠ delivery.

## Throttling

No internal cap. Callers in batch contexts should space sends by ≥2s.
