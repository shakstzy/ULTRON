"""Interactive Telethon login. Run once.

Reads phone from telegram.json if present, else prompts. Telegram sends a code
to the existing Telegram app (or SMS if no other session). User pastes it back.
If a 2FA cloud password is set, prompts for it.
"""
from __future__ import annotations

import asyncio
import getpass
import os
import sys

from session import (
    SESSION_FILE,
    load_credentials,
    open_client,
    write_credentials,
)


async def run_login() -> int:
    creds = load_credentials()
    phone = creds.phone or input("phone (E.164, e.g. +15125551234): ").strip()
    if not phone.startswith("+"):
        sys.exit("phone must be E.164, starting with +")

    # Persist phone so future logins skip the prompt.
    if creds.phone != phone:
        write_credentials(creds.api_id, creds.api_hash, phone)

    async with open_client(allow_unauthenticated=True) as client:
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"already logged in as {me.first_name} (@{me.username}) id={me.id}")
            return 0

        await client.send_code_request(phone)
        code = input("code from Telegram (5 digits): ").strip()
        try:
            await client.sign_in(phone=phone, code=code)
        except Exception as e:
            # Telethon raises SessionPasswordNeededError when 2FA is on.
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


if __name__ == "__main__":
    sys.exit(asyncio.run(run_login()))
