"""Shared test setup. Adds the substage dir to sys.path so tests can
import sibling modules (slug, prosemirror, render, ...) without making
the dir a Python package."""
import sys
from pathlib import Path

SUBSTAGE_DIR = Path(__file__).resolve().parent.parent
if str(SUBSTAGE_DIR) not in sys.path:
    sys.path.insert(0, str(SUBSTAGE_DIR))

FIXTURES = Path(__file__).resolve().parent / "fixtures"
