"""notion/route.py — skeleton."""
from __future__ import annotations

SOURCE_NAME = "notion"
DEFAULT_UNROUTED = "route_to_main"
MAIN_WS_FALLBACK = ("main", "personal")


def _block(ws_cfg: dict) -> dict | None:
    sources = (ws_cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get(SOURCE_NAME)
    return None


def route(item: dict, workspaces_config: dict) -> list[str]:
    matched: set[str] = set()
    for ws, cfg in workspaces_config.items():
        if _block(cfg) is not None:
            matched.add(ws)
    if not matched:
        for cand in MAIN_WS_FALLBACK:
            if cand in workspaces_config:
                return [cand]
        return []
    return sorted(matched)
