# Gmail ingest — current state audit (Phase 3 RESET §1)

> Generated 2026-05-02. Read-only audit; no code or config touched.

## What each file does today

### `_shell/bin/ingest-gmail.py` (the robot, ~950 lines)
- CLI: `--account <email> --run-id <id> [--dry-run] [--show] [--max-items N]`.
- Loads `_credentials/gmail-<account-slug>.json` (per-account authorized-user JSON).
- Walks every `workspaces/*/config/sources.yaml`, collects gmail blocks that mention this account, builds union include/exclude rules.
- Translates ULTRON predicates (`from:*@x`, `label:Y`, `subject:contains:Z`) to a Gmail `q=` clause via `_predicate_to_q`.
- Cursor at `_shell/cursors/gmail/<slug>.txt`: integer epoch seconds. First run uses `lookback_days_initial`. Subsequent runs use cursor as `after:<ts>`.
- Paginates `users.threads.list(q=...)`, fetches each via `users.threads.get(format='full')`.
- Pre-filter: 25MB size cap, OOO subject regex, all-senders-blocklisted, SPAM/TRASH labels, calendar-invite-only.
- Renders thread → markdown: `# Subject`, then per-message `## YYYY-MM-DD HH:MM — Sender <addr>`. HTML→markdown via html2text. Strips quoted history (`On <date> wrote:`) and signatures (`-- ` delimiter).
- Builds frontmatter (universal envelope + Gmail-specific) via `yaml.safe_dump`.
- Calls `route(thread, workspaces_config)` → list of workspace slugs.
- For each destination: writes file at deterministic path, appends ledger row (skipped if same key+hash already present).
- Advances cursor to max-internalDate seen. Appends one-line summary to `workspaces/<ws>/_meta/log.md`.
- Retry: max 3 attempts on 429/5xx with exponential backoff (no jitter).

### `_shell/stages/ingest/gmail/CONTEXT.md` (workflow contract)
- Inputs/Process/Outputs table form.
- References `format.md`, the cursor, the credentials file, the per-workspace ledger.
- Process step 4 says "Run self-review (~200 tokens) and write `_shell/runs/<run-id>/self-review.md`" — i.e. invokes an LLM at the end of each ingest.

### `_shell/stages/ingest/gmail/format.md` (data spec)
- File granularity: 1 file/thread.
- Path template: `workspaces/<ws>/raw/gmail/<account-slug>/<YYYY>/<MM>/<date>__<subject-slug>__<threadid8>.md`.
- Frontmatter: universal envelope (source, workspace, ingested_at, ingest_version, content_hash, provider_modified_at) + Gmail-specific (account, thread_id, message_ids, subject, participants, labels, first/last_message, message_count, attachments, deleted_upstream, superseded_by).
- Body: subject H1, per-message H2, attachment H3 sub-sections.
- Pre-filter list and dedup-key rules.

### `_shell/stages/ingest/gmail/route.py` (router, ~195 lines)
- Public API: `route(thread, workspaces_config) -> list[str]`.
- Per workspace, evaluates `api_query.include` (OR) AND not `api_query.exclude`.
- Predicates: `label:X`, `from:X`/`to:X`/`cc:X`/`any:X` (with `fnmatch` wildcards on the pattern), `subject:contains:X`, `subject:regex:X`.
- Account-aware: each `accounts[].account` is matched against `thread["account"]`.
- `also_route_to` extras are added unconditionally for every account hit (does **not** evaluate a `match` clause first).
- Unrouted fallback: looks up `ingest_unrouted_default` in `_workspace_meta` (always absent in current YAML); else `route_to_main` → `personal`/`main`. If any subscriber sets `skip`, returns `[]`.
- Tolerates legacy `sources: [{type: gmail, config: {...}}]` shape.

### `_credentials/INVENTORY.md`
- Documents 1 shared OAuth client (`gogcli-oauth-client.json`).
- Lists 4 distinct Gmail accounts (the original "5 files" framing was about FILES, not accounts: `gmail-{personal,health,finance}.json` all hold the same token for `adithya.shak.kumar@gmail.com`).
- Marks 3 of 4 accounts as "unverified" — written before live probe.

### `workspaces/*/config/sources.yaml`
- **eclipse**: dict shape, gmail account = `adithya@outerscope.xyz`, ULTRON-predicate include/exclude (`label:Eclipse`, `from:*@eclipse.audio`, etc).
- **personal**: dict shape, gmail account = `adithya@outerscope.xyz` with 7-day INBOX scope.
- **health**: dict shape, `gmail: []` (empty).
- **finance**: dict shape, `gmail: []` (empty).
- All four declare workspace + wiki + global_settings consistently.

## Live token probe (2026-05-02)

| Account | Auth | Profile email | messagesTotal | threadsTotal |
|---|---|---|---:|---:|
| `adithya@outerscope.xyz` | ✅ | `adithya@outerscope.xyz` | 1,120 | 793 |
| `adithya@synps.xyz` | ✅ | `adithya@synps.xyz` | 165 | 122 |
| `adithya@eclipse.builders` | ✅ | `adithya@eclipse.builders` | 2,149 | 1,941 |
| `adithya.shak.kumar@gmail.com` | ✅ | `adithya.shak.kumar@gmail.com` | 108,630 | 79,555 |

**4 distinct mailboxes**, all auth + getProfile clean. The "5 accounts" count was an artifact of `gmail-{personal,health,finance}.json` being three copies of the same token (same address shared across personal/health/finance workspaces).

## On-disk state

- `raw/gmail/...` — empty across all workspaces. Earlier dry-run smoke test wrote nothing.
- `_shell/cursors/gmail/` — empty (only `.gitkeep`).
- `_logs/` — `dispatcher.log` only; no gmail-specific logs yet.
- `_credentials/` — only `gmail-adithya-outerscope.json` is materialized in the ULTRON-native per-source shape. The other 3 distinct accounts still live only as `google-accounts/<acct>.json` or `gmail-{eclipse,personal,health,finance}.json`.

## Baseline tests (all green at audit time)

| Check | Result |
|---|---|
| `check-routes.py` | exit 0 |
| `check-frontmatter.py` | exit 0 |
| `test_rename_slug.py` | 14/14 |
| `test_gmail_union_query.py` | 7/7 |

## What's missing or wrong (the gap list)

Tagged **C/I/N** for critical / important / nice.

### A. Predicate-language fork-in-the-road *(decision needed before §3)*

1. **[C] api_query syntax: ULTRON-native vs Gmail-q=.** Today `api_query.include` items are ULTRON predicates (`from:*@eclipse.audio`, `label:Eclipse`, `subject:contains:foo`). The robot translates these to Gmail `q=` via `_predicate_to_q`. The reset spec §3.1 says they're "Gmail q= clauses" directly. These two interpretations diverge on:
   - **Wildcards**: `from:*@eclipse.audio` is fnmatch in ULTRON, literal `*` (= matches nothing) in Gmail.
   - **Temporal queries**: `newer_than:7d`, `after:1700000000` are valid Gmail q= but route.py can't evaluate them per-thread.
   - **Categories**: `category:promotions` is Gmail q= only.
   - Current robot translates a SUBSET; reset spec wants pass-through.
   - **Recommendation**: adopt Gmail q= as the canonical syntax in `api_query` (server-side filter only). Move all per-thread routing logic into `rules.match` (the new §3.1 block) which uses ULTRON-style structured fields (sender_email, sender_domain, label, subject_contains). Cleanest separation: server filter vs client routing live in different blocks with different languages.

### B. `route.py` correctness

2. **[C] `rules.match` clause is unimplemented.** `also_route_to` fires for every account hit instead of only when a `match: {...}` clause evaluates true. Currently if eclipse declares `accounts[0].rules: [{also_route_to: [personal]}]`, every Eclipse-hit thread also routes to personal — even though the spec wants the match clause to gate that.
3. **[I] Return type loses provenance.** Returns `list[str]`. Reset spec §3.3 wants `(destinations, matched_rules)` so the robot can populate `routed_by` frontmatter.
4. **[I] Unrouted default reads `_workspace_meta` from sources.yaml.** Workspace CLAUDE.md frontmatter has `ingest_unrouted_default` but it's never copied into sources.yaml; route.py's lookup always misses, so default is always "personal".
5. **[N] Top-level `api_query` (no `accounts` list) skips account-membership check.** Edge case; only triggers if a workspace puts `api_query` directly under `gmail:` instead of inside `accounts[]`.

### C. `ingest-gmail.py` shortfalls vs reset §5 spec

6. **[I] Cursor is timestamp-based, not historyId-based.** Cannot detect deletions, label changes, or label-removed events. `messages.list q="after:<ts>"` is a date filter; `users.history.list(startHistoryId=...)` is the proper incremental API. Lifecycle frontmatter (`deleted_upstream`, `superseded_by`) cannot be set without history.
7. **[I] No `flock`.** Two concurrent runs against the same account would double-fetch and double-write. Reset §5.3.E wants `/tmp/com.adithya.ultron.ingest-gmail-<account>.lock`.
8. **[I] Missing flags**: `--workspaces`, `--since`, `--reset-cursor`, `--account-list`. Reset §5.1.
9. **[I] No per-run logfile.** Today: errors only at `_logs/gmail-errors-<date>.log`. Reset §5.3.D wants per-run `_logs/gmail-<slug>-<run-id>.log` with thread-by-thread decisions.
10. **[I] Pre-filter mismatches**:
    - Doesn't catch `delivery (status )?notification` (OOO regex).
    - Doesn't blocklist `mailer-daemon@*`, `postmaster@*`, `donotreply@*`.
    - No MIME-allowlist enforcement (only `.ics`-only check).
11. **[I] PDF text extraction not implemented.** Reset §H bullet says binary-only is OK for the moment (text extraction is allowed via pdftotext/markitdown but not LLM/vision). Current robot writes "binary attachment, content not extracted" for everything.
12. **[N] Subject-prefix list.** Strips `Re:`, `Fwd:`, `FW:`, `AW:`, `[External]`, `[CONFIDENTIAL]`, `AUTO:`. Missing `[EXT]`, `[SPAM]` per reset §B.
13. **[N] BCC role not detected.** `parse_participants` walks From/To/Cc only.
14. **[N] Frontmatter missing `account_slug`, `routed_by`, attachments[].`message_index`.** Reset §D.
15. **[N] Retry caps at 3 attempts, no jitter.** Reset §5.3.C wants 5 + jitter.
16. **[N] Skipped-thread cursor advance.** Cursor is max-internalDate-seen. If a fetch fails mid-batch and we exit, cursor may not have advanced beyond the failed thread; OK in practice but worth documenting.

### D. `format.md` gaps vs reset §2

17. **[I] Missing `account_slug`, `routed_by` in frontmatter section.**
18. **[I] Missing "Forbidden behaviors" subsection** (no LLM during ingest, no path moves, no post-write FM edits except `deleted_upstream`).
19. **[N] Pre-filter blocklist incomplete** (mailer-daemon, postmaster, donotreply).
20. **[N] Subject prefix list incomplete** ([EXT], [SPAM]).
21. **[N] Attachments rule for `message_index` not stated.**

### E. `CONTEXT.md` gaps

22. **[I] Step 4 calls for an LLM self-review.** Reset §10 forbids LLM during ingest. Step needs to be removed or replaced with a deterministic post-run validator.
23. **[N] No cross-references to `sources-schema.md` (doesn't exist), `runbook-gmail.md` (doesn't exist), or `credentials-gmail.md` (doesn't exist).**

### F. `_credentials/INVENTORY.md` is stale

24. **[I] Marks 3 of 4 accounts as "unverified".** All 4 distinct accounts now verified live (numbers above).
25. **[I] Materialized files lag.** Only outerscope has the ULTRON-native shape. synps, eclipse-builders, shak-kumar-gmail still in `google-accounts/*.json` or `gmail-{eclipse,personal,health,finance}.json` form. Reset §6.1 wants per-account materialization.

### G. `workspaces/*/config/sources.yaml` gaps

26. **[I] Only one of four mailboxes is wired anywhere.** outerscope appears in eclipse + personal. synps, eclipse-builders, shak-kumar-gmail aren't referenced by any workspace's `gmail.accounts` list.
27. **[I] No `rules.match` blocks anywhere.** Schema exists in route.py for `rules[].also_route_to` but no workspace declares one.
28. **[I] If we adopt Gmail q= as the api_query language (per gap #1), every existing rule needs rewriting.** Eclipse's `from:*@eclipse.audio` becomes `from:eclipse.audio`; ULTRON predicates need to move into the `rules.match` block where they make sense.

### H. Validators

29. **[I] No `_shell/bin/validate-sources-yaml.py`.** Reset §3.2 wants it.

## Summary

Foundation is solid: 4 accounts auth clean, baseline tests green, Phase 2 architecture (workspace router check, deterministic paths, blake3 hashing, ledger model) is in place. Two structural decisions are still open:

- **Decision 1 (gap #1)**: api_query in Gmail q= syntax (recommended) vs ULTRON predicates.
- **Decision 2 (gap #4)**: where `ingest_unrouted_default` lives — workspace CLAUDE.md (current) vs sources.yaml (cleaner for route.py).

Rest of the gap list is execution against the reset spec's clearer contract.

---

## Stop here

Per the reset spec §1.3, do not proceed past this audit until the user confirms findings match their understanding and resolves Decisions 1+2.
