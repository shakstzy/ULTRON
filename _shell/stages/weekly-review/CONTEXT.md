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
1. Aggregate findings into a single packet at `_audit/reviews/<YYYY-WW>.md`.
2. Order by priority: route breakage > schema drift > stale entities > backfill candidates > schema/learning proposals.
3. Include open count for each proposal type per workspace.
4. Email or Slack to Adithya (optional — handled by side-channel, not part of this stage).

## Outputs
- `_audit/reviews/<YYYY-WW>.md`.

## Idempotency
Yes. Re-running rewrites the file deterministically.
