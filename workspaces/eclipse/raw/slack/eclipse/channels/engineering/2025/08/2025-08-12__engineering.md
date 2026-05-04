---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:36-05:00'
ingest_version: 1
content_hash: blake3:aa5b510a5e0156bb335fe6f19174aabd31cc0e5dc32f7f6d1da4672284f496d0
provider_modified_at: '2025-08-15T10:42:15-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-08-12'
date_range:
  first: '2025-08-12T09:52:17-05:00'
  last: '2025-08-15T10:42:15-05:00'
message_count: 2
thread_count: 2
participant_count: 4
participants:
- slug: yuri-albuquerque
  slack_user_id: U05TRBZNAMB
  display_name: Yuri Albuquerque
  real_name: Yuri Albuquerque
  email: yuri@eclipse.builders
- slug: samadhi-jay
  slack_user_id: U06LP8VPHNE
  display_name: Samadhi (Jay)
  real_name: Samadhi
  email: jay@eclipse.builders
- slug: supragya-raj
  slack_user_id: U07MHKH4BEW
  display_name: Supragya Raj
  real_name: Supragya Raj
  email: supragya@eclipse.builders
- slug: ben
  slack_user_id: U07UG9EBU4U
  display_name: Ben
  real_name: Ben
  email: ben@eclipse.builders
attachments: []
deleted_messages: []
edited_messages_count: 0
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-08-12 (Tuesday)

## 09:52 — Ben

we’re doing an async update today w some people OOO [here](https://www.notion.so/eclipsebuilders/Research-and-Performance-24d4a02308308071b754c2370b97f5bf?source=copy_link)

> ### 11:10 — Ben
> 
> @Supragya Raj need your update
> 
> ### 11:11 — Supragya Raj
> 
> Oh okay... I was in meeting just now
> 
> ### 11:11 — Supragya Raj
> 
> Will update
> 
## 12:24 — Yuri Albuquerque

@Samadhi (Jay) can you please review when you have the time? https://github.com/Eclipse-Laboratories-Inc/syzygy/pull/497/files

> ### 12:30 — Samadhi (Jay)
> 
> ya I'll take a deeper look a little later and run the tests. What is compare_instructions_and_stored_message meant for exactly?
> 
> ### 12:32 — Yuri Albuquerque
> 
> @Samadhi (Jay) when a relayer computes a instruction, it sends this instruction to squads to store it so it can wait for approval. So I compare the computed instruction with the one that is stored in squads to be sure another relayer isn't compromised and sending bogus instructions. If the comparison fail, the squads transaction in question should be cancelled
> 
> ### 12:32 — Yuri Albuquerque
> 
> you'll probably need help running the test, lmk when you want to run it
> 
> ### 12:32 — Yuri Albuquerque
> 
> it's a... complicated test
> 
> ### 12:33 — Samadhi (Jay)
> 
> dang haha. What's involved?
> 
> ### 12:34 — Yuri Albuquerque
> 
> you'll need to:
> 1 - run solana-test-validator
> 2 - airdrop to some accounts that are gonna be used
> 3 - deploy squads
> 4 - initialize squads config
> 5 - create a multisig account
> 
> ### 12:35 — Yuri Albuquerque
> 
> 6 - edit some variables with the correct Keypair or Pubkeys
> 
> ### 12:36 — Yuri Albuquerque
> 
> meanwhile I'll try to make the test simpler to run (probably requiring only squads to be deployed), but if you're running it before I simplify it I can help you to run it
> 
> ### 12:45 — Samadhi (Jay)
> 
> let me know when changes are done and I'll try it out
> 
> ### 09:01 — Yuri Albuquerque
> 
> @Samadhi (Jay) I've done some changes to the test and made it simpler to run. You still need to deploy squads and initialize the config, though
> 
> ### 09:02 — Yuri Albuquerque
> 
> I guess you still need a single airdrop, but now the steps should be:
> 1. run solana-test-validator
> 2. airdrop to the account that's gonna initialize the config
> 3. deploy squads
> 4. initialize the config
> 5. edit the program id for squads
> 
> ### 11:33 — Samadhi (Jay)
> 
> sorry for taking a while I was working on setting it up yesterday. What are the steps exactly for initializing the config? Once I have squads deployed what's next?
> 
> ### 11:34 — Yuri Albuquerque
> 
> https://github.com/Denommus/squads-v4/
> 
> ### 11:34 — Yuri Albuquerque
> 
> you need to compile and run the cli of that repo
> 
> ### 11:34 — Yuri Albuquerque
> 
> example of me running it:
> ```./target/release/squads-multisig-cli \
>     program-config-init \
>     --program-id GQGNGBWyWLQJHnnpxpNjd4qwqRK17Z3V6APS6ALee6KD \
>     --rpc-url http://localhost:8899 \
>     --initializer-keypair ~/projetos/squads-client/config_initializer.json \
>     --program-config-authority 2v4iR9uBFCkQcLtuRt4vh3qdooSJ4zAaLKrri6899Phx \
>     --treasury 6hHpKqBLA4HigNzcZNDCoC9hDq4gnxcBCfU8rY9PhsfT \
>     --multisig-creation-fee 10```
> 
> ### 11:35 — Yuri Albuquerque
> 
> the program-id needs to be replaced by the program id you have there, the initializer keypair needs to be a local key as well (you need to airdrop to it), the rest can stay the same
> 
> ### 11:36 — Yuri Albuquerque
> 
> if you need more help lmk
> 
> ### 11:37 — Samadhi (Jay)
> 
> ok. Why did you need to fork squads?
> 
> ### 11:38 — Yuri Albuquerque
> 
> because of the difference between anchor versions of syzygy and squads
> 
> ### 11:38 — Yuri Albuquerque
> 
> (I didn't even remember why I had a fork, thanks for asking)
> 
> ### 11:38 — Yuri Albuquerque
> 
> I guess you can use the main fork as well
> 
> ### 11:38 — Yuri Albuquerque
> 
> for this
> 
> ### 11:40 — Samadhi (Jay)
> 
> gotcha. Also once its initialized, is there a test I can run? Or what's a flow I should test
> 
> ### 11:40 — Yuri Albuquerque
> 
> just run `cargo test test_compare_instructions_and_stored_message -- --ignored`
> 
> ### 11:41 — Yuri Albuquerque
> 
> it's a slowish test because some airdrops happen and need to be confirmed
> 
> ### 11:41 — Samadhi (Jay)
> 
> sounds great. I'll try it a little later today
> 
> ### 11:42 — Yuri Albuquerque
> 
> ok, lmk
> 
> ### 09:54 — Samadhi (Jay)
> 
> what is the config_initializer.json?
> 
> ### 09:58 — Samadhi (Jay)
> 
> oh its just a regular keypair file
> 
> ### 10:42 — Samadhi (Jay)
> 
> cool looks good Yuri. Test passes. Approved
>
