"""
Routing template for a new source. Copy to `_shell/stages/ingest/<source>/route.py`
and adapt.

Contract:
    def route(item: dict, workspaces_config: dict) -> list[str]

Where:
    item                — source-native item (provider's response format).
    workspaces_config   — {ws_slug: parsed_sources_yaml} for every workspace.

Returns:
    Sorted, deduplicated list of workspace slugs the item should be written to.
    Empty list = skip.
"""
from __future__ import annotations


SOURCE_NAME = "<source>"
UNROUTED_DEFAULT = "route_to_main"   # or "skip" — adapt per source policy
MAIN_WS_FALLBACK = ("main", "personal")


def matches_include(item: dict, include_rules: list[str]) -> bool:
    """Translate include rules into a boolean check for this item.

    Most rules are predicate strings; the routing implementation parses them.
    Until the source ships a real predicate language, treat empty/missing as 'match all'.
    """
    if not include_rules:
        return True
    # TODO: per-source predicate evaluation. Today: include-all if rules present.
    return True


def matches_exclude(item: dict, exclude_rules: list[str]) -> bool:
    if not exclude_rules:
        return False
    return False


def main_workspace(workspaces_config: dict) -> str | None:
    for cand in MAIN_WS_FALLBACK:
        if cand in workspaces_config:
            return cand
    return None


def route(item: dict, workspaces_config: dict) -> list[str]:
    matched: set[str] = set()
    for ws, cfg in workspaces_config.items():
        sources = (cfg or {}).get("sources") or {}
        block = sources.get(SOURCE_NAME) if isinstance(sources, dict) else None
        if block is None:
            # Legacy list shape: [{type: <source>, config: {...}}, ...]
            if isinstance(sources, list):
                block = next(
                    (s.get("config", {}) for s in sources if s.get("type") == SOURCE_NAME),
                    None,
                )
        if block is None:
            continue
        include = block.get("api_query", {}).get("include", []) if isinstance(block, dict) else []
        exclude = block.get("api_query", {}).get("exclude", []) if isinstance(block, dict) else []
        if matches_include(item, include) and not matches_exclude(item, exclude):
            matched.add(ws)

    if not matched:
        if UNROUTED_DEFAULT == "skip":
            return []
        main = main_workspace(workspaces_config)
        if main is not None:
            return [main]
        return []

    return sorted(matched)
