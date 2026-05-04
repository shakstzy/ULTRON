---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:c96f9daa5ec45251c658fb79a1f6b146d228adff1cae7e19a124127ea817bc1a
provider_modified_at: '2025-07-31T13:41:08-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-07-30'
date_range:
  first: '2025-07-30T11:59:50-05:00'
  last: '2025-07-31T13:41:08-05:00'
message_count: 1
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
- slug: ben
  slack_user_id: U07UG9EBU4U
  display_name: Ben
  real_name: Ben
  email: ben@eclipse.builders
- slug: bernhard-kauer
  slack_user_id: U08J20E9FPD
  display_name: Bernhard Kauer
  real_name: Bernhard Kauer
  email: bernhard@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-07-30 (Wednesday)

## 11:59 — Bernhard Kauer

How does the withdrawal process work today without fraud-proofs?

> ### 12:01 — Bernhard Kauer
> 
> I would assume, that there is a trusted entity that forwards withdrawals from the L2 to the L1. And the L1 withdrawal contract simply trusts these inputs. Is this correct?
> 
> ### 12:14 — Alex Petrosyan
> 
> https://www.notion.so/eclipsebuilders/Withdrawals-Spec-V0-da73712ef51c42c48f2343b1dd7394b7
> 
> ### 12:14 — Alex Petrosyan
> 
> It's a bit out of date, but this was the original design idea
> 
> ### 14:00 — Michael
> 
> > I would assume, that there is a trusted entity that forwards withdrawals from the L2 to the L1. And the L1 withdrawal contract simply trusts these inputs. Is this correct?
> it is a trusted bridge yes, subject to a 7-day fraud window in which withdraws can be nullified. there is not a way to do provable withdraws on the L2 without an L2 state root, which is why we consider state root integration to be a blocker for the progress of the protocol. as far as the assurances and trust assumptions in the bridge, we've got pretty extensive technical documentation in [syzygy](https://github.com/Eclipse-Laboratories-Inc/syzygy).
> 
> ### 05:33 — Ben
> 
> but this is the entire state at a specific height or a subset of the state, @Michael?
> 
> ### 05:33 — Ben
> 
> meanwhile, block-level is clearly the goal of others, i.e.
> 
> ### 12:04 — Michael
> 
> @Ben Yep, this is exactly what we were discussing on the Design call yesterday. For withdraws, the requirement is there must be something provable on the the L1 regarding the state of the Eclipse bridge program - either entire chain state or a withdraw state subset is sufficient.
> 
> ### 13:41 — Bernhard Kauer
> 
> For now I will assume that there's a hash of the entire state available for every block, as we know that's fast enough to calculate. That should simplify it slightly.
>
