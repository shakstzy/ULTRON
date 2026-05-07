---
name: cloud-llm
description: Single dispatch point for cloud LLM calls — text or vision. Gemini Pro/Flash via the gemini CLI, cycling Adithya's cached accounts on 429. Halts loud (CloudLLMUnreachable) when all accounts exhausted. Use this from any consumer skill (instagram-summary, etc.) instead of hitting gemini directly.
allowed-tools: Bash
---

# cloud-llm

Shared cloud-LLM utility skill. Lives at `~/ULTRON/_shell/skills/cloud-llm/`. Consumed via the global symlink `~/.claude/skills/cloud-llm/`.

## Why

Adithya pays for Max + Gemini Ultra (3 accounts). Spreading work across accounts means no single weekly cap eats a long-running visual ingest.

## Engines

| engine | trigger | notes |
|---|---|---|
| **gemini Pro** (default) | every call | `-m gemini-3-pro-preview`. Cwd is the skill dir; image refs are staged underneath so the workspace sandbox accepts them. |
| **gemini Flash** | Pro 429 on the same account | no `-m` flag → CLI default Flash. |
| **claude -p sonnet** | every account exhausted | no path restriction; eats Max weekly cap. |

**Account priority** (hardcoded — Workspace plan first, personal as backup):
1. `avery@seedboxlabs.co`
2. `adithya@outerscope.xyz`
3. `adithya@eclipse.builders`

Cycling rotates `~/.gemini/oauth_creds.json` from `~/.gemini/accounts/<email>.json`.

## Consumer surface

```python
import sys
sys.path.insert(0, "/Users/shakstzy/ULTRON/_shell/skills/cloud-llm")
from client import describe_images, ask_text, CloudLLMUnreachable

# Vision — pass absolute paths, helper handles staging.
result = describe_images(["/abs/a.jpg", "/abs/b.jpg"], "Describe in 4 bullets.")

# Text only:
result = ask_text("Summarize: ...")
```

Both return `{"engine": "gemini-pro|gemini-flash|claude-sonnet", "account": <email or None>, "output": <str>}`.

## Behavior

1. Pro on account 1 → Flash on account 1 → Pro on account 2 → Flash on account 2 → ...
2. Quota errors (`429|exhausted|quota|rate.?limit` in stderr) rotate; non-quota errors halt loud.
3. All gemini exhausted → `claude -p sonnet`.
4. Both fail → raise `CloudLLMUnreachable`. No graceful degradation.

## Notes

- No daemon, no install. `gemini` and `claude` must be on PATH.
- Staging dir at `<skill>/staging/<runId>/` is auto-cleaned per call.
- Concurrent calls clobber `oauth_creds.json` mid-flight. Run consumers serially.
