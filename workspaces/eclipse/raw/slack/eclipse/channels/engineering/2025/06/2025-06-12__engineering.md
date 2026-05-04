---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:1461bb6dc0afa096273383b2fd13cefecc7366eced66b422d0a4fafe1c1105e4
provider_modified_at: '2025-06-12T15:05:51-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-06-12'
date_range:
  first: '2025-06-12T14:00:45-05:00'
  last: '2025-06-12T15:05:51-05:00'
message_count: 2
thread_count: 1
participant_count: 3
participants:
- slug: david
  slack_user_id: U04UCUX2Y8G
  display_name: David
  real_name: David
  email: david@eclipse.builders
- slug: rob
  slack_user_id: U07HVQQ1MQ8
  display_name: Rob
  real_name: Rob Hitchens
  email: rob@eclipse.builders
- slug: julien
  slack_user_id: U07V99QMTV5
  display_name: julien じゅりえん
  real_name: Julien Tregoat
  email: julien@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-06-12 (Thursday)

## 14:00 — Rob

Sprint

1. Concrete index blob exclusion proof verifier
2. Concrete indexed block exclusion proof verifier

## 14:36 — David

Heads up, google cloud and cloudflare down. Chain is up but archive rpcs are affected right now because we use google bigtable for archive data(  like solana )

> ### 14:43 — David
> 
> actually it looks like backpack's own backend is affected
> 
> ### 14:44 — David
> 
> our rpc still works for now
> 
> ### 14:57 — julien じゅりえん
> 
> been seeing a bunch of weird network issues all day, not even in eclipse but just like voip calls failing, unable to login to an app, etc
> 
> ### 14:59 — David
> 
> yea it's everywhere else
> 
> ### 14:59 — David
> 
> major issue across internet
> 
> ### 15:00 — David
> 
> I can't log into anything that uses google auth
> 
> ### 15:05 — julien じゅりえん
> 
> time to start hosting smtp servers
>
