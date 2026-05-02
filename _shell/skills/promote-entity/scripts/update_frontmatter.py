#!/usr/bin/env python3
"""
update_frontmatter.py — add `global: true` and `canonical: <uri>` to a workspace
entity page's frontmatter, idempotently.

Usage:
    update_frontmatter.py <page.md> --canonical lifeos:_global/entities/people/sydney
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.+?)\n---\s*\n?", re.DOTALL)


def patch(text: str, canonical: str) -> str:
    m = FRONTMATTER_RE.match(text)
    if not m:
        # No frontmatter: prepend a minimal one.
        return f"---\nglobal: true\ncanonical: {canonical}\n---\n\n{text}"
    block = m.group(1)
    body = text[m.end():]

    lines = [ln for ln in block.splitlines() if ln.rstrip()]
    keys = {ln.split(":", 1)[0].strip() for ln in lines if ":" in ln}

    if "global" not in keys:
        lines.append("global: true")
    else:
        lines = [
            ln if not ln.lstrip().startswith("global:") else "global: true"
            for ln in lines
        ]
    if "canonical" not in keys:
        lines.append(f"canonical: {canonical}")
    else:
        lines = [
            ln if not ln.lstrip().startswith("canonical:") else f"canonical: {canonical}"
            for ln in lines
        ]
    return "---\n" + "\n".join(lines) + "\n---\n" + body.lstrip("\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("page", type=Path)
    ap.add_argument("--canonical", required=True)
    args = ap.parse_args()
    if not args.page.exists():
        sys.stderr.write(f"not found: {args.page}\n")
        return 1
    new = patch(args.page.read_text(errors="ignore"), args.canonical)
    args.page.write_text(new)
    print(f"updated frontmatter: {args.page}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
