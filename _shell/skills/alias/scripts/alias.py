#!/usr/bin/env python3
"""
alias.py — merge slugs into a canonical slug.

Usage:
    alias.py merge <slug-a> <slug-b> [<slug-n>...] --canonical <slug-or-auto> [--type <type>] [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


FRONTMATTER_RE = re.compile(r"^---\s*\n(.+?)\n---\s*\n?", re.DOTALL)


def parse_fm(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith(("-", " ", "\t")):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, text[m.end():]


def find_pages(slug: str, type_: str | None) -> list[Path]:
    out: list[Path] = []
    workspaces_dir = ULTRON_ROOT / "workspaces"
    if workspaces_dir.exists():
        for ws_dir in sorted(workspaces_dir.iterdir()):
            if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
                continue
            entities = ws_dir / "wiki" / "entities"
            if not entities.exists():
                continue
            if type_:
                cand = entities / type_ / f"{slug}.md"
                if cand.exists():
                    out.append(cand)
            else:
                for p in entities.rglob(f"{slug}.md"):
                    out.append(p)
    global_dir = ULTRON_ROOT / "_global" / "entities"
    if global_dir.exists():
        if type_:
            cand = global_dir / type_ / f"{slug}.md"
            if cand.exists():
                out.append(cand)
        else:
            for p in global_dir.rglob(f"{slug}.md"):
                out.append(p)
    return out


def detect_canonical(slugs: list[str], type_: str | None) -> str:
    """Heuristic: longest slug wins; tie-broken by most-recent last_touched."""
    best = slugs[0]
    best_len = len(best)
    best_touched = ""
    for s in slugs:
        pages = find_pages(s, type_)
        last = ""
        for p in pages:
            fm, _ = parse_fm(p.read_text(errors="ignore"))
            t = fm.get("last_touched") or fm.get("last_updated") or ""
            if t > last:
                last = t
        if len(s) > best_len or (len(s) == best_len and last > best_touched):
            best, best_len, best_touched = s, len(s), last
    return best


def render_redirect_stub(alias: str, canonical: str, type_: str) -> str:
    today = date.today().isoformat()
    return (
        f"---\n"
        f"slug: {alias}\n"
        f"type: {type_}\n"
        f"canonical: lifeos:_global/entities/{type_}/{canonical}\n"
        f"redirect_to: {canonical}\n"
        f"aliased_at: {today}\n"
        f"---\n\n"
        f"This entity was merged into [[{canonical}]] on {today}. Wikilinks "
        f"to this slug still resolve here for history but should be rewritten "
        f"to point at the canonical slug.\n"
    )


def merge_alias_content_into_canonical(alias_page: Path, canonical_page: Path, alias_slug: str) -> None:
    if not canonical_page.exists():
        return
    alias_text = alias_page.read_text(errors="ignore")
    _fm, alias_body = parse_fm(alias_text)
    alias_body = alias_body.strip()
    if not alias_body:
        return
    # Strip auto-generated backlinks; rebuild later.
    alias_body = re.sub(r"## Backlinks[\s\S]*", "", alias_body, flags=re.MULTILINE).rstrip()
    if not alias_body:
        return

    canonical_text = canonical_page.read_text(errors="ignore")
    insertion = f"\n\n### From `{alias_slug}` (merged)\n\n{alias_body}\n"
    canonical_page.write_text(canonical_text.rstrip() + insertion + "\n")


def update_canonical_aliases(canonical_page: Path, aliases: list[str]) -> None:
    if not canonical_page.exists():
        return
    text = canonical_page.read_text(errors="ignore")
    fm, body = parse_fm(text)
    existing = fm.get("aliases", "")
    existing_set = {a.strip() for a in re.split(r"[,\[\]]", existing) if a.strip()}
    merged = sorted(existing_set | set(aliases))
    fm["aliases"] = "[" + ", ".join(merged) + "]"
    out_lines = ["---"]
    for k, v in fm.items():
        out_lines.append(f"{k}: {v}")
    out_lines.append("---")
    canonical_page.write_text("\n".join(out_lines) + "\n" + body.lstrip("\n"))


def merge(slugs: list[str], canonical: str, type_: str | None, dry_run: bool) -> int:
    aliases = [s for s in slugs if s != canonical]
    if not aliases:
        print("alias: nothing to merge (all slugs are the canonical)")
        return 0

    canonical_pages = find_pages(canonical, type_)
    if not canonical_pages:
        sys.stderr.write(f"alias: canonical slug {canonical} has no pages — promote one of the aliases first or pick a different canonical\n")
        return 2

    inferred_type = type_ or canonical_pages[0].parent.name
    canonical_page_global = ULTRON_ROOT / "_global" / "entities" / inferred_type / f"{canonical}.md"

    print(f"Canonical: {canonical} ({inferred_type})")
    print(f"Aliases:   {', '.join(aliases)}")
    print(f"Pages affected:")
    for p in canonical_pages:
        print(f"  canonical: {p.relative_to(ULTRON_ROOT)}")

    for alias in aliases:
        alias_pages = find_pages(alias, inferred_type)
        if not alias_pages:
            print(f"  alias {alias}: no pages")
            continue
        for alias_page in alias_pages:
            print(f"  alias {alias}: {alias_page.relative_to(ULTRON_ROOT)}")
            # Find the matching canonical page in the same workspace (or global) to fold content into.
            target = None
            for cp in canonical_pages:
                if str(cp.parent.parent) == str(alias_page.parent.parent):
                    target = cp
                    break
            if target is None and canonical_page_global.exists():
                target = canonical_page_global
            if not dry_run:
                if target is not None:
                    merge_alias_content_into_canonical(alias_page, target, alias)
                alias_page.write_text(render_redirect_stub(alias, canonical, inferred_type))
            # Rewrite wikilinks across the workspace (or globally if alias was global).
            try:
                ws = alias_page.relative_to(ULTRON_ROOT / "workspaces").parts[0]
                rewrite_args = [sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "rename-slug.py"),
                                alias, canonical, "--workspace", ws]
            except ValueError:
                rewrite_args = [sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "rename-slug.py"),
                                alias, canonical]
            if not dry_run:
                subprocess.run(rewrite_args, check=False)

    if not dry_run:
        for cp in canonical_pages:
            update_canonical_aliases(cp, aliases)
        subprocess.run([sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "build-backlinks.py")], check=False)
        rc = subprocess.run([sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "check-routes.py")], check=False).returncode
        if rc != 0:
            sys.stderr.write("alias: check-routes flagged broken links after merge.\n")
            return rc
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge")
    m.add_argument("slugs", nargs="+")
    m.add_argument("--canonical", required=True)
    m.add_argument("--type")
    m.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cmd != "merge":
        return 2
    canonical = args.canonical
    if canonical == "auto":
        canonical = detect_canonical(args.slugs, args.type)
        print(f"Detected canonical: {canonical}")
    elif canonical not in args.slugs:
        sys.stderr.write(f"alias: --canonical {canonical} must be one of {args.slugs}\n")
        return 2
    return merge(args.slugs, canonical, args.type, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
