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
            set _modified to (modification date of p) as string
        end try
        set entry to "{\"name\":\"" & my escape(_name) & "\",\"emails\":" & my listToJson(_emails) & ",\"phones\":" & my listToJson(_phones) & ",\"modified\":\"" & my escape(_modified) & "\"}"
        set contactList to contactList & {entry}
    end repeat
    return contactList as string
end tell

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
    """Returns list of contact dicts or None on permission failure."""
    try:
        result = subprocess.run(
            ["osascript", "-e", APPLESCRIPT],
            capture_output=True, text=True, timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        sys.stderr.write(f"contacts-sync: osascript unavailable: {e}\n")
        return None

    if result.returncode != 0:
        sys.stderr.write(f"contacts-sync: osascript failed: {result.stderr.strip()}\n")
        return None

    out = result.stdout.strip()
    if not out:
        return []

    # The AppleScript joins entries with ", " but each entry is JSON-shaped.
    # Split on },\s*{ boundaries (tolerant).
    entries: list[dict] = []
    raw_pieces = re.split(r"(?<=\}),\s*(?=\{)", out)
    for piece in raw_pieces:
        piece = piece.strip()
        if not piece:
            continue
        try:
            entries.append(json.loads(piece))
        except json.JSONDecodeError:
            sys.stderr.write(f"contacts-sync: failed to parse contact entry: {piece[:80]}\n")
    return entries


# ---- Slug derivation -----------------------------------------------------

def kebab_ascii(s: str, max_len: int = 40) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip()).strip("-").lower()
    return s[:max_len].rstrip("-") or "unknown"


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
    slug = derive_slug(contact)
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
    conflicts: list[tuple[str, dict, dict]] = []

    for c in contacts:
        slug = derive_slug(c)
        if slug in seen_slugs:
            conflicts.append((slug, seen_slugs[slug], c))
            continue
        seen_slugs[slug] = c
        counts[upsert(c, args.dry_run)] += 1

    sys.stderr.write(
        f"contacts-sync: {len(contacts)} total, "
        f"{counts['new']} new, {counts['updated']} updated, "
        f"{counts['unchanged']} unchanged, {len(conflicts)} conflicts\n"
    )
    for slug, a, b in conflicts:
        sys.stderr.write(f"  conflict: slug={slug} a={a.get('name')} b={b.get('name')}\n")

    if not args.dry_run:
        subprocess.run(
            [sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "build-backlinks.py")],
            check=False,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
