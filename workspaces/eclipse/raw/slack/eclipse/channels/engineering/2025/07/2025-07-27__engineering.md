---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:2823fc7ba88b534260c5d07a6ecc6d67b28a9bc16bff23ba737b32d0ec72972d
provider_modified_at: '2025-07-29T08:47:10-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-07-27'
date_range:
  first: '2025-07-27T07:49:46-05:00'
  last: '2025-07-29T08:47:10-05:00'
message_count: 3
thread_count: 1
participant_count: 4
participants:
- slug: daniel
  slack_user_id: U04HQ1YK91Q
  display_name: daniel
  real_name: daniel
  email: daniel@eclipse.builders
- slug: terry
  slack_user_id: U06QHBRHRQX
  display_name: terry
  real_name: terry
  email: terry@eclipse.builders
- slug: michael
  slack_user_id: U07BK2MA1NE
  display_name: Michael
  real_name: Michael Winters
  email: michael@eclipse.builders
- slug: anmol
  slack_user_id: U07JB3PK9J5
  display_name: Anmol
  real_name: Anmol Arora
  email: anmol@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-07-27 (Sunday)

## 07:49 — terry

Getting tons of DMs about bridge issues

## 11:07 — daniel

@Michael

## 11:42 — Michael

We've had a fix staged on sepolia since the week before last, but we are not moving forward with solidity audits with OZ, so we can't deploy.

> ### 11:44 — daniel
> 
> What do you suggest then?
> 
> ### 11:45 — Michael
> 
> No suggestion at this time, except for users to pay the suggested gas price by the UI.
>
> @Kayla let me know that we've paused on audits last Friday citing other priorities.
> 
> ### 11:55 — daniel
> 
> this is the wallet ui or the app ui ?
> 
> ### 12:42 — Michael
> 
> The app ui will suggest the correct gas price, and users need to accept that price in the wallet ui. metamask seems to be the most reliable. Not all wallets respect the site recommended gas price, so we recommend to use metamask if users encounter issues.
> 
> ### 12:43 — Michael
> 
> All withdraws are claimable, and the bridge audit state is clean.
> ```2025-07-27T17:39:54.265247Z  INFO eclipse_eth_bridge::eclipse::audit: 115: Audit completed in 305.83s: 34070 confirmed, 0 queued, 0 errored  ```
> As of this morning, the current bridge contract has settled 7869.57 ETH (30.1mm USD) since TGE and has 4396.39 ETH (16.8mm USD) of open withdraw authorizations remaining. The Treasury is solvent, the current balance is 14570.37 ETH (55.7 mm USD) which covers all outstanding authorizations.
> 
> ### 08:47 — Anmol
> 
> Does it make sense for us just record a video of us doing it and post on X? Its not unusable just have to pay the gas fee suggested by UI which people cant seem to figure out
>
> @Dylan @nate
>
