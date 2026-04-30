# Stage: ingest

## Purpose
Pull new source material into a workspace's `raw/` archive, dedupe via `_meta/ingested.jsonl`, optionally invoke the wiki agent for downstream synthesis.

## Invocation
`run-stage.sh ingest <workspace>`

## Inputs
- `workspaces/<ws>/config/sources.yaml`
- `workspaces/<ws>/_meta/ingested.jsonl` (for dedup)
- Source credentials in `_credentials/` or `~/.ULTRON/credentials/`. Per-source convention: `<source-id>.json` for OAuth, env vars for API keys.

## Process
1. Load sources from `config/sources.yaml`.
2. For each source, invoke its `bin` script (e.g., `_shell/bin/ingest-gmail.py`) with workspace and run_id arguments.
3. Each ingest script:
   a. Polls the source per its config.
   b. For each new item (not in `ingested.jsonl` by `source_uid`), writes to `raw/<source>/<YYYY-MM>/<slug>.md` with attachments inlined.
   c. Appends to `ingested.jsonl`.
4. After all sources complete, gather list of new raw files. Write to `_shell/runs/<RUN_ID>/input/new-raw.txt`.
5. If `wiki: true` (per `config/sources.yaml`), invoke the workspace wiki agent (`workspaces/<ws>/agents/wiki-agent.md`) with the new-raw list. Wiki agent updates `wiki/`.
6. Append run summary to `_meta/log.md`.

## Outputs
- New files in `raw/<source>/<YYYY-MM>/`.
- Updated `_meta/ingested.jsonl`.
- Possibly updated files in `wiki/`.
- Run artifacts in `_shell/runs/<RUN_ID>/`.

## Idempotency
Yes. Re-running consumes nothing already in `ingested.jsonl`.

## Failure mode
On per-source failure, that source skips and the failure is logged to `_logs/<workspace>-ingest.err.log`. Other sources proceed. Lint stage will surface the failure pattern next run.
