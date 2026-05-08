# Network Workspace Learnings

Workspace meta-knowledge that the wiki and lint agents reload every turn. ≤ 200 lines. Updated only by accepting entries from `_meta/learning-proposals.md`.

## Voice and tone

Global default. Direct, low-decoration, opinionated where evidence supports.

## Operational rules

- Raw deposits NEVER duplicate identity into `_global/entities/people/`. The global stub stays thin (identity + roster of backlinks); the raw deposit holds the full snapshot.
- Slug is the join key across LinkedIn, Apple Contacts, iMessage, Discord, etc. When a mismatch is found (`sandeep-r-eclipse` ≠ `sandeep-rao`), route through `/alias` — never hand-rewrite wikilinks.
- Auto-created global stubs from LinkedIn `get-profile` carry `entity_status: provisional` until promoted. Stubs without further activity are pruning candidates (rule TBD; not enforced in v1).
- LinkedIn write verbs (`send-connect`, `send-dm`, `accept-invite`, `withdraw-invite`) ALWAYS default to dry-run. Live action requires `--send` and explicit Adithya confirmation in chat.

## Past patterns

(empty — populated as the wiki agent learns from history)

## Mental models

- A person can exist as a global stub WITHOUT a workspace-local synthesis page. The thin stub + backlinks is the v1 normal case. Promote to a synthesis page only when the person earns workspace-specific narrative content (a deal, a pitched investment, an active outreach campaign).
- "Network" is a flat namespace by default — no sub-categorization (investors / founders / operators) at the folder level. Sub-categorization is a Bases query, not a directory layout.
