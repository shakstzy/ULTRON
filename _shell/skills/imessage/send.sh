#!/usr/bin/env bash
# send.sh — send an iMessage/SMS via Messages.app.
#
# Strategy: prefer "send via existing 1:1 chat" (preserves whatever service
# binding Messages.app already chose — iMessage / SMS / RCS). Fall back to
# "send via iMessage buddy" if no chat exists. No IDS lookup, no compiled
# binaries, no SQLite. Uniform AppleScript for portability.
#
# Usage:
#   send.sh --to <phone-or-email> --text "<body>"
#   send.sh --to <phone-or-email> --file <abs-path>   (file attachment)
#
# Emits JSON on stdout: {"handoff":"ok","path":"chat|buddy"}
# Exit 0 = handoff succeeded (Messages.app accepted). Delivery is visible
# only in Messages.app UI; this script does not claim delivery.
# Exit 2 = arg error. Exit 3 = osascript error.

set -euo pipefail

die() { echo "send.sh: $*" >&2; exit 2; }
esc() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }
digits_tail() { printf '%s' "$1" | tr -d -c '0-9' | tail -c 10; }

TO=""; TEXT=""; FILE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --to)   TO="$2";   shift 2 ;;
    --text) TEXT="$2"; shift 2 ;;
    --file) FILE="$2"; shift 2 ;;
    *) die "unknown flag: $1" ;;
  esac
done

[[ -z "$TO" ]] && die "--to required"
[[ -z "$TEXT$FILE" ]] && die "--text or --file required"
[[ -n "$FILE" && ! -f "$FILE" ]] && die "file not found: $FILE"

# Match phones by digit tail (last 10 digits) so +1, no-plus, and punctuation variants resolve.
if [[ "$TO" == *"@"* ]]; then NEEDLE="$TO"; else NEEDLE=$(digits_tail "$TO"); fi
ESC_NEEDLE=$(esc "$NEEDLE")
ESC_TO=$(esc "$TO")

# Try send-via-existing-chat first (handles iMessage, SMS, RCS uniformly).
if [[ -n "$FILE" ]]; then
  ABS_FILE=$(cd "$(dirname "$FILE")" && printf '%s/%s' "$(pwd)" "$(basename "$FILE")")
  ESC_VAL=$(esc "$ABS_FILE")
  PAYLOAD_KIND="POSIX file \"$ESC_VAL\""
else
  ESC_VAL=$(esc "$TEXT")
  PAYLOAD_KIND="\"$ESC_VAL\""
fi

CHAT_RESULT=$(osascript 2>/dev/null <<OSA || true
tell application "Messages"
  set needle to "$ESC_NEEDLE"
  repeat with c in chats
    try
      if (count of participants of c) is 1 then
        set p to 1st participant of c
        if (handle of p as string) contains needle then
          send $PAYLOAD_KIND to c
          return "ok"
        end if
      end if
    end try
  end repeat
  return "no-chat"
end tell
OSA
)

if [[ "$CHAT_RESULT" == "ok" ]]; then
  echo '{"handoff":"ok","path":"chat"}'
  exit 0
fi

# No existing chat — buddy fallback. iMessage only (AppleScript can't address SMS service for first-time recipients).
BUDDY_ERR=$(osascript 2>&1 <<OSA
tell application "Messages"
  set targetService to 1st service whose service type = iMessage
  set targetBuddy to buddy "$ESC_TO" of targetService
  send $PAYLOAD_KIND to targetBuddy
end tell
OSA
)

if [[ -z "$BUDDY_ERR" ]]; then
  echo '{"handoff":"ok","path":"buddy"}'
  exit 0
fi

# Both paths failed.
echo "send.sh: chat=$CHAT_RESULT, buddy_error=$BUDDY_ERR" >&2
printf '{"handoff":"error","chat_result":"%s","buddy_error":"%s"}\n' "$(esc "$CHAT_RESULT")" "$(esc "$BUDDY_ERR")"
exit 3
