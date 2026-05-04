#!/usr/bin/env python3
"""
ingest-drive.py — Google Drive → workspaces/<ws>/raw/drive/...

Authoritative spec: _shell/stages/ingest/drive/format.md
Workflow: _shell/stages/ingest/drive/CONTEXT.md
Setup / activation: _shell/stages/ingest/drive/SETUP.md
Routing: _shell/stages/ingest/drive/route.py

One robot run = one upstream account. Multi-account scheduling is the
launchd / cron layer's job: one plist per account-slug.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

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
TOKEN_URI = "https://oauth2.googleapis.com/token"

_SLUG_RUN_RE = re.compile(r"[^a-z0-9]+")
_HEX_FILTER_RE = re.compile(r"[^a-z0-9]")

MARKITDOWN_BIN = shutil.which("markitdown") or "/Users/shakstzy/.local/bin/markitdown"
PDFTOTEXT_BIN = shutil.which("pdftotext")


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


def folder_segment_slug(name: str) -> str:
    if not name:
        return "untitled-folder"
    try:
        import unicodedata
        name = unicodedata.normalize("NFKD", name)
        name = "".join(c for c in name if not unicodedata.combining(c))
    except Exception:
        pass
    name = name.encode("ascii", "ignore").decode("ascii").lower()
    name = _SLUG_RUN_RE.sub("-", name).strip("-")
    if not name:
        return "untitled-folder"
    return name[:60].rstrip("-") or "untitled-folder"


def file_slug(name: str) -> str:
    if not name:
        return "untitled-file"
    stem = name.rsplit(".", 1)[0] if "." in name else name
    return folder_segment_slug(stem) or "untitled-file"


def file_id_short(file_id: str) -> str:
    if not file_id:
        return "00000000"
    head = file_id[:8].lower()
    return _HEX_FILTER_RE.sub("_", head)


def cred_path(account: str) -> Path:
    return CREDS_DIR / f"gmail-{account_slug(account)}.json"


def cursor_path(account: str) -> Path:
    return CURSORS_DIR / f"{account_slug(account)}.txt"


def lock_path(account: str) -> Path:
    return Path(f"/tmp/com.adithya.ultron.ingest-drive-{account_slug(account)}.lock")


# ============================================================================
# Drive API client (raw HTTP, urllib)
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

    def _request(self, url: str, method: str = "GET", binary: bool = False, max_retries: int = 5) -> bytes | dict:
        attempt = 0
        while True:
            req = urllib.request.Request(
                url, method=method,
                headers={"Authorization": f"Bearer {self._token()}"},
            )
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    body = r.read()
                return body if binary else json.loads(body)
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                    backoff = min(2 ** attempt + 0.3 * attempt, 30)
                    time.sleep(backoff)
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
        fields = "files(id,name,mimeType,size,createdTime,modifiedTime,parents,owners(emailAddress,displayName),lastModifyingUser(emailAddress,displayName,permissionId),webViewLink,trashed,shortcutDetails,headRevisionId,permissions(emailAddress,displayName,role)),nextPageToken"
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
        f = fields or "id,name,mimeType,size,createdTime,modifiedTime,parents,owners(emailAddress,displayName),lastModifyingUser(emailAddress,displayName,permissionId),webViewLink,trashed,shortcutDetails,headRevisionId,permissions(emailAddress,displayName,role)"
        url = f"{DRIVE_API}/files/{urllib.parse.quote(file_id)}?fields={urllib.parse.quote(f)}&supportsAllDrives=true"
        resp = self._request(url)
        assert isinstance(resp, dict)
        return resp

    def export(self, file_id: str, mime: str, binary: bool = False) -> bytes | str:
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


# ============================================================================
# Body rendering (Lock 4)
# ============================================================================

def _markitdown_bytes(data: bytes, suffix: str) -> tuple[str, str, bool]:
    """Returns (body_text, method, succeeded). Method ∈ {markitdown, pdftotext, failed}."""
    import tempfile
    if PDFTOTEXT_BIN and suffix == ".pdf":
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as t:
                t.write(data); tmp = t.name
            r = subprocess.run([PDFTOTEXT_BIN, "-layout", tmp, "-"], capture_output=True, timeout=120)
            os.unlink(tmp)
            if r.returncode == 0 and r.stdout.strip():
                return (r.stdout.decode("utf-8", "replace"), "pdftotext", True)
        except Exception:
            pass
    if MARKITDOWN_BIN and Path(MARKITDOWN_BIN).exists():
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as t:
                t.write(data); tmp = t.name
            r = subprocess.run([MARKITDOWN_BIN, tmp], capture_output=True, timeout=180)
            os.unlink(tmp)
            if r.returncode == 0 and r.stdout.strip():
                return (r.stdout.decode("utf-8", "replace"), "markitdown", True)
        except Exception:
            pass
    return ("", "failed", False)


def render_body(client: DriveClient, file_meta: dict) -> tuple[str, str, bool, str]:
    """Returns (body, method, succeeded, ext). ext ∈ {.md, .csv}."""
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
        body = client.export(file_meta["id"], "text/plain")
        assert isinstance(body, str)
        slides = [s.strip() for s in body.split("\f") if s.strip()]
        rendered = "\n\n---\n\n".join(slides) if slides else body
        return (rendered, "native", True, ".md")
    if mime == MIME_PDF:
        data = client.download(file_meta["id"])
        body, method, ok = _markitdown_bytes(data, ".pdf")
        return (body, method, ok, ".md")
    raise ValueError(f"render_body called with unsupported mime: {mime}")


# ============================================================================
# Pre-filter (Lock 5)
# ============================================================================

def should_skip(file_meta: dict) -> tuple[bool, str | None]:
    if file_meta.get("trashed"):
        return True, "trashed"
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

def _yaml_dump(value, indent: int = 0) -> str:
    """Minimal deterministic YAML emitter for our frontmatter shapes."""
    pad = "  " * indent
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        if not value:
            return '""'
        if any(c in value for c in ":#'\"\n[]{}&*!|>%@`") or value[0] in "-? " or value != value.strip():
            return json.dumps(value, ensure_ascii=False)
        return value
    if isinstance(value, list):
        if not value:
            return "[]"
        out = []
        for item in value:
            if isinstance(item, dict):
                first = True
                for k, v in item.items():
                    rendered = _yaml_dump(v, indent + 2)
                    prefix = "- " if first else "  "
                    if isinstance(v, (dict, list)) and rendered not in ("[]", "{}"):
                        out.append(f"{pad}{prefix}{k}:\n{rendered}")
                    else:
                        out.append(f"{pad}{prefix}{k}: {rendered}")
                    first = False
            else:
                out.append(f"{pad}- {_yaml_dump(item, indent + 1)}")
        return "\n".join(out)
    if isinstance(value, dict):
        if not value:
            return "{}"
        out = []
        for k, v in value.items():
            rendered = _yaml_dump(v, indent + 1)
            if isinstance(v, (dict, list)) and rendered not in ("[]", "{}"):
                out.append(f"{pad}{k}:\n{rendered}")
            else:
                out.append(f"{pad}{k}: {rendered}")
        return "\n".join(out)
    return json.dumps(value, ensure_ascii=False)


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
    re_ingest_count: int,
    last_re_ingested_at: str | None,
) -> dict:
    import blake3 as _blake3

    body_hash = _blake3.blake3(body.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    owner = (file_meta.get("owners") or [{}])[0]
    last_mod = file_meta.get("lastModifyingUser") or {}
    perms = file_meta.get("permissions") or []

    fm = {
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
        "drive_mime_type": file_meta["mimeType"],
        "drive_file_type": drive_file_type,
        "drive_file_name": file_meta.get("name") or "",
        "drive_file_size_bytes": int(file_meta.get("size") or 0),
        "drive_web_view_link": file_meta.get("webViewLink") or "",
        "drive_created_at": file_meta.get("createdTime") or "",
        "drive_modified_at": file_meta.get("modifiedTime") or "",
        "drive_version": file_meta.get("headRevisionId") or "",
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
            {"email": p.get("emailAddress") or "", "role": p.get("role") or "",
             "display_name": p.get("displayName") or ""}
            for p in perms if p.get("emailAddress")
        ],
        "text_extraction_method": text_method,
        "text_extraction_succeeded": text_ok,
        "last_re_ingested_at": last_re_ingested_at,
        "re_ingest_count": re_ingest_count,
    }
    if shortcut_origin_id:
        fm["drive_shortcut_origin_id"] = shortcut_origin_id
    if drive_file_type == "sheet":
        fm["multi_tab_sheet"] = False  # v1: first tab only; multi-tab probe deferred
        fm["sheet_tab_names"] = []
        fm["sheet_exported_tab"] = None
    return fm


def serialize(file_path: Path, frontmatter: dict, body: str) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_block = _yaml_dump(frontmatter)
    out = f"---\n{yaml_block}\n---\n\n{body}"
    if not out.endswith("\n"):
        out += "\n"
    file_path.write_text(out, encoding="utf-8")


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
    p.add_argument("--mode", choices=("reconcile", "incremental"), default="incremental")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--show", action="store_true")
    p.add_argument("--max-files", type=int, default=0)
    p.add_argument("--folder", help="Restrict to one designated folder ID")
    p.add_argument("--reset-cursor", action="store_true")
    p.add_argument("--no-content", action="store_true")
    p.add_argument("--run-id", default=time.strftime("%Y%m%dT%H%M%S"))
    return p.parse_args(argv)


def acquire_flock(path: Path):
    import fcntl
    fh = open(path, "w")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.stderr.write(f"ingest-drive: another run holds {path}; exiting 0.\n")
        fh.close()
        sys.exit(0)
    return fh


def load_workspace_configs() -> dict[str, dict]:
    import yaml
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
            out[ws_dir.name] = yaml.safe_load(cfg.read_text()) or {}
        except yaml.YAMLError as e:
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


# ============================================================================
# Reconcile (Lock 6)
# ============================================================================

def reconcile(args: argparse.Namespace, designated: list[dict], client: DriveClient, account: str) -> int:
    """Full enumeration. v1 smoke: ingest only; deletion logic is the next pass."""
    import sys as _sys
    sys.path.insert(0, str(ULTRON_ROOT / "_shell" / "stages" / "ingest" / "drive"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "drive_route", ULTRON_ROOT / "_shell" / "stages" / "ingest" / "drive" / "route.py"
    )
    drive_route = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(drive_route)  # type: ignore[union-attr]

    workspaces = load_workspace_configs()

    written = 0
    skipped = 0
    failed: list[tuple[str, str]] = []

    cap = args.max_files or 10**9

    for d in designated:
        sys.stderr.write(f"ingest-drive: reconciling folder '{d['folder_name']}' ({d['folder_id']}) → {d['workspace']}\n")
        excluded = set(d.get("exclude_subfolders") or [])

        # BFS of the designated folder
        def walk(parent_id: str, path_segments: list[str], path_ids: list[str]):
            nonlocal written, skipped
            children = client.list_children(parent_id)
            for child in children:
                if written + skipped >= cap:
                    return
                if child["mimeType"] == MIME_FOLDER:
                    if child["id"] in excluded:
                        continue
                    walk(
                        child["id"],
                        path_segments + [folder_segment_slug(child["name"])],
                        path_ids + [child["id"]],
                    )
                    continue

                # Resolve shortcut → target
                shortcut_origin_id = None
                file_meta = child
                if child["mimeType"] == MIME_SHORTCUT:
                    target_id = (child.get("shortcutDetails") or {}).get("targetId")
                    target_mime = (child.get("shortcutDetails") or {}).get("targetMimeType")
                    if not target_id:
                        skipped += 1
                        continue
                    if target_mime in MIME_ALLOWED:
                        try:
                            file_meta = client.get_file(target_id)
                        except urllib.error.HTTPError as e:
                            failed.append((child["name"], f"shortcut-target {target_id}: HTTP {e.code}"))
                            skipped += 1
                            continue
                        shortcut_origin_id = child["id"]
                    else:
                        skipped += 1
                        continue

                skip, reason = should_skip(file_meta)
                if skip:
                    skipped += 1
                    sys.stderr.write(f"  skip {file_meta.get('name')}: {reason}\n")
                    continue

                drive_file_type = MIME_ALLOWED[file_meta["mimeType"]]

                # Render body
                if args.no_content:
                    body, method, ok, ext = "", "skipped", True, (".csv" if drive_file_type == "sheet" else ".md")
                else:
                    try:
                        body, method, ok, ext = render_body(client, file_meta)
                    except urllib.error.HTTPError as e:
                        failed.append((file_meta.get("name", ""), f"render: HTTP {e.code}"))
                        skipped += 1
                        continue

                # Routing → which workspace(s) get this file
                routing_meta = {
                    "drive_account": account,
                    "drive_designated_folder_id": d["folder_id"],
                }
                routes = drive_route.route(routing_meta, workspaces)
                if not routes:
                    sys.stderr.write(f"  unrouted {file_meta.get('name')}: no workspace claims folder {d['folder_id']}\n")
                    skipped += 1
                    continue

                # Build path + frontmatter per destination workspace
                file_id_short_str = file_id_short(file_meta["id"])
                slug_stem = file_slug(file_meta.get("name") or "")
                filename = f"{slug_stem}__{file_id_short_str}{ext}"

                for r in routes:
                    ws = r["workspace"]
                    out_dir = ULTRON_ROOT / "workspaces" / ws / "raw" / "drive" / account_slug(account)
                    if path_segments:
                        out_dir = out_dir.joinpath(*path_segments)
                    out_path = out_dir / filename

                    fm = build_frontmatter(
                        workspace=ws, account=account, designated_folder=d,
                        folder_path=path_segments, folder_id_path=path_ids,
                        file_meta=file_meta, drive_file_type=drive_file_type,
                        body=body, text_method=method, text_ok=ok,
                        shortcut_origin_id=shortcut_origin_id,
                        re_ingest_count=0, last_re_ingested_at=None,
                    )
                    if args.dry_run:
                        rel = out_path.relative_to(ULTRON_ROOT)
                        sys.stderr.write(f"  [dry] would write {rel} ({len(body)} body bytes, method={method})\n")
                        if args.show:
                            print(f"\n══════ {rel} ══════")
                            print(f"---\n{_yaml_dump(fm)}\n---\n")
                            print(body[:2000])
                            if len(body) > 2000:
                                print(f"\n... [{len(body)-2000} more bytes truncated for --show]")
                    else:
                        # Sheets get raw CSV (no frontmatter wrapper would corrupt the CSV).
                        # Apply the universal envelope as a sidecar `.frontmatter.yaml` for .csv,
                        # but for v1 smoke test we'll inline-comment the YAML at the top.
                        if ext == ".csv":
                            yaml_block = _yaml_dump(fm)
                            commented = "\n".join(f"# {line}" for line in yaml_block.splitlines())
                            content = f"# ---\n{commented}\n# ---\n{body}"
                            out_path.parent.mkdir(parents=True, exist_ok=True)
                            out_path.write_text(content, encoding="utf-8")
                        else:
                            serialize(out_path, fm, body)
                        rel = out_path.relative_to(ULTRON_ROOT)
                        sys.stderr.write(f"  wrote {rel} ({len(body)} body bytes, method={method})\n")
                    written += 1

        walk(d["folder_id"], [], [])

    sys.stderr.write(
        f"\ningest-drive: reconcile done — written={written}, skipped={skipped}, "
        f"failed={len(failed)}\n"
    )
    for name, why in failed:
        sys.stderr.write(f"  FAIL {name}: {why}\n")

    # Persist a fresh changes.list page token so subsequent --mode incremental works
    if not args.dry_run:
        try:
            cursor = client.start_page_token()
            CURSORS_DIR.mkdir(parents=True, exist_ok=True)
            cursor_path(account).write_text(cursor + "\n")
            sys.stderr.write(f"ingest-drive: cursor → {cursor}\n")
        except Exception as e:
            sys.stderr.write(f"ingest-drive: cursor persist failed (non-fatal): {e}\n")

    return 0 if not failed else 1


def incremental(args, designated, client, account):
    raise NotImplementedError(
        "incremental() is the Lock 7 fast-path. Use --mode reconcile for the v1 smoke test."
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
        sys.stderr.write(
            "ingest-drive: IMPLEMENTATION_READY = False; skeleton-only.\n"
        )
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
        if args.mode == "reconcile" or not cursor_path(args.account).exists():
            return reconcile(args, designated, client, args.account)
        return incremental(args, designated, client, args.account)
    finally:
        fh.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
