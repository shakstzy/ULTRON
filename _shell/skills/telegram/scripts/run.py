"""Telegram CLI dispatcher.

Verbs: login, whoami, chats, read, send, status, reset-breaker.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import timezone
from pathlib import Path
from typing import Any

# Allow `python3 scripts/run.py ...` from any cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from session import (
    SESSION_FILE,
    breaker_state,
    clear_breaker,
    load_credentials,
    open_client,
    session_exists,
)


def _kind_of(entity) -> str:
    from telethon.tl.types import Channel, Chat, User
    if isinstance(entity, User):
        return "dm"
    if isinstance(entity, Chat):
        return "group"
    if isinstance(entity, Channel):
        return "channel" if getattr(entity, "broadcast", False) else "group"
    return "unknown"


def _entity_title(entity) -> str:
    from telethon.tl.types import Channel, Chat, User
    if isinstance(entity, User):
        parts = [entity.first_name or "", entity.last_name or ""]
        name = " ".join(p for p in parts if p).strip()
        if entity.username:
            return f"{name or entity.username} (@{entity.username})"
        return name or f"id:{entity.id}"
    if isinstance(entity, (Chat, Channel)):
        title = entity.title or f"id:{entity.id}"
        if isinstance(entity, Channel) and entity.username:
            return f"{title} (@{entity.username})"
        return title
    return f"id:{getattr(entity, 'id', '?')}"


async def _resolve_chat(client, query: str):
    """Resolve a chat reference to a single entity. Accepts:
       - numeric id (e.g. "123456789" or "-100123...")
       - @username
       - case-insensitive substring of dialog title or first/last/username

    Returns (entity, chat_id) or raises SystemExit on 0 or >1 matches.
    """
    # numeric id
    try:
        chat_id = int(query)
        ent = await client.get_entity(chat_id)
        return ent, chat_id
    except ValueError:
        pass

    # @username
    if query.startswith("@"):
        ent = await client.get_entity(query)
        return ent, ent.id

    q = query.lower().strip()
    matches = []
    async for dlg in client.iter_dialogs(limit=500):
        ent = dlg.entity
        title = _entity_title(ent).lower()
        if q in title:
            matches.append((ent, dlg.id))
    if not matches:
        sys.exit(f"chat not found: {query!r}. Try: python3 scripts/run.py chats --query {query!r}")
    if len(matches) > 1:
        print(f"multiple matches for {query!r}:", file=sys.stderr)
        for ent, cid in matches[:10]:
            print(f"  {cid}\t{_kind_of(ent)}\t{_entity_title(ent)}", file=sys.stderr)
        sys.exit("disambiguate by passing numeric id or @username")
    return matches[0]


async def cmd_whoami(args) -> int:
    async with open_client() as client:
        me = await client.get_me()
        out = {
            "id": me.id,
            "first_name": me.first_name,
            "last_name": me.last_name,
            "username": me.username,
            "phone": me.phone,
            "is_premium": getattr(me, "premium", False),
        }
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            name = " ".join(p for p in [me.first_name or "", me.last_name or ""] if p).strip()
            print(f"{name} (@{me.username}) id={me.id} phone=+{me.phone}")
    return 0


async def cmd_chats(args) -> int:
    out = []
    async with open_client() as client:
        async for dlg in client.iter_dialogs(limit=args.limit):
            ent = dlg.entity
            kind = _kind_of(ent)
            if args.kind != "all" and kind != args.kind:
                continue
            title = _entity_title(ent)
            if args.query and args.query.lower() not in title.lower():
                continue
            last = dlg.message
            last_ts = last.date.astimezone(timezone.utc).isoformat() if last else None
            out.append({
                "id": dlg.id,
                "kind": kind,
                "title": title,
                "unread": dlg.unread_count,
                "last_ts": last_ts,
            })
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for row in out:
            unread = f" [{row['unread']}]" if row["unread"] else ""
            print(f"{row['id']:>15}  {row['kind']:<7}  {row['title']}{unread}")
    return 0


async def cmd_read(args) -> int:
    async with open_client() as client:
        ent, chat_id = await _resolve_chat(client, args.chat)
        me = await client.get_me()
        messages: list[dict[str, Any]] = []
        async for msg in client.iter_messages(ent, limit=args.limit):
            sender_id = getattr(msg.sender, "id", None) if msg.sender else None
            sender_name = None
            if msg.sender is not None:
                sender_name = _entity_title(msg.sender)
            media_kind = None
            if msg.photo:
                media_kind = "photo"
            elif msg.video:
                media_kind = "video"
            elif msg.voice:
                media_kind = "voice"
            elif msg.audio:
                media_kind = "audio"
            elif msg.document:
                media_kind = "document"
            elif msg.sticker:
                media_kind = "sticker"
            messages.append({
                "id": msg.id,
                "ts": msg.date.astimezone(timezone.utc).isoformat(),
                "from": {"id": sender_id, "name": sender_name, "is_me": sender_id == me.id},
                "text": msg.message or "",
                "reply_to_id": msg.reply_to_msg_id,
                "media_kind": media_kind,
                "edited": msg.edit_date.astimezone(timezone.utc).isoformat() if msg.edit_date else None,
            })
        # Telethon returns newest-first; flip to chronological.
        messages.reverse()
        result = {
            "chat": {"id": chat_id, "kind": _kind_of(ent), "title": _entity_title(ent)},
            "messages": messages,
        }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"# {result['chat']['title']} ({result['chat']['kind']}, id={result['chat']['id']})")
        for m in messages:
            who = "me" if m["from"]["is_me"] else (m["from"]["name"] or f"id:{m['from']['id']}")
            edit = " (edited)" if m["edited"] else ""
            media = f" [{m['media_kind']}]" if m["media_kind"] else ""
            text = m["text"] or ""
            print(f"{m['ts'][:19]}Z  {who}{edit}{media}: {text}")
    return 0


async def cmd_send(args) -> int:
    text = " ".join(args.text).strip()
    if not text:
        sys.exit("empty message")
    async with open_client() as client:
        ent, chat_id = await _resolve_chat(client, args.chat)
        if args.dry_run:
            out = {
                "dry_run": True,
                "chat_id": chat_id,
                "chat_title": _entity_title(ent),
                "chat_kind": _kind_of(ent),
                "text": text,
                "would_send": True,
            }
            if args.json:
                print(json.dumps(out, indent=2))
            else:
                print(f"DRY-RUN — would send to {out['chat_title']} (id={chat_id}, {out['chat_kind']}): {text!r}")
            return 0
        msg = await client.send_message(ent, text)
        out = {
            "chat_id": chat_id,
            "chat_title": _entity_title(ent),
            "message_id": msg.id,
            "ts": msg.date.astimezone(timezone.utc).isoformat(),
            "text": text,
        }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"sent to {out['chat_title']} (id={chat_id}) message_id={out['message_id']}")
    return 0


async def cmd_status(args) -> int:
    creds_present = False
    api_id = None
    phone = None
    try:
        c = load_credentials()
        creds_present = True
        api_id = c.api_id
        phone = c.phone
    except SystemExit:
        pass
    state = breaker_state()
    out = {
        "credentials_present": creds_present,
        "api_id": api_id,
        "phone": phone,
        "session_exists": session_exists(),
        "session_path": str(SESSION_FILE),
        "breaker": state,
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"credentials: {'OK' if creds_present else 'MISSING'} ({load_credentials.__module__})")
        print(f"api_id: {api_id}")
        print(f"phone: {phone}")
        print(f"session: {'OK' if out['session_exists'] else 'MISSING'} at {SESSION_FILE}")
        if state.get("halted"):
            print(f"breaker: HALTED — {state.get('reason')} ({state.get('age_seconds')}s ago)")
        else:
            print("breaker: clear")
    return 0


def cmd_reset_breaker(args) -> int:
    clear_breaker()
    print("breaker cleared")
    return 0


def cmd_login(args) -> int:
    from login import run_login
    return asyncio.run(run_login(args))


def main() -> int:
    p = argparse.ArgumentParser(prog="telegram", description="Telegram MTProto CLI (Telethon)")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="output JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("login", parents=[common], help="phone+code auth (one-time)")
    pl.add_argument("--send-code", action="store_true", help="phase 1: trigger Telegram code")
    pl.add_argument("--code", help="phase 2: 5-digit code from Telegram")
    pl.add_argument("--phone", help="override phone in telegram.json")
    pl.add_argument("--password", help="2FA cloud password if set")
    sub.add_parser("whoami", parents=[common], help="confirm session")

    pc = sub.add_parser("chats", parents=[common], help="list dialogs")
    pc.add_argument("--query", help="case-insensitive substring filter")
    pc.add_argument("--limit", type=int, default=100)
    pc.add_argument("--kind", choices=["dm", "group", "channel", "all"], default="all")

    pr = sub.add_parser("read", parents=[common], help="last N messages from a chat")
    pr.add_argument("chat", help="chat id, @username, or name substring")
    pr.add_argument("--limit", type=int, default=20)

    ps = sub.add_parser("send", parents=[common], help="send a text message")
    ps.add_argument("chat", help="chat id, @username, or name substring")
    ps.add_argument("text", nargs="+", help="message body")
    ps.add_argument("--dry-run", action="store_true",
                    help="resolve chat + render payload but do NOT send")

    sub.add_parser("status", parents=[common], help="credentials + session + breaker state")
    sub.add_parser("reset-breaker", parents=[common], help="clear 24h halt")

    args = p.parse_args()

    handlers_async = {
        "whoami": cmd_whoami,
        "chats": cmd_chats,
        "read": cmd_read,
        "send": cmd_send,
        "status": cmd_status,
    }
    handlers_sync = {
        "login": cmd_login,
        "reset-breaker": cmd_reset_breaker,
    }
    if args.cmd in handlers_async:
        return asyncio.run(handlers_async[args.cmd](args))
    return handlers_sync[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
