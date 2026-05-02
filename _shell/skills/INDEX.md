# ULTRON Skills Index

Project-local skills for ULTRON. Each skill lives at `_shell/skills/<name>/SKILL.md` with implementation scripts in `scripts/`. Skills marked **(symlinked global)** are also available outside ULTRON via a symlink in `~/.claude/skills/`.

| Skill | Purpose | Trigger phrases | Symlinked? |
|---|---|---|---|
| **promote-entity** | Promote a workspace entity to a canonical global stub at `_global/entities/<type>/<slug>.md` | "promote", "make X global", "canonicalize", "merge across workspaces" | yes |
| **alias** | Merge same-entity slugs (e.g., `sandeep-r` → `sandeep-rao`) | "these are the same", "alias", "consolidate", "duplicate slug" | yes |
| **link** | Assert structured relationships between entities (`colleague`, `reports_to`, `invested_in`, etc.) | "link", "related to", "X works with Y", "X reports to Y" | yes |
| **schedule** | Generate / load / unload launchd plists from `schedule.yaml` files | "schedule", "every day", "load cron", "show me what's scheduled" | yes |
| **contacts-sync** | Sync Apple Contacts → `_global/entities/people/` canonical stubs | "sync contacts", "update people", "import my contacts" | yes |

## How skills are wired

1. The skill body (`SKILL.md`) sits at `_shell/skills/<name>/SKILL.md` with frontmatter `name:` and `description:`. The `description:` field MUST start with "Use this skill EVERY time" plus a clear trigger so Claude Code's skill matcher fires reliably.
2. Implementation scripts live in `_shell/skills/<name>/scripts/`. They are plain Python / bash and can be run directly when debugging.
3. A symlink at `~/.claude/skills/<name>` makes the skill available globally.
4. Each skill ends its body with a brief Self-review checklist; calls to the skill must include a self-review pass before declaring done.

## Adding a new skill

1. `mkdir _shell/skills/<name>/scripts`.
2. Write `SKILL.md` with the canonical frontmatter shape (see existing skills).
3. Implement `scripts/main.py` (or whatever entrypoint the SKILL.md describes).
4. `chmod +x` the scripts.
5. `ln -s /Users/shakstzy/ULTRON/_shell/skills/<name> ~/.claude/skills/<name>`.
6. Add a row to this INDEX.md.

## Why project-local + symlinked

The skill bodies version-control with ULTRON (project-local), but Claude Code's skill matcher resolves them via `~/.claude/skills/` (global). Editing in one place, available in both. To remove a skill globally, `unlink ~/.claude/skills/<name>` — the project copy stays.
