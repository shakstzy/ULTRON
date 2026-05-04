---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:36-05:00'
ingest_version: 1
content_hash: blake3:086ad0796462ab6b789db5d2111cf76fe7e1a66a323354d3f6f7c8e551ae6041
provider_modified_at: '2026-04-06T10:56:07-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2026-04-02'
date_range:
  first: '2026-04-02T09:25:14-05:00'
  last: '2026-04-06T10:56:07-05:00'
message_count: 3
thread_count: 1
participant_count: 2
participants:
- slug: sydney
  slack_user_id: U04QMPSF03Y
  display_name: sydney
  real_name: sydney
  email: sydney@eclipse.builders
- slug: vj
  slack_user_id: U09UCLZ9U1E
  display_name: VJ
  real_name: VJ
  email: vedant@eclipse.builders
attachments:
- id: F0AQESS6CF7
  filename: Screenshot 2026-04-02 at 7.55.07 PM.png
  size_bytes: 152818
  mime: image/png
  sender_slug: vj
  sent_at: '2026-04-02T09:25:14-05:00'
  permalink: https://eclipse-labs.slack.com/files/U0A993YPZ1Q/F0AQESS6CF7/screenshot_2026-04-02_at_7.55.07___pm.png
  private_url: https://files.slack.com/files-pri/T04472N6YUU-F0AQESS6CF7/screenshot_2026-04-02_at_7.55.07___pm.png
deleted_messages: []
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2026-04-02 (Thursday)

## 09:25 — VJ

This would be under the tasks tab correct? Where we could say 2 user required for this task, as it would be under conversational task.

Also as we are fine with the bg noise when the users are recording their call conversation, do we want them to tag or label certain audio that might be detected in the bg like a dog bark or a siren? or maybe run an AI in the back to recognise these voices, so users don't have to do much work to write and label they could just click yes/no for ex. below ss.

[image: A screenshot of an AI audio detection interface displaying a frequency waveform with highlighted segments for "Dog Bark Detected" in blue and "Child Voice" in purple. The interface lists verified events including a "Dog bark at 4.2s - 5.1s" and a "Child voice at 7.8s - 9.2s" saying "100 cheeseburgers," both accompanied by orange checkmark buttons.]

## 09:25 — VJ

@Adithya Kumar (me)

## 11:27 — VJ

**Brief how it works?**

1. Invite a friend who has the app.
2. Get connected through a 'Private Room'.
3. Talk for 10 minutes about a random topic we give you.
4. Hang up and get paid.
**The "Step-by-Step" User Journey**

Step 1: Recruitment
• **User A** sees the task: "Talk with a friend/Have a conversation about (topic) with another user" under the 'Available Tasks' section.
• **Action:** They click "Start Task" which takes them to the task screen where we show "Share Invite Link" or "Copy Room Code." They send it to their friend via WhatsApp.
> "Room" logic:
> 1. **Host** clicks "Start Task" → Gets a **Room Code** (e.g., 1234).
> 2. **Host** tells **Friend via Whatsapp/iMessage or whatever**: "Enter code 1234 in the app." and send them a join link where the User B enters the code.
> Once the Friend enters the code, the app says: *"Connection established. Your microphones will now record locally for maximum quality."*
Step 2: The Sound Check (Crucial for Health/Quality)
• Before the call starts, show a **moving volume bar** for both users. (we can use what we have currently for that)
• **Copy:** *"Testing... speak into your phone. Stay in a quiet room with some background noise allowed, no bg music"*
Step 3: The Call (Recording State)
Instead of a blank screen, show a timer counting up to 10:00 (towards the bottom, we can use the same design for the 3,2,1 counter currently)
Below the timer, show the **Topic to chat about**. (This is something which user's can 'X' out.

> Note: Since it's not scripted, users often freeze up and don't know what to say.
> • The "Lame" Fix: On the calling screen, show a "Topic Card" that changes every 2 minutes or stays static.
> • Examples: "What is the best meal you've ever had?" or "If you won the lottery tomorrow, what's the first thing you'd buy?"
> • Why this helps: It ensures there is no "dead air," which makes the data better
Step 4: The Wrap-Up
• At the 10-minute mark, a small vibration/haptic or "Sound" tells them they've met the requirement.
• **Copy:** *"Goal reached! You can keep talking or hang up now to submit."*
@sydney does this approach work or are we missing something?

> ### 12:55 — sydney
> 
> I like this approach. let's make the topic card optional so only show it if theyre looking for topics. i think if we show it by default, theyre going to think that that's what they have to use in order to get paid. I like the minimum 10min idea, cause the data probably isn't super helpful if under 10min. let's just make sure they dont think 10min is the cap and im worried the timer might give off that vibe
> 
> ### 13:00 — VJ
> 
> but again as a user I might be confused like how long do I have to talk for? am I getting paid per hour? or a flat fee?
> 
> ### 13:01 — VJ
> 
> if per hour then, we don't have to have a sound
> 
> ### 13:32 — sydney
> 
> what if we count up in $$
> 
> ### 13:33 — sydney
> 
> "estimated earnings: $X.XX"
> 
> ### 13:33 — VJ
> 
> well but we should still have an per minute price or hourly price mentioned
> 
> ### 13:34 — VJ
> 
> and then we can show est. earnings as well
> 
> ### 13:34 — sydney
> 
> $12.5/hr for each
> 
> ### 13:34 — VJ
> 
> ok
> 
> ### 13:35 — sydney
> 
> we dont have to hardcode it tho. it will be the rate specified in the task creation dashboard
> 
> ### 13:35 — VJ
> 
> yep it'll go in the place of the price section
> 
> ### 23:36 — VJ
> 
> the approval cycle for these kinda tasks would be faster imo like within a few hours, or we can't define that yet?
> 
> ### 04:02 — VJ
> 
> @sydney
> 
> ### 10:56 — sydney
> 
> cant define it yet
>
