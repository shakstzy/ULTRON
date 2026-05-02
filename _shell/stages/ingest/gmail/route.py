"""
gmail/route.py — given a fetched Gmail thread + the parsed sources.yaml of
every workspace, decide which workspace(s) get a copy.

Public API:
    route(thread, workspaces_config) -> list[str]

`thread` is a Gmail API thread payload normalized to the helpers below.
`workspaces_config` is {ws_slug: parsed_sources_yaml}.

Routing semantics:
  - For each workspace's `sources.gmail` block: evaluate include rules and
    exclude rules against the thread. A workspace matches when at least
    one include rule fires AND no exclude rule fires.
  - Empty include set → match-all (subject to excludes).
  - If the thread matches no workspace, return the unrouted default
    ("route_to_main" → fallback to main / personal workspace; "skip" → []).
  - `also_route_to` extras append additional workspaces.
  - Conflict policy: fork. Return the deduplicated, sorted destination set.
"""
from __future__ import annotations

import fnmatch
import re
from typing import Iterable

SOURCE_NAME = "gmail"
DEFAULT_UNROUTED = "route_to_main"
MAIN_WS_FALLBACK = ("main", "personal")


def _participant_matches(thread: dict, predicate: str) -> bool:
    """`from:foo@*`, `to:*@eclipse.audio`, etc."""
    if ":" not in predicate:
        return False
    role, pat = predicate.split(":", 1)
    role = role.strip().lower()
    pat = pat.strip().lower()
    for p in thread.get("participants", []):
        roles = {r.lower() for r in p.get("roles", [])}
        email = (p.get("email") or "").lower()
        if role == "from" and "from" not in roles:
            continue
        if role == "to" and "to" not in roles:
            continue
        if role == "cc" and "cc" not in roles:
            continue
        if role == "any" or role in {"from", "to", "cc"}:
            if fnmatch.fnmatch(email, pat):
                return True
    return False


def _label_matches(thread: dict, predicate: str) -> bool:
    """`label:Eclipse`, `label:Eclipse/Investors`."""
    if not predicate.lower().startswith("label:"):
        return False
    target = predicate.split(":", 1)[1].strip()
    return any(label == target for label in thread.get("labels", []))


def _subject_matches(thread: dict, predicate: str) -> bool:
    """`subject:contains:<text>` or `subject:regex:<pattern>`."""
    if not predicate.lower().startswith("subject:"):
        return False
    _, kind, val = predicate.split(":", 2)
    subject = thread.get("subject") or ""
    if kind == "contains":
        return val.lower() in subject.lower()
    if kind == "regex":
        try:
            return re.search(val, subject) is not None
        except re.error:
            return False
    return False


def _evaluate_rule(thread: dict, rule: str) -> bool:
    rule = rule.strip()
    if not rule:
        return False
    if rule.startswith("label:"):
        return _label_matches(thread, rule)
    if rule.startswith(("from:", "to:", "cc:", "any:")):
        return _participant_matches(thread, rule)
    if rule.startswith("subject:"):
        return _subject_matches(thread, rule)
    # Unknown rule kinds are conservatively treated as no-match.
    return False


def _evaluate_any(thread: dict, rules: Iterable[str]) -> bool:
    rules = list(rules or [])
    if not rules:
        return True   # empty include set = match-all
    return any(_evaluate_rule(thread, r) for r in rules)


def _evaluate_excludes(thread: dict, rules: Iterable[str]) -> bool:
    return any(_evaluate_rule(thread, r) for r in (rules or []))


def _gmail_block(ws_cfg: dict) -> dict | None:
    sources = (ws_cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get(SOURCE_NAME)
    if isinstance(sources, list):
        for s in sources:
            if s.get("type") == SOURCE_NAME:
                return s.get("config") or s
    return None


def _main_workspace(workspaces_config: dict) -> str | None:
    for cand in MAIN_WS_FALLBACK:
        if cand in workspaces_config:
            return cand
    return None


def _unrouted_default_for(ws_cfg: dict) -> str:
    """Workspace CLAUDE.md frontmatter may specify ingest_unrouted_default."""
    meta = (ws_cfg or {}).get("_workspace_meta", {}) or {}
    return meta.get("ingest_unrouted_default") or DEFAULT_UNROUTED


def route(thread: dict, workspaces_config: dict) -> list[str]:
    matched: set[str] = set()
    extras: set[str] = set()

    for ws, cfg in workspaces_config.items():
        block = _gmail_block(cfg)
        if not block:
            continue

        # New shape (preferred): accounts: [{account, api_query: {include, exclude}, rules: [...]}].
        accounts = block.get("accounts") if isinstance(block, dict) else None
        if isinstance(accounts, list):
            for acct in accounts:
                if acct.get("account") and thread.get("account") and acct["account"] != thread["account"]:
                    continue
                api = acct.get("api_query", {}) or {}
                if _evaluate_any(thread, api.get("include")) and not _evaluate_excludes(thread, api.get("exclude")):
                    matched.add(ws)
                    for rule in acct.get("rules", []) or []:
                        also = rule.get("also_route_to") or []
                        for target in also:
                            extras.add(target)
            continue

        # Legacy flat shape: include / exclude on the gmail block directly.
        include = (block.get("api_query", {}) or {}).get("include") or block.get("labels") or []
        exclude = (block.get("api_query", {}) or {}).get("exclude") or block.get("exclude_labels") or []
        # Treat raw label arrays (legacy spec) as label: rules.
        include_rules = [r if isinstance(r, str) and ":" in r else f"label:{r}" for r in include]
        exclude_rules = [r if isinstance(r, str) and ":" in r else f"label:{r}" for r in exclude]
        if _evaluate_any(thread, include_rules) and not _evaluate_excludes(thread, exclude_rules):
            matched.add(ws)

    if not matched:
        # Pick the strictest unrouted default among all subscribing workspaces.
        # If any workspace says skip, skip (privacy-conservative).
        defaults = {
            _unrouted_default_for(cfg)
            for ws, cfg in workspaces_config.items()
            if _gmail_block(cfg) is not None
        }
        if "skip" in defaults:
            return []
        main = _main_workspace(workspaces_config)
        if main is not None:
            matched.add(main)

    matched.update(extras)
    return sorted(matched)
