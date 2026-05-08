#!/usr/bin/env bash
# dial.sh — place an outbound phone call via iPhone Continuity calling.
#
# Mac opens a tel: URL → FaceTime hands the dial to the iPhone over Continuity →
# the call goes out from Adithya's actual cell number.
#
# Modes:
#   --to "Mom"             contact-name resolution via Apple Contacts (osascript)
#   --to "+15125551234"    E.164 direct
#   --to "5125551234"      US 10-digit, auto-prefixed +1
#
# Default is --dry-run (zero side effects). Pass --send to actually dial.
#
# Emits JSON on stdout:
#   {"handoff":"ok","mode":"dry-run|send","recipient_input":"...","resolved_e164":"+1...","resolved_name":"...","action":"would-dial|dialing"}
#
# Exit codes:
#   0 — dry-run printed, or call handed to FaceTime
#   2 — arg error
#   3 — resolution error / FaceTime missing / Continuity disabled / ambiguous contact
set -euo pipefail

die()  { echo "dial.sh: $*" >&2; exit 2; }
fail() { echo "dial.sh: $*" >&2; exit 3; }
# AppleScript string escape: backslash and double-quote.
esc_as() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }

TO=""; MODE="dry-run"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --to)      [[ $# -ge 2 ]] || die "--to requires a value"; TO="$2"; shift 2 ;;
    --send)    MODE="send"; shift ;;
    --dry-run) MODE="dry-run"; shift ;;
    -h|--help) sed -n '2,21p' "$0"; exit 0 ;;
    *) die "unknown flag: $1" ;;
  esac
done

[[ -z "$TO" ]] && die "--to required"

# ─── FaceTime presence check ──────────────────────────────────────────────────
if [[ ! -d /System/Applications/FaceTime.app && ! -d /Applications/FaceTime.app ]]; then
  fail "FaceTime.app not found — phone calls require FaceTime"
fi

# ─── Phone number normalization ───────────────────────────────────────────────
normalize_e164() {
  local raw="$1"
  local digits
  digits=$(printf '%s' "$raw" | tr -d -c '0-9')
  case "$raw" in
    +*)
      [[ ${#digits} -ge 7 && ${#digits} -le 15 ]] || return 1
      printf '+%s' "$digits" ;;
    *)
      if [[ ${#digits} -eq 10 ]]; then
        printf '+1%s' "$digits"
      elif [[ ${#digits} -eq 11 && "${digits:0:1}" == "1" ]]; then
        printf '+%s' "$digits"
      elif [[ ${#digits} -ge 11 && ${#digits} -le 15 ]]; then
        printf '+%s' "$digits"
      else
        return 1
      fi ;;
  esac
}

# ─── Detect E.164-ish input vs contact name ───────────────────────────────────
# E.164-ish: optional +, 7-15 digits, optional spaces/dashes/parens. No letters.
RECIPIENT_NAME=""
RESOLVED_E164=""
if [[ "$TO" =~ ^[+]?[0-9\ \(\)\-]+$ ]]; then
  if RESOLVED_E164=$(normalize_e164 "$TO"); then
    RECIPIENT_NAME="$TO"
  else
    fail "could not normalize phone-like input to E.164: $TO"
  fi
else
  # ─── Apple Contacts resolution ────────────────────────────────────────────
  TO_AS=$(esc_as "$TO")
  RAW=$(osascript <<EOF 2>/dev/null
tell application "Contacts"
  set matches to (every person whose name is "$TO_AS")
  if (count of matches) is 0 then
    return "ERR::no-match"
  end if
  if (count of matches) > 1 then
    set names_list to ""
    repeat with p in matches
      set names_list to names_list & (name of p) & "||"
    end repeat
    return "ERR::multi-name::" & names_list
  end if
  set p to item 1 of matches
  set phones_list to phones of p
  if (count of phones_list) is 0 then
    return "ERR::no-phone::" & (name of p)
  end if
  set out to (name of p) & "::"
  repeat with ph in phones_list
    try
      set lab to (label of ph as string)
    on error
      set lab to "other"
    end try
    set val to (value of ph as string)
    set out to out & lab & "==" & val & "||"
  end repeat
  return out
end tell
EOF
)
  if [[ -z "$RAW" ]]; then
    fail "osascript returned empty — Contacts.app may need automation permission for this terminal"
  fi
  case "$RAW" in
    "ERR::no-match")
      fail "no Apple Contact matches name: $TO" ;;
    "ERR::multi-name::"*)
      LIST="${RAW#ERR::multi-name::}"
      echo "dial.sh: multiple Apple Contacts named '$TO'. Disambiguate by passing the full name or +E.164 directly:" >&2
      printf '  - %s\n' $(echo "$LIST" | tr '|' '\n' | grep -v '^$') >&2
      exit 3 ;;
    "ERR::no-phone::"*)
      fail "Apple Contact '${RAW#ERR::no-phone::}' has no phone number on file" ;;
  esac

  # Parse "<name>::<lab1>==<num1>||<lab2>==<num2>||..."
  RECIPIENT_NAME="${RAW%%::*}"
  PHONES_BLOCK="${RAW#*::}"

  # Pick best phone: prefer mobile/iPhone, else first.
  PICK=""
  IFS='|' read -ra PARTS <<<"$PHONES_BLOCK"
  for entry in "${PARTS[@]}"; do
    [[ -z "$entry" ]] && continue
    LAB="${entry%%==*}"
    NUM="${entry#*==}"
    case "$LAB" in
      *mobile*|*iPhone*|*iphone*|*Mobile*) PICK="$NUM"; break ;;
    esac
  done
  if [[ -z "$PICK" ]]; then
    for entry in "${PARTS[@]}"; do
      [[ -z "$entry" ]] && continue
      PICK="${entry#*==}"
      break
    done
  fi
  [[ -z "$PICK" ]] && fail "could not pick a phone for $RECIPIENT_NAME"
  if ! RESOLVED_E164=$(normalize_e164 "$PICK"); then
    fail "Apple Contact '$RECIPIENT_NAME' has phone '$PICK' that does not normalize to E.164"
  fi
fi

# ─── Continuity calling enablement check (best-effort, non-fatal in dry-run) ─
CONTINUITY_OK="unknown"
if VAL=$(defaults read com.apple.FaceTime CallsFromiPhone 2>/dev/null); then
  [[ "$VAL" == "1" ]] && CONTINUITY_OK="enabled" || CONTINUITY_OK="disabled"
fi
if [[ "$MODE" == "send" && "$CONTINUITY_OK" == "disabled" ]]; then
  fail "FaceTime → Calls from iPhone is disabled. Enable in FaceTime → Settings → 'Calls from iPhone' before --send"
fi

# ─── Emit handoff JSON ────────────────────────────────────────────────────────
ACTION=$([ "$MODE" = "send" ] && echo "dialing" || echo "would-dial")
ESC_NAME=$(printf '%s' "$RECIPIENT_NAME" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')
printf '{"handoff":"ok","mode":"%s","recipient_input":%s,"resolved_e164":"%s","resolved_name":%s,"continuity":"%s","action":"%s"}\n' \
  "$MODE" \
  "$(printf '%s' "$TO" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" \
  "$RESOLVED_E164" \
  "$ESC_NAME" \
  "$CONTINUITY_OK" \
  "$ACTION"

# ─── Dry-run exit ─────────────────────────────────────────────────────────────
if [[ "$MODE" != "send" ]]; then
  exit 0
fi

# ─── Live dial: 3-second countdown then open tel: URL via FaceTime ────────────
echo "dial.sh: live dial in 3s — Ctrl-C to abort. Recipient: $RECIPIENT_NAME ($RESOLVED_E164)" >&2
for i in 3 2 1; do echo -n "  $i..." >&2; sleep 1; done; echo "" >&2

# Open the tel: URL — FaceTime catches it. On a Continuity-enabled Mac this
# pops a "Call (via iPhone)" confirmation; on plain FaceTime it's "FaceTime
# Audio". We send a Return keystroke after a short focus delay to confirm the
# default action. If Adithya's setup has the FaceTime Audio button as default
# (no Continuity), this WILL place a FaceTime Audio call instead — surface
# clearly in the JSON so the user knows.
open "tel:$RESOLVED_E164"
sleep 0.9
osascript <<'OSA' >/dev/null 2>&1 || true
tell application "FaceTime" to activate
delay 0.3
tell application "System Events"
  key code 36
end tell
OSA

echo "dial.sh: handoff to FaceTime complete. Verify call placed in iPhone UI." >&2
exit 0
