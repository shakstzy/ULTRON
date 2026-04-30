# Wikilink Resolution

Canonical syntax for cross-references in ULTRON markdown.

## Syntax

| Form | Resolves to |
|---|---|
| `[[entity-name]]` | Within a workspace: `wiki/entities/<type>/entity-name.md`. Type inferred from schema. Error if multiple types match. |
| `[[@entity-name]]` | Always global: `_global/entities/<type>/entity-name.md`. |
| `[[ws:eclipse/entity-name]]` | Cross-workspace: `workspaces/eclipse/wiki/entities/<type>/entity-name.md`. |
| `[[concept:cap-table]]` | Within-workspace concept: `wiki/concepts/cap-table.md`. |
| `[[synthesis:q4-deals]]` | Within-workspace synthesis: `wiki/synthesis/q4-deals.md`. |
| `[[raw:gmail/2026-04/thread-id.md]]` | Raw archive reference. |

## Slug conventions

- Lowercase. Hyphen-separated. ASCII only.
- People: first-name-only when unambiguous; `<first>-<last>` when multiple share a first name; add disambiguating suffix only on collision (e.g., `sarah-eclipse-bd` vs `sarah-personal-friend`).
- Companies: lowercase, no suffixes (`anthropic`, not `anthropic-inc`).
- Concepts: noun-phrases (`ai-feature-tax`, `minimum-viable-moat`).
- Synthesis: topic-quarter when time-bounded (`q2-2026-bd-pipeline`).

## Validation

`_shell/bin/check-routes.py` parses every wikilink in every `.md` file and verifies it resolves to an existing file. Run before every commit; integrated into lint stage.

## Display labels

`[[target|display label]]` is supported. The validator splits on `|` and only checks the target before the pipe.
