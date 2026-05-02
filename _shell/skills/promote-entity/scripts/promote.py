#!/usr/bin/env python3
"""
promote.py — promote a workspace entity to a global stub.

Usage:
    promote.py manual <type> <slug> [--dry-run]
    promote.py auto-promote [--force-medium] [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


FRONTMATTER_RE = re.compile(r"^---\s*\n(.+?)\n---\s*\n?", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    block = m.group(1)
    body = text[m.end():]
    try:
        fm = yaml.safe_load(block) or {}
    except yaml.YAMLError as exc:
        sys.stderr.write(f"promote: warning — failed to parse frontmatter ({exc}); treating as empty\n")
        fm = {}
    if not isinstance(fm, dict):
        fm = {}
    return fm, body


def serialize_frontmatter(fm: dict) -> str:
    body = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return f"---\n{body}---\n"


def find_source_pages(slug: str, type_: str | None) -> list[tuple[str, Path]]:
    """Return [(workspace_name, page_path), ...]."""
    out: list[tuple[str, Path]] = []
    workspaces_dir = ULTRON_ROOT / "workspaces"
    if not workspaces_dir.exists():
        return out
    for ws_dir in sorted(workspaces_dir.iterdir()):
        if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
            continue
        entities = ws_dir / "wiki" / "entities"
        if not entities.exists():
            continue
        if type_:
            cand = entities / type_ / f"{slug}.md"
            if cand.exists():
                out.append((ws_dir.name, cand))
        else:
            for p in entities.rglob(f"{slug}.md"):
                out.append((ws_dir.name, p))
    return out


def merge_content(sources: list[tuple[str, Path]]) -> tuple[str, list[str]]:
    """Return (merged_body, names_aliases_seen)."""
    bodies: list[tuple[str, str, dict]] = []
    aliases: set[str] = set()
    for ws, p in sources:
        text = p.read_text(errors="ignore")
        fm, body = parse_frontmatter(text)
        for k in ("aliases", "alias"):
            v = fm.get(k)
            if isinstance(v, list):
                for a in v:
                    if isinstance(a, str) and a.strip():
                        aliases.add(a.strip())
            elif isinstance(v, str) and v:
                for a in v.strip("[] ").split(","):
                    a = a.strip().strip('"').strip("'")
                    if a:
                        aliases.add(a)
        bodies.append((ws, body, fm))

    # Pick the longest non-trivial intro paragraph as the canonical lede.
    lede = ""
    for ws, body, _fm in bodies:
        cleaned = body.strip()
        if not cleaned:
            continue
        first_para = cleaned.split("\n\n", 1)[0]
        if len(first_para) > len(lede):
            lede = first_para

    out_lines = []
    if lede:
        out_lines.append(lede)
        out_lines.append("")

    for ws, body, _fm in bodies:
        cleaned = body.strip()
        if not cleaned:
            continue
        out_lines.append(f"### {ws.title()} context")
        # Strip auto-generated backlink sections; build-backlinks rebuilds.
        cleaned = re.sub(r"## Backlinks[\s\S]*", "", cleaned, flags=re.MULTILINE).rstrip()
        # Demote heading depth: top-level H1/H2 in workspace pages → H4 here.
        cleaned = re.sub(r"^(#{1,2}) ", "#### ", cleaned, flags=re.MULTILINE)
        out_lines.append(cleaned)
        out_lines.append("")

    out_lines.append("## Backlinks")
    out_lines.append("")
    out_lines.append("(rebuilt by build-backlinks.py)")
    out_lines.append("")
    return "\n".join(out_lines).rstrip() + "\n", sorted(aliases)


def annotate_source_pages(global_uri: str, sources: list[tuple[str, Path]], dry_run: bool) -> None:
    for ws, p in sources:
        text = p.read_text(errors="ignore")
        fm, body = parse_frontmatter(text)
        fm["global"] = "true"
        fm["canonical"] = global_uri
        new_text = serialize_frontmatter(fm) + body.lstrip("\n")
        if not dry_run:
            p.write_text(new_text)
        print(f"  annotated {p.relative_to(ULTRON_ROOT)}")


def write_global_stub(slug: str, type_: str, sources: list[tuple[str, Path]], aliases: list[str], merged: str, dry_run: bool) -> Path:
    canonical_name = slug.replace("-", " ").title()
    # Take canonical_name from the most-recently-touched source if available.
    most_recent = None
    for ws, p in sources:
        fm, _ = parse_frontmatter(p.read_text(errors="ignore"))
        cn = fm.get("canonical_name") or fm.get("title")
        if cn:
            canonical_name = str(cn)
            most_recent = p
            break

    fm = {
        "slug": slug,
        "type": type_,
        "canonical_name": canonical_name,
        "aliases": aliases or [],
        "last_updated": date.today().isoformat(),
        "global": "true",
        "sources": [
            {"workspace": ws, "page": str(p.relative_to(ULTRON_ROOT))}
            for ws, p in sources
        ],
    }

    out = ULTRON_ROOT / "_global" / "entities" / type_ / f"{slug}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    body = serialize_frontmatter(fm) + "\n# " + canonical_name + "\n\n" + merged
    if not dry_run:
        out.write_text(body)
    return out


def manual_promote(args: argparse.Namespace) -> int:
    sources = find_source_pages(args.slug, args.type)
    if not sources:
        sys.stderr.write(f"promote: no sources found for slug={args.slug}\n")
        return 1
    inferred_type = args.type or sources[0][1].parent.name
    print(f"Found {len(sources)} source page(s) for {inferred_type}/{args.slug}:")
    for ws, p in sources:
        print(f"  - {ws}: {p.relative_to(ULTRON_ROOT)}")

    merged, aliases = merge_content(sources)
    canonical_uri = f"lifeos:_global/entities/{inferred_type}/{args.slug}"
    out = write_global_stub(args.slug, inferred_type, sources, aliases, merged, args.dry_run)
    annotate_source_pages(canonical_uri, sources, args.dry_run)

    if not args.dry_run:
        subprocess.run([sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "build-backlinks.py")], check=False)
        rc = subprocess.run([sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "check-routes.py")], check=False).returncode
        if rc != 0:
            sys.stderr.write("promote: check-routes flagged broken links after promotion; review.\n")
            return rc
    print(f"\nPromoted to {out.relative_to(ULTRON_ROOT)}")
    return 0


def auto_promote(args: argparse.Namespace) -> int:
    src = ULTRON_ROOT / "_shell" / "audit" / "promotion-candidates.md"
    if not src.exists():
        sys.stderr.write(f"promote: no candidates file at {src}; run find-cross-workspace-slugs.py first\n")
        return 1
    rc = 0
    for line in src.read_text(errors="ignore").splitlines():
        if not line.startswith("|") or "slug" in line or "---" in line:
            continue
        parts = [c.strip() for c in line.strip("|").split("|")]
        if len(parts) < 5:
            continue
        slug, type_, _ws_list, confidence, action = parts[:5]
        if "/promote" not in action:
            continue
        if confidence != "high (exact)" and not args.force_medium:
            continue
        ns = argparse.Namespace(slug=slug, type=type_, dry_run=args.dry_run)
        if manual_promote(ns) != 0:
            rc = 1
    return rc


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("manual")
    m.add_argument("type")
    m.add_argument("slug")
    m.add_argument("--dry-run", action="store_true")

    a = sub.add_parser("auto-promote")
    a.add_argument("--force-medium", action="store_true")
    a.add_argument("--dry-run", action="store_true")

    args = ap.parse_args()

    if args.cmd == "manual":
        return manual_promote(args)
    if args.cmd == "auto-promote":
        return auto_promote(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
