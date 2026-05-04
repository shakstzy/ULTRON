#!/usr/bin/env python3
"""
validate-drive-config.py — structural + (optional) live linting for the
sources.drive blocks across every workspace.

Usage:
    validate-drive-config.py [--workspace <ws>] [--live] [--output <path>]

Without --live: pure structural checks. No network.
With --live: trades each refresh token for an access token, calls
files.get for each declared folder ID, and verifies exclude_subfolders[]
are descendants of their parent.

Exit codes:
    0 — all checks pass
    1 — at least one violation
    2 — invocation error

See _shell/stages/ingest/drive/format.md § Lock 10 for the schema.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable

ULTRON_ROOT = Path(os.environ.get("ULTRON_ROOT", str(Path.home() / "ULTRON")))
CREDS_DIR = ULTRON_ROOT / "_credentials"
WS_ROOT = ULTRON_ROOT / "workspaces"


def _account_slug(email: str) -> str:
    if not email or "@" not in email:
        return ""
    local, _, domain = email.lower().partition("@")
    first = domain.split(".")[0] if domain else ""
    return f"{local}-{first}".replace(".", "-").strip("-")


def _load_yaml(path: Path):
    try:
        import yaml
    except ImportError:
        sys.stderr.write("validate-drive-config: missing dep pyyaml\n")
        sys.exit(2)
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text()) or {}
    except yaml.YAMLError as e:
        return {"_yaml_error": str(e)}


def _drive_block(cfg: dict) -> dict | None:
    sources = (cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get("drive")
    if isinstance(sources, list):
        for s in sources:
            if isinstance(s, dict) and s.get("type") == "drive":
                return s.get("config") or s
    return None


def structural_check(workspaces: list[str]) -> tuple[list[str], dict]:
    """Returns (violations, claims_index). claims_index = {folder_id: [(ws, account)]}."""
    violations: list[str] = []
    claims: dict[str, list[tuple[str, str]]] = {}

    for ws in workspaces:
        cfg_path = WS_ROOT / ws / "config" / "sources.yaml"
        cfg = _load_yaml(cfg_path)
        if cfg is None:
            continue
        if isinstance(cfg, dict) and "_yaml_error" in cfg:
            violations.append(f"{ws}: sources.yaml unparseable: {cfg['_yaml_error']}")
            continue
        block = _drive_block(cfg)
        if not block:
            continue

        accts = block.get("accounts")
        if not isinstance(accts, list):
            violations.append(f"{ws}: sources.drive.accounts must be a list")
            continue

        for i, acct in enumerate(accts):
            if not isinstance(acct, dict):
                violations.append(f"{ws}: sources.drive.accounts[{i}] is not a mapping")
                continue
            email = acct.get("account")
            if not email or "@" not in str(email):
                violations.append(f"{ws}: accounts[{i}].account missing or not an email")
                continue
            slug = _account_slug(email)
            cred = CREDS_DIR / f"gmail-{slug}.json"
            if not cred.exists():
                violations.append(
                    f"{ws}: accounts[{i}].account={email} → expected credential "
                    f"_credentials/gmail-{slug}.json not found"
                )

            folders = acct.get("folders")
            if not isinstance(folders, list) or not folders:
                violations.append(f"{ws}: accounts[{i}].folders must be a non-empty list")
                continue

            for j, folder in enumerate(folders):
                if not isinstance(folder, dict):
                    violations.append(f"{ws}: accounts[{i}].folders[{j}] is not a mapping")
                    continue
                fid = folder.get("id")
                fname = folder.get("name")
                if not fid or not isinstance(fid, str):
                    violations.append(f"{ws}: accounts[{i}].folders[{j}].id missing")
                    continue
                if not fname or not isinstance(fname, str):
                    violations.append(
                        f"{ws}: accounts[{i}].folders[{j}].name missing "
                        "(human-readable label is required for config clarity)"
                    )
                claims.setdefault(fid, []).append((ws, email))

                excl = folder.get("exclude_subfolders") or []
                if not isinstance(excl, list):
                    violations.append(
                        f"{ws}: accounts[{i}].folders[{j}].exclude_subfolders must be a list"
                    )
                    continue
                for k, e in enumerate(excl):
                    if not isinstance(e, dict) or not e.get("id"):
                        violations.append(
                            f"{ws}: accounts[{i}].folders[{j}].exclude_subfolders[{k}].id missing"
                        )

    # Lock 10: folder claims are exclusive in v1.
    for fid, owners in claims.items():
        unique_ws = {ws for ws, _ in owners}
        if len(unique_ws) > 1:
            violations.append(
                f"folder {fid} claimed by multiple workspaces: {sorted(unique_ws)}. "
                "Folder claims are exclusive in v1; deconflict in sources.yaml or "
                "wait for the routing-layer also_route_to mechanism."
            )

    return violations, claims


def _refresh_token(cred: dict) -> str | None:
    data = urllib.parse.urlencode({
        "client_id": cred.get("client_id", ""),
        "client_secret": cred.get("client_secret", ""),
        "refresh_token": cred.get("refresh_token", ""),
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(
        cred.get("token_uri", "https://oauth2.googleapis.com/token"),
        data=data,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()).get("access_token")
    except Exception:
        return None


def _drive_get(file_id: str, access_token: str, fields: str = "id,name,mimeType,parents,trashed") -> dict | None:
    url = (
        f"https://www.googleapis.com/drive/v3/files/{urllib.parse.quote(file_id)}"
        f"?fields={urllib.parse.quote(fields)}&supportsAllDrives=true"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read()).get("error", {})
        except Exception:
            body = {"code": e.code}
        return {"_error": body}
    except Exception as e:
        return {"_error": {"message": str(e)}}


def _is_descendant(child_id: str, ancestor_id: str, access_token: str, max_hops: int = 8) -> bool:
    """Walk parents up to max_hops; return True if ancestor_id is in the chain."""
    cur = child_id
    for _ in range(max_hops):
        if cur == ancestor_id:
            return True
        info = _drive_get(cur, access_token, fields="id,parents")
        if not info or "_error" in info:
            return False
        parents = info.get("parents") or []
        if not parents:
            return False
        cur = parents[0]
    return False


def live_check(claims: dict, workspaces: list[str]) -> list[str]:
    """For each (account, folder), confirm the account's token can read the folder
    and folder is the right type. Confirm exclude_subfolders descend from parent."""
    violations: list[str] = []

    # Group claims by account so we only refresh each token once.
    by_account: dict[str, dict] = {}
    for fid, owners in claims.items():
        for ws, email in owners:
            by_account.setdefault(email, {"folders": set(), "exclude_pairs": []})
            by_account[email]["folders"].add(fid)

    # Re-walk YAML to pull exclude pairs per account.
    for ws in workspaces:
        cfg = _load_yaml(WS_ROOT / ws / "config" / "sources.yaml")
        if not cfg or "_yaml_error" in (cfg or {}):
            continue
        block = _drive_block(cfg)
        if not block:
            continue
        for acct in block.get("accounts") or []:
            if not isinstance(acct, dict):
                continue
            email = acct.get("account")
            if not email:
                continue
            for folder in acct.get("folders") or []:
                if not isinstance(folder, dict) or not folder.get("id"):
                    continue
                parent = folder["id"]
                for e in folder.get("exclude_subfolders") or []:
                    if isinstance(e, dict) and e.get("id"):
                        by_account.setdefault(email, {"folders": set(), "exclude_pairs": []})
                        by_account[email]["exclude_pairs"].append((parent, e["id"]))

    for email, payload in by_account.items():
        slug = _account_slug(email)
        cred_path = CREDS_DIR / f"gmail-{slug}.json"
        if not cred_path.exists():
            violations.append(f"live: {email}: missing credential {cred_path}")
            continue
        try:
            cred = json.loads(cred_path.read_text())
        except Exception as e:
            violations.append(f"live: {email}: credential unreadable: {e}")
            continue

        access = _refresh_token(cred)
        if not access:
            violations.append(f"live: {email}: refresh_token failed")
            continue

        for fid in sorted(payload["folders"]):
            info = _drive_get(fid, access)
            if not info or "_error" in info:
                err = (info or {}).get("_error", {}).get("message", "no response")
                violations.append(f"live: {email}: folder {fid} not reachable: {err}")
                continue
            if info.get("mimeType") != "application/vnd.google-apps.folder":
                violations.append(
                    f"live: {email}: id {fid} is not a folder (mime: {info.get('mimeType')})"
                )
            if info.get("trashed"):
                violations.append(f"live: {email}: folder {fid} is trashed")

        for parent, child in payload["exclude_pairs"]:
            if not _is_descendant(child, parent, access):
                violations.append(
                    f"live: {email}: exclude_subfolders id {child} is not a descendant of {parent}"
                )

    return violations


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace")
    ap.add_argument("--live", action="store_true", help="Hit Drive API to verify folder IDs")
    ap.add_argument("--output")
    args = ap.parse_args()

    if not WS_ROOT.exists():
        sys.stderr.write(f"validate-drive-config: workspaces dir not found at {WS_ROOT}\n")
        return 2

    if args.workspace:
        if not (WS_ROOT / args.workspace).exists():
            sys.stderr.write(f"workspace not found: {args.workspace}\n")
            return 2
        workspaces = [args.workspace]
    else:
        workspaces = sorted(
            p.name for p in WS_ROOT.iterdir()
            if p.is_dir() and not p.name.startswith("_")
        )

    violations, claims = structural_check(workspaces)
    if args.live:
        violations.extend(live_check(claims, workspaces))

    output = "\n".join(violations)
    if args.output:
        Path(args.output).write_text(output + ("\n" if output else ""))
    elif output:
        print(output)

    if violations:
        sys.stderr.write(f"validate-drive-config: {len(violations)} violation(s)\n")
        return 1
    sys.stderr.write(
        f"validate-drive-config: OK — {len(claims)} designated folder(s) "
        f"across {len(workspaces)} workspace(s)\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
