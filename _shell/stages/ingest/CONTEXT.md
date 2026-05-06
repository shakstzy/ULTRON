# Stage: ingest (universal)

## Purpose
Pull new source material across ULTRON. Each source has its own substage at `_shell/stages/ingest/<source>/` with its own `CONTEXT.md`, `format.md`, and `route.py`. This file documents what every source must do.

## Architecture

- **One robot per source** at `_shell/bin/ingest-<source>.py`. Reads its substage's `format.md`, calls `route.py`, fans out to one or more workspaces.
- **One cursor per (source, account)** at `_shell/cursors/<source>/<account>.txt`. Cursors are SHARED across workspaces — a single API call serves every workspace that subscribes to that source. Per-workspace cursors are forbidden.
- **Per-workspace declarations** in `workspaces/<ws>/config/sources.yaml` say which sources this workspace consumes and its include/exclude rules. Workspaces never own ingest logic.
- **Conflict policy**: `fork`. An item matching multiple workspaces is written to ALL matching workspaces.

## Universal frontmatter envelope

Every raw file across every source MUST carry these YAML frontmatter fields:

```yaml
source: <source-name>            # gmail, slack, drive, imessage, ...
workspace: <ws-slug>             # which workspace this copy lives in
ingested_at: <ISO 8601>          # when ULTRON ingested it
ingest_version: <int>            # bump when format.md spec changes
content_hash: <blake3 of body>   # change-detection key
provider_modified_at: <ISO 8601> # last-modified per source
```

Source-specific keys layer on top. Each source's `format.md` defines its own additions.

## Contract: per-source substage

Each `_shell/stages/ingest/<source>/CONTEXT.md` follows the standard contract: Inputs / Process / Outputs / Self-review. Each `format.md` defines: file granularity, path template, frontmatter (universal + source-specific), body shape, pre-filter (deterministic, no LLM), dedup key. Each `route.py` exposes:

```python
def route(item: dict, all_sources_yaml: dict) -> list[str]:
    """Return list of workspace slugs the item should be written to."""
```

## Invocation
`run-stage.sh ingest <workspace>` (per-workspace dispatcher) OR `run-stage.sh ingest-source <source> <account>` (per-account dispatcher; fans to all subscribed workspaces). The schedule skill emits the per-(source,account) form.

## Idempotency
Yes. Re-running consumes nothing already in `ingested.jsonl` by `(source, key)`. Same-key + same-content_hash = skip. Same-key + different content_hash = overwrite at the deterministic path.

## Failure mode
Per-source failure isolated. One source dying does not abort siblings. Failure logged to `_logs/<workspace>-<source>.err.log`. Lint surfaces patterns.
