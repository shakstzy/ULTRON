#!/usr/bin/env python3
"""validate-routing.py — sanity-check _shell/docs/source-routing.md.

Checks:
1. Every (source, account, scope) tuple is unique.
2. Every workspace listed in `routes_to` exists at `workspaces/<slug>/`.
3. `routes_to` slugs are kebab-case lowercase.
4. Source type is one of the known set.
5. No row has empty source / account / scope / routes_to.
6. Account appears in `_credentials/accounts.yaml` for the given service
   (warning, not error — TBD accounts are allowed to be unknown).

Exit codes: 0 OK, 1 issues found, 2 missing matrix file.

Run from ULTRON root:
    python3 _shell/bin/validate-routing.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # accounts.yaml check skipped if pyyaml absent

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))

KNOWN_SOURCES = {
    "gmail", "drive", "slack", "granola", "fireflies",
    "imessage", "whatsapp", "manual",
}

SPECIAL_TARGETS = {"per-workspace", "TBD", ""}


def parse_matrix(path: Path) -> list[dict]:
    rows: list[dict] = []
    in_table = False
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
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


def load_known_workspaces() -> set[str]:
    return {
        p.name for p in (ULTRON_ROOT / "workspaces").iterdir()
        if p.is_dir() and not p.name.startswith("_")
    }


def load_accounts_registry() -> dict:
    p = ULTRON_ROOT / "_credentials" / "accounts.yaml"
    if not p.exists() or yaml is None:
        return {}
    return (yaml.safe_load(p.read_text()) or {}).get("accounts", {}) or {}


def main() -> int:
    matrix_path = ULTRON_ROOT / "_shell" / "docs" / "source-routing.md"
    if not matrix_path.exists():
        print(f"missing: {matrix_path}", file=sys.stderr)
        return 2

    rows = parse_matrix(matrix_path)
    workspaces = load_known_workspaces()
    accounts = load_accounts_registry()

    errors: list[str] = []
    warnings: list[str] = []

    # 1. Unique tuples.
    seen: dict[tuple, int] = {}
    for r in rows:
        key = (r["source"], r["account"], r["scope"])
        if key in seen:
            errors.append(
                f"line {r['lineno']}: duplicate of line {seen[key]}: {key}"
            )
        else:
            seen[key] = r["lineno"]

    # 2. Workspace existence + slug shape.
    for r in rows:
        targets = [t.strip() for t in r["routes_to"].split(",")]
        for t in targets:
            t_clean = re.sub(r"[()]", "", t).strip()
            if t_clean in SPECIAL_TARGETS:
                continue
            if not re.fullmatch(r"[a-z0-9-]+", t_clean):
                errors.append(
                    f"line {r['lineno']}: '{t_clean}' is not kebab-case lowercase"
                )
                continue
            if t_clean not in workspaces:
                errors.append(
                    f"line {r['lineno']}: routes_to references nonexistent "
                    f"workspace '{t_clean}'"
                )

    # 3. Source type known.
    for r in rows:
        if r["source"] and r["source"] not in KNOWN_SOURCES:
            errors.append(
                f"line {r['lineno']}: unknown source type '{r['source']}'. "
                f"Add to KNOWN_SOURCES if intentional."
            )

    # 4. Empty required cells.
    for r in rows:
        for k in ("source", "account", "scope", "routes_to"):
            if not r[k]:
                errors.append(f"line {r['lineno']}: empty {k}")

    # 5. Accounts registered (warn-only — TBD rows allowed to use unknown accounts).
    for r in rows:
        if "TBD" in r["account"] or r["source"] == "manual":
            continue
        if accounts and r["account"] not in accounts:
            warnings.append(
                f"line {r['lineno']}: account '{r['account']}' not in "
                f"_credentials/accounts.yaml"
            )

    # Output.
    if warnings:
        print(f"WARN: {len(warnings)} warning(s):")
        for w in warnings:
            print(f"  {w}")
        print()

    if errors:
        print(f"FAIL: {len(errors)} issue(s) in source-routing.md:")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"OK: {len(rows)} rows, no errors{f' ({len(warnings)} warnings)' if warnings else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
