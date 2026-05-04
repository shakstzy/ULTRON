---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:afbc8ca35f2ca3c5c54fe2ea33e192e76043551255780d7c2d75262ea0d50c7d
provider_modified_at: '2025-07-27T22:22:34-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-07-25'
date_range:
  first: '2025-07-25T09:45:08-05:00'
  last: '2025-07-27T22:22:34-05:00'
message_count: 3
thread_count: 3
participant_count: 8
participants:
- slug: kayla
  slack_user_id: U04F1UG1HC7
  display_name: Kayla
  real_name: Kayla Bu
  email: kayla.bu@eclipse.builders
- slug: caleb-jiang
  slack_user_id: U0554BYTBT6
  display_name: Caleb Jiang
  real_name: Caleb Jiang
  email: caleb@eclipse.builders
- slug: chinghua
  slack_user_id: U056A0YD9PG
  display_name: ChingHua
  real_name: ChingHua
  email: chinghua@eclipse.builders
- slug: alex-petrosyan
  slack_user_id: U05RB714333
  display_name: Alex Petrosyan
  real_name: Alex Petrosyan
  email: alex@eclipse.builders
- slug: michael
  slack_user_id: U07BK2MA1NE
  display_name: Michael
  real_name: Michael Winters
  email: michael@eclipse.builders
- slug: nagu
  slack_user_id: U07M6CY18P2
  display_name: Nagu
  real_name: Nagu
  email: nagu@eclipse.builders
- slug: olivier-desenfans
  slack_user_id: U07MEVDH39T
  display_name: Olivier Desenfans
  real_name: Olivier Desenfans
  email: olivier@eclipse.builders
- slug: ben
  slack_user_id: U07UG9EBU4U
  display_name: Ben
  real_name: Ben
  email: ben@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 1
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-07-25 (Friday)

## 09:45 — ChingHua

I'm feeling headache today so I have to do standup async: I tested the message-auth of orbit and fix the pr conflits.  I'm cleaning up those code I was trying too hard to parse the tx on enhanced txn. And reading the docs related to perps and parlays.

> ### 11:19 — Kayla
> 
> feel better frog
> 
## 11:05 — Olivier Desenfans

<!channel> weekly stand-up here: https://meet.google.com/hdw-zmin-uyu?authuser=1

> ### 11:07 — Olivier Desenfans
> 
> Notes [here](https://www.notion.so/eclipsebuilders/Weekly-R-D-standup-23b4a0230830802eb2d8e984453f4f0c), please fill in your updates when you see it
> 
> ### 11:07 — Ben
> 
> running late - joining shortly
> 
> ### 13:16 — Nagu
> 
> Apologies for missing today.
>
> I should be on time again starting Monday.
>
> I moved cross country and its been a bit crazy on my side. Thank you.
> 
## 15:49 — Olivier Desenfans

Any idea what an "account sequence mismatch" is on Celestia, and did we ever have to work around this?

> ### 05:25 — Alex Petrosyan
> 
> Yes. And Yes
> 
> ### 05:25 — Alex Petrosyan
> 
> Tagging @Michael
> 
> ### 05:40 — Alex Petrosyan
> 
> IIRC this was because the nonce isn't properly tacked in the async client and if the blobs are submitted out of order, your blob submission would fail
> 
> ### 11:44 — Michael
> 
> That's right, and also the only way to fix it is to restart the node. Perhaps @Caleb Jiang can help out?
> 
> ### 22:11 — Caleb Jiang
> 
> A watchdog continuously monitors the DA light node logs. If multiple "incorrect account sequence" errors are detected within a one-minute interval, it automatically restarts the DA light node.
> 
> ### 22:22 — Caleb Jiang
> 
> Additionally, the watchdog monitors the following errors to trigger a restart of the DA light node:
> • `"error reading server preface: EOF"`
> • `"panic in rpc method"`
> It also watches for the following errors from the DA light node to restart the Celestia consensus node:
> • `"proof is unexpectedly empty"`
> • `"failed to query for balance: rpc error: code = Canceled"`
>
