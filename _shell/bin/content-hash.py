#!/usr/bin/env python3
"""
content-hash.py — Blake3 hash of file content (stdout).

Usage:
    content-hash.py <path>
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from blake3 import blake3
except ImportError:
    sys.stderr.write("missing dep: pip install blake3\n")
    sys.exit(2)


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write("usage: content-hash.py <path>\n")
        return 2
    p = Path(sys.argv[1])
    if not p.exists():
        sys.stderr.write(f"not found: {p}\n")
        return 1
    print(blake3(p.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
