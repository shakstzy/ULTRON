#!/usr/bin/env python3
"""
check-budget.py — abort if month-to-date Anthropic API spend exceeds cap.

Reads `_shell/budget.yaml` (mtd_cap_usd) and the local tally file
`_logs/anthropic-mtd.json`. The tally is updated by post-run hooks (not yet
implemented; hook is a TODO once Adithya moves off the Max sub).

Exit 0 if under cap; exit 1 if over.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def load_yaml(path: Path) -> dict:
    """Minimal YAML parser for the simple budget.yaml shape (key: value, no nesting)."""
    out: dict[str, object] = {}
    if not path.exists():
        return out
    for raw in path.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip()
        # Strip inline comment.
        if "#" in val:
            val = val.split("#", 1)[0].strip()
        if not val:
            continue
        try:
            out[key.strip()] = int(val)
            continue
        except ValueError:
            pass
        try:
            out[key.strip()] = float(val)
            continue
        except ValueError:
            pass
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def main() -> int:
    budget_path = ULTRON_ROOT / "_shell" / "budget.yaml"
    tally_path = ULTRON_ROOT / "_logs" / "anthropic-mtd.json"

    budget = load_yaml(budget_path)
    cap = float(budget.get("mtd_cap_usd", 0) or 0)

    spent = 0.0
    if tally_path.exists():
        try:
            tally = json.loads(tally_path.read_text())
            spent = float(tally.get("usd_mtd", 0) or 0)
        except (json.JSONDecodeError, ValueError):
            spent = 0.0

    if cap and spent >= cap:
        sys.stderr.write(f"check-budget: ${spent:.2f} >= cap ${cap:.2f}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
