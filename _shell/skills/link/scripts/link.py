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

import yaml

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


def parse_fm(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        sys.stderr.write(f"link: warning — failed to parse frontmatter ({exc}); treating as empty\n")
        fm = {}
    if not isinstance(fm, dict):
        fm = {}
    return fm, text[m.end():]


def serialize_fm(fm: dict, body: str) -> str:
    out = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return f"---\n{out}---\n" + body.lstrip("\n")


def parse_relationships(text: str) -> list[dict]:
    fm, _body = parse_fm(text)
    rels = fm.get("relationships")
    if not isinstance(rels, list):
        return []
    out: list[dict] = []
    for r in rels:
        if isinstance(r, dict) and "type" in r and "target" in r:
            out.append(dict(r))
    return out


def write_edges(text: str, edges: list[dict]) -> str:
    fm, body = parse_fm(text)
    fm["relationships"] = edges
    return serialize_fm(fm, body)


def add_edge(page: Path, edge: dict) -> bool:
    text = page.read_text(errors="ignore")
    edges = parse_relationships(text)
    if any(e.get("type") == edge["type"] and e.get("target") == edge["target"] for e in edges):
        return False
    edges.append(edge)
    page.write_text(write_edges(text, edges))
    return True


def remove_edge(page: Path, edge: dict) -> bool:
    text = page.read_text(errors="ignore")
    edges = parse_relationships(text)
    new_edges = [e for e in edges if not (e.get("type") == edge["type"] and e.get("target") == edge["target"])]
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
        fwd_edge["note"] = args.note

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
            rev_edge["note"] = args.note
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
    edges = parse_relationships(p.read_text(errors="ignore"))
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
