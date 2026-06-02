#!/usr/bin/env python3
"""
stage-wiki-build.py — synthesize wiki entity pages from raw/ via per-source
parallel sub-agents.

Architecture (per agent-learning 2026-05-12):
  - Partition by SOURCE FILE, not entity cohort. One sub-agent per source.
  - Every parallel worker gets the current global slug index as read-only
    context so duplicate slugs don't proliferate.
  - Follow with a deterministic Python post-pass for forward-link stitch
    and backlinks regen (replace-not-append for idempotency).

Per-stage rules:
  - Curator-owned fields (`read_status`, `delivered_at`, `delivery_count`,
    `bite_size_minutes`) are PRESERVED on update — never overwritten.
  - Wiki entity pages get `source_hash` carried over from raw so the
    next run can skip unchanged sources.

This script is the PLANNER. It builds a work list of source files needing
synthesis and emits per-worker briefs to stdout / a job manifest. The
spawning of actual sub-agents is done by the caller (a Claude session)
which reads the manifest and dispatches with the Agent tool.

When invoked WITHOUT the Agent tool available (e.g. CLI), the script can
optionally invoke `codex exec` per work item as a synthesis backend. That
path is gated by `--codex` so it never fires by accident.

Usage:
  stage-wiki-build.py                          # build the work list
  stage-wiki-build.py --book thoreau-walden    # scope to one book
  stage-wiki-build.py --since 2026-05-01       # only raw items ingested since
  stage-wiki-build.py --dry-run                # report planned work, no writes
  stage-wiki-build.py --emit-briefs <dir>      # write per-worker briefs
  stage-wiki-build.py --codex                  # synthesize inline via codex exec
  stage-wiki-build.py --post-pass-only         # skip synthesis, just stitch+backlinks
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import lib_common as L


# ---------------------------------------------------------------------------
# Discovery: enumerate raw items needing synthesis
# ---------------------------------------------------------------------------

# Maps raw source kind → (raw glob, wiki entity dir, wiki entity type slug)
WIKI_DIR_MAP = {
    "article":       ("articles/**/*.md",            "articles",         "article"),
    "paper":         ("papers/*.md",                  "papers",           "paper"),
    "youtube-video": ("youtube/**/*.md",              "youtube-videos",   "youtube-video"),
    "reel":          ("reels/**/*.md",                "reels",            "reel"),
    "book":          ("books/*/*/_full.md",           "books",            "book"),
    "chapter":       ("books/*/*/ch-*.md",            "chapters",         "chapter"),
}


def _wiki_path_for(kind: str, slug: str) -> Path:
    _, entity_dir, _ = WIKI_DIR_MAP[kind]
    return L.WIKI / "entities" / entity_dir / f"{slug}.md"


def _raw_kind(raw_path: Path) -> str | None:
    """Classify a raw file into one of the wiki entity kinds. Books are
    special: `_full.md` is the book itself, `ch-*.md` is a chapter."""
    rel = raw_path.relative_to(L.RAW)
    parts = rel.parts
    if not parts:
        return None
    root = parts[0]
    if root == "articles":
        return "article"
    if root == "papers":
        return "paper"
    if root == "youtube":
        return "youtube-video"
    if root == "reels":
        return "reel"
    if root == "books":
        if raw_path.name == "_full.md":
            return "book"
        if raw_path.name.startswith("ch-"):
            return "chapter"
    return None


def _iter_raw(book_filter: str | None, since: str | None) -> list[tuple[Path, str]]:
    """Return [(raw_path, kind), ...] sorted, filtered."""
    out: list[tuple[Path, str]] = []
    if not L.RAW.exists():
        return out
    cutoff: datetime.date | None = None
    if since:
        try:
            cutoff = datetime.date.fromisoformat(since)
        except ValueError:
            print(f"  ! invalid --since date: {since!r}", file=sys.stderr)
            sys.exit(2)
    for raw in L.RAW.rglob("*.md"):
        # Skip .orphans/ and other hidden dirs anywhere in the path
        if any(p.startswith(".") for p in raw.relative_to(L.RAW).parts):
            continue
        if raw.name == ".gitkeep":
            continue
        kind = _raw_kind(raw)
        if kind is None:
            continue
        if book_filter:
            # only files under a book dir matching the slug
            parts = raw.relative_to(L.RAW).parts
            if not (parts[:1] == ("books",) and len(parts) >= 4 and parts[2] == book_filter):
                continue
        fm, _ = L.read_md(raw)
        if cutoff:
            d = (fm.get("ingested_at") or "")[:10]
            try:
                if datetime.date.fromisoformat(d) < cutoff:
                    continue
            except (ValueError, TypeError):
                continue
        out.append((raw, kind))
    out.sort(key=lambda r: str(r[0]))
    return out


# ---------------------------------------------------------------------------
# Work-item construction (one per raw file)
# ---------------------------------------------------------------------------

def _needs_synthesis(raw_path: Path, wiki_path: Path, force: bool) -> tuple[bool, str]:
    """Return (needs_synth, reason). Synthesis is needed when no wiki page
    exists OR raw content_hash doesn't match wiki source_hash."""
    if force:
        return True, "forced"
    if not wiki_path.exists():
        return True, "new"
    raw_fm, _ = L.read_md(raw_path)
    wiki_fm, _ = L.read_md(wiki_path)
    if raw_fm.get("content_hash") != wiki_fm.get("source_hash"):
        return True, "content-hash-changed"
    return False, "up-to-date"


def _slug_for_raw(raw_path: Path, kind: str, raw_fm: dict) -> str:
    """Derive the wiki entity slug from a raw file. Chapters always get
    prefixed with the book slug so two books with the same chapter title
    don't collide in wiki/entities/chapters/."""
    if kind == "chapter":
        book_slug = raw_fm.get("book_slug") or raw_path.parent.name
        return f"{book_slug}__{raw_path.stem}"
    if raw_fm.get("slug"):
        return raw_fm["slug"]
    if kind == "book":
        return raw_path.parent.name
    return raw_path.stem


def build_work_list(book_filter: str | None, since: str | None,
                    force: bool) -> list[dict]:
    work: list[dict] = []
    for raw_path, kind in _iter_raw(book_filter, since):
        raw_fm, _ = L.read_md(raw_path)
        slug = _slug_for_raw(raw_path, kind, raw_fm)
        wiki_path = _wiki_path_for(kind, slug)
        needs, reason = _needs_synthesis(raw_path, wiki_path, force)
        if not needs:
            continue
        work.append({
            "kind": kind,
            "slug": slug,
            "raw_path": str(raw_path.relative_to(L.WORKSPACE)),
            "wiki_path": str(wiki_path.relative_to(L.WORKSPACE)),
            "reason": reason,
        })
    return work


# ---------------------------------------------------------------------------
# Slug index (global) — readonly context for every sub-agent
# ---------------------------------------------------------------------------

def build_slug_index() -> list[str]:
    """Return `<path>/<slug> | <Title>` lines for every existing wiki entity.
    Per the parallel-ingest agent-learning, each sub-agent gets this as
    read-only context so they don't fabricate duplicate slugs."""
    out: list[str] = []
    ents = L.WIKI / "entities"
    if not ents.exists():
        return out
    for p in sorted(ents.rglob("*.md")):
        fm, _ = L.read_md(p)
        title = fm.get("title") or fm.get("canonical_name") or p.stem
        rel = p.relative_to(L.WIKI)
        out.append(f"{rel} | {title}")
    return out


# ---------------------------------------------------------------------------
# Per-worker brief
# ---------------------------------------------------------------------------

WORKER_BRIEF_TEMPLATE = """# Wiki synthesis task

You are one of N parallel workers building wiki entity pages from `raw/` for
the ULTRON `library` workspace. You handle EXACTLY ONE source file. Other
workers handle other files; do NOT touch anything outside your scope.

## Workspace context (read first)
- /Users/shakstzy/ULTRON/workspaces/library/CLAUDE.md
- /Users/shakstzy/ULTRON/workspaces/library/schema.md
- /Users/shakstzy/ULTRON/workspaces/library/identity.md
- /Users/shakstzy/ULTRON/workspaces/library/style.md
- /Users/shakstzy/ULTRON/workspaces/library/nomenclature.md
- /Users/shakstzy/ULTRON/workspaces/library/learnings.md
- /Users/shakstzy/ULTRON/workspaces/library/agents/wiki-agent.md (the canonical agent prompt)

## Your scope
- Source kind: **{kind}**
- Source slug: **{slug}**
- Read this raw file: `{raw_path}` (absolute: {raw_abs})
- Write this wiki entity page: `{wiki_path}` (absolute: {wiki_abs})

## Read-only slug index (do NOT invent new slugs that collide)
{slug_index_block}

## Per-type page format
Follow `schema.md` for your `{kind}` entity type EXACTLY. Required body sections in order:
  ## TL;DR        (1-3 sentences)
  ## Key takeaways  (3-7 bullets)
  ## Quote        (one ≤ 15 word quote with attribution; omit if nothing lands)
  ## Why it matters  (1-2 sentences)
  ## Connections (wikilinks to related entities, one per line)
  ## Backlinks   (leave empty — post-pass populates)

## Hard rules
1. Voice: per identity.md — internalized + scannable, not author-faithful, never academic.
2. Curator-owned fields (`read_status`, `delivered_at`, `delivery_count`,
   `bite_size_minutes`): if the wiki page ALREADY exists, PRESERVE these
   values from the existing frontmatter. Never overwrite.
3. Set `source_hash` in frontmatter = the raw file's `content_hash` field
   (copy verbatim). This is the change-detection key.
4. At most ONE direct quote per page, ≤ 15 words, attributed.
5. `mentioned_books: []`, `mentioned_concepts: []`, `tags: []` — populate
   when you see real mentions. Use existing slugs from the index when
   referencing other entities; otherwise leave empty.

## Output
Write the file at `{wiki_abs}`. Do NOT write anywhere else. Return a one-line
status: `OK <slug>` or `FAIL <slug>: <reason>`.
"""


def render_brief(item: dict, slug_index: list[str]) -> str:
    raw_abs = L.WORKSPACE / item["raw_path"]
    wiki_abs = L.WORKSPACE / item["wiki_path"]
    if len(slug_index) > 200:
        # Truncate for readability but say so
        idx_lines = slug_index[:200] + [f"... ({len(slug_index) - 200} more entries omitted)"]
    else:
        idx_lines = slug_index
    slug_index_block = "\n".join(idx_lines) if idx_lines else "(no existing wiki entities yet)"
    return WORKER_BRIEF_TEMPLATE.format(
        kind=item["kind"],
        slug=item["slug"],
        raw_path=item["raw_path"],
        raw_abs=raw_abs,
        wiki_path=item["wiki_path"],
        wiki_abs=wiki_abs,
        slug_index_block=slug_index_block,
    )


def emit_briefs(work: list[dict], out_dir: Path, slug_index: list[str]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, item in enumerate(work, 1):
        brief_path = out_dir / f"{i:04d}-{item['kind']}-{item['slug']}.md"
        brief_path.write_text(render_brief(item, slug_index), encoding="utf-8")
    manifest = {"work_count": len(work), "items": work,
                "slug_index_size": len(slug_index),
                "out_dir": str(out_dir), "emitted_at": L.iso_utc()}
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Codex backend (fallback when run from CLI without a Claude session)
# ---------------------------------------------------------------------------

def synthesize_via_codex(item: dict, slug_index: list[str], *,
                         workspace_root: Path) -> tuple[bool, str]:
    """Invoke `codex exec` to synthesize a single wiki entity page.
    Uses --output-last-message per the agent-learning so we get a parse-clean
    final assistant turn without session chrome."""
    brief = render_brief(item, slug_index)
    with tempfile.NamedTemporaryFile("w", suffix=".out", delete=False) as last:
        last_path = Path(last.name)
    try:
        proc = subprocess.run(
            ["codex", "exec", "--output-last-message", str(last_path),
             "--skip-git-repo-check", brief],
            capture_output=True, text=True, timeout=600, cwd=str(workspace_root),
        )
        if proc.returncode != 0:
            return False, f"codex rc={proc.returncode}: {proc.stderr.strip()[:200]}"
        # Check the file was actually written
        wiki_abs = L.WORKSPACE / item["wiki_path"]
        if not wiki_abs.exists():
            return False, "codex returned but wiki file not written"
        return True, "ok"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    finally:
        last_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Post-pass — forward-link stitch + backlinks regen (deterministic, idempotent)
# ---------------------------------------------------------------------------

_WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def _all_wiki_pages() -> list[Path]:
    ents = L.WIKI / "entities"
    if not ents.exists():
        return []
    return sorted(ents.rglob("*.md"))


def _slug_to_path() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for p in _all_wiki_pages():
        out[p.stem] = p
    return out


def _split_body_sections(body: str) -> list[tuple[str, str]]:
    """Return [(header, content), ...] preserving order. Pre-header content
    becomes ('', <content>)."""
    sections: list[tuple[str, str]] = []
    current_header = ""
    buf: list[str] = []
    for line in body.splitlines(keepends=True):
        m = re.match(r"^(##+ +.+?)\s*$", line.rstrip("\n"))
        if m:
            sections.append((current_header, "".join(buf)))
            current_header = m.group(1)
            buf = []
        else:
            buf.append(line)
    sections.append((current_header, "".join(buf)))
    return sections


def _set_section(body: str, header: str, content: str) -> str:
    sections = _split_body_sections(body)
    out: list[str] = []
    replaced = False
    for h, c in sections:
        if h == header:
            out.append(h + "\n")
            out.append(content if content.endswith("\n") else content + "\n")
            replaced = True
        else:
            if h:
                out.append(h + "\n")
            out.append(c)
    if not replaced:
        if out and not out[-1].endswith("\n\n"):
            out.append("\n")
        out.append(header + "\n")
        out.append(content if content.endswith("\n") else content + "\n")
    return "".join(out)


def post_pass_backlinks() -> dict:
    """Replace each page's `## Backlinks` section with the union of pages
    that link to its slug. Idempotent — re-running produces identical bytes."""
    pages = _all_wiki_pages()
    slug_to_path = _slug_to_path()
    referrers: dict[str, list[str]] = defaultdict(list)
    for p in pages:
        _, body = L.read_md(p)
        # Strip the existing Backlinks section out before scanning so we
        # don't recursively count old backlinks as forward links.
        for header, content in _split_body_sections(body):
            if header.lower().startswith("## backlinks"):
                continue
            for m in _WIKILINK_RE.finditer(content):
                target = m.group(1).strip().split("#")[0].strip()
                target = target.split("/")[-1]    # tolerate `path/slug` form
                if target == p.stem:
                    continue
                if target in slug_to_path:
                    referrers[target].append(p.stem)
    updated = 0
    for slug, link_set in referrers.items():
        target_path = slug_to_path[slug]
        fm, body = L.read_md(target_path)
        sorted_links = sorted(set(link_set))
        new_section = "\n" + "\n".join(f"- [[{s}]]" for s in sorted_links) + "\n"
        new_body = _set_section(body, "## Backlinks", new_section)
        if new_body != body:
            L.write_md(target_path, fm, new_body)
            updated += 1
    # Also clear backlinks on pages with NO referrers if they currently have any
    for p in pages:
        if p.stem in referrers:
            continue
        fm, body = L.read_md(p)
        if "## Backlinks" in body and re.search(r"## Backlinks\s*\n\s*-\s*\[\[", body):
            new_body = _set_section(body, "## Backlinks", "\n_(no backlinks yet)_\n")
            if new_body != body:
                L.write_md(p, fm, new_body)
                updated += 1
    return {"pages_scanned": len(pages), "pages_updated": updated,
            "referred_to_count": len(referrers)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", help="scope to a single book slug")
    ap.add_argument("--since", help="only raw items ingested on/after YYYY-MM-DD")
    ap.add_argument("--force", action="store_true",
                    help="re-synthesize even when source_hash matches")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--emit-briefs", type=Path,
                    help="write per-worker briefs to this dir + manifest.json")
    ap.add_argument("--codex", action="store_true",
                    help="synthesize inline via `codex exec` (one-by-one)")
    ap.add_argument("--post-pass-only", action="store_true",
                    help="skip discovery + synthesis; just run backlinks regen")
    args = ap.parse_args()

    if args.post_pass_only:
        rec = post_pass_backlinks()
        print(f"  post-pass: {rec}")
        return 0

    work = build_work_list(args.book, args.since, args.force)
    slug_index = build_slug_index()
    print(f"  found {len(work)} raw items needing synthesis "
          f"({len(slug_index)} existing wiki entities in index)")
    if not work:
        print("  nothing to do")
        return 0

    summary: dict[str, int] = {"total": len(work)}
    for item in work:
        summary[item["kind"]] = summary.get(item["kind"], 0) + 1
    print(f"  by kind: {summary}")

    if args.dry_run:
        for i, item in enumerate(work[:20], 1):
            print(f"    {i:3d}. [{item['kind']}] {item['slug']} ({item['reason']})")
        if len(work) > 20:
            print(f"    ... ({len(work) - 20} more)")
        return 0

    if args.emit_briefs:
        emit_briefs(work, args.emit_briefs, slug_index)
        print(f"  wrote {len(work)} briefs to {args.emit_briefs}")
        print(f"  manifest: {args.emit_briefs / 'manifest.json'}")
        return 0

    if args.codex:
        ok = 0
        failed = 0
        for i, item in enumerate(work, 1):
            print(f"[{i}/{len(work)}] codex: {item['kind']} {item['slug']}")
            success, msg = synthesize_via_codex(item, slug_index,
                                                workspace_root=L.WORKSPACE)
            if success:
                ok += 1
            else:
                failed += 1
                print(f"  ! failed: {msg}", file=sys.stderr)
        print(f"  synthesis summary: {ok} ok, {failed} failed (of {len(work)})")
        if ok:
            rec = post_pass_backlinks()
            print(f"  post-pass: {rec}")
        return 0 if failed == 0 else 1

    # No backend specified — instruct the user.
    print("  no backend specified. Options:")
    print("    --dry-run                  : list intended work")
    print("    --emit-briefs <dir>        : write per-worker briefs for parallel sub-agents")
    print("    --codex                    : synthesize inline via codex exec")
    print("  (a Claude session should use --emit-briefs <dir> and dispatch each brief"
          " via the Agent tool — one agent per source file.)")
    return 2


if __name__ == "__main__":
    sys.exit(main())
