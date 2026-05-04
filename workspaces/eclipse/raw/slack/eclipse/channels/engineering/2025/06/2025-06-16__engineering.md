---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:68a4947079376d54d39639b65411dbc7121dea390d0021d8d927137bb7d94985
provider_modified_at: '2025-06-16T15:00:20-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-06-16'
date_range:
  first: '2025-06-16T10:28:40-05:00'
  last: '2025-06-16T15:00:20-05:00'
message_count: 1
thread_count: 1
participant_count: 3
participants:
- slug: samadhi-jay
  slack_user_id: U06LP8VPHNE
  display_name: Samadhi (Jay)
  real_name: Samadhi
  email: jay@eclipse.builders
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
edited_messages_count: 1
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-06-16 (Monday)

## 10:28 — Olivier Desenfans

@Samadhi (Jay) I have a basic version of ZK exclusion proofs going [here](https://github.com/Eclipse-Laboratories-Inc/celestia-zk-fraud-proofs/blob/0a9b69221bd37f178a8296ae8daef3ea6957c0b1/methods/guest/src/bin/da_bridge.rs) (I created a dedicated repo), don't hesitate to take a look in advance and we can chat async before the meeting of tonight. I still have a few things to do (handle the invalid block height problem, update the docs, handle some error cases) but this should give you an insight of how exclusion proofs work with the sequence of spans method and Blobstream + Steel.

> ### 10:34 — Samadhi (Jay)
> 
> nice looking great. I'll keep looking it over
> 
> ### 10:35 — Olivier Desenfans
> 
> Do you already have a synced Mocha Celestia node? It's useful to run it. I need to update the docs for instructions but I can write that as soon as you want to run it, ping me.
> 
> ### 10:38 — Samadhi (Jay)
> 
> ya I'd like to run it
> 
> ### 10:38 — Samadhi (Jay)
> 
> I've been using https://frosty-thrilling-needle.celestia-mainnet.quiknode.pro/dae50c40249cbdfe9998ee72ec8487fe607e727d/ which is mainnet
> 
> ### 10:38 — Olivier Desenfans
> 
> Careful that the value at the end is an API key :stuck_out_tongue:
> 
> ### 10:39 — Olivier Desenfans
> 
> You'll need a Mocha node in any case, you can either run your own or you can create a second account on Quicknode.
> 
> ### 10:39 — Olivier Desenfans
> 
> Give me 30 minutes to update all this in the meantime
> 
> ### 11:50 — Olivier Desenfans
> 
> Added some minimal docs in the README at [this commit](https://github.com/Eclipse-Laboratories-Inc/celestia-zk-fraud-proofs/tree/01240ff1613222bafc1c65925ba62806b0d27998) @Samadhi (Jay)
> 
> ### 11:51 — Olivier Desenfans
> 
> There are a few issues that I need to fix with the host but you can already try use cases 2 and 3, these are expected to work properly (=fail) because they challenge valid index blobs.
> 
> ### 11:52 — Olivier Desenfans
> 
> Ah damn I forgot I still have a local dependency, fixing that as well
> 
> ### 12:48 — Olivier Desenfans
> 
> Fixed, you should now be able to compile it.
> 
> ### 13:30 — Rob
> 
> Not pressure, but please let me know if there are L1 .sol resources/examples in that repo. Elsewhere? Future? I just want to be caught up before we meet later.
> 
> ### 13:45 — Olivier Desenfans
> 
> There's [this file](https://github.com/Eclipse-Laboratories-Inc/celestia-zk-fraud-proofs/blob/96f056aa0e03ab62a427a02fbcb79f881cb3541d/contracts/src/Counter.sol) that implements the necessary logic to verify the proof and increments a counter if the proof is correct. I still need to add the index blob as public input there for the demo.
> 
> ### 13:57 — Olivier Desenfans
> 
> I didn't have the time to implement an example that implements exclusion checks on-chain since Thursday, but the inclusion example is fairly similar.
> 
> ### 15:00 — Olivier Desenfans
> 
> For reference during the call:
>
> Implemented:
> • DA challenge host + guest program, can challenge index blobs and their content.
> Todo:
> • DA challenge currently works on share indexes, not bad block heights. Currently implementing this.
> • Integration tests, we need a robust way to test every edge case.
> • Missing edge cases:
>     ◦ Invalid share range for the index blob, ex: unaligned shares (the host currently fails on this)
>
