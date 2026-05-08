#!/usr/bin/env python3
"""
Generate voice_profile + conversation_summary on each entity stub from iMessage history.

Reads:
  workspaces/personal/raw/imessage/individuals/<imsg-slug>/YYYY/*.md
  workspaces/personal/raw/imessage/_profiles/<imsg-slug>.md  (handle → entity match)
  _global/entities/people/<entity-slug>.md                    (target stub)

Writes (atomically) into the entity stub frontmatter:
  voice_profile:        — 200-400 token tone/register/abbreviation profile
  conversation_summary: — 300-500 token rolling summary of the relationship + recent topics
  voice_synthesized_at: — ISO timestamp

Skips contacts whose newest raw shard is older than the existing voice_synthesized_at,
so re-runs are cheap deltas. Caps per-run via --limit (default 20) to avoid quota
exhaustion. Single cloud-llm call per contact.

Usage:
  synthesize-voice-profiles.py                      # auto-pick stale, cap 20
  synthesize-voice-profiles.py --slug mom           # one entity slug
  synthesize-voice-profiles.py --limit 5            # cap at 5
  synthesize-voice-profiles.py --dry-run            # list targets + counts, no calls
  synthesize-voice-profiles.py --force --slug mom   # ignore freshness check
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

import yaml

ULTRON = Path(__file__).resolve().parents[2]
PEOPLE_DIR = ULTRON / "_global" / "entities" / "people"
RAW_INDIVIDUALS = ULTRON / "workspaces" / "personal" / "raw" / "imessage" / "individuals"
PROFILES_DIR = ULTRON / "workspaces" / "personal" / "raw" / "imessage" / "_profiles"
SHELL_SKILLS = ULTRON / "_shell" / "skills"

sys.path.insert(0, str(SHELL_SKILLS / "cloud-llm"))
from client import ask_text, CloudLLMUnreachable  # noqa: E402

MAX_INPUT_CHARS = 60_000  # ~15k tokens; biased to most recent shards


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm = yaml.safe_load(text[4:end]) or {}
    body = text[end + 5 :]
    return fm, body


def write_frontmatter(path: Path, fm: dict, body: str) -> None:
    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=10_000)
    path.write_text(f"---\n{fm_text}---\n{body}")


def index_imessage_to_entity() -> dict[str, str]:
    """Map imessage profile slug → entity slug by matching phone tails / emails.

    Returns: {imessage_slug: entity_slug}
    """
    if not PROFILES_DIR.is_dir():
        return {}
    handle_to_entity: dict[str, str] = {}
    for stub in PEOPLE_DIR.glob("*.md"):
        fm, _ = parse_frontmatter(stub)
        ids = fm.get("identifiers") or {}
        for ph in ids.get("phone") or []:
            tail = "".join(c for c in ph if c.isdigit())[-10:]
            if tail:
                handle_to_entity[tail] = stub.stem
        for em in ids.get("email") or []:
            handle_to_entity[em.lower()] = stub.stem
    mapping: dict[str, str] = {}
    for prof in PROFILES_DIR.glob("*.md"):
        pfm, _ = parse_frontmatter(prof)
        for h in pfm.get("contact_handles") or []:
            key = h.lower() if "@" in h else "".join(c for c in h if c.isdigit())[-10:]
            if key in handle_to_entity:
                mapping[prof.stem] = handle_to_entity[key]
                break
    return mapping


def newest_shard_mtime(imsg_dir: Path) -> datetime.datetime | None:
    latest: float = 0.0
    for f in imsg_dir.rglob("*.md"):
        latest = max(latest, f.stat().st_mtime)
    if latest == 0.0:
        return None
    return datetime.datetime.fromtimestamp(latest, tz=datetime.timezone.utc)


def load_recent_messages(imsg_dir: Path) -> str:
    shards = sorted(imsg_dir.rglob("*.md"))
    if not shards:
        return ""
    chunks: list[str] = []
    total = 0
    for shard in reversed(shards):
        text = shard.read_text()
        _, body = parse_frontmatter(shard)
        chunks.append(f"\n\n=== {shard.relative_to(imsg_dir)} ===\n{body}")
        total += len(body)
        if total >= MAX_INPUT_CHARS:
            break
    return "".join(reversed(chunks))[-MAX_INPUT_CHARS:]


SYNTH_PROMPT = """You are profiling how the user (Adithya) communicates with one specific contact based on their iMessage history below. Output STRICT JSON with exactly these two keys, nothing else:

{
  "voice_profile": "...",
  "conversation_summary": "..."
}

`voice_profile` (target 200-300 tokens): how Adithya talks TO this contact specifically. Tone register (jokey/casual/formal/curt/affectionate). Vocabulary patterns. Slang, abbreviations, profanity habits. Emoji usage. Typical message length. Greeting and sign-off patterns. Reply latency vibes if visible. Anything distinctive. Concrete observations only — quote 2-3 short lines as examples.

`conversation_summary` (target 300-500 tokens): the relationship and recent topics. Who is this person to Adithya. Recurring themes. What they've talked about in the last few months. Open threads, plans, ongoing topics. Inside references that would help compose a future message in voice. Don't include sensitive specifics that aren't load-bearing for tone.

Output ONLY the JSON. No markdown fences, no preamble.

iMessage history (most recent shards last):

"""


def synthesize_one(imsg_slug: str, entity_slug: str, dry_run: bool) -> dict:
    imsg_dir = RAW_INDIVIDUALS / imsg_slug
    stub_path = PEOPLE_DIR / f"{entity_slug}.md"
    if not stub_path.exists():
        return {"slug": entity_slug, "status": "missing-stub"}
    history = load_recent_messages(imsg_dir)
    if not history.strip():
        return {"slug": entity_slug, "status": "no-messages"}
    if dry_run:
        return {"slug": entity_slug, "status": "would-synthesize", "input_chars": len(history)}

    prompt = SYNTH_PROMPT + history
    try:
        result = ask_text(prompt)
    except CloudLLMUnreachable as e:
        return {"slug": entity_slug, "status": "cloud-unreachable", "error": str(e)[:300]}

    raw = result.get("output", "").strip()
    # Strip ``` fences if model decorated despite instructions
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"slug": entity_slug, "status": "bad-json", "raw_head": raw[:300]}

    fm, body = parse_frontmatter(stub_path)
    fm["voice_profile"] = parsed.get("voice_profile", "").strip()
    fm["conversation_summary"] = parsed.get("conversation_summary", "").strip()
    fm["voice_synthesized_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    fm["voice_synthesized_engine"] = result.get("engine")
    write_frontmatter(stub_path, fm, body)
    return {
        "slug": entity_slug,
        "status": "ok",
        "engine": result.get("engine"),
        "input_chars": len(history),
    }


def pick_targets(mapping: dict[str, str], force: bool) -> list[tuple[str, str]]:
    targets: list[tuple[str, str]] = []
    for imsg_slug, entity_slug in sorted(mapping.items()):
        imsg_dir = RAW_INDIVIDUALS / imsg_slug
        if not imsg_dir.is_dir():
            continue
        newest = newest_shard_mtime(imsg_dir)
        if newest is None:
            continue
        stub_path = PEOPLE_DIR / f"{entity_slug}.md"
        if not stub_path.exists():
            continue
        if not force:
            fm, _ = parse_frontmatter(stub_path)
            last = fm.get("voice_synthesized_at")
            if last:
                try:
                    last_dt = datetime.datetime.fromisoformat(last.replace("Z", "+00:00"))
                    if newest <= last_dt:
                        continue
                except Exception:
                    pass
        targets.append((imsg_slug, entity_slug))
    return targets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", help="single entity slug (e.g. 'mom') — bypasses freshness check")
    ap.add_argument("--limit", type=int, default=20, help="max contacts per run (default 20)")
    ap.add_argument("--dry-run", action="store_true", help="list targets + input sizes; no cloud calls")
    ap.add_argument("--force", action="store_true", help="re-synthesize even if stub is fresh")
    args = ap.parse_args()

    mapping = index_imessage_to_entity()
    if args.slug:
        rev = {ent: imsg for imsg, ent in mapping.items()}
        if args.slug not in rev:
            print(f"error: no imessage profile maps to entity slug '{args.slug}'", file=sys.stderr)
            return 2
        targets = [(rev[args.slug], args.slug)]
    else:
        targets = pick_targets(mapping, force=args.force)[: args.limit]

    if not targets:
        print("no targets need refresh")
        return 0

    print(f"# {len(targets)} target(s){' (dry-run)' if args.dry_run else ''}")
    for imsg_slug, entity_slug in targets:
        result = synthesize_one(imsg_slug, entity_slug, dry_run=args.dry_run)
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
