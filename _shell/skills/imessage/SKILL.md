---
name: imessage
description: Send an iMessage (or SMS/RCS via existing chat) from inside ULTRON. Uses Messages.app via AppleScript — no ObjC, no IDS lookup, no SQLite. Use for bot halt notifications, low-volume operator pings, or any place a script needs to text Adithya. For contact CRUD use `contacts-add` / `contacts-sync`.
---

# imessage

Slim ULTRON-native iMessage send. Lives at `~/ULTRON/_shell/skills/imessage/`. Consumed via the global symlink `~/.claude/skills/imessage/`.

## Why this exists

ULTRON's bots need to ping Adithya from cron when something halts (Bumble Turnstile, selector drift, cap exhausted). MCP tools can't run from cron — they need Claude in the loop. This skill is a 60-line bash + AppleScript send that any Python or Node consumer can shell out to.

For contact add/lookup use `contacts-add` (write) and `contacts-sync` (read) — they cover the contact side cleanly.

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
