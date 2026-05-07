#!/usr/bin/env python3
"""
apply-audit.py — apply user decisions from a graph-audit queue back to graph.json.

Reads a queue file produced by audit-relationships.py. For every item the user
has checked, modifies the corresponding workspace's graph.json and surgically
regenerates only the affected Obsidian pages. Rejected edges are appended to
_global/blacklists/edge-rejections.yaml so future graphify --update passes can
suppress re-extraction (Phase 6 will wire that suppression at ingest time; for
now the blacklist is recorded for later use).

Markers (from the queue):
    [x]  confirm — INFERRED→EXTRACTED, score=1.0
    [!]  reject  — remove edge, append to blacklist
    [?]  ambiguous — no-op (will be resurfaced next pass)
    [ ]  unchecked — no-op

Inline overrides (after the edge line):
    → new_relation       relabel
    ↔ flip               swap source and target
    ⇒ correct_slug       redirect target

Usage:
    apply-audit.py <queue.md> [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
WORKSPACES_DIR = ULTRON_ROOT / "workspaces"
BLACKLIST_PATH = ULTRON_ROOT / "_global" / "blacklists" / "edge-rejections.yaml"

ITEM_RE = re.compile(r"^- \[(?P<mark>[x!?\s])\] `(?P<src_label>[^`]+)` —`(?P<rel>[^`]+)`→ `(?P<tgt_label>[^`]+)` \((?P<conf>\w+) (?P<score>[\d.]+)\)(?P<rest>.*)$")
META_RE = re.compile(r"^\s+- <!-- (?P<ws>[\w-]+) \| (?P<src>[\w_-]+) \| (?P<rel>[\w_-]+) \| (?P<tgt>[\w_-]+) -->\s*$")
INLINE_RELABEL = re.compile(r"→\s*([\w_-]+)")
INLINE_FLIP = re.compile(r"↔\s*flip\b")
INLINE_REDIRECT = re.compile(r"⇒\s*([\w_-]+)")


def parse_queue(path: Path) -> list[dict]:
    """Returns one dict per checked item: {mark, ws, src, rel, tgt, relabel?, flip?, redirect?}."""
    decisions = []
    pending_item = None
    for raw in path.read_text().splitlines():
        m = ITEM_RE.match(raw)
        if m:
            mark = m.group("mark").strip()
            if mark not in {"x", "!", "?"}:
                pending_item = None
                continue
            rest = m.group("rest") or ""
            relabel = INLINE_RELABEL.search(rest)
            flip = bool(INLINE_FLIP.search(rest))
            redirect = INLINE_REDIRECT.search(rest)
            pending_item = {
                "mark": mark,
                "relabel": relabel.group(1) if relabel else None,
                "flip": flip,
                "redirect": redirect.group(1) if redirect else None,
            }
            continue
        if pending_item is not None:
            mm = META_RE.match(raw)
            if mm:
                pending_item.update({
                    "ws": mm.group("ws"),
                    "src": mm.group("src"),
                    "rel": mm.group("rel"),
                    "tgt": mm.group("tgt"),
                })
                decisions.append(pending_item)
            pending_item = None
    return decisions


def apply_to_graph(ws: str, decisions: list[dict], dry_run: bool) -> tuple[set[str], list[str]]:
    """Mutate the workspace's graph.json. Returns (affected_node_ids, log)."""
    gp = WORKSPACES_DIR / ws / "graphify-out" / "graph.json"
    if not gp.exists():
        return set(), [f"[{ws}] no graph.json — skipped"]

    backup = gp.with_suffix(".json.pre-audit.bak")
    if not dry_run:
        shutil.copy(gp, backup)
    g = json.loads(gp.read_text())
    links = g["links"]
    log: list[str] = []
    affected: set[str] = set()

    for d in decisions:
        # Locate the edge — match on source, target, relation
        idx = next(
            (i for i, l in enumerate(links)
             if l["source"] == d["src"] and l["target"] == d["tgt"] and l.get("relation") == d["rel"]),
            None,
        )
        if idx is None:
            log.append(f"  ! not found: {d['src']} -[{d['rel']}]-> {d['tgt']}")
            continue
        edge = links[idx]
        affected.update({d["src"], d["tgt"]})

        if d["mark"] == "!":
            # Remove edge, blacklist
            del links[idx]
            log.append(f"  - rejected: {d['src']} -[{d['rel']}]-> {d['tgt']}")
            continue

        if d["mark"] == "x":
            # Confirm + apply any inline overrides
            if d["flip"]:
                edge["source"], edge["target"] = edge["target"], edge["source"]
                edge["_src"], edge["_tgt"] = edge.get("_tgt", edge["target"]), edge.get("_src", edge["source"])
                affected.update({edge["source"], edge["target"]})
                log.append(f"  ↔ flipped: {edge['source']} -[{edge.get('relation')}]-> {edge['target']}")
            if d["relabel"]:
                old_rel = edge.get("relation")
                edge["relation"] = d["relabel"]
                log.append(f"  → relabeled: {edge['source']} {old_rel}→{d['relabel']} {edge['target']}")
            if d["redirect"]:
                edge["target"] = d["redirect"]
                edge["_tgt"] = d["redirect"]
                affected.add(d["redirect"])
                log.append(f"  ⇒ redirected target to {d['redirect']}")
            edge["confidence"] = "EXTRACTED"
            edge["confidence_score"] = 1.0
            edge["audit_provenance"] = "user-confirmed"
            edge["audit_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            log.append(f"  ✓ confirmed: {edge['source']} -[{edge.get('relation')}]-> {edge['target']}")

    if not dry_run:
        gp.write_text(json.dumps(g))
        log.append(f"  ↓ wrote {gp}")
    return affected, log


def append_blacklist(rejected: list[dict], dry_run: bool) -> None:
    if not rejected:
        return
    BLACKLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).date().isoformat()
    lines = [f"# Auto-appended {today}"]
    for d in rejected:
        lines.append(
            f"- {{ workspace: {d['ws']}, source: {d['src']}, "
            f"relation: {d['rel']}, target: {d['tgt']}, rejected_at: {today} }}"
        )
    if dry_run:
        print("\n[dry-run] would append to blacklist:")
        print("\n".join(lines))
        return
    existing = BLACKLIST_PATH.read_text() if BLACKLIST_PATH.exists() else ""
    BLACKLIST_PATH.write_text(existing + "\n" + "\n".join(lines) + "\n")


def render_affected(ws: str, affected: set[str]) -> int:
    """Surgically render only affected nodes' Obsidian pages."""
    gp = WORKSPACES_DIR / ws / "graphify-out" / "graph.json"
    obsidian_dir = WORKSPACES_DIR / ws / "graphify-out" / "obsidian"
    if not gp.exists() or not obsidian_dir.exists():
        return 0
    from networkx.readwrite import json_graph

    data = json.loads(gp.read_text())
    G = json_graph.node_link_graph(data, edges="links")

    def safe_name(label: str) -> str:
        cleaned = re.sub(r'[\\/*?:"<>|#^[\]]', "", label.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")).strip()
        cleaned = re.sub(r"\.(md|mdx|markdown)$", "", cleaned, flags=re.IGNORECASE)
        return cleaned or "unnamed"

    node_filename: dict[str, str] = {}
    seen: dict[str, int] = {}
    for nid, dat in G.nodes(data=True):
        base = safe_name(dat.get("label", nid))
        if base in seen:
            seen[base] += 1
            node_filename[nid] = f"{base}_{seen[base]}"
        else:
            seen[base] = 0
            node_filename[nid] = base

    def dom_conf(nid: str) -> str:
        confs = [ed.get("confidence", "EXTRACTED") for _, _, ed in G.edges(nid, data=True)]
        return Counter(confs).most_common(1)[0][0] if confs else "EXTRACTED"

    FTYPE_TAG = {"code": "graphify/code", "document": "graphify/document",
                 "paper": "graphify/paper", "image": "graphify/image"}
    node_community = {nid: int(dat["community"]) for nid, dat in G.nodes(data=True) if dat.get("community") is not None}

    written = 0
    for nid in affected:
        if nid not in G.nodes:
            continue
        dat = G.nodes[nid]
        label = dat.get("label", nid)
        cid = node_community.get(nid)
        community_name = f"Community {cid}"
        ftype = dat.get("file_type", "")
        ftype_tag = FTYPE_TAG.get(ftype, f"graphify/{ftype}" if ftype else "graphify/document")
        conf_tag = f"graphify/{dom_conf(nid)}"
        comm_tag = f"community/{community_name.replace(' ', '_')}"
        lines = [
            "---",
            f'source_file: "{dat.get("source_file", "")}"',
            f'type: "{ftype or "document"}"',
            f'community: "{community_name}"',
            "tags:",
            f"  - {ftype_tag}",
            f"  - {conf_tag}",
            f"  - {comm_tag}",
            "---",
            "",
            f"# {label}",
            "",
            "## Connections",
        ]
        edges = sorted(
            G.edges(nid, data=True),
            key=lambda e: (e[2].get("relation", ""), G.nodes[e[1] if e[0] == nid else e[0]].get("label", "")),
        )
        if not edges:
            lines.append("- (no edges)")
        else:
            for u, v, ed in edges:
                other = v if u == nid else u
                other_label = G.nodes[other].get("label", other)
                other_fn = node_filename[other]
                rel = ed.get("relation", "related_to")
                conf = ed.get("confidence", "EXTRACTED")
                line = (f"- [[{other_fn}|{other_label}]] - `{rel}` [{conf}]"
                        if other_fn != other_label
                        else f"- [[{other_label}]] - `{rel}` [{conf}]")
                lines.append(line)
        lines += ["", f"#{ftype_tag} #{conf_tag} #{comm_tag}"]
        (obsidian_dir / f"{node_filename[nid]}.md").write_text("\n".join(lines))
        written += 1
    return written


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("queue", help="path to a graph-audit-*.md file")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    queue_path = Path(args.queue)
    if not queue_path.exists():
        print(f"Queue not found: {queue_path}", file=sys.stderr)
        return 2

    decisions = parse_queue(queue_path)
    if not decisions:
        print("No checked items in queue.")
        return 0

    by_ws: dict[str, list[dict]] = defaultdict(list)
    for d in decisions:
        by_ws[d["ws"]].append(d)

    rejected_global: list[dict] = []
    counts = Counter(d["mark"] for d in decisions)
    print(f"Processing {len(decisions)} decisions: "
          f"{counts.get('x', 0)} confirm, {counts.get('!', 0)} reject, {counts.get('?', 0)} ambiguous")
    print()

    for ws, items in by_ws.items():
        print(f"## {ws} ({len(items)} items)")
        affected, log = apply_to_graph(ws, items, args.dry_run)
        for entry in log:
            print(entry)
        rejected_global.extend(d for d in items if d["mark"] == "!")
        if affected and not args.dry_run:
            n = render_affected(ws, affected)
            print(f"  ↻ surgically regenerated {n} pages")
        print()

    append_blacklist(rejected_global, args.dry_run)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
