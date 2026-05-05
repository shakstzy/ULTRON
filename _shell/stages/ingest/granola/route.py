"""
granola/route.py — given a fetched Granola doc + the parsed sources.yaml of
every workspace, decide which workspace(s) get a copy.

Public API:
    route(doc, workspaces_config) -> list[{workspace, rule}]

`doc` is a Granola document dict augmented with a `folder_titles: list[str]`
key — the titles of every Granola folder containing this document.
`workspaces_config` is `{ws_slug: parsed_sources_yaml}`.

Routing semantics:
  - Each workspace's `sources.granola.folders: [<title>, ...]` is the
    allowlist. Empty / missing → workspace ignores granola entirely.
  - A doc routes to workspace W iff at least one of W's allowlisted
    folder titles appears in `doc.folder_titles`.
  - Conflict policy: fork. A doc in two folders subscribed by two
    workspaces is written to BOTH workspaces.
  - Folder-title comparison is exact (case-sensitive). Granola folder
    titles are user-controlled identifiers; matching the casing keeps
    `folder:ECLIPSE` distinct from `folder:eclipse` if the user ever
    creates both.
  - Return list of `{workspace, rule}` dicts, sorted by workspace.
    `rule` is `"folder:<title>"` of the first allowlisted folder that
    fired (deterministic ordering = the workspace's own list order).

Out of scope here: include/exclude grammars, regex, calendar-event
attribute matching. If we ever need finer-grained routing (e.g. "Eclipse
folder but only when calendar_event.attendees contains @eclipse.audio")
we add it as an explicit `match` block, not a glob hack.
"""
from __future__ import annotations

from typing import Any

SOURCE_NAME = "granola"


def route(doc: dict[str, Any], workspaces_config: dict[str, dict]) -> list[dict[str, str]]:
    folder_titles = doc.get("folder_titles") or []
    if not folder_titles:
        return []

    folder_titles_set = set(folder_titles)
    decisions: list[dict[str, str]] = []

    for ws_slug, ws_cfg in workspaces_config.items():
        gran = (ws_cfg.get("sources") or {}).get(SOURCE_NAME) or {}
        wanted = gran.get("folders") or []
        if not wanted:
            continue
        # Preserve the workspace's own ordering when picking the rule label.
        for title in wanted:
            if title in folder_titles_set:
                decisions.append({"workspace": ws_slug, "rule": f"folder:{title}"})
                break

    decisions.sort(key=lambda d: d["workspace"])
    return decisions
