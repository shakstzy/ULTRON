"""apple-health/route.py — health metrics route to workspaces with health subscriptions."""
from __future__ import annotations

SOURCE_NAME = "apple-health"
DEFAULT_UNROUTED = "skip"


def _block(ws_cfg: dict) -> dict | None:
    sources = (ws_cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get(SOURCE_NAME)
    if isinstance(sources, list):
        for s in sources:
            if s.get("type") == SOURCE_NAME:
                return s.get("config") or s
    return None


def route(item: dict, workspaces_config: dict) -> list[str]:
    matched = sorted({ws for ws, cfg in workspaces_config.items() if _block(cfg) is not None})
    return matched
