# Example: a private workspace

This file is documentation, NOT a real workspace. It shows what a private workspace's `CLAUDE.md` frontmatter looks like and when to use it.

```yaml
---
workspace: therapist
wiki: true
exclude_from_super_graphify: true       # graphify super-merge skips this workspace entirely
ingest_unrouted_default: skip            # never accept content from sources that didn't explicitly allowlist this workspace
---
```

## When to use

Use the private template when the workspace contains material that must NEVER feed into cross-workspace synthesis. Examples:

- **therapist / medical** — content under HIPAA-equivalent expectation; cross-workspace inference is inappropriate.
- **legal-privileged** — attorney-client material.
- **partner-shared** — shared with a romantic partner under a privacy boundary.
- **journal-private** — solo introspection; even Adithya's other workspaces don't get to see this.

## What `exclude_from_super_graphify: true` does

`_shell/bin/graphify-run.sh` reads each workspace's `CLAUDE.md` frontmatter and SKIPS any with this flag set. The workspace can still run its OWN per-workspace `/graphify workspaces/<ws>/wiki` from inside Claude Code (Tier 1), but its graph is NEVER merged into `_graphify/super/graph.json` (Tier 2). Audit's "Cross-workspace surprises" check will not see this workspace's entities.

## What `ingest_unrouted_default: skip` does

When an ingest robot (Gmail, Slack, etc.) fetches an item that doesn't match any workspace's include rules, it normally falls back to a "main" workspace per source policy. With `skip` set, this workspace will REFUSE to be the recipient of unrouted items: the item must explicitly match this workspace's include rules to land here.

This pairs with `exclude_from_super_graphify: true` to make a workspace genuinely opaque to the rest of ULTRON.

## Caveats

- The `raw/` directory is still on disk. It is not encrypted at rest. The privacy boundary is at the workspace-routing and graph-merging layer, not the filesystem layer.
- Lint and audit can still SURFACE counts (e.g., "private workspace has 312 entities, last touched 2 days ago") without reading content.
- Backups (e.g., Time Machine) include private workspaces. If you need stronger isolation, encrypt the `raw/` directory at the OS level or move the workspace out of ULTRON entirely.
