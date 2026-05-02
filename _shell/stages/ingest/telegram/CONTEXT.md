# Stage: ingest-telegram

## Status
Skeleton. Telegram has multiple ingest paths (Telegram Desktop export, Bot API, MTProto). To enable, pick one and document here. Most likely path: Telegram Desktop's "Export chat history" → JSON → drop in `_inbox/`.

## Planned shape
Same as iMessage / WhatsApp: per (chat, year-month) markdown files at `workspaces/<ws>/raw/telegram/{individuals|groups|channels}/<slug>/<YYYY>/<YYYY-MM>__<slug>.md`.

## Default for unrouted
Skip (privacy-first).
