#!/usr/bin/env bash
# send.sh — send an iMessage/SMS/RCS via Messages.app to 1:1 OR group chats.
#
# Modes:
#   1:1 existing chat:    --to <phone-or-email> --text "<body>"
#   1:1 file attachment:  --to <phone-or-email> --file <abs-path>
#   1:1 fresh recipient:  same as above; falls back to iMessage buddy if no chat exists
#   Group by name:        --group "<exact chat name>" --text "<body>"
#   Group by participants:--to "<h1>,<h2>,<h3>" --text "<body>"   (matches existing group with EXACTLY these participants)
#   NEW group:            --new-group "<h1>,<h2>,<h3>" --text "<body>"   (creates group via imessage:// URL + keystroke send)
#
# Service binding for groups: AppleScript send-to-existing-chat preserves whatever Messages.app already chose
# (iMessage / SMS / RCS), so a mixed iMessage+Android group routes correctly without the caller specifying.
#
# NEW group creation uses Messages.app's `imessage://?addresses=` URL scheme (opens compose window pre-filled
# with recipients, Messages auto-creates the group on first send) plus GUI keystroke to send. Requires
# Accessibility permission for the parent process. Fragile — verify in Messages.app UI after.
#
# Emits JSON on stdout: {"handoff":"ok","path":"chat|buddy|group-by-name|group-by-participants|new-group"}
# Exit 0 = handoff accepted. Delivery is verifiable only in Messages.app UI.
# Exit 2 = arg error. Exit 3 = osascript / send error.

set -euo pipefail

die() { echo "send.sh: $*" >&2; exit 2; }
esc() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }
digits_tail() { printf '%s' "$1" | tr -d -c '0-9' | tail -c 10; }
urlenc() { python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1],safe=""),end="")' "$1"; }

TO=""; TEXT=""; TEXT_FILE=""; FILE=""; GROUP=""; NEW_GROUP=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --to)        TO="$2";        shift 2 ;;
    --text)      TEXT="$2";      shift 2 ;;
    --text-file) TEXT_FILE="$2"; shift 2 ;;
    --file)      FILE="$2";      shift 2 ;;
    --group)     GROUP="$2";     shift 2 ;;
    --new-group) NEW_GROUP="$2"; shift 2 ;;
    *) die "unknown flag: $1" ;;
  esac
done

# --text-file is the preferred path for any non-trivial draft (avoids shell quoting bugs
# with quotes / backticks / $ / newlines). Either flag works; --text wins if both given.
if [[ -z "$TEXT" && -n "$TEXT_FILE" ]]; then
  [[ -f "$TEXT_FILE" ]] || die "--text-file not found: $TEXT_FILE"
  TEXT=$(cat "$TEXT_FILE")
fi

[[ -z "$TO$GROUP$NEW_GROUP" ]] && die "--to, --group, or --new-group required"
[[ -z "$TEXT$FILE" ]] && die "--text, --text-file, or --file required"
[[ -n "$FILE" && ! -f "$FILE" ]] && die "file not found: $FILE"
[[ -n "$NEW_GROUP" && -n "$FILE" ]] && die "--new-group does not support --file (use --group after creation)"

if [[ -n "$FILE" ]]; then
  ABS_FILE=$(cd "$(dirname "$FILE")" && printf '%s/%s' "$(pwd)" "$(basename "$FILE")")
  ESC_VAL=$(esc "$ABS_FILE")
  PAYLOAD_KIND="POSIX file \"$ESC_VAL\""
else
  ESC_VAL=$(esc "$TEXT")
  PAYLOAD_KIND="\"$ESC_VAL\""
fi

# ─── Mode: NEW group via imessage:// URL with body pre-filled ────────────────
# URL scheme pre-fills both recipients AND body, so we just need to press Return.
# No body-typing keystrokes — eliminates the long-text / special-char / focus-race fragility.
if [[ -n "$NEW_GROUP" ]]; then
  # FIND-OR-CREATE semantics: if a group with exactly these participants already
  # exists (any service binding), reuse it. Only create a new chat if none matches.
  # This prevents Messages.app from spawning duplicate groups across iMessage/RCS/SMS
  # variants when the participant set is already known.
  RECIPIENTS=()
  IFS=',' read -ra TO_ARR <<<"$NEW_GROUP"
  for r in "${TO_ARR[@]}"; do
    r=$(echo "$r" | xargs)
    [[ -z "$r" ]] && RECIPIENTS+=() || RECIPIENTS+=("$r")
  done
  [[ ${#RECIPIENTS[@]} -eq 0 ]] && die "--new-group needs at least one recipient"

  # Build needles list (digit tails for phones, full string for emails) for AppleScript match.
  EXPECTED_COUNT=${#RECIPIENTS[@]}
  NEEDLES=""
  for r in "${RECIPIENTS[@]}"; do
    if [[ "$r" == *"@"* ]]; then n="$r"; else n=$(digits_tail "$r"); fi
    NEEDLES+="$n|"
  done
  ESC_NEEDLES=$(esc "${NEEDLES%|}")

  # Step 1: search for an existing chat with exactly this participant set.
  EXISTING=$(osascript 2>/dev/null <<OSA || true
tell application "Messages"
  set needle_str to "$ESC_NEEDLES"
  set AppleScript's text item delimiters to "|"
  set needles to text items of needle_str
  set AppleScript's text item delimiters to ""
  set expected to $EXPECTED_COUNT
  repeat with c in chats
    try
      if (count of participants of c) is expected then
        set found to 0
        repeat with p in participants of c
          set h to handle of p as string
          repeat with n in needles
            if h contains (n as string) then
              set found to found + 1
              exit repeat
            end if
          end repeat
        end repeat
        if found is expected then
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
  if [[ "$EXISTING" == "ok" ]]; then
    echo '{"handoff":"ok","path":"group-existing","note":"reused existing chat with this participant set"}'
    exit 0
  fi

  # Step 2: no match — create the group via URL scheme + Return.
  ADDR_LIST=$(IFS=','; echo "${RECIPIENTS[*]}")
  URL="imessage:?addresses=$(urlenc "$ADDR_LIST")&body=$(urlenc "$TEXT")"
  echo "send.sh: no existing group with these participants; opening $URL" >&2
  open "$URL"
  ERR=$(osascript 2>&1 <<'OSA'
tell application "Messages" to activate
delay 1.5
tell application "System Events" to key code 36
OSA
)
  if [[ -n "$ERR" ]]; then
    printf '{"handoff":"error","path":"group-create","error":"%s"}\n' "$(esc "$ERR")"
    exit 3
  fi
  echo '{"handoff":"ok","path":"group-created","note":"created new group via URL scheme"}'
  exit 0
fi

# ─── Mode: existing group by name ────────────────────────────────────────────
if [[ -n "$GROUP" ]]; then
  ESC_GROUP=$(esc "$GROUP")
  RESULT=$(osascript 2>/dev/null <<OSA || true
tell application "Messages"
  set target_name to "$ESC_GROUP"
  repeat with c in chats
    try
      if (count of participants of c) > 1 then
        try
          set nm to (name of c) as string
          if nm is target_name then
            send $PAYLOAD_KIND to c
            return "ok"
          end if
        end try
      end if
    end try
  end repeat
  return "no-chat"
end tell
OSA
)
  if [[ "$RESULT" == "ok" ]]; then
    echo '{"handoff":"ok","path":"group-by-name"}'
    exit 0
  fi
  printf '{"handoff":"error","path":"group-by-name","reason":"no group chat named %s"}\n' "$(esc "$GROUP")"
  exit 3
fi

# ─── Mode: multi-recipient via --to "+1,+2,+3" → delegates to find-or-create ─
# This is identical semantics to --new-group; we route through that block by
# re-execing ourselves with the right flag. Keeps one canonical code path for
# group dedupe.
if [[ "$TO" == *","* ]]; then
  if [[ -n "$FILE" ]]; then
    exec "$0" --new-group "$TO" --file "$FILE"
  else
    exec "$0" --new-group "$TO" --text "$TEXT"
  fi
fi

# ─── Mode: 1:1 (existing chat, then iMessage buddy fallback) ─────────────────
if [[ "$TO" == *"@"* ]]; then NEEDLE="$TO"; else NEEDLE=$(digits_tail "$TO"); fi
ESC_NEEDLE=$(esc "$NEEDLE")
ESC_TO=$(esc "$TO")

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

echo "send.sh: chat=$CHAT_RESULT, buddy_error=$BUDDY_ERR" >&2
printf '{"handoff":"error","chat_result":"%s","buddy_error":"%s"}\n' "$(esc "$CHAT_RESULT")" "$(esc "$BUDDY_ERR")"
exit 3
