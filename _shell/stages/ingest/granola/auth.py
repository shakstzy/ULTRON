"""Granola auth: read tokens that the desktop app maintains.

Desktop app is the SOLE refresh authority. We never call WorkOS ourselves
— two refreshers fighting over a single rotating refresh-token guarantees
one gets `Session has already ended.` on every run. Instead we just read
whatever the desktop app wrote and trust it.

Token sources (newest desktop schema first):
  1. `stored-accounts.json` — current desktop app (≥ ~Apr 2026). Account
     array; each entry has stringified `tokens` blob.
  2. `supabase.json` — legacy schema. Single `workos_tokens` blob.

`get_access_token()` picks whichever file exposes the freshest
non-expired access_token, with `stored-accounts.json` winning ties.
"""
from __future__ import annotations

import base64
import json
import time
from pathlib import Path

GRANOLA_DIR = Path.home() / "Library" / "Application Support" / "Granola"
SUPABASE_PATH = GRANOLA_DIR / "supabase.json"
STORED_ACCOUNTS_PATH = GRANOLA_DIR / "stored-accounts.json"


def _load_supabase(path: Path) -> tuple[dict, dict] | None:
    """Returns (tokens_dict, user_info_dict) or None if file missing/malformed."""
    try:
        raw = json.loads(path.read_text())
        toks = json.loads(raw["workos_tokens"])
        info = json.loads(raw.get("user_info") or "{}")
        if not toks.get("access_token"):
            return None
        return toks, info
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None


def _load_stored_accounts(path: Path) -> tuple[dict, dict] | None:
    """Same shape as _load_supabase, parsed from stored-accounts.json."""
    try:
        raw = json.loads(path.read_text())
        accts = json.loads(raw["accounts"])
        if not accts:
            return None
        a = accts[0]
        toks = json.loads(a["tokens"])
        info = json.loads(a.get("userInfo") or "{}")
        if not toks.get("access_token"):
            return None
        return toks, info
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None


def _token_exp(at: str) -> int:
    parts = at.split(".")
    if len(parts) != 3:
        return 0
    pad = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
    try:
        return int(json.loads(base64.urlsafe_b64decode(pad)).get("exp", 0))
    except Exception:
        return 0


def _pick_freshest() -> tuple[dict, dict]:
    """Pick the freshest token blob from either file. Raises if none usable."""
    candidates = []
    for label, loader, p in [
        ("stored", _load_stored_accounts, STORED_ACCOUNTS_PATH),
        ("supabase", _load_supabase, SUPABASE_PATH),
    ]:
        result = loader(p)
        if result:
            toks, info = result
            candidates.append((_token_exp(toks["access_token"]), label, toks, info))
    if not candidates:
        raise RuntimeError(
            f"no Granola tokens found in {STORED_ACCOUNTS_PATH} or {SUPABASE_PATH}; "
            "open the Granola desktop app and sign in"
        )
    candidates.sort(key=lambda c: c[0], reverse=True)
    exp, _label, toks, info = candidates[0]
    if exp <= time.time():
        raise RuntimeError(
            f"all Granola access_tokens are expired (latest exp={exp}); "
            "open the Granola desktop app to refresh, or sign in if needed"
        )
    return toks, info


def read_supabase_raw(path: Path = SUPABASE_PATH) -> dict:
    """Legacy entrypoint kept for callers that import it directly."""
    with open(path) as f:
        return json.load(f)


def parse_tokens(raw: dict) -> dict:
    return json.loads(raw["workos_tokens"])


def parse_user_info(raw: dict) -> dict:
    return json.loads(raw["user_info"])


def get_access_token(path: Path = SUPABASE_PATH) -> str:
    toks, _ = _pick_freshest()
    return toks["access_token"]


def get_account_email(path: Path = SUPABASE_PATH) -> str:
    _, info = _pick_freshest()
    return info.get("email", "")


def refresh_token(stale_access_token: str, path: Path = SUPABASE_PATH) -> str:
    """401-retry hook called by api.py.

    Desktop app handles all refresh; we just re-read the disk. If neither
    file's access_token differs from the stale one we 401'd on, surface a
    clear error so the cron's failure is actionable instead of cryptic.
    """
    toks, _ = _pick_freshest()
    fresh = toks["access_token"]
    if fresh == stale_access_token:
        raise RuntimeError(
            "Granola desktop app has not refreshed the access_token since "
            "our 401. Open the app (or sign in if it's stuck on the auth "
            "screen) — it is the sole refresh authority."
        )
    return fresh


