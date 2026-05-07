#!/usr/bin/env python3
"""route-preview.py — given source / account / scope, print matched workspaces.

Useful for debugging "where would this email / file / message land?"

Usage:
    route-preview.py --source gmail   --account adithya@outerscope.xyz --scope label:Eclipse
    route-preview.py --source drive   --account adithya@outerscope.xyz --scope folder:INCLUSIVELAYER
    route-preview.py --source slack   --account T04472N6YUU            --scope channel:deals
    route-preview.py --source granola --account default                --scope folder:ECLIPSE
    route-preview.py --source imessage --account local                 --scope contact-set:dating

Matches use exact-string scope by default. With --substring, the scope is
treated as a search term: any matrix row whose `scope` cell contains the
provided string matches.

Outputs:
    Matched rows (line numbers from the matrix, scope, routes_to)
    Effective workspace(s) the item would land in
    TBD warnings if all matching rows are TBD
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def parse_matrix() -> list[dict]:
    p = ULTRON_ROOT / "_shell" / "docs" / "source-routing.md"
    if not p.exists():
        sys.stderr.write(f"missing: {p}\n")
        sys.exit(2)
    rows: list[dict] = []
    in_table = False
    for lineno, line in enumerate(p.read_text().splitlines(), 1):
        s = line.strip()
        if (
            s.startswith("|")
            and "source" in s
            and "account" in s
            and "scope" in s
            and "routes_to" in s
        ):
            in_table = True
            continue
        if in_table and s.startswith("|---"):
            continue
        if in_table and s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) >= 4:
                rows.append({
                    "lineno": lineno,
                    "source": cells[0],
                    "account": cells[1],
                    "scope": cells[2],
                    "routes_to": cells[3],
                    "exclude": cells[4] if len(cells) > 4 else "",
                    "notes": cells[5] if len(cells) > 5 else "",
                })
        elif in_table and (s.startswith("#") or s.startswith("```")):
            in_table = False
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True)
    ap.add_argument("--account", required=True)
    ap.add_argument("--scope", required=True)
    ap.add_argument(
        "--substring", action="store_true",
        help="Match scope as a substring instead of exact equality.",
    )
    args = ap.parse_args()

    rows = parse_matrix()
    matches: list[dict] = []
    for r in rows:
        if r["source"] != args.source:
            continue
        if r["account"] != args.account:
            continue
        if args.substring:
            if args.scope not in r["scope"]:
                continue
        else:
            if r["scope"] != args.scope:
                continue
        matches.append(r)

    print(f"\nQuery: source={args.source} account={args.account} scope={args.scope}")
    print(f"Matched rows: {len(matches)}\n")

    if not matches:
        print("(no matrix rows match — content would fall through to source's "
              "unrouted-default behavior)")
        return 0

    print(f"{'line':>4}  {'scope':<35}  {'routes_to':<25}  notes")
    print(f"{'----':>4}  {'-' * 35}  {'-' * 25}  {'-' * 30}")
    targets: set[str] = set()
    has_non_tbd = False
    for r in matches:
        is_tbd = "TBD" in r["routes_to"] or "TBD" in r["notes"]
        marker = "[TBD]" if is_tbd else "     "
        print(
            f"{r['lineno']:>4}  {r['scope'][:35]:<35}  "
            f"{r['routes_to'][:25]:<25}  {marker} {r['notes'][:50]}"
        )
        if not is_tbd:
            has_non_tbd = True
            for t in r["routes_to"].split(","):
                t = t.strip()
                if t and t not in {"per-workspace", "TBD"}:
                    targets.add(t)

    print()
    if not has_non_tbd:
        print("WARNING: every matching row is TBD. The ingest driver will SKIP "
              "this content until at least one row is filled in.")
        return 0

    print(f"Effective routing → {sorted(targets)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
