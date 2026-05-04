"""
gmail/route.py — given a fetched Gmail thread + the parsed sources.yaml of
every workspace, decide which workspace(s) get a copy.

Public API:
    route(thread, workspaces_config) -> list[{workspace, rule}]

`thread` is a Gmail API thread payload normalized to the helpers below.
`workspaces_config` is {ws_slug: parsed_sources_yaml}.

Routing semantics:
  - For each workspace's `sources.gmail` block: evaluate include rules and
    exclude rules against the thread. A workspace matches when at least
    one include rule fires AND no exclude rule fires.
  - Empty include set → match-all (subject to excludes), reported as
    rule="<match-all>".
  - If the thread matches no workspace, return the unrouted default
    (`route_to_main` → fallback to main / personal workspace, reported as
    rule="<unrouted-default>"; `skip` → []).
  - `also_route_to` extras append additional workspaces.
  - Return list of {workspace, rule} dicts, sorted by workspace.

Rule grammar:
  A rule string is a Gmail-q=-style space-separated AND of clauses. Each
  clause is `[<-prefix>]predicate`. The rule fires iff every positive clause
  matches AND no negated clause matches.

  Predicates:
    label:<exact>
    from:<glob-or-domain>     to:/cc:/any: same shape
    subject:"<phrase>"        contains, case-insensitive
    subject:<text>            contains, case-insensitive
    subject:contains:<text>   contains, case-insensitive (legacy)
    subject:regex:<pattern>   regex

  `from:<bare-domain>` (no @, no *) matches any email at that domain or any
  subdomain (Gmail q=-like). Otherwise fnmatch on the full email.

Account-level shared excludes:
  An account block may set `api_query.exclude_from: <relative-path>` (or a
  list of paths) pointing at a YAML file with a top-level `excludes:` list
  of rule strings. Loaded once per path (LRU-cached), unioned with inline
  `api_query.exclude` rules. Path is resolved relative to ULTRON_ROOT.
"""
from __future__ import annotations

import fnmatch
import functools
import os
import re
import shlex
from pathlib import Path
from typing import Iterable

import yaml

SOURCE_NAME = "gmail"
DEFAULT_UNROUTED = "route_to_main"
MAIN_WS_FALLBACK = ("main", "personal")
MATCH_ALL_RULE = "<match-all>"
UNROUTED_RULE = "<unrouted-default>"


def _ultron_root() -> Path:
    return Path(os.environ.get("ULTRON_ROOT") or (Path.home() / "ULTRON"))


def _resolve_exclude_path(rel: str) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else _ultron_root() / rel


@functools.lru_cache(maxsize=64)
def _load_exclude_file(abs_path: str) -> tuple[str, ...]:
    p = Path(abs_path)
    if not p.exists():
        return ()
    try:
        data = yaml.safe_load(p.read_text()) or {}
    except (yaml.YAMLError, OSError):
        return ()
    rules = data.get("excludes") if isinstance(data, dict) else None
    if not isinstance(rules, list):
        return ()
    return tuple(r for r in rules if isinstance(r, str) and r.strip())


def _excludes_from_field(value) -> list[str]:
    paths: list[str] = []
    if isinstance(value, str):
        paths.append(value)
    elif isinstance(value, list):
        paths.extend(p for p in value if isinstance(p, str))
    out: list[str] = []
    for path in paths:
        out.extend(_load_exclude_file(str(_resolve_exclude_path(path))))
    return out


def _participant_matches(thread: dict, predicate: str) -> bool:
    """`from:foo@*`, `to:*@eclipse.audio`, `from:domain.com` (bare domain)."""
    if ":" not in predicate:
        return False
    role, pat = predicate.split(":", 1)
    role = role.strip().lower()
    pat = pat.strip().lower()
    if role not in {"from", "to", "cc", "any"}:
        return False
    bare_domain = pat and "@" not in pat and "*" not in pat
    for p in thread.get("participants", []):
        roles = {r.lower() for r in p.get("roles", [])}
        email = (p.get("email") or "").lower()
        if role != "any" and role not in roles:
            continue
        if bare_domain:
            _, _, dom = email.partition("@")
            if dom == pat or dom.endswith("." + pat):
                return True
        else:
            if fnmatch.fnmatch(email, pat):
                return True
    return False


def _label_matches(thread: dict, predicate: str) -> bool:
    if not predicate.lower().startswith("label:"):
        return False
    target = predicate.split(":", 1)[1].strip()
    return any(label == target for label in thread.get("labels", []))


def _subject_matches(thread: dict, predicate: str) -> bool:
    """`subject:"<phrase>"`, `subject:<text>`, `subject:contains:<text>`,
    or `subject:regex:<pattern>`. Quoted/bare forms are case-insensitive
    contains."""
    if not predicate.lower().startswith("subject:"):
        return False
    rest = predicate[len("subject:"):]
    subject = thread.get("subject") or ""
    if rest.startswith('"') and rest.endswith('"') and len(rest) >= 2:
        return rest[1:-1].lower() in subject.lower()
    lower = rest.lower()
    if lower.startswith("contains:"):
        return rest[len("contains:"):].lower() in subject.lower()
    if lower.startswith("regex:"):
        try:
            return re.search(rest[len("regex:"):], subject) is not None
        except re.error:
            return False
    return bool(rest) and rest.lower() in subject.lower()


def _evaluate_predicate(thread: dict, predicate: str) -> bool:
    predicate = predicate.strip()
    if not predicate:
        return False
    if predicate.startswith("label:"):
        return _label_matches(thread, predicate)
    if predicate.startswith(("from:", "to:", "cc:", "any:")):
        return _participant_matches(thread, predicate)
    if predicate.startswith("subject:"):
        return _subject_matches(thread, predicate)
    return False


def _tokenize_rule(rule: str) -> list[tuple[bool, str]]:
    """Split a compound rule into (negated, predicate) tokens. Quoted
    phrases are preserved as single tokens and re-quoted so downstream
    matchers see `subject:"X"` intact.

    Raises ValueError on orphan tokens (no `:`). Silent drop is unsafe:
    `subject:Out of Office` would shlex-split to ['subject:Out', 'of',
    'Office'] and degrade to `subject:"Out"`, matching anything containing
    "Out". Multi-word subjects must be quoted: `subject:"Out of Office"`.
    """
    try:
        lex = shlex.shlex(rule, posix=True)
        lex.whitespace_split = True
        lex.commenters = ""
        raw_tokens = list(lex)
    except ValueError as exc:
        raise ValueError(f"invalid rule {rule!r}: lex error ({exc})")
    out: list[tuple[bool, str]] = []
    for tok in raw_tokens:
        negated = False
        if tok.startswith("-") and len(tok) > 1 and ":" in tok[1:]:
            negated = True
            tok = tok[1:]
        if ":" not in tok:
            raise ValueError(
                f"invalid rule {rule!r}: orphan token {tok!r} has no predicate. "
                f"Quote multi-word subject phrases: subject:\"text with spaces\"."
            )
        head, _, tail = tok.partition(":")
        if head.lower() == "subject" and tail and not tail.startswith('"') \
                and tail.lower() not in ("contains", "regex") \
                and not tail.lower().startswith(("contains:", "regex:")):
            tok = f'subject:"{tail}"'
        out.append((negated, tok))
    return out


def _evaluate_rule(thread: dict, rule: str) -> bool:
    rule = rule.strip()
    if not rule:
        return False
    tokens = _tokenize_rule(rule)
    if not tokens:
        return False
    for negated, pred in tokens:
        matches = _evaluate_predicate(thread, pred)
        if negated and matches:
            return False
        if not negated and not matches:
            return False
    return True


def _first_matching_rule(thread: dict, rules: Iterable[str]) -> str | None:
    """Return the first rule that fires, MATCH_ALL_RULE for empty include set,
    or None if no include rule fires."""
    rules = list(rules or [])
    if not rules:
        return MATCH_ALL_RULE
    for r in rules:
        if _evaluate_rule(thread, r):
            return r
    return None


def _evaluate_excludes(thread: dict, rules: Iterable[str]) -> bool:
    return any(_evaluate_rule(thread, r) for r in (rules or []))


def _gmail_block(ws_cfg: dict) -> dict | None:
    sources = (ws_cfg or {}).get("sources")
    if isinstance(sources, dict):
        return sources.get(SOURCE_NAME)
    if isinstance(sources, list):
        for s in sources:
            if s.get("type") == SOURCE_NAME:
                return s.get("config") or s
    return None


def _main_workspace(workspaces_config: dict) -> str | None:
    for cand in MAIN_WS_FALLBACK:
        if cand in workspaces_config:
            return cand
    return None


def _unrouted_default_for(ws_cfg: dict) -> str:
    """Workspace CLAUDE.md frontmatter may specify ingest_unrouted_default."""
    meta = (ws_cfg or {}).get("_workspace_meta", {}) or {}
    return meta.get("ingest_unrouted_default") or DEFAULT_UNROUTED


def validate_workspaces_config(workspaces_config: dict) -> list[str]:
    """Run every include + exclude (inline + exclude_from) through the
    tokenizer once. Returns a list of human-readable error strings; empty
    list means valid. Catches typos and unquoted multi-word subjects up
    front so a bad rule cannot abort an in-progress run halfway through
    the thread loop, after Gmail fetches and partial writes have happened.
    """
    errors: list[str] = []

    def _check_list(ws: str, where: str, rules) -> list:
        # Bare strings would be iterated character-by-character ("subject:Bug"
        # → 's','u','b',...) by route()'s comprehension, silently turning a
        # config typo into "matches nothing." Reject up front.
        if rules is None:
            return []
        if isinstance(rules, str):
            errors.append(
                f"workspace={ws} {where}: must be a list, got str ({rules!r}). "
                f"Wrap single rules in a list: [{rules!r}]."
            )
            return []
        if not isinstance(rules, list):
            errors.append(f"workspace={ws} {where}: must be a list, got {type(rules).__name__}.")
            return []
        return rules

    def _check(ws: str, where: str, rule: str) -> None:
        if not isinstance(rule, str) or not rule.strip():
            return
        rule_str = rule if ":" in rule else f"label:{rule}"
        try:
            _tokenize_rule(rule_str)
        except ValueError as exc:
            errors.append(f"workspace={ws} {where} rule={rule!r}: {exc}")

    for ws, cfg in workspaces_config.items():
        block = _gmail_block(cfg)
        if not block:
            continue
        accounts = block.get("accounts") if isinstance(block, dict) else None
        if isinstance(accounts, list):
            block_api = block.get("api_query") or {}
            block_inc = _check_list(ws, "block include", block_api.get("include")) or _check_list(ws, "block labels", block.get("labels"))
            block_exc = _check_list(ws, "block exclude", block_api.get("exclude")) or _check_list(ws, "block exclude_labels", block.get("exclude_labels"))
            block_excf = _excludes_from_field(block_api.get("exclude_from"))
            for a in accounts:
                if isinstance(a, str):
                    # String-form accounts inherit the block-level api_query
                    # at runtime (see route() normalization). Validate those
                    # block-level rules under this account's label so a typo
                    # surfaces with context, not as a mid-run ValueError.
                    for r in block_inc:
                        _check(ws, f"account={a} include (block)", r)
                    for r in block_exc:
                        _check(ws, f"account={a} exclude (block)", r)
                    for r in block_excf:
                        _check(ws, f"account={a} exclude_from (block)", r)
                    continue
                if not isinstance(a, dict):
                    continue
                api = a.get("api_query") or {}
                acct_label = a.get("account") or "<unknown>"
                for r in _check_list(ws, f"account={acct_label} include", api.get("include")):
                    _check(ws, f"account={acct_label} include", r)
                for r in _check_list(ws, f"account={acct_label} exclude", api.get("exclude")):
                    _check(ws, f"account={acct_label} exclude", r)
                for r in _excludes_from_field(api.get("exclude_from")):
                    _check(ws, f"account={acct_label} exclude_from", r)
            continue
        api = block.get("api_query", {}) or {}
        for r in (_check_list(ws, "include (legacy)", api.get("include"))
                  or _check_list(ws, "labels (legacy)", block.get("labels"))):
            _check(ws, "include (legacy)", r)
        for r in (_check_list(ws, "exclude (legacy)", api.get("exclude"))
                  or _check_list(ws, "exclude_labels (legacy)", block.get("exclude_labels"))):
            _check(ws, "exclude (legacy)", r)
        for r in _excludes_from_field(api.get("exclude_from")):
            _check(ws, "exclude_from (legacy)", r)
    return errors


def route(thread: dict, workspaces_config: dict) -> list[dict]:
    """Returns list of {workspace, rule} entries, sorted by workspace.

    If an explicit account subscription matched (include fired) but its
    excludes vetoed the thread, the unrouted-default fallback is suppressed
    — the exclude is the user's intentional drop, not an "uncategorized"
    signal. Without this, account-level exclude lists (e.g. shared
    cold-pitch noise files) would all silently land back in the main
    workspace under <unrouted-default>.
    """
    matched: dict[str, str] = {}
    extras: dict[str, str] = {}
    explicit_reject = False

    for ws, cfg in workspaces_config.items():
        block = _gmail_block(cfg)
        if not block:
            continue

        # Preferred shape: accounts: [{account, api_query, rules}].
        accounts = block.get("accounts") if isinstance(block, dict) else None
        if isinstance(accounts, list):
            normalized: list[dict] = []
            for a in accounts:
                if isinstance(a, str):
                    block_api = block.get("api_query") or {}
                    normalized.append({
                        "account": a,
                        "api_query": {
                            "include": block_api.get("include") or block.get("labels") or [],
                            "exclude": block_api.get("exclude") or block.get("exclude_labels") or [],
                            # exclude_from was dropped here previously, so any
                            # workspace using string-form accounts + a shared
                            # exclude file (e.g., the synps cold-pitch list)
                            # silently lost the file's rules at runtime.
                            "exclude_from": block_api.get("exclude_from"),
                        },
                    })
                elif isinstance(a, dict):
                    normalized.append(a)
            for acct in normalized:
                if acct.get("account") and thread.get("account") and acct["account"] != thread["account"]:
                    continue
                api = acct.get("api_query", {}) or {}
                inc = api.get("include") or []
                exc = list(api.get("exclude") or [])
                exc.extend(_excludes_from_field(api.get("exclude_from")))
                inc_rules = [r if isinstance(r, str) and ":" in r else f"label:{r}" for r in inc]
                exc_rules = [r if isinstance(r, str) and ":" in r else f"label:{r}" for r in exc]
                fired = _first_matching_rule(thread, inc_rules)
                if fired:
                    if _evaluate_excludes(thread, exc_rules):
                        explicit_reject = True
                    else:
                        matched[ws] = fired
                        for rule in acct.get("rules", []) or []:
                            also = rule.get("also_route_to") or []
                            for target in also:
                                if target in workspaces_config:
                                    extras[target] = f"also_route_to-from-{ws}"
            continue

        # Legacy flat shape.
        # The block IS the gmail config dict (per _gmail_block), so the
        # account field lives directly on it. Without this filter, a
        # legacy-shape workspace's rules would evaluate against threads
        # from every other ingested account, silently routing mail into
        # the wrong workspace.
        legacy_account = block.get("account")
        if legacy_account and thread.get("account") and legacy_account != thread["account"]:
            continue
        api = block.get("api_query", {}) or {}
        include = api.get("include") or block.get("labels") or []
        exclude = list(api.get("exclude") or block.get("exclude_labels") or [])
        exclude.extend(_excludes_from_field(api.get("exclude_from")))
        include_rules = [r if isinstance(r, str) and ":" in r else f"label:{r}" for r in include]
        exclude_rules = [r if isinstance(r, str) and ":" in r else f"label:{r}" for r in exclude]
        fired = _first_matching_rule(thread, include_rules)
        if fired:
            if _evaluate_excludes(thread, exclude_rules):
                explicit_reject = True
            else:
                matched[ws] = fired

    if not matched:
        if explicit_reject:
            return []
        # Per-workspace eval, not pooled. A non-main workspace declaring
        # `ingest_unrouted_default: skip` must NOT veto the main fallback.
        main = _main_workspace(workspaces_config)
        if main is not None:
            main_default = _unrouted_default_for(workspaces_config.get(main, {}))
            if main_default == "skip":
                return []
            matched[main] = UNROUTED_RULE

    # Extras shouldn't overwrite explicit matches.
    for ws, rule in extras.items():
        matched.setdefault(ws, rule)
    return [{"workspace": ws, "rule": rule} for ws, rule in sorted(matched.items())]
