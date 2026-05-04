---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:33-05:00'
ingest_version: 1
content_hash: blake3:882082495fff69305d227a1c5a9b4df1e2c52cf6b8f96f484a23b7fe0c698a6d
provider_modified_at: '2025-05-14T18:06:51-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-05-09'
date_range:
  first: '2025-05-09T07:22:16-05:00'
  last: '2025-05-14T18:06:51-05:00'
message_count: 2
thread_count: 1
participant_count: 4
participants:
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
- slug: djordje-simovic
  slack_user_id: U07H81TM3B3
  display_name: Djordje Simovic
  real_name: Djordje Simovic
  email: djordje@eclipse.builders
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

# #engineering — 2025-05-09 (Friday)

## 07:22 — Alex Petrosyan

Record and Replay

> ### 07:22 — Alex Petrosyan
> 
> We have a few outstanding issues for how it works right now.
> 
> ### 07:23 — Alex Petrosyan
> 
> It's a bit too tightly coupled to the code that is in `solar-eclipse` limiting its usefulness as a testing tool
> 
> ### 07:23 — Alex Petrosyan
> 
> So there's two directions that I would like to take this in.
> 
> ### 07:24 — Alex Petrosyan
> 
> 1. We can try to decouple this from Agave, and make sure that all the code that we need to run record and replay with a reasonably compatible version is in the same repo. Or come up with a better compilation strategy.
> 
> ### 07:24 — Alex Petrosyan
> 
> 2. Start work on fidelity testing.
> 
> ### 07:25 — Alex Petrosyan
> 
> For the latter, I would like us to have a range of blocks spanning a month be broken down into representative edge cases.
> 
> ### 07:25 — Alex Petrosyan
> 
> If we had a 20x speedup, we could just do all the blocks, but reality is, we only need a few specific regimes: stress, idle, and a good mix of transactions.
> 
> ### 07:26 — Ben
> 
> @Djordje Simovic ^
> 
> ### 09:10 — Djordje Simovic
> 
> Replay project is strictly tied to agave or agave forks - if you intend on doing similar rnr on your custom client I suggest starting a fresh project instead
> 
> ### 09:11 — Alex Petrosyan
> 
> Fidelity testing it is, then
> 
> ### 09:13 — Ben
> 
> so what scenarios, @Alex Petrosyan?
> 
> ### 09:15 — Alex Petrosyan
> 
> We need:
> • Stress, so something like $TRUMP
> • Idle, where we have a small amount of transactions
> • Average case load, where we have one transaction touching most programs that were calling every program in  February.
> 
> ### 09:15 — Alex Petrosyan
> 
> • Major feature activations
> 
> ### 09:15 — Alex Petrosyan
> 
> • Major transitions to different client binaries
> 
> ### 09:22 — Alex Petrosyan
> 
> We can use @BM’s list for major feature activations as well
> 
> ### 16:39 — Ben
> 
> @Djordje Simovic can you update us on throughput simulations here?
> 
> ### 18:06 — Djordje Simovic
> 
> I’m building a low contention simulation to test max tps for the fast replay module - I’ll post numbers here likely tomorrow (or Friday)
> 
## 20:50 — Michael

core engineering update - great progress on component upgrades and security :efire:
• 1.17.31 to 1.18.26 upgrade working in the test harness (shoutout @BM !)
• v2.1.0 bridge components testing plan in flight
• multisig deposit relayer staged, improved withdraw security, and documentation
• great discussions on the stage 0 completion and stage 1 roadmap
