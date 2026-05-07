#!/usr/bin/env bash
# send.sh — send a WhatsApp message via the lharries/whatsapp-mcp Go bridge REST API.
#
# Modes:
#   1:1 by phone:    --to +15125551234 --text "<body>"
#   1:1 by contact:  --to "Sydney" --text "<body>"   (resolved via Apple Contacts → phone)
#   Group by name:   --group "kinetics-commercial-expansion-ai" --text "<body>"
#                    (slug from raw/whatsapp/groups/<slug>/, resolved to JID via messages.db)
#   Group by JID:    --group "120363405567809486@g.us" --text "<body>"
#   File attachment: --to <recipient> --file /abs/path
#
# Bridge must be running on http://localhost:8080. Pre-flight: GET /api/send returns 405 (POST-only).
# If the bridge is down, exit 4 and print a clear "bridge not running" message — never silently retry.
#
# Emits JSON on stdout:
#   {"handoff":"ok","path":"phone|contact|group-by-slug|group-by-jid","recipient":"<jid>","bridge_response":"..."}
# Exit 0 = bridge accepted handoff. Exit 2 = arg error. Exit 3 = resolution error. Exit 4 = bridge unreachable.
# Delivery is verifiable only on the recipient side; this script does not claim delivery.

set -euo pipefail

BRIDGE_BASE="${WHATSAPP_BRIDGE_BASE:-http://localhost:8080/api}"
ULTRON_ROOT="${ULTRON_ROOT:-$HOME/ULTRON}"
BRIDGE_DB="$HOME/.local/share/whatsapp-mcp/whatsapp-bridge/store/messages.db"

die()  { echo "send.sh: $*" >&2; exit 2; }
fail() { echo "send.sh: $*" >&2; exit 3; }

TO=""; GROUP=""; TEXT=""; FILE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --to)     TO="$2";     shift 2 ;;
    --group)  GROUP="$2";  shift 2 ;;
    --text)   TEXT="$2";   shift 2 ;;
    --file)   FILE="$2";   shift 2 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) die "unknown flag: $1" ;;
  esac
done

[[ -z "$TO$GROUP" ]] && die "--to or --group required"
[[ -n "$TO" && -n "$GROUP" ]] && die "--to and --group are mutually exclusive"
[[ -z "$TEXT" && -z "$FILE" ]] && die "--text or --file required"
[[ -n "$FILE" && ! -f "$FILE" ]] && die "file not found: $FILE"

# ─── Pre-flight: bridge reachable? ─────────────────────────────────────────────
# Outside-the-subshell `||` so `set -e` doesn't kill us on curl's connect error.
HTTP_CODE=$(curl -sS -o /dev/null -w '%{http_code}' -m 3 -X POST "$BRIDGE_BASE/send" -d '{}' 2>/dev/null) || HTTP_CODE="000"
if [[ "$HTTP_CODE" == "000" ]]; then
  echo "send.sh: bridge unreachable at $BRIDGE_BASE — start the WhatsApp bridge daemon first" >&2
  exit 4
fi

# ─── Resolve recipient → bridge format ─────────────────────────────────────────
PATH_TAG=""
RECIPIENT=""

if [[ -n "$GROUP" ]]; then
  if [[ "$GROUP" == *@g.us ]]; then
    RECIPIENT="$GROUP"
    PATH_TAG="group-by-jid"
  else
    # Slug → JID lookup. Slug matches the kebab-cased chat name, so we re-slug
    # candidates from the chats table and pick the one that matches.
    JID=$(python3 - <<PY
import re, sqlite3
slug = "$GROUP".strip()
def kc(s):
    s = re.sub(r"[^\w\s-]", "", (s or "").lower())
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown"
con = sqlite3.connect("file:$BRIDGE_DB?mode=ro", uri=True)
matches = [r[0] for r in con.execute("SELECT jid, name FROM chats WHERE jid LIKE '%@g.us'").fetchall() if False]
# Re-do cleanly: enumerate, kebab the name, match slug.
matches = []
for jid, name in con.execute("SELECT jid, name FROM chats WHERE jid LIKE '%@g.us'").fetchall():
    if kc(name) == slug:
        matches.append(jid)
print("|".join(matches))
PY
)
    if [[ -z "$JID" ]]; then
      fail "no group chat matched slug '$GROUP' in $BRIDGE_DB"
    fi
    if [[ "$JID" == *"|"* ]]; then
      fail "ambiguous group slug '$GROUP' — multiple JIDs matched: $JID"
    fi
    RECIPIENT="$JID"
    PATH_TAG="group-by-slug"
  fi
elif [[ "$TO" =~ ^\+[0-9]{7,15}$ ]]; then
  RECIPIENT="${TO#+}"
  PATH_TAG="phone"
else
  # Contact-name resolution via Apple Contacts (osascript). Returns one or more
  # phone numbers; if multiple, we fail loud and ask the caller to pin a number.
  PHONES=$(osascript <<APPLE 2>/dev/null
tell application "Contacts"
  set out to ""
  repeat with p in (every person whose name is "$TO")
    repeat with ph in phones of p
      set out to out & (value of ph as string) & "|"
    end repeat
  end repeat
  return out
end tell
APPLE
)
  PHONES="${PHONES%|}"
  if [[ -z "$PHONES" ]]; then
    fail "no Apple Contact named '$TO' (try +E.164 directly)"
  fi
  COUNT=$(awk -F'|' '{print NF}' <<<"$PHONES")
  if [[ "$COUNT" -gt 1 ]]; then
    fail "contact '$TO' has $COUNT phones: $PHONES — pass +E.164 explicitly"
  fi
  # Normalize: digits only, strip leading + and any formatting
  E164=$(printf '%s' "$PHONES" | tr -dc '0-9+')
  E164="${E164#+}"
  if [[ -z "$E164" ]]; then
    fail "contact '$TO' phone could not be normalized to E.164: $PHONES"
  fi
  RECIPIENT="$E164"
  PATH_TAG="contact"
fi

# ─── POST to bridge ────────────────────────────────────────────────────────────
PAYLOAD=$(python3 -c '
import json, sys
d = {"recipient": sys.argv[1]}
if sys.argv[2]: d["message"] = sys.argv[2]
if sys.argv[3]: d["media_path"] = sys.argv[3]
print(json.dumps(d))
' "$RECIPIENT" "$TEXT" "$FILE")

RESP=$(curl -sS -m 30 -X POST -H 'Content-Type: application/json' -d "$PAYLOAD" "$BRIDGE_BASE/send" 2>&1) || {
  echo "send.sh: bridge POST failed: $RESP" >&2
  exit 4
}

# Extract success flag from the response
SUCCESS=$(python3 -c '
import json, sys
try:
    d = json.loads(sys.argv[1])
    print("true" if d.get("success") else "false")
except Exception:
    print("false")
' "$RESP" 2>/dev/null || echo "false")

if [[ "$SUCCESS" != "true" ]]; then
  echo "send.sh: bridge rejected send — $RESP" >&2
  exit 3
fi

# Compose handoff JSON
python3 -c '
import json, sys
print(json.dumps({
    "handoff": "ok",
    "path": sys.argv[1],
    "recipient": sys.argv[2],
    "bridge_response": json.loads(sys.argv[3]).get("message", ""),
}))
' "$PATH_TAG" "$RECIPIENT" "$RESP"
