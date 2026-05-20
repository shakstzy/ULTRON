---
source: slack
workspace: eclipse
ingested_at: '2026-05-20T14:28:33-05:00'
ingest_version: 1
content_hash: blake3:b96013bbe0bce7b2be8dd5e5abdee15aa18375c782dd0aae8504fe91d5be2ac6
provider_modified_at: '2026-05-20T13:45:16-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2026-05-20'
date_range:
  first: '2026-05-20T13:26:35-05:00'
  last: '2026-05-20T13:45:16-05:00'
message_count: 1
thread_count: 1
participant_count: 3
participants:
- slug: daniel
  slack_user_id: U04HQ1YK91Q
  display_name: daniel
  real_name: daniel
  email: daniel@eclipse.builders
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

# #engineering — 2026-05-20 (Wednesday)

## 13:26 — Adithya Kumar (me)

yo review is ridiculously slow to load large .wav files ik this is prolly tough to do on browser but is there any work around to where we could cache this maybe for just a preview whenever im doing partner upload sanity checks?

> ### 13:34 — julien じゅりえん
> 
> we transcode some audio to mp3 i forget which formats so it works better. maybe we can do this for large files to mp3 or opus or something small for listening, then still allow downloading original and show analysis of the original. would also lower s3 egress costs tho im sure thats minor
>
> buffering should be possible but i think there was a reason i didnt before
>
> cc @daniel
> 
> ### 13:42 — daniel
> 
> whats the context here, what page
> 
> ### 13:44 — julien じゅりえん
> 
> review page on web
> 
> ### 13:45 — daniel
> 
> @Adithya Kumar (me) make a gh issue with a link and an image,  I can fix
>
