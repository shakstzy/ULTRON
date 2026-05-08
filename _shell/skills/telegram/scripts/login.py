"""Two-shot Telethon login.

Phase 1: `login --send-code`
  Connects, calls send_code_request(phone), persists phone_code_hash to a file,
  exits cleanly. Telegram pushes a 5-digit code to the existing Telegram app
  (or SMS if no other session exists).

Phase 2: `login --code 12345 [--password 'pwd']`
  Reads phone_code_hash, signs in. On 2FA challenge, expects --password.

Phase C: `login` (no flags)
  TTY-interactive fallback for hands-on debugging.
"""
from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import os
import sys
from datetime import datetime, timezone

from session import (
    CRED_DIR,
    SESSION_FILE,
    load_credentials,
    open_client,
    write_credentials,
)

CODE_HASH_FILE = CRED_DIR / ".telegram-login-hash.json"


def _save_hash(phone: str, phone_code_hash: str) -> None:
    CRED_DIR.mkdir(parents=True, exist_ok=True)
    CODE_HASH_FILE.write_text(json.dumps({
        "phone": phone,
        "phone_code_hash": phone_code_hash,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }))
    os.chmod(CODE_HASH_FILE, 0o600)


def _load_hash() -> dict | None:
    if not CODE_HASH_FILE.exists():
        return None
    return json.loads(CODE_HASH_FILE.read_text())


def _clear_hash() -> None:
    if CODE_HASH_FILE.exists():
        CODE_HASH_FILE.unlink()


async def _send_code() -> int:
    creds = load_credentials()
    if not creds.phone:
        sys.exit("phone not in telegram.json")
    if not creds.phone.startswith("+"):
        sys.exit("phone must be E.164")

    async with open_client(allow_unauthenticated=True) as client:
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"already logged in as {me.first_name} (@{me.username}) id={me.id}")
            return 0
        sent = await client.send_code_request(creds.phone)
        _save_hash(creds.phone, sent.phone_code_hash)
        print(f"code sent to {creds.phone}; relay via: login --code <DIGITS>")
    return 0


async def _sign_in(code: str, password: str | None) -> int:
    saved = _load_hash()
    if not saved:
        sys.exit("no pending code hash — run `login --send-code` first")
    phone = saved["phone"]
    phone_code_hash = saved["phone_code_hash"]

    async with open_client(allow_unauthenticated=True) as client:
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"already logged in as {me.first_name} (@{me.username}) id={me.id}")
            _clear_hash()
            return 0
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        except Exception as e:
            if "SessionPasswordNeededError" in type(e).__name__:
                if not password:
                    sys.exit("2FA password required: re-run with --password '<pwd>'")
                await client.sign_in(password=password)
            else:
                raise
        me = await client.get_me()
        print(f"logged in as {me.first_name} (@{me.username}) id={me.id}")

    _clear_hash()
    if SESSION_FILE.exists():
        os.chmod(SESSION_FILE, 0o600)
    return 0


async def _interactive() -> int:
    """TTY fallback. Single process; keeps connection open across input prompt."""
    creds = load_credentials()
    phone = creds.phone or input("phone (E.164): ").strip()
    if not phone.startswith("+"):
        sys.exit("phone must be E.164")
    if creds.phone != phone:
        write_credentials(creds.api_id, creds.api_hash, phone)

    async with open_client(allow_unauthenticated=True) as client:
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"already logged in as {me.first_name} (@{me.username}) id={me.id}")
            return 0
        sent = await client.send_code_request(phone)
        code = input("code from Telegram: ").strip()
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=sent.phone_code_hash)
        except Exception as e:
            if "SessionPasswordNeededError" in type(e).__name__:
                pwd = getpass.getpass("2FA cloud password: ")
                await client.sign_in(password=pwd)
            else:
                raise
        me = await client.get_me()
        print(f"logged in as {me.first_name} (@{me.username}) id={me.id}")
    if SESSION_FILE.exists():
        os.chmod(SESSION_FILE, 0o600)
    return 0


async def run_login(args: argparse.Namespace | None = None) -> int:
    if args is None:
        return await _interactive()
    if getattr(args, "send_code", False):
        return await _send_code()
    if getattr(args, "code", None):
        return await _sign_in(args.code, getattr(args, "password", None))
    return await _interactive()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--send-code", action="store_true")
    p.add_argument("--code")
    p.add_argument("--password")
    args = p.parse_args()
    return asyncio.run(run_login(args))


if __name__ == "__main__":
    sys.exit(main())
