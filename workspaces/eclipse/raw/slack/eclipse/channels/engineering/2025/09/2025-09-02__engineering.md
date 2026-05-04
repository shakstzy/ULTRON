---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:36-05:00'
ingest_version: 1
content_hash: blake3:0d76c7a8af32f6ac2e2b8b81c55150f61645a3e84e917745a480d7dd7004f0b9
provider_modified_at: '2025-09-04T11:34:30-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-09-02'
date_range:
  first: '2025-09-02T16:57:14-05:00'
  last: '2025-09-04T11:34:30-05:00'
message_count: 1
thread_count: 1
participant_count: 3
participants:
- slug: sydney
  slack_user_id: U04QMPSF03Y
  display_name: sydney
  real_name: sydney
  email: sydney@eclipse.builders
- slug: michael
  slack_user_id: U07BK2MA1NE
  display_name: Michael
  real_name: Michael Winters
  email: michael@eclipse.builders
- slug: cemal
  slack_user_id: U07JEV700QJ
  display_name: cemal
  real_name: cemal
  email: cemal@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 1
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-09-02 (Tuesday)

## 16:57 — sydney

@Michael can you check this withdraw please?
Direction: Eclipse → Ethereum When: 9 days ago Amount: ~0.7082 ETH Tx on Eclipsescan: https://eclipsescan.xyz/tx/5GuHitivtKC267NSANnDrni8LaaXBRFZnW7WAKrnHyBgtVf7HS9NWqVQm4WNxWUXCBJA3arg8PJC4R2FsuYFi5Hu
Destination (L1) address: 0xF82b3a0CD76EF3DcFaF772c27b2a39F1e1915494

On Eclipsescan the instruction shows “Eclipse Bridge: Withdraw” and my balance was debited on Eclipse, but nothing has arrived on Ethereum yet.
My Eclipse Address: 3QNEG55gFsmoJgU5ZBMF35dgSnUt4fyGDYy43sGtMmCo

> ### 18:30 — Michael
> 
> ```2025-09-02T23:27:54.480010Z  INFO eclipse_eth_bridge::eclipse::audit: 60: Withdrawal Confirmed 227467294336: [from=3QNEG55gFsmoJgU5ZBMF35dgSnUt4fyGDYy43sGtMmCo, destination=0xE72068966b7647F50fDcA83644be59c977C3d915, amount=0.70820 ETH]```
> @sydney this withdraw is on-chain. It seems like the user has the wrong destination address in mind.
>
> ```2025-09-02T23:28:49.659486Z  INFO eclipse_eth_bridge::eclipse::audit: 115: Audit completed in 153.31s: 40717 confirmed, 0 queued, 0 errored```
> The audit state is clean for the withdraw system.
> 
> ### 19:13 — sydney
> 
> thanks!
> 
> ### 02:52 — cemal
> 
> @Michael it says this withdrawal has been confirmed, but the api is not returning anything:
>
> ```2025-09-04T07:48:08.104707Z  INFO eclipse_eth_bridge::eclipse::audit: 60: Withdrawal Confirmed 903550883403: [from=EPFw5GiPgh1NcKMReGm1WWdSee83Uu1VgssWxXP3Zf6N, destination=0xFc0E8faa3e71FeB229e3eE05D6DfEf302c5F5CAB, amount=0.12350 ETH]
> 2025-09-04T07:48:08.104746Z  INFO eclipse_eth_bridge::eclipse::audit: 115: Audit completed in 1.19ms: 1 confirmed, 0 queued, 0 errored```
> https://withdraw.api.prod.eclipse.xyz/0xFc0E8faa3e71FeB229e3eE05D6DfEf302c5F5CAB
> https://eclipsescan.xyz/tx/3oiBSA8fDbntLZvZUHQdxKwYA3R4eenQ4oVFXrGdTyaAzJDdLFRWvFPsPuC3Cj54s6Mrsrx6wzG6mMNiTwcWisBY
> 
> ### 11:34 — Michael
> 
> @cemal sent you a DM to resolve
>
