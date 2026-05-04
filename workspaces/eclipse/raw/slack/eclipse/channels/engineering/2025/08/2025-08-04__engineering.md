---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:36-05:00'
ingest_version: 1
content_hash: blake3:6a4edfefbad582d07011cd8a55996fff8160809b9e70870b4fe307105b149b0e
provider_modified_at: '2025-08-04T23:22:48-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-08-04'
date_range:
  first: '2025-08-04T16:37:49-05:00'
  last: '2025-08-04T23:22:48-05:00'
message_count: 1
thread_count: 1
participant_count: 5
participants:
- slug: vijay
  slack_user_id: U0596K34S4B
  display_name: Vijay
  real_name: Vijay
  email: vijay@eclipse.builders
- slug: cooper
  slack_user_id: U05U6497UAE
  display_name: Cooper
  real_name: Cooper Kernan
  email: cooper@eclipse.builders
- slug: michael
  slack_user_id: U07BK2MA1NE
  display_name: Michael
  real_name: Michael Winters
  email: michael@eclipse.builders
- slug: julien
  slack_user_id: U07V99QMTV5
  display_name: julien じゅりえん
  real_name: Julien Tregoat
  email: julien@eclipse.builders
- slug: johnny
  slack_user_id: U0937CH496U
  display_name: johnny
  real_name: Johnny
  email: johnny@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-08-04 (Monday)

## 16:37 — julien じゅりえん

not sure if we're using etherscan eclipsescan API for anything internally but they're deprecating the v1 API so in case we are, gotta migrate to v2 if we aren't already

https://docs.etherscan.io/etherscan-v2/v2-quickstart

> ### 17:14 — Vijay
> 
> cc @johnny - worth checking with sydney also
> 
> ### 17:29 — johnny
> 
> @julien じゅりえん good catch - what's the est effort to migrate to v2?
> 
> ### 17:32 — julien じゅりえん
> 
> well it depends on if we’re using it at all @johnny - not sure if we were using it for anything like flipside data or stuff. but the migration guide makes it look pretty simple just swapping out endpoint formats
> 
> ### 17:32 — julien じゅりえん
> 
> cc @Cooper perhaps maybe knows if it’s used anywhere
> 
> ### 17:33 — johnny
> 
> ok cool pinged Sydney too
> 
> ### 17:55 — Cooper
> 
> Pinged Flipside, thx for flagging
> 
> ### 21:30 — johnny
> 
> @Michael are we using this API for anything bridge related?
> 
> ### 23:11 — Michael
> 
> @johnny ya we use it for the gas oracle in the withdraw relayer. I can update and test tom. Looks like just a quick config change.
> 
> ### 23:22 — johnny
> 
> gotcha thanks!
>
