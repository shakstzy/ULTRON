#!/usr/bin/env python3
"""
ingest-drive.py — Google Drive → workspaces/<ws>/raw/drive/...

Authoritative spec: _shell/stages/ingest/drive/format.md
Workflow: _shell/stages/ingest/drive/CONTEXT.md
Setup / activation: _shell/stages/ingest/drive/SETUP.md
Routing: _shell/stages/ingest/drive/route.py

One robot run = one upstream account.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml as _yaml

IMPLEMENTATION_READY = True

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
CREDS_DIR = ULTRON_ROOT / "_credentials"
CURSORS_DIR = ULTRON_ROOT / "_shell" / "cursors" / "drive"
LOGS_DIR = ULTRON_ROOT / "_logs"

INGEST_VERSION = 1

MIME_FOLDER = "application/vnd.google-apps.folder"
MIME_SHORTCUT = "application/vnd.google-apps.shortcut"
MIME_DOC = "application/vnd.google-apps.document"
MIME_SHEET = "application/vnd.google-apps.spreadsheet"
MIME_SLIDE = "application/vnd.google-apps.presentation"
MIME_PDF = "application/pdf"

MIME_SKIP_PREFIXES = ("video/", "audio/", "image/")
MIME_SKIP_EXACT = frozenset({
    "application/zip",
    "application/x-tar",
    "application/gzip",
    "application/x-7z-compressed",
    "application/x-rar-compressed",
    "application/octet-stream",
    "application/vnd.google-apps.script",
    "application/vnd.google-apps.form",
    "application/vnd.google-apps.drawing",
    "application/vnd.google-apps.site",
})

MIME_ALLOWED: dict[str, str] = {
    MIME_PDF: "pdf",
    MIME_DOC: "doc",
    MIME_SHEET: "sheet",
    MIME_SLIDE: "slide",
}

MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024

DRIVE_API = "https://www.googleapis.com/drive/v3"
SHEETS_API = "https://sheets.googleapis.com/v4"
TOKEN_URI = "https://oauth2.googleapis.com/token"

_SLUG_RUN_RE = re.compile(r"[^a-z0-9]+")
_HEX_FILTER_RE = re.compile(r"[^a-z0-9]")

MARKITDOWN_BIN = shutil.which("markitdown") or "/Users/shakstzy/.local/bin/markitdown"
PDFTOTEXT_BIN = shutil.which("pdftotext")

DRIVE_FIELDS = (
    "id,name,mimeType,size,createdTime,modifiedTime,parents,trashed,"
    "owners(emailAddress,displayName),"
    "lastModifyingUser(emailAddress,displayName,permissionId),"
    "webViewLink,headRevisionId,shortcutDetails,"
    "capabilities(canDownload,canReadRevisions),"
    "explicitlyTrashed,sharedWithMeTime,driveId"
)

# How many extra hex chars to try on filename collision before aborting.
COLLISION_LADDER = (8, 12, 16, 24)


# ============================================================================
# Slug / path helpers (Lock 9, Lock 1)
# ============================================================================

def account_slug(email: str) -> str:
    if not email or "@" not in email:
        return ""
    local, _, domain = email.lower().partition("@")
    first_segment = domain.split(".")[0] if domain else ""
    raw = f"{local}-{first_segment}".strip("-")
    return _SLUG_RUN_RE.sub("-", raw).strip("-")


def _slug_pipeline(name: str) -> str:
    if not name:
        return ""
    try:
        import unicodedata
        name = unicodedata.normalize("NFKD", name)
        name = "".join(c for c in name if not unicodedata.combining(c))
    except Exception:
        pass
    name = name.encode("ascii", "ignore").decode("ascii").lower()
    name = _SLUG_RUN_RE.sub("-", name).strip("-")
    return name[:60].rstrip("-")


def folder_segment_slug(name: str) -> str:
    return _slug_pipeline(name) or "untitled-folder"


def file_slug(name: str) -> str:
    if not name:
        return "untitled-file"
    stem = name.rsplit(".", 1)[0] if "." in name else name
    return _slug_pipeline(stem) or "untitled-file"


def file_id_short(file_id: str, length: int = 8) -> str:
    if not file_id:
        return "0" * length
    head = file_id[:length].lower()
    return _HEX_FILTER_RE.sub("_", head)


def cred_path(account: str) -> Path:
    return CREDS_DIR / f"gmail-{account_slug(account)}.json"


def cursor_path(account: str) -> Path:
    return CURSORS_DIR / f"{account_slug(account)}.txt"


def lock_path(account: str) -> Path:
    # NOTE: must NOT collide with the cron plist's outer `flock -n` path
    # (/tmp/com.adithya.ultron.ingest-drive-<account>.lock). Same reasoning
    # as ingest-slack.py — the outer flock would silently starve the inner
    # one and the script would exit 0 doing zero work under launchd.
    return Path(f"/tmp/ultron-ingest-drive-{account_slug(account)}.script.lock")


# ============================================================================
# Drive API client
# ============================================================================

class DriveClient:
    def __init__(self, cred: dict):
        self._cred = cred
        self._access_token: str | None = None
        self._token_exp = 0.0

    def _refresh(self) -> None:
        data = urllib.parse.urlencode({
            "client_id": self._cred["client_id"],
            "client_secret": self._cred["client_secret"],
            "refresh_token": self._cred["refresh_token"],
            "grant_type": "refresh_token",
        }).encode()
        req = urllib.request.Request(
            self._cred.get("token_uri", TOKEN_URI), data=data, method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            tok = json.loads(r.read())
        self._access_token = tok["access_token"]
        self._token_exp = time.time() + int(tok.get("expires_in", 3600)) - 60

    def _token(self) -> str:
        if not self._access_token or time.time() >= self._token_exp:
            self._refresh()
        return self._access_token  # type: ignore[return-value]

    def _request(self, url: str, method: str = "GET", binary: bool = False, max_retries: int = 5):
        attempt = 0
        while True:
            req = urllib.request.Request(
                url, method=method,
                headers={"Authorization": f"Bearer {self._token()}"},
            )
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    body = r.read()
                return body if binary else json.loads(body)
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                    time.sleep(min(2 ** attempt + 0.3 * attempt, 30))
                    attempt += 1
                    continue
                if e.code == 401 and attempt < 1:
                    self._refresh()
                    attempt += 1
                    continue
                raise
            except urllib.error.URLError:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    attempt += 1
                    continue
                raise

    def list_children(self, parent_id: str) -> list[dict]:
        out: list[dict] = []
        page = ""
        fields = f"files({DRIVE_FIELDS}),nextPageToken"
        q = f"'{parent_id}' in parents and trashed=false"
        while True:
            url = (
                f"{DRIVE_API}/files?q={urllib.parse.quote(q)}"
                f"&fields={urllib.parse.quote(fields)}"
                f"&pageSize=200"
                f"&supportsAllDrives=true&includeItemsFromAllDrives=true"
            )
            if page:
                url += f"&pageToken={urllib.parse.quote(page)}"
            resp = self._request(url)
            assert isinstance(resp, dict)
            out.extend(resp.get("files", []))
            page = resp.get("nextPageToken", "")
            if not page:
                break
        return out

    def get_file(self, file_id: str, fields: str | None = None) -> dict:
        f = fields or DRIVE_FIELDS
        url = f"{DRIVE_API}/files/{urllib.parse.quote(file_id)}?fields={urllib.parse.quote(f)}&supportsAllDrives=true"
        resp = self._request(url)
        assert isinstance(resp, dict)
        return resp

    def list_permissions(self, file_id: str) -> tuple[list[dict], bool]:
        """Returns (permissions, visible). Paginated. visible=False ONLY on
        403/404 (limited sharing visibility). Other HTTP errors propagate so
        the run fails and the cursor doesn't advance."""
        out: list[dict] = []
        page = ""
        try:
            while True:
                url = (
                    f"{DRIVE_API}/files/{urllib.parse.quote(file_id)}/permissions"
                    f"?fields=permissions(emailAddress,displayName,role,type),nextPageToken"
                    f"&supportsAllDrives=true&pageSize=100"
                )
                if page:
                    url += f"&pageToken={urllib.parse.quote(page)}"
                resp = self._request(url)
                assert isinstance(resp, dict)
                out.extend(resp.get("permissions") or [])
                page = resp.get("nextPageToken", "")
                if not page:
                    break
            return (out, True)
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return ([], False)
            raise  # 500/502/503/504/429-after-retries are run-fatal

    def export(self, file_id: str, mime: str, binary: bool = False):
        url = f"{DRIVE_API}/files/{urllib.parse.quote(file_id)}/export?mimeType={urllib.parse.quote(mime)}&supportsAllDrives=true"
        body = self._request(url, binary=True)
        assert isinstance(body, bytes)
        return body if binary else body.decode("utf-8", errors="replace")

    def download(self, file_id: str) -> bytes:
        url = f"{DRIVE_API}/files/{urllib.parse.quote(file_id)}?alt=media&supportsAllDrives=true"
        body = self._request(url, binary=True)
        assert isinstance(body, bytes)
        return body

    def start_page_token(self) -> str:
        url = f"{DRIVE_API}/changes/startPageToken?supportsAllDrives=true"
        resp = self._request(url)
        assert isinstance(resp, dict)
        return resp["startPageToken"]

    def sheet_metadata(self, file_id: str) -> dict | None:
        """Returns sheet metadata, or None if Sheets API is genuinely
        unavailable for this file (403/404 — Sheets API access not granted
        or sheet hidden). Other HTTP errors propagate so the run fails."""
        url = (
            f"{SHEETS_API}/spreadsheets/{urllib.parse.quote(file_id)}"
            f"?fields=sheets.properties(title,index,sheetType)"
        )
        try:
            resp = self._request(url)
            assert isinstance(resp, dict)
            return resp
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return None
            raise  # 500/502/503/504/429-after-retries are run-fatal


# ============================================================================
# Body rendering (Lock 4)
# ============================================================================

def _extract_text_from_pdf_bytes(data: bytes):
    if PDFTOTEXT_BIN:
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as t:
                t.write(data)
                tmp = t.name
            r = subprocess.run([PDFTOTEXT_BIN, "-layout", tmp, "-"], capture_output=True, timeout=180)
            if r.returncode == 0 and r.stdout.strip():
                return (r.stdout.decode("utf-8", "replace"), "pdftotext", True)
        except Exception:
            pass
        finally:
            if tmp:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
    if MARKITDOWN_BIN and Path(MARKITDOWN_BIN).exists():
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as t:
                t.write(data)
                tmp = t.name
            r = subprocess.run([MARKITDOWN_BIN, tmp], capture_output=True, timeout=180)
            if r.returncode == 0 and r.stdout.strip():
                return (r.stdout.decode("utf-8", "replace"), "markitdown", True)
        except Exception:
            pass
        finally:
            if tmp:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
    return ("", "failed", False)


def _render_slides_from_pdf(data: bytes) -> tuple[str, str, bool]:
    text, method, ok = _extract_text_from_pdf_bytes(data)
    if not ok or not text.strip():
        return ("", method, False)

    if "\f" in text:
        pages = [p.strip() for p in text.split("\f") if p.strip()]
    else:
        pages = re.split(r"\n{3,}", text.strip())
        pages = [p.strip() for p in pages if p.strip()]
        if not pages:
            pages = [text.strip()]

    chunks: list[str] = []
    for page in pages:
        lines = [ln.rstrip() for ln in page.splitlines() if ln.strip()]
        if not lines:
            continue
        title = lines[0]
        body_lines = lines[1:] if len(lines) > 1 else []
        chunk = f"# {title}"
        if body_lines:
            chunk += "\n\n" + "\n".join(body_lines)
        chunks.append(chunk)

    return ("\n\n---\n\n".join(chunks), method, True)


def render_body(client: DriveClient, file_meta: dict) -> tuple[str, str, bool, str]:
    mime = file_meta["mimeType"]
    if mime == MIME_DOC:
        body = client.export(file_meta["id"], "text/markdown")
        assert isinstance(body, str)
        return (body, "native", True, ".md")
    if mime == MIME_SHEET:
        body = client.export(file_meta["id"], "text/csv")
        assert isinstance(body, str)
        return (body, "native", True, ".csv")
    if mime == MIME_SLIDE:
        pdf = client.export(file_meta["id"], "application/pdf", binary=True)
        assert isinstance(pdf, bytes)
        body, method, ok = _render_slides_from_pdf(pdf)
        return (body, method, ok, ".md")
    if mime == MIME_PDF:
        data = client.download(file_meta["id"])
        body, method, ok = _extract_text_from_pdf_bytes(data)
        return (body, method, ok, ".md")
    raise ValueError(f"render_body called with unsupported mime: {mime}")


# ============================================================================
# Pre-filter (Lock 5)
# ============================================================================

def should_skip(file_meta: dict) -> tuple[bool, str | None]:
    if file_meta.get("trashed"):
        return True, "trashed"
    caps = file_meta.get("capabilities") or {}
    if caps.get("canDownload") is False:
        return True, "cannot-download"
    mime = file_meta.get("mimeType") or ""
    if any(mime.startswith(p) for p in MIME_SKIP_PREFIXES):
        return True, f"mime-skip:{mime}"
    if mime in MIME_SKIP_EXACT:
        return True, f"mime-skip:{mime}"
    if mime not in MIME_ALLOWED and mime != MIME_SHORTCUT:
        return True, f"mime-not-allowed:{mime}"
    size = int(file_meta.get("size") or 0)
    if size > MAX_FILE_SIZE_BYTES:
        return True, f"size>{MAX_FILE_SIZE_BYTES}"
    return False, None


# ============================================================================
# Frontmatter (Lock 2, Lock 3)
# ============================================================================

class _QuotedStr(str):
    pass


def _quoted_str_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style='"')


_yaml.add_representer(_QuotedStr, _quoted_str_representer, Dumper=_yaml.SafeDumper)


def _ensure_string_safety(value):
    if isinstance(value, str):
        return _QuotedStr(value)
    if isinstance(value, dict):
        return {k: _ensure_string_safety(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_ensure_string_safety(v) for v in value]
    return value


def emit_frontmatter_yaml(data: dict) -> str:
    safe = _ensure_string_safety(data)
    return _yaml.safe_dump(
        safe, sort_keys=False, allow_unicode=True, default_flow_style=False, width=4096
    ).rstrip()


def build_frontmatter(
    *,
    workspace: str,
    account: str,
    designated_folder: dict,
    folder_path: list[str],
    folder_id_path: list[str],
    file_meta: dict,
    drive_file_type: str,
    body: str,
    text_method: str,
    text_ok: bool,
    shortcut_origin_id: str | None,
    shortcut_visible_name: str | None,
    re_ingest_count: int,
    last_re_ingested_at: str | None,
    shared_with: list[dict],
    shared_with_visible: bool,
    sheet_meta: dict | None,
    sheet_metadata_visible: bool,
    raw_identity_id: str,
) -> dict:
    import blake3 as _blake3

    body_hash = _blake3.blake3(body.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    owner = (file_meta.get("owners") or [{}])[0]
    last_mod = file_meta.get("lastModifyingUser") or {}

    # drive_file_name: shortcut's visible name when applicable, target's name
    # otherwise. Path uses shortcut name's slug; frontmatter records both ids.
    visible_name = shortcut_visible_name or file_meta.get("name") or ""

    fm: dict = {
        "source": "drive",
        "workspace": workspace,
        "ingested_at": now,
        "ingest_version": INGEST_VERSION,
        "content_hash": f"blake3:{body_hash}",
        "provider_modified_at": file_meta.get("modifiedTime") or "",
        "drive_account": account,
        "drive_account_slug": account_slug(account),
        "drive_file_id": file_meta["id"],
        "drive_file_id_short": file_id_short(file_meta["id"]),
        "drive_raw_identity_id": raw_identity_id,
        "drive_mime_type": file_meta["mimeType"],
        "drive_file_type": drive_file_type,
        "drive_file_name": visible_name,
        "drive_file_size_bytes": int(file_meta.get("size") or 0),
        "drive_web_view_link": file_meta.get("webViewLink") or "",
        "drive_created_at": file_meta.get("createdTime") or "",
        "drive_modified_at": file_meta.get("modifiedTime") or "",
        "drive_version": str(file_meta.get("headRevisionId") or ""),
        "drive_folder_path": folder_path,
        "drive_folder_id_path": folder_id_path,
        "drive_designated_folder_id": designated_folder["folder_id"],
        "drive_designated_folder_name": designated_folder["folder_name"],
        "owner": {
            "email": owner.get("emailAddress") or "",
            "display_name": owner.get("displayName") or "",
        },
        "last_modifier": {
            "email": last_mod.get("emailAddress") or "",
            "display_name": last_mod.get("displayName") or "",
            "modified_at": file_meta.get("modifiedTime") or "",
        },
        "shared_with": [
            {"email": p.get("emailAddress") or "",
             "role": p.get("role") or "",
             "display_name": p.get("displayName") or ""}
            for p in shared_with if p.get("emailAddress")
        ],
        "shared_with_visible": shared_with_visible,
        "text_extraction_method": text_method,
        "text_extraction_succeeded": text_ok,
        "last_re_ingested_at": last_re_ingested_at,
        "re_ingest_count": re_ingest_count,
    }
    if shortcut_origin_id:
        fm["drive_shortcut_origin_id"] = shortcut_origin_id
    if drive_file_type == "sheet":
        if sheet_meta and isinstance(sheet_meta.get("sheets"), list):
            tabs = [s.get("properties", {}).get("title", "")
                    for s in sheet_meta["sheets"] if isinstance(s, dict)]
            tabs = [t for t in tabs if t]
            fm["multi_tab_sheet"] = len(tabs) > 1
            fm["sheet_tab_names"] = tabs
            fm["sheet_exported_tab"] = tabs[0] if tabs else None
        else:
            fm["multi_tab_sheet"] = False
            fm["sheet_tab_names"] = []
            fm["sheet_exported_tab"] = None
        fm["sheet_metadata_visible"] = sheet_metadata_visible
    return fm


# ============================================================================
# Raw enumeration (for Lock 6 reconciliation)
# ============================================================================

FRONTMATTER_FENCE_RE = re.compile(r"^---\s*\n(.+?)\n---\s*", re.DOTALL)


def _read_raw_frontmatter(path: Path) -> dict | None:
    try:
        if path.suffix == ".csv":
            sidecar = path.with_suffix(".csv.frontmatter.yaml")
            if not sidecar.exists():
                return None
            return _yaml.safe_load(sidecar.read_text()) or {}
        text = path.read_text(errors="ignore")
        m = FRONTMATTER_FENCE_RE.match(text)
        if not m:
            return None
        return _yaml.safe_load(m.group(1)) or {}
    except (OSError, _yaml.YAMLError):
        return None


def _enumerate_raw(account: str, ws: str, designated_folder_id: str) -> dict:
    """Returns { drive_raw_identity_id: {path, modified_at, ...} } for a single workspace."""
    out: dict[str, dict] = {}
    base = ULTRON_ROOT / "workspaces" / ws / "raw" / "drive" / account_slug(account)
    if not base.exists():
        return out
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in (".md", ".csv"):
            continue
        if p.name.endswith(".csv.frontmatter.yaml"):
            continue
        fm = _read_raw_frontmatter(p)
        if not fm:
            continue
        if fm.get("source") != "drive":
            continue
        if fm.get("drive_designated_folder_id") != designated_folder_id:
            continue
        ident = fm.get("drive_raw_identity_id") or fm.get("drive_file_id")
        if not ident:
            continue
        out[ident] = {
            "path": p,
            "modified_at": fm.get("provider_modified_at") or fm.get("drive_modified_at") or "",
            "re_ingest_count": int(fm.get("re_ingest_count") or 0),
            "last_re_ingested_at": fm.get("last_re_ingested_at"),
            "frontmatter": fm,
        }
    return out


# ============================================================================
# Atomic write helpers
# ============================================================================

def _atomic_write_text(path: Path, content: str) -> None:
    """Write text via temp + rename so partial writes never land at the final
    path. Also fsync the parent directory after rename — without it, the
    rename can be lost across power failure even though the new inode survives."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp.{os.getpid()}")
    with tmp.open("w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dir_fd = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    except OSError:
        pass
    finally:
        os.close(dir_fd)


def serialize_md(file_path: Path, frontmatter: dict, body: str) -> None:
    yaml_block = emit_frontmatter_yaml(frontmatter)
    out = f"---\n{yaml_block}\n---\n\n{body}"
    if not out.endswith("\n"):
        out += "\n"
    _atomic_write_text(file_path, out)


def serialize_csv_with_sidecar(file_path: Path, frontmatter: dict, body: str) -> None:
    """Write the BODY first, then the sidecar. If a crash interrupts between
    the two writes, the result is: new body + stale (or missing) sidecar.
    The next reconcile reads the stale sidecar's provider_modified_at,
    finds it doesn't match Drive's modifiedTime, and triggers a full
    re-render that fixes both. The reverse order (sidecar-first) would
    advertise the new content via NEW provider_modified_at while the body
    on disk is still old → next reconcile would short-circuit on the
    matching modified_at and never repair the body. Body-first is the
    self-healing order."""
    sidecar = file_path.with_suffix(".csv.frontmatter.yaml")
    _atomic_write_text(file_path, body)
    _atomic_write_text(sidecar, emit_frontmatter_yaml(frontmatter) + "\n")


def hard_delete(path: Path, log_action) -> None:
    if path.exists():
        path.unlink()
        log_action({"action": "delete", "path": str(path.relative_to(ULTRON_ROOT))})
    sidecar = path.with_suffix(".csv.frontmatter.yaml") if path.suffix == ".csv" else None
    if sidecar and sidecar.exists():
        sidecar.unlink()
        log_action({"action": "delete-sidecar", "path": str(sidecar.relative_to(ULTRON_ROOT))})


# ============================================================================
# CLI
# ============================================================================

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="ingest-drive.py",
        description="Google Drive → ULTRON raw markdown. See format.md for spec.",
    )
    p.add_argument("--account", required=True)
    p.add_argument("--workspaces", help="Comma-separated subset; default = all subscribers")
    p.add_argument("--mode", choices=("reconcile", "incremental"), default="reconcile",
                   help="reconcile = Lock 6 source of truth (v1 default). incremental = Lock 7 (first-run falls back to reconcile; cursor-driven path NotImplementedError until Lock 7 ships).")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--show", action="store_true")
    p.add_argument("--max-files", type=int, default=0,
                   help="Cap on files processed. When hit, skips the deletion phase to avoid wiping unvisited raw files.")
    p.add_argument("--folder", help="Restrict to one designated folder ID")
    p.add_argument("--reset-cursor", action="store_true")
    p.add_argument("--no-content", action="store_true")
    p.add_argument("--run-id", default=time.strftime("%Y%m%dT%H%M%S"))
    return p.parse_args(argv)


def acquire_flock(path: Path):
    """Per-account flock. Concurrent invocation exits 0 silently."""
    import fcntl
    fh = open(path, "w")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fh.close()
        sys.exit(0)
    return fh


def load_workspace_configs() -> dict[str, dict]:
    out: dict[str, dict] = {}
    ws_root = ULTRON_ROOT / "workspaces"
    if not ws_root.exists():
        return out
    for ws_dir in ws_root.iterdir():
        if not ws_dir.is_dir() or ws_dir.name.startswith("_"):
            continue
        cfg = ws_dir / "config" / "sources.yaml"
        if not cfg.exists():
            continue
        try:
            out[ws_dir.name] = _yaml.safe_load(cfg.read_text()) or {}
        except _yaml.YAMLError as e:
            sys.stderr.write(f"ingest-drive: {ws_dir.name}/sources.yaml unreadable: {e}\n")
    return out


def designated_folders_for(account: str, workspaces: dict[str, dict]) -> list[dict]:
    out: list[dict] = []
    for ws, cfg in workspaces.items():
        sources = cfg.get("sources") if isinstance(cfg, dict) else None
        block = sources.get("drive") if isinstance(sources, dict) else None
        if not block:
            continue
        for acct in block.get("accounts") or []:
            if not isinstance(acct, dict):
                continue
            if (acct.get("account") or "").lower() != account.lower():
                continue
            for folder in acct.get("folders") or []:
                if not isinstance(folder, dict) or not folder.get("id"):
                    continue
                out.append({
                    "workspace": ws,
                    "folder_id": folder["id"],
                    "folder_name": folder.get("name") or "",
                    "exclude_subfolders": [
                        e.get("id") for e in (folder.get("exclude_subfolders") or [])
                        if isinstance(e, dict) and e.get("id")
                    ],
                })
    return out


def load_drive_route_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "drive_route", ULTRON_ROOT / "_shell" / "stages" / "ingest" / "drive" / "route.py"
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ============================================================================
# Reconcile (Lock 6) — phased: enumerate → plan → write → delete
# ============================================================================

def reconcile(args, designated, client, account, workspaces_filter: dict[str, dict] | None = None):
    workspaces = workspaces_filter if workspaces_filter is not None else load_workspace_configs()
    drive_route = load_drive_route_module()

    # Cursor captured BEFORE any enumeration so changes during the run replay.
    pre_cursor: str | None = None
    try:
        pre_cursor = client.start_page_token()
    except Exception as e:
        sys.stderr.write(f"ingest-drive: cursor-pre fetch failed (non-fatal): {e}\n")

    log_path = LOGS_DIR / f"drive-{account_slug(account)}-{args.run_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = log_path.open("a") if not args.dry_run else None

    def log(record: dict) -> None:
        record.setdefault("ts", datetime.now(timezone.utc).isoformat(timespec="seconds"))
        record.setdefault("account", account)
        record.setdefault("run_id", args.run_id)
        if log_fh:
            log_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            log_fh.flush()

    log({"action": "run-start", "mode": "reconcile",
         "designated_folders": [{"workspace": d["workspace"], "id": d["folder_id"], "name": d["folder_name"]} for d in designated],
         "pre_cursor": pre_cursor})

    written = updated = unchanged = skipped = deleted = 0
    failed: list[tuple[str, str]] = []
    cap = args.max_files or 10**9
    cap_hit = False
    sheet_meta_cache: dict[str, tuple[dict | None, bool]] = {}
    perms_cache: dict[str, tuple[list[dict], bool]] = {}

    try:
        for d in designated:
            sys.stderr.write(f"ingest-drive: reconciling '{d['folder_name']}' ({d['folder_id']}) → {d['workspace']}\n")
            excluded = set(d.get("exclude_subfolders") or [])
            raw_index = _enumerate_raw(account, d["workspace"], d["folder_id"])

            # ----- PHASE 1: enumerate Drive ----------------------------------
            # Track per-subtree enumeration failures. If any subtree failed,
            # the deletion pass is skipped for that designated folder.
            enum_failed = False
            drive_files: list[dict] = []  # each: {file_meta, shortcut_origin_id, shortcut_visible_name, path_segments, path_ids}

            def walk(parent_id: str, path_segments: list[str], path_ids: list[str]) -> bool:
                """Returns True if subtree fully enumerated."""
                nonlocal enum_failed, cap_hit
                try:
                    children = client.list_children(parent_id)
                except urllib.error.HTTPError as e:
                    failed.append((parent_id, f"list_children HTTP {e.code}"))
                    log({"action": "fail", "subtree": parent_id, "reason": f"list_children HTTP {e.code}"})
                    enum_failed = True
                    return False
                for child in children:
                    if len(drive_files) >= cap:
                        cap_hit = True
                        log({"action": "cap-hit", "limit": cap})
                        return False
                    if child["mimeType"] == MIME_FOLDER:
                        if child["id"] in excluded:
                            log({"action": "exclude-subfolder", "id": child["id"], "name": child["name"]})
                            continue
                        ok = walk(
                            child["id"],
                            path_segments + [folder_segment_slug(child["name"])],
                            path_ids + [child["id"]],
                        )
                        if not ok:
                            return False
                        continue

                    shortcut_origin_id: str | None = None
                    shortcut_visible_name: str | None = None
                    file_meta = child
                    if child["mimeType"] == MIME_SHORTCUT:
                        sd = child.get("shortcutDetails") or {}
                        target_id = sd.get("targetId")
                        target_mime = sd.get("targetMimeType")
                        if not target_id:
                            skipped_local("shortcut-no-target", child)
                            continue
                        if target_mime not in MIME_ALLOWED:
                            skipped_local(f"shortcut-target-mime:{target_mime}", child)
                            continue
                        try:
                            file_meta = client.get_file(target_id)
                        except urllib.error.HTTPError as e:
                            failed.append((child.get("name", ""), f"shortcut-target {target_id}: HTTP {e.code}"))
                            log({"action": "fail", "name": child.get("name"),
                                 "reason": f"shortcut-target HTTP {e.code}"})
                            enum_failed = True  # don't delete the shortcut's existing raw on transient failure
                            continue
                        shortcut_origin_id = child["id"]
                        shortcut_visible_name = child.get("name")

                    skip, reason = should_skip(file_meta)
                    if skip:
                        skipped_local(reason, file_meta)
                        continue

                    drive_files.append({
                        "file_meta": file_meta,
                        "shortcut_origin_id": shortcut_origin_id,
                        "shortcut_visible_name": shortcut_visible_name,
                        "path_segments": path_segments,
                        "path_ids": path_ids,
                    })
                return True

            def skipped_local(reason: str, fm: dict) -> None:
                nonlocal skipped
                skipped += 1
                sys.stderr.write(f"  skip {fm.get('name')}: {reason}\n")
                log({"action": "skip", "name": fm.get("name"), "reason": reason})

            walk(d["folder_id"], [], [])

            # ----- PHASE 2: plan + write/update -----------------------------
            live_keys: set[str] = set()
            for entry in drive_files:
                file_meta = entry["file_meta"]
                shortcut_origin_id = entry["shortcut_origin_id"]
                shortcut_visible_name = entry["shortcut_visible_name"]
                path_segments = entry["path_segments"]
                path_ids = entry["path_ids"]

                drive_file_type = MIME_ALLOWED[file_meta["mimeType"]]
                ext = ".csv" if drive_file_type == "sheet" else ".md"
                raw_identity_id = shortcut_origin_id or file_meta["id"]

                # Slug: shortcut's name when applicable, else target/file name
                slug_source = shortcut_visible_name or file_meta.get("name") or ""
                slug_stem = file_slug(slug_source)

                # Routing — confirm the file is claimed by this workspace
                # BEFORE marking the identity as "live" for delete protection.
                # If a previously-routed file is no longer routed, its raw
                # SHOULD be deleted by Phase 3.
                routing_meta = {
                    "drive_account": account,
                    "drive_designated_folder_id": d["folder_id"],
                }
                routes = drive_route.route(routing_meta, workspaces)
                routes = [r for r in routes if r["workspace"] == d["workspace"]]
                if not routes:
                    skipped += 1
                    log({"action": "skip", "name": slug_source, "reason": "unrouted"})
                    continue
                live_keys.add(raw_identity_id)

                for r in routes:
                    ws = r["workspace"]
                    out_dir = ULTRON_ROOT / "workspaces" / ws / "raw" / "drive" / account_slug(account)
                    if path_segments:
                        out_dir = out_dir.joinpath(*path_segments)

                    # Filename collision ladder
                    out_path = None
                    for length in COLLISION_LADDER:
                        idn = file_id_short(raw_identity_id, length)
                        cand = out_dir / f"{slug_stem}__{idn}{ext}"
                        if not cand.exists():
                            out_path = cand
                            break
                        existing_fm = _read_raw_frontmatter(cand)
                        if existing_fm:
                            existing_identity = (
                                existing_fm.get("drive_raw_identity_id")
                                or existing_fm.get("drive_file_id")
                            )
                            if existing_identity == raw_identity_id:
                                out_path = cand
                                break
                        # collision: same path, different identity → try longer
                        log({"action": "collision-extend", "path": str(cand.relative_to(ULTRON_ROOT)),
                             "id_short_attempted": idn, "attempted_length": length})
                    if out_path is None:
                        failed.append((slug_source, "filename-collision-unresolved"))
                        log({"action": "fail", "name": slug_source, "reason": "filename-collision-unresolved"})
                        continue

                    existing = raw_index.get(raw_identity_id)
                    drive_mtime = file_meta.get("modifiedTime") or ""
                    body_unchanged = bool(existing and existing["modified_at"] == drive_mtime
                                          and existing["path"] == out_path)

                    # Sheet metadata (cache per file_id)
                    sheet_meta = None
                    sheet_visible = True
                    if drive_file_type == "sheet":
                        if file_meta["id"] not in sheet_meta_cache:
                            sm = client.sheet_metadata(file_meta["id"])
                            sheet_meta_cache[file_meta["id"]] = (sm, sm is not None)
                        sheet_meta, sheet_visible = sheet_meta_cache[file_meta["id"]]

                    # Permissions (cache per file_id). list_permissions() handles
                    # 403/404 internally as visibility=false; let other HTTP
                    # errors propagate so the run fails and the cursor doesn't
                    # advance past partial state.
                    if file_meta["id"] not in perms_cache:
                        perms_cache[file_meta["id"]] = client.list_permissions(file_meta["id"])
                    shared, shared_visible = perms_cache[file_meta["id"]]

                    # Render body only when modifiedTime advanced (or first ingest)
                    if body_unchanged:
                        # Reuse existing body to avoid API churn but rebuild
                        # frontmatter so permission/sharing changes propagate.
                        try:
                            existing_text = existing["path"].read_text(errors="ignore")
                            if ext == ".csv":
                                body = existing_text
                            else:
                                body_match = re.match(r"^---\s*\n.+?\n---\s*\n+", existing_text, re.DOTALL)
                                body = existing_text[body_match.end():] if body_match else existing_text
                        except OSError:
                            body_unchanged = False  # force re-render
                        method = existing.get("frontmatter", {}).get("text_extraction_method", "native")
                        ok = bool(existing.get("frontmatter", {}).get("text_extraction_succeeded", True))

                    if not body_unchanged:
                        if args.no_content:
                            body, method, ok = "", "skipped", True
                        else:
                            try:
                                body, method, ok, _ext_check = render_body(client, file_meta)
                            except urllib.error.HTTPError as e:
                                failed.append((slug_source, f"render: HTTP {e.code}"))
                                log({"action": "fail", "name": slug_source, "reason": f"render HTTP {e.code}"})
                                continue

                    # Re-ingest counters preserve existing values
                    if existing and not body_unchanged:
                        re_count = existing["re_ingest_count"] + 1
                        re_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
                    elif existing:
                        re_count = existing["re_ingest_count"]
                        re_at = existing["last_re_ingested_at"]
                    else:
                        re_count = 0
                        re_at = None

                    fm = build_frontmatter(
                        workspace=ws, account=account, designated_folder=d,
                        folder_path=path_segments, folder_id_path=path_ids,
                        file_meta=file_meta, drive_file_type=drive_file_type,
                        body=body, text_method=method, text_ok=ok,
                        shortcut_origin_id=shortcut_origin_id,
                        shortcut_visible_name=shortcut_visible_name,
                        re_ingest_count=re_count, last_re_ingested_at=re_at,
                        shared_with=shared, shared_with_visible=shared_visible,
                        sheet_meta=sheet_meta, sheet_metadata_visible=sheet_visible,
                        raw_identity_id=raw_identity_id,
                    )
                    rel = out_path.relative_to(ULTRON_ROOT)

                    if args.dry_run:
                        sys.stderr.write(f"  [dry] {rel} ({len(body)}b, method={method}, body_unchanged={body_unchanged})\n")
                        if args.show:
                            print(f"\n══════ {rel} ══════")
                            print(f"---\n{emit_frontmatter_yaml(fm)}\n---\n")
                            print(body)
                        if existing:
                            updated += 1
                        else:
                            written += 1
                        continue

                    # Atomic write (new path first; existing at different
                    # path is deleted in PHASE 4 / move-cleanup below).
                    if drive_file_type == "sheet":
                        serialize_csv_with_sidecar(out_path, fm, body)
                    else:
                        serialize_md(out_path, fm, body)

                    # If this was a move, the old path lives in raw_index
                    # under the same identity → schedule for delete after
                    # write succeeds.
                    if existing and existing["path"] != out_path:
                        hard_delete(existing["path"], log)
                        log({"action": "move-cleanup", "from": str(existing["path"].relative_to(ULTRON_ROOT)),
                             "to": str(rel)})

                    if existing:
                        if body_unchanged:
                            unchanged += 1
                            log({"action": "frontmatter-only", "path": str(rel)})
                        else:
                            updated += 1
                            log({"action": "update", "path": str(rel), "method": method,
                                 "drive_file_id": file_meta["id"], "raw_identity_id": raw_identity_id,
                                 "modified_at": drive_mtime})
                    else:
                        written += 1
                        log({"action": "write", "path": str(rel), "method": method,
                             "drive_file_id": file_meta["id"], "raw_identity_id": raw_identity_id,
                             "modified_at": drive_mtime})
                    sys.stderr.write(f"  {'frontmatter-only' if (existing and body_unchanged) else ('update' if existing else 'write')} {rel}\n")

            # ----- PHASE 3: DELETE — only if enum complete + no cap hit -----
            if enum_failed:
                log({"action": "delete-pass-skipped", "reason": "enum-failures",
                     "designated_folder_id": d["folder_id"]})
                sys.stderr.write(f"  delete pass SKIPPED for {d['folder_id']} (enum had failures)\n")
            elif cap_hit:
                log({"action": "delete-pass-skipped", "reason": "cap-hit",
                     "designated_folder_id": d["folder_id"]})
                sys.stderr.write(f"  delete pass SKIPPED for {d['folder_id']} (--max-files cap hit)\n")
            else:
                for ident, entry in raw_index.items():
                    if ident in live_keys:
                        continue
                    if not args.dry_run:
                        hard_delete(entry["path"], log)
                    else:
                        sys.stderr.write(f"  [dry] would delete {entry['path'].relative_to(ULTRON_ROOT)}\n")
                        log({"action": "would-delete", "path": str(entry["path"].relative_to(ULTRON_ROOT))})
                    deleted += 1

        sys.stderr.write(
            f"\ningest-drive: reconcile done — written={written}, updated={updated}, "
            f"unchanged={unchanged}, deleted={deleted}, skipped={skipped}, failed={len(failed)}\n"
        )
        for name, why in failed:
            sys.stderr.write(f"  FAIL {name}: {why}\n")

        log({"action": "run-end", "summary": {
            "written": written, "updated": updated, "unchanged": unchanged,
            "deleted": deleted, "skipped": skipped, "failed": len(failed),
            "cap_hit": cap_hit,
        }})

        # Cursor advances ONLY if no failures + no cap hit + not dry-run
        if not args.dry_run and not failed and not cap_hit and pre_cursor:
            CURSORS_DIR.mkdir(parents=True, exist_ok=True)
            cursor_path(account).write_text(pre_cursor + "\n")
            sys.stderr.write(f"ingest-drive: cursor → {pre_cursor}\n")
        elif failed:
            sys.stderr.write("ingest-drive: cursor NOT advanced (run had failures)\n")
        elif cap_hit:
            sys.stderr.write("ingest-drive: cursor NOT advanced (--max-files cap hit)\n")

        return 0 if not failed else 1
    finally:
        if log_fh:
            log_fh.close()


def incremental(args, designated, client, account, workspaces_filter=None):
    """Lock 7 fast-path. First-run (cursor missing/empty) falls through to
    reconcile per spec. Cursor-driven event stream not yet implemented;
    raises NotImplementedError when a cursor exists."""
    cur_p = cursor_path(account)
    if not cur_p.exists() or not cur_p.read_text().strip():
        sys.stderr.write("ingest-drive: incremental first-run → falling back to reconcile per Lock 7.\n")
        return reconcile(args, designated, client, account, workspaces_filter)
    raise NotImplementedError(
        "Lock 7 cursor-driven incremental is not yet implemented. "
        "Use --mode reconcile until it ships, or --reset-cursor to force first-run reconcile."
    )


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    cred_p = cred_path(args.account)
    if not cred_p.exists():
        sys.stderr.write(f"ingest-drive: missing credential at {cred_p}.\n")
        return 0

    workspaces = load_workspace_configs()
    if args.workspaces:
        keep = set(args.workspaces.split(","))
        workspaces = {k: v for k, v in workspaces.items() if k in keep}

    designated = designated_folders_for(args.account, workspaces)
    if args.folder:
        designated = [d for d in designated if d["folder_id"] == args.folder]
    if not designated:
        sys.stderr.write(
            f"ingest-drive: no designated folders for {args.account} in any "
            "workspace's sources.yaml. See SETUP.md § 3.\n"
        )
        return 0

    if not IMPLEMENTATION_READY:
        sys.stderr.write("ingest-drive: IMPLEMENTATION_READY = False; skeleton-only.\n")
        return 0

    CURSORS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if args.reset_cursor and cursor_path(args.account).exists():
        cursor_path(args.account).unlink()

    cred = json.loads(cred_p.read_text())
    if "_account" in cred and "account" not in cred:
        cred["account"] = cred["_account"]
    client = DriveClient(cred)

    fh = acquire_flock(lock_path(args.account))
    try:
        if args.mode == "reconcile":
            return reconcile(args, designated, client, args.account, workspaces)
        return incremental(args, designated, client, args.account, workspaces)
    finally:
        fh.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
