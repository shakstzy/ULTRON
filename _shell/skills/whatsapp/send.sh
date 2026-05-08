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
# Bridge must be running on http://localhost:8080. If down, exit 4 with a clear message — never silently retry.
#
# Emits JSON on stdout:
#   {"handoff":"ok","path":"phone|contact|group-by-slug|group-by-jid","recipient":"<jid>","bridge_response":"..."}
# Exit codes:
#   0 — bridge accepted handoff (delivery is verifiable only on the recipient side; this script does not claim delivery)
#   2 — arg error (missing/conflicting flags, file missing, missing flag value)
#   3 — resolution error (no contact / ambiguous contact / no group slug match / non-E.164 phone / bridge rejected send / file in sensitive dir)
#   4 — bridge unreachable on localhost:8080

set -euo pipefail

BRIDGE_BASE="${WHATSAPP_BRIDGE_BASE:-http://localhost:8080/api}"
ULTRON_ROOT="${ULTRON_ROOT:-$HOME/ULTRON}"
BRIDGE_DB="$HOME/.local/share/whatsapp-mcp/whatsapp-bridge/store/messages.db"

die()  { echo "send.sh: $*" >&2; exit 2; }
fail() { echo "send.sh: $*" >&2; exit 3; }
need_value() {
  # $1 = flag name, $2 = next arg count remaining
  [[ $2 -ge 2 ]] || die "$1 requires a value"
}

TO=""; GROUP=""; TEXT=""; FILE=""; DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --to)      need_value "$1" "$#"; TO="$2";    shift 2 ;;
    --group)   need_value "$1" "$#"; GROUP="$2"; shift 2 ;;
    --text)    need_value "$1" "$#"; TEXT="$2";  shift 2 ;;
    --file)    need_value "$1" "$#"; FILE="$2";  shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) sed -n '2,21p' "$0"; exit 0 ;;
    *) die "unknown flag: $1" ;;
  esac
done

[[ -z "$TO$GROUP" ]] && die "--to or --group required"
[[ -n "$TO" && -n "$GROUP" ]] && die "--to and --group are mutually exclusive"
[[ -z "$TEXT" && -z "$FILE" ]] && die "--text or --file required"
[[ -n "$FILE" && ! -f "$FILE" ]] && die "file not found: $FILE"

# ─── File-path sensitive-dir denylist (data-exfil defense) ─────────────────────
# Skill is callable by LLMs; an attacker prompt could try `--file /tmp/innocent`
# where /tmp/innocent is a symlink to $HOME/.ssh/id_rsa. We must follow the
# symlink chain BEFORE checking the denylist — otherwise the bridge opens the
# file via the OS, follows the symlink itself, and exfiltrates the secret.
if [[ -n "$FILE" ]]; then
  ABS_FILE=$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$FILE")
  if [[ ! -f "$ABS_FILE" ]]; then
    die "file not found after symlink resolve: $FILE → $ABS_FILE"
  fi
  case "$ABS_FILE" in
    "$HOME/.ssh/"*|"$HOME/.aws/"*|"$HOME/.gnupg/"*|"$HOME/.config/"*|"$HOME/Library/Keychains/"*|"/etc/"*|"$ULTRON_ROOT/_credentials/"*)
      fail "refusing to send file in sensitive directory: $ABS_FILE" ;;
  esac
  case "$(basename "$ABS_FILE" | tr '[:upper:]' '[:lower:]')" in
    *credential*|*secret*|*token*|*apikey*|*api_key*|*.pem|*.key|*.pkcs12|*.p12|.env|*.env)
      fail "refusing to send file with sensitive name: $ABS_FILE" ;;
  esac
  FILE="$ABS_FILE"
fi

# ─── Pre-flight: bridge reachable? ─────────────────────────────────────────────
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
    # Slug → JID lookup. Mirrors the collision-resolution logic in ingest:
    # - Each chat has a base slug (kebab of name) and may have a disambiguator
    #   suffix when ingest detected multiple chats with the same base slug.
    # - The user could supply either the base slug (no collision) or the
    #   suffixed form (collision), so we accept either and dedupe at the end.
    # - The full whatsmeow JID is the source of truth — passing slug + db
    #   path as argv prevents Python heredoc injection.
    JID=$(python3 - "$GROUP" "$BRIDGE_DB" <<'PY'
import hashlib, re, sqlite3, sys
from collections import defaultdict
slug_in = sys.argv[1].strip()
db = sys.argv[2]
def kc(s):
    s = re.sub(r"[^\w\s-]", "", (s or "").lower())
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown"
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
groups = list(con.execute("SELECT jid, name FROM chats WHERE jid LIKE \"%@g.us\"").fetchall())
# Build base→[jid] then assign each jid a suffixed slug iff its base is shared.
base = {jid: kc(name) for jid, name in groups}
buckets = defaultdict(list)
for jid, b in base.items():
    buckets[b].append(jid)
def short_suffix(jid: str) -> str:
    digits = re.sub(r"\D", "", jid.split("@", 1)[0])
    return digits[-4:] if len(digits) >= 4 else (digits or "x")
suffixed = {}
for b, jids in buckets.items():
    if len(jids) <= 1:
        continue
    used = set()
    fallback = []
    for jid in jids:
        s = f"{b}-{short_suffix(jid)}"
        if s in used:
            fallback.append(jid)
        else:
            suffixed[jid] = s
            used.add(s)
    for jid in fallback:
        suffixed[jid] = f"{b}-" + hashlib.sha256(jid.encode()).hexdigest()[:8]
matches = []
for jid, _ in groups:
    candidates = {base[jid]}
    if jid in suffixed:
        candidates.add(suffixed[jid])
    if slug_in in candidates:
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
  # Apple Contacts resolution. Pass `$TO` as an osascript argv argument (NOT
  # interpolated into the script source) so a contact name with quotes/backslashes
  # can't inject AppleScript or `do shell script` commands.
  PHONES=$(osascript -e '
on run argv
  set the_name to item 1 of argv
  set out to ""
  tell application "Contacts"
    repeat with p in (every person whose name is the_name)
      repeat with ph in phones of p
        set out to out & (value of ph as string) & "|"
      end repeat
    end repeat
  end tell
  return out
end run
' -- "$TO" 2>/dev/null || true)
  PHONES="${PHONES%|}"
  if [[ -z "$PHONES" ]]; then
    fail "no Apple Contact named '$TO' (try +E.164 directly)"
  fi
  COUNT=$(awk -F'|' '{print NF}' <<<"$PHONES")
  if [[ "$COUNT" -gt 1 ]]; then
    fail "contact '$TO' has $COUNT phones: $PHONES — pass +E.164 explicitly"
  fi
  # Strict E.164: must start with `+`, contain only digits after, length 7-15.
  # Without `+`, the leading country code is ambiguous (US (512)555-1234 →
  # 5125551234 would route to a non-existent international number).
  CANDIDATE=$(printf '%s' "$PHONES" | tr -d ' ()-.\t')
  if [[ ! "$CANDIDATE" =~ ^\+[0-9]{7,15}$ ]]; then
    fail "contact '$TO' phone is not E.164 (must start with + and country code): $PHONES"
  fi
  RECIPIENT="${CANDIDATE#+}"
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

# Dry-run: surface resolved recipient + payload, do NOT POST. Used for testing
# recipient resolution / file denylist without risking an actual send.
if [[ "$DRY_RUN" == "1" ]]; then
  python3 -c '
import json, sys
print(json.dumps({
    "handoff": "dry-run",
    "path": sys.argv[1],
    "recipient": sys.argv[2],
    "would_post": json.loads(sys.argv[3]),
}, indent=2))
' "$PATH_TAG" "$RECIPIENT" "$PAYLOAD"
  exit 0
fi

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

python3 -c '
import json, sys
print(json.dumps({
    "handoff": "ok",
    "path": sys.argv[1],
    "recipient": sys.argv[2],
    "bridge_response": json.loads(sys.argv[3]).get("message", ""),
}))
' "$PATH_TAG" "$RECIPIENT" "$RESP"
