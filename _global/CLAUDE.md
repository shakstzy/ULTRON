# Global Tier

You are in `_global/`, the cross-workspace canonical layer.

## Layout

- `entities/<type>/<slug>.md` — One file per entity. Type is folder; slug is filename. Default starter types: `people`, `companies`, `projects`, `concepts`. New types added by audit-agent recommendation only.
- `agent-learnings.md` — Append-only log of cross-cutting agent-behavior fixes. Soft cap 100 lines; compact older entries when exceeded (audit-agent flags this).
- `wikilink-resolution.md` — Canonical wikilink syntax for the entire system.

## What lives here vs at workspace level

- **Here:** identity (canonical name + aliases + slug), the roster of backlinks (which workspaces have a wiki page on this entity, with a one-line context per backlink), and stable cross-workspace facts.
- **NOT here:** workspace-specific synthesis, recent thread context, deal pipeline notes, project-specific opinions. Those live in `workspaces/<ws>/wiki/entities/<type>/<slug>.md`.

## Backlink discipline

Each entity stub lists every workspace where there is workspace-level synthesis on this entity, with a one-line "what kind of context lives there." This is rebuilt by `_shell/bin/build-backlinks.py`, which the audit stage runs.

## Promotion criteria

A workspace entity becomes a global entity when it appears in 2+ workspaces with substantive synthesis. Audit recommends. Adithya promotes manually.
