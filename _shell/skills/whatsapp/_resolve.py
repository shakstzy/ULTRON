"""
_resolve.py — canonical group-slug ↔ JID resolution for the WhatsApp skill.

MUST stay in lock-step with the collision-resolution algorithm in
`_shell/bin/ingest-whatsapp.py` (`resolve_chat_identity` + the slug-collision
pre-pass in `main`). Round 3 review surfaced that send.sh and read.sh had
diverged: each had a partial / first-come-first-serve fallback while ingest
ran a strict two-pass (last-4 first; sha256 prefix on still-duplicates).
This module is the single source of truth. send.sh and read.sh import
`resolve_group_by_slug()` and never re-implement the algorithm inline.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
from collections import defaultdict


def kebab(s: str) -> str:
    """Mirrors ingest's slugify(): lowercase, alnum + hyphen only."""
    s = re.sub(r"[^\w\s-]", "", (s or "").lower())
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown"


def _last4(jid: str) -> str:
    digits = re.sub(r"\D", "", jid.split("@", 1)[0])
    return digits[-4:] if len(digits) >= 4 else (digits or "x")


def group_slug_map(bridge_db_path: str) -> dict[str, str]:
    """Return {jid: resolved_slug} for every @g.us chat, with collision-resolved slugs.

    Algorithm (must match ingest-whatsapp.py exactly):
      1. Compute base slug = kebab(chat.name) for every group jid.
      2. For each base slug shared by 2+ jids, append `-<last4-of-jid-digits>`.
      3. If any post-suffix slug is STILL not unique within the cluster, escalate
         every duplicated jid in that cluster to `-<sha256(jid)[:8]>`.
      4. Solo jids keep their base slug.

    The resulting map is 1:1 — every jid has exactly one slug, every slug points
    at exactly one jid.
    """
    con = sqlite3.connect(f"file:{bridge_db_path}?mode=ro", uri=True)
    rows = list(con.execute("SELECT jid, name FROM chats WHERE jid LIKE \"%@g.us\"").fetchall())
    con.close()

    base = {jid: kebab(name) for jid, name in rows}
    buckets: dict[str, list[str]] = defaultdict(list)
    for jid, b in base.items():
        buckets[b].append(jid)

    out: dict[str, str] = {}
    for b, jids in buckets.items():
        if len(jids) <= 1:
            out[jids[0]] = b
            continue

        # First pass: last-4 disambiguator on ALL members (parity with ingest).
        first_pass = {jid: f"{b}-{_last4(jid)}" for jid in jids}

        # Second pass: if any first-pass slug is still duplicated within this
        # cluster, escalate every duplicated jid in the cluster to sha256 prefix.
        counts: dict[str, int] = defaultdict(int)
        for jid in jids:
            counts[first_pass[jid]] += 1
        for jid in jids:
            if counts[first_pass[jid]] > 1:
                first_pass[jid] = f"{b}-{hashlib.sha256(jid.encode()).hexdigest()[:8]}"
        out.update(first_pass)

    return out


def resolve_group_by_slug(bridge_db_path: str, user_slug: str) -> list[str]:
    """Return JIDs whose collision-resolved slug equals `user_slug`.

    Empty list = no match. Length >1 = ambiguous (should be unreachable since
    `group_slug_map()` produces a 1:1 mapping; defensive check anyway).

    Caller-provided `user_slug` is whatever the user typed:
      - a base slug (matches if no collision occurred for that name)
      - a collision-resolved slug (`<base>-<4digits>` or `<base>-<8hex>`)
    """
    if not user_slug:
        return []
    user_slug = user_slug.strip()
    slug_map = group_slug_map(bridge_db_path)
    return [jid for jid, slug in slug_map.items() if slug == user_slug]


if __name__ == "__main__":
    # CLI entrypoint used by send.sh and read.sh — keeps shell glue minimal.
    import argparse
    import json
    import sys

    p = argparse.ArgumentParser(description="Resolve a group slug to a JID.")
    p.add_argument("--db", required=True, help="Path to bridge messages.db")
    p.add_argument("--slug", help="Slug to resolve (omit to dump full slug→jid map as JSON)")
    args = p.parse_args()

    if args.slug:
        matches = resolve_group_by_slug(args.db, args.slug)
        print("|".join(matches))
        sys.exit(0)
    print(json.dumps({jid: slug for jid, slug in group_slug_map(args.db).items()}, indent=2))
