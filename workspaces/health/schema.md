# Health Schema

Workspace schema for health, fitness, nutrition, vitals, sleep, supplements, providers.

## Entity types

| Type | Folder | Definition |
|---|---|---|
| workout | `wiki/entities/workouts/` | A single training session or repeating program. |
| supplement | `wiki/entities/supplements/` | A substance taken regularly (vitamins, peptides, prescription, etc.). |
| provider | `wiki/entities/providers/` | A doctor, PT, dietitian, or other health professional. |
| vital | `wiki/entities/vitals/` | A repeating measurement (weight, BP, HRV, resting HR, sleep). |

## Per-type page format

### workout

```yaml
---
slug: <kebab>
type: workout
canonical_name: <name>
category: lift | cardio | mobility | sport | other
status: active | paused | retired
last_touched: <YYYY-MM-DD>
---
```

Body: `## Description`, `## Sessions` (dated bullets with reps/weight/distance/time), `## Notes`, `## Backlinks`.

### supplement

```yaml
---
slug: <kebab>
type: supplement
canonical_name: <name>
dose: <amount + units>
frequency: daily | weekly | as-needed | cycled
status: active | paused | discontinued
started: <YYYY-MM-DD>
last_touched: <YYYY-MM-DD>
---
```

Body: `## Why`, `## History` (dose changes / cycles), `## Effects observed`, `## Backlinks`.

### provider

```yaml
---
slug: <kebab>
type: provider
canonical_name: <name>
role: primary-care | specialist | dietitian | pt | dentist | optometrist | other
specialty: <if specialist>
last_touched: <YYYY-MM-DD>
---
```

Body: `## Context`, `## Visits` (dated bullets), `## Open follow-ups`, `## Backlinks`.

### vital

```yaml
---
slug: <kebab>
type: vital
canonical_name: <name>
units: <units>
target_range: <range or n/a>
last_touched: <YYYY-MM-DD>
---
```

Body: `## Definition`, `## Recent values` (dated, units explicit), `## Trend`, `## Backlinks`.

## Vocabulary

- "vital" = a repeating quantitative measurement.
- "session" = one instance of a workout.
- "cycle" = a defined-duration on/off period for a supplement.
- "lab" = a clinical lab result (BMP, lipid panel, hormone panel, etc.).

## Schema change protocol

Schema changes flow through `_meta/schema-proposals.md`.
