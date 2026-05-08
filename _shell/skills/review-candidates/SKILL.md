---
name: review-candidates
description: Use this skill EVERY time Adithya wants to triage cross-workspace candidate edges — confirming or rejecting suggested links and aliases that the system inferred from per-workspace graphify outputs. Trigger on phrases like "review candidates", "review my graph candidates", "review knowledge graph queue", "what links should I confirm", "triage my graph", "any candidate edges", "review-candidates", "review candidate edges". The CLI is interactive (y/n/s/q per candidate). Accepted candidates fire the existing `link` or `alias` skills, rejected candidates are remembered forever and never resurface.
---

# review-candidates

Bridges per-workspace graphify outputs into the canonical `_global/entities/` and `wiki/entities/` layers via human-in-the-loop confirmation.

## Why

Per-workspace graphify is literal — only catches what's explicitly stated. Real cross-workspace insight (e.g., the same person appearing under different ids in eclipse and personal, or two people with many shared connections who haven't been linked) requires a manual confirmation step. This skill surfaces those candidates and lets Adithya say yes/no/skip without seeing 200 of them at once.

## Tooling

Two scripts in `_shell/bin/`:

1. **`generate-candidate-edges.py`** — deterministic. No LLM. Produces:
   - **alias candidates**: same normalized label across 2+ workspaces, different on-disk slugs. Resolves graphify node ids (`sydney_huang_eclipse`) to actual entity slugs (`sydney-huang-eclipse`). Skips candidates where one endpoint has no entity file.
   - **link candidates** (cooccurrence): pairs sharing N+ common neighbors in `_graphify/super/graph.json`, no direct edge. `min_shared` defaults to 4.
   - Skips anything in `_shell/audit/rejected_edges.jsonl` (durable negatives).

2. **`review-candidates.py`** — interactive CLI. Walks pending candidates, for each:
   - shows subj, obj, type, reason, evidence, confidence
   - accepts `y/n/s/q`
   - on `y`: dispatches to `link.py add` (with `--symmetric` for cooccur types like `knows`) or `alias.py merge`
   - on `n`: writes to `rejected_edges.jsonl`, never resurfaces
   - on `s`: leaves pending for later
   - on `q`: exits, saves state

## Daily flow

```bash
# Refresh candidate queue (run after super-merge, or whenever)
~/ULTRON/.venv/bin/python3 ~/ULTRON/_shell/bin/generate-candidate-edges.py

# Triage 10 at a time
python3 ~/ULTRON/_shell/bin/review-candidates.py --limit 10

# Just see how many are pending
python3 ~/ULTRON/_shell/bin/review-candidates.py --list
```

Filter by kind:
```bash
python3 ~/ULTRON/_shell/bin/review-candidates.py --kind alias --limit 5
```

## Files

- `_shell/audit/candidate_edges.jsonl` — append-only queue. Pending, accepted, and skipped candidates all live here. Status field tracks state.
- `_shell/audit/rejected_edges.jsonl` — durable negatives. Generator reads this every run to skip re-emission.

## Hard rules

- The generator NEVER auto-accepts. Always pending.
- The CLI NEVER touches Apple Contacts, only `_global/entities/` and `wiki/entities/`.
- Rejected edges stay rejected forever. To resurrect one, manually edit the JSONL files.
- Use the venv python for the generator (`~/ULTRON/.venv/bin/python3`). `review-candidates.py` runs on system python.

## When NOT to use this skill

- Adding a brand new typed edge between two known entities → use `link` directly.
- Merging two known-duplicate slugs → use `alias` directly.
- Promoting a workspace entity to global → use `promote-entity`.

This skill is for the BACKLOG of suggestions the system generates, not for ad-hoc edge writes.
