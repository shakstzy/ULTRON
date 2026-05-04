---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:33-05:00'
ingest_version: 1
content_hash: blake3:7ad1ede4a3ba30e29aeaaeba86eafc53961e4ec135215c744a322e257ef4273e
provider_modified_at: '2025-05-20T06:36:46-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-05-06'
date_range:
  first: '2025-05-06T00:30:43-05:00'
  last: '2025-05-20T06:36:46-05:00'
message_count: 2
thread_count: 2
participant_count: 6
participants:
- slug: david
  slack_user_id: U04UCUX2Y8G
  display_name: David
  real_name: David
  email: david@eclipse.builders
- slug: anmol
  slack_user_id: U07JB3PK9J5
  display_name: Anmol
  real_name: Anmol Arora
  email: anmol@eclipse.builders
- slug: nagu
  slack_user_id: U07M6CY18P2
  display_name: Nagu
  real_name: Nagu
  email: nagu@eclipse.builders
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

# #engineering — 2025-05-06 (Tuesday)

## 00:30 — David

Solana had a Token2022 zero day associated with token2022 confidential tokens  [https://solana.com/undefined/en/news/post-mortem-may-2-2025](https://solana.com/undefined/en/news/post-mortem-may-2-2025)

This shouldn’t affect us but if we do upgrade token2022 we need to be careful of this version and the corresponding ELGamal proof program versions

> ### 01:37 — julien じゅりえん
> 
> @Ben lmfao phew :sweat_smile: not that we were rushing to have this but amusing timing
> 
> ### 03:07 — Ben
> 
> Right @julien じゅりえん
> 
> ### 05:31 — Nagu
> 
> The vulnerability is similar to the Frozen-Heart vulnerability that hit ZK systems (Bulletproofs and Plonk), especially FST (Fiat Shamir Transcripts). The full algebraic components were missing from the FST hash, so someone can forge proofs by replaying the transcripts until you hit the correct commitments.
>
> In general, soundness related bugs in ZK are very difficult catch. You need a combination of things like the Solana’s patch: a single canonical transcript, negative fuzzing, prop testing, differential CI, and if you are going for batching, use performance safe hashing like poseidon or merkle roots.
> 
## 14:35 — Olivier Desenfans

Asking for Diego from Celestia: is this [doc on how to run a mainnet RPC node](https://eclipsebuilders.notion.site/How-to-run-mainnetbeta-RPC-node-19eb6f80e8d34b54838b03995d3f9865) up-to-date (I'd guess not)? And if not, what's the best source?

> ### 20:37 — David
> 
>  It should be, I tagged @BM on the thread
> 
> ### 20:37 — David
> 
> He can help shortly
> 
> ### 20:38 — David
> 
> Also regarding Diego asking for access to Celestia publisher, any idea what the context is?
> 
> ### 20:38 — David
> 
> Happy to grant just not sure what they need it for
> 
> ### 03:11 — Olivier Desenfans
> 
> The verifier is for technical discussions, I think he’s just curious about the publisher
> 
> ### 06:36 — Anmol
> 
> different occasion but same topic:
>
> this repo is private now (https://github.com/Eclipse-Laboratories-Inc/solar-eclipse) but is mentioned in the mainnet rpc node doc, should ideally update
> 
> ### 06:36 — Anmol
> 
> got a [github issue](https://github.com/Eclipse-Laboratories-Inc/dev-docs/issues/7) regarding it
>
