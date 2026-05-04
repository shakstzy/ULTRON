---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:36-05:00'
ingest_version: 1
content_hash: blake3:a8ee1ef2716c0081ae8b6979ae6e7fbb209ade0631ee1215d455585ff307067d
provider_modified_at: '2026-04-10T14:04:20-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2026-04-10'
date_range:
  first: '2026-04-10T13:34:19-05:00'
  last: '2026-04-10T14:04:20-05:00'
message_count: 1
thread_count: 1
participant_count: 2
participants:
- slug: julien
  slack_user_id: U07V99QMTV5
  display_name: julien じゅりえん
  real_name: Julien Tregoat
  email: julien@eclipse.builders
- slug: adithya-shak-kumar
  slack_user_id: U0A993YPZ1Q
  display_name: Adithya Kumar (me)
  real_name: Adithya Kumar
  email: adithya@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 4
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2026-04-10 (Friday)

## 13:34 — julien じゅりえん

so claude made opus 1m context the default. but you can get access to the opus original 200k context if you type in `/model opus` .

 I like to keep my context on the 200k unless it's a large never ending task, and even then, the models start to tell you that it's better to compact around 50-60% for those (vs 80~% for 200k)

if I need to fniish a task or concept and I'm almost there, i'll switch off to 1m just to get it done then get back to opus default, gotta turn off autocompacting so you can decide if or when to compact. plus then you can tell it how to compact if you need that

> ### 14:01 — Adithya Kumar (me)
> 
> Lowk isn't token util kinda like credit utilization rate always maximize the capacity but lower ur usage as much as possible
> 
> ### 14:01 — Adithya Kumar (me)
> 
> Like 50k tokens work better on 1m window than 200k
> 
> ### 14:02 — julien じゅりえん
> 
> ooooo that's good to know
> 
> ### 14:03 — julien じゅりえん
> 
> I thought it didn't matter
> 
> ### 14:04 — julien じゅりえん
> 
> I figure the 50k tokens work better based on what's in your context and how related the task is to it vs if it's going to increase scope
> 
> ### 14:04 — julien じゅりえん
> 
> the 200k limit at least makes me think about it so i reset if it's not the same topic
>
