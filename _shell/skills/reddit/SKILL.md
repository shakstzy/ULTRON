---
name: reddit
description: Use this skill EVERY time you need to read Reddit content (search posts, browse a subreddit's hot/new/top/controversial/rising, fetch a post + comment thread, look up a user's activity, or check a subreddit's metadata). Trigger on phrases like "what's on r/X", "search reddit for X", "top posts in r/X", "summarize this reddit thread", "is r/X active", "what's u/X been posting", or any URL containing `reddit.com/r/.../comments/`. Stdlib Python CLI hitting Reddit's `*.json` endpoints — terse markdown output, zero context cost until triggered. Always use this skill — never reach for firecrawl or brave-search to read Reddit.
---

# reddit

Single-file Python script under `scripts/reddit.py`. Stdlib only, no PRAW. Hits Reddit's JSON endpoints. Default output is compact markdown; `--json` returns cleaned structured data.

**Why this skill exists:** native HTTP beats firecrawl/brave-search for site-specific reads. The wrapper itself never loads into context — only this SKILL.md does, and only when a trigger fires.

## When this fires

Trigger phrases (semantic, non-exhaustive): "what's on r/X", "search reddit for X", "top posts in r/X this week", "what does r/X say about Y", "summarize this reddit thread", "find reddit threads about X", "what's u/X been posting", "is r/X still active", any `reddit.com/r/.../comments/...` URL.

Do NOT fire for:
- Posting / voting / replying — read-only, no write support.
- Private / quarantined subs — public API returns 403 without OAuth.
- Bulk media downloads — out of scope.

## Auth

**Default:** anonymous, no auth. Reddit rate-limits unauth'd reads to ~10 req/min per IP. Script auto-retries 429s twice (respects `Retry-After` header), then surfaces.

**Optional OAuth (6x rate limit):** set `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` in env (`.claude/settings.local.json`). Script switches to `oauth.reddit.com` via `client_credentials` grant, lifting cap to ~60 req/min. Token cached at `~/.cache/reddit-cli/token.json` (mode 0600). To get creds: https://www.reddit.com/prefs/apps → "create app" → script type → grab client_id (top of card) and secret. Read-only, no user account access.

## Procedure

Invoke the script directly (works from any cwd):

```bash
~/ULTRON/_shell/skills/reddit/scripts/reddit.py <subcommand> [args]
```

Subcommands:

```bash
# Search (cross-sub or scoped)
reddit.py search "<query>" [--sub SUB] [--limit N=10] \
  [--time hour|day|week|month|year|all] [--sort relevance|hot|top|new|comments]

# Listings (sort orders)
reddit.py hot <subreddit> [--limit N=10]
reddit.py new <subreddit> [--limit N=10]
reddit.py top <subreddit> [--time hour|day|week|month|year|all=day] [--limit N=10]
reddit.py controversial <subreddit> [--time ...=day] [--limit N=10]
reddit.py rising <subreddit> [--limit N=10]

# Single post + comment thread
reddit.py post <id|url> [--top N=10] [--depth D=2] [--links]
#   id can be a bare ID (1sxmg6z), a full URL, or /r/.../comments/ID/...
#   --links extracts external URLs from shown comments (deduped, reddit-internal filtered)

# User activity
reddit.py user <username> [--kind submitted|comments] [--limit N=10]

# Subreddit metadata (about page)
reddit.py info <subreddit>
#   subscribers, online count, age, type (public/private/restricted), NSFW, description
```

Global flags (work before OR after the subcommand):
- `--json` — raw cleaned JSON instead of markdown
- `--ua "<string>"` — override User-Agent (default fine for read-only)

## Output shape

Markdown (default): post header line `r/sub · u/author · score↑ · Nc · age · [flair]`, then `id` + permalink, then external link if any, then a 400-char selftext snippet. Comments are nested with `**u/author** (score↑): body` indented by depth.

JSON: array of post dicts (or `{post, comments}` for the post subcommand). All raw_json=1 (HTML entities decoded).

## Examples

```bash
# What's hot in r/LocalLLaMA right now
~/ULTRON/_shell/skills/reddit/scripts/reddit.py hot LocalLLaMA --limit 5

# Recent discussion of a topic
~/ULTRON/_shell/skills/reddit/scripts/reddit.py search "claude opus 4.7" --time week --limit 10

# Read a thread someone shared, with link extraction
~/ULTRON/_shell/skills/reddit/scripts/reddit.py post "https://www.reddit.com/r/Python/comments/1sxmg6z/" --top 15 --depth 2 --links

# Subreddit metadata before joining a discussion
~/ULTRON/_shell/skills/reddit/scripts/reddit.py info ClaudeAI

# Quick scan of one user
~/ULTRON/_shell/skills/reddit/scripts/reddit.py user spez --kind submitted --limit 5
```

## Budget

- Default cap: 5 calls per task. Each call = one Reddit listing or thread. Confirm before going higher.
- Anonymous limit ~10 req/min; with OAuth env vars set, ~60 req/min. Don't fan out across many subs without asking.
- For deep comment trees, prefer increasing `--depth` over re-calling — one fetch with `--depth 4` is cheaper than 4 nested fetches.

## Ingest standard (saving threads to raw/)

For archiving a Reddit thread under a workspace's `raw/` so it can be referenced later, graphified, or summarized:

```bash
reddit.py post <id|url> --save <workspace> [--top 50] [--depth 6]
```

This is the ONE supported save path. There is no separate ingest CLI — the `--save` flag IS the standard.

**File path:** `~/ULTRON/workspaces/<ws>/raw/reddit/<subreddit>/<YYYY-MM-DD>__<post_id>__<title-slug>.md`
- Date is the post's `created_utc`, not when you ran the command. Makes files sort chronologically by Reddit-time.
- `<title-slug>` is lowercased, alphanum + hyphens, capped at 60 chars.
- Workspace must already exist under `workspaces/`. Valid: `personal`, `eclipse`, `finance`, `health`, `seedbox`, `synapse` (script errors if not found).

**Frontmatter (canonical fields, in order):**
```yaml
source: reddit
workspace: <ws>
ingested_at: <ISO 8601 UTC>          # when the file was written
ingest_version: 1
content_hash: sha256:<hex>           # of the rendered body, lets you detect drift on re-ingest
provider_modified_at: <ISO 8601 UTC> # post's created_utc, parity with gmail's provider_modified_at
post_id: <reddit id>
permalink: https://reddit.com/<perm>
url: <external link if non-self post, else null>
subreddit: <sub>
author: u/<...>
title: "<title>"
flair: <flair or null>
score: <int>
num_comments: <int>
upvote_ratio: <float>
nsfw: <bool>
spoiler: <bool>
locked: <bool>
top_comments_captured: <actual N captured, may be < --top if thread was small>
max_depth_captured: <D from --depth>
```

**Body shape (deterministic, recreate-able from data):**
```markdown
# <title>

> r/<sub> · u/<author> · <score>↑ · <num_comments>c · <ago> · [<flair>]
> <permalink>
> external: <url>             # only present if external link

## Selftext                    # only present if selftext non-empty

<full selftext, no truncation>

## Top <N> comments (depth <D>)

- **u/foo** (123↑): <full body, multi-line preserved with indent>
  - **u/bar** (45↑): <full reply>

## External links cited in comments   # only present if any non-reddit links found

- <url>
- <url>
```

**Key rules:**
1. Full bodies, no truncation (this is an archive, not a summary).
2. `[deleted]` / `[removed]` comments dropped silently.
3. "More comments" placeholders skipped (would need OAuth + morechildren; not worth the dep).
4. Re-running on the same post overwrites the file. Use `content_hash` to detect drift if you cared about diffs.
5. Default `--save` triggers wider capture: bump `--top` to 50 and `--depth` to 6 explicitly. (No automatic boost — caller's choice, keeps the flag honest.)
6. ONLY ingest on explicit user intent ("save this thread", "archive this", "ingest to <ws>"). Don't auto-save on every read.

## Notes

- API base: anonymous = `https://www.reddit.com<path>.json`; OAuth = `https://oauth.reddit.com<path>` (no .json suffix).
- "[deleted]" / "[removed]" comments are filtered out of markdown output.
- "more comments" placeholders are skipped. Expanding them needs OAuth + the morechildren endpoint, out of scope.
- Quarantined subs return 403; locked threads are still readable. NSFW subs work but content not filtered.
- Pairs naturally with `firecrawl` only for external links cited in threads (not for Reddit itself).

## Self-review checklist

Before declaring a Reddit-read task done:

1. Did the trigger genuinely require Reddit data, or could it have been answered from loaded context?
2. Did the call respect the 5-calls-per-task budget? If you went higher, did you check in first?
3. If 429 fired, did you back off (script auto-retries) or fan out anyway?
4. For long threads, did you summarize first and only paste the full output if explicitly asked?
5. Did any external URLs from the thread get followed via `firecrawl` only when the user asked, not automatically?
