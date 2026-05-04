---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:421fc5eb69a844594f7e2550c4d8e157f5df3e7e7858185dd14f5bc8ab05fd51
provider_modified_at: '2025-07-10T07:20:47-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-07-09'
date_range:
  first: '2025-07-09T14:04:46-05:00'
  last: '2025-07-10T07:20:47-05:00'
message_count: 1
thread_count: 1
participant_count: 3
participants:
- slug: alex-petrosyan
  slack_user_id: U05RB714333
  display_name: Alex Petrosyan
  real_name: Alex Petrosyan
  email: alex@eclipse.builders
- slug: yuri-albuquerque
  slack_user_id: U05TRBZNAMB
  display_name: Yuri Albuquerque
  real_name: Yuri Albuquerque
  email: yuri@eclipse.builders
- slug: fikunmi
  slack_user_id: U07RFM6MP9D
  display_name: fikunmi
  real_name: Fikunmi Ajayi-Peters
  email: fikunmi@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-07-09 (Wednesday)

## 14:04 — Yuri Albuquerque

@Alex Petrosyan https://github.com/Eclipse-Laboratories-Inc/solar-eclipse/pull/117 could you take a look?

> ### 14:23 — Alex Petrosyan
> 
> One question and I want to run the test, which I'll do tomorrow.
> 
> ### 14:27 — Yuri Albuquerque
> 
> I can add the feature guard, I'll do it tomorrow morning
> 
> ### 14:45 — Alex Petrosyan
> 
> Don't.
> 
> ### 14:45 — Alex Petrosyan
> 
> We likely won't need it, and if we do I can just squash all our commits again
> 
> ### 14:45 — Yuri Albuquerque
> 
> ok
> 
> ### 16:32 — fikunmi
> 
> How long do we plan to store snapshots?
> 
> ### 05:09 — Alex Petrosyan
> 
> Tests pass. PR approved
> 
> ### 07:16 — Yuri Albuquerque
> 
> @fikunmi I need snapshots about 7 days old
> 
> ### 07:18 — fikunmi
> 
> oh, for da bridging work?
>
> I was more curious as to how many we currently store and the storage implications.
>
> Thanks for clarifying.
> 
> ### 07:19 — Yuri Albuquerque
> 
> for the full node
> 
> ### 07:19 — Yuri Albuquerque
> 
> @Alex Petrosyan thanks
> 
> ### 07:20 — fikunmi
> 
> oh ok. I assume it's for something like starting from the last proven slot
> 
> ### 07:20 — Yuri Albuquerque
> 
> yeah, something like that
>
