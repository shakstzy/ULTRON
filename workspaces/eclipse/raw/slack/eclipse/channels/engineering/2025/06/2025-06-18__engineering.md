---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:452a3ef56d17ad9c85c984b4591763d7e8998d93a4cc18bc5e853a83bcc4ac9d
provider_modified_at: '2025-06-19T18:49:26-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-06-18'
date_range:
  first: '2025-06-18T11:33:03-05:00'
  last: '2025-06-19T18:49:26-05:00'
message_count: 4
thread_count: 3
participant_count: 4
participants:
- slug: yuri-albuquerque
  slack_user_id: U05TRBZNAMB
  display_name: Yuri Albuquerque
  real_name: Yuri Albuquerque
  email: yuri@eclipse.builders
- slug: michael
  slack_user_id: U07BK2MA1NE
  display_name: Michael
  real_name: Michael Winters
  email: michael@eclipse.builders
- slug: rob
  slack_user_id: U07HVQQ1MQ8
  display_name: Rob
  real_name: Rob Hitchens
  email: rob@eclipse.builders
- slug: olivier-desenfans
  slack_user_id: U07MEVDH39T
  display_name: Olivier Desenfans
  real_name: Olivier Desenfans
  email: olivier@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-06-18 (Wednesday)

## 11:33 — Yuri Albuquerque

I can't join the daily today, I have some errands to do. I'll need to talk to Michael later to define some actions, because I feel blocked now, but I might be wrong

> ### 11:43 — Olivier Desenfans
> 
> What's the blocking point?
> 
> ### 11:47 — Yuri Albuquerque
> 
> it seems I need a result from the L1 fetcher, or I need to begin working on the L1 fetcher, to actually proceed on the celestia fetcher. For now the celestia fetcher already downloads blobs and there's already a block unpacker
> 
> ### 11:49 — Olivier Desenfans
> 
> What do you need exactly? IMO you could fetch a snapshot, fetch blobs around the creation of the snapshot (finding the exact L2 block requires downloading a bit more than necessary, but it's okay at this stage) and then the next step would be re-execution.
>
> I don't understand why you need the L1 fetcher at this stage?
> 
> ### 11:50 — Yuri Albuquerque
> 
> I still need a way of downloading older snapshots anyway
> 
> ### 11:50 — Yuri Albuquerque
> 
> again, I could be wrong regarding being blocked, I'm just reading the requirements and I'm not sure how to proceed
> 
> ### 11:51 — Olivier Desenfans
> 
> > I still need a way of downloading older snapshots anyway
> Yes later on, but right now we can work with what we have
> 
> ### 11:51 — Yuri Albuquerque
> 
> ok
> 
> ### 11:51 — Yuri Albuquerque
> 
> I'll work on fetching the snapshot, then
> 
> ### 11:52 — Olivier Desenfans
> 
> It's not ideal of course, but we have not designed that particular step of storing snapshots on DA yet.
> 
## 12:03 — Michael

https://meet.google.com/ojv-qkpn-jyq?authuser=0

## 17:18 — Rob

@Olivier Desenfans @Michael @Samadhi (Jay) I had a little time to mull over the findings this morning and think about the various concerns. I'm not confident this will address all concerns, but the conversation might help us converge on a concrete description.

https://github.com/Eclipse-Laboratories-Inc/syzygy-gateway/blob/gatewayDA/documentation/09_da_commitment_timing.md

> ### 17:24 — Olivier Desenfans
> 
> Yes, I was thinking of something similar. The only question here is how to reliably query the block height inside Steel but I'm sure it's doable one way or another.
> 
## 18:30 — Rob

@Olivier Desenfans @Michael @Samadhi (Jay)

Sequence diagram, as presently understood (maps to above).

https://github.com/Eclipse-Laboratories-Inc/syzygy-gateway/blob/gatewayDA/documentation/10_DA_flow.md

> ### 17:52 — Olivier Desenfans
> 
> Looking good until step 14, I don't get why the on-chain verifier goes to Celestia. It should find the info on-chain either with the gateway or some other smart contract.
> 
> ### 18:49 — Rob
> 
> Good catch. That should point to Gateway. Will fix.
>
