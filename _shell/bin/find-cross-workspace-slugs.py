#!/usr/bin/env python3
"""
find-cross-workspace-slugs.py — aggregator over per-workspace Graphify
output. Identifies entities appearing in 2+ workspaces and ranks them as
promotion candidates.

Approach:
  - Read every workspaces/<ws>/graphify-out/graph.json.
  - For each node, derive a normalized matching key (lowercase, alphanum-only,
    parenthetical disambiguators stripped).
  - Aggregate by key. Filter to keys appearing in 2+ workspaces.
  - Rank by total cross-workspace degree.

Why no fuzzy match: ULTRON deliberately uses context-disambiguated slugs
(e.g., `aaliyah-hinge-austin`, `abby-tinder-austin`). Fuzzy string matching
on these is dangerous — `difflib` matches them at 0.85+ because of shared
suffixes, producing false-positive alias suggestions for unrelated people.
Exact normalized match on label is the only safe rule.

Output: `_shell/audit/promotion-candidates.md`. Idempotent — re-running
overwrites this file.

Usage: find-cross-workspace-slugs.py [--top N] [--min-degree D] [--stdout]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
WORKSPACES_DIR = ULTRON_ROOT / "workspaces"
DEFAULT_OUTPUT = ULTRON_ROOT / "_shell" / "audit" / "promotion-candidates.md"

# Skip community/cluster nodes — they aren't entities.
EXCLUDE_PREFIXES = ("_community_", "community_", "_cluster_")

# Skip generic terms that show up everywhere and aren't useful as
# promotion candidates.
GENERIC_LABELS = {
    "user", "me", "i", "you", "they", "we",
    "claude", "chatgpt", "gpt", "ai", "llm", "the user",
}


def norm_key(label: str | None, node_id: str | None) -> str:
    """Normalize a label/id for cross-workspace matching.

    - Lowercases, replaces non-alphanum with spaces, collapses whitespace.
    - Strips parenthetical disambiguators ONLY if the remaining label has
      2+ tokens. Single-token names with parens like `Alex (landlord)` and
      `Alex (artist)` keep their parens so they don't collapse to the same
      key (different people, common first name).
    """
    raw = (label or node_id or "").strip()
    if not raw:
        return ""
    stripped = re.sub(r"\([^)]*\)", "", raw).strip()
    if len(stripped.split()) >= 2:
        raw = stripped
    raw = re.sub(r"[^a-z0-9\s]+", " ", raw.lower())
    return re.sub(r"\s+", " ", raw).strip()


def load_workspace_graph(ws_dir: Path) -> tuple[list[dict], list[dict]] | None:
    p = ws_dir / "graphify-out" / "graph.json"
    if not p.exists():
        return None
    try:
        g = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        sys.stderr.write(f"warn: {ws_dir.name}: malformed graph.json ({e})\n")
        return None
    return g.get("nodes", []), g.get("links", [])


def degree_index(links: list[dict]) -> dict[str, int]:
    """Count edges per node id. Each link contributes one degree to the
    source endpoint and one to the target endpoint. Graphify writes both
    `source`/`target` (NetworkX) and `_src`/`_tgt` (legacy) on every edge —
    use whichever pair is populated, never both, to avoid double-counting.
    """
    deg: dict[str, int] = defaultdict(int)
    for l in links:
        src = l.get("source") or l.get("_src")
        tgt = l.get("target") or l.get("_tgt")
        if isinstance(src, str):
            deg[src] += 1
        if isinstance(tgt, str):
            deg[tgt] += 1
    return deg


def collect_candidates() -> dict[str, list[dict]]:
    """Return {norm_key: [{ws, id, label, degree, community}]}."""
    by_key: dict[str, list[dict]] = defaultdict(list)
    if not WORKSPACES_DIR.exists():
        return by_key

    for ws_dir in sorted(WORKSPACES_DIR.iterdir()):
        if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
            continue
        loaded = load_workspace_graph(ws_dir)
        if loaded is None:
            continue
        nodes, links = loaded
        deg = degree_index(links)

        for n in nodes:
            node_id = n.get("id") or ""
            label = n.get("label") or n.get("norm_label") or node_id
            if any(node_id.lower().startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            key = norm_key(label, node_id)
            if not key or key in GENERIC_LABELS:
                continue
            by_key[key].append({
                "workspace": ws_dir.name,
                "id": node_id,
                "label": label,
                "degree": deg.get(node_id, 0),
                "community": n.get("community"),
            })
    return by_key


def assess_confidence(entries: list[dict]) -> str:
    """High if all workspaces use the same id; medium if the normalized
    label matches but ids differ."""
    ids = {e["id"] for e in entries if e.get("id")}
    return "high" if len(ids) == 1 else "medium"


def render(rows: list[dict], min_degree: int) -> str:
    lines = [
        "# Cross-Workspace Slug Candidates",
        "",
        "Generated by `_shell/bin/find-cross-workspace-slugs.py`. Idempotent — re-running overwrites this file.",
        "",
        "Source: per-workspace Graphify outputs (`graphify-out/graph.json`).",
        "Match rule: exact normalized label across 2+ workspaces. No fuzzy matching (intentional — see script docstring).",
        "",
        f"_{len(rows)} candidates. Min summed degree: {min_degree}._",
        "",
        "| label | primary id | workspaces | total degree | confidence | recommended action |",
        "|---|---|---|---|---|---|",
    ]
    if not rows:
        lines.append("| (none) | | | | | |")
    else:
        for r in rows:
            ws_str = ", ".join(r["workspaces"])
            action = "/promote" if r["confidence"] == "high" and r["total_degree"] >= 5 else "review"
            lines.append(
                f"| {r['primary_label']} | `{r['primary_id']}` | {ws_str} "
                f"| {r['total_degree']} | {r['confidence']} | {action} |"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=200,
                    help="Cap rows in output (default: 200).")
    ap.add_argument("--min-degree", type=int, default=2,
                    help="Skip candidates with summed degree below this (default: 2).")
    ap.add_argument("--stdout", action="store_true",
                    help="Print to stdout instead of writing the file.")
    args = ap.parse_args()

    by_key = collect_candidates()

    rows: list[dict] = []
    for key, entries in by_key.items():
        ws_set = {e["workspace"] for e in entries}
        if len(ws_set) < 2:
            continue
        total_degree = sum(e["degree"] for e in entries)
        if total_degree < args.min_degree:
            continue
        primary = max(entries, key=lambda e: e["degree"])
        rows.append({
            "key": key,
            "primary_label": primary["label"],
            "primary_id": primary["id"],
            "workspaces": sorted(ws_set),
            "total_degree": total_degree,
            "confidence": assess_confidence(entries),
        })

    rows.sort(key=lambda r: (-r["total_degree"], r["key"]))
    rows = rows[: args.top]

    out = render(rows, args.min_degree)
    if args.stdout:
        sys.stdout.write(out)
        return 0

    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(out)
    print(f"wrote {DEFAULT_OUTPUT.relative_to(ULTRON_ROOT)} ({len(rows)} candidates)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
