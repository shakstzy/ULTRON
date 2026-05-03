# Stage: ingest-imessage

> **Authoritative data spec**: `format.md` (paths, frontmatter, body, pre-filter, attachment copy, cursor, dedup, forbidden behaviors).
> **Operator runbook**: `SETUP.md` (Full Disk Access, Contacts permission, timing, v1.5 caveats).
> **Routing**: `route.py` (per-workspace allowlist, default skip).

## Inputs
| Source | Location | Why |
|---|---|---|
| Subscriptions | `workspaces/*/config/sources.yaml` (imessage block) | Per-contact / per-group allowlist + per-workspace routing |
| Cursor | `_shell/cursors/imessage/<account>.txt` | `last_rowid` + `last_message_date` (account = `local`) |
| Source DB | `~/Library/Messages/chat.db` | Local SQLite, opened read-only |
| Attachments root | `~/Library/Messages/Attachments/` | Binary copies (per § G of `format.md`) |
| Apple Contacts | `Contacts.framework` via PyObjC | Slug derivation priority 1 |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` | Per-workspace dedup keyed by `imessage:<contact_slug>:<YYYY-MM>` |

## Process
One robot run = one local chat.db. (Future iCloud-only-device support adds per-device cursors.)

1. **flock** `/tmp/com.adithya.ultron.ingest-imessage.lock`. Concurrent run exits 0 silently.
2. **Open chat.db** read-only via URI (`?mode=ro`). Bail with actionable error if Full Disk Access is missing (see `SETUP.md`).
3. **Read cursor**. Sanity-check per `format.md` § H: ROWID path if `last_rowid` row exists and date matches; else date path with warning.
4. **Resolve Contacts** via `Contacts.framework` (PyObjC). On permission denial, fall back to email / phone / hash slug derivation.
5. **For each new message** (from cursor query):
   - Apply universal blocklist (`format.md` § F).
   - Resolve `contact_slug` against `_profiles/` (create stub on first sight).
   - Bucket by `(contact_slug, YYYY-MM)`.
6. **For each (contact, month) bucket**:
   - Filter and merge tapbacks per `format.md` § I.
   - Copy attachments per `format.md` § G (100 MB / month budget).
   - Render markdown per `format.md` § E.
   - Compute `content_hash` (blake3 of body markdown).
   - Call `route(item, workspaces_config) -> destinations`.
   - Per destination: skip if `(key, content_hash)` matches existing ledger row; else write file at deterministic path and append ledger row.
7. **Profile updates**: append new handles / aliases to `_profiles/<slug>.md`. Never delete prior entries.
8. **Advance cursor** atomically (both `last_rowid` and `last_message_date`) only after successful write phase. Mid-batch failure leaves cursor; next run replays.
9. **Per-workspace summary** appended to `workspaces/<ws>/_meta/log.md`.
10. **Self-review** writes anomalies to `_shell/runs/<RUN_ID>/self-review.md`: missing attachments, pruned months, ROWID-reset warnings, route misses.

## Outputs
| Artifact | Location |
|---|---|
| Month files | `workspaces/<ws>/raw/imessage/{individuals\|groups}/<slug>/<YYYY>/<YYYY-MM>__<slug>.md` |
| Profile stubs | `workspaces/<ws>/raw/imessage/_profiles/<slug>.md` |
| Attachment copies | `workspaces/<ws>/raw/imessage/{individuals\|groups}/<slug>/<YYYY>/_attachments/<id>.<ext>` |
| Cursor | `_shell/cursors/imessage/<account>.txt` |
| Ledger | `workspaces/<ws>/_meta/ingested.jsonl` |
| Workspace log | `workspaces/<ws>/_meta/log.md` |
| Self-review | `_shell/runs/<RUN_ID>/self-review.md` |

## Out of scope (this phase)
LLM / vision attachment extraction; full edit-history reconstruction (deferred to v1.5); cross-source dedup (Slack / WhatsApp message merging); voice-memo transcription; iCloud-only device sync.

## Status
Skeleton. `_shell/bin/ingest-imessage.py` is foundation-only with `IMPLEMENTATION_READY = False`. Activation is a later session. See `SETUP.md` for the flip-on procedure.
