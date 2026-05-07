#!/usr/bin/env python3
"""
add.py — write a new entry into Apple Contacts and sync the result into
`_global/entities/people/`.

See `_shell/skills/contacts-add/SKILL.md` for the full contract.

Usage:
    add.py add --name "Maya" [--phone "+15125551212"]... [--email "maya@x.com"]...
               [--organization "X"] [--note "..."] [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
SYNC_SCRIPT = ULTRON_ROOT / "_shell" / "skills" / "contacts-sync" / "scripts" / "sync.py"


def build_contact(args: argparse.Namespace):
    """Construct a CNMutableContact from args. Returns the object or None
    if the Contacts framework is unavailable."""
    try:
        from Contacts import (  # type: ignore
            CNMutableContact, CNLabeledValue, CNPhoneNumber,
            CNLabelHome, CNLabelWork,
        )
    except ImportError as e:
        sys.stderr.write(f"contacts-add: Contacts framework unavailable: {e}\n")
        sys.stderr.write("Hint: run with the venv python at ~/ULTRON/.venv/bin/python3\n")
        return None

    contact = CNMutableContact.alloc().init()

    if args.name:
        # Split on first space: given + family. Single-word names go to given_name.
        parts = args.name.strip().split(None, 1)
        contact.setGivenName_(parts[0])
        if len(parts) > 1:
            contact.setFamilyName_(parts[1])

    if args.organization:
        contact.setOrganizationName_(args.organization)

    if args.note:
        # CNContactNoteKey requires entitlements on macOS 13+; skip silently
        # if the API isn't available. The note is preserved in the markdown
        # body anyway.
        try:
            contact.setNote_(args.note)
        except Exception:
            pass

    if args.phone:
        labeled = []
        for p in args.phone:
            num = CNPhoneNumber.phoneNumberWithStringValue_(p)
            labeled.append(CNLabeledValue.labeledValueWithLabel_value_(CNLabelHome, num))
        contact.setPhoneNumbers_(labeled)

    if args.email:
        labeled = []
        for e in args.email:
            labeled.append(CNLabeledValue.labeledValueWithLabel_value_(CNLabelHome, e))
        contact.setEmailAddresses_(labeled)

    return contact


def describe_contact(contact) -> str:
    given = contact.givenName() or ""
    family = contact.familyName() or ""
    org = contact.organizationName() or ""
    name = (given + " " + family).strip() or org or "(unnamed)"
    phones = [p.value().stringValue() for p in (contact.phoneNumbers() or [])]
    emails = [str(e.value()) for e in (contact.emailAddresses() or [])]
    parts = [f"name={name!r}"]
    if phones:
        parts.append(f"phones={phones}")
    if emails:
        parts.append(f"emails={emails}")
    if org:
        parts.append(f"org={org!r}")
    return " ".join(parts)


def find_duplicates(args: argparse.Namespace) -> list[str]:
    """Return display names of existing contacts that match by phone or
    email. Used for pre-save duplicate guarding."""
    try:
        from Contacts import (  # type: ignore
            CNContactStore, CNContactFetchRequest,
            CNContactGivenNameKey, CNContactFamilyNameKey,
            CNContactPhoneNumbersKey, CNContactEmailAddressesKey,
        )
    except ImportError:
        return []

    norm_phones = {re.sub(r"\D", "", p) for p in (args.phone or []) if p}
    norm_emails = {e.strip().lower() for e in (args.email or []) if e}
    if not norm_phones and not norm_emails:
        return []

    store = CNContactStore.alloc().init()
    keys = [CNContactGivenNameKey, CNContactFamilyNameKey,
            CNContactPhoneNumbersKey, CNContactEmailAddressesKey]
    req = CNContactFetchRequest.alloc().initWithKeysToFetch_(keys)
    matches: list[str] = []

    def cb(contact, stop):
        for ph in contact.phoneNumbers():
            digits = re.sub(r"\D", "", ph.value().stringValue() or "")
            if digits and digits in norm_phones:
                matches.append(_display(contact))
                return
        for em in contact.emailAddresses():
            v = str(em.value() or "").strip().lower()
            if v and v in norm_emails:
                matches.append(_display(contact))
                return

    try:
        store.enumerateContactsWithFetchRequest_error_usingBlock_(req, None, cb)
    except Exception:
        pass
    return matches


def _display(contact) -> str:
    g = (contact.givenName() or "").strip()
    f = (contact.familyName() or "").strip()
    return (g + " " + f).strip() or "(unnamed)"


def cmd_add(args: argparse.Namespace) -> int:
    if not (args.name or args.phone or args.email):
        sys.stderr.write("contacts-add: refuse — need at least one of --name / --phone / --email\n")
        return 2

    if args.name and len(args.name) > 200:
        sys.stderr.write("contacts-add: refuse — name longer than 200 chars\n")
        return 2

    contact = build_contact(args)
    if contact is None:
        return 1

    if args.dry_run:
        dupes = find_duplicates(args)
        if dupes:
            print(f"[DRY-RUN] would add: {describe_contact(contact)}")
            print(f"[DRY-RUN] WARNING: existing contact(s) match by phone/email: {dupes}")
        else:
            print(f"[DRY-RUN] would add: {describe_contact(contact)}")
        return 0

    if not args.force:
        dupes = find_duplicates(args)
        if dupes:
            sys.stderr.write(
                f"contacts-add: refusing — existing contact(s) match by phone/email: {dupes}. "
                f"Re-run with --force to add anyway.\n"
            )
            return 4

    from Contacts import CNContactStore, CNSaveRequest  # type: ignore

    store = CNContactStore.alloc().init()
    req = CNSaveRequest.alloc().init()
    req.addContact_toContainerWithIdentifier_(contact, None)

    # pyobjc's signature for executeSaveRequest_error_ may return either
    # `(success, error)` or just `success` depending on bridge support
    # version. Guard the unpack.
    result = store.executeSaveRequest_error_(req, None)
    if isinstance(result, tuple):
        success, err = result[0], result[1] if len(result) > 1 else None
    else:
        success, err = bool(result), None
    if not success:
        sys.stderr.write(f"contacts-add: save failed: {err}\n")
        return 3

    print(f"added: {describe_contact(contact)}")

    # Refresh the global people stub so callers can immediately reference it.
    if SYNC_SCRIPT.exists():
        rc = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT)],
            capture_output=True, text=True,
        )
        if rc.returncode != 0:
            sys.stderr.write(f"contacts-add: post-sync warning: {rc.stderr.strip()}\n")
        else:
            tail = rc.stdout.strip().splitlines()[-1] if rc.stdout.strip() else ""
            print(f"sync: {tail}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("--name")
    a.add_argument("--phone", action="append", default=[])
    a.add_argument("--email", action="append", default=[])
    a.add_argument("--organization")
    a.add_argument("--note")
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--force", action="store_true",
                   help="Save even if a contact with matching phone/email exists.")

    args = ap.parse_args()
    if args.cmd == "add":
        return cmd_add(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
