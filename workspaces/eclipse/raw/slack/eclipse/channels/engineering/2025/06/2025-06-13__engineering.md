---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:7931d664f05cd44cc05337fb0442d6997e474de83b4cbf01512298d27a3445e4
provider_modified_at: '2025-06-15T21:53:38-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-06-13'
date_range:
  first: '2025-06-13T12:03:14-05:00'
  last: '2025-06-15T21:53:38-05:00'
message_count: 3
thread_count: 2
participant_count: 6
participants:
- slug: daniel
  slack_user_id: U04HQ1YK91Q
  display_name: daniel
  real_name: daniel
  email: daniel@eclipse.builders
- slug: david
  slack_user_id: U04UCUX2Y8G
  display_name: David
  real_name: David
  email: david@eclipse.builders
- slug: yuri-albuquerque
  slack_user_id: U05TRBZNAMB
  display_name: Yuri Albuquerque
  real_name: Yuri Albuquerque
  email: yuri@eclipse.builders
- slug: terry
  slack_user_id: U06QHBRHRQX
  display_name: terry
  real_name: terry
  email: terry@eclipse.builders
- slug: michael
  slack_user_id: U07BK2MA1NE
  display_name: Michael
  real_name: Michael Winters
  email: michael@eclipse.builders
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

# #engineering — 2025-06-13 (Friday)

## 12:03 — David

moving stand back by 30 min

> ### 12:14 — Olivier Desenfans
> 
> Will miss it for family time, I'm busy preparing the MVP for ZK DA fraud proofs. Couldn't finish it today so I pushed back the next sync on this topic to Monday.
> 
## 12:31 — Yuri Albuquerque

https://meet.google.com/zwa-wecw-ifj?authuser=0

## 12:40 — daniel

Hey all, I need to find a funding source or eth address for a wallet, whats' the best way to do that at the moment

> ### 12:47 — terry
> 
> etherscan -> first tx
> 
> ### 12:48 — daniel
> 
> I need to lookup the eth address from an eclipse one.
> 
> ### 12:48 — daniel
> 
> and for like a ton
> 
> ### 12:48 — daniel
> 
> I'm looking for a DB on the relayer
> 
> ### 13:25 — David
> 
> @Michael how much of this can we get from the relayer db?
> 
> ### 13:32 — Michael
> 
> looking for some deposits ? we can run the knight and relate eclipse addresses to ethereum addresses for deposits. I did provide a flat file to Sydney (so it may be in there if it's not too recent).
> 
> ### 13:36 — Michael
> 
> This goes to the end of TurboTap - if its more recent, I can run the knight and regenerate the data
> 
> ### 21:53 — Michael
> 
> @daniel @David ran this over the weekend, here is an updated version of the mainnet deposit data (as of Sunday afternoon).
>
