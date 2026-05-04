---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:33-05:00'
ingest_version: 1
content_hash: blake3:3c2e5e20752dc111be5548d8f95a108b2f937714adf216b180222cb1b75cc26a
provider_modified_at: '2025-05-13T16:55:47-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-05-12'
date_range:
  first: '2025-05-12T10:13:40-05:00'
  last: '2025-05-13T16:55:47-05:00'
message_count: 2
thread_count: 2
participant_count: 7
participants:
- slug: kayla
  slack_user_id: U04F1UG1HC7
  display_name: Kayla
  real_name: Kayla Bu
  email: kayla.bu@eclipse.builders
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
- slug: nagu
  slack_user_id: U07M6CY18P2
  display_name: Nagu
  real_name: Nagu
  email: nagu@eclipse.builders
- slug: fikunmi
  slack_user_id: U07RFM6MP9D
  display_name: fikunmi
  real_name: Fikunmi Ajayi-Peters
  email: fikunmi@eclipse.builders
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

# #engineering — 2025-05-12 (Monday)

## 10:13 — Alex Petrosyan

Some [problems](https://github.com/rust-lang/rust/issues/140933) that we've ran into. Any user of `eclipse-crypto` be advised.

> ### 10:24 — fikunmi
> 
> It's kinda funny seeing bugs in large codebases
> Any idea what the actual bug is?
> 
> ### 10:35 — Alex Petrosyan
> 
> Somehow related to `sha3`. Maybe it rethrows an SIGILL as an exception during optimisation
> 
> ### 13:36 — Bernhard Kauer
> 
> It is located in the LLVM optimizer.  It produces invalid SIMD code that the register allocator can not fullfill.  It therefore triggers an assertion.
> 
> ### 13:38 — Bernhard Kauer
> 
> One reason for this bug is that `sha3` is a relatively new ARM CPU extension. And this is a corner case: we could trigger it only with u64, a reference to an array and a rotate-right.
> 
> ### 13:52 — Bernhard Kauer
> 
> And the instruction it wants to generate here is an `xar`
>
>  https://developer.arm.com/documentation/ddi0602/2022-03/SIMD-FP-Instructions/XAR--Exclusive-OR-and-Rotate-
> 
## 12:41 — Kayla

what's the minimum number of confirmation blocks that can confirm transactions on mainnet?

> ### 18:08 — David
> 
> @fikunmi or @daniel maybe can double check this for me, but I think Solana's `finalized` commitment level should serve this purpose, which should be 32 blocks.
> 
> ### 18:09 — David
> 
> They can alternatively use the same number of blocks as they already do for Solana.
> 
> ### 18:10 — David
> 
> They can alternatively use what they already use for Solana
> 
> ### 18:38 — Kayla
> 
> super helpful thanks david!
> 
> ### 18:39 — David
> 
> If they use something much larger for their solana integration please let me know
> 
> ### 04:05 — Nagu
> 
> This, I think, is actually a tricky question for a rollup architecture like ours because of semantics.
>
> The minimum number of confirmation blocks on the Eclipse mainnet to confirm a transaction is likely 1 block, as this represents the inclusion of the transaction in a batch that is published to Celestia and committed to Ethereum.
>
> This initial confirmation is subject to the optimistic rollup’s challenge period (7 days), during which fraud proofs can be submitted. Final settlement on Ethereum may require additional block confirmations (e.g., 12–32 on Ethereum), but this is not specific to Eclipse’s block production.
> 
> ### 06:42 — fikunmi
> 
> Err. Depends on the app. A Solana block is considered rooted when 31 blocks have been confirmed on it and our API says the same thing but our cluster is very small and we don’t have very long fork graphs. 16 is more than enough.
>
> When we stop doing consensus then we can move to block time/ time taken to post a batch.
> 
> ### 13:02 — Kayla
> 
> got it, thank you both for this - this q was from a CEX who's integrating with our mainnet - i'm guessing they're asking to  ensure they only process finalized txns for deposits, withdrawals, trades
> 
> ### 13:03 — Kayla
> 
> what's the safest response with that context (16, 32)?
> 
> ### 13:05 — David
> 
> Yea I sort of figured being on the longer side at 32 would be okay for that purpose. What do you guys think?
> 
> ### 16:50 — Ben
> 
> I assume being conservative works for your purposes, @Kayla?
> 
> ### 16:55 — Kayla
> 
> yup thanks - let them know 32, seems to work for them
>
