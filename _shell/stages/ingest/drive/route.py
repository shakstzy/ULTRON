"""drive/route.py — see _template/route.py for the contract."""
from __future__ import annotations

import fnmatch

SOURCE_NAME = "drive"
DEFAULT_UNROUTED = "route_to_main"
MAIN_WS_FALLBACK = ("main", "personal")


def _drive_block(ws_cfg: dict) -> dict | None:
    sources = (ws_cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get(SOURCE_NAME)
    if isinstance(sources, list):
        for s in sources:
            if s.get("type") == SOURCE_NAME:
                return s.get("config") or s
    return None


def _folder_match(file_meta: dict, folders: list[str]) -> bool:
    if not folders:
        return True
    parents = file_meta.get("parent_paths") or []
    for pat in folders:
        for parent in parents:
            if fnmatch.fnmatch(parent, pat) or parent.startswith(pat):
                return True
    return False


def _mime_match(file_meta: dict, allowlist: list[str]) -> bool:
    if not allowlist:
        return True
    mime = file_meta.get("mime") or ""
    return any(fnmatch.fnmatch(mime, p) for p in allowlist)


def _main_workspace(workspaces_config: dict) -> str | None:
    for cand in MAIN_WS_FALLBACK:
        if cand in workspaces_config:
            return cand
    return None


def route(file_meta: dict, workspaces_config: dict) -> list[str]:
    matched: set[str] = set()
    for ws, cfg in workspaces_config.items():
        block = _drive_block(cfg)
        if not block:
            continue
        if file_meta.get("account") and block.get("account") and block["account"] != file_meta["account"]:
            continue
        folders = block.get("folders") or []
        mimes = block.get("mime_types") or []
        if _folder_match(file_meta, folders) and _mime_match(file_meta, mimes):
            matched.add(ws)

    if not matched:
        defaults = {
            (cfg or {}).get("_workspace_meta", {}).get("ingest_unrouted_default", DEFAULT_UNROUTED)
            for ws, cfg in workspaces_config.items()
            if _drive_block(cfg) is not None
        }
        if "skip" in defaults:
            return []
        main = _main_workspace(workspaces_config)
        if main is not None:
            matched.add(main)
    return sorted(matched)
