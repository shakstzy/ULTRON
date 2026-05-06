#!/usr/bin/env python3
"""
describe-attachments.py — global parallel description pass.

Walks all `workspaces/<ws>/raw/imessage/**/*.md`, finds attachments
where `description: null` AND `source_available: true` AND `sha256` set,
builds ONE global worklist deduped by sha256, runs parallel Gemini
calls, then patches each affected month-file frontmatter in place.

After this completes, re-run ingest-imessage-oneshot.py to update
body lines with descriptions (it reads descriptions from the patched
frontmatter as its prior cache).

Usage:
    describe-attachments.py --workspace personal [--workers 32] [--dry-run]
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import glob
import hashlib
import os
import random
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

import yaml  # type: ignore

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
DB = Path.home() / "Library" / "Messages" / "chat.db"
ATTACHMENTS_INCLUDE = str(Path.home() / "Library" / "Messages" / "Attachments")
DESCRIPTION_MODEL = "gemini-3-flash-preview"
DEFAULT_WORKERS = 32

PROMPT_VISION = (
    "Describe what's in this in one sentence under 100 characters. "
    "Be specific and concrete. No preamble, just the description."
)
PROMPT_TEXT = (
    "Summarize this file in two sentences under 200 characters total. "
    "Surface-level only: what is it, what's the gist."
)

_REFUSAL_RE = re.compile(
    r"(cannot access|cannot describe|cannot view|unable to (access|view|read)|"
    r"outside (the |my )?(allowed )?workspace|outside the allowed|"
    r"i (don't|do not) have (permission|access)|file path is outside)",
    re.IGNORECASE,
)
_RATE_LIMIT_RE = re.compile(
    r"(rate ?limit|quota|429|503|resource[_ ]exhausted|too many requests|"
    r"retry after|try again later|requests per minute|tokens per minute|"
    r"\bRPM\b|\bTPM\b|temporarily unavailable|service unavailable|"
    r"overloaded|capacity|exceeded your (current )?limit|"
    r"user rate limit|rate exceeded)",
    re.IGNORECASE,
)
_INELIGIBLE_RE = re.compile(
    r"(IneligibleTierError|ValidationRequiredError|"
    r"not eligible for Gemini Code Assist|Account validation required)",
    re.IGNORECASE,
)

_COOLDOWN_LOCK = threading.Lock()
_COOLDOWN_RELEASE_AT = [0.0]


def _request_cooldown(seconds):
    with _COOLDOWN_LOCK:
        target = time.monotonic() + seconds
        if target > _COOLDOWN_RELEASE_AT[0]:
            _COOLDOWN_RELEASE_AT[0] = target


def _wait_cooldown():
    while True:
        with _COOLDOWN_LOCK:
            wait = _COOLDOWN_RELEASE_AT[0] - time.monotonic()
        if wait <= 0:
            return
        time.sleep(min(wait, 5.0))


# ---------------------------------------------------------------------------
# Per-worker account isolation: each gemini call pinned to its own HOME
# pointing at one of N account creds. Workers fan out across all accounts
# in round-robin, so 64 workers + 8 accounts = 8 workers per account in
# parallel. No global oauth_creds.json contention; no thundering herd.
# ---------------------------------------------------------------------------
import shutil

ACCOUNTS_DIR = Path.home() / ".gemini" / "accounts"
POOL_ROOT = Path("/tmp/gemini-account-pool")  # per-account HOME dirs
ACCOUNTS: list[tuple[str, Path]] = []         # (name, home_path)

_account_lock = threading.Lock()
_acct_idx = [0]                  # round-robin counter
_exhausted: set[str] = set()     # account names exhausted in this run


def init_account_state():
    """Set up an isolated HOME dir per account in the pool dir.
    Each subprocess.run(gemini...) picks one and runs with HOME=<that dir>.
    Each per-account HOME needs both oauth_creds.json AND settings.json
    (selectedType=oauth-personal); without settings.json, gemini fails
    with 'Please set an Auth method'."""
    POOL_ROOT.mkdir(parents=True, exist_ok=True)
    if not ACCOUNTS_DIR.exists():
        sys.exit(f"no ~/.gemini/accounts/ dir; auth at least one account first")
    global_settings = Path.home() / ".gemini" / "settings.json"
    if not global_settings.exists():
        sys.exit("ERROR: ~/.gemini/settings.json missing — bootstrap initial gemini auth first")
    for acct_file in sorted(ACCOUNTS_DIR.glob("*.json")):
        name = acct_file.stem
        home = POOL_ROOT / name
        gemini_dir = home / ".gemini"
        gemini_dir.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(acct_file, gemini_dir / "oauth_creds.json")
            shutil.copy2(global_settings, gemini_dir / "settings.json")
            ACCOUNTS.append((name, home))
        except OSError as e:
            sys.stderr.write(f"  WARNING: skipping {name} — {e}\n")
    if not ACCOUNTS:
        sys.exit("no accounts loaded into pool")
    print(f"  pool: {len(ACCOUNTS)} account(s) — {[a[0] for a in ACCOUNTS]}")
    print(f"  workers will round-robin across all accounts in parallel")


def get_next_account():
    """Round-robin pick; skip exhausted. Returns (name, home_path) or None."""
    with _account_lock:
        live = [a for a in ACCOUNTS if a[0] not in _exhausted]
        if not live:
            return None
        idx = _acct_idx[0] % len(live)
        _acct_idx[0] += 1
        return live[idx]


def mark_exhausted(name):
    with _account_lock:
        if name in _exhausted:
            return
        _exhausted.add(name)
        live = len(ACCOUNTS) - len(_exhausted)
        sys.stdout.write(f"\n  >>> {name} exhausted ({len(_exhausted)}/{len(ACCOUNTS)} down, {live} live)\n")
        sys.stdout.flush()


def hash_file(path):
    """Compute sha256 of a file. Returns hex or None."""
    if not path.exists() or path.is_dir():
        return None
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(64 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def kind_of(mime):
    if not mime:
        return "file"
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("video/"):
        return "video"
    if mime.startswith("audio/"):
        return "audio"
    if mime.startswith("text/") or mime in ("application/pdf", "application/json"):
        return "text"
    return "file"


def gemini_describe_once(path, kind, account, timeout=180):
    """Single Gemini CLI call with HOME pinned to a specific account dir.
    `account` is (name, home_path); we set env HOME=<home_path> so the CLI
    reads that account's oauth_creds.json instead of the global one."""
    if kind not in ("image", "video", "text"):
        return None, None, "unsupported"
    if not Path(path).exists() or Path(path).is_dir():
        return None, None, "missing"
    prompt = PROMPT_VISION if kind in ("image", "video") else PROMPT_TEXT
    cmd = [
        "gemini",
        "-m", DESCRIPTION_MODEL,
        "-p", f"{prompt}\n\n@{path}",
        "-o", "text",
        "--approval-mode", "plan",
        "--include-directories", ATTACHMENTS_INCLUDE,
    ]
    env = os.environ.copy()
    env["HOME"] = str(account[1])  # account home dir
    env["GEMINI_CLI_TRUST_WORKSPACE"] = "true"  # bypass trust prompt in per-account HOME
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return None, None, "timeout"
    except FileNotFoundError:
        return None, None, "no_cli"

    # Order matters: returncode==0 is the source of truth for success.
    # gemini-cli emits "exhausted your capacity... retrying" to stderr on
    # transient rate limits then auto-retries and succeeds — we must NOT
    # flag those as rate_limit. Only inspect stderr regex on actual failure.
    stderr = proc.stderr or ""
    if _INELIGIBLE_RE.search(stderr):
        return None, None, "ineligible"
    if proc.returncode != 0:
        if _RATE_LIMIT_RE.search(stderr):
            return None, None, "rate_limit"
        return None, None, "failure"
    desc = (proc.stdout or "").strip()
    lines = [ln.strip() for ln in desc.splitlines() if ln.strip()]
    if not lines:
        return None, None, "empty"
    desc = lines[-1]
    if _REFUSAL_RE.search(desc):
        return None, None, "refusal"
    cap = 100 if kind in ("image", "video") else 200
    if len(desc) > cap:
        desc = desc[: cap - 1].rstrip() + "…"
    return desc, DESCRIPTION_MODEL, None


def gemini_describe_with_retry(path, kind, max_retries=5):
    """Pull a fresh account from the round-robin pool each attempt.
    On rate_limit: mark that account exhausted, try another. Only after
    ALL accounts exhausted do we cooldown-and-wait."""
    delay = 5.0
    for attempt in range(max_retries + 1):
        _wait_cooldown()
        account = get_next_account()
        if account is None:
            # All accounts exhausted; cooldown and try once more
            sleep_for = delay + random.uniform(0, delay)
            _request_cooldown(sleep_for)
            time.sleep(sleep_for)
            delay = min(delay * 2, 120)
            if attempt >= max_retries:
                return None, None, "all_exhausted"
            # After waiting, clear exhausted set partially to give accounts
            # a chance to refill (we can't know server-side; just retry)
            with _account_lock:
                _exhausted.clear()
            continue
        desc, model, err = gemini_describe_once(path, kind, account)
        if err in ("rate_limit", "ineligible"):
            mark_exhausted(account[0])
            continue  # try another account immediately
        return desc, model, err
    return None, None, "rate_limit"


# ---------------------------------------------------------------------------
# Phase 1: scan markdown files, build needed sha set + path map
# ---------------------------------------------------------------------------
def scan_workspace(ws_root):
    """Returns {sha256: {kind, files: [(path, attachment_index)]}}."""
    needed = {}
    md_paths = glob.glob(str(ws_root / "raw" / "imessage" / "**" / "*.md"), recursive=True)
    for path in md_paths:
        if "/_profiles/" in path:
            continue
        try:
            text = Path(path).read_text()
        except OSError:
            continue
        m = re.match(r"^---\n(.+?)\n---\n", text, re.DOTALL)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception:
            continue
        for i, a in enumerate(fm.get("attachments") or []):
            if a.get("description"):
                continue
            if not a.get("source_available"):
                continue
            sha = a.get("sha256")
            if not sha:
                continue
            kind = kind_of(a.get("mime"))
            if kind not in ("image", "video", "text"):
                continue
            entry = needed.setdefault(sha, {"kind": kind, "files": []})
            entry["files"].append((path, i))
    return needed


# ---------------------------------------------------------------------------
# Phase 2: build sha → src_path map by hashing all chat.db attachments
# ---------------------------------------------------------------------------
def build_path_map(needed_sha_set, workers):
    """For each attachment in chat.db, hash it; if sha256 in needed_sha_set,
    record the path. Parallelizes the hashing."""
    import sqlite3
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = conn.execute("""
        SELECT filename, mime_type FROM attachment
        WHERE filename IS NOT NULL
    """).fetchall()
    conn.close()
    print(f"  chat.db has {len(rows)} attachment rows; hashing in parallel...")

    sha_to_path = {}
    sha_to_mime = {}
    map_lock = threading.Lock()
    progress = [0]
    total = len(rows)

    def hash_task(fn_mime):
        fn, mime = fn_mime
        path = Path(os.path.expanduser(fn)) if fn else None
        if path is None:
            return None, None, None, None
        sha = hash_file(path)
        with map_lock:
            progress[0] += 1
            if progress[0] % 500 == 0:
                sys.stdout.write(f"\r    ...{progress[0]}/{total} hashed")
                sys.stdout.flush()
        if sha and sha in needed_sha_set:
            return sha, str(path), mime, kind_of(mime)
        return None, None, None, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(hash_task, r) for r in rows]
        for fut in concurrent.futures.as_completed(futures):
            try:
                sha, path, mime, kind = fut.result()
            except Exception:
                continue
            if sha and path and sha not in sha_to_path:
                sha_to_path[sha] = (path, mime, kind)

    sys.stdout.write(f"\r    ...{total}/{total} hashed     \n")
    return sha_to_path


# ---------------------------------------------------------------------------
# Phase 3: parallel Gemini describe (with periodic checkpoint)
# ---------------------------------------------------------------------------
def parallel_describe(worklist, workers, needed, dry_run, checkpoint_every=100, on_progress=None):
    """Run parallel Gemini describe. Periodically checkpoints completed
    descriptions to disk by patching frontmatters in batches, so that
    a quota exhaustion / kill mid-run preserves all progress so far."""
    results = {}
    if not worklist:
        return results
    done = [0]
    total = len(worklist)
    startup_jitter_done = set()
    jitter_lock = threading.Lock()

    # Checkpoint buffer
    pending_buffer = {}
    pending_lock = threading.Lock()
    checkpoints = [0]

    # Track running counts across all completions
    counts = {"success": 0, "rate_limit": 0, "other": 0}
    counts_lock = threading.Lock()

    def maybe_checkpoint(force=False):
        with pending_lock:
            if not pending_buffer:
                if force:
                    pass
                else:
                    return
            if not force and len(pending_buffer) < checkpoint_every:
                return
            snapshot = dict(pending_buffer)
            pending_buffer.clear()
        if snapshot:
            patched = patch_files(needed, snapshot, dry_run)
        else:
            patched = 0
        checkpoints[0] += 1
        with counts_lock:
            c = dict(counts)
        sys.stdout.write(f"\n  checkpoint #{checkpoints[0]}: {len(snapshot)} descs persisted ({patched} files); "
                         f"running: {c['success']} ok, {c['rate_limit']} rate, {c['other']} other\n")
        sys.stdout.flush()

    def task(item):
        tid = threading.get_ident()
        with jitter_lock:
            if tid not in startup_jitter_done:
                startup_jitter_done.add(tid)
                time.sleep(random.uniform(0, 2.0))
        sha, path, kind = item
        desc, model, err = gemini_describe_with_retry(Path(path), kind)
        if desc:
            return sha, {
                "description": desc,
                "model": model,
                "extracted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "error": None,
            }
        return sha, {
            "description": None, "model": None, "extracted_at": None, "error": err,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(task, item) for item in worklist]
        for fut in concurrent.futures.as_completed(futures):
            try:
                sha, payload = fut.result()
            except Exception as e:
                done[0] += 1
                sys.stderr.write(f"\n  worker exception: {e}\n")
                continue
            results[sha] = payload
            with counts_lock:
                if payload["description"]:
                    counts["success"] += 1
                elif payload.get("error") == "rate_limit":
                    counts["rate_limit"] += 1
                else:
                    counts["other"] += 1
            if payload["description"]:
                with pending_lock:
                    pending_buffer[sha] = payload
            done[0] += 1
            if on_progress and (done[0] % 25 == 0 or done[0] == total):
                on_progress(done[0], total)
            # Checkpoint when buffer reaches threshold
            with pending_lock:
                buffer_size = len(pending_buffer)
            if buffer_size >= checkpoint_every:
                maybe_checkpoint()

    # Final flush
    maybe_checkpoint(force=True)
    return results


# ---------------------------------------------------------------------------
# Phase 4: patch frontmatter
# ---------------------------------------------------------------------------
def patch_files(needed, descriptions, dry_run):
    """For each described sha, patch every file containing it."""
    files_to_update = {}  # path -> list of (sha, idx, payload)
    for sha, info in needed.items():
        if sha not in descriptions:
            continue
        payload = descriptions[sha]
        for path, idx in info["files"]:
            files_to_update.setdefault(path, []).append((sha, idx, payload))

    print(f"  patching {len(files_to_update)} files...")
    patched = 0
    for path, updates in files_to_update.items():
        try:
            text = Path(path).read_text()
        except OSError:
            continue
        m = re.match(r"^---\n(.+?)\n---\n(.*)", text, re.DOTALL)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception:
            continue
        body = m.group(2)
        atts = fm.get("attachments") or []
        changed = False
        for sha, idx, payload in updates:
            if idx >= len(atts):
                continue
            if atts[idx].get("sha256") != sha:
                continue
            if payload["description"]:
                atts[idx]["description"] = payload["description"]
                atts[idx]["description_model"] = payload["model"]
                atts[idx]["extracted_at"] = payload["extracted_at"]
                changed = True
        if changed:
            fm["attachments"] = atts
            new_text = "---\n" + yaml.safe_dump(fm, sort_keys=False, default_flow_style=False) + "---\n" + body
            if not dry_run:
                Path(path).write_text(new_text)
            patched += 1
    return patched


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ws_root = ULTRON_ROOT / "workspaces" / args.workspace
    if not (ws_root / "raw" / "imessage").exists():
        sys.exit(f"no raw/imessage tree at {ws_root}")

    print(f"workspace: {args.workspace}")
    print(f"workers:   {args.workers}")
    print(f"dry-run:   {args.dry_run}")
    init_account_state()

    print(f"\nphase 1: scanning month files for missing descriptions...")
    needed = scan_workspace(ws_root)
    print(f"  {len(needed)} unique sha256 need description across "
          f"{sum(len(v['files']) for v in needed.values())} file references")

    if not needed:
        print("nothing to do")
        return

    print(f"\nphase 2: building sha256 → src_path map (hashing chat.db attachments)...")
    needed_sha = set(needed.keys())
    sha_to_path = build_path_map(needed_sha, args.workers)
    matched = sum(1 for s in needed_sha if s in sha_to_path)
    unmatched = len(needed_sha) - matched
    print(f"  matched: {matched}  unmatched: {unmatched}")

    worklist = []
    for sha, info in needed.items():
        if sha not in sha_to_path:
            continue
        path, mime, kind = sha_to_path[sha]
        # Override scan kind with chat.db mime (more accurate)
        worklist.append((sha, path, kind))
    print(f"\nphase 3: describing {len(worklist)} attachments ({args.workers}x parallel)...")

    def progress(done, total):
        sys.stdout.write(f"\r    ...{done}/{total} described")
        sys.stdout.flush()
        if done == total:
            sys.stdout.write("\n")

    started = time.monotonic()
    descriptions = parallel_describe(
        worklist, args.workers, needed, args.dry_run,
        checkpoint_every=100, on_progress=progress,
    )
    elapsed = time.monotonic() - started
    succeeded = sum(1 for d in descriptions.values() if d["description"])
    failed = len(descriptions) - succeeded
    print(f"\n  succeeded: {succeeded}  failed: {failed}  elapsed: {elapsed:.0f}s")

    print(f"\ndone. Re-run ingest-imessage-oneshot.py to update body lines.")


if __name__ == "__main__":
    main()
