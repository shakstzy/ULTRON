---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:e2fec3fd0873a31bf290f5ed2e13668bcc72dba739ecb35ac1b10903e5e50342
provider_modified_at: '2025-06-06T10:45:52-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-06-05'
date_range:
  first: '2025-06-05T01:22:21-05:00'
  last: '2025-06-06T10:45:52-05:00'
message_count: 5
thread_count: 2
participant_count: 4
participants:
- slug: sydney
  slack_user_id: U04QMPSF03Y
  display_name: sydney
  real_name: sydney
  email: sydney@eclipse.builders
- slug: david
  slack_user_id: U04UCUX2Y8G
  display_name: David
  real_name: David
  email: david@eclipse.builders
- slug: michael
  slack_user_id: U07BK2MA1NE
  display_name: Michael
  real_name: Michael Winters
  email: michael@eclipse.builders
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

# #engineering — 2025-06-05 (Thursday)

## 01:22 — David

<!subteam^S07JZUU6YS0> - Please add your github email address to this document. We are going to do a airdrop dry run very soon. Thanks!

https://docs.google.com/document/d/1gycJBuTomBCsm3PAmtqwIF8MN-OZINSN-8ip-zla-sY/edit?tab=t.0

> ### 15:21 — David
> 
> @sydney looks like we've gathered a decent number of emails
> 
> ### 15:21 — David
> 
> thanks everyone
> 
> ### 15:23 — sydney
> 
> thanks david + team!
> 
## 10:17 — Ben

The OP stack path

> ### 10:17 — Ben
> 
> I had a detailed discussion about “embracing” the OP stack path w @Olivier Desenfans today, @Michael @David
> 
> ### 10:18 — Ben
> 
> we need to map this out and enumerate very clearly the parts we’d need to change w bridge-related changes, SVM-related parts, and the stuff that touches Kona/Celestia
> 
> ### 10:18 — Ben
> 
> I don’t want to go into this without a very clear plan
> 
> ### 10:19 — Ben
> 
> I’ve asked for a similarly clear “alternative path” that involves us building out not only the missing parts leading to the fraud proof subsystem, but also forced/escape bits just so that we have a clear comparison
> 
> ### 10:20 — Ben
> 
> it may take more time to do adequate experimentation w OP stack to make this plan, but this time is worth it; having said that, continuing to focus on CD0 seems warranted @Michael
> 
> ### 16:26 — Michael
> 
> @Ben makes sense. For OP, we'd want to do the same thing we did when investigating Kailua, particularly the L2 touchpoints. What aspects of the stack would we need to re-implement for SVM, and what will be the data model for cross-chain communication (SVM types to EVM types). The best case is we can leverage most of the existing Ethereum infrastructure with minimal changes.
>
> The cd1 iteration makes sense to me too. It will help us establish the on-chain data model for da-bridging and da-proving, and can simultaneously provide a simple L1 anchor for the full node via the index blob.
> 
> ### 16:35 — Michael
> 
> Kailua and OP are deep pools - and the idea of extending them or making them more useable is interesting. For example, it would be really nice if we could lift the Kailua dispute framework into a library that the DA proving system could use. My guess is that the OP investigation will reveal similar challenges and opportunities.
>
> The "out of the box" idea seems unrealistic to me at a high level, and my guess is that both Kailua and OP are probably going to require significant modification to integrate with SVM. So I'm also wondering what kinds of programs we'll need to deploy on Eclipse to interface with OP and Kailua. If we can find a way to get all this running smoothly between the chains it's a very cool technology.
> 
> ### 10:45 — Ben
> 
> yes, nothing is quite out of the box; let’s see which path is easier
> 
## 12:04 — David

Meeting running over feel free to start standup.

## 12:04 — Michael

https://meet.google.com/zwa-wecw-ifj?authuser=0

## 12:25 — Ben

learning session on DeFi starting in a few minutes
Video call link: https://meet.google.com/ehn-pfwp-pge
