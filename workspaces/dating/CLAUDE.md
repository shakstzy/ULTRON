---
workspace: dating
wiki: true
exclude_from_super_graphify: false
ingest_unrouted_default: skip
---

# Dating — Workspace Router

You are in workspace `dating` — Adithya's dating-app activity and the people threaded through it.

## What this workspace is

Tinder, Bumble, Hinge, and adjacent platforms. Browser-automated where possible (mirroring QUANTUM's tinder / bumble ban-aversion patterns: patchright, manual auth, strict pacing). Tracks matches, conversations, dates met, follow-ups, and the small set of relationships that develop into ongoing context.

Participates in the cross-workspace graph: matches who become recurring people in your life can surface across workspaces via `[[@person]]` global stubs.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `identity.md` — workspace voice override
4. `nomenclature.md` — file-system routing

## Voice override

Personal, low-decoration, terse. Honest about pattern-matching without being clinical. See `identity.md`.

## Hard rules (workspace-specific)

1. **HITL gates.** Every outbound message goes through `SEND`. No automated reply chains. Manual review of bot-drafted replies before send.
2. **Manual auth only.** No stored credentials drive writeable sessions. Each platform requires fresh manual login. Session cookies in `_credentials/dating-<platform>.json`.
3. **Ban-aversion.** Tinder: 100/day swipes, 20/hour messages, skip 1-2 days/week. Bumble: 50/day swipes, 10/hour messages, Date-mode only. Halt on Arkose / Turnstile / Face-Check / login-wall / captcha.
4. **No API-direct.** Patchright + persistent Chrome profiles only.
5. **Person privacy.** Each match is an entity in `wiki/entities/people/<first-name-context>.md`. Phone numbers and last names live only in `raw/`. Wiki-level synthesis is fair game for the super graph; raw-level platform-specific detail is not graphed.
6. Commit messages: `chore(dating): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is X (a match)? | `wiki/entities/people/<x>.md` |
| Active conversations | `wiki/synthesis/active.md` |
| Recent dates / met-IRL log | `wiki/synthesis/met-irl.md` |
| Platform raw history | `raw/<platform>/<YYYY-MM>/...` |
| iMessage threads with dating contacts | `raw/imessage/<latest>/<thread>.md` (filtered to `routes_to: dating` per source-routing) |
| Save a match's phone / email to Apple Contacts | `_shell/skills/contacts-add/SKILL.md` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Cross-source routing in `_shell/docs/source-routing.md`. Sources today: manual exports until patchright bots are ported from QUANTUM. iMessage filtered by `routes_to: dating` rule on contact-set.
