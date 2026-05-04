---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:34-05:00'
ingest_version: 1
content_hash: blake3:b98357f686f3347f21634c7c88dd39b5a1fd31d9dbae4afd3b48fa497f73af20
provider_modified_at: '2025-05-29T13:58:25-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-05-23'
date_range:
  first: '2025-05-23T03:51:21-05:00'
  last: '2025-05-29T13:58:25-05:00'
message_count: 6
thread_count: 1
participant_count: 6
participants:
- slug: david
  slack_user_id: U04UCUX2Y8G
  display_name: David
  real_name: David
  email: david@eclipse.builders
- slug: bm
  slack_user_id: U055RJ51URE
  display_name: BM
  real_name: BM
  email: bm@eclipse.builders
- slug: samadhi-jay
  slack_user_id: U06LP8VPHNE
  display_name: Samadhi (Jay)
  real_name: Samadhi
  email: jay@eclipse.builders
- slug: michael
  slack_user_id: U07BK2MA1NE
  display_name: Michael
  real_name: Michael Winters
  email: michael@eclipse.builders
- slug: rob
  slack_user_id: U07HVQQ1MQ8
  display_name: Rob
  real_name: Rob Hitchens
  email: rob@eclipse.builders
- slug: olivier-desenfans
  slack_user_id: U07MEVDH39T
  display_name: Olivier Desenfans
  real_name: Olivier Desenfans
  email: olivier@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 3
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-05-23 (Friday)

## 03:51 — David

:thread: Just synced with @BM about green lighting the 1.18.26 upgrade. @BM will make preparations and start the first set of feature gates tonight. We can use this thread for updates and expected timelines.

> ### 04:11 — BM
> 
> The current mainnet epoch is 178. The upcoming plan is as follows:
> 1. The current epoch is 178: activate [the first batch of feature gates](https://www.notion.so/eclipsebuilders/Solana-Upgrade-Woes-1594a0230830802a8d70c8320c385762?pvs=4#1fb4a023083080dd9444d369e66da966) that have already been removed in v1.18.26.2.
> 2. Epoch 179: launch a new node running v1.18.26.2 to verify whether it can coexist with existing nodes or if it still cause panic.
> 3. Epoch 180: activate[ the second batch of feature gates](https://www.notion.so/eclipsebuilders/Solana-Upgrade-Woes-1594a0230830802a8d70c8320c385762?pvs=4#1fb4a0230830805fa41beaeb0b6a7f16) that are still present in v1.18.26.2 but have been modified.
> 4. Epoch 181: ensure that mainnet is operating normally, and spin up a new v1.18.26 node to test whether it runs correctly.
> 5. Epoch 182, begin upgrading our nodes(including one AWS entrypoint node, one OVH archive node, and one OVH bitz dedicated node).
> 6. Epoch 183: upgrading our remaining nodes(including sequencer node). Also begin notifying partners to start their own upgrade processes.
> • If step 2 confirms that v1.17.31 and v1.18.26 successful coexistence, we might revisit whether this step3&4 is still necessary.
> 
> ### 04:52 — BM
> 
> Assuming epoch lasting 1d 19h 13m 46s, the expected timestamps for epochs 179–185 are:
> ```| Epoch | UTC+0               | UTC+8               | UTC-7               |
> | ----- | ------------------- | ------------------- | ------------------- |
> | 179   | 2025-05-24 13:26:43 | 2025-05-24 21:26:43 | 2025-05-24 06:26:43 |
> | 180   | 2025-05-26 08:40:29 | 2025-05-26 16:40:29 | 2025-05-26 01:40:29 |
> | 181   | 2025-05-28 03:54:15 | 2025-05-28 11:54:15 | 2025-05-27 20:54:15 |
> | 182   | 2025-05-29 23:08:01 | 2025-05-30 07:08:01 | 2025-05-29 16:08:01 |
> | 183   | 2025-05-31 18:21:47 | 2025-06-01 02:21:47 | 2025-05-31 11:21:47 |
> | 184   | 2025-06-02 13:35:33 | 2025-06-02 21:35:33 | 2025-06-02 06:35:33 |
> | 185   | 2025-06-04 08:49:19 | 2025-06-04 16:49:19 | 2025-06-04 01:49:19 |```
> 
> ### 04:53 — BM
> 
> I just activated [the first batch of feature gates](https://www.notion.so/eclipsebuilders/Solana-Upgrade-Woes-1594a0230830802a8d70c8320c385762?pvs=4#1fb4a023083080dd9444d369e66da966). it will active at epoch 179(2025-05-24 12:86:43)
> 
> ### 09:51 — Samadhi (Jay)
> 
> so step 3 would only be the 2 features we found necessary?
> 
> ### 09:52 — BM
> 
> > so step 3 would only be the 2 features we found necessary?
> yes
> 
> ### 12:01 — BM
> 
> Good news! I launched a v1.18.26 node during epoch 178 to verify coexist again, and it still panicked (couldn’t coexist for more than 10 minutes).
> However, after mainnet entered epoch 179, I relaunched the v1.18.26 node, and it's now been coexisting for over 3 hours. I’ll continue monitoring to see if it can stay stable for more than a day.
> 
> ### 12:07 — BM
> 
> If v1.18.26 continues to coexist stably throughout epoch 180 without panicking, we could consider skipping step 3, that is we won’t activate the `commission_updates_only_allowed_in_first_half_of_epoch` and `deprecate_unused_legacy_vote_plumbing` feature gates during this upgrade v1.17.31 to v1.18.26 process.
> 
> ### 05:53 — BM
> 
> Mainnet now in epoch 180, and the v1.18.26.2 mainnet node has been coexisting without any issues so far.
> 
> ### 13:04 — Samadhi (Jay)
> 
> interesting that its running without 11 `epoch_accounts_hash` enabled. Right @BM?
> 
> ### 13:06 — Samadhi (Jay)
> 
> the only other feature that had logic that was put into a feature gate is 14 `commission_updates_only_allowed_in_first_half_of_epoch`
> 
> ### 13:07 — Samadhi (Jay)
> 
> for clarity, 23 `deprecate_unused_legacy_vote_plumbing` was voted yes its "safe" to upgrade but not that its necessary
> 
> ### 13:15 — BM
> 
> > interesting that its running without 11 `epoch_accounts_hash` enabled. Right @BM?
> 11 `epoch_accounts_hash`  has been enabled before.
> 
> ### 13:16 — Samadhi (Jay)
> 
> ok gotcha. So only 14 maybe needs enabling
> 
> ### 13:19 — BM
> 
> Since coexistence is currently stable, should we postpone activating 14 `commission_updates_only_allowed_in_first_half_of_epoch` until after all nodes have been upgraded to v1.18.26?
> 
> ### 13:24 — Samadhi (Jay)
> 
> wouldn't it be better to do with 1 node than all at once?
> 
> ### 13:36 — Samadhi (Jay)
> 
> maybe we don't even have commission updates allowed and thats why its running fine?
>
> Left is 1.18 and right is 1.17. This is the difference in the two. In 1.18 the error check that used to be in the code block becomes gated by the feature
> 
> ### 13:38 — Samadhi (Jay)
> 
> so if we don't currently have comission updates enabled in general then this feature doesn't need to be activated
> 
> ### 13:58 — BM
> 
> > wouldn't it be better to do with 1 node than all at once?
> No, once a feature gate is activated, it takes effect for all nodes on mainnet. That means v1.17.31 nodes and v1.18.26 nodes would follow different commission logic.
> 
> ### 14:05 — Samadhi (Jay)
> 
> Do you know if we have commission updates allowed in general?
> 
> ### 14:37 — BM
> 
> Mainnet has only four voters(one owned by us, three owned by luganodes), control over increasing or decreasing the stake of the four voters is in our hands.
>
> And we have restrictions on allowing new voters to join.
> https://github.com/Eclipse-Laboratories-Inc/solar-eclipse/pull/19
> 
> ### 14:39 — BM
> 
> So i think any voter commission updates are carried out in a planned and intentional manner by us.
> 
> ### 14:43 — Samadhi (Jay)
> 
> ok :+1: 14 is not needed then
> 
> ### 22:51 — David
> 
> @BM can you post a quick update here about the upgrade status that we just synced about today? Thanks!
> 
> ### 13:54 — BM
> 
> all mainnet nodes we owned have been upgraded to v1.18.26.3 now. include:
> AWS
> ```Sequencer x 1
> Entrypoint x 1
> RCP x 1```
> GCP
> ```Archive x 1
> Warehouse x 1```
> OVH
> ```RPC x 1
> BITS dedicated x 3
> Archive x 1```
> Note. Since Backpack's access to historical data caused issues on the archive node, we've temporarily change one of the Bitz nodes to serve as a backpack dedicated node.
> 
> ### 13:58 — BM
> 
> BTW, we skipped step3 in this upgrade. So all our node are upgraded to v1.18.26.3 at epoch 181.
> ```3. Epoch 180: activate the second batch of feature gates that are still present in v1.18.26.2 but have been modified.```
> 
## 12:03 — Michael

https://meet.google.com/zwa-wecw-ifj?authuser=0

## 12:11 — Olivier Desenfans

[What is Kailua](https://www.notion.so/eclipsebuilders/What-is-Kailua-1fc4a02308308009aa9ed3eccbac668d)

## 15:03 — Rob

https://meet.google.com/pif-gucd-qhm?authuser=4

## 17:39 — Michael

weekly core eng update - great progress on key deliverables this week :efire:
• finalized syzygy bridge documentation and forwarded commit to OtterSec for audit quote ([76e6fc6](https://github.com/Eclipse-Laboratories-Inc/syzygy/commit/76e6fc6411b206fc7d8c8c0d2bd9a9211449a0c9))
• continuing work on automatic nullification of fraudulent withdraws (troll enhancement)
• starting work on the full node implementation (celestia types, solana version integration)
• great discussions on Kailua critical path and next steps for the protocol
• validator 1.18.26 upgrade for mainnet in flight - hope to finalize before TGE

## 17:48 — Olivier Desenfans

Hey guys, here are my [handover notes](https://www.notion.so/eclipsebuilders/Holiday-handover-June-2025-1fc4a023083080c3a9edcb061be15054) for my holidays, godspeed on stage 0!
