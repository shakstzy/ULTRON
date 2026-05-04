---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:5e8ca9e306acd1e90625e361f38b545721573c583d96d89960e554da26908bb2
provider_modified_at: '2025-06-03T02:14:31-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-06-02'
date_range:
  first: '2025-06-02T12:11:31-05:00'
  last: '2025-06-03T02:14:31-05:00'
message_count: 3
thread_count: 1
participant_count: 4
participants:
- slug: bm
  slack_user_id: U055RJ51URE
  display_name: BM
  real_name: BM
  email: bm@eclipse.builders
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
- slug: julien
  slack_user_id: U07V99QMTV5
  display_name: julien じゅりえん
  real_name: Julien Tregoat
  email: julien@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-06-02 (Monday)

## 12:11 — BM

We have completed upgrading all of our nodes to v1.18.26.3, and all Luganodes nodes have also been upgraded to v1.18.26.3. This means the upgrade process is now fully complete.

> ### 12:12 — Michael
> 
> amazing work @BM and eng team getting 1.18.26 across the line !
> 
> ### 12:12 — BM
> 
> If anyone/partners encounters any issues, please contact DevOps. Thanks.
>
> P.S. We are currently aware of a performance issue on the archive node when accessing historical data.
> https://eclipse-labs.slack.com/archives/C07KEKU8LU8/p1748600988086159
> 
> ### 15:37 — julien じゅりえん
> 
> ballin. @BM is there any migration info we should add to the “running a node” doc or was that already done
> 
> ### 02:14 — BM
> 
> I’ve already updated [the doc](https://eclipsebuilders.notion.site/How-to-run-mainnetbeta-RPC-node-binary-tarball-1664a02308308031901deb8889b2bc21?source=copy_link). Based on the latest cluster gossip information, in addition to us and Luganodes, 2 of other partners(i'm not sure who it is) have also started upgrading their nodes.
> 
## 14:20 — Ben

folks, as mentioned last week, please **make sure to get your manager’s approval** before you plan any vacation — on Slack is fine, but don’t assume it’s a given — we’re trying to plan ahead and to balance a number of priorities

## 14:21 — Ben

This week’s learning session will be @terry and @fikunmi talking about the DEX landscape: *Defi and related market making explained* — please join on Thursday at the usual time
