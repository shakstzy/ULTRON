# Setup: ingest-imessage

> Permissions, caveats, and the flip-on procedure for the iMessage robot.
> Read alongside `format.md` (data spec) and `CONTEXT.md` (workflow).

## 1. Full Disk Access (REQUIRED)
`chat.db` lives at `~/Library/Messages/chat.db` and is locked behind macOS
Full Disk Access (FDA). The process running the robot must be granted FDA.

Steps:
1. **System Settings** → **Privacy & Security** → **Full Disk Access**.
2. Add the binary that will execute the robot:
   - Manual / interactive runs: add `Terminal.app` (or `iTerm.app`).
   - Unattended launchd runs: add `/bin/bash` (or whichever shell launchd
     spawns from the plist in `_shell/plists/`).
3. Verify access:
   ```bash
   sqlite3 -readonly ~/Library/Messages/chat.db \
     "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
   ```
   This must print a list of table names. If you see
   `Error: unable to open database file` or `Operation not permitted`,
   FDA is not granted.

The robot bails with **exit code 3** and an actionable stderr message on
FDA failure. cron / launchd will see the failure (it does not silently
return 0).

## 2. Apple Contacts permission (RECOMMENDED)
Slug derivation priority 1 reads contact names via `Contacts.framework`
(PyObjC). Without this permission the robot still works but every contact
falls through to email / phone / hash slugs (priorities 2 to 4 of
`format.md` § C).

Steps:
1. First run that hits PyObjC `CNContactStore` triggers a system prompt
   asking to grant Contacts access to the parent app (Terminal, iTerm,
   etc.). Approve it.
2. If no prompt fires (e.g., previously denied), open
   **System Settings** → **Privacy & Security** → **Contacts** and toggle
   the parent app on.
3. Verify with a one-liner:
   ```bash
   python3 -c "from Contacts import CNContactStore; \
     CNContactStore.alloc().init().requestAccessForEntityType_completionHandler_(0, lambda granted, err: print('granted:', granted))"
   ```
   Expect `granted: True`. If `False`, the slug derivation falls back per
   `format.md` § C.

PyObjC is the dependency. Install with:
```bash
pip3 install pyobjc-framework-Contacts pyobjc-framework-Cocoa
```
`pyobjc-framework-Cocoa` is also required: the v1 attributedBody parser uses `Foundation.NSUnarchiver`. Pin in `_shell/bin/requirements.txt` only when activating the robot.

**attributedBody parser caveats** (verified live, round-2 review):
- Wrap each `NSUnarchiver.decodeObject()` call in `objc.autorelease_pool()`. Without it, ObjC temporaries accumulate over a 100K-message backfill and OOM the process.
- Catch `NSInvalidUnarchiveOperationException`. Some messages contain undocumented Apple classes (`MSMessage`, app-extension payloads). Decode failure → fall back to `[app message: <balloon_bundle_id>]` per `format.md` § E. Never crash; never emit raw obj-descriptions.
- When the decoded `NSAttributedString` includes `NSTextAttachment`, the underlying string contains `U+FFFC` (object replacement character). Strip these from rendered text; the attachment itself is captured separately via `message_attachment_join`.

## 3. chat.db read-only verification
The robot uses SQLite URI mode `?mode=ro`. Confirm read-only behavior with:
```bash
sqlite3 -readonly ~/Library/Messages/chat.db ".tables"
```
This must list (at minimum): `attachment`, `chat`, `chat_handle_join`,
`chat_message_join`, `handle`, `message`, `message_attachment_join`.
Missing tables means the schema has shifted (newer macOS releases sometimes
rename or add columns). Bail and re-spec before running.

**Schema variants (verified against macOS Sonoma)**: the columns
`is_edited` and `is_unsent` are NOT present on Sonoma's `message` table.
Detection alternatives the implementation must use:
- **Edited**: `date_edited > 0` (verified working; 42/187K msgs flagged on this Mac).
- **Unsent**: no clean column. The heuristic `text IS NULL AND attributedBody IS NULL AND date_edited > 0` is **NOT reliable**: media-only messages and quirks fire false positives (Gemini round 2). Parse the `message_summary_info` binary plist for the unsent sentinel. v1 renders edits via `date_edited`; v1.5 implements the plist parser for unsents.

**1:1 vs group**: distinguished by `chat.style` (`style = 43` is group;
otherwise 1:1). Group chats route to `groups/<slug>/`, 1:1 to
`individuals/<slug>/`.

## 4. Realistic timing expectations
- **First run** with empty cursor: 20 to 60 minutes for a 150-200K message
  chat.db with ~10K attachments (this Mac measures 187K msgs / 8.6K
  attachments). Attachment copy (per `format.md` § G) is the bottleneck;
  I/O bound, not CPU bound.
- **Incremental runs** (cursor non-empty): seconds to minutes depending on
  daily message volume.
- **Schema-only re-renders** (`--no-attachments`): a few minutes for full
  archive rewrite.
- The 5-minute estimate that appeared in earlier proposals is too
  optimistic. Plan for 30 minutes on first run.

## 5. v1 vs v1.5 caveats (deferred work)
Documented gaps the v1 robot does NOT cover. These are intentional
deferrals; do not attempt them in v1.

| Gap | v1 behavior | v1.5 plan |
|---|---|---|
| Edit history | Stores `is_edited: true`, renders current text only | Parse `message.message_summary_info` plist, walk edit chain, render full prior text |
| Vanished-row auto-detection | `deleted_upstream` set only on cursor-resync rediscovery | Periodic full-table scan to detect rows missing from chat.db and mark `deleted_upstream` on the corresponding month files |
| Voice-memo transcription | Recorded as `[audio: <filename>, <size>]` only | Whisper-based transcription on demand via separate skill |
| Vision / OCR on images | Metadata only | Wiki-promotion-time skill `_shell/skills/imessage-attachment-extract/` |
| Cross-platform merge (iMessage + Slack DMs + WhatsApp) | Per-source archives stay independent | Wiki entity page synthesizes across sources |
| Polls (iOS 17+) structured payload | Captured as `[app message: <bundle_id>]` | Parse poll payload, render options + votes |
| iCloud-only device support | Single `local` cursor | Per-device cursor under `_shell/cursors/imessage/` |

## 6. Privacy compartmentalization
A `private` workspace can opt out of the super-graph and cross-workspace
audit (e.g., for therapist conversations). Configure per-workspace
inclusion in `_graphify/` config; `format.md` does not change.

## 7. Activation procedure (flipping IMPLEMENTATION_READY)
Do NOT run this until all of the below are green:

1. Full Disk Access verified (§ 1).
2. Apple Contacts permission verified or accepted as fallback (§ 2).
3. chat.db schema verified (§ 3).
4. At least one workspace `sources.yaml` has an `imessage` block with at
   least one allowlisted contact or group.
5. Validators green:
   ```bash
   python3 _shell/bin/check-routes.py
   python3 _shell/bin/check-frontmatter.py
   python3 _shell/tests/test_rename_slug.py
   ```
6. Dry-run produces sane output:
   ```bash
   python3 _shell/bin/ingest-imessage.py --dry-run --max-contacts 3 --show
   ```

When all green, edit `_shell/bin/ingest-imessage.py` and set:
```python
IMPLEMENTATION_READY = True
```
First live run should be `--max-contacts 3` to validate end-to-end before
unlocking the full archive.

## 8. Troubleshooting
- **ROWID reset warning in logs**: chat.db was rebuilt (Mac migration,
  Messages reset, iCloud resync). The robot fell back to date-based
  cursor. Expected behavior; no action required.
- **`source_missing: true` on many attachments**: iCloud "Optimize Storage"
  pruned old binaries. Recover by going to **Messages** → **Settings** →
  **iMessage** and toggling "Keep Messages" to "Forever", then forcing a
  re-download. v1 logs the loss but does not retry.
- **`attachment_pruned: true` on a month**: a single month exceeded the
  100 MB copy budget. Bump the budget in `format.md` § G or accept the
  pruning (sha256 + size still recorded for later reconciliation).
- **All contacts falling to `phone-...` or `unknown-...` slugs**:
  Apple Contacts permission denied. Re-grant per § 2.
