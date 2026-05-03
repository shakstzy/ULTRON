"""imessage/route.py — strict allowlist routing. Defaults to skip when no workspace claims a contact."""
from __future__ import annotations

SOURCE_NAME = "imessage"
DEFAULT_UNROUTED = "skip"          # privacy-first


def _imessage_block(ws_cfg: dict) -> dict | None:
    sources = (ws_cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get(SOURCE_NAME)
    if isinstance(sources, list):
        for s in sources:
            if s.get("type") == SOURCE_NAME:
                return s.get("config") or s
    return None


def _contact_match(item: dict, contacts: list[dict]) -> bool:
    if not contacts:
        return False
    item_slug = (item.get("contact_slug") or "").lower()
    item_handles = {h.lower() for h in (item.get("contact_handles") or [])}
    for c in contacts:
        if (c.get("slug") or "").lower() == item_slug:
            return True
        if any(h.lower() in item_handles for h in (c.get("handles") or [])):
            return True
    return False


def _group_match(item: dict, groups: list[dict]) -> bool:
    # NOTE (Codex review): `group_identifier` and `contact_name` are mutable
    # display strings. The stable identity is `chat.guid`. Routing-session
    # work: switch the matcher to prefer `g.get("chat_guid")` against
    # `item.get("chat_guid")` and fall back to identifier only when the
    # workspace's sources.yaml omits chat_guid (deprecated path).
    if not groups:
        return False
    if item.get("contact_type") != "group":
        return False
    item_slug = (item.get("contact_slug") or "").lower()
    item_id = item.get("group_identifier") or item.get("contact_name") or ""
    item_guid = item.get("chat_guid") or ""
    for g in groups:
        if g.get("chat_guid") and item_guid and g["chat_guid"] == item_guid:
            return True
        if (g.get("slug") or "").lower() == item_slug:
            return True
        if g.get("identifier") and g["identifier"] == item_id:
            return True
    return False


def route(item: dict, workspaces_config: dict) -> list[str]:
    matched: set[str] = set()
    for ws, cfg in workspaces_config.items():
        block = _imessage_block(cfg)
        if not block:
            continue
        if item.get("contact_type") == "group":
            if _group_match(item, block.get("groups") or []):
                matched.add(ws)
        else:
            if _contact_match(item, block.get("contacts") or []):
                matched.add(ws)
    return sorted(matched)
