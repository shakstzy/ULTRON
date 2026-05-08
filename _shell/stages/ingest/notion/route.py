"""notion/route.py — workspace fan-out for notion source.

The runner walks `workspaces/<ws>/config/sources.yaml`'s `sources.notion.targets`
list per workspace. There is no shared "all targets" pool that would need
multi-workspace fan-out — each target is owned by one workspace by design.

Kept for parity with other sources in case future targets are shared
(e.g. a global page mirrored into multiple workspaces).
"""
from __future__ import annotations

SOURCE_NAME = "notion"
DEFAULT_UNROUTED = "skip"
MAIN_WS_FALLBACK = ("main", "personal")


def _block(ws_cfg: dict) -> dict | None:
    sources = (ws_cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get(SOURCE_NAME)
    return None


def route(item: dict, workspaces_config: dict) -> list[str]:
    """Return workspaces that subscribe to a given notion target.

    `item` shape: {"id": <notion-id>, "kind": "page"|"database", "label": str|None}
    """
    matched: set[str] = set()
    target_id = (item or {}).get("id", "").replace("-", "").lower()
    for ws, cfg in workspaces_config.items():
        block = _block(cfg)
        if not block:
            continue
        for tgt in (block.get("targets") or []):
            tgt_id = (tgt.get("id") or tgt.get("url") or "").replace("-", "").lower()
            if tgt_id and tgt_id.endswith(target_id):
                matched.add(ws)
                break
    return sorted(matched) if matched else []
