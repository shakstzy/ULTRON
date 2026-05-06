#!/usr/bin/env python3
"""
sync.py — sync Apple Contacts → _global/entities/people/<slug>.md.

Skeleton: produces the AppleScript query, parses results, writes / updates
canonical stubs. Frontmatter is overwritten on every run; body is preserved
after first creation.

Usage:
    sync.py [--dry-run] [--limit N]

Skips when Contacts.app cannot be queried (e.g., automation permission denied).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
PEOPLE_DIR = ULTRON_ROOT / "_global" / "entities" / "people"

PLACEHOLDER_BODY = (
    "## Notes\n\n"
    "(populated by user / wiki agent)\n\n"
    "## Backlinks\n\n"
    "(rebuilt by build-backlinks.py)\n"
)


# ---- AppleScript bridge --------------------------------------------------

APPLESCRIPT = r"""
tell application "Contacts"
    set contactList to {}
    repeat with p in people
        set _name to ""
        try
            set _name to name of p
        end try
        set _emails to {}
        repeat with e in emails of p
            set _emails to _emails & {value of e}
        end repeat
        set _phones to {}
        repeat with ph in phones of p
            set _phones to _phones & {value of ph}
        end repeat
        set _modified to ""
        try
            set _modified to my isoDate(modification date of p)
        end try
        set entry to "{\"name\":\"" & my escape(_name) & "\",\"emails\":" & my listToJson(_emails) & ",\"phones\":" & my listToJson(_phones) & ",\"modified\":\"" & my escape(_modified) & "\"}"
        set contactList to contactList & {entry}
    end repeat
    set AppleScript's text item delimiters to linefeed
    set _out to contactList as string
    set AppleScript's text item delimiters to ""
    return _out
end tell

on isoDate(d)
    set y to year of d as string
    set m to (month of d as integer)
    set dd to day of d
    set hh to hours of d
    set mm to minutes of d
    set ss to seconds of d
    return y & "-" & my pad(m) & "-" & my pad(dd) & "T" & my pad(hh) & ":" & my pad(mm) & ":" & my pad(ss)
end isoDate

on pad(n)
    set s to n as string
    if (count of s) < 2 then set s to "0" & s
    return s
end pad

on escape(s)
    set s to my replaceText(s, "\\", "\\\\")
    set s to my replaceText(s, "\"", "\\\"")
    set s to my replaceText(s, return, " ")
    set s to my replaceText(s, linefeed, " ")
    return s
end escape

on replaceText(theText, find, repl)
    set AppleScript's text item delimiters to find
    set theTextItems to text items of theText
    set AppleScript's text item delimiters to repl
    set theText to theTextItems as string
    set AppleScript's text item delimiters to ""
    return theText
end replaceText

on listToJson(L)
    set out to "["
    set first to true
    repeat with item_ in L
        if not first then set out to out & ","
        set out to out & "\"" & my escape(item_ as string) & "\""
        set first to false
    end repeat
    set out to out & "]"
    return out
end listToJson
"""


def query_contacts() -> list[dict] | None:
    """Returns list of contact dicts or None on permission failure.

    Uses the macOS Contacts framework via pyobjc — same approach as
    `ingest-imessage-oneshot.py`. The previous AppleScript-based reader
    failed with a parser error on this machine.
    """
    try:
        from Contacts import (  # type: ignore
            CNContactStore, CNContactFetchRequest,
            CNContactGivenNameKey, CNContactFamilyNameKey,
            CNContactNicknameKey, CNContactOrganizationNameKey,
            CNContactPhoneNumbersKey, CNContactEmailAddressesKey,
        )
    except ImportError as e:
        sys.stderr.write(f"contacts-sync: Contacts framework unavailable: {e}\n")
        return None

    store = CNContactStore.alloc().init()
    keys = [CNContactGivenNameKey, CNContactFamilyNameKey, CNContactNicknameKey,
            CNContactOrganizationNameKey, CNContactPhoneNumbersKey,
            CNContactEmailAddressesKey]
    req = CNContactFetchRequest.alloc().initWithKeysToFetch_(keys)

    entries: list[dict] = []

    def cb(contact, stop):
        given = (contact.givenName() or "").strip()
        family = (contact.familyName() or "").strip()
        nick = (contact.nickname() or "").strip()
        org = (contact.organizationName() or "").strip()
        name = (given + " " + family).strip() or nick or org
        emails = []
        for e in contact.emailAddresses():
            v = str(e.value() or "").strip()
            if v:
                emails.append(v)
        phones = []
        for p in contact.phoneNumbers():
            v = (p.value().stringValue() or "").strip()
            if v:
                phones.append(v)
        if not name and not emails and not phones:
            return
        entries.append({
            "name": name,
            "emails": emails,
            "phones": phones,
            "modified": "",
        })

    try:
        store.enumerateContactsWithFetchRequest_error_usingBlock_(req, None, cb)
    except Exception as e:
        sys.stderr.write(f"contacts-sync: Contacts enumeration failed: {e}\n")
        return None

    return entries


# ---- Slug derivation -----------------------------------------------------

def kebab_ascii(s: str, max_len: int = 40) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip()).strip("-").lower()
    return s[:max_len].rstrip("-") or "unknown"


def _disambiguator(contact: dict) -> str:
    """Stable 4-hex-char tag derived from the contact's identifiers."""
    parts = [
        (contact.get("name") or "").strip().lower(),
        ",".join(sorted(e.lower() for e in (contact.get("emails") or []))),
        ",".join(sorted(re.sub(r"\D", "", p) for p in (contact.get("phones") or []))),
    ]
    raw = "|".join(parts).encode("utf-8")
    return hashlib.blake2b(raw, digest_size=2).hexdigest()


def derive_slug(contact: dict) -> str:
    name = (contact.get("name") or "").strip()
    if name:
        return kebab_ascii(name)
    emails = contact.get("emails") or []
    if emails:
        e = emails[0]
        if "@" in e:
            local, _, domain = e.partition("@")
            stem = domain.split(".", 1)[0]
            return kebab_ascii(f"{local}-{stem}")
    phones = contact.get("phones") or []
    if phones:
        digits = re.sub(r"\D", "", phones[0])
        return f"phone-{digits}"[:40]
    raw = json.dumps(contact, sort_keys=True).encode("utf-8")
    return f"unknown-{hashlib.blake2b(raw, digest_size=4).hexdigest()}"


# ---- Frontmatter shaping -------------------------------------------------

def render_frontmatter(contact: dict, slug: str) -> str:
    now = datetime.now(timezone.utc).isoformat()
    body_for_hash = json.dumps({
        "name": contact.get("name", ""),
        "emails": sorted(contact.get("emails") or []),
        "phones": sorted(contact.get("phones") or []),
    }, sort_keys=True).encode("utf-8")
    h = hashlib.blake2b(body_for_hash, digest_size=16).hexdigest()
    title = contact.get("name") or slug

    emails = contact.get("emails") or []
    phones = contact.get("phones") or []

    return (
        "---\n"
        "source: apple-contacts\n"
        "workspace: _global\n"
        f"ingested_at: {now}\n"
        "ingest_version: 1\n"
        f"content_hash: blake2b:{h}\n"
        f"provider_modified_at: {contact.get('modified') or now}\n"
        "\n"
        f"title: {title}\n"
        f"slug: {slug}\n"
        "type: person\n"
        f"canonical_uri: lifeos:_global/entities/people/{slug}\n"
        "aliases: []\n"
        "identifiers:\n"
        f"  email: {json.dumps(emails)}\n"
        f"  phone: {json.dumps(phones)}\n"
        "  slack: []\n"
        f"last_synced: {now}\n"
        "global: true\n"
        "---\n"
    )


FRONTMATTER_RE = re.compile(r"^---\s*\n.+?\n---\s*\n?", re.DOTALL)


def upsert(contact: dict, dry_run: bool) -> str:
    slug = contact.get("__slug_override") or derive_slug(contact)
    PEOPLE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PEOPLE_DIR / f"{slug}.md"
    new_fm = render_frontmatter(contact, slug)

    if out_path.exists():
        existing = out_path.read_text(errors="ignore")
        existing_body = FRONTMATTER_RE.sub("", existing, count=1) or PLACEHOLDER_BODY
        new_text = new_fm + "\n" + existing_body.lstrip("\n")
        if existing == new_text:
            return "unchanged"
        if not dry_run:
            out_path.write_text(new_text)
        return "updated"
    else:
        if not dry_run:
            out_path.write_text(new_fm + "\n# " + (contact.get("name") or slug) + "\n\n" + PLACEHOLDER_BODY)
        return "new"


# ---- main ----------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="Process at most N contacts (debugging).")
    args = ap.parse_args()

    contacts = query_contacts()
    if contacts is None:
        return 0   # best-effort: permission denied
    if args.limit:
        contacts = contacts[: args.limit]

    counts = {"new": 0, "updated": 0, "unchanged": 0}
    seen_slugs: dict[str, dict] = {}
    disambiguated: list[tuple[str, str, dict]] = []

    for c in contacts:
        slug = derive_slug(c)
        if slug in seen_slugs:
            tag = _disambiguator(c)
            new_slug = f"{slug}-{tag}"[:40]
            # extremely unlikely, but keep extending if even the disambig collides
            i = 1
            while new_slug in seen_slugs:
                new_slug = f"{slug}-{tag}-{i}"[:40]
                i += 1
            disambiguated.append((slug, new_slug, c))
            slug = new_slug
        seen_slugs[slug] = c
        c["__slug_override"] = slug
        counts[upsert(c, args.dry_run)] += 1

    sys.stderr.write(
        f"contacts-sync: {len(contacts)} total, "
        f"{counts['new']} new, {counts['updated']} updated, "
        f"{counts['unchanged']} unchanged, {len(disambiguated)} disambiguated\n"
    )
    for original, new_slug, c in disambiguated:
        sys.stderr.write(f"  collision: {original!r} → {new_slug!r} (name={c.get('name')!r})\n")

    if not args.dry_run:
        subprocess.run(
            [sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "build-backlinks.py")],
            check=False,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
