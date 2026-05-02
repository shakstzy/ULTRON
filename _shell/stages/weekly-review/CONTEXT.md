# Stage: weekly-review

## Purpose
Compose review packet from the prior week's audit + lint reports for human (Adithya) review.

## Invocation
`run-stage.sh weekly-review`

## Inputs
- Latest `_audit/weekly/<YYYY-WW>.md`.
- All workspaces' `_meta/lint-*.md` from the past 7 days.
- All `_meta/schema-proposals.md` and `_meta/learning-proposals.md` open items.

## Process
1. `_shell/bin/build-weekly-packet.py` produces a structured packet at `_shell/audit/packets/<YYYY>-W<WW>.md` (cross-workspace candidates, super-graph report, per-workspace activity tail, recent failures, open proposals).
2. Claude reads that packet and adds prose synthesis under section 6 (Synthesis) of the same file. Optionally writes a parallel review at `_audit/reviews/<YYYY-WW>.md`.
3. Order Claude's synthesis by priority: route breakage > schema drift > stale entities > backfill candidates > schema/learning proposals.
4. Include open count for each proposal type per workspace.
5. Email or Slack to Adithya (optional — handled by side-channel, not part of this stage).

## Outputs
- `_audit/reviews/<YYYY-WW>.md`.

## Idempotency
Yes. Re-running rewrites the file deterministically.
