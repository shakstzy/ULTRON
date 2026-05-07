---
name: whatsapp
description: Send a WhatsApp message (text or media) to a 1:1 contact or a named group from inside ULTRON. Lives at `~/ULTRON/_shell/skills/whatsapp/`. Hits the lharries/whatsapp-mcp Go bridge REST API on `localhost:8080` — no MCP loaded into Claude sessions, just bash + curl + Python wrapper. Trigger phrases like "whatsapp <name>: <text>", "send <name> a whatsapp", "wa <name>: <text>", "whatsapp the <group> group: <text>". For ingest/read see `_shell/bin/ingest-whatsapp.py`. For contact CRUD use `contacts-add` / `contacts-sync`.
---

# whatsapp

Slim ULTRON-native WhatsApp send. Mirrors the `imessage` skill pattern: a bash entrypoint (`send.sh`), a Python wrapper (`client.py`), and this doc. Zero Claude-session context cost — only loaded when triggered.

## Why this exists

ULTRON ingests WhatsApp via the Go bridge that lharries/whatsapp-mcp ships. The bridge runs as a daemon, maintains a websocket to WhatsApp's servers via whatsmeow, and exposes a REST API on `localhost:8080`. The MCP server that ships in the same repo would load `mcp__whatsapp__*` tool definitions into every Claude Code session forever — that's bloat we don't want. So instead we keep the daemon and ignore the MCP layer; this skill is a thin bash + Python shim over the daemon's REST API.

For inbound (read) — `_shell/bin/ingest-whatsapp.py` reads the bridge's SQLite directly and writes per-(chat, month) markdown shards under `workspaces/<ws>/raw/whatsapp/`. No REST involvement on the read path.

## Pre-flight

The bridge must be running. If not, `send.sh` exits 4 with a clear `bridge unreachable` message — never silently retry. To bring the bridge up:

```bash
WHATSAPP_PAIR_PHONE=+15126601911 ~/.local/bin/whatsapp-bridge &
```

…or load the launchd plist (see "Daemonization" below).

## Recipient resolution

Same gating spirit as the imessage skill. NEVER ask Adithya for a phone number — resolve, then confirm. Order:

1. **Direct E.164** (`+15125551234`) → strip `+`, hand to bridge.
2. **Apple Contacts name** (`"Sydney"`) → `osascript` query against `Contacts.app` for that exact name. Single phone match → use it. Multiple phones → fail loud, ask the caller to disambiguate by passing `+E.164` explicitly. Zero matches → fail.
3. **Group by slug** (`"kinetics-commercial-expansion-ai"`) → re-kebab every chat name in `messages.db` and match. Single match → use the JID. Multiple matches → fail loud (rare; would mean two groups with name-collision after slugify).
4. **Group by JID** (`"120363405567809486@g.us"`) → pass through unchanged.

Sends are gated per Adithya's standing rules (explicit-permission action). Always show the draft + resolved recipient before invoking.

## CLI

```bash
# 1:1 by phone
~/ULTRON/_shell/skills/whatsapp/send.sh --to +15125551234 --text "hey"

# 1:1 by Apple Contact name
~/ULTRON/_shell/skills/whatsapp/send.sh --to "Sydney" --text "morning ☀️"

# Group by slug (matches a folder under raw/whatsapp/groups/)
~/ULTRON/_shell/skills/whatsapp/send.sh --group "kinetics-commercial-expansion-ai" --text "gm"

# Group by JID (no resolution overhead)
~/ULTRON/_shell/skills/whatsapp/send.sh --group "120363405567809486@g.us" --text "gm"

# File attachment (image / video / audio / document)
~/ULTRON/_shell/skills/whatsapp/send.sh --to +15125551234 --file /abs/path/to/photo.jpg
```

Emits JSON on stdout: `{"handoff":"ok","path":"phone|contact|group-by-slug|group-by-jid","recipient":"<jid-or-digits>","bridge_response":"..."}`. Exit 0 = bridge accepted handoff. Delivery is verifiable only on the recipient side; this skill does not claim delivery.

Exit codes:
- `2` arg error (missing `--to`/`--group`/`--text`/`--file`, mutually-exclusive flags violated, file not found)
- `3` resolution error (no contact match / ambiguous contact / no group slug match / bridge rejected the send)
- `4` bridge unreachable on `localhost:8080` — start the daemon first, do NOT silently retry

## Python consumer surface

```python
import sys
sys.path.insert(0, "/Users/shakstzy/ULTRON/_shell/skills/whatsapp")
from client import send_whatsapp, WhatsAppError

# 1:1 by phone
send_whatsapp("+15125551234", text="hey")

# Group by slug
send_whatsapp(group="kinetics-commercial-expansion-ai", text="gm")

# File
send_whatsapp("+15125551234", file="/abs/path/to/photo.jpg")
```

Returns the parsed JSON dict from `send.sh`. Raises `WhatsAppError` on non-zero exit (the exception carries `.exit_code` and `.stderr`).

## Daemonization

The Go bridge is a persistent daemon — it must stay connected to WhatsApp's servers to receive messages and process the history sync that `ingest-whatsapp.py` later reads. It's wired into `_shell/config/global-schedule.yaml` as a `daemon:` entry:

```yaml
daemons:
  whatsapp_bridge:
    command: /Users/shakstzy/.local/bin/whatsapp-bridge
    working_dir: /Users/shakstzy/.local/share/whatsapp-mcp/whatsapp-bridge
    keep_alive: true
    env:
      WHATSAPP_PAIR_PHONE: "+15126601911"
```

Compiled to a launchd plist with `KeepAlive: true` (auto-restart on crash) by the `schedule` skill. Load explicitly via `schedule load com.adithya.ultron.daemon-whatsapp-bridge`.

If the WhatsApp linked-device auth ever expires (~20 days per WhatsApp), the bridge will print a fresh QR/pairing code request to its log; the daemon will keep restarting (and failing) until re-authenticated. Fix:

```bash
launchctl bootout gui/$(id -u)/com.adithya.ultron.daemon-whatsapp-bridge
rm ~/.local/share/whatsapp-mcp/whatsapp-bridge/store/*.db
WHATSAPP_PAIR_PHONE=+15126601911 ~/.local/bin/whatsapp-bridge
# enter pairing code on phone, then:
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.adithya.ultron.daemon-whatsapp-bridge.plist
```

## Throttling

WhatsApp has aggressive anti-spam at the account level. The send.sh script imposes no internal cap — callers in batch contexts must space sends ≥3s apart and never exceed ~50 outbound messages/hr. Beyond that, expect device unlinking or temporary account restrictions.

## When NOT to use

- Reactions / emoji tapbacks — bridge doesn't expose this endpoint yet.
- Editing or deleting messages — bridge doesn't expose this either.
- Voice/video calls — out of scope for whatsmeow.
- Sending a voice message that should appear playable inline — use `send_audio_message` semantics from the upstream MCP server (`.ogg` Opus required); for now `--file` sends as a generic audio attachment.
- Bulk outbound (>50/hr) — will get the account flagged.

## Permissions

- macOS Automation → grant Terminal/iTerm/Ghostty access to **Contacts** (System Settings → Privacy & Security → Automation). Without this, contact-name resolution returns empty.
- Bridge must be running and authenticated. See `Daemonization`.

## Related

- `_shell/bin/ingest-whatsapp.py` — the read path; per-(chat, month) markdown shards under `workspaces/<ws>/raw/whatsapp/`.
- `imessage` skill — sister skill for iMessage/SMS/RCS via Messages.app AppleScript.
- `discord` / `telegram` — analogous skills for those platforms.
