---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:b6008882812ebb86d5961064cc79c728058d410dff4ff3f527fcf15c46a13169
provider_modified_at: '2025-06-20T07:18:07-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-06-19'
date_range:
  first: '2025-06-19T12:03:46-05:00'
  last: '2025-06-20T07:18:07-05:00'
message_count: 4
thread_count: 2
participant_count: 6
participants:
- slug: daniel
  slack_user_id: U04HQ1YK91Q
  display_name: daniel
  real_name: daniel
  email: daniel@eclipse.builders
- slug: vijay
  slack_user_id: U0596K34S4B
  display_name: Vijay
  real_name: Vijay
  email: vijay@eclipse.builders
- slug: alex-petrosyan
  slack_user_id: U05RB714333
  display_name: Alex Petrosyan
  real_name: Alex Petrosyan
  email: alex@eclipse.builders
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
- slug: ben
  slack_user_id: U07UG9EBU4U
  display_name: Ben
  real_name: Ben
  email: ben@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 1
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-06-19 (Thursday)

## 12:03 — Michael

https://meet.google.com/zwa-wecw-ifj?authuser=0

## 12:26 — Ben

Folks, as we are starting to grow, slowly but steadily, as I discussed with various managers over the last several weeks, we’re shaking up the meeting structure for <!subteam^S084X3CG5FZ> a bit. We plan to have 9--10 PST meetings four days a week, but each day will have a theme, as shown below:

> M - no meeting (all hands already there)
> T research+perf
> W core-driven design meeting
> T learning session
> F final weekly <!subteam^S084X3CG5FZ> update - effectively a summary end-of-week report from everyone
This is to serve several goals:
• a slight time adjustment to accomodate those not in PST
• we want to give a chance for individual teams to present to all other <!subteam^S084X3CG5FZ> members — we’ve already had this experience with design meetings from core, learning sessions, etc. Some days will be dedicated to one topics, others will be updates across a range of projects.
• The goal is to raise the bar in terms of what the presenting team does, but only require that once a week. Of course, this will require some preparation, but hey, this is your chance to show off the most exciting thing you’ve been doing to the rest of your colleagues.
• we still want to enable small standups for individual teams, but as we grow, we don’t expect everyone to participate.
We do expect all of <!subteam^S084X3CG5FZ> to be at the four 9-10 meetings mentioned above. I will be updating the Team calendar in coming days. Additionally, individual teams like Core and Research will have their own standup meetings with smaller groups separate from this calendar, at a time they find convenient.

> ### 12:28 — daniel
> 
> is the daily global eng. standup currently at 10am pst impacted by this ?
> 
> ### 12:29 — Ben
> 
> yea, we will shuffle things around to make this work - don’t worry and wait for calendar invites :slightly_smiling_face:
> 
> ### 12:30 — Ben
> 
> @David was saying some folks wanted to do standups later in the day, which this plan would allow for
> 
> ### 12:32 — Michael
> 
> Will there be daily meetings at 9am PT ?
> 
> ### 12:32 — Ben
> 
> 4 days a week
> 
> ### 12:33 — Ben
> 
> out of 7
> 
> ### 12:33 — Michael
> 
> okay, that's a pretty substanial schedule impact.
> 
> ### 12:33 — Michael
> 
> might want to make sure everyone is okay with that.
> 
> ### 12:34 — Ben
> 
> this is the best way we found to satisfy conflicting goals
> 
> ### 12:35 — Michael
> 
> no worries, just want to make sure everyone can make it
> 
> ### 12:36 — Ben
> 
> trying to balance--not easy for @Supragya Raj and @Nagu w the Tue option, but they have been trying their best
> 
> ### 02:33 — Ben
> 
> also @David and @Olivier Desenfans adjusted other standing meetings
> 
> ### 02:33 — Ben
> 
> so we should now be good to go
> 
> ### 02:33 — Ben
> 
> w the updated schedule starting next week
> 
## 14:55 — Vijay

Hey guys, please be there at the meetings that Ben outlined. It is mandatory, and 1 hour of meetings 4 days a week is not a lot to ask. It will be more efficient to collectively reorient around this structure

## 17:50 — Olivier Desenfans

Pretty happy to announce that I now have a sweet Docker Compose setup that launches Celestia, Anvil and Blobstream locally :eyes: It gave me the occasion to check how mature the Blobstream implementation from RISC Zero is, so far it looks fine (excluding some outdated Dockerfile issues).

> ### 18:54 — Alex Petrosyan
> 
> Congrats. This was a huge pain in the early days, because of the troubles that we had. @David can tell you more.
> 
> ### 07:18 — Ben
> 
> Curious to hear more as well @David
>
