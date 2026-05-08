"""Telethon login. Single-process flow with file-based code relay.

Phase A (verb: `login --start`): connect, send_code_request, then poll
  CRED_DIR/.telegram-code-pending until Adithya writes the code there. Same
  TelegramClient stays connected the whole time, so we never fight Telegram's
  cross-process TTL.

Phase B (verb: `login --submit-code 12345`): atomically writes the code into
  the pending file. The background Phase-A process picks it up within a second
  and finishes sign-in.

Phase C (verb: `login`): TTY-interactive fallback for hands-on debugging.
"""
from __future__ import annotations

import argparse
import asyncio
import getpass
import os
import sys
from pathlib import Path

from session import (
    CRED_DIR,
    SESSION_FILE,
    load_credentials,
    open_client,
    write_credentials,
)

PENDING_CODE = CRED_DIR / ".telegram-code-pending"
LOGIN_LOG = CRED_DIR / ".telegram-login.log"
LOGIN_DONE = CRED_DIR / ".telegram-login-done"
POLL_TIMEOUT_SECONDS = 3600  # 1 hour for Adithya to relay


def _log(msg: str) -> None:
    LOGIN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOGIN_LOG.open("a") as f:
        f.write(msg + "\n")


def _clear_state() -> None:
    for p in (PENDING_CODE, LOGIN_LOG, LOGIN_DONE):
        if p.exists():
            p.unlink()


async def _wait_for_code() -> str:
    for _ in range(POLL_TIMEOUT_SECONDS):
        if PENDING_CODE.exists():
            code = PENDING_CODE.read_text().strip()
            PENDING_CODE.unlink()
            _log(f"code received from pending file")
            return code
        await asyncio.sleep(1)
    raise TimeoutError(f"no code received in {POLL_TIMEOUT_SECONDS}s")


async def _start_persistent_login(password: str | None) -> int:
    creds = load_credentials()
    if not creds.phone:
        sys.exit("phone not in telegram.json")

    _clear_state()
    LOGIN_LOG.write_text("login starting\n")

    async with open_client(allow_unauthenticated=True) as client:
        if await client.is_user_authorized():
            me = await client.get_me()
            _log(f"already authorized as @{me.username} id={me.id}")
            LOGIN_DONE.write_text("ok\n")
            print(f"already logged in as {me.first_name} (@{me.username}) id={me.id}")
            return 0

        sent = await client.send_code_request(creds.phone)
        _log(f"code sent for {creds.phone}, hash={sent.phone_code_hash[:8]}...")
        # Visible signal to caller that the request is live and we're now waiting.
        print(f"code sent to {creds.phone}; waiting for {PENDING_CODE} ({POLL_TIMEOUT_SECONDS//60} min)")
        sys.stdout.flush()

        code = await _wait_for_code()

        try:
            await client.sign_in(
                phone=creds.phone,
                code=code,
                phone_code_hash=sent.phone_code_hash,
            )
        except Exception as e:
            if "SessionPasswordNeededError" in type(e).__name__:
                if not password:
                    _log("2FA needed but no password supplied at start")
                    LOGIN_DONE.write_text("error: 2fa-no-password\n")
                    sys.exit("2FA password required — restart with --password")
                _log("submitting 2FA password")
                await client.sign_in(password=password)
            else:
                _log(f"sign_in error: {type(e).__name__}: {e}")
                LOGIN_DONE.write_text(f"error: {type(e).__name__}\n")
                raise

        me = await client.get_me()
        _log(f"signed in as @{me.username} id={me.id}")
        LOGIN_DONE.write_text(f"ok @{me.username} id={me.id}\n")
        print(f"logged in as {me.first_name} (@{me.username}) id={me.id}")

    if SESSION_FILE.exists():
        os.chmod(SESSION_FILE, 0o600)
    return 0


def _submit_code(code: str) -> int:
    if not code or not code.isdigit():
        sys.exit(f"code must be digits, got {code!r}")
    PENDING_CODE.parent.mkdir(parents=True, exist_ok=True)
    PENDING_CODE.write_text(code)
    os.chmod(PENDING_CODE, 0o600)
    print(f"code {code} written to {PENDING_CODE}; background login process should pick it up within 1s")
    return 0


async def _interactive() -> int:
    """TTY fallback. Single process, keeps connection open."""
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
    if args is None or (not args.start and not args.submit_code):
        return await _interactive()
    if args.submit_code:
        return _submit_code(args.submit_code)
    return await _start_persistent_login(args.password)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", action="store_true",
                   help="connect, request code, wait for --submit-code (run in background)")
    p.add_argument("--submit-code", help="relay 5-digit code to a running --start process")
    p.add_argument("--password", help="2FA cloud password if set")
    args = p.parse_args()
    if args.submit_code:
        return _submit_code(args.submit_code)
    return asyncio.run(run_login(args))


if __name__ == "__main__":
    sys.exit(main())
