# Stage: ingest-<source>

## Inputs
| Source | File / Location | Why |
|---|---|---|
| All workspace source configs | `workspaces/*/config/sources.yaml` | Build union query |
| Source format spec | `_shell/stages/ingest/<source>/format.md` | Output format |
| Cursor | `_shell/cursors/<source>/<account>.txt` | Incremental marker |
| Credentials | `_credentials/<source>-<account>.json` | Auth |
| Dedup ledger | `workspaces/*/_meta/ingested.jsonl` | Per-workspace dedup |

## Process
1. Read all workspaces' `config/sources.yaml` that include this source.
2. Build union query: UNION of `include` rules, INTERSECT with `exclude` rules.
3. Read cursor for this account.
4. Call API with union query + cursor.
5. For each returned item:
   a. Apply deterministic skip rules from `format.md` (size caps, sender domain blocklist, mime allowlist, etc.).
   b. Convert to standardized markdown per `format.md`.
   c. Compute `content_hash` (blake3).
   d. Call `route.py` to determine destination workspaces.
   e. Write file to each destination workspace's `raw/<source>/...` at the deterministic path.
   f. Append a `{source, key, content_hash, raw_path, ingested_at}` row to each destination's `_meta/ingested.jsonl`.
6. Advance cursor to latest seen marker.
7. Append summary to each affected workspace's `_meta/log.md`.

## Outputs
| Artifact | Location | Format |
|---|---|---|
| Standardized raw files | `workspaces/<ws>/raw/<source>/...` | markdown |
| Updated cursor | `_shell/cursors/<source>/<account>.txt` | text |
| Ledger updates | `workspaces/<ws>/_meta/ingested.jsonl` | JSONL |
| Log entries | `workspaces/<ws>/_meta/log.md` | markdown |

## Self-review (~200 tokens)
- Verify every new file has the universal frontmatter envelope.
- Verify cursor advanced.
- Verify ledger entries match files written.
- Verify `route.py` decisions look sane (no item went to zero workspaces when rules should have matched).
- Surface anomalies to `_shell/runs/<RUN_ID>/self-review.md`.
