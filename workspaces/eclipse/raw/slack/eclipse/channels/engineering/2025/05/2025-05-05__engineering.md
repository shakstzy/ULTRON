---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:32-05:00'
ingest_version: 1
content_hash: blake3:4e4e01938b30fb6cae55ddb51fc215a3dd512a1d68bbb0aa61fed731881a648a
provider_modified_at: '2025-05-07T11:57:06-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-05-05'
date_range:
  first: '2025-05-05T04:28:50-05:00'
  last: '2025-05-07T11:57:06-05:00'
message_count: 4
thread_count: 3
participant_count: 7
participants:
- slug: david
  slack_user_id: U04UCUX2Y8G
  display_name: David
  real_name: David
  email: david@eclipse.builders
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
- slug: samadhi-jay
  slack_user_id: U06LP8VPHNE
  display_name: Samadhi (Jay)
  real_name: Samadhi
  email: jay@eclipse.builders
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
edited_messages_count: 2
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-05-05 (Monday)

## 04:28 — Alex Petrosyan

RocksDB is the new `zeroize`. I'm already running into issues compiling `librocksdb-sys` on my machine. For the moment the solutions seem to be fairly simple, downgrading the packages, but will keep you guys updated.

> ### 04:44 — Alex Petrosyan
> 
> OK. So some more colour to this error.
> 
> ### 04:44 — Alex Petrosyan
> 
> The problem is missing includes of `cstdint` they used to be implicitly included in GCC prior to 13, but are now not.
> 
> ### 04:44 — Alex Petrosyan
> 
> So there are cascading failures.
> 
> ### 04:46 — Alex Petrosyan
> 
> The problem is not exactly easy to fix, and it will become an issue as more and more distros are going to ship with GCC13 later on,
> 
> ### 04:46 — Alex Petrosyan
> 
> I'm thinking of a way to fix this issue for the time being.
> 
> ### 11:56 — Alex Petrosyan
> 
> I found a solution:
> 
> ### 11:56 — Alex Petrosyan
> 
> ```CXXFLAGS="$CXXFLAGS -include cstdint" cargo build```
> 
> ### 11:57 — Alex Petrosyan
> 
> This is annoying, but can be fixed system-wide
> 
## 12:49 — Rob

Standup?

> ### 12:49 — Yuri Albuquerque
> 
> wrong room again?
> 
> ### 12:50 — Yuri Albuquerque
> 
> [meet.google.com/ixa-heoe-phb](http://meet.google.com/ixa-heoe-phb)
> 
> ### 12:50 — Rob
> 
> Probably. I'm in the one on the calendar
> 
> ### 12:50 — Yuri Albuquerque
> 
> it's weird you keep getting this problem
> 
> ### 12:52 — Alex Petrosyan
> 
> I do too
> 
> ### 12:52 — Michael
> 
> I can re-invite you to the new one
> 
> ### 12:52 — Alex Petrosyan
> 
> I just keep the links in an org-file
> 
> ### 12:52 — Michael
> 
> do you guys have multiple meet links ?
> 
> ### 12:52 — Alex Petrosyan
> 
> I have nada in my calendar
> 
> ### 12:53 — Michael
> 
> kk - let me try
> 
> ### 12:53 — Rob
> 
> I think it gets messed from long chains of revisions.
>
> Why not blow it away and create a new one?
> 
> ### 12:54 — Michael
> 
> Just sent a new invite to both of you - did it work??
> 
> ### 12:56 — Rob
> 
> Got it. Another update in a long chain of revisions. Matches today's room for me.
> 
> ### 12:56 — Rob
> 
> Next week shows the same room
> 
> ### 12:57 — Michael
> 
> nice ... sounds good
> 
## 12:56 — Samadhi (Jay)

wip bridge security doc https://www.notion.so/eclipsebuilders/Bridge-Security-1ea4a02308308038a20ae328138c4242?showMoveTo=true&saveParent=true

@Olivier Desenfans feel free to add to it

> ### 12:56 — Olivier Desenfans
> 
> Can you give me access?
> 
> ### 12:57 — Samadhi (Jay)
> 
> ok should have it now
> 
## 13:06 — David

fyi this is what @BM backported: https://github.com/anza-xyz/agave/pull/1981 - Amazing work!!
