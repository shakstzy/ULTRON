# Stage: query

## Purpose
Reference manual for interactive Claude Code use. There is NO automated query workflow — interactive sessions ARE the query stage. This file exists so Claude knows how to navigate when entering ULTRON interactively.

## Routing protocol

When asked a question:

1. Read `~/ULTRON/CLAUDE.md` if not already loaded.
2. Identify the workspace scope. Cross-workspace? Single workspace? Global?
3. For single-workspace: enter that workspace, read its `CLAUDE.md` → `schema.md` → `learnings.md` → `nomenclature.md`. Use the routing table in `nomenclature.md` to find the relevant file.
4. For global: read `_global/CLAUDE.md`, drill into the entity stub, follow backlinks.
5. For cross-workspace synthesis: use `_shell/bin/build-backlinks.py` (or read the latest output) to see all workspace backlinks for an entity, then read each.

## When the route fails

If a wikilink resolves to a non-existent file, treat as a backfill candidate:
1. Note the missing file in `workspaces/<ws>/_meta/backfill-log.md`.
2. Continue answering with `raw/` material (use ripgrep on the raw archive).
3. The lint agent will surface this as a backfill candidate next run.

## What you don't do

- Do not modify wiki/schema/learnings during query.
- Do not synthesize new pages during query.
- Do not run the wiki agent during interactive use.
