---
source: manual
workspace: personal
ingested_at: 2026-05-07T13:00:00+00:00
ingest_version: 1
content_hash: manual:studies-at-direction-fix-v1
provider_modified_at: 2026-05-07T13:00:00+00:00
---

# studies_at — Direction Convention

The `studies_at` relation flows Person → Institution. Rishika UC Berkeley studies at UC Berkeley. Rohin UC Berkeley studies at UC Berkeley. The institution does not study at the person; any inverted edge ("UC Berkeley studies_at Person") is a graphify direction artifact and should be flipped on next pass.
