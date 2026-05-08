#!/usr/bin/env python3
"""
generate-candidate-edges.py — produce a queue of likely cross-workspace
edges for human review. Output: `_shell/audit/candidate_edges.jsonl`.

Two candidate sources, both deterministic, no LLM:

(1) ALIAS candidates. Same normalized label, different ids, across 2+
    workspaces. Reuses the logic from `find-cross-workspace-slugs.py`.
    Action on accept: `alias merge ... --canonical <pick>`.

(2) CO-OCCURRENCE candidates. Pairs of nodes with N+ shared neighbors
    in the super-graph but no direct edge. Suggests "these likely know
    each other / are connected." Action on accept: `link add subj
    knows obj`.

Rejected candidates are remembered in `_shell/audit/rejected_edges.jsonl`
so they never resurface.

Usage:
    generate-candidate-edges.py [--min-shared 4] [--limit 200] [--no-cooccur]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
WORKSPACES_DIR = ULTRON_ROOT / "workspaces"
SUPER_GRAPH = ULTRON_ROOT / "_graphify" / "super" / "graph.json"
GLOBAL_ENTITIES = ULTRON_ROOT / "_global" / "entities"
AUDIT_DIR = ULTRON_ROOT / "_shell" / "audit"
CANDIDATES_FILE = AUDIT_DIR / "candidate_edges.jsonl"
REJECTED_FILE = AUDIT_DIR / "rejected_edges.jsonl"

EXCLUDE_PREFIXES = ("_community_", "community_", "_cluster_")
GENERIC_LABELS = {
    "user", "me", "i", "you", "they", "we",
    "claude", "chatgpt", "gpt", "ai", "llm", "the user",
}


def norm_key(label: str | None, node_id: str | None) -> str:
    """Same normalization as find-cross-workspace-slugs.py."""
    raw = (label or node_id or "").strip()
    if not raw:
        return ""
    stripped = re.sub(r"\([^)]*\)", "", raw).strip()
    if len(stripped.split()) >= 2:
        raw = stripped
    raw = re.sub(r"[^a-z0-9\s]+", " ", raw.lower())
    return re.sub(r"\s+", " ", raw).strip()


def edge_id(subj: str, obj: str, kind: str) -> str:
    """Stable id for dedup. Order-independent for symmetric kinds."""
    parts = sorted([subj, obj]) if kind in ("alias", "knows", "co_attended") else [subj, obj]
    return hashlib.blake2b(f"{kind}:{parts[0]}:{parts[1]}".encode(), digest_size=8).hexdigest()


def build_slug_index() -> dict[str, str]:
    """Index every existing entity slug under _global/entities/ AND each
    workspace's wiki/entities/. Returns {normalized_form -> canonical_slug}.

    Graphify uses underscored node ids; the skills look up files by slug
    (typically hyphenated). This index lets us map graphify-id -> actual
    file slug so accepted candidates can dispatch into link/alias cleanly.
    """
    index: dict[str, str] = {}

    def _add(slug: str) -> None:
        if not slug:
            return
        # Map both the slug as-is and its underscore-equivalent.
        for form in {slug, slug.replace("-", "_"), slug.replace("_", "-")}:
            index.setdefault(form.lower(), slug)

    if GLOBAL_ENTITIES.exists():
        for p in GLOBAL_ENTITIES.rglob("*.md"):
            _add(p.stem)

    if WORKSPACES_DIR.exists():
        for ws in WORKSPACES_DIR.iterdir():
            if not ws.is_dir() or ws.name.startswith("_"):
                continue
            ents = ws / "wiki" / "entities"
            if not ents.exists():
                continue
            for p in ents.rglob("*.md"):
                _add(p.stem)

    return index


def resolve_slug(node_id: str, index: dict[str, str]) -> str | None:
    """Return the canonical file slug for a graphify node id, or None if
    no entity file exists for it."""
    if not node_id:
        return None
    return index.get(node_id.lower())


def load_super() -> dict | None:
    if not SUPER_GRAPH.exists():
        sys.stderr.write(f"warn: no super-graph at {SUPER_GRAPH}; run graphify-supermerge first\n")
        return None
    try:
        return json.loads(SUPER_GRAPH.read_text())
    except json.JSONDecodeError as e:
        sys.stderr.write(f"error: malformed super-graph: {e}\n")
        return None


def load_per_workspace_nodes() -> dict[str, list[dict]]:
    """Return {ws_name: [node_dict]}."""
    out: dict[str, list[dict]] = {}
    for ws_dir in sorted(WORKSPACES_DIR.iterdir()):
        if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
            continue
        gp = ws_dir / "graphify-out" / "graph.json"
        if not gp.exists():
            continue
        try:
            g = json.loads(gp.read_text())
        except json.JSONDecodeError:
            continue
        nodes: list[dict] = []
        for n in g.get("nodes", []):
            node_id = n.get("id") or ""
            if any(node_id.lower().startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            nodes.append({
                "ws": ws_dir.name,
                "id": node_id,
                "label": n.get("label") or n.get("norm_label") or node_id,
            })
        out[ws_dir.name] = nodes
    return out


def load_rejected_ids() -> set[str]:
    if not REJECTED_FILE.exists():
        return set()
    out: set[str] = set()
    for line in REJECTED_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "id" in r:
            out.add(r["id"])
    return out


def load_existing_pending_ids() -> set[str]:
    """Don't re-emit candidates already pending."""
    if not CANDIDATES_FILE.exists():
        return set()
    out: set[str] = set()
    for line in CANDIDATES_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("status") == "pending" and "id" in r:
            out.add(r["id"])
    return out


def alias_candidates(per_ws: dict[str, list[dict]], slug_index: dict[str, str]) -> list[dict]:
    """Same normalized label, different ids, 2+ workspaces."""
    by_key: dict[str, list[dict]] = defaultdict(list)
    for ws, nodes in per_ws.items():
        for n in nodes:
            key = norm_key(n["label"], n["id"])
            if not key or key in GENERIC_LABELS:
                continue
            by_key[key].append(n)

    out: list[dict] = []
    for key, entries in by_key.items():
        ws_set = {e["ws"] for e in entries}
        if len(ws_set) < 2:
            continue
        # Resolve graphify node ids to actual on-disk entity slugs. Any
        # candidate whose endpoints don't have entity files is skipped —
        # link/alias would just fail, no point queueing.
        resolved = []
        for e in entries:
            slug = resolve_slug(e["id"], slug_index)
            if slug is None:
                continue
            resolved.append({**e, "slug": slug})
        if len({r["slug"] for r in resolved}) < 2:
            continue

        slugs = sorted({r["slug"] for r in resolved}, key=len, reverse=True)
        canonical = slugs[0]
        for r in resolved:
            if r["slug"] == canonical:
                continue
            out.append({
                "id": edge_id(r["slug"], canonical, "alias"),
                "kind": "alias",
                "subj": r["slug"],
                "obj": canonical,
                "subj_label": r["label"],
                "obj_label": next(x["label"] for x in resolved if x["slug"] == canonical),
                "type": "alias_of",
                "reason": f"normalized label '{key}' resolves to multiple entity slugs across {len(ws_set)} workspaces",
                "confidence": 0.7,
                "proposed_by": "label_overlap",
                "evidence": {
                    "workspaces": sorted(ws_set),
                    "graphify_ids": sorted({r["id"] for r in resolved}),
                    "resolved_slugs": slugs,
                },
                "status": "pending",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })
    return out


def cooccurrence_candidates(super_g: dict, min_shared: int, slug_index: dict[str, str]) -> list[dict]:
    """Pairs with min_shared+ shared neighbors but no direct edge."""
    nodes = super_g.get("nodes", [])
    links = super_g.get("links", [])

    # Build adjacency.
    adj: dict[str, set[str]] = defaultdict(set)
    direct: set[tuple[str, str]] = set()
    for l in links:
        s = l.get("source") or l.get("_src")
        t = l.get("target") or l.get("_tgt")
        if not (isinstance(s, str) and isinstance(t, str)) or s == t:
            continue
        adj[s].add(t)
        adj[t].add(s)
        direct.add(tuple(sorted([s, t])))

    # Drop community nodes.
    valid_ids = {
        n.get("id") for n in nodes
        if not any((n.get("id") or "").lower().startswith(p) for p in EXCLUDE_PREFIXES)
    }

    # Count shared-neighbor pairs by walking each node's neighbor pairs.
    shared: dict[tuple[str, str], int] = defaultdict(int)
    for hub, neighbors in adj.items():
        if hub not in valid_ids:
            continue
        ns = sorted(n for n in neighbors if n in valid_ids)
        for i in range(len(ns)):
            for j in range(i + 1, len(ns)):
                shared[(ns[i], ns[j])] += 1

    out: list[dict] = []
    for (a, b), count in shared.items():
        if count < min_shared:
            continue
        if (a, b) in direct:
            continue
        a_slug = resolve_slug(a, slug_index)
        b_slug = resolve_slug(b, slug_index)
        # Skip pairs we can't apply against — both endpoints need entity files.
        if a_slug is None or b_slug is None or a_slug == b_slug:
            continue
        confidence = min(0.9, 0.4 + 0.05 * count)
        out.append({
            "id": edge_id(a_slug, b_slug, "knows"),
            "kind": "link",
            "subj": a_slug,
            "obj": b_slug,
            "subj_label": a_slug,
            "obj_label": b_slug,
            "type": "knows",
            "reason": f"{count} shared neighbors, no direct edge",
            "confidence": round(confidence, 2),
            "proposed_by": "cooccurrence",
            "evidence": {"shared_count": count, "graphify_ids": [a, b]},
            "status": "pending",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
    out.sort(key=lambda c: -c["evidence"]["shared_count"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-shared", type=int, default=4,
                    help="Minimum shared neighbors for a co-occurrence candidate (default: 4).")
    ap.add_argument("--limit", type=int, default=200,
                    help="Cap total candidates emitted this run (default: 200).")
    ap.add_argument("--no-cooccur", action="store_true",
                    help="Skip co-occurrence candidates (alias only).")
    args = ap.parse_args()

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    rejected = load_rejected_ids()
    pending = load_existing_pending_ids()
    skip = rejected | pending

    slug_index = build_slug_index()
    per_ws = load_per_workspace_nodes()
    aliases = alias_candidates(per_ws, slug_index)
    aliases = [c for c in aliases if c["id"] not in skip]

    cooccur: list[dict] = []
    if not args.no_cooccur:
        sg = load_super()
        if sg is not None:
            cooccur = cooccurrence_candidates(sg, args.min_shared, slug_index)
            cooccur = [c for c in cooccur if c["id"] not in skip]

    new_candidates = aliases + cooccur
    new_candidates = new_candidates[: args.limit]

    if not new_candidates:
        print("no new candidates")
        return 0

    # Append-only.
    with CANDIDATES_FILE.open("a") as f:
        for c in new_candidates:
            f.write(json.dumps(c) + "\n")

    by_kind = defaultdict(int)
    for c in new_candidates:
        by_kind[c["kind"]] += 1
    print(f"wrote {len(new_candidates)} candidates ({dict(by_kind)}) to {CANDIDATES_FILE.relative_to(ULTRON_ROOT)}")
    print(f"existing pending skipped: {len(pending)}; previously rejected skipped: {len(rejected)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
