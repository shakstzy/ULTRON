# Source Routing Matrix

Single source of truth for how external content flows into ULTRON workspaces.

Each row binds: **source** + **account** + **scope** (label / folder / channel / contact-set) → **workspace**. The ingest driver (`_shell/bin/ingest-driver.py`) reads this file. Per-workspace `config/sources.yaml` files declare which credentials / API to use; this file declares which workspace owns each scope.

## Editing rules

1. One row per (source, account, scope) tuple. No duplicates.
2. `routes_to` may list multiple workspaces (comma-separated, no spaces). Content lands in all listed workspaces.
3. `exclude` is optional; comma-separated source-native filters (gmail labels, drive folder names, slack channels).
4. Workspaces with `ingest_unrouted_default: skip` REFUSE unrouted items: an item must explicitly match a row to land there.
5. Workspaces with `ingest_unrouted_default: route_to_main` accept unrouted items per the source's main-workspace policy.
6. Updates take effect on the next `run-stage.sh ingest <ws>` or `run-stage.sh ingest-source <source> <account>`.
7. Rows with `routes_to: TBD` are placeholders Adithya will fill in. The ingest driver MUST refuse to run a source that has unresolved TBDs for its account.

## Source schemes

- **gmail** — `account` is the email address. `scope` is a gmail search clause: `label:X`, `from:*@y.com`, `to:z@w.com`, `subject:"Foo"`. Multiple clauses can be ANDed via the `+` separator (e.g. `label:Music+from:*@distrokid.com`).
- **drive** — `account` is the email. `scope` is `folder:<NAME>` (case-sensitive, exact match to top-level folder name).
- **slack** — `account` is the workspace ID (e.g. `T04472N6YUU`). `scope` is `channel:<name>` or `dm:<user-id>`.
- **granola** — `account` is the granola login email; `default` if only one. `scope` is `folder:<NAME>` (exact match to upstream Granola UI folder).
- **fireflies** — `account` is the fireflies login email. `scope` is `channel:<name>` or `meeting-tag:<tag>`.
- **imessage** — `account` is `local`. `scope` is `contact-set:<label>`. Contact lists for each set live in `_global/contact-sets.yaml` (TBD).
- **whatsapp** — `account` is the phone number. `scope` is `chat:<name>` or `contact-set:<label>`.
- **manual** — `account` is `local`. `scope` is `path:<watch-dir>`. Each workspace has its own `raw/manual/_inbox/`; routing is implicit.

## Routing matrix

| source | account | scope | routes_to | exclude | notes |
|---|---|---|---|---|---|
| gmail | adithya@outerscope.xyz | label:Eclipse | eclipse | from:noreply@*,label:SPAM,label:TRASH | |
| gmail | adithya@outerscope.xyz | from:*@eclipse.audio | eclipse | label:SPAM,label:TRASH | |
| gmail | adithya@outerscope.xyz | from:*@eclipse.builders | eclipse | label:SPAM,label:TRASH | |
| gmail | adithya@outerscope.xyz | label:Seedbox | seedbox | | |
| gmail | adithya@outerscope.xyz | label:Outerscope | outerscope | label:SPAM,label:TRASH | TBD: confirm label exists |
| gmail | adithya@outerscope.xyz | label:Mosaic | mosaic | label:SPAM,label:TRASH | TBD: confirm label exists |
| gmail | adithya@outerscope.xyz | label:Synapse | synapse | label:SPAM,label:TRASH | TBD: confirm label exists |
| gmail | adithya@synps.xyz | (all) | synapse | from:noreply@*,label:SPAM,label:TRASH | primary synapse mailbox |
| gmail | adithya.shak.kumar@gmail.com | (all) | personal | label:SPAM,label:TRASH,label:Promotions | personal default |
| gmail | adithya.shak.kumar@gmail.com | label:RealEstate | real-estate | | TBD: confirm label name |
| gmail | adithya.shak.kumar@gmail.com | label:PropertyMgmt | property-management | | TBD: confirm label name |
| gmail | adithya.shak.kumar@gmail.com | label:Music | music | | TBD: confirm label name |
| gmail | adithya.shak.kumar@gmail.com | label:Clipping | clipping | | TBD: confirm label name |
| gmail | adithya.shak.kumar@gmail.com | label:OnlyFans | onlyfans | | TBD: confirm label name |
| gmail | adithya.shak.kumar@gmail.com | label:Trading | trading | | TBD: confirm label name |
| gmail | adithya.shak.kumar@gmail.com | label:Library | library | | TBD: confirm label name |
| gmail | adithya@outerscope.xyz | label:InclusiveLayer | inclusive-layer | label:SPAM,label:TRASH | TBD: confirm label name |
| gmail | adithya.shak.kumar@gmail.com | label:Sei | sei | | TBD: confirm label name + which mailbox holds Sei mail |
| drive | adithya@outerscope.xyz | folder:INCLUSIVELAYER | inclusive-layer | | flipped from outerscope; folder name confirmed |
| drive | adithya@outerscope.xyz | folder:MOSAIC | mosaic | | TBD: confirm exact folder name |
| drive | adithya@outerscope.xyz | folder:SYNAPSE | synapse | | TBD: confirm exact folder name |
| drive | adithya@synps.xyz | folder:SYNAPSE | synapse | | TBD: confirm if synapse drive content lives in synps.xyz vs outerscope.xyz |
| drive | TBD | folder:SEI | sei | | TBD: which account hosts Sei drive content (if any), and whether credentials are still valid |
| slack | T04472N6YUU | channel:app-team | eclipse | | eclipse-labs.slack.com |
| slack | T04472N6YUU | channel:data-sourcing | eclipse | | |
| slack | T04472N6YUU | channel:deals | eclipse | | |
| slack | T04472N6YUU | channel:engineering | eclipse | | |
| slack | T04472N6YUU | channel:eclipse-ugc | eclipse | | private channel C0AR2P8H268 |
| slack | T04472N6YUU | channel:general | eclipse | | |
| granola | default | folder:ECLIPSE | eclipse | | |
| granola | default | folder:MOSAIC | mosaic | | TBD: confirm exact folder name |
| granola | default | folder:SYNAPSE | synapse | | TBD: confirm exact folder name |
| granola | default | folder:OUTERSCOPE | outerscope | | TBD: confirm folder exists |
| granola | default | folder:INCLUSIVELAYER | inclusive-layer | | TBD: confirm whether a Granola folder exists upstream |
| granola | default | folder:SEI | sei | | TBD: confirm whether a Granola folder exists upstream |
| slack | TBD | channel:* | sei | | TBD: was there a Sei Slack workspace; are credentials still valid |
| imessage | local | contact-set:dating | dating | | TBD: define contact set in _global/contact-sets.yaml |
| imessage | local | contact-set:music | music | | TBD: define contact set |
| imessage | local | contact-set:property-mgmt | property-management | | TBD: tenants + vendors |
| imessage | local | (default) | personal | | unmapped contacts route to personal |
| manual | local | path:workspaces/{ws}/raw/manual/_inbox/ | (per-workspace) | | each workspace has its own inbox; routing is implicit |

## Workspaces still requiring source rules

These rows above are marked `TBD`. Adithya fills them. Until filled, the ingest driver refuses to run for that scope and logs `unresolved-tbd` to `_logs/ingest-driver.log`.

- **mosaic** — Drive folder name, Granola folder name, gmail label
- **synapse** — Drive folder name, Granola folder name, gmail label (synps.xyz domain wired)
- **onlyfans** — gmail label; future creator-platform browser scrape rows
- **real-estate** — gmail label
- **property-management** — gmail label, imessage contact-set; future Zillow Rental Manager scrape
- **dating** — imessage contact-set; future tinder / bumble / hinge browser scrape rows
- **library** — gmail label; future article / podcast / paper extract rows
- **trading** — gmail label; future exchange CSV import rows
- **music** — gmail label, imessage contact-set; future DistroKid scrape row
- **clipping** — gmail label; future yt-dlp / mlx-whisper / metrics-poll rows
- **inclusive-layer** — gmail label confirmation, Granola folder confirmation (drive folder confirmed: INCLUSIVELAYER)
- **sei** — gmail label + which mailbox; whether Drive / Slack credentials still valid; Granola folder confirmation

## Cross-workspace duplication

If an item legitimately belongs in two workspaces (e.g., a Mosaic+Synapse joint contract email), put both slugs in `routes_to`, comma-separated. The ingest driver writes the item to both `raw/` trees, sharing content hash so dedupe still works.

If an item is ambiguous (no clear home), let it fall to the source's default workspace per `ingest_unrouted_default`. Do NOT add catch-all rules here.

## Conflicts

- If two rows match the same item, the more specific scope wins (e.g., `label:Eclipse` beats `(all)` for the same account).
- If two same-specificity rows match (true tie), the row that appears LATER in the matrix wins. The ingest driver logs the conflict to `_logs/ingest-driver.log`.
- Contact-set membership conflicts (one contact in two sets) are flagged at lint time and resolved by adding a per-contact override in `_global/contact-sets.yaml`.
