# Stage: ingest-whatsapp

## Status
Skeleton. WhatsApp's "Export chat" produces zip files with a `_chat.txt` and media. To enable: drop exports at `workspaces/<ws>/raw/whatsapp/_inbox/`, implement parsing in `_shell/bin/ingest-whatsapp.py`.

## Planned shape
- Per (contact-or-group, year-month) markdown file, similar to iMessage.
- Slug derivation from the export's chat title or first participant.
- Body: day-grouped messages with attachments referenced (media zipped alongside).

## Default for unrouted
Skip (privacy-first, like iMessage).
