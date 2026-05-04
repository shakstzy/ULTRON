#!/usr/bin/env python3
"""
check-frontmatter.py — validate the universal frontmatter envelope on every raw file.

Every file in `workspaces/<ws>/raw/<source>/...` MUST carry these YAML keys:
    source, workspace, ingested_at, ingest_version, content_hash, provider_modified_at

Manual sources (where the dropped artifact may be a PDF / image / CSV) are
exempt from the body-frontmatter requirement; their universal envelope is
expected in the workspace's `_meta/ingested.jsonl` row instead. This script
flags non-manual files only.

Usage:
    check-frontmatter.py [--workspace <ws>] [--output <path>]

Exit codes:
    0 — all envelopes present
    1 — at least one file is missing required keys
    2 — invocation error
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))

REQUIRED_KEYS = {
    "source",
    "workspace",
    "ingested_at",
    "ingest_version",
    "content_hash",
    "provider_modified_at",
}

# Sources whose body files are not required to carry the envelope (the row in
# ingested.jsonl carries it instead).
EXEMPT_SOURCES = {"manual", "apple-health", "plaid", "plaid-export"}

# Profile stubs are identity / metadata files, not data files. They have
# their own per-source frontmatter contract (see format.md Lock 7) and are
# exempt from the universal envelope.
EXEMPT_FILENAMES = {"_profile.md"}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.+?)\n---", re.DOTALL)
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:", re.MULTILINE)


def parse_frontmatter_keys(text: str) -> set[str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return set()
    block = m.group(1)
    return {match.group(1) for match in KEY_RE.finditer(block)}


def file_source(p: Path) -> str | None:
    """Infer source from path: workspaces/<ws>/raw/<source>/...

    Returns None for files inside any `_<system-dir>/` segment under the
    source root (e.g. `raw/imessage/_profiles/`, `_attachments/`).
    Underscore-prefixed dirs are system metadata (identity stubs, attachment
    binaries) and don't carry the per-ingest universal envelope by design.
    """
    try:
        rel = p.relative_to(ULTRON_ROOT).parts
    except ValueError:
        return None
    if len(rel) < 4 or rel[0] != "workspaces" or rel[2] != "raw":
        return None
    for seg in rel[4:]:
        if seg.startswith("_"):
            return None
    return rel[3]


def find_violations(scope: Path) -> list[tuple[Path, set[str]]]:
    out: list[tuple[Path, set[str]]] = []
    for ws_dir in (scope.iterdir() if scope.is_dir() else []):
        if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
            continue
        raw_dir = ws_dir / "raw"
        if not raw_dir.exists():
            continue
        for p in raw_dir.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() != ".md":
                continue
            if p.name in EXEMPT_FILENAMES:
                continue
            src = file_source(p)
            if src is None or src in EXEMPT_SOURCES:
                continue
            try:
                text = p.read_text(errors="ignore")
            except OSError:
                continue
            keys = parse_frontmatter_keys(text)
            missing = REQUIRED_KEYS - keys
            if missing:
                out.append((p, missing))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace")
    ap.add_argument("--output")
    args = ap.parse_args()

    if args.workspace:
        scope = (ULTRON_ROOT / "workspaces" / args.workspace).parent  # walk all if no ws filter
        if args.workspace:
            target = ULTRON_ROOT / "workspaces" / args.workspace
            if not target.exists():
                sys.stderr.write(f"workspace not found: {args.workspace}\n")
                return 2
            # Limit to that workspace by passing its parent and filtering.
            tmp = type("X", (), {})()
            violations = []
            raw_dir = target / "raw"
            if raw_dir.exists():
                for p in raw_dir.rglob("*.md"):
                    if p.name in EXEMPT_FILENAMES:
                        continue
                    src = file_source(p)
                    if src is None or src in EXEMPT_SOURCES:
                        continue
                    try:
                        text = p.read_text(errors="ignore")
                    except OSError:
                        continue
                    missing = REQUIRED_KEYS - parse_frontmatter_keys(text)
                    if missing:
                        violations.append((p, missing))
        else:
            violations = find_violations(ULTRON_ROOT / "workspaces")
    else:
        violations = find_violations(ULTRON_ROOT / "workspaces")

    lines = []
    for p, missing in violations:
        try:
            rel = p.relative_to(ULTRON_ROOT)
        except ValueError:
            rel = p
        lines.append(f"{rel}\tmissing: {', '.join(sorted(missing))}")

    out = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(out + ("\n" if out else ""))
    elif out:
        print(out)

    if violations:
        sys.stderr.write(f"check-frontmatter: {len(violations)} file(s) missing universal envelope keys\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
