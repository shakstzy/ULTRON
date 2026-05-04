---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:36-05:00'
ingest_version: 1
content_hash: blake3:1a04d40c5ff029c48c1e5ee2c73d719908f28bc86722b9e44e5a803c83ab7008
provider_modified_at: '2026-03-31T13:49:19-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2026-03-30'
date_range:
  first: '2026-03-30T14:00:22-05:00'
  last: '2026-03-31T13:49:19-05:00'
message_count: 2
thread_count: 1
participant_count: 2
participants:
- slug: daniel
  slack_user_id: U04HQ1YK91Q
  display_name: daniel
  real_name: daniel
  email: daniel@eclipse.builders
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

# #engineering — 2026-03-30 (Monday)

## 14:00 — Adithya Kumar (me)

yoo hope everyones doing well:

was chatting w sydney and got the idea of adding a metadata flag during the API batch upload process that:
• Auto-detects when audio has diarized speakers
• Tags speaker identifiers (speaker 1, speaker 2, etc.)
• Standardizes this across different data providers (since Fluffle uploads paired folders, but another provider might do it differently)

> ### 14:32 — daniel
> 
> we don't do this during upload, but we do it afterward
> 
> ### 14:33 — daniel
> 
> what problem are you trying to sovle ?
> 
> ### 14:33 — daniel
> 
> we might have already done the work ehre
> 
> ### 13:49 — Adithya Kumar (me)
> 
> Some form of visual tagging for the same conversation, basically combining both sides of the convo for easier approvals
> 
## 14:00 — Adithya Kumar (me)

how trivial/nontrivial would this be to implement
