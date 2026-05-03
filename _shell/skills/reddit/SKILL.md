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
