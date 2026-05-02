"""apple-contacts/route.py — apple-contacts always routes to _global, not workspaces.

This module exists to satisfy the universal stage shape. The contacts-sync
skill bypasses the workspace router pattern entirely.
"""
from __future__ import annotations

SOURCE_NAME = "apple-contacts"
DEFAULT_UNROUTED = "global"


def route(item: dict, workspaces_config: dict) -> list[str]:
    """Always returns the special ['_global'] sentinel; the runner writes to _global/entities/people/."""
    return ["_global"]
