"""manual/route.py — manual sources route to the workspace whose _inbox/ they were dropped into.

There is no API call here. The robot's own logic in _shell/bin/ingest-manual.py
walks each workspace's manual sources directly, so this route function is
identity-shaped: an item from workspace X stays in workspace X.
"""
from __future__ import annotations

SOURCE_NAME = "manual"
DEFAULT_UNROUTED = "skip"


def route(item: dict, workspaces_config: dict) -> list[str]:
    """Manual items carry their target workspace in `item['workspace']`."""
    ws = item.get("workspace")
    if ws and ws in workspaces_config:
        return [ws]
    return []
