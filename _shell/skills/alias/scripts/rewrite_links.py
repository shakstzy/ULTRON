#!/usr/bin/env python3
"""rewrite_links.py — delegate to _shell/bin/rename-slug.py to rewrite wikilinks
from an alias slug to a canonical slug across one or all workspaces.

Usage:
    rewrite_links.py <old> <new> [--workspace <ws>]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--workspace")
    args = ap.parse_args()
    cmd = [sys.executable, str(ULTRON_ROOT / "_shell" / "bin" / "rename-slug.py"), args.old, args.new]
    if args.workspace:
        cmd += ["--workspace", args.workspace]
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
