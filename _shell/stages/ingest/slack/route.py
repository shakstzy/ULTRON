"""slack/route.py — workspace + channel/DM allowlist routing."""
from __future__ import annotations

SOURCE_NAME = "slack"
DEFAULT_UNROUTED = "route_to_main"
MAIN_WS_FALLBACK = ("main", "personal")


def _slack_block(ws_cfg: dict) -> dict | None:
    sources = (ws_cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get(SOURCE_NAME)
    if isinstance(sources, list):
        for s in sources:
            if s.get("type") == SOURCE_NAME:
                return s.get("config") or s
    return None


def _channel_match(meta: dict, channels: list[str]) -> bool:
    if not channels:
        return False
    name = (meta.get("channel_name") or "").lstrip("#")
    return name in channels


def _dm_match(meta: dict, participants_slugs: list[str]) -> bool:
    """Match DMs by the OTHER participant's slug. The user always appears
    in their own DMs, so the user's canonical slug is excluded before
    matching — otherwise putting "adithya-shak-kumar" in `include_dms_with`
    would route every DM."""
    if not participants_slugs:
        return False
    if meta.get("channel_type") not in {"im", "mpim"}:
        return False
    parts = {(p.get("slug") or "").lower() for p in meta.get("participants") or []}
    parts.discard("adithya-shak-kumar")  # always-present self
    return any(s in parts for s in participants_slugs)


def _main_workspace(workspaces_config: dict) -> str | None:
    for cand in MAIN_WS_FALLBACK:
        if cand in workspaces_config:
            return cand
    return None


def route(meta: dict, workspaces_config: dict) -> list[str]:
    matched: set[str] = set()
    for ws, cfg in workspaces_config.items():
        block = _slack_block(cfg)
        if not block:
            continue
        if meta.get("slack_workspace_id") and block.get("workspace_id") and meta["slack_workspace_id"] != block["workspace_id"]:
            continue
        if _channel_match(meta, block.get("channels") or []):
            matched.add(ws)
            continue
        if _dm_match(meta, block.get("include_dms_with") or []):
            matched.add(ws)

    if not matched:
        defaults = {
            (cfg or {}).get("_workspace_meta", {}).get("ingest_unrouted_default", DEFAULT_UNROUTED)
            for ws, cfg in workspaces_config.items()
            if _slack_block(cfg) is not None
        }
        if "skip" in defaults:
            return []
        main = _main_workspace(workspaces_config)
        if main is not None:
            matched.add(main)
    return sorted(matched)
