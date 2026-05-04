---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:36-05:00'
ingest_version: 1
content_hash: blake3:2bc09acf7be5758600f6915ba4a09b137851d186ebdc3918088129a65c993cf8
provider_modified_at: '2025-08-13T10:57:57-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-08-11'
date_range:
  first: '2025-08-11T06:51:26-05:00'
  last: '2025-08-13T10:57:57-05:00'
message_count: 4
thread_count: 4
participant_count: 6
participants:
- slug: david
  slack_user_id: U04UCUX2Y8G
  display_name: David
  real_name: David
  email: david@eclipse.builders
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
- slug: supragya-raj
  slack_user_id: U07MHKH4BEW
  display_name: Supragya Raj
  real_name: Supragya Raj
  email: supragya@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 2
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-08-11 (Monday)

## 06:51 — Alex Petrosyan

Sparse availability today. Pulled an all nighter to prevent an electrical fire

> ### 07:58 — Olivier Desenfans
> 
> Good luck, I hope everything's alright now!
> 
## 07:58 — Olivier Desenfans

Do we have a reference HTTP API library that we use in Rust? I see several mentions of `actix-web`, just want to confirm.

> ### 10:42 — Supragya Raj
> 
> I think syzygy uses this. Any reason looking for conformance here?
> 
> ### 10:43 — Supragya Raj
> 
> client: reqwest / hyper maybe. server end could be different
> 
> ### 10:54 — Olivier Desenfans
> 
> I don’t want to multiply crates just for the sake of it
> 
> ### 16:09 — Alex Petrosyan
> 
> Axum or actix web.
> 
> ### 16:10 — Alex Petrosyan
> 
> Actix is older, but faster abd more reliable. Less eronomic though. I would prefer it for internal code.
> 
> ### 16:39 — Olivier Desenfans
> 
> Thanks, haven’t tried axum yet but I’ve gone with actix-web in the meantime. Nothing that an LLM can’t port, worst case =P
> 
> ### 16:40 — Alex Petrosyan
> 
> Axum's only selling point is a slightly higher level API
> 
> ### 16:40 — Alex Petrosyan
> 
> And it's fairly close to actix
> 
## 11:40 — David

Cancelling Wednesday core design sync for this week because we are focusing on audit remediations.

> ### 10:57 — Supragya Raj
> 
> This stands cancelled today?
> 
## 19:48 — Michael

Audit remediation branches for OZ in case anyone is interested to have a look.

CanonicalBridge: https://github.com/Eclipse-Laboratories-Inc/syzygy-canonical-bridge/pull/10
Treasury: https://github.com/Eclipse-Laboratories-Inc/syzygy-canonical-bridge/pull/11

Their feedback on the overall design of our contracts is quite positive!

> The security model relies on a time-locked withdrawal process initiated by a trusted off-chain relayer. When a withdrawal is authorized by the `CanonicalBridgeV3` contract, it enters a 7-day fraud-detection window. During this period, an account holding the `WITHDRAW_CANCELLER_ROLE` can veto the transaction. Users can only claim their ETH from the Treasury after this window has successfully passed, providing a strong safeguard against fraudulent activity. This structure establishes a highly secure bridge by enforcing a strict separation of concerns between logic and custody, implementing a mandatory fraud-detection window for all withdrawals, and leveraging a multi-layered, role-based security model .. Overall, the codebase demonstrated high quality and was supported by a comprehensive test suite. The Eclipse team was highly responsive and collaborative throughout the engagement, contributing to a smooth and efficient audit process.

> ### 13:10 — Rob
> 
> Why Treasury mods *at this time?*
> 
> ### 13:17 — Michael
> 
> For completeness - they asked us to remediate them so we will have their suggestions in a reference branch. We do not need to redeploy the Treasury.
> 
> ### 14:03 — Michael
> 
> @David @Rob I've wrapped up the remediations in OZ defender for the solidity code. I've also updated our tests in a few places so we have 100pct line coverage on tests. I'll let OZ know that we've completed this phase of the solidity audit later today, after a final review of the remediations.
>
