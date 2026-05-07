#!/usr/bin/env python3
"""
ingest-paper.py — paper ingest for the library workspace.

Inputs:
  - arxiv ID or URL: 1706.03762, https://arxiv.org/abs/1706.03762, https://arxiv.org/pdf/1706.03762
  - doi.org URL: https://doi.org/<doi>
  - direct PDF URL: anything ending in .pdf
  - local PDF path: --pdf-path /path/to/paper.pdf

Pipeline:
  1. Resolve to a local PDF
  2. Extract metadata (arxiv API for arxiv IDs; PDF text for others)
  3. Run docling (preferred) or pdftotext for clean markdown
  4. Synthesize wiki entity page via cloud-llm
  5. Write raw + wiki, log

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
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import lib_common as L

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) ULTRON-library/1.0"
HTTP_TIMEOUT = 60
ARXIV_API = "http://export.arxiv.org/api/query?id_list={id}"

ARXIV_ID_RE = re.compile(r"\b(\d{4}\.\d{4,5})(v\d+)?\b")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return resp.read()


def download_to(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp, open(dest, "wb") as out:
        shutil.copyfileobj(resp, out)


# ---------------------------------------------------------------------------
# arXiv API
# ---------------------------------------------------------------------------

def arxiv_metadata(arxiv_id: str) -> dict:
    """Query arXiv API for metadata. Returns dict with title, authors, year, abstract."""
    raw = fetch(ARXIV_API.format(id=arxiv_id))
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(raw)
    entry = root.find("a:entry", ns)
    if entry is None:
        raise RuntimeError(f"arxiv: no entry for {arxiv_id}")
    title = (entry.find("a:title", ns).text or "").strip()
    title = re.sub(r"\s+", " ", title)
    abstract = (entry.find("a:summary", ns).text or "").strip()
    abstract = re.sub(r"\s+", " ", abstract)
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
    }


# ---------------------------------------------------------------------------
# PDF → markdown via docling preferred, pdftotext fallback
# ---------------------------------------------------------------------------

def pdf_to_markdown(pdf_path: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    docling = shutil.which("docling")
    if docling:
        cmd = [docling, "--from", "pdf", "--to", "md", "--output", str(out_path.parent), str(pdf_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if proc.returncode == 0:
            # docling writes <stem>.md to output dir; rename if needed
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
    raise RuntimeError("neither docling nor pdftotext available; install one")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def parse_input(target: str) -> dict:
    """Classify the input and return {kind, ...}."""
    # arxiv ID literal
    m = ARXIV_ID_RE.fullmatch(target.strip())
    if m:
        return {"kind": "arxiv", "arxiv_id": m.group(1)}
    # arxiv URL
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
    overwrite: bool = False,
) -> Path:
    if not target and not pdf_path:
        raise ValueError("must provide a URL/arxiv-id positional or --pdf-path")

    meta: dict = {}

    # Step 1: resolve to local PDF + collect metadata
    if pdf_path:
        local_pdf = Path(pdf_path).expanduser().resolve()
        if not local_pdf.exists():
            raise FileNotFoundError(local_pdf)
        meta = {"title": title, "authors": [author] if author else [], "year": year, "pdf_url": None}
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
            print(f"  doi-only ingest not yet supported; pass an arxiv URL or --pdf-path", file=sys.stderr)
            sys.exit(2)
        else:
            print(f"  unsupported input shape: {target!r}", file=sys.stderr)
            sys.exit(2)

    final_title = meta.get("title") or title or local_pdf.stem
    final_authors = meta.get("authors") or ([author] if author else ["Anonymous"])
    final_year = meta.get("year") or year or 0
    first_author = final_authors[0] if final_authors else "Anonymous"
    slug = L.paper_slug(final_title, first_author, final_year or "noyear")

    # Raw dir
    paper_dir = L.RAW / "papers" / slug
    paper_dir.mkdir(parents=True, exist_ok=True)
    raw_pdf_path = paper_dir / "paper.pdf"
    if local_pdf.resolve() != raw_pdf_path.resolve():
        shutil.copy2(local_pdf, raw_pdf_path)

    md_path = paper_dir / "paper.md"
    print(f"  extracting → {md_path}")
    pdf_to_markdown(raw_pdf_path, md_path)

    # Sanity: must have some text
    if not md_path.exists() or md_path.stat().st_size < 1000:
        raise RuntimeError(f"extracted markdown too short ({md_path.stat().st_size if md_path.exists() else 0} bytes)")

    raw_meta = {
        "slug": slug,
        "title": final_title,
        "authors": final_authors,
        "year": final_year,
        "arxiv_id": meta.get("arxiv_id"),
        "doi": meta.get("doi"),
        "abstract": meta.get("abstract"),
        "pdf_url": meta.get("pdf_url"),
        "ingested_at": L.today(),
        "raw_md_path": str(md_path.relative_to(L.WORKSPACE)),
        "raw_pdf_sha256": L.file_sha256(raw_pdf_path),
    }
    L.write_md(paper_dir / "metadata.md", raw_meta, "")

    # Synthesize — papers are usually 8-30 pages so often fit in one shot
    md_text = md_path.read_text(encoding="utf-8", errors="replace")
    print(f"  synthesizing wiki page via cloud-llm…")
    syn = L.synthesize(
        metadata={
            "title": final_title,
            "authors": final_authors,
            "year": final_year,
            "type": "paper",
            "abstract": meta.get("abstract"),
        },
        content=md_text,
        max_content_chars=80_000,
    )

    # Author stubs
    author_slugs = [L.ensure_person_stub(a, role="author", domain=None) for a in final_authors]

    base_fm = {
        "type": "paper",
        "title": final_title,
        "authors": author_slugs,
        "venue": meta.get("venue"),
        "year": final_year or None,
        "arxiv_id": meta.get("arxiv_id"),
        "doi": meta.get("doi"),
        "source_url": meta.get("pdf_url") or target,
        "tags": [],
        "mentioned_concepts": [],
        "mentioned_books": [],
    }
    page = L.write_entity_page("paper", slug, base_fm, syn, overwrite=overwrite)
    print(f"  wrote {page.relative_to(L.WORKSPACE)}")
    L.log_event(f"ingest-paper: {slug} ({final_title!r})")
    L.log_ingest("paper", slug, "ok", {"first_author": first_author, "year": final_year})
    return page


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="arxiv URL/ID, doi URL, or direct PDF URL")
    ap.add_argument("--pdf-path", help="local PDF file path")
    ap.add_argument("--title")
    ap.add_argument("--author")
    ap.add_argument("--year", type=int)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    if not args.target and not args.pdf_path:
        ap.print_help()
        return 2
    try:
        ingest_paper(
            target=args.target,
            pdf_path=args.pdf_path,
            title=args.title,
            author=args.author,
            year=args.year,
            overwrite=args.overwrite,
        )
    except SystemExit:
        raise
    except Exception as e:
        print(f"  FATAL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
