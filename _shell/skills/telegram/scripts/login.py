"""Two-phase Telethon login (works across turns when Adithya relays the code).

Phase 1: `python3 run.py login --send-code`
  Connects, calls send_code_request(phone), persists phone_code_hash to a
  temp file under ~/ULTRON/_credentials/, exits cleanly. Telegram pushes a
  5-digit code to the existing Telegram app (or SMS if no other session).

Phase 2: `python3 run.py login --code 12345 [--password ...]`
  Reads phone_code_hash, calls sign_in(). On 2FA challenge, expects --password.
  Cleans up the hash file.

Single-shot interactive `python3 run.py login` (no flags) still works for
hands-on debugging.
"""
from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from session import (
    CRED_DIR,
    SESSION_FILE,
    load_credentials,
    open_client,
    write_credentials,
)

CODE_HASH_FILE = CRED_DIR / ".telegram-login-hash.json"


def _save_hash(phone: str, phone_code_hash: str) -> None:
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


async def _send_code(phone_override: str | None) -> int:
    creds = load_credentials()
    phone = phone_override or creds.phone
    if not phone:
        sys.exit("phone not in telegram.json and not provided via --phone")
    if not phone.startswith("+"):
        sys.exit("phone must be E.164, starting with +")

    if creds.phone != phone:
        write_credentials(creds.api_id, creds.api_hash, phone)

    async with open_client(allow_unauthenticated=True) as client:
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"already logged in as {me.first_name} (@{me.username}) id={me.id}")
            return 0
        sent = await client.send_code_request(phone)
        _save_hash(phone, sent.phone_code_hash)
        print(f"code sent to {phone}; relay it via: login --code <DIGITS>")
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
                    sys.exit("2FA cloud password required: re-run with --password '<pwd>'")
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
    """Hands-on fallback when stdin is a TTY."""
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
    if args is None or (not args.send_code and not args.code):
        return await _interactive()
    if args.send_code:
        return await _send_code(args.phone)
    return await _sign_in(args.code, args.password)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--send-code", action="store_true")
    p.add_argument("--code", help="5-digit code from Telegram")
    p.add_argument("--phone", help="override phone in telegram.json")
    p.add_argument("--password", help="2FA cloud password if set")
    args = p.parse_args()
    return asyncio.run(run_login(args))


if __name__ == "__main__":
    sys.exit(main())
