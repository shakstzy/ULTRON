---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:36-05:00'
ingest_version: 1
content_hash: blake3:16f30010eaf143ff01bc37a46526648cf9e9c4f41dabeefe2eb78bc8cc62e879
provider_modified_at: '2026-03-25T14:29:51-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2026-01-27'
date_range:
  first: '2026-01-27T17:30:46-05:00'
  last: '2026-03-25T14:29:51-05:00'
message_count: 1
thread_count: 1
participant_count: 3
participants:
- slug: cemal
  slack_user_id: U07JEV700QJ
  display_name: cemal
  real_name: cemal
  email: cemal@eclipse.builders
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
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2026-01-27 (Tuesday)

## 17:30 — julien じゅりえん

been messin around with subagents today. the verification agent cursor suggests is handy so far, caught a bunch of stuff faster https://cursor.com/docs/context/subagents#verification-agent

> ### 17:34 — cemal
> 
> is it the same thing as claude skills
> 
> ### 17:35 — cemal
> 
> oh no
> 
> ### 17:40 — julien じゅりえん
> 
> yeah i'm still understanding its value. I don't fully get why it's better to have an agent that is 'specialized' in an area of coding since I figure it already knows everything, but think it has to do with context and limiting its concerns so it's less likely to miss things (which is ig why the verification agent is helpful currently bc things get lost in the sauce?). so big picture and small picture separation. and for task parallelization
> 
> ### 17:44 — julien じゅりえん
> 
> I guess also handles parallelization well
> 
> ### 14:29 — Adithya Kumar (me)
> 
> bro and sequential tasks too if you set up some skills for your harness and your [agents.md since it gets autoinjected every time it](http://agents.it) goes insane
>
