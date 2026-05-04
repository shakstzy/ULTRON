"""
drive/route.py — given a Drive file and the parsed sources.yaml of every
workspace, decide which workspace(s) get a copy.

Public API:
    route(file_meta, workspaces_config) -> list[{workspace, rule}]

`file_meta` is a Drive file dict normalized to the helpers below. Required
keys:
    drive_account              # full email
    drive_designated_folder_id # the designated root that this file rolled up
                               # under (set by the ingest robot when it
                               # enumerates a designated folder, NOT
                               # something the API gives you)

`workspaces_config` is {ws_slug: parsed_sources_yaml}.

Routing semantics (v1):
  - For each workspace's `sources.drive` block: scan
    `accounts[].folders[].id`. A workspace matches when one of its
    folder IDs equals `file_meta["drive_designated_folder_id"]` AND the
    `accounts[].account` equals `file_meta["drive_account"]`.
  - Folder claims are exclusive in v1. If two workspaces claim the same
    folder ID, the validator (validate-drive-config.py) flags it; this
    function still returns both, sorted, leaving the operator to fix the
    config.
  - No `<unrouted-default>` fallback. A Drive file is only ever ingested
    via a designated folder claim, so an "unrouted" Drive file is a bug
    upstream (the robot shouldn't have fetched it).
  - `also_route_to` and folder glob patterns are deferred to v1.5.

Returned shape mirrors gmail/route.py: `[{workspace, rule}]`, sorted by
workspace. The rule is `folder:<designated_folder_id>` so the ledger row
records what claimed the file.
"""
from __future__ import annotations

SOURCE_NAME = "drive"


def _drive_block(ws_cfg: dict) -> dict | None:
    sources = (ws_cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get(SOURCE_NAME)
    if isinstance(sources, list):
        for s in sources:
            if isinstance(s, dict) and s.get("type") == SOURCE_NAME:
                return s.get("config") or s
    return None


def _normalize_accounts(block: dict) -> list[dict]:
    """Drive block uses `accounts: [{account, folders: [...]}]`."""
    accts = block.get("accounts")
    if isinstance(accts, list):
        return [a for a in accts if isinstance(a, dict)]
    return []


def route(file_meta: dict, workspaces_config: dict) -> list[dict]:
    """Returns list of {workspace, rule} entries, sorted by workspace."""
    file_account = (file_meta.get("drive_account") or "").lower()
    file_folder_id = file_meta.get("drive_designated_folder_id")
    if not file_account or not file_folder_id:
        return []

    matched: dict[str, str] = {}

    for ws, cfg in workspaces_config.items():
        block = _drive_block(cfg)
        if not block:
            continue
        for acct in _normalize_accounts(block):
            if (acct.get("account") or "").lower() != file_account:
                continue
            for folder in acct.get("folders") or []:
                if not isinstance(folder, dict):
                    continue
                if folder.get("id") == file_folder_id:
                    matched[ws] = f"folder:{file_folder_id}"
                    break

    return [{"workspace": ws, "rule": rule} for ws, rule in sorted(matched.items())]
