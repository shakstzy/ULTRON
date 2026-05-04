---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:03ed30a75cd699384dbfd0311fd9bec9c47de2a74ce0807135606644980d9a3c
provider_modified_at: '2025-06-18T08:38:25-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-06-17'
date_range:
  first: '2025-06-17T12:09:32-05:00'
  last: '2025-06-18T08:38:25-05:00'
message_count: 1
thread_count: 1
participant_count: 2
participants:
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
edited_messages_count: 2
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-06-17 (Tuesday)

## 12:09 — Olivier Desenfans

@Michael see [here](https://specs.optimism.io/protocol/derivation.html#batch-submission-wire-format) how OP manages batch serialization / deserialization and splitting.

> ### 08:34 — Ben
> 
> Are we aiming to borrow this verbatim?
> 
> ### 08:35 — Olivier Desenfans
> 
> Not at the moment, I just wanted to showcase an example where individual blobs do not deserialize on their own.
> 
> ### 08:38 — Olivier Desenfans
> 
> Last week we discussed of a possible attack to make the size of an L2 block larger than the maximum blob size on Celestia, an attacker could create a very minimal contract then spam transactions with full account access lists, possibling sending thousands of 1KB txs. The blob size limit is at 8MB so I think it's feasible today.
>
> An easy fix is for batches to be split into blobs arbitrarily to optimize for blob size and nothing else.
>
