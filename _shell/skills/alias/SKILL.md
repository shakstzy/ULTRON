---
name: alias
description: Use this skill EVERY time you discover that two slugs name the same entity. Trigger on phrases like "these are the same person", "merge sandeep-r and sandeep-rao", "alias", "consolidate", "this slug is a duplicate". Picks a canonical slug, rewrites every reference to the alias slug to point at the canonical, leaves a redirect stub at the alias slug. Always use this skill — never delete an alias file or hand-rewrite wikilinks.
---

# alias

Merges two (or more) slugs that refer to the same entity. Picks a canonical slug, rewrites all wikilinks to the aliases, leaves a redirect stub at each alias slug pointing at canonical, preserves history.

## When to use

- Audit / `find-cross-workspace-slugs.py` flagged a fuzzy match (e.g., `sandeep-r` ≈ `sandeep-rao` at 0.91 confidence).
- You manually realize two pages are the same person / company / project.
- Cleaning up after a typo or after Apple Contacts changed how a contact is named.

## Modes

### `merge <slug-a> <slug-b> [<slug-n>...] --canonical <slug>`
Explicit merge. Canonical must be one of the listed slugs.

### `merge <slug-a> <slug-b> --canonical auto`
Detect canonical via heuristics:
- Longer slug wins (more specific).
- Among equally long, pick the more recently `last_touched`.
- Tie → ask the user; in scripted mode, pick alphabetically first.

### `dry-run`
Print the rewrite plan without applying.

## Process

1. **Locate target pages.** For each slug, find every workspace page (`workspaces/*/wiki/entities/<type>/<slug>.md`) and any global stub (`_global/entities/<type>/<slug>.md`).
2. **Detect canonical** (per `scripts/detect_canonical.py`).
3. **For each non-canonical alias slug**:
   a. Move its content (if any) into the canonical page's body under `### From <alias-slug>` IF the canonical page exists. (If only the alias has content, rename via `_shell/bin/rename-slug.py` and stop.)
   b. Replace the alias's file content with a redirect stub:
```yaml
---
slug: <alias-slug>
type: <type>
canonical: lifeos:_global/entities/<type>/<canonical-slug>   # or workspace path if no global
redirect_to: <canonical-slug>
aliased_at: <today>
---

This entity was merged into [[<canonical-slug>]] on <today>. Wikilinks
to this slug still resolve here for history but should be rewritten.
```
   c. Run `scripts/rewrite_links.py` (which delegates to `_shell/bin/rename-slug.py`) for each (workspace, alias→canonical) pair.
4. **Update the canonical page's `aliases:` frontmatter** to include every alias slug.
5. **Rebuild backlinks.** `_shell/bin/build-backlinks.py`.
6. **Verify.** `_shell/bin/check-routes.py` clean.

## Outputs

- Each alias slug becomes a redirect stub.
- Canonical page absorbs alias content under per-alias headers.
- Canonical page's `aliases:` frontmatter list grows.
- All wikilinks `[[<alias>]]` etc. now point at `[[<canonical>]]`.
- Log line in `_logs/alias.log` with `<canonical> ← <alias-1>, <alias-2>...`.

## Self-review (~150 tokens)

- `check-routes.py` clean.
- The redirect stub at each alias resolves to the canonical.
- The canonical page's `aliases:` list contains every merged slug.
- Backlinks rebuilt; the canonical stub now lists every workspace page that referenced any alias.
- No alias content was lost (size check).
- If the canonical was not previously global and 2+ workspaces touched the merged entity → suggest `/promote` next.

## Hard rules

- NEVER delete an alias file. Keep it as a redirect stub forever.
- NEVER alias across types (a `person` slug cannot be aliased to a `company` slug).
- NEVER touch `_global/agent-learnings.md` from an alias merge — that's audit territory.
