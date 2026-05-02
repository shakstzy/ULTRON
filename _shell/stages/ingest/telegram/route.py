"""telegram/route.py — skeleton, allowlist routing like iMessage."""
from __future__ import annotations

SOURCE_NAME = "telegram"
DEFAULT_UNROUTED = "skip"


def _block(ws_cfg: dict) -> dict | None:
    sources = (ws_cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get(SOURCE_NAME)
    return None


def route(item: dict, workspaces_config: dict) -> list[str]:
    matched: set[str] = set()
    for ws, cfg in workspaces_config.items():
        block = _block(cfg)
        if not block:
            continue
        if (block.get("chats") or block.get("channels") or block.get("groups")):
            matched.add(ws)
    return sorted(matched)
