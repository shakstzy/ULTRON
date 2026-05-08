#!/usr/bin/env python3
"""
ingest-notion.py — Notion → workspaces/<ws>/raw/notion/...

Authoritative spec: _shell/stages/ingest/notion/format.md
Workflow:           _shell/stages/ingest/notion/CONTEXT.md
Routing:            _shell/stages/ingest/notion/route.py

Single Python entry point. Stdlib + yaml + blake3 + cloud-llm (for image VLM).

Per-workspace targets are declared in `workspaces/<ws>/config/sources.yaml`
under `sources.notion.targets`. Each target is one root page or database.
The walker recurses into child_page and child_database blocks; every Notion
page becomes one .md file. Pages whose `last_edited_time` matches the
existing file's frontmatter `provider_modified_at` are skipped.

Auth: integration token from macOS Keychain at service `quantum-notion`,
account `default`. The integration must be invited to each target page.

Image blocks are downloaded to `<page-dir>/_assets/<block-id8>.<ext>` and
described via cloud-llm Gemini Flash. File blocks are recorded as a
metadata-only line (name + type) — no download, no VLM.
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
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml as _yaml

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
LOGS_DIR = ULTRON_ROOT / "_logs"
INGEST_VERSION = 1

NOTION_API = "https://api.notion.com/v1"
NOTION_API_VERSION = "2022-06-28"

KEYCHAIN_SERVICE = "quantum-notion"
KEYCHAIN_ACCOUNT = "default"

CLOUD_LLM_PATH = Path.home() / ".claude" / "skills" / "cloud-llm"

VLM_PROMPT = (
    "Describe this image in one sentence under 120 characters. "
    "Be concrete and specific. No preamble."
)
VLM_DESC_CAP = 120

PAGE_SIZE = 100  # Notion API default

# Block types we render verbatim. Anything else falls through to a
# "[unsupported: <type>]" stub so the source isn't silently dropped.
SUPPORTED_BLOCK_TYPES = frozenset({
    "paragraph", "heading_1", "heading_2", "heading_3",
    "bulleted_list_item", "numbered_list_item", "to_do",
    "toggle", "quote", "callout", "code", "divider",
    "image", "file", "pdf", "video", "audio",
    "bookmark", "embed", "link_preview",
    "child_page", "child_database",
    "table", "table_row",
    "column_list", "column",
    "synced_block", "equation",
})


# ============================================================================
# Slug helpers (mirror ingest-drive.py's pipeline)
# ============================================================================

_SLUG_RUN_RE = re.compile(r"[^a-z0-9]+")


def _slugify(name: str, max_len: int = 60) -> str:
    if not name:
        return ""
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.encode("ascii", "ignore").decode("ascii").lower()
    name = _SLUG_RUN_RE.sub("-", name).strip("-")
    return name[:max_len].rstrip("-") or "untitled"


def _id8(uuid_or_id: str) -> str:
    """Notion IDs are dashed UUIDs — strip dashes, take first 8 hex chars."""
    s = (uuid_or_id or "").replace("-", "").lower()
    s = re.sub(r"[^a-f0-9]", "", s)
    return (s + "0" * 8)[:8]


def _normalize_id(uuid_or_id: str) -> str:
    """Strip dashes for stable comparison + URL paths; Notion API accepts both."""
    return (uuid_or_id or "").replace("-", "").lower()


# ============================================================================
# Token + API client
# ============================================================================

def _keychain_token() -> str:
    p = subprocess.run(
        ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE,
         "-a", KEYCHAIN_ACCOUNT, "-w"],
        capture_output=True, text=True,
    )
    if p.returncode != 0:
        sys.stderr.write(
            f"ingest-notion: Keychain miss for service={KEYCHAIN_SERVICE} "
            f"account={KEYCHAIN_ACCOUNT}\n{p.stderr}"
        )
        sys.exit(2)
    tok = p.stdout.strip()
    if not tok:
        sys.exit("ingest-notion: empty token from Keychain")
    return tok


class NotionClient:
    def __init__(self, token: str):
        self.token = token

    def _request(self, method: str, path: str, body: dict | None = None,
                 max_retries: int = 5) -> dict:
        url = f"{NOTION_API}{path}"
        attempt = 0
        while True:
            data = json.dumps(body).encode() if body is not None else None
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": NOTION_API_VERSION,
                "Content-Type": "application/json",
            }
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < max_retries:
                    retry_after = float(e.headers.get("Retry-After", "1"))
                    time.sleep(min(retry_after, 30))
                    attempt += 1
                    continue
                if e.code in (500, 502, 503, 504) and attempt < max_retries:
                    time.sleep(min(2 ** attempt, 30))
                    attempt += 1
                    continue
                body_text = ""
                try:
                    body_text = e.read().decode("utf-8", "replace")[:400]
                except Exception:
                    pass
                raise RuntimeError(f"notion {method} {path} HTTP {e.code}: {body_text}") from e
            except urllib.error.URLError:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    attempt += 1
                    continue
                raise

    def get_page(self, page_id: str) -> dict:
        return self._request("GET", f"/pages/{_normalize_id(page_id)}")

    def get_database(self, db_id: str) -> dict:
        return self._request("GET", f"/databases/{_normalize_id(db_id)}")

    def get_block(self, block_id: str) -> dict:
        return self._request("GET", f"/blocks/{_normalize_id(block_id)}")

    def list_block_children(self, block_id: str) -> list[dict]:
        out: list[dict] = []
        cursor = None
        while True:
            qs = f"page_size={PAGE_SIZE}"
            if cursor:
                qs += f"&start_cursor={urllib.parse.quote(cursor)}"
            resp = self._request("GET", f"/blocks/{_normalize_id(block_id)}/children?{qs}")
            out.extend(resp.get("results", []))
            if not resp.get("has_more"):
                return out
            cursor = resp.get("next_cursor")

    def query_database(self, db_id: str) -> list[dict]:
        out: list[dict] = []
        cursor = None
        while True:
            body: dict = {"page_size": PAGE_SIZE}
            if cursor:
                body["start_cursor"] = cursor
            resp = self._request("POST", f"/databases/{_normalize_id(db_id)}/query", body=body)
            out.extend(resp.get("results", []))
            if not resp.get("has_more"):
                return out
            cursor = resp.get("next_cursor")


# ============================================================================
# Rich-text rendering
# ============================================================================

def _rt_render(rich_text: list[dict]) -> str:
    """Notion rich_text array → markdown inline string."""
    parts: list[str] = []
    for r in rich_text or []:
        text = r.get("plain_text", "")
        if not text:
            continue
        ann = r.get("annotations") or {}
        if ann.get("code"):
            text = f"`{text}`"
        if ann.get("bold"):
            text = f"**{text}**"
        if ann.get("italic"):
            text = f"*{text}*"
        if ann.get("strikethrough"):
            text = f"~~{text}~~"
        if ann.get("underline"):
            text = f"<u>{text}</u>"
        href = r.get("href")
        if href:
            text = f"[{text}]({href})"
        parts.append(text)
    return "".join(parts)


def _page_title(page: dict) -> str:
    """Extract a page title from a page object (page or db row)."""
    props = page.get("properties") or {}
    # Database rows: find the "title" property
    for prop in props.values():
        if (prop or {}).get("type") == "title":
            return _rt_render(prop.get("title") or []).strip() or "Untitled"
    # Top-level pages: properties.title (older shape) or .Name (DB title prop)
    title = props.get("title") or {}
    rt = title.get("title") if isinstance(title, dict) else None
    if rt:
        return _rt_render(rt).strip() or "Untitled"
    return "Untitled"


# ============================================================================
# Image / file block media handling
# ============================================================================

def _media_url(block: dict, kind: str) -> tuple[str, str | None]:
    """Returns (url, name). For file/image/pdf/video/audio blocks."""
    payload = block.get(kind) or {}
    name = payload.get("name") or ""
    if payload.get("type") == "external":
        return ((payload.get("external") or {}).get("url", ""), name)
    if payload.get("type") == "file":
        return ((payload.get("file") or {}).get("url", ""), name)
    return ("", name)


def _ext_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    base = parsed.path.rsplit("/", 1)[-1]
    if "." in base:
        ext = "." + base.rsplit(".", 1)[-1].lower()
        # Strip query-tail from extension
        ext = re.sub(r"[^a-z0-9.]+", "", ext)
        if 2 <= len(ext) <= 6:
            return ext
    return ".bin"


def _download_to(url: str, dest: Path, timeout: int = 60) -> bool:
    if not url:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ULTRON-ingest-notion/1"})
        with urllib.request.urlopen(req, timeout=timeout) as r, \
             tempfile.NamedTemporaryFile(delete=False, dir=dest.parent,
                                         prefix=".tmp.", suffix=dest.suffix) as t:
            tmp_path = Path(t.name)
            shutil.copyfileobj(r, t)
        os.replace(tmp_path, dest)
        return True
    except (urllib.error.URLError, OSError) as e:
        sys.stderr.write(f"  download failed {url[:80]}: {e}\n")
        try:
            if "tmp_path" in locals():
                tmp_path.unlink(missing_ok=True)  # type: ignore[arg-type]
        except Exception:
            pass
        return False


_CLOUD_LLM_LOADED = False
_describe_images = None


def _load_cloud_llm():
    global _CLOUD_LLM_LOADED, _describe_images
    if _CLOUD_LLM_LOADED:
        return _describe_images
    sys.path.insert(0, str(CLOUD_LLM_PATH))
    try:
        from client import describe_images  # type: ignore
        _describe_images = describe_images
    except Exception as e:
        sys.stderr.write(f"ingest-notion: cloud-llm import failed: {e}\n")
        _describe_images = None
    _CLOUD_LLM_LOADED = True
    return _describe_images


def _describe_image(path: Path) -> str | None:
    fn = _load_cloud_llm()
    if fn is None:
        return None
    try:
        result = fn([str(path.resolve())], VLM_PROMPT)
    except Exception as e:
        sys.stderr.write(f"  VLM error {path.name}: {e}\n")
        return None
    desc = (result or {}).get("output") or ""
    desc = desc.strip().splitlines()[0].strip() if desc.strip() else ""
    if not desc:
        return None
    if len(desc) > VLM_DESC_CAP:
        desc = desc[: VLM_DESC_CAP - 1].rstrip() + "…"
    return desc


# ============================================================================
# Block → markdown
# ============================================================================

class RenderCtx:
    """Per-page rendering state. Holds child links + asset directory for VLM."""

    def __init__(self, page_dir: Path, client: NotionClient,
                 child_pages: list[dict], child_dbs: list[dict],
                 image_descriptions: bool, _seen: set[str] | None = None):
        self.page_dir = page_dir
        self.client = client
        # Each: {"id": <id>, "title": <title>, "slug": <slug>, "kind": "page"|"db"}
        self.child_pages = child_pages
        self.child_dbs = child_dbs
        self.image_descriptions = image_descriptions
        self._seen_synced: set[str] = _seen or set()


def _render_blocks(blocks: list[dict], ctx: RenderCtx, depth: int = 0) -> str:
    out: list[str] = []
    in_list_kind: str | None = None
    for blk in blocks:
        t = blk.get("type")
        rendered, list_kind = _render_block(blk, ctx, depth)
        # blank line between non-list blocks; tighter spacing between list items
        if list_kind != in_list_kind:
            if out and not out[-1].endswith("\n\n"):
                out.append("\n")
            in_list_kind = list_kind
        if not rendered:
            continue
        if list_kind:
            out.append(rendered + "\n")
        else:
            out.append(rendered + "\n\n")
    return "".join(out).rstrip() + "\n"


def _indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line if line else line for line in text.split("\n"))


def _render_block(blk: dict, ctx: RenderCtx, depth: int) -> tuple[str, str | None]:
    """Returns (markdown, list_kind). list_kind is "ul"|"ol"|None."""
    t = blk.get("type") or ""
    payload = blk.get(t) or {}
    has_children = bool(blk.get("has_children"))
    rt = payload.get("rich_text") or []
    text = _rt_render(rt) if rt else ""

    children_md = ""
    if has_children and t not in ("child_page", "child_database", "synced_block",
                                  "table", "column_list"):
        try:
            kids = ctx.client.list_block_children(blk["id"])
        except Exception as e:
            sys.stderr.write(f"  child fetch failed {blk['id'][:8]} ({t}): {e}\n")
            kids = []
        if kids:
            children_md = _render_blocks(kids, ctx, depth + 1).rstrip()

    if t == "paragraph":
        body = text
        if children_md:
            body = (body + "\n\n" + _indent(children_md, "  ")).strip()
        return body, None

    if t in ("heading_1", "heading_2", "heading_3"):
        level = {"heading_1": 1, "heading_2": 2, "heading_3": 3}[t]
        # Toggle heading? Notion exposes is_toggleable + has_children — keep flat in v1.
        return f"{'#' * level} {text}".rstrip(), None

    if t == "bulleted_list_item":
        body = f"- {text}"
        if children_md:
            body += "\n" + _indent(children_md, "  ")
        return body, "ul"

    if t == "numbered_list_item":
        body = f"1. {text}"
        if children_md:
            body += "\n" + _indent(children_md, "   ")
        return body, "ol"

    if t == "to_do":
        checked = payload.get("checked")
        body = f"- [{'x' if checked else ' '}] {text}"
        if children_md:
            body += "\n" + _indent(children_md, "  ")
        return body, "ul"

    if t == "toggle":
        # Render as a callout-style fold: a > line then indented children.
        body = f"<details><summary>{text}</summary>\n\n{children_md}\n\n</details>"
        return body, None

    if t == "quote":
        body = "\n".join(f"> {ln}" for ln in text.split("\n"))
        if children_md:
            body += "\n" + _indent(children_md, "> ")
        return body, None

    if t == "callout":
        icon = (payload.get("icon") or {}).get("emoji") or ""
        body = f"> {icon + ' ' if icon else ''}{text}".rstrip()
        if children_md:
            body += "\n" + _indent(children_md, "> ")
        return body, None

    if t == "code":
        lang = payload.get("language") or ""
        return f"```{lang}\n{text}\n```", None

    if t == "divider":
        return "---", None

    if t == "equation":
        expr = payload.get("expression") or text
        return f"$$\n{expr}\n$$", None

    if t == "bookmark":
        url = payload.get("url") or ""
        cap = _rt_render(payload.get("caption") or [])
        return f"[{cap or url}]({url})", None

    if t in ("embed", "link_preview"):
        url = payload.get("url") or ""
        return f"[{url}]({url})", None

    if t in ("image", "video", "audio"):
        url, name = _media_url(blk, t)
        cap = _rt_render(payload.get("caption") or [])
        if t == "image":
            return _render_image(blk, url, cap, ctx), None
        # video / audio: link only (Adithya: only image blocks go to VLM)
        label = cap or name or t
        return f"[{label}]({url})" if url else f"[{label}](#)", None

    if t in ("file", "pdf"):
        url, name = _media_url(blk, t)
        cap = _rt_render(payload.get("caption") or [])
        # Adithya: file blocks → metadata-only line, no download, no VLM.
        # URL is signed and expires; record name + caption only.
        label = cap or name or t
        return f"📎 **{label}** _(notion {t})_", None

    if t == "child_page":
        title = payload.get("title") or "Untitled"
        slug = _slugify(title)
        ctx.child_pages.append({
            "id": blk["id"],
            "title": title,
            "slug": slug,
            "kind": "page",
        })
        return f"[[{slug}__{_id8(blk['id'])}|{title}]]", None

    if t == "child_database":
        title = payload.get("title") or "Untitled DB"
        slug = _slugify(title)
        ctx.child_dbs.append({
            "id": blk["id"],
            "title": title,
            "slug": slug,
            "kind": "db",
        })
        return f"[[{slug}__{_id8(blk['id'])}/index|{title}]]", None

    if t == "synced_block":
        # Render once per page; if synced from elsewhere, follow once.
        synced_from = (payload.get("synced_from") or {}).get("block_id")
        anchor = synced_from or blk["id"]
        if anchor in ctx._seen_synced:
            return "", None
        ctx._seen_synced.add(anchor)
        try:
            kids = ctx.client.list_block_children(anchor)
        except Exception:
            kids = []
        if not kids:
            return "", None
        return _render_blocks(kids, ctx, depth + 1).rstrip(), None

    if t == "column_list":
        try:
            cols = ctx.client.list_block_children(blk["id"])
        except Exception:
            cols = []
        rendered_cols: list[str] = []
        for col in cols:
            try:
                col_kids = ctx.client.list_block_children(col["id"])
            except Exception:
                col_kids = []
            if col_kids:
                rendered_cols.append(_render_blocks(col_kids, ctx, depth + 1).rstrip())
        return "\n\n".join(rendered_cols), None

    if t == "column":
        # Handled by column_list; bare columns shouldn't appear here.
        return "", None

    if t == "table":
        try:
            rows = ctx.client.list_block_children(blk["id"])
        except Exception:
            rows = []
        return _render_table(blk, rows), None

    if t == "table_row":
        # Rendered by parent table. Bare rows shouldn't appear at top level.
        return "", None

    if t == "unsupported":
        return "[unsupported notion block]", None

    # Default: surface type tag so we know what's missing.
    return f"[unrendered:{t}]", None


def _render_image(blk: dict, url: str, caption: str, ctx: RenderCtx) -> str:
    if not url:
        return f"![{caption or 'image'}](#)"
    ext = _ext_from_url(url)
    asset_dir = ctx.page_dir / "_assets"
    asset_path = asset_dir / f"{_id8(blk['id'])}{ext}"
    rel = f"_assets/{asset_path.name}"
    if not asset_path.exists():
        ok = _download_to(url, asset_path)
        if not ok:
            return f"![{caption or 'image'}]({rel})"
    alt = caption
    if ctx.image_descriptions and not alt:
        desc = _describe_image(asset_path)
        if desc:
            alt = desc
    if not alt:
        alt = "image"
    if caption and caption != alt:
        return f"![{alt}]({rel})\n*{caption}*"
    return f"![{alt}]({rel})"


def _render_table(blk: dict, rows: list[dict]) -> str:
    payload = blk.get("table") or {}
    has_header = payload.get("has_column_header", False)
    width = payload.get("table_width") or 0
    grid: list[list[str]] = []
    for row in rows:
        cells = (row.get("table_row") or {}).get("cells") or []
        grid.append([_rt_render(c) for c in cells])
    if not grid:
        return ""
    if not width:
        width = max(len(r) for r in grid)
    for r in grid:
        while len(r) < width:
            r.append("")
    if has_header and len(grid) >= 2:
        head = grid[0]
        body = grid[1:]
    else:
        head = [""] * width
        body = grid
    out = ["| " + " | ".join(c.replace("\n", " ") for c in head) + " |"]
    out.append("| " + " | ".join(["---"] * width) + " |")
    for r in body:
        out.append("| " + " | ".join(c.replace("\n", " ") for c in r) + " |")
    return "\n".join(out)


# ============================================================================
# Page property rendering (database row props)
# ============================================================================

def _render_property(prop: dict) -> Any:
    pt = (prop or {}).get("type")
    if pt is None:
        return None
    val = prop.get(pt)
    if pt == "title":
        return _rt_render(val or [])
    if pt == "rich_text":
        return _rt_render(val or [])
    if pt == "number":
        return val
    if pt == "select":
        return (val or {}).get("name") if val else None
    if pt == "status":
        return (val or {}).get("name") if val else None
    if pt == "multi_select":
        return [s.get("name") for s in val or []]
    if pt == "date":
        if not val:
            return None
        return {"start": val.get("start"), "end": val.get("end")}
    if pt == "checkbox":
        return bool(val)
    if pt == "url":
        return val
    if pt == "email":
        return val
    if pt == "phone_number":
        return val
    if pt == "people":
        return [p.get("name") or p.get("id") for p in val or []]
    if pt == "files":
        return [f.get("name") for f in val or []]
    if pt == "relation":
        return [r.get("id") for r in val or []]
    if pt == "rollup":
        # Best-effort: stringify
        return val
    if pt == "formula":
        f = val or {}
        return f.get(f.get("type") or "")
    if pt == "created_time":
        return val
    if pt == "created_by":
        return (val or {}).get("name") or (val or {}).get("id")
    if pt == "last_edited_time":
        return val
    if pt == "last_edited_by":
        return (val or {}).get("name") or (val or {}).get("id")
    if pt == "unique_id":
        u = val or {}
        prefix = u.get("prefix")
        num = u.get("number")
        return f"{prefix}-{num}" if prefix else num
    return val


def _render_properties_block(props: dict) -> str:
    if not props:
        return ""
    lines = ["| Property | Value |", "| --- | --- |"]
    for name, prop in props.items():
        v = _render_property(prop)
        if v is None or v == "" or v == []:
            continue
        if isinstance(v, list):
            v = ", ".join(str(x) for x in v)
        elif isinstance(v, dict):
            v = json.dumps(v, ensure_ascii=False)
        v = str(v).replace("\n", " ").replace("|", "\\|")
        lines.append(f"| {name.replace('|', '\\|')} | {v} |")
    return "\n".join(lines) if len(lines) > 2 else ""


# ============================================================================
# Frontmatter + atomic write
# ============================================================================

class _QuotedStr(str):
    pass


def _quoted_repr(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style='"')


_yaml.add_representer(_QuotedStr, _quoted_repr, Dumper=_yaml.SafeDumper)


def _wrap(value):
    if isinstance(value, str):
        return _QuotedStr(value)
    if isinstance(value, dict):
        return {k: _wrap(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_wrap(v) for v in value]
    return value


def _emit_yaml(d: dict) -> str:
    return _yaml.safe_dump(_wrap(d), sort_keys=False, allow_unicode=True,
                           default_flow_style=False, width=4096).rstrip()


def _atomic_write(path: Path, content: str) -> None:
    """Atomic temp + rename, with file fsync and parent-directory fsync so
    the rename itself is durable across power failure."""
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


FM_FENCE = re.compile(r"^---\s*\n(.+?)\n---\s*", re.DOTALL)


def _read_existing_fm(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        return None
    m = FM_FENCE.match(text)
    if not m:
        return None
    try:
        return _yaml.safe_load(m.group(1)) or {}
    except _yaml.YAMLError:
        return None


def _build_frontmatter(*, workspace: str, page: dict, target_label: str,
                       parent_path: list[str], body: str, kind: str,
                       properties: dict | None) -> dict:
    import blake3 as _blake3
    body_hash = _blake3.blake3(body.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    fm: dict = {
        "source": "notion",
        "workspace": workspace,
        "ingested_at": now,
        "ingest_version": INGEST_VERSION,
        "content_hash": f"blake3:{body_hash}",
        "provider_modified_at": page.get("last_edited_time") or "",
        "notion_page_id": _normalize_id(page["id"]),
        "notion_page_id_dashed": page["id"],
        "notion_kind": kind,  # "page" | "db_index" | "db_row"
        "notion_target_label": target_label,
        "notion_url": page.get("url") or "",
        "notion_title": _page_title(page),
        "notion_parent_path": parent_path,
        "notion_created_at": page.get("created_time") or "",
        "notion_last_edited_at": page.get("last_edited_time") or "",
        "notion_archived": bool(page.get("archived")),
    }
    if properties:
        fm["notion_properties"] = properties
    return fm


def _serialize_md(path: Path, fm: dict, body: str) -> None:
    yaml_block = _emit_yaml(fm)
    out = f"---\n{yaml_block}\n---\n\n{body}"
    if not out.endswith("\n"):
        out += "\n"
    _atomic_write(path, out)


# ============================================================================
# Walker
# ============================================================================

class Walker:
    def __init__(self, *, client: NotionClient, workspace: str,
                 target_label: str, target_dir: Path,
                 image_descriptions: bool, force: bool, dry_run: bool, log):
        self.client = client
        self.workspace = workspace
        self.target_label = target_label
        self.target_dir = target_dir
        self.image_descriptions = image_descriptions
        self.force = force
        self.dry_run = dry_run
        self.log = log
        self.stats = {"written": 0, "updated": 0, "unchanged": 0, "skipped": 0,
                      "failed": 0, "images_described": 0}
        self.live_paths: set[Path] = set()  # files this run touched

    def walk_root(self, root_id: str, root_kind_hint: str | None = None) -> None:
        norm = _normalize_id(root_id)
        # Auto-detect if hint missing.
        kind = root_kind_hint
        try:
            obj = self.client.get_page(norm)
            obj_kind = "page"
        except Exception:
            try:
                obj = self.client.get_database(norm)
                obj_kind = "database"
            except Exception as e:
                sys.stderr.write(f"ingest-notion: cannot fetch {root_id}: {e}\n")
                self.stats["failed"] += 1
                return
        if kind and kind != obj_kind:
            sys.stderr.write(f"  warn: hint={kind} but actual={obj_kind} for {root_id[:8]}\n")
        if obj_kind == "page":
            self.process_page(obj, parent_dir=self.target_dir, parent_path=[self.target_label])
        else:
            self.process_database(obj, parent_dir=self.target_dir,
                                  parent_path=[self.target_label])

    def _page_filename_pair(self, page: dict, parent_dir: Path) -> tuple[Path, Path]:
        """Returns (single_file_path, folder_index_path)."""
        title = _page_title(page)
        slug = _slugify(title)
        idn = _id8(page["id"])
        name = f"{slug}__{idn}"
        return (parent_dir / f"{name}.md", parent_dir / name / "index.md")

    def _db_paths(self, db: dict, parent_dir: Path) -> tuple[Path, Path]:
        """Returns (folder, index_path)."""
        title = _page_title(db) or (db.get("title") and _rt_render(db["title"])) or "untitled-db"
        if not title or title == "Untitled":
            # databases have a separate `title` array at top level
            title = _rt_render(db.get("title") or []) or "untitled-db"
        slug = _slugify(title)
        idn = _id8(db["id"])
        folder = parent_dir / f"{slug}__{idn}"
        return (folder, folder / "index.md")

    def process_page(self, page: dict, parent_dir: Path, parent_path: list[str]) -> Path:
        if page.get("archived") and not self.force:
            self.log({"action": "skip-archived", "id": page["id"]})
            self.stats["skipped"] += 1
            return parent_dir

        single_path, folder_index = self._page_filename_pair(page, parent_dir)

        # Pre-walk: determine if page has child_page/child_database to decide
        # between single-file and folder layout. Pull children once.
        try:
            blocks = self.client.list_block_children(page["id"])
        except Exception as e:
            sys.stderr.write(f"  block fetch failed for page {page['id'][:8]}: {e}\n")
            self.stats["failed"] += 1
            return parent_dir
        has_subpages = any(b.get("type") in ("child_page", "child_database")
                           for b in blocks)
        out_path = folder_index if has_subpages else single_path
        page_dir = out_path.parent  # folder for assets + child files

        # Skip if unchanged.
        existing_fm = _read_existing_fm(out_path)
        unchanged = (
            not self.force
            and existing_fm is not None
            and existing_fm.get("provider_modified_at") == page.get("last_edited_time")
            and existing_fm.get("notion_page_id") == _normalize_id(page["id"])
        )
        if unchanged:
            self.stats["unchanged"] += 1
            self.live_paths.add(out_path)
            self.log({"action": "skip-unchanged", "path": str(out_path.relative_to(ULTRON_ROOT))})
            # Still descend into children (they may have changed even if parent didn't).
        else:
            # Render the page body.
            child_pages: list[dict] = []
            child_dbs: list[dict] = []
            ctx = RenderCtx(
                page_dir=page_dir, client=self.client,
                child_pages=child_pages, child_dbs=child_dbs,
                image_descriptions=self.image_descriptions,
            )
            body_md = _render_blocks(blocks, ctx)

            kind = "db_row" if (page.get("parent") or {}).get("type") == "database_id" else "page"

            # Properties only meaningful on database rows. Top-level pages have a
            # synthetic `title` property which duplicates notion_title — skip them.
            properties = page.get("properties") or {}
            props_compact: dict = {}
            if kind == "db_row":
                for name, prop in properties.items():
                    v = _render_property(prop)
                    if v is None or v == "" or v == []:
                        continue
                    props_compact[name] = v

            header = f"# {_page_title(page)}\n"
            if kind == "db_row" and props_compact:
                header += "\n" + _render_properties_block(properties) + "\n"
            full_body = header + "\n" + body_md

            fm = _build_frontmatter(
                workspace=self.workspace, page=page,
                target_label=self.target_label,
                parent_path=parent_path,
                body=full_body, kind=kind,
                properties=props_compact or None,
            )
            if self.dry_run:
                sys.stderr.write(f"  [dry] {out_path.relative_to(ULTRON_ROOT)} ({len(full_body)}b)\n")
            else:
                _serialize_md(out_path, fm, full_body)
                self.live_paths.add(out_path)
                action = "update" if existing_fm else "write"
                self.stats["updated" if existing_fm else "written"] += 1
                self.log({"action": action, "path": str(out_path.relative_to(ULTRON_ROOT)),
                          "title": _page_title(page),
                          "page_id": _normalize_id(page["id"])})
                sys.stderr.write(f"  {action} {out_path.relative_to(ULTRON_ROOT)}\n")

        # Recurse into subpages discovered in blocks.
        for blk in blocks:
            t = blk.get("type")
            if t == "child_page":
                try:
                    sub = self.client.get_page(blk["id"])
                except Exception as e:
                    sys.stderr.write(f"  child_page fetch failed: {e}\n")
                    self.stats["failed"] += 1
                    continue
                self.process_page(sub, parent_dir=page_dir,
                                  parent_path=parent_path + [_page_title(page)])
            elif t == "child_database":
                try:
                    sub_db = self.client.get_database(blk["id"])
                except Exception as e:
                    sys.stderr.write(f"  child_database fetch failed: {e}\n")
                    self.stats["failed"] += 1
                    continue
                self.process_database(sub_db, parent_dir=page_dir,
                                      parent_path=parent_path + [_page_title(page)])

        return page_dir

    def process_database(self, db: dict, parent_dir: Path, parent_path: list[str]) -> Path:
        folder, index_path = self._db_paths(db, parent_dir)
        folder.mkdir(parents=True, exist_ok=True)
        try:
            rows = self.client.query_database(db["id"])
        except Exception as e:
            sys.stderr.write(f"  query_database failed for {db['id'][:8]}: {e}\n")
            self.stats["failed"] += 1
            return folder

        # Recurse into each row first so wikilinks resolve.
        row_links: list[str] = []
        for row in rows:
            self.process_page(row, parent_dir=folder,
                              parent_path=parent_path + [_rt_render(db.get("title") or []) or "DB"])
            title = _page_title(row)
            slug = _slugify(title)
            idn = _id8(row["id"])
            row_links.append(f"- [[{slug}__{idn}|{title}]]")

        # Build index.md
        title = _rt_render(db.get("title") or []) or "Untitled DB"
        body_lines = [f"# {title}", ""]
        desc = _rt_render(db.get("description") or [])
        if desc:
            body_lines += [desc, ""]
        body_lines += [f"_{len(rows)} rows_", ""]
        body_lines += row_links
        body = "\n".join(body_lines) + "\n"

        existing_fm = _read_existing_fm(index_path)
        unchanged = (
            not self.force
            and existing_fm is not None
            and existing_fm.get("provider_modified_at") == db.get("last_edited_time")
            and existing_fm.get("notion_page_id") == _normalize_id(db["id"])
        )
        if unchanged:
            self.stats["unchanged"] += 1
            self.live_paths.add(index_path)
        else:
            fm = _build_frontmatter(
                workspace=self.workspace, page=db,
                target_label=self.target_label,
                parent_path=parent_path,
                body=body, kind="db_index",
                properties=None,
            )
            if self.dry_run:
                sys.stderr.write(f"  [dry] {index_path.relative_to(ULTRON_ROOT)} ({len(body)}b)\n")
            else:
                _serialize_md(index_path, fm, body)
                self.live_paths.add(index_path)
                action = "update" if existing_fm else "write"
                self.stats["updated" if existing_fm else "written"] += 1
                self.log({"action": action, "path": str(index_path.relative_to(ULTRON_ROOT)),
                          "title": title,
                          "page_id": _normalize_id(db["id"])})
                sys.stderr.write(f"  {action} {index_path.relative_to(ULTRON_ROOT)}\n")
        return folder


# ============================================================================
# Workspace config
# ============================================================================

def _load_workspace_configs() -> dict[str, dict]:
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
            sys.stderr.write(f"ingest-notion: {ws_dir.name}/sources.yaml unreadable: {e}\n")
    return out


def _targets_for_workspace(ws_cfg: dict) -> list[dict]:
    sources = (ws_cfg or {}).get("sources") or {}
    notion = sources.get("notion") or {}
    return notion.get("targets") or []


# ============================================================================
# Main
# ============================================================================

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="ingest-notion.py",
        description="Notion → ULTRON raw markdown. See _shell/stages/ingest/notion/format.md",
    )
    p.add_argument("--workspace", help="Run only this workspace (default: all subscribed).")
    p.add_argument("--url", help="Ad-hoc target URL or ID; bypasses sources.yaml. Requires --workspace.")
    p.add_argument("--label", help="Target label for --url. Default: derived from page title.")
    p.add_argument("--kind", choices=("page", "database"),
                   help="Hint for --url. Default: auto-detect.")
    p.add_argument("--no-vlm", action="store_true", help="Skip image VLM descriptions.")
    p.add_argument("--force", action="store_true", help="Re-render even if last_edited_time unchanged.")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--run-id", default=time.strftime("%Y%m%dT%H%M%S"))
    return p.parse_args(argv)


_NOTION_URL_RE = re.compile(
    r"(?:https?://[^/]+\.notion\.(?:so|site)/[^?#\s]*?)?-?([0-9a-f]{32})\b",
    re.IGNORECASE,
)


def _id_from_url_or_raw(s: str) -> str:
    m = _NOTION_URL_RE.search(s)
    if m:
        return m.group(1).lower()
    cand = s.strip().replace("-", "").lower()
    if re.fullmatch(r"[0-9a-f]{32}", cand):
        return cand
    sys.exit(f"ingest-notion: cannot parse Notion id from: {s!r}")


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"ingest-notion-{args.run_id}.log"
    log_fh = log_path.open("a") if not args.dry_run else None

    def log(record: dict) -> None:
        record.setdefault("ts", datetime.now(timezone.utc).isoformat(timespec="seconds"))
        record.setdefault("run_id", args.run_id)
        if log_fh:
            log_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            log_fh.flush()

    token = _keychain_token()
    client = NotionClient(token)

    # Verify token + capture workspace name
    try:
        me = client._request("GET", "/users/me")
        ws_name = (((me.get("bot") or {}).get("owner") or {}).get("workspace_name")
                   or me.get("name") or "?")
        bot_ws_name = (me.get("bot") or {}).get("workspace_name") or ws_name
        sys.stderr.write(f"ingest-notion: token OK — bot in '{bot_ws_name}'\n")
        log({"action": "auth-ok", "workspace_name": bot_ws_name})
    except Exception as e:
        sys.stderr.write(f"ingest-notion: token check failed: {e}\n")
        return 2

    # Build target plan
    plan: list[tuple[str, str, str | None, str | None]] = []  # (ws, root_id, kind, label)
    if args.url:
        if not args.workspace:
            sys.exit("ingest-notion: --url requires --workspace")
        rid = _id_from_url_or_raw(args.url)
        plan.append((args.workspace, rid, args.kind, args.label))
    else:
        all_ws = _load_workspace_configs()
        if args.workspace:
            all_ws = {k: v for k, v in all_ws.items() if k == args.workspace}
        for ws_slug, cfg in all_ws.items():
            for tgt in _targets_for_workspace(cfg):
                rid = _id_from_url_or_raw(tgt.get("url") or tgt.get("id") or "")
                plan.append((ws_slug, rid, tgt.get("kind"), tgt.get("label")))

    if not plan:
        sys.stderr.write("ingest-notion: no targets in plan; nothing to do.\n")
        return 0

    # Execute
    rc = 0
    grand: dict[str, int] = {"written": 0, "updated": 0, "unchanged": 0,
                             "skipped": 0, "failed": 0}
    for ws_slug, rid, kind, label in plan:
        # Resolve label if not supplied
        target_label = label
        if not target_label:
            try:
                if kind == "database":
                    obj = client.get_database(rid)
                    title = _rt_render(obj.get("title") or []) or "untitled-db"
                else:
                    obj = client.get_page(rid)
                    title = _page_title(obj)
                target_label = _slugify(title)
            except Exception:
                target_label = f"target-{rid[:8]}"
        target_dir = ULTRON_ROOT / "workspaces" / ws_slug / "raw" / "notion" / target_label
        sys.stderr.write(f"ingest-notion: → {ws_slug} :: {target_label} ({rid[:8]})\n")
        log({"action": "target-start", "workspace": ws_slug,
             "label": target_label, "id": rid, "kind": kind})

        walker = Walker(
            client=client, workspace=ws_slug,
            target_label=target_label, target_dir=target_dir,
            image_descriptions=not args.no_vlm,
            force=args.force, dry_run=args.dry_run, log=log,
        )
        try:
            walker.walk_root(rid, root_kind_hint=kind)
        except Exception as e:
            sys.stderr.write(f"ingest-notion: target {rid[:8]} crashed: {e}\n")
            log({"action": "target-fail", "id": rid, "error": str(e)})
            walker.stats["failed"] += 1
            rc = 1

        for k in grand:
            grand[k] += walker.stats.get(k, 0)
        log({"action": "target-end", "workspace": ws_slug,
             "label": target_label, "stats": dict(walker.stats)})

    sys.stderr.write(
        f"\ningest-notion: done — written={grand['written']}, "
        f"updated={grand['updated']}, unchanged={grand['unchanged']}, "
        f"skipped={grand['skipped']}, failed={grand['failed']}\n"
    )
    log({"action": "run-end", "stats": grand})
    if log_fh:
        log_fh.close()
    return 0 if grand["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
