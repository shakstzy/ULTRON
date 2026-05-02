"""whatsapp/route.py — skeleton, allowlist routing like iMessage."""
from __future__ import annotations

SOURCE_NAME = "whatsapp"
DEFAULT_UNROUTED = "skip"


def _block(ws_cfg: dict) -> dict | None:
    sources = (ws_cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get(SOURCE_NAME)
    return None


def route(item: dict, workspaces_config: dict) -> list[str]:
    # Without contact / group allowlists wired, default to skip.
    matched: set[str] = set()
    for ws, cfg in workspaces_config.items():
        block = _block(cfg)
        if not block:
            continue
        # When implemented, mirror imessage/route.py allowlist matching here.
        # For the skeleton: refuse to route until the workspace explicitly allowlists.
        if (block.get("contacts") or block.get("groups")):
            matched.add(ws)
    return sorted(matched)
