#!/usr/bin/env python3
"""detect_canonical.py — heuristic canonical-slug picker for the alias skill.

Usage:
    detect_canonical.py <slug-a> <slug-b> [<slug-n>...] [--type <type>]
"""
from __future__ import annotations

import argparse
import sys

# Reuse alias.py helpers via import path manipulation when called standalone.
import os
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
sys.path.insert(0, str(ULTRON_ROOT / "_shell" / "skills" / "alias" / "scripts"))

from alias import detect_canonical   # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--type")
    args = ap.parse_args()
    print(detect_canonical(args.slugs, args.type))
    return 0


if __name__ == "__main__":
    sys.exit(main())
