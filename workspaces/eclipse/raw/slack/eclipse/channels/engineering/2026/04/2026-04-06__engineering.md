---
source: slack
workspace: eclipse
ingested_at: '2026-05-04T16:31:36-05:00'
ingest_version: 1
content_hash: blake3:ef64d0762560d93bd2d8076a25d0d476f934a99442b5b2e1dc13890b53cbeff2
provider_modified_at: '2026-04-06T12:52:59-05:00'
slack_workspace_slug: eclipse
slack_workspace_id: T04472N6YUU
container_type: channel
container_slug: engineering
container_id: C04LY65HW7M
date: '2026-04-06'
date_range:
  first: '2026-04-06T11:12:32-05:00'
  last: '2026-04-06T12:52:59-05:00'
message_count: 2
thread_count: 1
participant_count: 1
participants:
- slug: julien
  slack_user_id: U07V99QMTV5
  display_name: julien じゅりえん
  real_name: Julien Tregoat
  email: julien@eclipse.builders
attachments:
- id: F0AQNQTM2K1
  filename: image.png
  size_bytes: 364302
  mime: image/png
  sender_slug: julien
  sent_at: '2026-04-06T11:12:32-05:00'
  permalink: https://eclipse-labs.slack.com/files/U0A993YPZ1Q/F0AQNQTM2K1/image.png
  private_url: https://files.slack.com/files-pri/T04472N6YUU-F0AQNQTM2K1/image.png
deleted_messages: []
edited_messages_count: 3
chat_db_message_ids: null
deleted_upstream: null
container_archived: false
---

# #engineering — 2026-04-06 (Monday)

## 11:12 — julien じゅりえん

trying out this IDE. it has first class AI support with external agents. so you can use claude code with it like cursor, passing in lines etc, or any other agent - doesn't have to be api key usage. can even use cursor agents. I found it because it's NOT an electron editor, it's built in Rust so hopefully way more performant [https://zed.dev/](https://zed.dev/)

[image: A screenshot of the Zed code editor interface shows a "Welcome to Zed" screen on the left and an active AI chat panel titled "test" on the right. In the chat, the user asks "who am i," and the assistant identifies the user as "julien" on macOS after reading a memory file at `.claude/projects/-Users-julien/memory/MEMORY.md`.]

## 12:30 — julien じゅりえん

more tools for making the most of Claude code. i've started using some of these and had good results. the plugins are a combo of high level rulesets and prompts but there's also MCPs in there which are less useful imo

one I really like is `codex` reviews, you can use chatgpt subscription for the plugin instead of API key which is handy. it has review features, and I think the adversarial review is most interesting; i've been messing with adversarial prompts since normal code reviews tend to feel optimistic. [this one is external, not in the official marketplace](https://github.com/openai/codex-plugin-cc). prob are adversarial review plugins for other models

`superpowers` is required imo, I find it improves plan development but also just has a ton of other best practices it imbues your agent with

apparently `typescript-lsp` language server plugin also super helpful

https://claude.com/plugins

> ### 12:52 — julien じゅりえん
> 
> this is apparently a monster for context but sick https://claude.com/plugins/ralph-loop
>
