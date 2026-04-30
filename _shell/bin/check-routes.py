#!/usr/bin/env python3
"""
check-routes.py — validate every wikilink in ULTRON.

Walks every `.md` file under ULTRON (or a single workspace), parses every
`[[...]]` wikilink, resolves it via _global/wikilink-resolution.md rules, and
reports broken links.

Usage:
    check-routes.py [--workspace <ws>] [--paths-only] [--output <path>]

Exit codes:
    0 — all routes resolve
    1 — broken routes found
    2 — invocation error
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

# Files we deliberately skip (templates with intentionally-unresolved placeholders, ephemeral run state).
SKIP_PATH_FRAGMENTS = (
    "/_shell/runs/",
    "/_credentials/",
    "/.git/",
    "/_template/",
)


def current_workspace_dir(file: Path) -> Path | None:
    """Return the workspace root for a file inside workspaces/<ws>/, else None."""
    try:
        rel = file.relative_to(ULTRON_ROOT)
    except ValueError:
        return None
    parts = rel.parts
    if parts and parts[0] == "workspaces" and len(parts) >= 2:
        return ULTRON_ROOT / "workspaces" / parts[1]
    return None


def resolve_global(slug: str) -> Path | None:
    base = ULTRON_ROOT / "_global" / "entities"
    if not base.exists():
        return None
    for type_dir in base.iterdir():
        if not type_dir.is_dir():
            continue
        cand = type_dir / f"{slug}.md"
        if cand.exists():
            return cand
    return None


def resolve_ws(rest: str) -> Path | None:
    if "/" not in rest:
        return None
    ws, name = rest.split("/", 1)
    ws_dir = ULTRON_ROOT / "workspaces" / ws / "wiki"
    if not ws_dir.exists():
        return None
    # Name may include intermediate path like "entities/people/sydney" or just "sydney".
    if "/" in name:
        cand = ws_dir / f"{name}.md"
        return cand if cand.exists() else None
    entities_dir = ws_dir / "entities"
    if not entities_dir.exists():
        return None
    for type_dir in entities_dir.iterdir():
        if not type_dir.is_dir():
            continue
        cand = type_dir / f"{name}.md"
        if cand.exists():
            return cand
    return None


def _is_safe_relative(rest: str) -> bool:
    """Reject absolute paths and any '..' parts to prevent path-traversal exploits in wikilinks."""
    if not rest:
        return False
    if rest.startswith("/") or rest.startswith("\\"):
        return False
    parts = rest.replace("\\", "/").split("/")
    return all(p not in ("..", "") for p in parts) or all(p != ".." for p in parts if p)


def _ensure_within(base: Path, candidate: Path) -> Path | None:
    """Resolve `candidate` and return it only if still under `base` after symlink resolution."""
    try:
        resolved = candidate.resolve()
        base_resolved = base.resolve()
        resolved.relative_to(base_resolved)
    except (OSError, ValueError):
        return None
    return resolved if resolved.exists() else None


def resolve_within_ws(file: Path, segment: str, target: str) -> Path | None:
    if not _is_safe_relative(target):
        return None
    ws_dir = current_workspace_dir(file)
    if ws_dir is None:
        return None
    cand = ws_dir / "wiki" / segment / f"{target}.md"
    return _ensure_within(ws_dir / "wiki" / segment, cand)


def resolve_raw(file: Path, rest: str) -> Path | None:
    if not _is_safe_relative(rest):
        return None
    ws_dir = current_workspace_dir(file)
    if ws_dir is None:
        return None
    cand = ws_dir / "raw" / rest
    return _ensure_within(ws_dir / "raw", cand)


def resolve_bare(file: Path, target: str) -> Path | None:
    ws_dir = current_workspace_dir(file)
    if ws_dir is None:
        return None
    # First: top-level wiki file (e.g., [[overview]] → wiki/overview.md).
    top = ws_dir / "wiki" / f"{target}.md"
    if top.exists():
        return top
    # Then: entity lookup under wiki/entities/<type>/.
    entities_dir = ws_dir / "wiki" / "entities"
    if not entities_dir.exists():
        return None
    matches = list(entities_dir.rglob(f"{target}.md"))
    return matches[0] if len(matches) == 1 else None


def resolve(target: str, current_file: Path) -> Path | None:
    """Resolve a wikilink target per _global/wikilink-resolution.md."""
    target = target.strip()
    if not target:
        return None

    if target.startswith("@"):
        return resolve_global(target[1:])
    if target.startswith("ws:"):
        return resolve_ws(target[3:])
    if target.startswith("concept:"):
        return resolve_within_ws(current_file, "concepts", target[len("concept:"):])
    if target.startswith("synthesis:"):
        return resolve_within_ws(current_file, "synthesis", target[len("synthesis:"):])
    if target.startswith("raw:"):
        return resolve_raw(current_file, target[len("raw:"):])
    return resolve_bare(current_file, target)


def should_skip(path: Path) -> bool:
    s = str(path)
    return any(frag in s for frag in SKIP_PATH_FRAGMENTS)


FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
# Match variable-length inline code spans per CommonMark: a run of N backticks
# closes only on another run of exactly N backticks. Handles `code`, ``co`de``,
# and ```multi`tick```.
INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)+?\1", re.DOTALL)


def strip_code_spans(line: str) -> str:
    """Remove inline-code spans so wikilinks inside backticks are ignored."""
    return INLINE_CODE_RE.sub("", line)


def find_broken(scope: Path) -> list[tuple[Path, int, str]]:
    broken: list[tuple[Path, int, str]] = []
    for md in scope.rglob("*.md"):
        if should_skip(md):
            continue
        try:
            text = md.read_text(errors="ignore")
        except OSError:
            continue
        in_fence = False
        fence_marker: str | None = None
        for line_num, raw_line in enumerate(text.splitlines(), 1):
            m_fence = FENCE_RE.match(raw_line)
            if m_fence is not None:
                tok = m_fence.group(1)[0]   # '`' or '~'
                if not in_fence:
                    in_fence = True
                    fence_marker = tok
                elif fence_marker == tok:
                    in_fence = False
                    fence_marker = None
                continue
            if in_fence:
                continue
            line = strip_code_spans(raw_line)
            for m in WIKILINK_RE.finditer(line):
                # Drop display label after pipe and any leading bang for embeds.
                target = m.group(1).split("|")[0].lstrip("!")
                if not resolve(target, md):
                    broken.append((md, line_num, target))
    return broken


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace")
    ap.add_argument("--paths-only", action="store_true",
                    help="Print only unique source file paths (one per line).")
    ap.add_argument("--output")
    args = ap.parse_args()

    if args.workspace:
        scope = ULTRON_ROOT / "workspaces" / args.workspace
        if not scope.exists():
            print(f"workspace not found: {args.workspace}", file=sys.stderr)
            return 2
    else:
        scope = ULTRON_ROOT

    broken = find_broken(scope)

    if args.paths_only:
        unique_paths = sorted({str(p) for p, _, _ in broken})
        out = "\n".join(unique_paths)
    else:
        out = "\n".join(f"{p}:{ln}\t[[{t}]]" for p, ln, t in broken)

    if args.output:
        Path(args.output).write_text(out + ("\n" if out else ""))
    else:
        if out:
            print(out)

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
