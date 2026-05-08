#!/usr/bin/env python3
"""
review-candidates.py — interactive CLI for the candidate-edges queue.

Reads `_shell/audit/candidate_edges.jsonl`, walks pending candidates one
at a time, asks accept / reject / skip / quit. On accept, dispatches to
the existing `link` or `alias` skill. Rejected candidates land in
`_shell/audit/rejected_edges.jsonl` so the generator never re-emits them.

Usage:
    review-candidates.py [--limit 10] [--kind alias|link] [--list] [--non-interactive]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
AUDIT_DIR = ULTRON_ROOT / "_shell" / "audit"
CANDIDATES_FILE = AUDIT_DIR / "candidate_edges.jsonl"
REJECTED_FILE = AUDIT_DIR / "rejected_edges.jsonl"

LINK_SCRIPT = ULTRON_ROOT / "_shell" / "skills" / "link" / "scripts" / "link.py"
ALIAS_SCRIPT = ULTRON_ROOT / "_shell" / "skills" / "alias" / "scripts" / "alias.py"


def load_candidates() -> list[dict]:
    if not CANDIDATES_FILE.exists():
        return []
    out: list[dict] = []
    for line in CANDIDATES_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def write_candidates(rows: list[dict]) -> None:
    CANDIDATES_FILE.write_text("\n".join(json.dumps(r) for r in rows) + ("\n" if rows else ""))


def append_rejected(c: dict) -> None:
    REJECTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    rej = dict(c)
    rej["status"] = "rejected"
    rej["rejected_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with REJECTED_FILE.open("a") as f:
        f.write(json.dumps(rej) + "\n")


def render_card(c: dict, idx: int, total: int) -> str:
    lines = [
        f"\n[{idx + 1}/{total}] {c['kind'].upper()} candidate (confidence {c['confidence']})",
        f"  subj: {c['subj_label']!r}  (id={c['subj']})",
        f"  obj:  {c['obj_label']!r}  (id={c['obj']})",
        f"  type: {c['type']}",
        f"  proposed by: {c['proposed_by']}",
        f"  reason: {c['reason']}",
    ]
    ev = c.get("evidence")
    if ev:
        lines.append(f"  evidence: {json.dumps(ev)}")
    return "\n".join(lines)


def apply_accept(c: dict) -> tuple[bool, str]:
    """Fire the existing skill. Returns (success, message)."""
    if c["kind"] == "alias":
        # alias merge <alias-slug> <canonical-slug> --canonical <canonical>
        cmd = [
            sys.executable, str(ALIAS_SCRIPT),
            "merge", c["subj"], c["obj"],
            "--canonical", c["obj"],
        ]
    elif c["kind"] == "link":
        cmd = [
            sys.executable, str(LINK_SCRIPT),
            "add", c["subj"], c["type"], c["obj"],
            "--note", f"accepted from candidate {c['id']}",
        ]
    else:
        return False, f"unknown kind: {c['kind']}"

    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode == 0:
        return True, out.strip().splitlines()[-1] if out.strip() else "ok"
    # link/alias return non-zero when check-routes flags pre-existing broken
    # wikilinks. Treat the actual edge write as success unless stdout/stderr
    # signal a real failure.
    if "added" in out or "Canonical:" in out:
        return True, "(applied; check-routes flagged unrelated pre-existing broken links)"
    return False, out.strip().splitlines()[-1] if out.strip() else f"exit {proc.returncode}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10,
                    help="Review at most N pending candidates per session (default: 10).")
    ap.add_argument("--kind", choices=["alias", "link"], default=None,
                    help="Filter to a single candidate kind.")
    ap.add_argument("--list", action="store_true",
                    help="Print the queue summary and exit (no review).")
    ap.add_argument("--non-interactive", action="store_true",
                    help="List the next N candidates as JSON and exit.")
    args = ap.parse_args()

    rows = load_candidates()
    pending = [r for r in rows if r.get("status") == "pending"]
    if args.kind:
        pending = [r for r in pending if r.get("kind") == args.kind]

    if args.list:
        from collections import Counter
        kinds = Counter(r["kind"] for r in pending)
        accepted = sum(1 for r in rows if r.get("status") == "accepted")
        print(f"pending: {len(pending)}  ({dict(kinds)})")
        print(f"accepted (already actioned): {accepted}")
        print(f"file: {CANDIDATES_FILE.relative_to(ULTRON_ROOT)}")
        return 0

    if not pending:
        print("no pending candidates. run generate-candidate-edges.py to refresh.")
        return 0

    if args.non_interactive:
        for c in pending[: args.limit]:
            print(json.dumps(c))
        return 0

    batch = pending[: args.limit]
    print(f"reviewing {len(batch)} of {len(pending)} pending candidates. "
          f"y=accept · n=reject · s=skip · q=quit")

    accepted_count = 0
    rejected_count = 0
    skipped_count = 0

    for i, c in enumerate(batch):
        print(render_card(c, i, len(batch)))
        while True:
            resp = input("  [y/n/s/q]> ").strip().lower()
            if resp in ("y", "n", "s", "q"):
                break
            print("  please enter y, n, s, or q")

        if resp == "q":
            break
        if resp == "s":
            skipped_count += 1
            continue
        if resp == "n":
            c["status"] = "rejected"
            c["rejected_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            append_rejected(c)
            rejected_count += 1
            print("  rejected (will not resurface)")
            continue
        # accept
        ok, msg = apply_accept(c)
        if ok:
            c["status"] = "accepted"
            c["accepted_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            accepted_count += 1
            print(f"  accepted: {msg}")
        else:
            print(f"  FAILED: {msg}  (left as pending)")

    write_candidates(rows)

    print(f"\nsummary: accepted={accepted_count}  rejected={rejected_count}  "
          f"skipped={skipped_count}  remaining_pending={sum(1 for r in rows if r.get('status') == 'pending')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
