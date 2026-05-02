#!/usr/bin/env python3
"""
rename-slug.py — atomically rename an entity slug across ULTRON.

Usage:
    rename-slug.py <old> <new> [--type <type>] [--workspace <ws>]

Behavior:
- If both --type and --workspace are given, moves
    workspaces/<ws>/wiki/entities/<type>/<old>.md → <new>.md
- If only --type, moves the global stub
    _global/entities/<type>/<old>.md → <new>.md
- Then rewrites every wikilink that targets the old slug across the appropriate
  scope, including:
    [[old]]                          → [[new]]
    [[@old]]                         → [[@new]]
    [[old|label]]                    → [[new|label]]
    ![[old]]                         → ![[new]]
    [[ws:any/old]]                   → [[ws:any/new]]
    [[ws:any/entities/<type>/old]]   → [[ws:any/entities/<type>/new]]
- Refuses to overwrite an existing destination file.
- Rebuilds backlinks and runs check-routes after.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))

WIKILINK_RE = re.compile(r"(!?)\[\[([^\]]+)\]\]")

SKIP_PATH_FRAGMENTS = (
    "/_shell/runs/",
    "/_credentials/",
    "/.git/",
    "/_template/",
)


def should_skip(p: Path) -> bool:
    s = str(p)
    return any(frag in s for frag in SKIP_PATH_FRAGMENTS)


def rewrite_target(target: str, old: str, new: str) -> str:
    """Rewrite a wikilink target slug-aware. Preserves @, ws: prefixes and trailing path segments."""
    # Strip display label for matching; preserve it on output.
    if "|" in target:
        ref, label = target.split("|", 1)
    else:
        ref, label = target, None

    rewritten_ref = ref

    if ref == old:
        rewritten_ref = new
    elif ref == f"@{old}":
        rewritten_ref = f"@{new}"
    elif ref.startswith("ws:"):
        rest = ref[3:]
        if "/" in rest:
            ws_part, slug_part = rest.split("/", 1)
            # slug_part may be 'old', 'old|...', 'entities/people/old', etc.
            if slug_part == old:
                rewritten_ref = f"ws:{ws_part}/{new}"
            elif slug_part.endswith(f"/{old}"):
                rewritten_ref = f"ws:{ws_part}/{slug_part[: -len(old)]}{new}"
        # bare ws:foo (no slug part) → no change.
    # Other prefixes (concept:, synthesis:, raw:) intentionally untouched —
    # those identify pages by full file path / topic, not slug.

    if label is None:
        return rewritten_ref
    return f"{rewritten_ref}|{label}"


FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)+?\1", re.DOTALL)


def patch_text(text: str, old: str, new: str) -> str:
    """Return the rewritten text. Skips fenced code blocks and inline code spans."""
    out: list[str] = []
    in_fence = False
    fence_marker: str | None = None
    for raw_line in text.splitlines(keepends=True):
        stripped = raw_line.rstrip("\n")
        m_fence = FENCE_RE.match(stripped)
        if m_fence is not None:
            tok = m_fence.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_marker = tok
            elif fence_marker == tok:
                in_fence = False
                fence_marker = None
            out.append(raw_line)
            continue
        if in_fence:
            out.append(raw_line)
            continue

        # Mask inline code spans, rewrite outside, restore.
        masks: list[str] = []

        def mask(match: re.Match) -> str:
            masks.append(match.group(0))
            return f"\x00{len(masks) - 1}\x00"

        masked = INLINE_CODE_RE.sub(mask, raw_line)

        def repl(m: re.Match) -> str:
            bang = m.group(1)
            target = m.group(2)
            return f"{bang}[[{rewrite_target(target, old, new)}]]"

        rewritten = WIKILINK_RE.sub(repl, masked)
        for idx, original in enumerate(masks):
            rewritten = rewritten.replace(f"\x00{idx}\x00", original)
        out.append(rewritten)
    return "".join(out)


def patch_file(p: Path, old: str, new: str, dry_run: bool = False) -> bool:
    """Returns True if the file content changed (or would change in dry-run)."""
    try:
        text = p.read_text(errors="ignore")
    except OSError:
        return False

    new_text = patch_text(text, old, new)
    if new_text != text:
        if not dry_run:
            p.write_text(new_text)
        return True
    return False


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--type", dest="type_")
    ap.add_argument("--workspace")
    ap.add_argument("--dry-run", action="store_true", help="Print what would change without applying.")
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    if args.old == args.new:
        sys.stderr.write("rename-slug: old == new; nothing to do\n")
        return 0

    # 1. Move the canonical file, refusing to overwrite.
    if args.type_ and args.workspace:
        src = ULTRON_ROOT / "workspaces" / args.workspace / "wiki" / "entities" / args.type_ / f"{args.old}.md"
        dst = ULTRON_ROOT / "workspaces" / args.workspace / "wiki" / "entities" / args.type_ / f"{args.new}.md"
    elif args.type_:
        src = ULTRON_ROOT / "_global" / "entities" / args.type_ / f"{args.old}.md"
        dst = ULTRON_ROOT / "_global" / "entities" / args.type_ / f"{args.new}.md"
    else:
        src = None
        dst = None

    if src is not None and src.exists():
        if dst is None:
            sys.stderr.write("rename-slug: internal error — dst not set\n")
            return 2
        if dst.exists():
            sys.stderr.write(f"rename-slug: destination already exists: {dst}\n")
            return 2
        if args.dry_run:
            print(f"[dry-run] would move: {src} → {dst}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dst)
            print(f"moved: {src} → {dst}")
    elif src is not None:
        sys.stderr.write(f"rename-slug: source not found: {src} (only patching wikilinks)\n")

    # 2. Patch wikilinks across the scope.
    if args.workspace:
        scope_dir = ULTRON_ROOT / "workspaces" / args.workspace
    else:
        scope_dir = ULTRON_ROOT

    patched: list[Path] = []
    for md in scope_dir.rglob("*.md"):
        if should_skip(md):
            continue
        if patch_file(md, args.old, args.new, dry_run=args.dry_run):
            patched.append(md)
    label = "would patch" if args.dry_run else "patched"
    print(f"{label} {len(patched)} file(s):")
    for p in patched:
        try:
            print(f"  {p.relative_to(ULTRON_ROOT)}")
        except ValueError:
            print(f"  {p}")

    if args.dry_run:
        return 0

    # 3. Rebuild backlinks.
    subprocess.run(
        [sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "build-backlinks.py")],
        check=False,
    )

    # 4. Verify.
    cmd = [sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "check-routes.py")]
    if args.workspace:
        cmd += ["--workspace", args.workspace]
    rc = subprocess.run(cmd, check=False).returncode
    return rc


if __name__ == "__main__":
    sys.exit(main())
