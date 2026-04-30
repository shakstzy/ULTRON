#!/usr/bin/env python3
"""
build-backlinks.py — refresh the ## Backlinks section in every global entity stub.

For each `_global/entities/<type>/<slug>.md`, scan all workspaces for matching
`wiki/entities/<*>/<slug>.md` pages and rewrite the stub's `## Backlinks`
section.

Usage:
    build-backlinks.py [--dry-run] [--workspace <ws>]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
BACKLINK_HEADER = "## Backlinks"
BACKLINK_AUTO_MARKER = "<!-- AUTO-GENERATED-BACKLINKS — do not edit manually -->"


def slug_from_filename(p: Path) -> str:
    return p.stem


def find_workspace_pages_for(slug: str) -> dict[str, Path]:
    """Return {workspace_name: workspace_page_path} for every workspace with a page on this slug."""
    out: dict[str, Path] = {}
    workspaces_dir = ULTRON_ROOT / "workspaces"
    if not workspaces_dir.exists():
        return out
    for ws_dir in sorted(workspaces_dir.iterdir()):
        if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
            continue
        entities_dir = ws_dir / "wiki" / "entities"
        if not entities_dir.exists():
            continue
        matches = sorted(entities_dir.rglob(f"{slug}.md"))
        if matches:
            out[ws_dir.name] = matches[0]
    return out


def extract_context_line(page: Path) -> str:
    """First non-frontmatter, non-header sentence — used as the one-line backlink description."""
    try:
        text = page.read_text(errors="ignore")
    except OSError:
        return "(unreadable)"
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("<!--"):
            continue
        snippet = line[:120].rstrip(".")
        return snippet + ("..." if len(line) > 120 else "")
    return "(no description)"


def regenerate_backlinks(stub: Path, dry_run: bool) -> bool:
    """Rewrite the ## Backlinks section in `stub`. Returns True if file content would change."""
    slug = slug_from_filename(stub)
    workspace_pages = find_workspace_pages_for(slug)

    new_lines = [BACKLINK_HEADER, "", BACKLINK_AUTO_MARKER, ""]
    if not workspace_pages:
        new_lines.append("- (no workspace pages reference this entity)")
    else:
        for ws, page in sorted(workspace_pages.items()):
            ctx = extract_context_line(page)
            new_lines.append(f"- [[ws:{ws}/{slug}]] — {ctx}")
    new_lines.append("")
    new_block = "\n".join(new_lines)

    text = stub.read_text(errors="ignore")
    if BACKLINK_HEADER in text:
        # Replace existing section through next H2 or EOF.
        pattern = re.compile(
            rf"{re.escape(BACKLINK_HEADER)}[\s\S]*?(?=\n## |\Z)",
            re.MULTILINE,
        )
        new_text = pattern.sub(new_block.rstrip() + "\n", text)
    else:
        new_text = text.rstrip() + "\n\n" + new_block

    if new_text != text:
        if not dry_run:
            stub.write_text(new_text)
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workspace", help="Limit which workspaces' pages we scan when finding backlinks.")
    args = ap.parse_args()

    global_dir = ULTRON_ROOT / "_global" / "entities"
    if not global_dir.exists():
        print(f"no global entities dir: {global_dir}", file=sys.stderr)
        return 0

    changed: list[Path] = []
    for stub in sorted(global_dir.rglob("*.md")):
        if regenerate_backlinks(stub, args.dry_run):
            changed.append(stub)

    label = "would update" if args.dry_run else "updated"
    print(f"{label}: {len(changed)} stubs")
    for s in changed:
        try:
            print(f"  {s.relative_to(ULTRON_ROOT)}")
        except ValueError:
            print(f"  {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
