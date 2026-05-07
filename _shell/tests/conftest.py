"""Shared test setup. Adds _shell/bin to sys.path so tests can
import the CLI scripts as modules via importlib."""
import sys
from pathlib import Path

ULTRON_ROOT = Path(__file__).resolve().parents[2]
BIN_DIR = ULTRON_ROOT / "_shell" / "bin"
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))

FIXTURES = Path(__file__).resolve().parent / "fixtures"
