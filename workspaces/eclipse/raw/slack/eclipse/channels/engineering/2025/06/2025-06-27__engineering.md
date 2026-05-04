---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:35-05:00'
ingest_version: 1
content_hash: blake3:10501508b01f019b22270b706aa480537287823303f4c8d28de5775b61cc22d0
provider_modified_at: '2025-06-30T15:57:32-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2025-06-27'
date_range:
  first: '2025-06-27T10:22:28-05:00'
  last: '2025-06-30T15:57:32-05:00'
message_count: 2
thread_count: 1
participant_count: 4
participants:
- slug: yuri-albuquerque
  slack_user_id: U05TRBZNAMB
  display_name: Yuri Albuquerque
  real_name: Yuri Albuquerque
  email: yuri@eclipse.builders
- slug: cooper
  slack_user_id: U05U6497UAE
  display_name: Cooper
  real_name: Cooper Kernan
  email: cooper@eclipse.builders
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
attachments: []
deleted_messages: []
edited_messages_count: 2
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2025-06-27 (Friday)

## 10:22 — Yuri Albuquerque

I have some errands to do today, I'm not sure I'll be able to attend the meetings. My update is that I'm creating an endpoint to download older snapshots from a solar-eclipse node

## 12:11 — Cooper

Hey all <!here>, Flipside is deprecating the State of Eclipse dashboard [here](https://flipsidecrypto.xyz/flipsideteam/state-of-eclipse-IbQKJw) on 07/28/25, they've provided the queries [here](https://github.com/cprkrn/flipside_queries-/tree/main/eclipse-analytics)- curious your thoughts on best solutions to re-host this data + get some sort of public facing UI? The data will still be accessible via Snowflake. They've suggested potentially Looker / Tableau + they also have an in-house MCP solution with Claude albeit that's not public facing.

> ### 12:11 — Olivier Desenfans
> 
> Oh damn, that's not ideal
> 
> ### 12:11 — Olivier Desenfans
> 
> Why are they stopping? Are they asking for too much to maintain it?
> 
> ### 12:12 — Cooper
> 
> No they're just pivoting into a new direction and not providing these for anyone anymore.
> 
> ### 12:13 — Olivier Desenfans
> 
> Dune would be the place to be then, having our data there would be great for analysis. But they'll probably charge us a bunch.
> 
> ### 12:13 — Ben
> 
> Tableau is pretty legit
> 
> ### 12:13 — Ben
> 
> lookerstudio is free to us? @Cooper
> 
> ### 12:14 — Cooper
> 
> Dune is an option but we'd have to pay a lot / @Ren Yu Kong said Dune isn't great / I think Tableau or Looker might be best just unsure how complex it is to configure @Olivier Desenfans
> 
> ### 12:14 — Cooper
> 
> Not sure if Looker studio is free but will see @Ben
> 
> ### 12:15 — Ben
> 
> should be under standard https://cloud.google.com/looker/pricing
> 
> ### 12:16 — Ben
> 
> plus https://other-docs.snowflake.com/en/connectors/google-looker-studio-connector
> 
> ### 12:16 — Cooper
> 
> Ah ok didn't realize it was Google related, maybe best to plan that route
> 
> ### 12:16 — Cooper
> 
> Thanks for some context
> 
> ### 15:56 — Ben
> 
> @Cooper how viable is Looker for us?
> 
> ### 15:57 — Cooper
> 
> Should be doable- haven’t spent too much time looking into it yet
>
