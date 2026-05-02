#!/usr/bin/env python3
"""
link.py — assert / remove / list structured relationships between entities.

Usage:
    link.py add <subject> <relation> <object> [--directed] [--symmetric] [--note "..."] [--workspace <ws>]
    link.py remove <subject> <relation> <object> [--workspace <ws>]
    link.py list <slug>
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


SYMMETRIC = {
    "colleague", "friend", "partner", "married_to", "co_founded",
    "co_author", "sibling", "roommate",
}

INVERSE = {
    "reports_to": "manages",
    "manages": "reports_to",
    "mentors": "mentee_of",
    "mentee_of": "mentors",
    "invested_in": "investor_of",
    "investor_of": "invested_in",
    "founded": "founder_of",
    "founder_of": "founded",
    "client_of": "vendor_of",
    "vendor_of": "client_of",
    "parent_of": "child_of",
    "child_of": "parent_of",
    "acquired": "acquired_by",
    "acquired_by": "acquired",
    "subsidiary_of": "parent_company_of",
    "parent_company_of": "subsidiary_of",
    "introduced": "introduced_by",
    "introduced_by": "introduced",
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.+?)\n---\s*\n?", re.DOTALL)
RELATIONSHIPS_RE = re.compile(r"^relationships:\s*\n((?:\s+-\s+\{.*?\}\s*\n)+)", re.MULTILINE)
EDGE_RE = re.compile(r"-\s*\{\s*type:\s*([^,]+),\s*target:\s*([^,]+),(.*?)\}\s*$")


def find_page(slug: str, workspace: str | None = None) -> Path | None:
    """Prefer global stub, then workspace pages. Returns None if not found."""
    global_dir = ULTRON_ROOT / "_global" / "entities"
    if global_dir.exists():
        for p in global_dir.rglob(f"{slug}.md"):
            return p
    workspaces_dir = ULTRON_ROOT / "workspaces"
    if workspaces_dir.exists():
        for ws_dir in sorted(workspaces_dir.iterdir()):
            if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
                continue
            if workspace and ws_dir.name != workspace:
                continue
            entities = ws_dir / "wiki" / "entities"
            if entities.exists():
                for p in entities.rglob(f"{slug}.md"):
                    return p
    return None


def parse_relationships(text: str) -> tuple[list[dict], int, int]:
    """Return (edges, start_offset, end_offset) — indices of the relationships block in text."""
    m_fm = FRONTMATTER_RE.match(text)
    if not m_fm:
        return [], 0, 0
    block = m_fm.group(1)
    m_rel = RELATIONSHIPS_RE.search(block)
    if not m_rel:
        return [], 0, 0
    edges_block = m_rel.group(1)
    edges: list[dict] = []
    for line in edges_block.splitlines():
        line = line.strip()
        m_e = EDGE_RE.match(line)
        if not m_e:
            continue
        rel_type = m_e.group(1).strip()
        target = m_e.group(2).strip()
        rest = m_e.group(3).strip()
        kv: dict[str, str] = {}
        for part in re.split(r",\s*(?=[a-z_]+:)", rest):
            if ":" not in part:
                continue
            k, _, v = part.partition(":")
            kv[k.strip()] = v.strip().strip('"').strip("'")
        edges.append({"type": rel_type, "target": target, **kv})
    fm_start = m_fm.start(1)
    return edges, fm_start + m_rel.start(), fm_start + m_rel.end()


def write_edges(text: str, edges: list[dict]) -> str:
    """Replace (or insert) the relationships block."""
    lines_out = ["relationships:"]
    for e in edges:
        kv = ", ".join(f"{k}: {v}" for k, v in e.items())
        lines_out.append(f"  - {{ {kv} }}")
    edges_block = "\n".join(lines_out) + "\n"

    m_fm = FRONTMATTER_RE.match(text)
    if not m_fm:
        new_fm = f"---\n{edges_block}---\n"
        return new_fm + text
    block = m_fm.group(1)
    m_rel = RELATIONSHIPS_RE.search(block)
    if m_rel:
        new_block = block[:m_rel.start()] + edges_block + block[m_rel.end():]
    else:
        new_block = block.rstrip() + "\n" + edges_block
    return f"---\n{new_block}---\n" + text[m_fm.end():].lstrip("\n")


def add_edge(page: Path, edge: dict) -> bool:
    text = page.read_text(errors="ignore")
    edges, _, _ = parse_relationships(text)
    if any(e["type"] == edge["type"] and e["target"] == edge["target"] for e in edges):
        return False
    edges.append(edge)
    page.write_text(write_edges(text, edges))
    return True


def remove_edge(page: Path, edge: dict) -> bool:
    text = page.read_text(errors="ignore")
    edges, _, _ = parse_relationships(text)
    new_edges = [e for e in edges if not (e["type"] == edge["type"] and e["target"] == edge["target"])]
    if len(new_edges) == len(edges):
        return False
    page.write_text(write_edges(text, new_edges))
    return True


def cmd_add(args: argparse.Namespace) -> int:
    subject_page = find_page(args.subject, args.workspace)
    object_page = find_page(args.object, args.workspace)
    if subject_page is None:
        sys.stderr.write(f"link: subject not found: {args.subject}\n")
        return 1
    if object_page is None:
        sys.stderr.write(f"link: object not found: {args.object}\n")
        return 1

    today = date.today().isoformat()
    fwd_edge = {"type": args.relation, "target": args.object, "asserted": today}
    if args.note:
        fwd_edge["note"] = f'"{args.note}"'

    if add_edge(subject_page, fwd_edge):
        print(f"added: {args.subject} -- {args.relation} --> {args.object}")
    else:
        print(f"already present: {args.subject} -- {args.relation} --> {args.object}")

    inverse = None
    if args.directed and not args.symmetric:
        inverse = INVERSE.get(args.relation)
    elif args.symmetric or args.relation in SYMMETRIC:
        inverse = args.relation
    elif args.relation in INVERSE:
        inverse = INVERSE[args.relation]

    if inverse:
        rev_edge = {"type": inverse, "target": args.subject, "asserted": today}
        if args.note:
            rev_edge["note"] = f'"{args.note}"'
        if add_edge(object_page, rev_edge):
            print(f"added (reciprocal): {args.object} -- {inverse} --> {args.subject}")

    subprocess.run([sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "build-backlinks.py")], check=False)
    rc = subprocess.run([sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "check-routes.py")], check=False).returncode
    return rc


def cmd_remove(args: argparse.Namespace) -> int:
    subject_page = find_page(args.subject, args.workspace)
    object_page = find_page(args.object, args.workspace)
    if subject_page is None or object_page is None:
        sys.stderr.write("link: subject or object not found\n")
        return 1
    fwd = {"type": args.relation, "target": args.object}
    rev_type = INVERSE.get(args.relation, args.relation if args.relation in SYMMETRIC else None)

    removed_fwd = remove_edge(subject_page, fwd)
    removed_rev = False
    if rev_type:
        rev = {"type": rev_type, "target": args.subject}
        removed_rev = remove_edge(object_page, rev)
    print(f"removed fwd={removed_fwd} rev={removed_rev}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    p = find_page(args.slug)
    if p is None:
        sys.stderr.write(f"link: not found: {args.slug}\n")
        return 1
    edges, _, _ = parse_relationships(p.read_text(errors="ignore"))
    if not edges:
        print(f"{args.slug}: no relationships")
        return 0
    print(f"{args.slug}:")
    for e in edges:
        print(f"  - {e['type']} -> {e['target']}" + (f"   ({e['note']})" if e.get('note') else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("subject")
    a.add_argument("relation")
    a.add_argument("object")
    a.add_argument("--directed", action="store_true")
    a.add_argument("--symmetric", action="store_true")
    a.add_argument("--note")
    a.add_argument("--workspace")

    r = sub.add_parser("remove")
    r.add_argument("subject")
    r.add_argument("relation")
    r.add_argument("object")
    r.add_argument("--workspace")

    l = sub.add_parser("list")
    l.add_argument("slug")

    args = ap.parse_args()
    if args.cmd == "add":
        return cmd_add(args)
    if args.cmd == "remove":
        return cmd_remove(args)
    if args.cmd == "list":
        return cmd_list(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
