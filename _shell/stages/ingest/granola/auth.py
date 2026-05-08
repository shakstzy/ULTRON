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


def _load_stored_accounts(path: Path, email: str | None = None) -> tuple[dict, dict] | None:
    """Same shape as _load_supabase, parsed from stored-accounts.json.

    If `email` is given, return that account's tokens; raise if missing.
    Otherwise return accounts[0] for back-compat with single-account use.
    """
    try:
        raw = json.loads(path.read_text())
        accts = json.loads(raw["accounts"])
        if not accts:
            return None
        if email:
            a = next((x for x in accts if x.get("email", "").lower() == email.lower()), None)
            if a is None:
                raise RuntimeError(
                    f"requested account {email!r} not in {path.name}; "
                    f"available: {[x.get('email') for x in accts]}"
                )
        else:
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


def _pick_freshest(email: str | None = None) -> tuple[dict, dict]:
    """Pick the freshest token blob from either file. Raises if none usable.

    If `email` is given, both files are filtered to that account; supabase.json
    is single-account so it only contributes when `parse_user_info` matches.
    """
    candidates = []
    stored = _load_stored_accounts(STORED_ACCOUNTS_PATH, email=email)
    if stored:
        toks, info = stored
        candidates.append((_token_exp(toks["access_token"]), "stored", toks, info))
    supa = _load_supabase(SUPABASE_PATH)
    if supa:
        toks, info = supa
        if not email or info.get("email", "").lower() == email.lower():
            candidates.append((_token_exp(toks["access_token"]), "supabase", toks, info))
    if not candidates:
        raise RuntimeError(
            f"no Granola tokens found in {STORED_ACCOUNTS_PATH} or {SUPABASE_PATH}"
            f"{' for ' + email if email else ''}; open the Granola desktop app and sign in"
        )
    candidates.sort(key=lambda c: c[0], reverse=True)
    exp, _label, toks, info = candidates[0]
    if exp <= time.time():
        raise RuntimeError(
            f"all Granola access_tokens are expired (latest exp={exp}); "
            "open the Granola desktop app to refresh, or sign in if needed"
        )
    return toks, info


def get_access_token(path: Path = SUPABASE_PATH, email: str | None = None) -> str:
    toks, _ = _pick_freshest(email=email)
    return toks["access_token"]


def get_account_email(path: Path = SUPABASE_PATH) -> str:
    _, info = _pick_freshest()
    return info.get("email", "")


def refresh_token(stale_access_token: str, path: Path = SUPABASE_PATH,
                  email: str | None = None, max_wait_s: int = 30) -> str:
    """401-retry hook called by api.py.

    Desktop app handles all refresh; we re-read disk and poll briefly for the
    desktop to write a new token. If still unchanged after `max_wait_s`,
    surface a clear error so the cron failure is actionable.
    """
    deadline = time.time() + max_wait_s
    while True:
        toks, _ = _pick_freshest(email=email)
        fresh = toks["access_token"]
        if fresh != stale_access_token:
            return fresh
        if time.time() >= deadline:
            raise RuntimeError(
                "Granola desktop app has not refreshed the access_token within "
                f"{max_wait_s}s of our 401. Open the app (or sign in if it's "
                "stuck on the auth screen) — it is the sole refresh authority."
            )
        time.sleep(2)


