#!/usr/bin/env python3
"""
triage-imessage.py — classify every chat in chat.db using Apple Contacts as
the gate, write auto-allowlist entries to sources.yaml, dump the ambiguous
middle to a review file.

Tiers (per CONTEXT.md / format.md, with confirmed user policy):
  Tier 1I  1:1 chat where the peer's handle resolves to an Apple Contacts entry → auto-allowlist
  Tier 1G  group chat with ≥1 participant in Apple Contacts → auto-allowlist
  Tier 2   handle hits universal blocklist (toll-free, shortcode, noreply) → skip silently
  Tier 3   not in Contacts, not blocklist, has ≥5 msgs both directions → flag for review
  Tier 4   not in Contacts, low activity OR 100% one-direction → skip

Usage:
    triage-imessage.py --workspace personal [--dry-run]

Outputs:
    workspaces/<ws>/config/sources.yaml      (merged: existing + tier 1 entries)
    _shell/runs/<ts>/imessage-triage.md      (full report; Tier 3 review section)
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import sqlite3
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import yaml  # type: ignore

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
DB = Path.home() / "Library" / "Messages" / "chat.db"

TOLL_FREE = ("+1800", "+1888", "+1877", "+1866", "+1855", "+1844", "+1833")
NOREPLY_LOCAL = ("verify", "noreply", "no-reply", "donotreply", "alerts",
                 "notification", "notifications", "info", "support",
                 "system", "mailer-daemon", "postmaster")

PHONE_NONDIGIT_RE = re.compile(r"[^\d+]")
SLUG_BAD = re.compile(r"[^a-z0-9]+")


# ---------------------------------------------------------------------------
# Apple Contacts loading
# ---------------------------------------------------------------------------
def load_contacts() -> tuple[dict[str, str], dict[str, str], int]:
    """Returns ({phone -> name}, {email -> name}, total_contact_count).

    Falls back to ({}, {}, 0) if Contacts.framework is unreachable.
    """
    try:
        from Contacts import (  # type: ignore
            CNContactStore, CNContactFetchRequest,
            CNContactGivenNameKey, CNContactFamilyNameKey,
            CNContactNicknameKey, CNContactOrganizationNameKey,
            CNContactPhoneNumbersKey, CNContactEmailAddressesKey,
        )
    except ImportError:
        return {}, {}, 0

    store = CNContactStore.alloc().init()
    keys = [CNContactGivenNameKey, CNContactFamilyNameKey, CNContactNicknameKey,
            CNContactOrganizationNameKey, CNContactPhoneNumbersKey,
            CNContactEmailAddressesKey]
    req = CNContactFetchRequest.alloc().initWithKeysToFetch_(keys)
    phones: dict[str, str] = {}
    emails: dict[str, str] = {}
    state = {"total": 0}

    def cb(contact, stop):
        state["total"] += 1
        given = contact.givenName() or ""
        family = contact.familyName() or ""
        nick = contact.nickname() or ""
        org = contact.organizationName() or ""
        name = (given + " " + family).strip() or nick or org or "(unnamed)"
        for p in contact.phoneNumbers():
            s = p.value().stringValue()
            n = normalize_phone(s)
            if n:
                phones[n] = name
        for e in contact.emailAddresses():
            v = str(e.value() or "").strip().lower()
            if v:
                emails[v] = name

    ok, err = store.enumerateContactsWithFetchRequest_error_usingBlock_(req, None, cb)
    if not ok:
        sys.stderr.write(f"warning: Contacts enumerate failed: {err}\n")
    return phones, emails, state["total"]


# ---------------------------------------------------------------------------
# Handle normalization + classification helpers
# ---------------------------------------------------------------------------
def normalize_phone(s: str | None) -> str | None:
    if not s:
        return None
    digits = PHONE_NONDIGIT_RE.sub("", s)
    if not digits:
        return None
    if not digits.startswith("+"):
        if len(digits) == 10:
            digits = "+1" + digits
        elif len(digits) == 11 and digits.startswith("1"):
            digits = "+" + digits
    return digits or None


def normalize_handle(h: str | None) -> str | None:
    if not h:
        return None
    h = h.strip()
    if "@" in h:
        return h.lower()
    return normalize_phone(h)


def is_blocked(handle: str | None) -> bool:
    if not handle:
        return False
    if any(handle.startswith(p) for p in TOLL_FREE):
        return True
    if "@" in handle and any(handle.split("@")[0].lower().startswith(p)
                             for p in NOREPLY_LOCAL):
        return True
    if re.fullmatch(r"\d{5,6}", handle):
        return True
    # 5-6 digit shortcode without `+` prefix and no leading 1
    digits = PHONE_NONDIGIT_RE.sub("", handle)
    if digits and digits == handle and len(digits) <= 6:
        return True
    return False


def slug_from_name(name: str) -> str:
    """Lowercase, ASCII-fold, hyphen-separate."""
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = s.lower().strip()
    s = SLUG_BAD.sub("-", s).strip("-")
    return s or "unnamed"


def slug_from_handle(handle: str) -> str:
    if "@" in handle:
        local, domain = handle.split("@", 1)
        return f"email-{slug_from_name(local)}-at-{slug_from_name(domain)}"
    digits = PHONE_NONDIGIT_RE.sub("", handle)
    return f"phone-{digits}"


# ---------------------------------------------------------------------------
# chat.db scan
# ---------------------------------------------------------------------------
def scan_chats(conn) -> list[dict]:
    """Return list of dicts per chat with participants, msg counts, dates."""
    chat_rows = conn.execute("""
        SELECT c.ROWID, c.guid, c.style, c.service_name,
               COALESCE(c.display_name, '') AS display_name
        FROM chat c
    """).fetchall()
    chats = []
    for cid, cguid, style, svc, dname in chat_rows:
        handles = [h for (h,) in conn.execute("""
            SELECT h.id
            FROM chat_handle_join chj
            JOIN handle h ON h.ROWID = chj.handle_id
            WHERE chj.chat_id = ?
        """, (cid,)).fetchall()]
        msg_counts = conn.execute("""
            SELECT COUNT(*),
                   SUM(CASE WHEN m.is_from_me = 1 THEN 1 ELSE 0 END),
                   MIN(m.date), MAX(m.date)
            FROM message m
            JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
            WHERE cmj.chat_id = ?
        """, (cid,)).fetchone()
        total, from_me, dmin, dmax = msg_counts
        from_me = from_me or 0
        from_them = (total or 0) - from_me
        chats.append({
            "rowid": cid,
            "guid": cguid,
            "style": style,
            "service": svc,
            "display_name": dname,
            "handles": handles,
            "total_msgs": total or 0,
            "my_msgs": from_me,
            "their_msgs": from_them,
            "date_min": dmin,
            "date_max": dmax,
        })
    return chats


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------
def classify(chat: dict, phones: dict, emails: dict) -> tuple[str, dict]:
    """Returns (tier, extras) where tier in {'1I','1G','2','3','4'}."""
    is_group = chat["style"] == 43
    matched_handles = []   # [(handle, name)]
    blocked_handles = []
    raw_handles = []       # [(handle, normalized, name_or_None)]
    for h in chat["handles"]:
        n = normalize_handle(h)
        name = None
        if n:
            name = phones.get(n) or emails.get(n)
        if name:
            matched_handles.append((h, name))
        if is_blocked(h):
            blocked_handles.append(h)
        raw_handles.append((h, n, name))

    extras = {
        "matched": matched_handles,
        "blocked": blocked_handles,
        "raw": raw_handles,
    }

    if is_group:
        if matched_handles:
            return "1G", extras
        # Group with no contact match still might be worth keeping if it has
        # signal volume; flag for review.
        if chat["total_msgs"] >= 50:
            return "3", extras
        return "4", extras

    # 1:1
    if not chat["handles"]:
        return "4", extras
    peer = chat["handles"][0]
    if blocked_handles:
        return "2", extras
    if matched_handles:
        return "1I", extras
    # Not in contacts, not blocked
    if chat["my_msgs"] >= 5 and chat["their_msgs"] >= 5:
        return "3", extras
    return "4", extras


# ---------------------------------------------------------------------------
# Tier 1 → sources.yaml entry
# ---------------------------------------------------------------------------
def build_individual_entry(chat: dict, name: str, used_slugs: set[str]) -> dict:
    base = slug_from_name(name) if name and name != "(unnamed)" else slug_from_handle(chat["handles"][0])
    slug = base
    suffix = 2
    while slug in used_slugs:
        # Disambiguate by last 4 of first phone
        digits = PHONE_NONDIGIT_RE.sub("", chat["handles"][0]) if chat["handles"] else ""
        if digits and len(digits) >= 4:
            slug = f"{base}-{digits[-4:]}"
            if slug in used_slugs:
                slug = f"{base}-{suffix}"
                suffix += 1
        else:
            slug = f"{base}-{suffix}"
            suffix += 1
    used_slugs.add(slug)
    return {
        "slug": slug,
        "handles": chat["handles"],
        "full_archive": True,
    }


def build_group_entry(chat: dict, phones: dict, emails: dict,
                      used_slugs: set[str]) -> dict:
    if chat["display_name"]:
        base = slug_from_name(chat["display_name"])
    else:
        # Compose from sorted matched member names (or first-2 handles)
        names = []
        for h in chat["handles"]:
            n = normalize_handle(h)
            nm = (phones.get(n) if n else None) or (emails.get(n) if n else None)
            if nm and nm != "(unnamed)":
                names.append(nm.split()[0])  # first name only
        names = sorted(set(names))[:3]
        if names:
            base = "group-" + "-".join(slug_from_name(n) for n in names)
        else:
            base = f"group-{chat['rowid']}"
    base = base[:60]  # cap length
    slug = base
    suffix = 2
    while slug in used_slugs:
        slug = f"{base}-{suffix}"
        suffix += 1
    used_slugs.add(slug)
    return {
        "slug": slug,
        "chat_guid": chat["guid"],
        "full_archive": True,
    }


# ---------------------------------------------------------------------------
# Output rendering
# ---------------------------------------------------------------------------
def fmt_mac_date(val):
    if not val:
        return "?"
    try:
        # Mac absolute time — try ns, fall back to seconds
        epoch = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
        ns_dt = epoch + datetime.timedelta(seconds=float(val) / 1e9)
        if datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc) <= ns_dt < datetime.datetime(2200, 1, 1, tzinfo=datetime.timezone.utc):
            return ns_dt.date().isoformat()
        return (epoch + datetime.timedelta(seconds=float(val))).date().isoformat()
    except (OverflowError, ValueError):
        return "?"


def write_review(report_dir: Path, all_classified: list[tuple[dict, str, dict]],
                 phones: dict, emails: dict):
    report_dir.mkdir(parents=True, exist_ok=True)
    f = report_dir / "imessage-triage.md"
    counts = Counter(t for _, t, _ in all_classified)
    lines = ["# iMessage triage report", "",
             f"_generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}_", "",
             "## Summary", "",
             f"- Tier 1I (1:1, in Contacts):    {counts.get('1I', 0)}",
             f"- Tier 1G (group, ≥1 Contact):   {counts.get('1G', 0)}",
             f"- Tier 2  (blocklist):           {counts.get('2', 0)}",
             f"- Tier 3  (review needed):       {counts.get('3', 0)}",
             f"- Tier 4  (low activity skip):   {counts.get('4', 0)}",
             ""]

    # Tier 3 details
    tier3 = [(c, x) for c, t, x in all_classified if t == "3"]
    tier3.sort(key=lambda r: -(r[0]["total_msgs"]))
    lines.append("## Tier 3 — review (not in Contacts, ≥5 msgs both directions)")
    lines.append("")
    lines.append("To override: copy the YAML block under it into "
                 "`workspaces/<ws>/config/sources.yaml` under `sources.imessage.contacts` "
                 "(or `groups`).")
    lines.append("")
    for c, x in tier3[:200]:  # cap output
        kind = "group" if c["style"] == 43 else "1:1"
        dn = c["display_name"] or "(no display name)"
        first = fmt_mac_date(c["date_min"])
        last = fmt_mac_date(c["date_max"])
        handles = ", ".join(c["handles"][:5]) + ("..." if len(c["handles"]) > 5 else "")
        lines.append(f"### {kind}: {dn} — {c['total_msgs']} msgs ({c['my_msgs']} sent, {c['their_msgs']} recv) — {first} to {last}")
        lines.append(f"- handles: `{handles}`")
        if c["style"] == 43:
            lines.append(f"")
            lines.append(f"```yaml")
            lines.append(f"- slug: REVIEWED-NAME-HERE")
            lines.append(f"  chat_guid: {c['guid']}")
            lines.append(f"  full_archive: true")
            lines.append(f"```")
        else:
            lines.append(f"")
            lines.append(f"```yaml")
            lines.append(f"- slug: REVIEWED-NAME-HERE")
            lines.append(f"  handles: {c['handles']}")
            lines.append(f"  full_archive: true")
            lines.append(f"```")
        lines.append("")

    if len(tier3) > 200:
        lines.append(f"_truncated; {len(tier3) - 200} more Tier 3 chats not shown_")

    f.write_text("\n".join(lines) + "\n")
    return f


def merge_sources_yaml(cfg_path: Path, individuals: list[dict], groups: list[dict],
                       dry_run: bool):
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
    else:
        cfg = {}
    cfg.setdefault("sources", {})
    cfg["sources"].setdefault("imessage", {})
    imsg = cfg["sources"]["imessage"]
    existing_individuals = imsg.get("contacts") or []
    existing_groups = imsg.get("groups") or []

    # Dedupe by slug (preserve existing entries; only add new)
    existing_indiv_slugs = {c["slug"] for c in existing_individuals}
    existing_group_slugs = {g["slug"] for g in existing_groups}

    new_indivs = [c for c in individuals if c["slug"] not in existing_indiv_slugs]
    new_groups = [g for g in groups if g["slug"] not in existing_group_slugs]

    imsg["contacts"] = existing_individuals + new_indivs
    imsg["groups"] = existing_groups + new_groups

    if dry_run:
        return new_indivs, new_groups

    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False))
    return new_indivs, new_groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--dry-run", action="store_true",
                    help="don't write sources.yaml, only the report")
    args = ap.parse_args()

    ws_root = ULTRON_ROOT / "workspaces" / args.workspace
    cfg_path = ws_root / "config" / "sources.yaml"

    print(f"loading Apple Contacts...")
    phones, emails, total_contacts = load_contacts()
    if total_contacts == 0:
        sys.exit("ERROR: zero Apple Contacts loaded. Verify Contacts permission.")
    print(f"  {total_contacts} contacts: {len(phones)} unique phones, {len(emails)} unique emails")

    print(f"opening chat.db read-only...")
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    print(f"scanning chats...")
    chats = scan_chats(conn)
    print(f"  {len(chats)} total chats")

    print(f"classifying...")
    classified = []
    for chat in chats:
        tier, extras = classify(chat, phones, emails)
        classified.append((chat, tier, extras))

    counts = Counter(t for _, t, _ in classified)
    msgs_by_tier = Counter()
    for c, t, _ in classified:
        msgs_by_tier[t] += c["total_msgs"]

    # Build tier-1 entries
    used_slugs = set()
    individuals_entries = []
    groups_entries = []
    for chat, tier, extras in classified:
        if tier == "1I":
            name = extras["matched"][0][1] if extras["matched"] else None
            individuals_entries.append(
                build_individual_entry(chat, name, used_slugs))
        elif tier == "1G":
            groups_entries.append(
                build_group_entry(chat, phones, emails, used_slugs))

    # Merge into sources.yaml
    new_indiv, new_group = merge_sources_yaml(cfg_path, individuals_entries, groups_entries,
                                              dry_run=args.dry_run)

    # Write report
    run_id = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    report_dir = ULTRON_ROOT / "_shell" / "runs" / f"triage-imessage-{run_id}"
    report_path = write_review(report_dir, classified, phones, emails)

    print()
    print("==== TRIAGE SUMMARY ====")
    for tier, label in [
        ("1I", "Tier 1I (1:1 in Contacts, auto-allowlist)"),
        ("1G", "Tier 1G (group ≥1 in Contacts, auto-allowlist)"),
        ("2",  "Tier 2  (blocklist, skip)"),
        ("3",  "Tier 3  (review)"),
        ("4",  "Tier 4  (low activity, skip)"),
    ]:
        print(f"  {label:<54} {counts.get(tier,0):>5} chats / {msgs_by_tier.get(tier,0):>7,} msgs")
    print()
    print(f"sources.yaml: {len(new_indiv)} new individuals, {len(new_group)} new groups appended")
    print(f"  ({'dry-run, no file written' if args.dry_run else cfg_path})")
    print(f"review report: {report_path}")

    conn.close()


if __name__ == "__main__":
    main()
