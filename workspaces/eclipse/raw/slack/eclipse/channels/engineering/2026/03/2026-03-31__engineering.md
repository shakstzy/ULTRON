---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:36-05:00'
ingest_version: 1
content_hash: blake3:1922567cb6a8d1a243e3c2630464f9cee4be1f280c1f1583f41355e98fb0831f
provider_modified_at: '2026-03-31T17:46:59-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2026-03-31'
date_range:
  first: '2026-03-31T13:13:34-05:00'
  last: '2026-03-31T17:46:59-05:00'
message_count: 3
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
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2026-03-31 (Tuesday)

## 13:13 — julien じゅりえん

gotta investigate this in our apps. the attack is interesting. it self destructs after it does its task: “Within two seconds of `npm install`, the malware was already calling home to the attacker's server before npm had even finished resolving dependencies.”

[https://www.stepsecurity.io/blog/axios-compromised-on-npm-malicious-versions-drop-remote-access-trojan](https://www.stepsecurity.io/blog/axios-compromised-on-npm-malicious-versions-drop-remote-access-trojan)

> ### 13:13 — Adithya Kumar (me)
> 
> bruhhh yee the npm hack is crazy networkchuck made a video about it earlier
> 
## 13:13 — Adithya Kumar (me)

is there a way to incoming task requests from our internal system (like a simple JSON API that returns tasks with: task_description, required_skills, max_payout, deadline, location_preference)

## 17:46 — Adithya Kumar (me)

Two-Channel Audio Feature Spec
Problem
Buyers want two separate audio files from a single conversation — each capturing one speaker's proximal voice + ambient room noise during silences (simulating a phone call scenario, like a customer service agent/customer interaction).
User Flow
**User A** opens app → imports contacts → invites **User B** to a call
User B joins (must also have the app installed)
Both users connect via **VoIP call** within the app
Each device records its own mic independently — capturing the user's primary voice + whatever background/room noise the mic picks up
1. Two separate audio files are uploaded to the backend, tagged to the **same conversation/session ID**
Backend Requirements
• **VoIP infrastructure** — hosted via GCP or AWS
• **Conversation ID** — metadata tag linking both audio files as the same session
• No diarization, no splicing, no audio manipulation — each file is left as-is
• Both files should be the same length (co-start/co-end with the call)
Task/Prompt Admin Side
• No special task type needed beyond standard creation — just tailored instructions telling users to make a call with a partner
Payouts
• For B2B/partner uploads: manual invoice + bank transfer
• For app users: standard app payout flow
Open Questions
Exact buyer requirements need to be written down and confirmed (Daniel flagged this)
Do buyers need timestamp metadata (speaker turn markers)?
Scripts vs. free conversation — what do we instruct users to talk about?
• Estimated build time: **~1–2 weeks** (most infra already exists — recording, upload, app store approval done)
