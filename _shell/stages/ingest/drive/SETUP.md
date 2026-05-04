# Setup: ingest-drive

> OAuth scope verification + folder ID retrieval + sources.yaml
> configuration + the activation procedure for the Drive robot. Read
> alongside `format.md` (data spec) and `CONTEXT.md` (workflow).

## 1. OAuth scopes (REQUIRED)

The Drive robot reuses each Gmail credential file (`_credentials/gmail-<account-slug>.json`)
because the same OAuth client minted both — Drive scope was included at
mint time alongside Gmail. **No separate Drive credential files are needed.**

Required scope: at least
`https://www.googleapis.com/auth/drive.readonly`. Most existing tokens
have the broader `https://www.googleapis.com/auth/drive` (read + write);
the robot is hard-coded to read-only API methods regardless (see
`format.md` Forbidden Behaviors).

### 1.1 Verify a token's scopes

```bash
python3 - <<'PY'
import json, urllib.parse, urllib.request
from pathlib import Path

ACCOUNT_SLUG = "adithya-eclipse"   # <-- edit me
cred = json.loads(Path(f"/Users/shakstzy/ULTRON/_credentials/gmail-{ACCOUNT_SLUG}.json").read_text())
data = urllib.parse.urlencode({
    "client_id": cred["client_id"],
    "client_secret": cred["client_secret"],
    "refresh_token": cred["refresh_token"],
    "grant_type": "refresh_token",
}).encode()
req = urllib.request.Request(cred.get("token_uri", "https://oauth2.googleapis.com/token"), data=data, method="POST")
tok = json.loads(urllib.request.urlopen(req, timeout=10).read())
info_url = "https://www.googleapis.com/oauth2/v3/tokeninfo?" + urllib.parse.urlencode({"access_token": tok["access_token"]})
info = json.loads(urllib.request.urlopen(info_url, timeout=10).read())
scopes = info.get("scope", "").split()
print("scopes:", scopes)
print("drive.readonly OR drive present:", any(s in scopes for s in ("https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/drive")))
PY
```

### 1.2 Current state (verified 2026-05-03)

All 4 ULTRON Gmail credentials carry `https://www.googleapis.com/auth/drive`:

| Account | Credential file | Drive scope |
|---|---|---|
| `adithya@outerscope.xyz` | `gmail-adithya-outerscope.json` | ✅ drive |
| `adithya@synps.xyz` | `gmail-adithya-synps.json` | ✅ drive |
| `adithya@eclipse.builders` | `gmail-adithya-eclipse.json` | ✅ drive |
| `adithya.shak.kumar@gmail.com` | `gmail-adithya-shak-kumar-gmail.json` | ✅ drive |

The legacy `_credentials/drive-eclipse.json` (gog-shaped, no `account` key)
is redundant with `gmail-adithya-eclipse.json` and is NOT used by the
robot. It can be removed in a future cleanup pass.

### 1.3 Re-minting (if a future audit finds drive scope missing)

If a credential ever loses Drive scope, re-mint via the gog CLI (which the
existing tokens were derived from):

```bash
gog auth login -a <email> --scopes \
  https://mail.google.com/,https://www.googleapis.com/auth/drive.readonly
```

Then copy the refreshed token into the matching
`gmail-<account-slug>.json` per `_credentials/INVENTORY.md` § Recovery /
rotation.

## 2. Folder ID retrieval

Designated folders are identified by their Drive folder ID (the long
opaque string in the URL).

### 2.1 My Drive folder

1. Open the folder in `https://drive.google.com/`.
2. URL is `https://drive.google.com/drive/folders/<FOLDER_ID>`.
3. Copy `<FOLDER_ID>` into `sources.yaml` under
   `sources.drive.accounts[].folders[].id`.

### 2.2 "Shared with me" folder

The shared folder's URL still contains its real folder ID; you can paste
that directly into `sources.yaml`. If the folder is hard to navigate to in
"Shared with me", create a shortcut in My Drive for navigation comfort
(right-click → "Add shortcut to Drive"). The shortcut's URL points at the
**original** folder ID — use that, not the shortcut's own ID.

If you do NOT add a shortcut and you'd rather find the ID via API:

```bash
python3 - <<'PY'
import json, urllib.parse, urllib.request
from pathlib import Path

ACCOUNT_SLUG = "adithya-eclipse"
cred = json.loads(Path(f"/Users/shakstzy/ULTRON/_credentials/gmail-{ACCOUNT_SLUG}.json").read_text())
tok_data = urllib.parse.urlencode({
    "client_id": cred["client_id"],
    "client_secret": cred["client_secret"],
    "refresh_token": cred["refresh_token"],
    "grant_type": "refresh_token",
}).encode()
tok = json.loads(urllib.request.urlopen(urllib.request.Request(cred.get("token_uri", "https://oauth2.googleapis.com/token"), data=tok_data, method="POST"), timeout=10).read())
q = urllib.parse.quote("mimeType='application/vnd.google-apps.folder' and sharedWithMe=true")
url = f"https://www.googleapis.com/drive/v3/files?q={q}&fields=files(id,name,owners(emailAddress))&pageSize=100"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok['access_token']}"})
print(json.dumps(json.loads(urllib.request.urlopen(req, timeout=10).read()), indent=2))
PY
```

### 2.3 Validation

After populating `sources.yaml`, run the structural validator:

```bash
python3 _shell/bin/validate-drive-config.py
```

Add `--live` to confirm every folder ID is reachable via the account's
credential and every `exclude_subfolders[].id` is actually a descendant of
its parent. Live validation makes Drive API calls; skip when developing
offline.

## 3. sources.yaml drive block

Per workspace, in `workspaces/<ws>/config/sources.yaml`:

```yaml
sources:
  drive:
    accounts:
      - account: adithya@outerscope.xyz
        folders:
          - id: 1abcDEF_folder_id        # from the Drive folder URL
            name: "Eclipse Labs"
          - id: 2ghiJKL_folder_id
            name: "Investor Updates"
            exclude_subfolders:
              - id: 9xyzPDQ_drafts_folder_id
                name: "Drafts"
      - account: adithya.shak.kumar@gmail.com
        folders:
          - id: 3mnoSTU_folder_id
            name: "Personal Documents"
```

Schema reference in `format.md` Lock 10. The `name:` field is human-only;
the robot keys on `id`. Designated folders are recursive by default;
`exclude_subfolders` carves out specific subtrees.

**Multi-workspace claims**: by default each folder ID belongs to exactly
one workspace. Validator flags duplicate claims as errors. Intentional
fan-out (one folder, multiple workspaces) is a routing-layer feature that
will land in a later session.

## 4. Realistic timing expectations

Drive API quotas: 1,000 units / user / 100 seconds (default). A `files.get`
with content export is 1–5 units; `files.list` page is ~10–50 units. So
per-account practical throughput is ~50 file content reads per minute
sustained, with bursts much higher.

| Scenario | Expected duration |
|---|---|
| First reconciliation, ~50 files in the designated folder | 30–60 seconds |
| First reconciliation, ~500 files | 8–15 minutes |
| First reconciliation, ~5,000 files | 1–3 hours (rate-limited; backoff dominates) |
| Daily incremental, low activity | seconds to a minute |
| Daily incremental, high activity (50 files changed) | 1–3 minutes |
| `--mode reconcile` daily safety pass | scales with total file count, similar to first run but cached |

If the first reconciliation overruns: the robot pauses on 429 (exponential
backoff + jitter) but does not abort. A long first run is fine — the
flock prevents overlap with the next scheduled invocation.

## 5. Multi-account setup

Each upstream Gmail account is one robot run, one credential file, one
cursor, one flock. To wire multiple accounts:

1. Add an entry per account under `sources.drive.accounts[]` in the
   workspace's `sources.yaml` (one block per workspace; multiple
   `accounts[]` entries inside it).
2. Run validation: `_shell/bin/validate-drive-config.py`.
3. The plist compiler (when ULTRON's launchd schedule is run) generates
   one `com.adithya.ultron.ingest-drive-<account-slug>.plist` per unique
   account-slug across all workspaces. Same dedup logic as Gmail
   (`_credentials/INVENTORY.md` § Plist inventory note).

## 6. Manual smoke test (before activating)

With `IMPLEMENTATION_READY = False`, the robot exits 0 with a TODO message.
Once the implementation lands, smoke-test BEFORE flipping the flag in main:

```bash
# Dry-run on a single small folder
python3 _shell/bin/ingest-drive.py \
  --account adithya@eclipse.builders \
  --folder <small_test_folder_id> \
  --max-files 5 \
  --mode reconcile \
  --dry-run --show
```

Expect: 0–5 rendered file blobs printed to stdout, no writes, no cursor
mutation. Verify path, frontmatter, body shape against `format.md`.

## 7. Activation (flipping `IMPLEMENTATION_READY`)

Do NOT flip until ALL of the below are green:

1. OAuth scope verified per account (§ 1.1) — at least one account must
   have `drive` or `drive.readonly`.
2. At least one workspace's `sources.yaml` has a `drive` block with at
   least one designated folder.
3. Validators green (structural):
   ```bash
   python3 _shell/bin/check-routes.py
   python3 _shell/bin/check-frontmatter.py
   python3 _shell/tests/test_rename_slug.py
   python3 _shell/bin/validate-drive-config.py
   ```
4. Live validator green:
   ```bash
   python3 _shell/bin/validate-drive-config.py --live
   ```
5. `pdftotext` available on `$PATH` (`brew install poppler` if missing).
   `markitdown` available as a fallback (`pip3 install markitdown`).
6. Dry-run smoke test (§ 6) prints sane content.

When all green, edit `_shell/bin/ingest-drive.py` and set:

```python
IMPLEMENTATION_READY = True
```

First live run should be a single small designated folder against one
account, e.g.:

```bash
python3 _shell/bin/ingest-drive.py \
  --account adithya@eclipse.builders \
  --folder <small_test_folder_id> \
  --mode reconcile \
  --max-files 25
```

Then unlock the full enumerate:

```bash
python3 _shell/bin/ingest-drive.py \
  --account adithya@eclipse.builders \
  --mode reconcile
```

Wire to launchd in a separate session.

## 8. Troubleshooting

- **`invalid_grant` on token refresh**: the refresh token was revoked.
  Re-mint via gog (§ 1.3) and update the credential file.
- **`insufficientScopes`**: the token doesn't have `drive` or
  `drive.readonly`. Re-mint with the scope flag (§ 1.3).
- **`notFound` on a designated folder ID**: the account doesn't have
  permission, or the folder was deleted. Verify in the UI, then either
  remove the folder from `sources.yaml` or have it re-shared.
- **`changes.list` returns 410 (token expired)**: cursor expired (Drive
  retains tokens ~30 days). Robot auto-recovers by deleting the cursor
  and falling through to full reconciliation. No manual action needed.
- **Sustained 429s on first run**: large designated folder. Lower
  `--max-files` for the bootstrap, then lift the cap on the next run.
  Quota recovers per-100-seconds; the robot's exponential backoff handles
  this automatically — be patient.
- **PDF extraction returning empty bodies**: scanned/image-only PDFs.
  Frontmatter records `text_extraction_succeeded: false`. v1 does not OCR.
- **Sheet content looks wrong**: v1 exports the FIRST tab only. Check
  `multi_tab_sheet: true` in frontmatter; if there's important data on
  another tab, the v1.5 multi-tab export is the unblock path.
- **Folder rename in Drive**: existing raw files KEEP their old paths
  (the robot is prospective-only on renames). New ingests / re-ingests
  land at the new path. Reconciliation hard-deletes the orphans on the
  next run.

## 9. v1 vs v1.5 caveats (deferred work)

| Gap | v1 behavior | v1.5 plan |
|---|---|---|
| Sheets multi-tab | First tab only | Per-tab files; routing by tab name |
| Comments / suggestions | Skipped | Render inline below the affected paragraph |
| Embedded images | `[image: <inline>]` placeholder | Optional copy to `_attachments/` |
| Scanned PDFs | Empty body, `text_extraction_succeeded: false` | OCR via separate skill |
| Drawings / Forms / Sites | Skipped (Lock 5) | Out of scope |
| Per-folder routing rules | Folder claim is exclusive per workspace | `also_route_to:` for explicit fan-out |
| Owner / sharing changes | Re-derived on re-ingest | `permissions.list` events drive immediate re-render |
| Cross-source merge | Drive file isolated from Gmail attachment of same file | Wiki entity page synthesizes |

## 10. Cross-references

- Data spec: `format.md`. Workflow: `CONTEXT.md`. Routing: `route.py`.
- Validator: `_shell/bin/validate-drive-config.py`.
- Universal envelope check: `_shell/bin/check-frontmatter.py`.
- Credential inventory: `_credentials/INVENTORY.md`.
