# Stage 04 — wiki-build (library)

## Purpose
Synthesize the wiki layer from `raw/`. One wiki entity page per source. For books, one additional `wiki/entities/chapters/<book>__ch-NN.md` per chapter. NO new ingest. Reads `raw/`, writes `wiki/`.

## Why this is a stage (not a one-shot /graphify call)
Earlier docs deferred wiki synthesis to `/graphify --wiki workspaces/library`. Promoting it to a formal stage gives: (1) re-runnable per-book scope; (2) curator-owned field preservation guarantees that don't depend on the graphify skill's behavior; (3) Adithya can target one book without rebuilding the whole graph.

## Inputs
- `raw/<source>/...md` (all sources)
- `wiki/entities/**` existing pages (to preserve curator-owned fields)
- `agents/wiki-agent.md` (the prompt)
- `schema.md`, `style.md`, `identity.md`, `nomenclature.md`, `learnings.md` (workspace context)

## Process
1. Enumerate raw items needing synthesis: items where no wiki entity page exists OR raw `content_hash` ≠ wiki frontmatter `source_hash`.
2. For each item, spawn one wiki-agent sub-agent per source file (per the parallel-ingest agent-learning) with the workspace context preloaded.
3. Agent writes / updates the wiki entity page following `schema.md` formats. Curator-owned fields (`read_status`, `delivered_at`, `delivery_count`) are PRESERVED on update.
4. For books with chapters: agent writes one page per chapter with `parent_book` wikilink, plus the book's roll-up page.
5. After all per-source writes, run the deterministic post-pass:
   - Forward-link stitch (multi-token titles + literal slugs only; single-token names queue for review).
   - Backlinks regen (replace, never append, idempotent).
6. Concept promotion: scan `mentioned_concepts:` frontmatter across wiki/entities; concepts appearing in 3+ sources get `wiki/concepts/<slug>.md`. Synthesis topics at 5+ sources get proposed in `_meta/synthesis-proposals.md`.

## Idempotency
Yes. Unchanged raw `content_hash` → wiki page skipped. Curator-owned fields preserved on every update. Backlinks pass is replace-not-append.

## Invocation
```bash
bin/stage-wiki-build.py                            # all unprocessed
bin/stage-wiki-build.py --book clear-atomic-habits # one book + its chapters
bin/stage-wiki-build.py --since 2026-05-01         # raw items ingested since date
bin/stage-wiki-build.py --force                    # re-synthesize regardless of hash
```

## Outputs
- `wiki/entities/<type>/<slug>.md` (one per source)
- `wiki/entities/chapters/<book-slug>__ch-NN.md` (one per chapter, books only)
- `wiki/concepts/<slug>.md` (promoted at 3+ sources)
- `_meta/synthesis-proposals.md` appended (5+ source clusters)
- `_meta/log.md` appended

## Failure mode
Per-source isolated. One bad wiki-agent run does not abort the batch. Failures recorded in `_meta/wiki-build-errors.jsonl`. Lint surfaces patterns.

## Curator
`bin/library-next.py` reads `wiki/entities/`, scores, returns one bite. Stages 01-04 are the *producers*; curator is the *consumer*. They run on different schedules.
