#!/usr/bin/env python3
"""
audit-relationships.py — generate a markdown audit queue of ambiguous graph edges.

Walks every workspace's graphify-out/graph.json and surfaces edges that need a
human decision: INFERRED edges with low confidence, direction-suspect edges
(institutions that "study at" people, etc.), missing reciprocals on symmetric
relations, and outright AMBIGUOUS edges.

Output is a markdown file at _queues/graph-audit-YYYY-MM-DD-<ws>.md (or -all.md
when run across every workspace). The user marks each item with `[x]` (confirm),
`[!]` (reject + blacklist), `[?]` (still ambiguous), then runs apply-audit.py.

Usage:
    audit-relationships.py [--workspace <ws>|all] [--threshold 0.85] [--output <path>]

Exit codes:
    0 — queue generated
    1 — no ambiguous edges found across requested scope
    2 — invocation error
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
WORKSPACES_DIR = ULTRON_ROOT / "workspaces"
QUEUES_DIR = ULTRON_ROOT / "_queues"

SYMMETRIC_RELATIONS = {
    "friend", "colleague", "partner", "married_to", "co_founded",
    "co_author", "sibling", "roommate", "roommate_of",
    "ex_partner_of", "dated",
}

PERSON_TO_ORG_RELATIONS = {
    "studies_at", "works_at", "founded", "co_founded",
    "invested_in", "attends", "attended",
}
PERSON_TO_PLACE_RELATIONS = {
    "lives_in", "formerly_lived_in", "lived_at", "born_in",
}
PERSON_TO_PERSON_RELATIONS = {
    "mentors", "mentee_of", "reports_to", "manages", "married_to",
    "parent_of", "child_of", "sibling", "friend", "ex_partner_of",
    "dated", "partner", "roommate", "roommate_of",
}
PERSON_RELATIONS = (
    PERSON_TO_ORG_RELATIONS | PERSON_TO_PLACE_RELATIONS | PERSON_TO_PERSON_RELATIONS
)


def is_org_or_place(node: dict) -> bool:
    label = (node.get("label") or "").lower()
    nid = node.get("id", "").lower()
    return any(
        kw in label or kw in nid
        for kw in (
            "university", "college", "school", "labs", "inc", "corp", "ltd",
            "company", "studio", "berkeley", "stanford", "mit", "academy",
            "austin", "los angeles", "san francisco", "new york", "miami",
            "city", "street", "avenue", "park", "country", "state",
        )
    )


def load_graph(graph_path: Path) -> dict:
    with graph_path.open() as f:
        return json.load(f)


def fmt_edge(src_label: str, rel: str, tgt_label: str, conf: str, score, src_file) -> str:
    s = f"`{src_label}` —`{rel}`→ `{tgt_label}` ({conf} {score})"
    if src_file:
        sf = src_file.split("raw/", 1)[-1] if "raw/" in src_file else src_file
        sf = sf[:60]
        s += f" — {sf}"
    return s


def audit_workspace(ws_name: str, threshold: float = 0.85) -> dict[str, list]:
    graph_path = WORKSPACES_DIR / ws_name / "graphify-out" / "graph.json"
    if not graph_path.exists():
        return {}
    g = load_graph(graph_path)
    nodes_by_id = {n["id"]: n for n in g["nodes"]}
    links = g["links"]

    buckets: dict[str, list] = {
        "direction_suspect": [],
        "amb_outright": [],
        "low_conf_inferred": [],
        "co_occurrence_inferred": [],
        "missing_reciprocal": [],
    }

    pair_relations: dict[frozenset, set[str]] = defaultdict(set)
    for l in links:
        pair_relations[frozenset((l["source"], l["target"]))].add(l.get("relation", ""))

    for l in links:
        src = nodes_by_id.get(l["source"])
        tgt = nodes_by_id.get(l["target"])
        if not src or not tgt:
            continue
        rel = l.get("relation", "")
        conf = l.get("confidence", "EXTRACTED")
        score = l.get("confidence_score", 1.0)
        line = fmt_edge(src.get("label", l["source"]), rel, tgt.get("label", l["target"]),
                        conf, score, l.get("source_file", ""))
        meta = f"  - <!-- {ws_name} | {l['source']} | {rel} | {l['target']} -->"

        if conf == "AMBIGUOUS":
            buckets["amb_outright"].append((line, meta))
            continue

        if rel in PERSON_RELATIONS and is_org_or_place(src) and not is_org_or_place(tgt):
            buckets["direction_suspect"].append((line, meta))
            continue

        if conf == "INFERRED":
            if rel in {"co_attended", "discussed_with", "mentioned_by", "messages_with"} and score < 0.9:
                buckets["co_occurrence_inferred"].append((line, meta))
            elif score < threshold:
                buckets["low_conf_inferred"].append((line, meta))

        if rel in SYMMETRIC_RELATIONS:
            pair = frozenset((l["source"], l["target"]))
            if rel not in pair_relations[pair]:
                continue
            reverse_count = sum(
                1 for ll in links
                if ll["source"] == l["target"] and ll["target"] == l["source"] and ll.get("relation") == rel
            )
            if reverse_count == 0:
                buckets["missing_reciprocal"].append((line, meta))

    return buckets


def render_queue(scope: str, by_workspace: dict[str, dict[str, list]]) -> str:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    today = now[:10]
    total = sum(len(items) for ws_buckets in by_workspace.values() for items in ws_buckets.values())

    lines = [
        "---",
        "type: graph-audit",
        f"generated_at: {now}",
        f"scope: {scope}",
        f"total_items: {total}",
        "---",
        "",
        f"# Graph Audit — {today} — {scope}",
        "",
        "Mark each item then run `apply-audit.py` on this file.",
        "",
        "**Markers:**",
        "- `[x]` confirm (upgrade INFERRED→EXTRACTED, or keep edge as-is)",
        "- `[!]` reject (remove edge + blacklist this exact (src, rel, tgt) from future inference)",
        "- `[?]` still ambiguous (keep, will be re-surfaced on next audit pass)",
        "- `[ ]` unchecked (no decision yet — will be re-surfaced next pass)",
        "",
        "**Inline overrides** (after the edge line, on the same line):",
        "- ` → new_relation` to relabel the edge",
        "- ` ↔ flip` to reverse direction",
        "- ` ⇒ correct_target_slug` to redirect to a different target node",
        "",
    ]

    section_titles = {
        "direction_suspect": "Direction-suspect (institution acting as person, etc.)",
        "amb_outright": "AMBIGUOUS edges (graphify uncertain)",
        "low_conf_inferred": "Low-confidence INFERRED (below threshold)",
        "co_occurrence_inferred": "Co-occurrence INFERRED (mentioned/discussed_with/messages_with)",
        "missing_reciprocal": "Missing reciprocals on symmetric relations",
    }

    for ws_name, buckets in by_workspace.items():
        ws_total = sum(len(items) for items in buckets.values())
        if ws_total == 0:
            continue
        lines.append(f"## Workspace: `{ws_name}` ({ws_total} items)")
        lines.append("")
        for key, title in section_titles.items():
            items = buckets.get(key, [])
            if not items:
                continue
            lines.append(f"### {title} ({len(items)})")
            lines.append("")
            for line, meta in items:
                lines.append(f"- [ ] {line}")
                lines.append(meta)
            lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default="all", help="workspace name or 'all' (default: all)")
    ap.add_argument("--threshold", type=float, default=0.85,
                    help="INFERRED edges below this confidence go to low-conf bucket")
    ap.add_argument("--output", help="explicit output path (default: _queues/graph-audit-YYYY-MM-DD-<scope>.md)")
    args = ap.parse_args()

    if args.workspace == "all":
        workspaces = sorted(
            d.name for d in WORKSPACES_DIR.iterdir()
            if d.is_dir() and (d / "graphify-out" / "graph.json").exists()
        )
        scope = "all"
    else:
        workspaces = [args.workspace]
        scope = args.workspace

    if not workspaces:
        print("No workspaces with graphify-out/graph.json found.", file=sys.stderr)
        return 1

    by_workspace: dict[str, dict[str, list]] = {}
    for ws in workspaces:
        buckets = audit_workspace(ws, threshold=args.threshold)
        if buckets:
            by_workspace[ws] = buckets

    total = sum(
        len(items) for ws_buckets in by_workspace.values() for items in ws_buckets.values()
    )
    if total == 0:
        print(f"No ambiguous edges across {scope}.")
        return 1

    QUEUES_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).date().isoformat()
    out_path = (
        Path(args.output) if args.output
        else QUEUES_DIR / f"graph-audit-{today}-{scope}.md"
    )
    out_path.write_text(render_queue(scope, by_workspace))
    print(f"Wrote {total} items across {len(by_workspace)} workspace(s) to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
