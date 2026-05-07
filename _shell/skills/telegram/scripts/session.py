"""TelegramSession: Telethon client wrapper + circuit breaker.

Session and credential paths are deliberately fixed: ~/ULTRON/_credentials/.
Both files are chmod 600 and gitignored.
"""
from __future__ import annotations

import json
import os
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

CRED_DIR = Path.home() / "ULTRON" / "_credentials"
CRED_FILE = CRED_DIR / "telegram.json"
SESSION_FILE = CRED_DIR / "telegram.session"
BREAKER_FILE = CRED_DIR / ".telegram-breaker.json"
BREAKER_COOLDOWN_SECONDS = 24 * 3600


@dataclass
class Credentials:
    api_id: int
    api_hash: str
    phone: str | None = None


def load_credentials() -> Credentials:
    if not CRED_FILE.exists():
        sys.exit(
            f"missing {CRED_FILE}\n"
            "create it with: {\"api_id\": <int>, \"api_hash\": \"<32-hex>\", \"phone\": \"+1...\"}"
        )
    raw = json.loads(CRED_FILE.read_text())
    if not isinstance(raw.get("api_id"), int) or not isinstance(raw.get("api_hash"), str):
        sys.exit(f"{CRED_FILE} must have integer api_id and string api_hash")
    return Credentials(api_id=raw["api_id"], api_hash=raw["api_hash"], phone=raw.get("phone"))


def write_credentials(api_id: int, api_hash: str, phone: str | None = None) -> None:
    CRED_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"api_id": api_id, "api_hash": api_hash}
    if phone:
        payload["phone"] = phone
    CRED_FILE.write_text(json.dumps(payload, indent=2))
    os.chmod(CRED_FILE, 0o600)


def breaker_state() -> dict:
    if not BREAKER_FILE.exists():
        return {"halted": False}
    try:
        s = json.loads(BREAKER_FILE.read_text())
    except json.JSONDecodeError:
        return {"halted": False}
    halted_at = s.get("halted_at")
    if not halted_at:
        return {"halted": False}
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(halted_at)).total_seconds()
    if age >= BREAKER_COOLDOWN_SECONDS:
        return {"halted": False, "expired": True, "halted_at": halted_at, "reason": s.get("reason")}
    return {"halted": True, "halted_at": halted_at, "reason": s.get("reason"), "age_seconds": int(age)}


def trip_breaker(reason: str) -> None:
    BREAKER_FILE.write_text(json.dumps({
        "halted_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    }, indent=2))


def clear_breaker() -> None:
    if BREAKER_FILE.exists():
        BREAKER_FILE.unlink()


@asynccontextmanager
async def open_client(*, allow_unauthenticated: bool = False):
    """Connect, yield client, disconnect. Trips breaker on auth/flood failure.

    allow_unauthenticated=True is for `login` only — every other verb requires
    an existing session.
    """
    state = breaker_state()
    if state.get("halted"):
        sys.exit(f"BREAKER_HALTED: {state.get('reason')} (halted {state.get('age_seconds')}s ago, cooldown 24h)")

    from telethon import TelegramClient
    from telethon.errors import AuthKeyError, FloodWaitError, SessionPasswordNeededError

    creds = load_credentials()
    CRED_DIR.mkdir(parents=True, exist_ok=True)
    client = TelegramClient(str(SESSION_FILE.with_suffix("")), creds.api_id, creds.api_hash)
    await client.connect()
    try:
        if not allow_unauthenticated and not await client.is_user_authorized():
            sys.exit("not logged in — run: python3 scripts/run.py login")
        yield client
    except AuthKeyError as e:
        trip_breaker(f"AuthKeyError: {e}")
        sys.exit(f"BREAKER tripped: AuthKeyError — re-run `login`")
    except FloodWaitError as e:
        if e.seconds > 600:
            trip_breaker(f"FloodWaitError {e.seconds}s")
            sys.exit(f"BREAKER tripped: flood wait {e.seconds}s")
        raise
    except SessionPasswordNeededError:
        sys.exit("2FA cloud password required — run `login` interactively")
    finally:
        if client.is_connected():
            await client.disconnect()


def session_exists() -> bool:
    return SESSION_FILE.exists() and SESSION_FILE.stat().st_size > 0
