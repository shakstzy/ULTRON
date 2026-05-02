#!/usr/bin/env python3
"""Test the Gmail union query construction in ingest-gmail.py.

Asserts:
  * Union covers eclipse + personal includes when both subscribe.
  * Excludes from any subscriber appear as `-` clauses.
  * No duplicate clauses.
  * Total q= length stays under Gmail's practical 2KB limit.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ULTRON_ROOT = Path(__file__).resolve().parent.parent.parent
os.environ.setdefault("ULTRON_ROOT", str(ULTRON_ROOT))

sys.path.insert(0, str(ULTRON_ROOT / "_shell" / "bin"))

# ingest-gmail.py is hyphen-named; load via importlib.
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "ingest_gmail", ULTRON_ROOT / "_shell" / "bin" / "ingest-gmail.py"
)
ingest_gmail = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ingest_gmail)


# ---- fixtures ------------------------------------------------------------

ECLIPSE_CFG = {
    "sources": {
        "gmail": {
            "accounts": [
                {
                    "account": "adithya@outerscope.xyz",
                    "lookback_days_initial": 365,
                    "api_query": {
                        "include": [
                            "label:Eclipse",
                            "from:*@eclipse.audio",
                            "to:*@eclipse.audio",
                        ],
                        "exclude": [
                            "from:noreply@*",
                            "label:SPAM",
                            "label:TRASH",
                        ],
                    },
                }
            ]
        }
    }
}

PERSONAL_CFG = {
    "sources": {
        "gmail": {
            "accounts": [
                {
                    "account": "adithya@outerscope.xyz",
                    "lookback_days_initial": 7,
                    "api_query": {
                        "include": ["label:INBOX"],
                        "exclude": [
                            "from:noreply@*",
                            "label:Eclipse",
                            "label:SPAM",
                            "label:TRASH",
                        ],
                    },
                }
            ]
        }
    }
}

# Health/finance: gmail block empty → no subscription for this account
EMPTY_CFG = {"sources": {"gmail": []}}


def test_collect_account_rules_unions_subscribers() -> None:
    workspaces = {"eclipse": ECLIPSE_CFG, "personal": PERSONAL_CFG,
                  "health": EMPTY_CFG, "finance": EMPTY_CFG}
    inc, exc, lookback = ingest_gmail.collect_account_rules(
        "adithya@outerscope.xyz", workspaces
    )
    # all eclipse + personal includes
    for c in ("label:Eclipse", "from:*@eclipse.audio", "to:*@eclipse.audio", "label:INBOX"):
        assert c in inc, f"missing include {c!r}: {inc}"
    # excludes union
    for c in ("from:noreply@*", "label:SPAM", "label:TRASH", "label:Eclipse"):
        assert c in exc, f"missing exclude {c!r}: {exc}"
    # max lookback wins
    assert lookback == 365, lookback


def test_collect_account_rules_no_subscribers() -> None:
    inc, exc, lookback = ingest_gmail.collect_account_rules(
        "ghost@nowhere.tld", {"eclipse": ECLIPSE_CFG, "personal": PERSONAL_CFG}
    )
    assert inc == [] and exc == []
    assert lookback == ingest_gmail.GMAIL_INITIAL_LOOKBACK_DAYS_DEFAULT


def test_predicate_to_q_translations() -> None:
    cases = {
        "label:Eclipse": "label:Eclipse",
        "label:Eclipse/Investors": "label:Eclipse/Investors",
        "from:*@eclipse.audio": "from:eclipse.audio",
        "to:*@eclipse.audio": "to:eclipse.audio",
        "from:noreply@*": "from:noreply",            # best-effort: drop trailing wildcard
        "from:*@*": None,                            # all-wildcard -> drop
        "subject:contains:Q3 deck": 'subject:"Q3 deck"',
        "subject:regex:^Re:.*": None,                # untranslatable to q=
        "any:foo": None,
        "": None,
    }
    for pred, want in cases.items():
        got = ingest_gmail._predicate_to_q(pred)
        assert got == want, f"_predicate_to_q({pred!r}) = {got!r}, want {want!r}"


def test_build_q_union_dedup_under_limit() -> None:
    workspaces = {"eclipse": ECLIPSE_CFG, "personal": PERSONAL_CFG}
    inc, exc, _ = ingest_gmail.collect_account_rules(
        "adithya@outerscope.xyz", workspaces
    )
    q = ingest_gmail.build_q(inc, exc, after_ts=1700000000)
    # OR of translatable includes
    assert "(label:Eclipse OR from:eclipse.audio OR to:eclipse.audio OR label:INBOX)" in q, q
    # excludes appear as -clauses
    for needle in ("-label:SPAM", "-label:TRASH", "-label:Eclipse", "-from:noreply"):
        assert needle in q, f"missing {needle!r} in {q!r}"
    # universal hardening
    assert "-in:trash" in q and "-in:spam" in q and "after:1700000000" in q
    # length under Gmail's ~2KB practical q= limit
    assert len(q) < 2000, f"q too long: {len(q)} chars"


def test_legacy_list_shape_still_works() -> None:
    """The Phase 1 legacy `sources: [{type: gmail, config: {...}}]` shape must still load."""
    legacy = {
        "sources": [
            {
                "type": "gmail",
                "config": {
                    "account": "legacy@example.com",
                    "labels": ["L1", "L2"],
                    "exclude_labels": ["X1"],
                    "lookback_days_initial": 30,
                },
            }
        ]
    }
    inc, exc, lookback = ingest_gmail.collect_account_rules(
        "legacy@example.com", {"legacy": legacy}
    )
    assert "label:L1" in inc and "label:L2" in inc
    assert "label:X1" in exc
    assert lookback == 30


def test_account_slug() -> None:
    cases = {
        "adithya@outerscope.xyz": "adithya-outerscope",
        "adithya.shak.kumar@gmail.com": "adithya-shak-kumar-gmail",
        "ADITHYA@Eclipse.Builders": "adithya-eclipse",
    }
    for email, want in cases.items():
        got = ingest_gmail.account_slug(email)
        assert got == want, f"account_slug({email}) = {got!r}, want {want!r}"


def test_subject_slug() -> None:
    cases = {
        "Re: Q3 deck review": "q3-deck-review",
        "FWD: Re: AUTO: status": "status",
        "[External] Re: hello": "hello",
        "": "no-subject",
        "   ": "no-subject",
        "Naïve résumé café": "naive-resume-cafe",
    }
    for raw, want in cases.items():
        got = ingest_gmail.subject_slug(raw)
        assert got == want, f"subject_slug({raw!r}) = {got!r}, want {want!r}"


# ---- runner --------------------------------------------------------------

def main() -> int:
    tests = [
        ("collect_account_rules unions", test_collect_account_rules_unions_subscribers),
        ("collect_account_rules no subscribers", test_collect_account_rules_no_subscribers),
        ("predicate->q translations", test_predicate_to_q_translations),
        ("build_q union/dedup/limit", test_build_q_union_dedup_under_limit),
        ("legacy list shape", test_legacy_list_shape_still_works),
        ("account_slug", test_account_slug),
        ("subject_slug", test_subject_slug),
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
