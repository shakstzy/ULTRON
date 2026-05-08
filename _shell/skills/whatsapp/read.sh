#!/usr/bin/env bash
# read.sh — peek at a WhatsApp chat's recent messages without ingesting.
#
# Modes:
#   By contact name:  --to "Aamir Khan UC Berkeley" --limit 20
#   By phone E.164:   --to +15125551234 --limit 20
#   By group slug:    --group east-parke-main-group --limit 20
#   By group/dm JID:  --to 15125551234@s.whatsapp.net --limit 20
#                  OR --group 120363023221027012@g.us --limit 20
#
# Reads from the bridge's local SQLite (read-only). Bridge does NOT need to be
# running — historical messages are persisted. Only most-recent N messages are
# returned (default 20). Output is the same `**HH:MM — sender:** text` format
# as the per-month markdown shards, prepended with a one-line chat header.
#
# Exit codes:
#   0 — printed N messages
#   2 — arg error
#   3 — chat not found / ambiguous slug
#   4 — bridge SQLite missing (bridge has never run + paired)

set -euo pipefail

ULTRON_ROOT="${ULTRON_ROOT:-$HOME/ULTRON}"
BRIDGE_DB="$HOME/.local/share/whatsapp-mcp/whatsapp-bridge/store/messages.db"
WA_DB="$HOME/.local/share/whatsapp-mcp/whatsapp-bridge/store/whatsapp.db"

die()  { echo "read.sh: $*" >&2; exit 2; }
fail() { echo "read.sh: $*" >&2; exit 3; }
need_value() { [[ $2 -ge 2 ]] || die "$1 requires a value"; }

TO=""; GROUP=""; LIMIT=20
while [[ $# -gt 0 ]]; do
  case "$1" in
    --to)     need_value "$1" "$#"; TO="$2";    shift 2 ;;
    --group)  need_value "$1" "$#"; GROUP="$2"; shift 2 ;;
    --limit)  need_value "$1" "$#"; LIMIT="$2"; shift 2 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) die "unknown flag: $1" ;;
  esac
done

[[ -z "$TO$GROUP" ]] && die "--to or --group required"
[[ -n "$TO" && -n "$GROUP" ]] && die "--to and --group are mutually exclusive"
[[ ! -f "$BRIDGE_DB" ]] && { echo "read.sh: bridge SQLite missing at $BRIDGE_DB" >&2; exit 4; }
[[ "$LIMIT" =~ ^[0-9]+$ ]] || die "--limit must be a positive integer"

# All resolution + rendering happens in one Python pass for atomicity. Inputs
# arrive via argv (NOT heredoc interpolation) to prevent injection.
python3 - "$BRIDGE_DB" "$WA_DB" "$ULTRON_ROOT" "$TO" "$GROUP" "$LIMIT" <<'PY'
import os, re, sqlite3, sys
from collections import defaultdict
from pathlib import Path

bridge_db, wa_db, ultron_root, to_arg, group_arg, limit = sys.argv[1:7]
limit = int(limit)
contacts_dir = Path(ultron_root) / "_global" / "entities" / "people"

def kc(s):
    s = re.sub(r"[^\w\s-]", "", (s or "").lower())
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown"

def jid_to_phone(jid):
    if not jid or "@s.whatsapp.net" not in jid:
        return None
    digits = jid.split("@", 1)[0].split(":", 1)[0].strip()
    return ("+" + digits) if digits.isdigit() else None

# Build phone → display from Apple Contacts + whatsmeow_contacts
def name_for_phone(phone, contacts, wa_contacts):
    return contacts.get(phone) or wa_contacts.get(phone)

# Apple Contacts
contacts = {}
phone_re = re.compile(r"\+\d{7,15}")
if contacts_dir.exists():
    for f in contacts_dir.glob("*.md"):
        text = f.read_text(errors="replace")
        title = re.search(r"^title:\s*(.+)$", text, flags=re.MULTILINE)
        display = title.group(1).strip() if title else f.stem
        for ph in phone_re.findall(text):
            contacts[ph] = display

# whatsmeow_contacts + lid_map
wa_contacts = {}
lid_map = {}
try:
    c = sqlite3.connect(f"file:{wa_db}?mode=ro", uri=True)
    for tjid, fn, pn, bn in c.execute(
        "SELECT their_jid, full_name, push_name, business_name FROM whatsmeow_contacts"
    ).fetchall():
        ph = jid_to_phone(tjid or "")
        if ph:
            n = (fn or "").strip() or (pn or "").strip() or (bn or "").strip()
            if n:
                wa_contacts[ph] = n
    for lid, pn in c.execute("SELECT lid, pn FROM whatsmeow_lid_map").fetchall():
        if lid and pn and pn.isdigit():
            lid_map[str(lid)] = "+" + pn
    c.close()
except sqlite3.Error:
    pass

# Resolve the requested chat → JID
con = sqlite3.connect(f"file:{bridge_db}?mode=ro", uri=True)
target_jid = None

if group_arg:
    if group_arg.endswith("@g.us"):
        target_jid = group_arg
    else:
        # Mirror send.sh: try base slug AND collision-resolved suffix
        groups = list(con.execute("SELECT jid, name FROM chats WHERE jid LIKE \"%@g.us\"").fetchall())
        base = {jid: kc(name) for jid, name in groups}
        buckets = defaultdict(list)
        for jid, b in base.items():
            buckets[b].append(jid)
        suffixed = {}
        for b, jids in buckets.items():
            if len(jids) <= 1:
                continue
            for jid in jids:
                d = re.sub(r"\D", "", jid.split("@", 1)[0])
                suffixed[jid] = f"{b}-" + (d[-4:] if len(d) >= 4 else (d or "x"))
        candidates = []
        for jid, _ in groups:
            cand = {base[jid]}
            if jid in suffixed:
                cand.add(suffixed[jid])
            if group_arg in cand:
                candidates.append(jid)
        if not candidates:
            sys.stderr.write(f"read.sh: no group chat matched slug '{group_arg}'\n")
            sys.exit(3)
        if len(candidates) > 1:
            sys.stderr.write(f"read.sh: ambiguous group slug '{group_arg}' — {len(candidates)} matches\n")
            sys.exit(3)
        target_jid = candidates[0]
elif to_arg:
    if "@" in to_arg and ("@s.whatsapp.net" in to_arg or "@lid" in to_arg):
        target_jid = to_arg
    elif re.match(r"^\+[0-9]{7,15}$", to_arg):
        target_jid = to_arg.lstrip("+") + "@s.whatsapp.net"
    else:
        # Apple Contact name → phone → JID
        # (osascript here for parity with send.sh; argv passed via -- to prevent injection)
        import subprocess
        proc = subprocess.run(
            ["osascript", "-e",
             'on run argv\n'
             '  tell application "Contacts"\n'
             '    set out to ""\n'
             '    repeat with p in (every person whose name is item 1 of argv)\n'
             '      repeat with ph in phones of p\n'
             '        set out to out & (value of ph as string) & "|"\n'
             '      end repeat\n'
             '    end repeat\n'
             '    return out\n'
             '  end tell\n'
             'end run',
             "--", to_arg],
            capture_output=True, text=True,
        )
        phones = (proc.stdout or "").rstrip("|\n")
        if not phones:
            sys.stderr.write(f"read.sh: no Apple Contact named '{to_arg}'\n")
            sys.exit(3)
        candidates = [p for p in phones.split("|") if p]
        if len(candidates) > 1:
            sys.stderr.write(f"read.sh: contact '{to_arg}' has {len(candidates)} phones; pass +E.164 explicitly\n")
            sys.exit(3)
        digits = re.sub(r"[^0-9+]", "", candidates[0])
        if not re.match(r"^\+[0-9]{7,15}$", digits):
            sys.stderr.write(f"read.sh: contact '{to_arg}' phone not E.164: {candidates[0]}\n")
            sys.exit(3)
        target_jid = digits.lstrip("+") + "@s.whatsapp.net"

if not target_jid:
    sys.stderr.write("read.sh: could not resolve chat\n")
    sys.exit(3)

# Fetch chat name + last N messages
chat_row = con.execute("SELECT name FROM chats WHERE jid = ?", (target_jid,)).fetchone()
chat_name = chat_row[0] if chat_row else target_jid
rows = con.execute(
    "SELECT timestamp, sender, content, is_from_me, media_type, filename "
    "FROM messages WHERE chat_jid = ? ORDER BY timestamp DESC LIMIT ?",
    (target_jid, limit),
).fetchall()

# Reverse to chronological order for output
rows = list(reversed(rows))
if not rows:
    sys.stderr.write(f"read.sh: no messages found for {target_jid}\n")
    sys.exit(0)

print(f"# {chat_name}  ({target_jid}, last {len(rows)} msgs)\n")
for ts, sender, content, is_me, media, fname in rows:
    # sender label
    if is_me:
        label = "me"
    else:
        ph = jid_to_phone(sender or "")
        if not ph and (sender or "").endswith("@lid"):
            bare = sender.split("@", 1)[0].split(":", 1)[0]
            ph = lid_map.get(bare)
        label = (ph and name_for_phone(ph, contacts, wa_contacts)) or ph or (f"@{(sender or 'unknown').split('@',1)[0]}")
    ts_short = ts[:16] if ts else "??"
    body = (content or "").rstrip()
    if media and not body:
        body = f"[{media}: {fname}]" if fname else f"[{media}]"
    elif media and body:
        tag = f"[{media}: {fname}]" if fname else f"[{media}]"
        body = f"{tag} {body}"
    elif not body:
        body = "[empty]"
    print(f"**{ts_short} — {label}:** {body}")
PY
