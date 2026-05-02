#!/usr/bin/env python3
"""
merge_content.py — body-merge helper for promote-entity.

Standalone usage (rare; the main promote.py does its own merge):
    merge_content.py <ws-page-1.md> <ws-page-2.md> ...

Prints the merged body to stdout. Same algorithm as promote.py:
- Pick the longest non-trivial intro paragraph as the lede.
- Per-workspace ### headers wrap each workspace's body.
- Strip auto-generated ## Backlinks sections.
- Demote H1/H2 within workspace bodies to H4.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.+?)\n---\s*\n?", re.DOTALL)


def split_frontmatter(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return text[m.end():] if m else text


def merge(paths: list[Path]) -> str:
    bodies: list[tuple[str, str]] = []
    for p in paths:
        ws = p.parts[-5] if len(p.parts) >= 5 else p.stem
        body = split_frontmatter(p.read_text(errors="ignore")).strip()
        bodies.append((ws, body))

    lede = ""
    for _ws, body in bodies:
        if not body:
            continue
        first = body.split("\n\n", 1)[0]
        if len(first) > len(lede):
            lede = first

    out: list[str] = []
    if lede:
        out.append(lede)
        out.append("")

    for ws, body in bodies:
        if not body:
            continue
        out.append(f"### {ws.title()} context")
        body = re.sub(r"## Backlinks[\s\S]*", "", body, flags=re.MULTILINE).rstrip()
        body = re.sub(r"^(#{1,2}) ", "#### ", body, flags=re.MULTILINE)
        out.append(body)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("usage: merge_content.py <ws-page>...\n")
        sys.exit(2)
    paths = [Path(p) for p in sys.argv[1:]]
    print(merge(paths))
