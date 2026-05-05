"""Granola auth: token read + 401-driven WorkOS refresh. Lock 7 of format.md.

Single source of truth: `~/Library/Application Support/Granola/supabase.json`.
Refresh runs under flock at `/tmp/com.adithya.ultron.granola-token-refresh.lock`
to avoid racing the desktop app's own refresh-token rotation.
"""
from __future__ import annotations

import base64
import contextlib
import fcntl
import json
import os
import tempfile
import time
import urllib.request
from pathlib import Path

SUPABASE_PATH = Path.home() / "Library" / "Application Support" / "Granola" / "supabase.json"
LOCK_PATH = "/tmp/com.adithya.ultron.granola-token-refresh.lock"
WORKOS_REFRESH_URL = "https://api.workos.com/user_management/authenticate"


def read_supabase_raw(path: Path = SUPABASE_PATH) -> dict:
    """Parse the supabase.json file. Returns the outer dict; the
    `workos_tokens` and `user_info` fields are themselves JSON strings."""
    with open(path) as f:
        return json.load(f)


def parse_tokens(raw: dict) -> dict:
    return json.loads(raw["workos_tokens"])


def parse_user_info(raw: dict) -> dict:
    return json.loads(raw["user_info"])


def get_access_token(path: Path = SUPABASE_PATH) -> str:
    return parse_tokens(read_supabase_raw(path))["access_token"]


def get_account_email(path: Path = SUPABASE_PATH) -> str:
    return parse_user_info(read_supabase_raw(path)).get("email", "")


def _jwt_payload(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        return {}
    pad = lambda s: s + "=" * ((4 - len(s) % 4) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(pad(parts[1])).decode())
    except Exception:
        return {}


@contextlib.contextmanager
def _file_lock(path: str):
    """Exclusive-blocking flock. Released on context exit."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def refresh_via_workos(refresh_token: str, client_id: str, timeout: int = 20) -> dict:
    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    req = urllib.request.Request(
        WORKOS_REFRESH_URL,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _atomic_write_json(path: Path, payload: dict) -> None:
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".",
                                suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def refresh_token(stale_access_token: str,
                  path: Path = SUPABASE_PATH) -> str:
    """Lock-protected refresh.

    1. Acquire flock.
    2. Re-read supabase.json. If file's access_token differs from the
       stale one we 401'd on, the desktop app already rotated. Use it,
       skip the refresh.
    3. Otherwise call WorkOS, atomic-write back, return new token.

    Raises on non-recoverable errors. Caller catches and fails loudly.
    """
    with _file_lock(LOCK_PATH):
        raw = read_supabase_raw(path)
        toks = parse_tokens(raw)
        if toks["access_token"] != stale_access_token:
            return toks["access_token"]

        client_id = _jwt_payload(stale_access_token).get("client_id")
        if not client_id:
            raise RuntimeError("could not extract client_id from stale JWT")
        resp = refresh_via_workos(toks["refresh_token"], client_id)

        new_toks = dict(toks)
        new_toks["access_token"] = resp["access_token"]
        new_toks["refresh_token"] = resp.get("refresh_token", toks["refresh_token"])
        new_toks["obtained_at"] = int(time.time() * 1000)
        if "expires_in" in resp:
            new_toks["expires_in"] = resp["expires_in"]
        else:
            payload = _jwt_payload(new_toks["access_token"])
            if "exp" in payload:
                new_toks["expires_in"] = max(0, int(payload["exp"] - time.time()))

        new_raw = dict(raw)
        new_raw["workos_tokens"] = json.dumps(new_toks)
        _atomic_write_json(path, new_raw)
        return new_toks["access_token"]
