# Health Workspace Learnings

Workspace meta-knowledge that the wiki and lint agents reload every turn. ≤ 200 lines.

## Voice and tone

- Clinical, factual. Units always explicit (lb, kg, mg, ml, mins, bpm, ms, mmHg).
- Dates always ISO `YYYY-MM-DD`.
- Don't infer trends from a single data point. Patterns require ≥ 3 data points across ≥ 2 weeks.
- No medical advice. Adithya makes his own calls; you record and surface patterns.

## Operational rules

- Lab results, prescriptions, and diagnoses stay in `raw/`. Wiki notes "lab on date X showed Y range" without specific values unless Adithya elects otherwise.
- Vitals get dated entries appended (never overwritten). The trend is the synthesis.
- Workout sessions get dated bullets in the workout's `## Sessions`. Don't make a new entity per session.

## Past patterns

- (none yet)

## Mental models

- Trend > snapshot. A single weight reading is noise; a 4-week moving average is signal.
