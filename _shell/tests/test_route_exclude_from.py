#!/usr/bin/env python3
"""Tests for route.py compound predicates, negation, and exclude_from.

Asserts:
  * Compound rules `from:X subject:"Y"` AND-evaluate.
  * Negated clauses `-subject:"Z"` work.
  * `subject:"phrase"` quoted form is contains, case-insensitive.
  * `from:<bare-domain>` matches the domain and subdomains.
  * `api_query.exclude_from: <path>` loads excludes from a separate YAML.
  * exclude_from rules union with inline `exclude` rules.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import yaml

ULTRON_ROOT = Path(__file__).resolve().parent.parent.parent
os.environ.setdefault("ULTRON_ROOT", str(ULTRON_ROOT))
sys.path.insert(0, str(ULTRON_ROOT / "_shell" / "stages" / "ingest" / "gmail"))

import route  # noqa: E402


def _thread(*, frm: str = "", subject: str = "", labels=None, account: str = "adithya@synps.xyz") -> dict:
    return {
        "account": account,
        "subject": subject,
        "labels": list(labels or []),
        "participants": [{"email": frm, "name": "", "roles": ["from"]}] if frm else [],
    }


def test_compound_and() -> None:
    rule = 'from:workspace-noreply@google.com subject:"Product Update"'
    fires = route._evaluate_rule(
        _thread(frm="workspace-noreply@google.com", subject="Product Update: October"), rule)
    assert fires, "compound rule should fire when both clauses match"

    fires = route._evaluate_rule(
        _thread(frm="workspace-noreply@google.com", subject="[Action Required] Domain renewal"), rule)
    assert not fires, "compound rule should NOT fire when subject clause misses"

    fires = route._evaluate_rule(
        _thread(frm="other@google.com", subject="Product Update"), rule)
    assert not fires, "compound rule should NOT fire when from clause misses"


def test_negated_clause() -> None:
    rule = 'from:hello@alchemy.com -subject:"invited to"'
    excluded = route._evaluate_rule(
        _thread(frm="hello@alchemy.com", subject="Latest from Alchemy"), rule)
    assert excluded, "newsletter from hello@alchemy.com should be excluded"

    kept = route._evaluate_rule(
        _thread(frm="hello@alchemy.com", subject="You are invited to Alchemy workspace"), rule)
    assert not kept, "workspace invite should NOT be excluded (negation kicks in)"


def test_subject_quoted_form() -> None:
    fires = route._evaluate_rule(_thread(subject="Stand out on Google Search"), 'subject:"Stand out on Google"')
    assert fires
    fires = route._evaluate_rule(_thread(subject="STAND OUT ON GOOGLE"), 'subject:"stand out"')
    assert fires, "subject contains is case-insensitive"
    fires = route._evaluate_rule(_thread(subject="other"), 'subject:"Stand out"')
    assert not fires


def test_bare_domain_matches_subdomains() -> None:
    rule = "from:cluely.com"
    assert route._evaluate_rule(_thread(frm="roy@cluely.com"), rule)
    assert route._evaluate_rule(_thread(frm="hello@mail.cluely.com"), rule)
    assert not route._evaluate_rule(_thread(frm="roy@cluelyfake.com"), rule)
    assert not route._evaluate_rule(_thread(frm="roy@notcluely.com"), rule)


def test_legacy_predicates_still_work() -> None:
    assert route._evaluate_rule(_thread(labels=["Eclipse"]), "label:Eclipse")
    assert route._evaluate_rule(_thread(frm="sydney@eclipse.audio"), "from:*@eclipse.audio")
    assert route._evaluate_rule(_thread(subject="Welcome"), "subject:contains:Welcome")
    assert route._evaluate_rule(_thread(subject="Welcome"), "subject:regex:^Welcome$")
    assert not route._evaluate_rule(_thread(subject="Welcome"), "subject:regex:^[")  # bad regex → False


def test_throwaway_tld_glob() -> None:
    assert route._evaluate_rule(_thread(frm="spam@foo.info"), "from:*.info")
    assert route._evaluate_rule(_thread(frm="x@bar.live"), "from:*.live")
    assert not route._evaluate_rule(_thread(frm="x@bar.com"), "from:*.info")


def test_exclude_from_loads_external_file() -> None:
    """End-to-end: route() honors exclude_from path, unioning shared excludes
    with inline ones."""
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        # Pretend td is ULTRON_ROOT for path resolution.
        old_root = os.environ.get("ULTRON_ROOT")
        os.environ["ULTRON_ROOT"] = str(td_path)
        try:
            exclude_file = td_path / "shared-excludes.yaml"
            exclude_file.write_text(yaml.safe_dump({
                "excludes": [
                    "from:igniteyourfunnels.com",
                    'from:hello@alchemy.com -subject:"invited to"',
                    'from:workspace-noreply@google.com subject:"Product Update"',
                ]
            }))
            route._load_exclude_file.cache_clear()

            workspaces_config = {
                "personal": {
                    "sources": {
                        "gmail": {
                            "accounts": [
                                {
                                    "account": "adithya@synps.xyz",
                                    "api_query": {
                                        "include": [],  # match-all
                                        "exclude": ["label:SPAM", "label:TRASH"],
                                        "exclude_from": "shared-excludes.yaml",
                                    },
                                }
                            ]
                        }
                    }
                }
            }

            cold = _thread(frm="paul@igniteyourfunnels.com", subject="Yes?")
            assert route.route(cold, workspaces_config) == [], \
                "cold-pitch from shared exclude file must drop"

            news = _thread(frm="hello@alchemy.com", subject="Latest news")
            assert route.route(news, workspaces_config) == [], \
                "alchemy newsletter must drop"

            invite = _thread(frm="hello@alchemy.com",
                             subject="operations@synps.xyz invited to Alchemy workspace")
            got = route.route(invite, workspaces_config)
            assert got and got[0]["workspace"] == "personal", \
                f"workspace invite must NOT drop; got {got!r}"

            ws_op = _thread(frm="workspace-noreply@google.com",
                            subject="[Action Required] Domain renewal")
            got = route.route(ws_op, workspaces_config)
            assert got and got[0]["workspace"] == "personal", \
                f"operational workspace mail must NOT drop; got {got!r}"

            ws_promo = _thread(frm="workspace-noreply@google.com",
                               subject="Product Update: New features")
            assert route.route(ws_promo, workspaces_config) == [], \
                "subject-scoped promo must drop"

            inline = _thread(labels=["TRASH"])
            assert route.route(inline, workspaces_config) == [], \
                "inline exclude (label:TRASH) must still apply"
        finally:
            route._load_exclude_file.cache_clear()
            if old_root is None:
                os.environ.pop("ULTRON_ROOT", None)
            else:
                os.environ["ULTRON_ROOT"] = old_root


def test_exclude_from_missing_file_is_silent() -> None:
    """exclude_from pointing at a non-existent path must not crash; the
    inline excludes remain authoritative."""
    workspaces_config = {
        "personal": {
            "sources": {
                "gmail": {
                    "accounts": [
                        {
                            "account": "adithya@synps.xyz",
                            "api_query": {
                                "include": [],
                                "exclude": ["label:TRASH"],
                                "exclude_from": "_shell/config/account-excludes/does-not-exist.yaml",
                            },
                        }
                    ]
                }
            }
        }
    }
    got = route.route(_thread(frm="anyone@elsewhere.tld"), workspaces_config)
    assert got and got[0]["workspace"] == "personal"


def main() -> int:
    tests = [
        ("compound AND", test_compound_and),
        ("negated clause", test_negated_clause),
        ("subject quoted form", test_subject_quoted_form),
        ("bare domain matches subdomains", test_bare_domain_matches_subdomains),
        ("legacy predicates still work", test_legacy_predicates_still_work),
        ("throwaway TLD glob", test_throwaway_tld_glob),
        ("exclude_from loads external file", test_exclude_from_loads_external_file),
        ("exclude_from missing file silent", test_exclude_from_missing_file_is_silent),
    ]
    passed = 0
    failed: list[tuple[str, str]] = []
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as exc:
            print(f"FAIL  {name}: {exc}")
            failed.append((name, str(exc)))
        except Exception as exc:
            print(f"ERROR {name}: {type(exc).__name__}: {exc}")
            failed.append((name, repr(exc)))
    print()
    print(f"{passed}/{len(tests)} passed")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
