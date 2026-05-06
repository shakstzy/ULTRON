# Buildplans

Captured build-design corpus for QUANTUM workspaces and skills. One subfolder per workspace.

## Index

| Workspace | Folder | Status |
|---|---|---|
| clipping | `clipping/` | v1 shipped 2026-04-28; learning loop + scraper layer + template variation in flight |

## Conventions

- Plain words, short sentences, no em dashes (matches ULTRON Voice).
- Each workspace folder has a `00-architecture.md` first; subsequent files are review captures, deferred items, and design memos.
- Frontmatter optional. When present, use `status: shipped|in-flight|deferred` and `last_updated: YYYY-MM-DD`.
- Source-of-truth for live code is the QUANTUM workspace itself. Buildplans here capture WHY, REVIEWS, and FUTURE WORK only.
