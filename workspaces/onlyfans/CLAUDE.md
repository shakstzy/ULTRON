---
workspace: onlyfans
wiki: true
exclude_from_super_graphify: true
ingest_unrouted_default: skip
---

# OnlyFans — Workspace Router

You are in workspace `onlyfans` — Adithya's OnlyFans creator-business operating context.

## What this workspace is

Adult content creation, fan messaging, subscription tier ops, payouts, and platform compliance. Browser-automated where possible (mirroring the tinder / bumble ban-aversion patterns from QUANTUM). HITL-gated on every outbound message and every monetary action.

Private by design: `exclude_from_super_graphify: true` keeps entities out of the cross-workspace graph.

## Reading order on entry

1. `schema.md` — entity types, page formats
2. `learnings.md` — workspace meta-knowledge
3. `identity.md` — workspace voice override
4. `nomenclature.md` — file-system routing

## Voice override

Ops-tight. Numbers verbatim. No persuasion language. See `identity.md`.

## Hard rules (workspace-specific)

1. **HITL gates always.** Every outbound DM goes through `SEND`. Every PPV / mass message goes through `PUBLISH`. Every monetary action goes through `LAUNCH-AD` or `CONFIRM`. No silent automation.
2. **Manual auth only.** No stored credentials drive a writeable session. Login is human-in-loop. Session cookies live in `_credentials/onlyfans-session.json`.
3. **Ban-aversion.** Mirror tinder / bumble pacing: cap outbound DMs at 50/day, 10/hour. Halt on captcha / Cloudflare / platform challenge. Skip 1-2 days/week. Manual posts only on platform-flagged days.
4. **Subscriber privacy.** Real identifiers (handle, billing name) live ONLY in `raw/`. Wiki uses `fan-<short-hash>` slugs.
5. **Excluded from cross-workspace graph.** Audit's "Cross-workspace surprises" check skips this workspace.
6. Commit messages: `chore(onlyfans): <stage> <YYYY-MM-DD>`.

## Routing table — common queries

| Query | Path |
|---|---|
| Who is fan / subscriber X? | `wiki/entities/fans/<slug>.md` |
| What was last month's payout? | `raw/manual/payouts/<YYYY-MM>.md` then `wiki/synthesis/payouts.md` |
| Active campaigns / PPV drops | `wiki/synthesis/campaigns.md` |
| Platform comms (DMCA, payout issue, policy mail) | `raw/gmail/<account>/<YYYY-MM>/...` |

## Agents

- `agents/wiki-agent.md` — used by ingest stage for wiki updates.
- `agents/lint-agent.md` — used by lint stage.

## Sources

Declared in `config/sources.yaml`. Cross-source routing in `_shell/docs/source-routing.md`. Sources today: `manual` (`raw/manual/_inbox/` for payouts + screenshots) until creator-platform browser flows are wired.
