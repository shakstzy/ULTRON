---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:d6e8c13d238750f06c8dc3f4ab48e568c5755726567168fb24fdb1d63f06b083
provider_modified_at: '2025-07-12T15:35:12-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-07-11'
date_range:
  first: '2025-07-11T11:05:16-05:00'
  last: '2025-07-12T15:35:12-05:00'
message_count: 4
thread_count: 1
participant_count: 4
participants:
- slug: alex-petrosyan
  slack_user_id: U05RB714333
  display_name: Alex Petrosyan
  real_name: Alex Petrosyan
  email: alex@eclipse.builders
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
attachments: []
deleted_messages: []
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-07-11 (Friday)

## 11:05 — Alex Petrosyan

<!here> Standup

## 11:05 — Alex Petrosyan

https://meet.google.com/hdw-zmin-uyu?authuser=0&pli=1

## 14:34 — Michael

I've merged the span sequence implementation for the da-bridge after testing with our [celestia-mainnet-test-node](https://celenium.io/address/celestia1hmpar250ealnzyhwjul6n58vd325fxjlkk9ane?tab=transactions). The updated publisher indexes span sequences and keeps up with the chain. The next step for the da-bridge is the index blob and gateway integration.

https://github.com/Eclipse-Laboratories-Inc/syzygy-celestia-publisher/pull/50

## 15:31 — Rob

@Michael I want to land on type/naming finalization for L1 so I can refactor it one more time. We should be close to confident about it soon.

> ### 19:40 — Michael
> 
> @Rob @Samadhi (Jay) span sequence looks good - I followed the contract's definition for the celestia-publisher.
> ```/// @notice A span sequence is used reference a blob submission to Celestia
> /// @param height The Celestia height in which the blob was included
> /// @param startIndex The start index of the span in the square
> /// @param numShares The number of shares in the span
> struct SpanSequence {
>     uint128 height;
>     uint64 startIndex;
>     uint64 numShares;
> }```
> for batchHeader, this should work
> ```/// @notice The header of a batch
> /// @param prevBatchHash The hash of the previous batch
> /// @param indexBlobHash The hash of the index blob
> /// @param l2StartSlot The starting slot that contains the first L2 block in the batch
> /// @param l2EndSlot The ending slot that contains the last L2 block in the batch
> /// @param spanSequences The span sequence for the batch index blob
> struct BatchHeader {
>     bytes32 prevBatchHash;
>     bytes32 indexBlobHash;
>     uint256 l2StartSlot;
>     uint256 l2EndSlot;
>     SpanSequence spanSequence;
> }```
> lmk what you guys think. Also updated the doc strings.
> 
> ### 20:10 — Samadhi (Jay)
> 
> I thought Rob's latest no longer has l2 start and end slots. Or did we decide to keep them for reconstruction purposes
> 
> ### 20:11 — Samadhi (Jay)
> 
> I think the indexBlobHash may no longer be necessary in the new system
> 
> ### 20:20 — Rob
> 
> ```batchhash => blobCommitHash
> batchRoot => blobHash (indexBlobHash)```
> I'd extrapolate from that to `prevBlobCommitHash`
>
> This renames the ambiguous `batchHash` we use as a UID to a meaningful value in celestia that is *also* the UID in L1.
>
> To @Samadhi (Jay) observation. i do recall the discussion about possible removal of the L2 slot range. It's acceptable to me to leave it in if it's useful metadata, but also acceptable to remove it if it's useless. The origin there is a first approximation, not deep thought. I have no strong feeling either way, but we should construct our rationale and then execute.
> 
> ### 21:32 — Michael
> 
> Yes we definitely want the start and end slots as utility for the full node and transparency of what is being posted.
> 
> ### 21:35 — Michael
> 
> I don't think we need any hashes on L1, just the span sequence of the index blob. You could always get that data and compute the hash.
> 
> ### 15:35 — Rob
> 
> L1 has its own organization needs, like previous "hash/id" to maintain internal organization and a unique identifier to find them. Those don't go away but they're subject to naming disambiguation and pre-image definition.
>
> The payload is a separate concern. It currently contains one hash, called `batchHash` which was thought to be, probably, useful in the future. That may or may not be the case right now. That depends on whether the host/guest/verifier relies on it. If I had to guess, I'd say "No?" but I don't have great top-of-mind awareness of how that's evolving. @Samadhi (Jay)?
>
> Neither of those values has ever had a defined pre-image definition. Like, "this is what you hash and how you hash it". L1 is agnostic about how it's done. The rename/mapping I posted above is a proposal to resolve the method and meaning, couple it more tightly to the Celestia world and name it intuitively so our connections are easier to follow.
>
