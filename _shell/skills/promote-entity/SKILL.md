---
name: promote-entity
description: Use this skill EVERY time you want to promote a workspace entity into a canonical global stub at `_global/entities/<type>/<slug>.md`. Trigger on phrases like "promote this entity", "make X global", "canonicalize Sydney", "merge Sydney's pages across eclipse and personal into a global stub", "this person matters everywhere now". Always use this skill — never hand-create global stubs.
---

# promote-entity

Promotes a workspace entity to the global tier. Reads one or more workspaces' wiki pages for the same slug, merges their content into a global stub at `_global/entities/<type>/<slug>.md`, and marks the source pages with `global: true` + a `canonical:` pointer.

## When to use

- Audit flagged the entity as appearing in 2+ workspaces (look at `_shell/audit/promotion-candidates.md`).
- You explicitly want a person / company / project to be canonical regardless of how many workspaces touch it.
- You're consolidating after a /alias merge and want the surviving entity promoted.

## Modes

### `auto-promote`
Reads `_shell/audit/promotion-candidates.md` and promotes every entry whose `recommended action` is `/promote` and whose confidence is `high`. Skips medium/low without --force.

### `manual <type> <slug>`
Promotes one specific entity. Looks at every workspace's `wiki/entities/<type>/<slug>.md`, merges, creates the global stub.

### `dry-run`
Show what would change without writing anything.

## Process

1. **Locate sources.** Find every `workspaces/<ws>/wiki/entities/<type>/<slug>.md` matching the target. (Type may be inferred from frontmatter if not provided.)
2. **Validate.** Each source page must have YAML frontmatter with at least `slug:` and `type:`. Fail with a clear message if not.
3. **Confirm canonical name.** Read each source page's `canonical_name` (or `title`). If they disagree, surface the disagreement and ask for the user's pick (or take the most recent `last_touched` as default in `auto-promote`).
4. **Merge body content.** Run `scripts/merge_content.py` which:
   - Reads each source's body (post-frontmatter).
   - Picks `## Identity` / `## Context` / first-paragraph from the source with the longest non-trivial content.
   - Concatenates `## Active threads` / `## Open questions` / similar workspace-flavored sections under per-workspace H3s (`### Eclipse context`, `### Personal context`, etc.).
   - Drops auto-generated `## Backlinks` sections (build-backlinks.py will rebuild).
5. **Write the global stub.** `_global/entities/<type>/<slug>.md` with frontmatter:
```yaml
---
slug: <slug>
type: <type>
canonical_name: <name>
aliases: [...]
last_updated: <today>
global: true
sources:
  - workspace: eclipse
    page: workspaces/eclipse/wiki/entities/<type>/<slug>.md
  - workspace: personal
    page: workspaces/personal/wiki/entities/<type>/<slug>.md
---
```
6. **Annotate source pages.** Run `scripts/update_frontmatter.py` which adds `global: true` and `canonical: lifeos:_global/entities/<type>/<slug>` to each source page's frontmatter.
7. **Rebuild backlinks.** `_shell/bin/build-backlinks.py`.
8. **Verify.** `_shell/bin/check-routes.py` must return clean.

## Outputs

- New `_global/entities/<type>/<slug>.md`.
- Each source page gains `global: true` and `canonical:` keys.
- `_shell/audit/promotion-candidates.md` row removed (handled by `find-cross-workspace-slugs.py` next run).
- Log line in `_logs/promote-entity.log`.

## Self-review (~150 tokens)

- Global stub exists and parses as YAML+markdown.
- Every source page resolves to the global stub via `canonical:`.
- `build-backlinks.py` produced a non-empty `## Backlinks` on the new stub.
- `check-routes.py` clean.
- No source page lost its body content (size before vs after).
- If aliases were named, every alias also has a `canonical:` pointer.
