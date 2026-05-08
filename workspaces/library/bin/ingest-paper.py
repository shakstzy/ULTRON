#!/usr/bin/env python3
"""
ingest-paper.py — capture an academic paper into the library workspace's raw/.

Pure capture: arxiv API for metadata (when applicable), download PDF, extract
markdown via docling (or pdftotext fallback), write ONE file at
`raw/papers/<slug>.md` with the universal envelope. Original PDF kept
alongside as `<slug>.pdf` for re-extraction. NO cloud-llm. NO wiki writes.

Inputs: arxiv URL/ID, doi.org URL (limited support), direct PDF URL, or
a local PDF via --pdf-path.

Usage:
  ingest-paper.py 1706.03762
  ingest-paper.py https://arxiv.org/abs/1706.03762
  ingest-paper.py --pdf-path ~/Downloads/paper.pdf --title "X" --author "Y" --year 2023
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import lib_common as L

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) ULTRON-library/1.0"
HTTP_TIMEOUT = 60
ARXIV_API = "http://export.arxiv.org/api/query?id_list={id}"
ARXIV_ID_RE = re.compile(r"\b(\d{4}\.\d{4,5})(v\d+)?\b")
SOURCE = "paper"


class IngestError(Exception):
    """Raised when ingest cannot complete. Caught by main() and by batch callers."""


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return resp.read()


def download_to(url: str, dest: Path, max_bytes: int = 200_000_000) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp, open(dest, "wb") as out:
        written = 0
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if written > max_bytes:
                out.close()
                dest.unlink(missing_ok=True)
                raise IngestError(f"download exceeded {max_bytes} bytes; aborting")
            out.write(chunk)


def arxiv_metadata(arxiv_id: str) -> dict:
    raw = fetch(ARXIV_API.format(id=arxiv_id))
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(raw)
    entry = root.find("a:entry", ns)
    if entry is None:
        raise RuntimeError(f"arxiv: no entry for {arxiv_id}")
    title = re.sub(r"\s+", " ", (entry.find("a:title", ns).text or "")).strip()
    abstract = re.sub(r"\s+", " ", (entry.find("a:summary", ns).text or "")).strip()
    published = (entry.find("a:published", ns).text or "").strip()
    year = int(published[:4]) if len(published) >= 4 else None
    authors = []
    for a in entry.findall("a:author", ns):
        n = a.find("a:name", ns)
        if n is not None and n.text:
            authors.append(n.text.strip())
    pdf_url = None
    for link in entry.findall("a:link", ns):
        if link.get("title") == "pdf":
            pdf_url = link.get("href")
    return {
        "title": title,
        "authors": authors,
        "year": year,
        "abstract": abstract,
        "pdf_url": pdf_url or f"https://arxiv.org/pdf/{arxiv_id}",
        "arxiv_id": arxiv_id,
        "published": published,
    }


def pdf_to_markdown(pdf_path: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    docling = shutil.which("docling")
    if docling:
        cmd = [docling, "--from", "pdf", "--to", "md", "--output", str(out_path.parent), str(pdf_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if proc.returncode == 0:
            produced = out_path.parent / (pdf_path.stem + ".md")
            if produced.exists() and produced.resolve() != out_path.resolve():
                shutil.move(produced, out_path)
            if out_path.exists():
                return
            print(f"  docling exited 0 but no markdown found; falling back", file=sys.stderr)
        else:
            print(f"  docling failed (rc={proc.returncode}); falling back to pdftotext\n  stderr: {proc.stderr[:200]}", file=sys.stderr)
    if shutil.which("pdftotext"):
        cmd = ["pdftotext", "-layout", str(pdf_path), str(out_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode != 0:
            raise RuntimeError(f"pdftotext failed: {proc.stderr[:200]}")
        return
    raise RuntimeError("neither docling nor pdftotext available")


def parse_input(target: str) -> dict:
    m = ARXIV_ID_RE.fullmatch(target.strip())
    if m:
        return {"kind": "arxiv", "arxiv_id": m.group(1)}
    if "arxiv.org" in target:
        m = ARXIV_ID_RE.search(target)
        if m:
            return {"kind": "arxiv", "arxiv_id": m.group(1)}
    if "doi.org/" in target:
        return {"kind": "doi", "doi": target.split("doi.org/", 1)[1]}
    if target.startswith(("http://", "https://")) and target.lower().endswith(".pdf"):
        return {"kind": "pdf-url", "url": target}
    return {"kind": "unknown", "url": target}


def ingest_paper(
    target: str | None,
    pdf_path: str | None,
    title: str | None = None,
    author: str | None = None,
    year: int | None = None,
) -> Path:
    if not target and not pdf_path:
        raise ValueError("must provide a URL/arxiv-id or --pdf-path")

    meta: dict = {}

    if pdf_path:
        local_pdf = Path(pdf_path).expanduser().resolve()
        if not local_pdf.exists():
            raise FileNotFoundError(local_pdf)
        meta = {"title": title, "authors": [author] if author else [], "year": year}
    else:
        info = parse_input(target)
        if info["kind"] == "arxiv":
            print(f"  fetching arxiv metadata: {info['arxiv_id']}")
            am = arxiv_metadata(info["arxiv_id"])
            meta.update(am)
            tmp = Path("/tmp") / f"library-paper-{L.today()}"
            tmp.mkdir(parents=True, exist_ok=True)
            local_pdf = tmp / f"{info['arxiv_id']}.pdf"
            print(f"  downloading {meta['pdf_url']} → {local_pdf}")
            download_to(meta["pdf_url"], local_pdf)
        elif info["kind"] == "pdf-url":
            tmp = Path("/tmp") / f"library-paper-{L.today()}"
            tmp.mkdir(parents=True, exist_ok=True)
            local_pdf = tmp / "paper.pdf"
            print(f"  downloading {info['url']} → {local_pdf}")
            download_to(info["url"], local_pdf)
            meta = {"title": title, "authors": [author] if author else [], "year": year, "pdf_url": info["url"]}
        elif info["kind"] == "doi":
            raise IngestError("doi-only ingest not yet supported; pass an arxiv URL or --pdf-path")
        else:
            raise IngestError(f"unsupported input shape: {target!r}")

    final_title = meta.get("title") or title or local_pdf.stem
    final_authors = meta.get("authors") or ([author] if author else ["Anonymous"])
    final_year = meta.get("year") or year or 0
    first_author = final_authors[0] if final_authors else "Anonymous"
    slug = L.paper_slug(final_title, first_author, final_year or "noyear")

    paper_dir = L.RAW / "papers"
    paper_dir.mkdir(parents=True, exist_ok=True)
    raw_pdf_path = paper_dir / f"{slug}.pdf"
    if local_pdf.resolve() != raw_pdf_path.resolve():
        shutil.copy2(local_pdf, raw_pdf_path)

    md_intermediate = paper_dir / f"{slug}.body.md"
    print(f"  extracting markdown from {raw_pdf_path.name}")
    pdf_to_markdown(raw_pdf_path, md_intermediate)
    if not md_intermediate.exists() or md_intermediate.stat().st_size < 1000:
        size = md_intermediate.stat().st_size if md_intermediate.exists() else 0
        raise IngestError(f"extracted markdown too short ({size} bytes)")
    body = md_intermediate.read_text(encoding="utf-8", errors="replace")
    md_intermediate.unlink(missing_ok=True)

    raw_path = paper_dir / f"{slug}.md"
    raw_path = L.collision_safe_path(raw_path, source_url=meta.get("pdf_url") or target)
    extra = {
        "slug": slug,
        "title": final_title,
        "authors": final_authors,
        "year": final_year or None,
        "arxiv_id": meta.get("arxiv_id"),
        "doi": meta.get("doi"),
        "venue": meta.get("venue"),
        "abstract": meta.get("abstract"),
        "pdf_url": meta.get("pdf_url") or target,
        "pdf_sha256": L.file_sha256(raw_pdf_path),
    }
    L.write_raw(
        raw_path,
        source=SOURCE,
        body=body,
        provider_modified_at=meta.get("published"),
        extra=extra,
    )
    print(f"  wrote raw/{raw_path.relative_to(L.RAW)}")
    L.log_event(f"ingest-paper: {slug} ({final_title!r})")
    L.log_ingest("paper", slug, "ok", {"first_author": first_author, "year": final_year})
    return raw_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="arxiv URL/ID, doi URL, or direct PDF URL")
    ap.add_argument("--pdf-path", help="local PDF file path")
    ap.add_argument("--title")
    ap.add_argument("--author")
    ap.add_argument("--year", type=int)
    args = ap.parse_args()

    if not args.target and not args.pdf_path:
        ap.print_help()
        return 2
    try:
        ingest_paper(args.target, args.pdf_path, args.title, args.author, args.year)
    except IngestError as e:
        print(f"  ! {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
